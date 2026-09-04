import pytest
from unittest.mock import patch, MagicMock
from app.models import ContentFingerprint
from app.blockchain import deploy_contract, register_content, get_onchain_record, verify_content
from web3.exceptions import Web3Exception

@pytest.fixture
def mock_w3(monkeypatch):
    monkeypatch.setenv("RPC_URL", "http://127.0.0.1:8545")
    monkeypatch.setenv("PRIVATE_KEY", "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
    monkeypatch.setenv("CONTRACT_ADDRESS", "0x1234567890123456789012345678901234567890")
    
    mock = MagicMock()
    mock.is_connected.return_value = True
    return mock

@pytest.fixture
def sample_fingerprint():
    return ContentFingerprint(
        content_hash="a"*64,
        image_hash="b"*64,
        source_url="http://example.com",
        title="Test",
        source="Source",
        timestamp="2024-01-01T12:00:00+00:00"
    )

@patch('app.blockchain.Web3')
def test_deploy_contract_no_artifact(mock_web3_class, mock_w3):
    mock_web3_class.return_value = mock_w3
    mock_web3_class.HTTPProvider.return_value = "provider"
    
    with pytest.raises(FileNotFoundError, match="Contract artifact not found"):
        deploy_contract()

@patch('app.blockchain.Web3')
def test_register_content_success(mock_web3_class, mock_w3, sample_fingerprint):
    mock_web3_class.return_value = mock_w3
    mock_web3_class.HTTPProvider.return_value = "provider"
    
    mock_contract = MagicMock()
    mock_w3.eth.contract.return_value = mock_contract
    
    mock_tx = {"to": "0x1"}
    mock_contract.functions.registerContent().build_transaction.return_value = mock_tx
    
    mock_signed = MagicMock()
    mock_signed.raw_transaction = b"signed"
    mock_w3.eth.account.sign_transaction.return_value = mock_signed
    
    mock_w3.eth.send_raw_transaction.return_value = b"txhash"
    
    mock_receipt = MagicMock()
    mock_receipt.status = 1
    mock_receipt.transactionHash.hex.return_value = "0xabc"
    mock_receipt.blockNumber = 42
    mock_w3.eth.wait_for_transaction_receipt.return_value = mock_receipt
    
    receipt = register_content(sample_fingerprint)
    
    assert receipt.block_number == 42
    assert receipt.content_hash == sample_fingerprint.content_hash

@patch('app.blockchain.Web3')
def test_register_content_revert(mock_web3_class, mock_w3, sample_fingerprint):
    mock_web3_class.return_value = mock_w3
    
    mock_receipt = MagicMock()
    mock_receipt.status = 0 # Reverted
    mock_w3.eth.wait_for_transaction_receipt.return_value = mock_receipt
    
    with pytest.raises(RuntimeError, match="Transaction reverted by the EVM"):
        register_content(sample_fingerprint)

@patch('app.blockchain.Web3')
def test_verify_content_success(mock_web3_class, mock_w3, sample_fingerprint):
    mock_web3_class.return_value = mock_w3
    
    mock_contract = MagicMock()
    mock_w3.eth.contract.return_value = mock_contract
    
    # tuple: (contentHash, sourceUrl, timestamp, submitter)
    mock_contract.functions.getRegistration().call.return_value = (
        b"a"*32,
        "http://example.com",
        1234567890,
        "0xabc"
    )
    
    result = verify_content(sample_fingerprint)
    assert result.status == "VERIFIED"
    assert result.onchain_timestamp == 1234567890

@patch('app.blockchain.Web3')
def test_verify_content_missing(mock_web3_class, mock_w3, sample_fingerprint):
    mock_web3_class.return_value = mock_w3
    
    mock_contract = MagicMock()
    mock_w3.eth.contract.return_value = mock_contract
    
    # timestamp = 0 means missing
    mock_contract.functions.getRegistration().call.return_value = (
        b"0"*32,
        "",
        0,
        "0x0"
    )
    
    result = verify_content(sample_fingerprint)
    assert result.status == "MISSING"

@patch('app.blockchain.Web3')
def test_connection_error(mock_web3_class):
    mock_w3 = MagicMock()
    mock_w3.is_connected.return_value = False
    mock_web3_class.return_value = mock_w3
    
    from app.blockchain import _get_w3
    with pytest.raises(ConnectionError, match="RPC unavailable"):
        _get_w3()
