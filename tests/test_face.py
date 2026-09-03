import pytest
from unittest.mock import patch, MagicMock
from app.face import process_face
import face_recognition

@patch('app.face.face_recognition')
def test_process_face_valid_single_face(mock_fr):
    mock_fr.load_image_file.return_value = "dummy_image_data"
    mock_fr.face_locations.return_value = [(10, 20, 30, 40)]  # one face location
    
    mock_encoding = MagicMock()
    mock_encoding.tolist.return_value = [0.1, 0.2, 0.3]
    mock_fr.face_encodings.return_value = [mock_encoding]
    
    result = process_face("valid_path.jpg")
    
    assert result.input_path == "valid_path.jpg"
    assert result.face_location == (10, 20, 30, 40)
    assert result.encoding == [0.1, 0.2, 0.3]
    assert result.face_count == 1
    
    mock_fr.load_image_file.assert_called_once_with("valid_path.jpg")
    mock_fr.face_locations.assert_called_once_with("dummy_image_data")
    mock_fr.face_encodings.assert_called_once_with("dummy_image_data", [(10, 20, 30, 40)])

@patch('app.face.face_recognition')
def test_process_face_no_face(mock_fr):
    mock_fr.load_image_file.return_value = "dummy_image_data"
    mock_fr.face_locations.return_value = []  # no faces
    
    with pytest.raises(ValueError, match="No faces detected in the image."):
        process_face("no_face.jpg")

@patch('app.face.face_recognition')
def test_process_face_multiple_faces(mock_fr):
    mock_fr.load_image_file.return_value = "dummy_image_data"
    mock_fr.face_locations.return_value = [(10, 20, 30, 40), (50, 60, 70, 80)]  # two faces
    
    with pytest.raises(ValueError, match="Multiple faces detected. Expected 1, found 2."):
        process_face("multiple_faces.jpg")

def test_process_face_nonexistent_file():
    # In order to test FileNotFoundError properly, we should ensure the real or patched
    # load_image_file raises it. We'll just patch the mocked instance.
    with patch('app.face.face_recognition.load_image_file', side_effect=FileNotFoundError):
        with pytest.raises(ValueError, match="Image not found at path: nonexistent.jpg"):
            process_face("nonexistent.jpg")
