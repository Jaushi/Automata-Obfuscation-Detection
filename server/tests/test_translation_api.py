import pytest
import json
from app.utils import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_translate_endpoint_success(client):
    payload = {"text": "m4h4l k1t4 q"}
    response = client.post('/api/translate', 
                           data=json.dumps(payload),
                           content_type='application/json')
    
    data = response.get_json()
    assert response.status_code == 200
    assert data['success'] is True
    assert "mahal kita ko" in data['translated']

def test_translate_endpoint_no_data(client):
    response = client.post('/api/translate', 
                           data=json.dumps({}),
                           content_type='application/json')
    assert response.status_code == 400