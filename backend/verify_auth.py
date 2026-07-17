from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

for path, payload in [
    ('/api/v1/auth/login', {'email':'admin@cineai.vn','password':'admin123'}),
    ('/api/v1/auth/register', {'name':'User Test','email':'newuser@example.com','password':'secret123'}),
]:
    resp = client.post(path, json=payload)
    print(path, resp.status_code, resp.json())
