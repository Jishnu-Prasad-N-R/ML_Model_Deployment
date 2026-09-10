import pytest

from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

@pytest.fixture
def client():
    
    with TestClient(app) as test:
        
        yield test
        
@pytest.fixture
def auth_headers():
    
    return {"X-API-Key": settings.API_KEY}