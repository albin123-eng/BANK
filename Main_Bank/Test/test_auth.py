def test_register_creates_account(client):
    payload = {
        "email": "test1@test.com",
        "username": "test1",
        "first_name": "Test",
        "last_name": "User",
        "password": "Pass123!"
    }

    r = client.post("/auth/register", json=payload)
    assert r.status_code in (200, 201)

    data = r.json()
    assert data["username"] == "test1"
    assert data["balance"] == 0
    assert "account_id" in data
