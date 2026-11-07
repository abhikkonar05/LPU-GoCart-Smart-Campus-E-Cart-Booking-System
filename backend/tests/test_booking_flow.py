"""
LPU GoCart - End-to-End Booking, Atomic Seat Locking & Demo Payment Test
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_auth_token(email: str, password: str, full_name: str, reg_no: str) -> str:
    # Try login, if fails, register
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    if res.status_code == 200:
        return res.json()["access_token"]
    
    reg_res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": full_name,
        "role": "STUDENT",
        "registration_number": reg_no
    })
    return reg_res.json()["access_token"]

def test_routes_listing():
    res = client.get("/api/v1/routes")
    assert res.status_code == 200
    routes = res.json()
    assert len(routes) >= 3
    codes = [r["code"] for r in routes]
    assert "ROUTE-A" in codes

def test_carts_listing():
    res = client.get("/api/v1/carts")
    assert res.status_code == 200
    carts = res.json()
    assert len(carts) >= 1
    assert "cart_number" in carts[0]

def test_atomic_seat_locking_and_duplicate_prevention():
    token_student1 = get_auth_token("student_alpha@lpu.in", "Pass123!", "Alpha Student", "12101111")
    token_student2 = get_auth_token("student_beta@lpu.in", "Pass123!", "Beta Student", "12102222")

    # Get first cart and its seats
    carts_res = client.get("/api/v1/carts")
    cart_id = carts_res.json()[0]["id"]
    
    cart_detail = client.get(f"/api/v1/carts/{cart_id}").json()
    seat = cart_detail["seats"][1] # Seat S2
    seat_id = seat["id"]

    # Student 1 locks Seat S2
    lock_payload = {
        "cart_id": cart_id,
        "trip_id": "", # Service finds active trip
        "seat_id": seat_id
    }
    headers1 = {"Authorization": f"Bearer {token_student1}"}
    lock_res1 = client.post("/api/v1/bookings/lock-seat", json=lock_payload, headers=headers1)
    assert lock_res1.status_code == 200
    lock_data = lock_res1.json()
    lock_id = lock_data["lock_id"]
    trip_id = lock_data["trip_id"]

    # Student 2 tries to lock the SAME Seat S2 concurrently -> MUST BE REJECTED (409 Conflict)!
    headers2 = {"Authorization": f"Bearer {token_student2}"}
    lock_res2 = client.post("/api/v1/bookings/lock-seat", json=lock_payload, headers=headers2)
    assert lock_res2.status_code == 409
    assert "currently held" in lock_res2.json()["detail"]

    # Student 1 creates pending booking
    routes = client.get("/api/v1/routes").json()
    route = routes[0]
    pickup_stop_id = route["stops"][0]["id"]
    drop_stop_id = route["stops"][1]["id"]

    booking_payload = {
        "lock_id": lock_id,
        "trip_id": trip_id,
        "cart_id": cart_id,
        "seat_id": seat_id,
        "pickup_stop_id": pickup_stop_id,
        "drop_stop_id": drop_stop_id,
        "fare_amount": 10.0
    }
    booking_res = client.post("/api/v1/bookings/create-pending", json=booking_payload, headers=headers1)
    assert booking_res.status_code == 201
    booking_id = booking_res.json()["id"]

    # Student 1 creates payment intent
    intent_res = client.post("/api/v1/payments/create-intent", json={
        "booking_id": booking_id,
        "amount": 10.0,
        "gateway": "demo"
    }, headers=headers1)
    assert intent_res.status_code == 200
    payment_id = intent_res.json()["payment_id"]

    # Student 1 confirms Demo Payment
    pay_res = client.post("/api/v1/payments/demo-confirm", json={
        "payment_id": payment_id,
        "booking_id": booking_id,
        "simulate_status": "SUCCESS"
    }, headers=headers1)
    assert pay_res.status_code == 200
    pay_data = pay_res.json()
    assert pay_data["success"] is True
    assert pay_data["booking_status"] == "CONFIRMED"

    # Verify Boarding QR Ticket generated
    ticket_res = client.get(f"/api/v1/bookings/{booking_id}/ticket", headers=headers1)
    assert ticket_res.status_code == 200
    ticket = ticket_res.json()
    assert "qr_token" in ticket
    assert ticket["qr_token"].startswith("LPU-TICKET:")

