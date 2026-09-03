import os
import requests
from app.models import SearchResult

def search_image(image_path: str) -> list[SearchResult]:
    """
    Search the web for the given image using SerpApi Google Lens.
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("SERPAPI_API_KEY environment variable is not set.")

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    # Step 1: Upload the image to SerpApi to get an image_id
    upload_url = "https://serpapi.com/image"
    
    try:
        with open(image_path, "rb") as image_file:
            files = {"image": image_file}
            data = {"api_key": api_key}
            upload_resp = requests.post(upload_url, files=files, data=data)
            upload_resp.raise_for_status()
            upload_data = upload_resp.json()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Network error during image upload: {e}")
    except ValueError:
        raise ValueError("Malformed JSON response from SerpApi during upload.")

    if "error" in upload_data:
        raise ValueError(f"SerpApi upload error: {upload_data['error']}")
        
    image_id = upload_data.get("image_id") or upload_data.get("id")
    if not image_id:
        raise ValueError("No image_id returned from SerpApi upload.")

    # Step 2: Perform Google Lens search using the image_id
    search_url = "https://serpapi.com/search"
    params = {
        "engine": "google_lens",
        "image_id": image_id,
        "api_key": api_key
    }
    
    try:
        search_resp = requests.get(search_url, params=params)
        search_resp.raise_for_status()
        search_data = search_resp.json()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Network error during Google Lens search: {e}")
    except ValueError:
        raise ValueError("Malformed JSON response from SerpApi during search.")

    if "error" in search_data:
        raise ValueError(f"SerpApi search error: {search_data['error']}")

    # Step 3: Parse results
    results = []
    
    # Google Lens results often appear in 'visual_matches' or 'exact_matches'
    matches = search_data.get("visual_matches", [])
    if not matches:
        matches = search_data.get("exact_matches", [])
        
    for index, match in enumerate(matches):
        title = match.get("title", "Unknown Title")
        source = match.get("source", "Unknown Source")
        url = match.get("link", match.get("url", ""))
        thumbnail = match.get("thumbnail", "")
        
        # Skip if no URL is provided
        if not url:
            continue
            
        results.append(
            SearchResult(
                title=title,
                source=source,
                url=url,
                thumbnail=thumbnail,
                position=index + 1,
                result_type="visual_match"
            )
        )

    return results

def search_web_for_face(face_data: bytes) -> list[dict]:
    """
    Search the web for the given face data.
    """
    raise NotImplementedError("search_web_for_face is not implemented yet")
