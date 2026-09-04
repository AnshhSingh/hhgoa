import typer
from dotenv import load_dotenv

from app.pipeline import run_pipeline

load_dotenv()

app = typer.Typer(help="Face-to-Web Blockchain Verification Pipeline")

@app.command()
def process(image_path: str = typer.Option(..., "--image-path", help="Path to input image")):
    """
    Legacy command placeholder.
    """
    typer.echo(f"Processing image {image_path}")

@app.command()
def run(image: str = typer.Option(..., "--image", help="Path to the input image")):
    """Run the complete end-to-end verification pipeline."""
    from app.pipeline import run_pipeline
    
    typer.echo(f"Starting pipeline for {image}...")
    result = run_pipeline(image)
    
    typer.echo(f"FACE DETECTED: {'YES' if result.face_detected else 'NO'}")
    typer.echo(f"SEARCH COMPLETED: {'YES' if result.search_completed else 'NO'}")
    
    if result.candidate_found and result.face_match:
        typer.echo("CANDIDATE FOUND: YES")
        typer.echo("FACE MATCH: YES")
        typer.echo(f"CONTENT HASH: {result.content_hash}")
        typer.echo(f"BLOCKCHAIN TX: {result.blockchain_tx}")
        typer.echo(f"BLOCK NUMBER: {result.block_number}")
        typer.echo(f"ON-CHAIN VERIFICATION: {result.onchain_verification}")
    else:
        typer.echo("CANDIDATE FOUND: NO") if not result.candidate_found else typer.echo("FACE MATCH: NO")
        if result.error_message:
            typer.echo(f"STOPPED: {result.error_message}")
            
@app.command()
def verify(result_file: str = typer.Option(..., "--result", help="Path to the JSON result file")):
    """Verify a local result file against the blockchain."""
    import json
    from app.models import CandidateContent
    from app.hashing import create_content_fingerprint
    from app.blockchain import get_onchain_record
    
    with open(result_file, "r") as f:
        saved_data = json.load(f)
        
    original_hash = saved_data["original_content_hash"]
    candidate = CandidateContent(**saved_data["candidate"])
    
    current_fingerprint = create_content_fingerprint(candidate)
    current_hash = current_fingerprint.content_hash
    
    typer.echo(f"Original On-Chain Hash:\n{original_hash}\n")
    typer.echo(f"Current Content Hash:\n{current_hash}\n")
    
    if original_hash == current_hash:
        record = get_onchain_record(original_hash)
        if record:
            typer.echo("Result:\n✅ VERIFIED")
        else:
            typer.echo("Result:\n❌ TAMPERED (Hash not found on chain)")
    else:
        typer.echo("Result:\n❌ TAMPERED")

@app.command()
def tamper(result_file: str = typer.Option(..., "--result", help="Path to the JSON result file")):
    """Demo command: Intentionally tamper with a saved result file."""
    import json
    
    with open(result_file, "r") as f:
        saved_data = json.load(f)
        
    # Tamper with the candidate metadata
    saved_data["candidate"]["title"] = "HACKED TITLE - TAMPERED METADATA"
    
    with open(result_file, "w") as f:
        json.dump(saved_data, f, indent=4)
        
    typer.echo(f"Tampered with {result_file}. The title has been changed.")
    typer.echo(f"Run 'python main.py verify --result {result_file}' to test verification failure.")

@app.command()
def status():
    """
    Check system status.
    """
    typer.echo("System is ready.")

if __name__ == "__main__":
    app()
