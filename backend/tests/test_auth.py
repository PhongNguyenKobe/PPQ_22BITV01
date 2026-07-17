from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_login_admin():
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@cineai.vn", "password": "admin123"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_login_customer():
    response = client.post(
        "/api/auth/login",
        json={"email": "customer@gmail.com", "password": "customer123"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "customer"


def test_register_customer_v1_endpoint():
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "User Test", "email": "newuser@example.com", "password": "secret123"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "customer"
    assert response.json()["email"] == "newuser@example.com"


def test_login_v1_endpoint():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@cineai.vn", "password": "admin123"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_protected_admin_endpoint_requires_token():
    response = client.get("/api/admin/dashboard")
    assert response.status_code == 401


def test_checkout_creates_order_and_returns_history():
    login_response = client.post(
        "/api/auth/login",
        json={"email": "customer@gmail.com", "password": "customer123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    checkout_response = client.post(
        "/api/orders/checkout",
        json={
            "items": [
                {
                    "product_id": "p1",
                    "title": "Test Movie Ticket",
                    "quantity": 2,
                    "unit_price": 50000,
                }
            ]
        },
        headers=headers,
    )
    assert checkout_response.status_code == 200
    order_data = checkout_response.json()
    assert order_data["user_email"] == "customer@gmail.com"
    assert order_data["subtotal_amount"] == 100000
    assert order_data["total_amount"] == 100000
    assert order_data["status"] == "PENDING"
    assert len(order_data["items"]) == 1

    history_response = client.get("/api/orders/my", headers=headers)
    assert history_response.status_code == 200
    history_data = history_response.json()
    assert isinstance(history_data, list)
    assert any(order["id"] == order_data["id"] for order in history_data)

    get_response = client.get(f"/api/orders/{order_data['id']}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == order_data["id"]
