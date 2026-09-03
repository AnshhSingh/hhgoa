def test_app_imports():
    from app import face
    from app import search
    from app import matcher
    from app import hashing
    from app import blockchain
    from app import pipeline
    from app import models
    
    assert face is not None
    assert search is not None
    assert matcher is not None
    assert hashing is not None
    assert blockchain is not None
    assert pipeline is not None
    assert models is not None
