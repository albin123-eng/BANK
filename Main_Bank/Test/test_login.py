def test_login(client):
    client.post("/auth/register", json={
        "email": "test2@test.com",
        "username": "test2",
        "first_name": "Test",
        "last_name": "User",
        "password": "Pass123!"
    })

    r = client.post("/auth/token", data={"username": "test2", "password": "Pass123!"})

    assert r.status_code == 200
    assert "access_token" in r.json()
