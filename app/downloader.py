import os
import uuid
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from app.models import SearchResult, CandidateContent

# Constants
TIMEOUT_SEC = 10
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
CANDIDATES_DIR = os.path.join("data", "results", "candidates")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def _extract_image_url(page_url: str) -> str | None:
    """Attempt to extract a primary image URL from a given webpage."""
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(page_url, headers=headers, timeout=TIMEOUT_SEC)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        
        # 1. Try Open Graph image
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return urljoin(page_url, og_image["content"])
            
        # 2. Try Twitter Card image
        twitter_image = soup.find("meta", {"name": "twitter:image"})
        if twitter_image and twitter_image.get("content"):
            return urljoin(page_url, twitter_image["content"])
            
        # 3. Just grab the first large-looking image
        for img in soup.find_all("img"):
            src = img.get("src")
            if src and not src.startswith("data:"):
                return urljoin(page_url, src)
                
    except Exception:
        pass
        
    return None

def download_candidate(result: SearchResult) -> CandidateContent:
    """Download the candidate image and return CandidateContent."""
    os.makedirs(CANDIDATES_DIR, exist_ok=True)
    
    # 1. Determine image URL
    image_url = _extract_image_url(result.url)
    if not image_url:
        # Fallback to the thumbnail from the search result
        image_url = result.thumbnail
        
    if not image_url:
        return CandidateContent(
            source_url=result.url,
            image_url=None,
            local_image_path=None,
            title=result.title,
            source=result.source,
            retrieval_success=False
        )
        
    # 2. Download the image
    headers = {"User-Agent": USER_AGENT}
    try:
        # Stream the download to enforce size limit
        with requests.get(image_url, headers=headers, timeout=TIMEOUT_SEC, stream=True) as resp:
            resp.raise_for_status()
            
            content_type = resp.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                raise ValueError("URL did not return an image content type.")
                
            file_size = int(resp.headers.get("Content-Length", 0))
            if file_size > MAX_FILE_SIZE_BYTES:
                raise ValueError("Image file exceeds maximum allowed size.")
                
            ext = ".jpg"
            if "png" in content_type:
                ext = ".png"
            elif "webp" in content_type:
                ext = ".webp"
                
            filename = f"candidate_{uuid.uuid4().hex}{ext}"
            local_path = os.path.join(CANDIDATES_DIR, filename)
            
            downloaded_bytes = 0
            with open(local_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    downloaded_bytes += len(chunk)
                    if downloaded_bytes > MAX_FILE_SIZE_BYTES:
                        raise ValueError("Image file exceeds maximum allowed size during streaming.")
                    f.write(chunk)
                    
            return CandidateContent(
                source_url=result.url,
                image_url=image_url,
                local_image_path=local_path,
                title=result.title,
                source=result.source,
                retrieval_success=True
            )
            
    except Exception:
        return CandidateContent(
            source_url=result.url,
            image_url=image_url,
            local_image_path=None,
            title=result.title,
            source=result.source,
            retrieval_success=False
        )

def process_candidates(results: list[SearchResult], limit: int = 10) -> list[CandidateContent]:
    """Process a list of SearchResults and download their candidate images."""
    candidates = []
    for result in results[:limit]:
        candidates.append(download_candidate(result))
    return candidates
