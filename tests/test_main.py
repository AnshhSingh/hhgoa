from typer.testing import CliRunner
from main import app

runner = CliRunner()

def test_app_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Face-to-Web Blockchain Verification Pipeline" in result.stdout

def test_app_status():
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "System is ready." in result.stdout
