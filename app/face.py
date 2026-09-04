import face_recognition
import numpy as np
from app.models import FaceResult

def process_face(image_path: str) -> FaceResult:
    """
    Extract face encodings from a single image containing exactly one face.
    """
    try:
        image = face_recognition.load_image_file(image_path)
        # Ensure image is 8-bit RGB to prevent dlib "Unsupported image type" errors
        if image.dtype != 'uint8':
            # Scale 16-bit to 8-bit if necessary, or just cast
            if image.dtype == 'uint16':
                image = (image / 256).astype(np.uint8)
            else:
                image = image.astype(np.uint8)
    except FileNotFoundError:
        raise ValueError(f"Image not found at path: {image_path}")
    except Exception as e:
        raise ValueError(f"Could not load image: {str(e)}")
        
    face_locations = face_recognition.face_locations(image)
    face_count = len(face_locations)
    
    if face_count == 0:
        raise ValueError("No faces detected in the image.")
    if face_count > 1:
        raise ValueError(f"Multiple faces detected. Expected 1, found {face_count}.")
        
    # Get the single face location and encoding
    face_location = face_locations[0]
    face_encodings = face_recognition.face_encodings(image, face_locations)
    
    return FaceResult(
        input_path=image_path,
        face_location=face_location,
        encoding=face_encodings[0].tolist() if hasattr(face_encodings[0], 'tolist') else list(face_encodings[0]),
        face_count=face_count
    )

def extract_face(image_path: str) -> bytes:
    """
    Extract face embeddings or cropped face from image.
    """
    raise NotImplementedError("extract_face is not implemented yet")
