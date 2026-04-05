def _login(client, email: str, password: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_viewer_forbidden_on_admin_endpoint(client):
    token = _login(client, "viewer@example.com", "viewer1234")
    response = client.get("/users", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "forbidden"


def test_viewer_can_read_dashboard_but_not_records(client):
    token = _login(client, "viewer@example.com", "viewer1234")

    dashboard_response = client.get("/dashboard/summary", headers={"Authorization": f"Bearer {token}"})
    records_response = client.get("/financial-records", headers={"Authorization": f"Bearer {token}"})

    assert dashboard_response.status_code == 200
    assert records_response.status_code == 403


def test_analyst_forbidden_on_record_write(client):
    token = _login(client, "analyst@example.com", "analyst1234")
    response = client.post(
        "/financial-records",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "amount": "250.00",
            "type": "expense",
            "category": "travel",
            "record_date": "2026-04-03",
            "notes": "Taxi",
        },
    )

    assert response.status_code == 403


def test_admin_can_create_record(client):
    token = _login(client, "admin@example.com", "admin1234")
    response = client.post(
        "/financial-records",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "amount": "250.00",
            "type": "expense",
            "category": "travel",
            "record_date": "2026-04-03",
            "notes": "Taxi",
        },
    )

    assert response.status_code == 201
    assert response.json()["category"] == "travel"


def test_summary_report_returns_expected_totals(client):
    token = _login(client, "analyst@example.com", "analyst1234")
    response = client.get("/reports/summary", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_income"] == "1000.00"
    assert payload["total_expense"] == "300.00"
    assert payload["net_balance"] == "700.00"
