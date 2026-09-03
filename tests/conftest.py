import sys
from unittest.mock import MagicMock

# Mock face_recognition because it requires dlib which fails to build without C++ tools on some machines
mock_face_recognition = MagicMock()
sys.modules['face_recognition'] = mock_face_recognition
