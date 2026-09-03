# Face-to-Web Blockchain Verification Pipeline

A CLI application for verifying faces against the web and recording the results on a blockchain.

## Requirements

- Python 3.11+
- CMake and C++ Build Tools (required for `dlib` and `face_recognition` installation on Windows)

## Installation

1. Ensure you have CMake and a C++ compiler installed on your system.
2. Clone the repository and navigate to the project directory.
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

You can use the CLI to check the status or process an image.

```bash
python main.py --help
python main.py status
```

### Providing an Input Image

To run the verification pipeline, provide an image path using the `process` command's `--image-path` argument:

```bash
python main.py process --image-path ./data/input/my_photo.jpg
```

## How the Verification Pipeline Works

### 1. Face Detection
This project uses the Python `face_recognition` library to detect faces and extract their encodings.

1. **Loading**: The image is loaded from the specified path.
2. **Detection**: We detect all faces present in the image. The pipeline strictly requires **exactly one face**. If zero or multiple faces are found, it raises an explicit error.
3. **Encoding**: If one face is successfully detected, we extract a 128-dimensional face encoding (a list of floating-point numbers) which is used to uniquely identify the face during the search and matching phases.

### 2. Web & Social Media Discovery
We utilize Google Lens via SerpApi to discover visually similar images on the web.

1. **API Key Setup**: You must set a valid SerpApi key in your `.env` file using the `SERPAPI_API_KEY` environment variable.
2. **Dynamic Retrieval**: The pipeline dynamically interacts with the live web. It uploads your image securely to SerpApi and retrieves an `image_id`.
3. **Reverse Image Search**: Using this `image_id`, the system queries Google Lens. It parses the resulting JSON (visual or exact matches) to extract real-world URLs, source names, and thumbnails. The results are not hardcoded, meaning they will change organically based on live search results.

### 3. Face Verification & Matching
Once candidate images are downloaded from the web, the system uses the `face_recognition` library to detect faces in each candidate and generates encodings.

1. **Similarity Verification**: It compares the original face encoding to the candidate encodings using a configurable distance threshold (default is 0.6).
2. **Privacy Focus**: The pipeline strictly performs **similarity verification** ("Is this the same face?"). It does **not** perform identity identification, and it will never attempt to attach a name or real-world identity to a face.
3. **Best Match Selection**: The pipeline compares all candidates and selects the single strongest match (the face with the smallest distance) to record as verified evidence.
