import pytest
from unittest.mock import patch, MagicMock
from app.models import PipelineResult, CandidateContent, MatchResult, ContentFingerprint, BlockchainReceipt, VerificationResult
from app.pipeline import run_pipeline

@pytest.fixture
def mock_pipeline_deps():
    with patch('app.pipeline.process_face') as mock_face, \
         patch('app.pipeline.search_image') as mock_search, \
         patch('app.pipeline.process_candidates') as mock_process_candidates, \
         patch('app.pipeline.find_best_match') as mock_match, \
         patch('app.pipeline.create_content_fingerprint') as mock_fingerprint, \
         patch('app.pipeline.register_content') as mock_register, \
         patch('app.pipeline.verify_content') as mock_verify:
         
        yield {
            "face": mock_face,
            "search": mock_search,
            "process_candidates": mock_process_candidates,
            "match": mock_match,
            "fingerprint": mock_fingerprint,
            "register": mock_register,
            "verify": mock_verify
        }

def test_run_pipeline_success(mock_pipeline_deps):
    # Setup mocks
    deps = mock_pipeline_deps
    
    mock_face_result = MagicMock()
    mock_face_result.encoding = [0.1, 0.2, 0.3]
    deps["face"].return_value = mock_face_result
    
    deps["search"].return_value = []
    
    mock_candidate = CandidateContent(
        source_url="http://example.com",
        title="Test",
        source="Test",
        retrieval_success=True,
        local_image_path="test.jpg"
    )
    deps["process_candidates"].return_value = [mock_candidate]
    
    mock_match_result = MatchResult(
        is_match=True, distance=0.1, threshold=0.6, candidate_path="test.jpg"
    )
    deps["match"].return_value = (mock_candidate, mock_match_result)
    
    mock_fp = ContentFingerprint(
        content_hash="hash_123", image_hash="img_hash", source_url="http://example.com",
        title="Test", source="Test", timestamp="2024"
    )
    deps["fingerprint"].return_value = mock_fp
    
    mock_receipt = BlockchainReceipt(
        transaction_hash="tx_123", block_number=42, contract_address="0x1", content_hash="hash_123"
    )
    deps["register"].return_value = mock_receipt
    
    mock_verify = VerificationResult(
        status="VERIFIED", message="ok", onchain_timestamp=123,
        onchain_source_url="url", onchain_submitter="0x0"
    )
    deps["verify"].return_value = mock_verify
    
    # Run
    result = run_pipeline("input.jpg")
    
    # Assert
    assert result.face_detected is True
    assert result.search_completed is True
    assert result.candidate_found is True
    assert result.face_match is True
    assert result.content_hash == "hash_123"
    assert result.blockchain_tx == "tx_123"
    assert result.block_number == 42
    assert result.onchain_verification == "VERIFIED"
    assert result.error_message is None

def test_run_pipeline_no_match(mock_pipeline_deps):
    deps = mock_pipeline_deps
    
    deps["face"].return_value = MagicMock(encoding=[0.1])
    deps["search"].return_value = []
    deps["process_candidates"].return_value = []
    deps["match"].return_value = None  # No match found
    
    result = run_pipeline("input.jpg")
    
    assert result.face_detected is True
    assert result.search_completed is True
    assert result.candidate_found is False
    assert result.face_match is False
    assert result.error_message == "No matching candidate face found in the search results."
    assert result.content_hash is None
    assert result.blockchain_tx is None
    
    # Ensure blockchain was never called
    deps["register"].assert_not_called()
    deps["verify"].assert_not_called()

def test_run_pipeline_face_detection_fails(mock_pipeline_deps):
    deps = mock_pipeline_deps
    deps["face"].side_effect = ValueError("No face detected")
    
    result = run_pipeline("input.jpg")
    
    assert result.face_detected is False
    assert result.error_message == "No face detected"
    deps["search"].assert_not_called()
