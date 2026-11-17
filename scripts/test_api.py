import sys
import os
sys.path.insert(0, os.path.abspath("backend"))

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# 1. Health test
res = client.get("/health")
print("GET /health ->", res.status_code, res.json())
assert res.status_code == 200

# 2. Routes test
res = client.get("/api/v1/routes")
print("GET /api/v1/routes ->", res.status_code, f"{len(res.json())} routes found")
assert res.status_code == 200
assert len(res.json()) >= 3

# 3. Carts test
res = client.get("/api/v1/carts")
print("GET /api/v1/carts ->", res.status_code, f"{len(res.json())} carts found")
assert res.status_code == 200
assert len(res.json()) >= 4

# 4. Auth test: Customer login
res = client.post("/api/v1/auth/login", json={"email": "customer@lpu.in", "password": "customer123"})
print("POST /api/v1/auth/login (customer) ->", res.status_code, res.json().get("role"))
assert res.status_code == 200
assert res.json().get("role") == "CUSTOMER"
customer_token = res.json()["access_token"]

# 5. Auth test: Driver login
res = client.post("/api/v1/auth/login", json={"email": "driver@lpu.in", "password": "driver123"})
print("POST /api/v1/auth/login (driver) ->", res.status_code, res.json().get("role"))
assert res.status_code == 200
assert res.json().get("role") == "DRIVER"

# 6. Auth test: Admin login
res = client.post("/api/v1/auth/login", json={"email": "admin@lpu.in", "password": "admin123"})
print("POST /api/v1/auth/login (admin) ->", res.status_code, res.json().get("role"))
assert res.status_code == 200
assert res.json().get("role") == "ADMIN"
admin_token = res.json()["access_token"]

# 7. Admin metrics test
res = client.get("/api/v1/admin/metrics", headers={"Authorization": f"Bearer {admin_token}"})
print("GET /api/v1/admin/metrics ->", res.status_code, res.json())
assert res.status_code == 200

print("\n[ALL TESTS PASSED] Backend API, Auth, Roles, and Database are 100% operational!")
