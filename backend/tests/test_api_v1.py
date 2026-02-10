import pytest
from datetime import date, timedelta

def test_auth_flow(client):
    # 1. Register
    register_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    response = client.post("/auth/register", json=register_data)
    assert response.status_code == 200
    assert response.json()["email"] == register_data["email"]
    
    # 2. Login
    login_data = {
        "username": register_data["email"],
        "password": register_data["password"]
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None
    
    # 3. Get Me
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == register_data["email"]

def test_user_update(client):
    # Register and login
    register_data = {"email": "update@example.com", "password": "password"}
    client.post("/auth/register", json=register_data)
    login_data = {"username": register_data["email"], "password": register_data["password"]}
    token = client.post("/auth/login", data=login_data).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Update profile
    update_data = {
        "full_name": "Updated Name",
        "emoji": "🚀",
        "start_date": str(date.today()),
        "deadline": str(date.today() + timedelta(days=365))
    }
    response = client.put("/users/me", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["emoji"] == update_data["emoji"]
    assert data["start_date"] == update_data["start_date"]
    assert data["deadline"] == update_data["deadline"]

def test_grid_weeks(client):
    # Register and login
    register_data = {"email": "weeks@example.com", "password": "password"}
    client.post("/auth/register", json=register_data)
    token = client.post("/auth/login", data={"username": "weeks@example.com", "password": "password"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create week progress
    week_data = {
        "week_start_date": str(date.today()),
        "is_completed": True,
        "note": "Great week"
    }
    response = client.post("/grid/weeks", json=week_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["is_completed"] is True
    
    # Get weeks
    response = client.get("/grid/weeks", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["note"] == "Great week"

def test_special_periods(client):
    # Register and login
    register_data = {"email": "periods@example.com", "password": "password"}
    client.post("/auth/register", json=register_data)
    token = client.post("/auth/login", data={"username": "periods@example.com", "password": "password"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create special period
    period_data = {
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=7)),
        "period_type": "vacation",
        "description": "Beach time"
    }
    response = client.post("/grid/special-periods", json=period_data, headers=headers)
    assert response.status_code == 200
    period_id = response.json()["id"]
    
    # Get special periods
    response = client.get("/grid/special-periods", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    
    # Delete special period
    response = client.delete(f"/grid/special-periods/{period_id}", headers=headers)
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get("/grid/special-periods", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 0
