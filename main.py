import typer
from dotenv import load_dotenv

from app.pipeline import run_pipeline

load_dotenv()

app = typer.Typer(help="Face-to-Web Blockchain Verification Pipeline")

@app.command()
def process(image_path: str = typer.Option(..., help="Path to the input image file")):
    """
    Process an image through the verification pipeline.
    """
    typer.echo(f"Processing image: {image_path}")
    run_pipeline(image_path)

@app.command()
def status():
    """
    Check system status.
    """
    typer.echo("System is ready.")

if __name__ == "__main__":
    app()
