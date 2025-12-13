import pytest
from server.app import app  
from server.app.models import NetspeakPatterns 

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert b'success' in response.data

def test_model_creation(): 
    model = NetspeakPatterns(data={"patterns": ["test"]})
    assert model.is_valid()