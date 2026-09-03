import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from app.models import CandidateContent
from app.matcher import match_candidate, find_best_match

@patch('app.matcher.face_recognition')
def test_match_candidate_success(mock_fr):
    mock_fr.load_image_file.return_value = "dummy_image"
    mock_fr.face_encodings.return_value = [[0.1, 0.2, 0.3], [0.8, 0.9, 1.0]]
    # Match the first face with 0.1 distance, and second with 0.9 distance
    mock_fr.face_distance.return_value = np.array([0.1, 0.9])
    
    reference_encoding = [0.1, 0.2, 0.3]
    result = match_candidate(reference_encoding, "candidate.jpg", threshold=0.6)
    
    assert result.is_match is True
    assert result.distance == 0.1
    assert result.threshold == 0.6
    assert result.matched_face_index == 0
    assert result.candidate_path == "candidate.jpg"

@patch('app.matcher.face_recognition')
def test_match_candidate_no_match(mock_fr):
    mock_fr.load_image_file.return_value = "dummy_image"
    mock_fr.face_encodings.return_value = [[0.8, 0.9, 1.0]]
    mock_fr.face_distance.return_value = np.array([0.8])
    
    reference_encoding = [0.1, 0.2, 0.3]
    result = match_candidate(reference_encoding, "candidate.jpg", threshold=0.6)
    
    assert result.is_match is False
    assert result.distance == 0.8
    assert result.matched_face_index is None

@patch('app.matcher.face_recognition')
def test_match_candidate_no_faces(mock_fr):
    mock_fr.load_image_file.return_value = "dummy_image"
    mock_fr.face_encodings.return_value = []
    
    result = match_candidate([0.1, 0.2, 0.3], "candidate.jpg")
    
    assert result.is_match is False
    assert result.distance == 1.0

@patch('app.matcher.face_recognition')
def test_match_candidate_file_error(mock_fr):
    mock_fr.load_image_file.side_effect = FileNotFoundError
    
    result = match_candidate([0.1, 0.2, 0.3], "bad_path.jpg")
    
    assert result.is_match is False
    assert result.distance == 1.0
    assert result.candidate_path == "bad_path.jpg"

@patch('app.matcher.match_candidate')
def test_find_best_match(mock_match):
    c1 = CandidateContent(
        source_url="http://1", title="1", source="1", retrieval_success=True, local_image_path="1.jpg"
    )
    c2 = CandidateContent(
        source_url="http://2", title="2", source="2", retrieval_success=True, local_image_path="2.jpg"
    )
    c3 = CandidateContent(
        source_url="http://3", title="3", source="3", retrieval_success=False, local_image_path=None
    )
    
    # Mock c1 to match with distance 0.4
    r1 = MagicMock()
    r1.is_match = True
    r1.distance = 0.4
    
    # Mock c2 to match better with distance 0.2
    r2 = MagicMock()
    r2.is_match = True
    r2.distance = 0.2
    
    def side_effect(ref, path, threshold):
        if path == "1.jpg": return r1
        if path == "2.jpg": return r2
        return None
        
    mock_match.side_effect = side_effect
    
    best = find_best_match([0.0], [c1, c2, c3], threshold=0.6)
    
    assert best is not None
    assert best[0] == c2
    assert best[1] == r2

@patch('app.matcher.match_candidate')
def test_find_best_match_none_found(mock_match):
    c1 = CandidateContent(
        source_url="http://1", title="1", source="1", retrieval_success=True, local_image_path="1.jpg"
    )
    
    r1 = MagicMock()
    r1.is_match = False
    r1.distance = 0.8
    mock_match.return_value = r1
    
    best = find_best_match([0.0], [c1], threshold=0.6)
    assert best is None
