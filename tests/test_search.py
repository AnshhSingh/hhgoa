import os
import pytest
import requests
from unittest.mock import patch, MagicMock
from app.search import search_image

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("SERPAPI_API_KEY", "test_api_key")

@pytest.fixture
def mock_no_env(monkeypatch):
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)

def test_search_image_missing_api_key(mock_no_env):
    with pytest.raises(ValueError, match="SERPAPI_API_KEY environment variable is not set."):
        search_image("dummy.jpg")

def test_search_image_file_not_found(mock_env):
    with pytest.raises(FileNotFoundError, match="Image not found at path: nonexistent.jpg"):
        search_image("nonexistent.jpg")

@patch('app.search.os.path.exists')
@patch('builtins.open')
@patch('app.search.requests.post')
@patch('app.search.requests.get')
def test_search_image_success_visual_matches(mock_get, mock_post, mock_open, mock_exists, mock_env):
    mock_exists.return_value = True
    
    # Mock upload response
    mock_post_resp = MagicMock()
    mock_post_resp.json.return_value = {"image_id": "test_image_id"}
    mock_post.return_value = mock_post_resp
    
    # Mock search response
    mock_get_resp = MagicMock()
    mock_get_resp.json.return_value = {
        "visual_matches": [
            {
                "title": "Match 1",
                "source": "Source 1",
                "link": "https://example.com/1",
                "thumbnail": "thumb1.jpg"
            }
        ]
    }
    mock_get.return_value = mock_get_resp
    
    results = search_image("dummy.jpg")
    
    assert len(results) == 1
    assert results[0].title == "Match 1"
    assert results[0].source == "Source 1"
    assert results[0].url == "https://example.com/1"
    assert results[0].thumbnail == "thumb1.jpg"
    assert results[0].position == 1
    assert results[0].result_type == "visual_match"

@patch('app.search.os.path.exists')
@patch('builtins.open')
@patch('app.search.requests.post')
@patch('app.search.requests.get')
def test_search_image_empty_results(mock_get, mock_post, mock_open, mock_exists, mock_env):
    mock_exists.return_value = True
    
    mock_post_resp = MagicMock()
    mock_post_resp.json.return_value = {"image_id": "test_image_id"}
    mock_post.return_value = mock_post_resp
    
    mock_get_resp = MagicMock()
    mock_get_resp.json.return_value = {}
    mock_get.return_value = mock_get_resp
    
    results = search_image("dummy.jpg")
    assert len(results) == 0

@patch('app.search.os.path.exists')
@patch('builtins.open')
@patch('app.search.requests.post')
def test_search_image_network_error_upload(mock_post, mock_open, mock_exists, mock_env):
    mock_exists.return_value = True
    mock_post.side_effect = requests.exceptions.RequestException("Connection refused")
    
    with pytest.raises(ConnectionError, match="Network error during image upload: Connection refused"):
        search_image("dummy.jpg")

@patch('app.search.os.path.exists')
@patch('builtins.open')
@patch('app.search.requests.post')
def test_search_image_api_error_upload(mock_post, mock_open, mock_exists, mock_env):
    mock_exists.return_value = True
    mock_post_resp = MagicMock()
    mock_post_resp.json.return_value = {"error": "Invalid API key."}
    mock_post.return_value = mock_post_resp
    
    with pytest.raises(ValueError, match="SerpApi upload error: Invalid API key."):
        search_image("dummy.jpg")

@patch('app.search.os.path.exists')
@patch('builtins.open')
@patch('app.search.requests.post')
@patch('app.search.requests.get')
def test_search_image_api_error_search(mock_get, mock_post, mock_open, mock_exists, mock_env):
    mock_exists.return_value = True
    mock_post_resp = MagicMock()
    mock_post_resp.json.return_value = {"image_id": "test_image_id"}
    mock_post.return_value = mock_post_resp
    
    mock_get_resp = MagicMock()
    mock_get_resp.json.return_value = {"error": "Search failed."}
    mock_get.return_value = mock_get_resp
    
    with pytest.raises(ValueError, match="SerpApi search error: Search failed."):
        search_image("dummy.jpg")
