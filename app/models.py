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

class ContentFingerprint(BaseModel):
    content_hash: str
    image_hash: str
    source_url: str
    title: str
    source: str
    timestamp: str

class BlockchainReceipt(BaseModel):
    transaction_hash: str
    block_number: int
    contract_address: str
    content_hash: str

class VerificationResult(BaseModel):
    status: str
    message: str
    onchain_timestamp: Optional[int] = None
    onchain_source_url: Optional[str] = None
    onchain_submitter: Optional[str] = None

class PipelineResult(BaseModel):
    face_detected: bool = False
    search_completed: bool = False
    candidate_found: bool = False
    face_match: bool = False
    content_hash: Optional[str] = None
    blockchain_tx: Optional[str] = None
    block_number: Optional[int] = None
    onchain_verification: Optional[str] = None
    error_message: Optional[str] = None
    result_file: Optional[str] = None
