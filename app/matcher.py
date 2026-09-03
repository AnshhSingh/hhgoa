import numpy as np
import face_recognition
from typing import Optional, Tuple
from app.models import CandidateContent, MatchResult

def match_candidate(reference_encoding: list[float], candidate_path: str, threshold: float = 0.6) -> MatchResult:
    """
    Check if a candidate image contains a face matching the reference encoding.
    This performs similarity verification, not identity/name identification.
    """
    try:
        image = face_recognition.load_image_file(candidate_path)
    except Exception:
        return MatchResult(
            is_match=False,
            distance=1.0,
            threshold=threshold,
            matched_face_index=None,
            candidate_path=candidate_path
        )
        
    candidate_encodings = face_recognition.face_encodings(image)
    
    if not candidate_encodings:
        return MatchResult(
            is_match=False,
            distance=1.0,
            threshold=threshold,
            matched_face_index=None,
            candidate_path=candidate_path
        )
        
    ref_np = np.array(reference_encoding)
    distances = face_recognition.face_distance(candidate_encodings, ref_np)
    
    best_index = int(np.argmin(distances))
    best_distance = float(distances[best_index])
    
    is_match = best_distance <= threshold
    
    return MatchResult(
        is_match=is_match,
        distance=best_distance,
        threshold=threshold,
        matched_face_index=best_index if is_match else None,
        candidate_path=candidate_path
    )

def find_best_match(reference_encoding: list[float], candidates: list[CandidateContent], threshold: float = 0.6) -> Optional[Tuple[CandidateContent, MatchResult]]:
    """
    Find the strongest matching candidate from a list of downloaded candidates.
    Returns the CandidateContent and its MatchResult.
    """
    best_match: Optional[Tuple[CandidateContent, MatchResult]] = None
    best_distance = float('inf')
    
    for candidate in candidates:
        if not candidate.retrieval_success or not candidate.local_image_path:
            continue
            
        result = match_candidate(reference_encoding, candidate.local_image_path, threshold)
        
        if result.is_match and result.distance < best_distance:
            best_distance = result.distance
            best_match = (candidate, result)
            
    return best_match

def match_faces(source_face: bytes, target_faces: list[bytes]) -> list[dict]:
    """
    Legacy matcher placeholder.
    """
    raise NotImplementedError("match_faces is not implemented yet")
