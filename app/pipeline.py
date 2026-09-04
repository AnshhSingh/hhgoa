from typing import Optional
from app.face import process_face
from app.search import search_image
from app.downloader import process_candidates
from app.matcher import find_best_match
from app.hashing import create_content_fingerprint
from app.blockchain import register_content, verify_content
from app.models import PipelineResult

def run_pipeline(input_image: str) -> PipelineResult:
    result = PipelineResult()
    
    try:
        # 1-3. Process face
        face_result = process_face(input_image)
        result.face_detected = True
        
        # 4-6. Search SerpApi
        search_results = search_image(input_image)
        result.search_completed = True
        
        # 7. Retrieve candidates
        candidates = process_candidates(search_results, limit=10)
        
        # 8-9. Compare and find best match
        best_match_tuple = find_best_match(face_result.encoding, candidates)
        if not best_match_tuple:
            result.error_message = "No matching candidate face found in the search results."
            return result
            
        candidate, match_info = best_match_tuple
        result.candidate_found = True
        result.face_match = True
        
        # 10. Fingerprint
        fingerprint = create_content_fingerprint(candidate)
        result.content_hash = fingerprint.content_hash
        
        # 11. Register on chain
        receipt = register_content(fingerprint)
        result.blockchain_tx = receipt.transaction_hash
        result.block_number = receipt.block_number
        
        # 12-14. Verify
        verification = verify_content(fingerprint)
        result.onchain_verification = verification.status
        
        # 15. Produce structured result
        import json
        import uuid
        import os
        
        filename = f"data/results/verification_{uuid.uuid4().hex}.json"
        os.makedirs("data/results", exist_ok=True)
        
        saved_data = {
            "original_content_hash": fingerprint.content_hash,
            "candidate": candidate.model_dump(),
            "blockchain_receipt": receipt.model_dump()
        }
        
        with open(filename, "w") as f:
            json.dump(saved_data, f, indent=4)
            
        result.result_file = filename
        
    except Exception as e:
        result.error_message = str(e)
        
    return result
