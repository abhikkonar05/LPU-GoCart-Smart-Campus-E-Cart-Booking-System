"""
LPU GoCart - Authentication & User Role Tests
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_student_registration_and_login():
    email = f"test_student_unique@lpu.in"
    reg_payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Aman Sharma",
        "phone_number": "+919876543211",
        "role": "STUDENT",
        "registration_number": "12104599",
        "department": "Computer Science",
        "hostel_block": "BH-3"
    }

    # Register
    res = client.post("/api/v1/auth/register", json=reg_payload)
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "STUDENT"
    assert data["email"] == email

    # Login
    login_payload = {
        "email": email,
        "password": "Password123!"
    }
    login_res = client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # Verify Profile via /auth/me
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == email
    assert me_data["role"] == "STUDENT"
    assert me_data["registration_number"] == "12104599"

def test_login_invalid_password():
    payload = {
        "email": "admin@lpu.in",
        "password": "WrongPassword999"
    }
    res = client.post("/api/v1/auth/login", json=payload)
    assert res.status_code == 401

