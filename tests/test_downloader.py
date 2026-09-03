import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
from app.models import SearchResult
from app.downloader import download_candidate, process_candidates

@pytest.fixture
def dummy_result():
    return SearchResult(
        title="Test Title",
        source="Test Source",
        url="https://example.com/page",
        thumbnail="https://example.com/thumb.jpg",
        position=1,
        result_type="visual_match"
    )

@patch('app.downloader.requests.get')
def test_download_candidate_success_og_image(mock_get, dummy_result):
    # Setup mock responses for two GET requests:
    # 1. Page fetch (HTML)
    # 2. Image fetch (Binary)
    
    mock_html_resp = MagicMock()
    mock_html_resp.content = b'<html><head><meta property="og:image" content="https://example.com/image.jpg" /></head></html>'
    mock_html_resp.raise_for_status.return_value = None
    
    mock_img_resp = MagicMock()
    mock_img_resp.headers = {"Content-Type": "image/jpeg", "Content-Length": "1024"}
    mock_img_resp.iter_content.return_value = [b"fake_image_data"]
    mock_img_resp.__enter__.return_value = mock_img_resp
    
    mock_get.side_effect = [mock_html_resp, mock_img_resp]
    
    with patch('builtins.open', mock_open()):
        candidate = download_candidate(dummy_result)
        
    assert candidate.retrieval_success is True
    assert candidate.image_url == "https://example.com/image.jpg"
    assert candidate.local_image_path is not None
    assert candidate.local_image_path.endswith(".jpg")

@patch('app.downloader.requests.get')
def test_download_candidate_fallback_to_thumbnail(mock_get, dummy_result):
    # Page fetch fails or finds no image
    mock_html_resp = MagicMock()
    mock_html_resp.content = b'<html></html>'
    
    mock_img_resp = MagicMock()
    mock_img_resp.headers = {"Content-Type": "image/png", "Content-Length": "1024"}
    mock_img_resp.iter_content.return_value = [b"fake_image_data"]
    mock_img_resp.__enter__.return_value = mock_img_resp
    
    mock_get.side_effect = [mock_html_resp, mock_img_resp]
    
    with patch('builtins.open', mock_open()):
        candidate = download_candidate(dummy_result)
        
    assert candidate.retrieval_success is True
    assert candidate.image_url == dummy_result.thumbnail
    assert candidate.local_image_path.endswith(".png")

@patch('app.downloader.requests.get')
def test_download_candidate_not_an_image(mock_get, dummy_result):
    mock_html_resp = MagicMock()
    mock_html_resp.content = b'<html></html>'
    
    mock_img_resp = MagicMock()
    mock_img_resp.headers = {"Content-Type": "text/html", "Content-Length": "1024"}
    mock_img_resp.__enter__.return_value = mock_img_resp
    
    mock_get.side_effect = [mock_html_resp, mock_img_resp]
    
    candidate = download_candidate(dummy_result)
        
    assert candidate.retrieval_success is False
    assert candidate.local_image_path is None

@patch('app.downloader.requests.get')
def test_download_candidate_too_large(mock_get, dummy_result):
    mock_html_resp = MagicMock()
    mock_html_resp.content = b'<html></html>'
    
    mock_img_resp = MagicMock()
    # 6 MB > 5 MB
    mock_img_resp.headers = {"Content-Type": "image/jpeg", "Content-Length": str(6 * 1024 * 1024)}
    mock_img_resp.__enter__.return_value = mock_img_resp
    
    mock_get.side_effect = [mock_html_resp, mock_img_resp]
    
    candidate = download_candidate(dummy_result)
        
    assert candidate.retrieval_success is False

@patch('app.downloader.download_candidate')
def test_process_candidates_limit(mock_download):
    mock_download.return_value = MagicMock()
    
    results = [
        SearchResult(title=f"T{i}", source=f"S{i}", url=f"U{i}", thumbnail=f"Th{i}", position=i, result_type="match")
        for i in range(15)
    ]
    
    processed = process_candidates(results, limit=10)
    
    assert len(processed) == 10
    assert mock_download.call_count == 10
