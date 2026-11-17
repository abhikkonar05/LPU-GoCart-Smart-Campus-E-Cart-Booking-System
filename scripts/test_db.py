"""
LPU GoCart - Database Health & Seed Verification Script
Tests SQLAlchemy models, database connection, and seeded records.
"""

import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.database.connection import engine, SessionLocal, Base, DATABASE_URL
from app.database.models import User, Cart, Route, RouteStop, CartSeat
from app.database.seed import seed_database

print("=" * 60)
print("     LPU GoCart - Database Connection & Seed Diagnostic")
print("=" * 60)
print(f"DATABASE_URL : {DATABASE_URL}")
print(f"DIALECT      : {engine.dialect.name}")
print("-" * 60)

try:
    # 1. Run Seed
    print("[1/4] Running schema initialization and seed data...")
    seed_database()
    print("[OK] Schema & seed executed without errors.")

    # 2. Query Users
    db = SessionLocal()
    print("\n[2/4] Verifying Default Role Accounts:")
    users = db.query(User).all()
    for u in users:
        print(f"     - {u.role:<8} : {u.email:<20} ({u.full_name})")

    # 3. Query Routes & Stops
    print("\n[3/4] Verifying Campus Routes:")
    routes = db.query(Route).all()
    for r in routes:
        stops_count = len(r.stops)
        print(f"     - [{r.code}] {r.name:<32} (Fare: Rs.{r.fare_amount}, Stops: {stops_count})")

    # 4. Query Carts & Seats
    print("\n[4/4] Verifying Fleet & 6-Seat Capacities:")
    carts = db.query(Cart).all()
    for c in carts:
        seats_count = len(c.seats)
        print(f"     - Cart {c.cart_number} : {c.name:<18} ({seats_count} seats, Battery: {c.battery_percentage}%, Status: {c.cart_status})")

    db.close()
    print("\n" + "=" * 60)
    print(" [SUCCESS] Phase 2 Database verified and fully operational!")
    print("=" * 60)

except Exception as e:
    print(f"\n[ERROR] Database diagnostic encountered an error: {e}")
    sys.exit(1)
