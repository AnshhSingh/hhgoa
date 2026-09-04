import hashlib
import json
from datetime import datetime, timezone
from app.models import CandidateContent, ContentFingerprint

def calculate_file_sha256(path: str) -> str:
    """Calculate the SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def create_content_fingerprint(candidate: CandidateContent) -> ContentFingerprint:
    """Create a deterministic fingerprint for a matching candidate."""
    if not candidate.local_image_path:
        raise ValueError("Candidate must have a valid local image path to be fingerprinted.")
        
    image_hash = calculate_file_sha256(candidate.local_image_path)
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Create deterministic representation for content_hash
    content_dict = {
        "source_url": candidate.source_url,
        "image_hash": image_hash,
        "title": candidate.title,
        "source": candidate.source,
    }
    
    # Sort keys to ensure deterministic JSON string
    content_str = json.dumps(content_dict, sort_keys=True)
    content_hash = hashlib.sha256(content_str.encode('utf-8')).hexdigest()
    
    return ContentFingerprint(
        content_hash=content_hash,
        image_hash=image_hash,
        source_url=candidate.source_url,
        title=candidate.title,
        source=candidate.source,
        timestamp=timestamp
    )
