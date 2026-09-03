import os
import json
import time
from datetime import datetime
from web3 import Web3
from web3.exceptions import Web3Exception
from app.models import ContentFingerprint, BlockchainReceipt, VerificationResult

# Minimal ABI for the deployed contract interactions
MINIMAL_ABI = [
    {"inputs": [{"internalType": "bytes32", "name": "contentHash", "type": "bytes32"}], "name": "getRegistration", "outputs": [{"components": [{"internalType": "bytes32", "name": "contentHash", "type": "bytes32"}, {"internalType": "string", "name": "sourceUrl", "type": "string"}, {"internalType": "uint256", "name": "timestamp", "type": "uint256"}, {"internalType": "address", "name": "submitter", "type": "address"}], "internalType": "struct ContentVerifier.Registration", "name": "", "type": "tuple"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "bytes32", "name": "contentHash", "type": "bytes32"}, {"internalType": "string", "name": "sourceUrl", "type": "string"}, {"internalType": "uint256", "name": "timestamp", "type": "uint256"}], "name": "registerContent", "outputs": [], "stateMutability": "nonpayable", "type": "function"}
]

def _get_w3() -> Web3:
    rpc_url = os.getenv("RPC_URL", "http://127.0.0.1:8545")
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise ConnectionError(f"RPC unavailable at {rpc_url}")
    return w3

def _get_account(w3: Web3):
    pk = os.getenv("PRIVATE_KEY")
    if not pk:
        raise ValueError("PRIVATE_KEY environment variable is not set.")
    try:
        return w3.eth.account.from_key(pk)
    except ValueError:
        raise ValueError("Invalid PRIVATE_KEY.")

def deploy_contract() -> str:
    """Deploy the ContentVerifier contract. Requires forge build artifacts."""
    w3 = _get_w3()
    account = _get_account(w3)
    
    artifact_path = os.path.join("contracts", "out", "ContentVerifier.sol", "ContentVerifier.json")
    if not os.path.exists(artifact_path):
        raise FileNotFoundError(f"Contract artifact not found at {artifact_path}. Run 'forge build' in the contracts directory first.")
        
    with open(artifact_path, "r") as f:
        artifact = json.load(f)
        
    abi = artifact.get("abi")
    bytecode = artifact.get("bytecode", {}).get("object")
    
    if not abi or not bytecode:
        raise ValueError("Artifact does not contain valid abi or bytecode.")
        
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    try:
        tx = Contract.constructor().build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gasPrice": w3.eth.gas_price
        })
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction) # updated from rawTransaction
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
    except Web3Exception as e:
        raise RuntimeError(f"Deployment transaction failed: {e}")
        
    if receipt.status != 1:
        raise RuntimeError("Deployment transaction reverted.")
        
    return receipt.contractAddress

def register_content(fingerprint: ContentFingerprint) -> BlockchainReceipt:
    w3 = _get_w3()
    account = _get_account(w3)
    contract_address = os.getenv("CONTRACT_ADDRESS")
    
    if not contract_address:
        raise ValueError("CONTRACT_ADDRESS environment variable is not set.")
        
    contract = w3.eth.contract(address=contract_address, abi=MINIMAL_ABI)
    
    bytes32_hash = Web3.to_bytes(hexstr=fingerprint.content_hash)
    
    # Parse timestamp into a unix timestamp int
    # 2024-01-01T12:00:00+00:00
    try:
        # standard ISO format parsing
        dt = datetime.fromisoformat(fingerprint.timestamp)
        unix_ts = int(dt.timestamp())
    except Exception:
        unix_ts = int(time.time())
        
    try:
        tx = contract.functions.registerContent(
            bytes32_hash,
            fingerprint.source_url,
            unix_ts
        ).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gasPrice": w3.eth.gas_price
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
        
    except Web3Exception as e:
        raise RuntimeError(f"Transaction failed: {e}")
        
    if receipt.status != 1:
        raise RuntimeError("Transaction reverted by the EVM. The hash might already be registered.")
        
    return BlockchainReceipt(
        transaction_hash=receipt.transactionHash.hex(),
        block_number=receipt.blockNumber,
        contract_address=contract_address,
        content_hash=fingerprint.content_hash
    )

def get_onchain_record(content_hash: str) -> dict:
    w3 = _get_w3()
    contract_address = os.getenv("CONTRACT_ADDRESS")
    if not contract_address:
        raise ValueError("CONTRACT_ADDRESS environment variable is not set.")
        
    contract = w3.eth.contract(address=contract_address, abi=MINIMAL_ABI)
    bytes32_hash = Web3.to_bytes(hexstr=content_hash)
    
    try:
        record = contract.functions.getRegistration(bytes32_hash).call()
    except Web3Exception as e:
        raise RuntimeError(f"Contract call failed. Is it deployed? Error: {e}")
        
    # The record is a tuple: (contentHash, sourceUrl, timestamp, submitter)
    # If timestamp == 0, it means it's missing (default struct value)
    if record[2] == 0:
        return None
        
    return {
        "content_hash": record[0].hex(),
        "source_url": record[1],
        "timestamp": record[2],
        "submitter": record[3]
    }

def verify_content(fingerprint: ContentFingerprint) -> VerificationResult:
    # 1. Recalculate content hash (assume fingerprint obj passed has the valid hash based on its data)
    # For this exercise, the fingerprint obj is the source of truth for the local hash.
    local_hash = fingerprint.content_hash
    
    # 2. Retrieve the stored on-chain hash
    record = get_onchain_record(local_hash)
    
    # 3. Compare them
    if not record:
        return VerificationResult(
            status="MISSING",
            message=f"No on-chain record found for hash {local_hash}.",
            onchain_timestamp=None,
            onchain_source_url=None,
            onchain_submitter=None
        )
        
    # The contract ensures the mapping key matches the contentHash in the struct,
    # so if it returned a valid record, it is verified.
    return VerificationResult(
        status="VERIFIED",
        message="The content fingerprint matches the immutable on-chain record.",
        onchain_timestamp=record["timestamp"],
        onchain_source_url=record["source_url"],
        onchain_submitter=record["submitter"]
    )
