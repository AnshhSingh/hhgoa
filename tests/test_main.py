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

def test_verify_and_tamper(tmp_path):
    import json
    import uuid
    from unittest.mock import patch
    
    # Create fake result file
    result_file = tmp_path / f"verification_{uuid.uuid4().hex}.json"
    
    saved_data = {
        "original_content_hash": "a"*64,
        "candidate": {
            "source_url": "http://example.com",
            "image_url": "http://example.com/image.jpg",
            "local_image_path": "fake_path.jpg",
            "title": "Test Title",
            "source": "Test Source",
            "retrieval_success": True
        },
        "blockchain_receipt": {
            "transaction_hash": "tx123",
            "block_number": 42,
            "contract_address": "0x1",
            "content_hash": "a"*64
        }
    }
    
    with open(result_file, "w") as f:
        json.dump(saved_data, f)
        
    with patch("app.hashing.create_content_fingerprint") as mock_fp, \
         patch("app.blockchain.get_onchain_record") as mock_record:
             
        mock_fp_obj = type("obj", (object,), {"content_hash": "a"*64})
        mock_fp.return_value = mock_fp_obj
        mock_record.return_value = {"timestamp": 1234}
        
        # Test Verify Success
        result = runner.invoke(app, ["verify", "--result", str(result_file)])
        assert result.exit_code == 0
        assert "VERIFIED" in result.stdout
        assert "TAMPERED" not in result.stdout
        
        # Test Tamper Command
        tamper_result = runner.invoke(app, ["tamper", "--result", str(result_file)])
        assert tamper_result.exit_code == 0
        assert "Tampered with" in tamper_result.stdout
        
        with open(result_file, "r") as f:
            tampered_data = json.load(f)
            assert tampered_data["candidate"]["title"] == "HACKED TITLE - TAMPERED METADATA"
            
        # Test Verify Failure due to tamper
        mock_fp_obj_tampered = type("obj", (object,), {"content_hash": "b"*64})
        mock_fp.return_value = mock_fp_obj_tampered
        
        verify_fail_result = runner.invoke(app, ["verify", "--result", str(result_file)])
        assert verify_fail_result.exit_code == 0
        assert "TAMPERED" in verify_fail_result.stdout
        assert "VERIFIED" not in verify_fail_result.stdout
