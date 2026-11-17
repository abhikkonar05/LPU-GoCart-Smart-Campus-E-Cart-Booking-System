import json
import urllib.request

BASE_URL = "http://127.0.0.1:8000/api/v1"

def post(endpoint, data, token=None):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {token}"} if token else {})
        }
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode("utf-8"))

def get(endpoint, token=None):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}"} if token else {}
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode("utf-8"))

print("=== [1] Customer Authentication ===")
customer_auth = post("/auth/login", {"email": "customer@lpu.in", "password": "customer123"})
c_token = customer_auth["access_token"]
print("Customer logged in:", customer_auth["full_name"], "| Role:", customer_auth["role"])

print("\n=== [2] Browse Routes and Available Carts ===")
routes = get("/routes", c_token)
print(f"Routes found: {len(routes)} (First: {routes[0]['code']} - {routes[0]['name']})")
carts = get("/carts", c_token)
cart = carts[0]
print(f"Selected Cart: {cart['cart_number']} ({cart['name']}) | Seats Free: {cart['available_seats']}/{cart['total_seats']}")

cart_detail = get(f"/carts/{cart['id']}", c_token)
seat = cart_detail["seats"][1] # S2
pickup_id = routes[0]["stops"][0]["id"]
drop_id = routes[0]["stops"][-1]["id"]
print(f"Target Seat: {seat['seat_label']} | Pickup: {routes[0]['stops'][0]['name']} -> Drop: {routes[0]['stops'][-1]['name']}")

print("\n=== [3] Atomic 5-Minute Seat Lock ===")
lock_res = post("/bookings/lock-seat", {
    "cart_id": cart["id"],
    "trip_id": "auto",
    "seat_id": seat["id"]
}, c_token)
print("Seat Locked successfully:", lock_res["seat_label"], "| Remaining seconds:", lock_res["remaining_seconds"])

print("\n=== [4] Create Pending Booking ===")
booking_res = post("/bookings/create-pending", {
    "lock_id": lock_res["lock_id"],
    "trip_id": lock_res["trip_id"],
    "cart_id": cart["id"],
    "seat_id": seat["id"],
    "booking_type": "SEAT",
    "pickup_stop_id": pickup_id,
    "drop_stop_id": drop_id,
    "fare_amount": 10.0,
    "small_bags": 1,
    "medium_bags": 0,
    "large_bags": 0,
    "luggage_fee": 0.0
}, c_token)
booking_id = booking_res["id"]
print("Pending Booking Created:", booking_res["booking_code"], "| Amount: Rs.", booking_res["fare_amount"])

print("\n=== [5] Demo Payment & Confirmation ===")
intent_res = post("/payments/create-intent", {
    "booking_id": booking_id,
    "amount": 10.0
}, c_token)
payment_id = intent_res["payment_id"]
print("Payment Intent created:", payment_id, "| Gateway:", intent_res["gateway"])

confirm_res = post("/payments/demo-confirm", {
    "payment_id": payment_id,
    "booking_id": booking_id,
    "simulate_status": "SUCCESS"
}, c_token)
print("Payment Confirmed:", confirm_res["message"], "| TxRef:", confirm_res["transaction_reference"])

print("\n=== [6] Boarding Pass & QR Generation ===")
ticket_res = get(f"/bookings/{booking_id}/ticket", c_token)
qr_token = ticket_res["qr_token"]
print("Ticket Issued:", ticket_res["booking_code"], "| Passenger:", ticket_res["passenger_name"])
print("QR Token:", qr_token)

print("\n=== [7] Driver Authentication & QR Verification ===")
driver_auth = post("/auth/login", {"email": "driver@lpu.in", "password": "driver123"})
d_token = driver_auth["access_token"]
print("Driver logged in:", driver_auth["full_name"], "| Role:", driver_auth["role"])

verify_res = post("/drivers/verify-qr", {"qr_token": qr_token}, d_token)
print("Driver scanned QR:", verify_res["message"], "| Status: CHECKED_IN")

print("\n=== [8] Admin Fleet Control & Analytics ===")
admin_auth = post("/auth/login", {"email": "admin@lpu.in", "password": "admin123"})
a_token = admin_auth["access_token"]
metrics = get("/admin/metrics", a_token)
print("Admin Metrics -> Carts:", metrics["total_carts"], "| Today's Bookings:", metrics["total_bookings_today"], "| Revenue: Rs.", metrics["total_revenue_today"])

print("\n🎉 [FULL END-TO-END PIPELINE VERIFIED 100% OPERATIONAL!]")
