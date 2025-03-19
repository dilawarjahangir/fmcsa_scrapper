import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_query_carrier():
    response = client.post("/api/carrier", json={"mc_number": "1684710"})
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data
