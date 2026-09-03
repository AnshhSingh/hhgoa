import pytest
from app.models import CandidateContent
from app.hashing import calculate_file_sha256, create_content_fingerprint

def test_identical_files_produce_identical_hashes(tmp_path):
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    
    file1.write_bytes(b"hello world")
    file2.write_bytes(b"hello world")
    
    hash1 = calculate_file_sha256(str(file1))
    hash2 = calculate_file_sha256(str(file2))
    
    assert hash1 == hash2

def test_changing_file_changes_hash(tmp_path):
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    
    file1.write_bytes(b"hello world")
    file2.write_bytes(b"hello world!")
    
    hash1 = calculate_file_sha256(str(file1))
    hash2 = calculate_file_sha256(str(file2))
    
    assert hash1 != hash2

def test_create_content_fingerprint(tmp_path):
    image_file = tmp_path / "image.jpg"
    image_file.write_bytes(b"fake image data")
    
    candidate = CandidateContent(
        source_url="https://example.com",
        image_url="https://example.com/image.jpg",
        local_image_path=str(image_file),
        title="Test Title",
        source="Test Source",
        retrieval_success=True
    )
    
    fingerprint1 = create_content_fingerprint(candidate)
    assert fingerprint1.content_hash
    assert fingerprint1.image_hash
    assert fingerprint1.source_url == "https://example.com"
    assert fingerprint1.title == "Test Title"
    assert fingerprint1.source == "Test Source"
    assert fingerprint1.timestamp
    
    # Check deterministic nature
    fingerprint2 = create_content_fingerprint(candidate)
    assert fingerprint1.content_hash == fingerprint2.content_hash
    assert fingerprint1.image_hash == fingerprint2.image_hash

def test_create_content_fingerprint_missing_image():
    candidate = CandidateContent(
        source_url="https://example.com",
        title="Test",
        source="Source",
        retrieval_success=False
    )
    
    with pytest.raises(ValueError, match="Candidate must have a valid local image path to be fingerprinted."):
        create_content_fingerprint(candidate)
