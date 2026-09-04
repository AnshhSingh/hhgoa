import sys
from typer.testing import CliRunner
from main import app
from unittest.mock import patch, MagicMock

print("=== STARTING DRY RUN ===")

runner = CliRunner()

# Mock everything external so we can see the exact CLI output
with patch("app.pipeline.process_face") as mock_face, \
     patch("app.pipeline.search_image") as mock_search, \
     patch("app.pipeline.process_candidates") as mock_process_candidates, \
     patch("app.pipeline.find_best_match") as mock_match, \
     patch("app.pipeline.create_content_fingerprint") as mock_fingerprint, \
     patch("app.pipeline.register_content") as mock_register, \
     patch("app.pipeline.verify_content") as mock_verify:
     
    # 1. Face
    mock_face_result = MagicMock()
    mock_face_result.encoding = [0.1]
    mock_face.return_value = mock_face_result
    
    # 2. Search
    mock_search.return_value = []
    
    # 3. Candidates
    from app.models import CandidateContent, MatchResult, ContentFingerprint, BlockchainReceipt, VerificationResult
    
    mock_candidate = CandidateContent(
        source_url="http://example.com",
        title="Original Source",
        source="Test Source",
        retrieval_success=True,
        local_image_path="test.jpg"
    )
    mock_process_candidates.return_value = [mock_candidate]
    
    # 4. Match
    mock_match_result = MatchResult(
        is_match=True, distance=0.1, threshold=0.6, candidate_path="test.jpg"
    )
    mock_match.return_value = (mock_candidate, mock_match_result)
    
    # 5. Fingerprint
    mock_fp = ContentFingerprint(
        content_hash="abc123hash", image_hash="imghash", source_url="http://example.com",
        title="Original Source", source="Test Source", timestamp="2024"
    )
    mock_fingerprint.return_value = mock_fp
    
    # 6. Register
    mock_receipt = BlockchainReceipt(
        transaction_hash="0xabcd1234", block_number=1337, contract_address="0xcontract", content_hash="abc123hash"
    )
    mock_register.return_value = mock_receipt
    
    # 7. Verify
    mock_verify_result = VerificationResult(
        status="VERIFIED", message="ok", onchain_timestamp=123,
        onchain_source_url="url", onchain_submitter="0x0"
    )
    mock_verify.return_value = mock_verify_result
    
    print("\n[Executing: python main.py run --image data/input/test.jpg]")
    result = runner.invoke(app, ["run", "--image", "data/input/test.jpg"])
    print(result.stdout)
    
    print("\n=== DRY RUN COMPLETED ===")
