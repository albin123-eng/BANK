def test_transfer_creates_transactions(client):
    # user A
    client.post("/auth/register", json={
        "email": "a@test.com",
        "username": "a",
        "first_name": "A",
        "last_name": "User",
        "password": "Pass123!"
    })

    # user B
    client.post("/auth/register", json={
        "email": "b@test.com",
        "username": "b",
        "first_name": "B",
        "last_name": "User",
        "password": "Pass123!"
    })

    # login A
    resp = client.post("/auth/token", data={
        "username": "a",
        "password": "Pass123!"
    })
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # deposit first
    client.post("/account/deposit", json={"amount": 100}, headers=headers)

    # transfer
    r = client.post(
        "/transfer",
        json={"to_account_id": 2, "amount": 50},
        headers=headers
    )

    assert r.status_code == 200
    assert r.json()["message"] == "Transfer successful"
