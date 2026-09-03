from pydantic import BaseModel
from typing import Optional, List, Tuple

class FaceResult(BaseModel):
    input_path: str
    face_location: Tuple[int, int, int, int]
    encoding: List[float]
    face_count: int

class PipelineConfig(BaseModel):
    image_path: str
    
class ProcessResult(BaseModel):
    success: bool
    hash_value: Optional[str] = None

class SearchResult(BaseModel):
    title: str
    source: str
    url: str
    thumbnail: str
    position: int
    result_type: str

class CandidateContent(BaseModel):
    source_url: str
    image_url: Optional[str] = None
    local_image_path: Optional[str] = None
    title: str
    source: str
    retrieval_success: bool

class MatchResult(BaseModel):
    is_match: bool
    distance: float
    threshold: float
    matched_face_index: Optional[int] = None
    candidate_path: str
