"""
LPU GoCart - Automated Database Seed & Bootstrap
Populates initial users (ADMIN, DRIVER, CUSTOMER), campus routes, stops, and carts.
"""

import logging
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal, Base, engine
from app.database.models import User, Route, RouteStop, Cart, CartSeat
from app.core.security import get_password_hash

logger = logging.getLogger("lpu_gocart.seed")

def seed_database(db: Session = None):
    """Seed default records if tables are empty."""
    close_at_end = False
    if db is None:
        db = SessionLocal()
        close_at_end = True

    try:
        # Ensure tables exist
        Base.metadata.create_all(bind=engine)

        # 1. Seed Users if not present
        admin = db.query(User).filter(User.email == "admin@lpu.in").first()
        if not admin:
            admin = User(
                id="99999999-9999-9999-9999-999999999999",
                email="admin@lpu.in",
                hashed_password=get_password_hash("admin123"),
                full_name="LPU Transport Admin",
                phone_number="+919876543210",
                role="ADMIN",
                is_active=True
            )
            db.add(admin)

        driver = db.query(User).filter(User.email == "driver@lpu.in").first()
        if not driver:
            driver = User(
                id="88888888-8888-8888-8888-888888888888",
                email="driver@lpu.in",
                hashed_password=get_password_hash("driver123"),
                full_name="Rajinder Singh",
                phone_number="+919812345678",
                role="DRIVER",
                is_active=True
            )
            db.add(driver)

        customer = db.query(User).filter(User.email == "customer@lpu.in").first()
        if not customer:
            customer = User(
                id="77777777-7777-7777-7777-777777777777",
                email="customer@lpu.in",
                hashed_password=get_password_hash("customer123"),
                full_name="Aman Sharma",
                phone_number="+919876501234",
                role="CUSTOMER",
                is_active=True
            )
            db.add(customer)

        db.flush()

        # 2. Seed Routes if not present
        if db.query(Route).count() == 0:
            route_a = Route(
                id="11111111-1111-1111-1111-111111111111",
                name="Main Gate - UniMall Express",
                code="ROUTE-A",
                start_point="Main Gate (Gate 1)",
                destination="UniMall & Food Court",
                description="Direct express loop connecting Gate 1 with UniMall and Engineering Blocks",
                fare_amount=10.0,
                estimated_duration_minutes=10,
                distance_km=1.8,
                is_active=True
            )
            db.add(route_a)
            db.flush()

            stops_a = [
                RouteStop(route_id=route_a.id, name="Main Gate (Gate 1)", latitude=31.2538, longitude=75.7012, sequence_order=1, estimated_minutes=0),
                RouteStop(route_id=route_a.id, name="Block 32 (Engineering)", latitude=31.2545, longitude=75.7040, sequence_order=2, estimated_minutes=3),
                RouteStop(route_id=route_a.id, name="UniMall & Food Court", latitude=31.2529, longitude=75.7048, sequence_order=3, estimated_minutes=6),
                RouteStop(route_id=route_a.id, name="Central Library / Block 34", latitude=31.2552, longitude=75.7058, sequence_order=4, estimated_minutes=10),
            ]
            db.add_all(stops_a)

            route_b = Route(
                id="22222222-2222-2222-2222-222222222222",
                name="Hostels - Central Academic Loop",
                code="ROUTE-B",
                start_point="Boys Hostels (BH 1-8)",
                destination="Girls Hostels (GH 1-6)",
                description="Frequent shuttle servicing student residential hostels and library",
                fare_amount=10.0,
                estimated_duration_minutes=15,
                distance_km=2.4,
                is_active=True
            )
            db.add(route_b)
            db.flush()

            stops_b = [
                RouteStop(route_id=route_b.id, name="Boys Hostels (BH 1-8)", latitude=31.2568, longitude=75.7082, sequence_order=1, estimated_minutes=0),
                RouteStop(route_id=route_b.id, name="Central Library / Block 34", latitude=31.2552, longitude=75.7058, sequence_order=2, estimated_minutes=4),
                RouteStop(route_id=route_b.id, name="Girls Hostels (GH 1-6)", latitude=31.2515, longitude=75.7075, sequence_order=3, estimated_minutes=8),
                RouteStop(route_id=route_b.id, name="UniMall & Food Court", latitude=31.2529, longitude=75.7048, sequence_order=4, estimated_minutes=14),
            ]
            db.add_all(stops_b)

            route_c = Route(
                id="33333333-3333-3333-3333-333333333333",
                name="Campus Perimeter Green Line",
                code="ROUTE-C",
                start_point="Main Gate (Gate 1)",
                destination="Gate 4 / Residential Area",
                description="Circumnavigates campus via Unipolis, stadium, and residential blocks",
                fare_amount=15.0,
                estimated_duration_minutes=20,
                distance_km=3.5,
                is_active=True
            )
            db.add(route_c)
            db.flush()

            stops_c = [
                RouteStop(route_id=route_c.id, name="Main Gate (Gate 1)", latitude=31.2538, longitude=75.7012, sequence_order=1, estimated_minutes=0),
                RouteStop(route_id=route_c.id, name="Unipolis & Sports Complex", latitude=31.2530, longitude=75.7025, sequence_order=2, estimated_minutes=4),
                RouteStop(route_id=route_c.id, name="Gate 4 / Residential Area", latitude=31.2510, longitude=75.7005, sequence_order=3, estimated_minutes=8),
                RouteStop(route_id=route_c.id, name="Girls Hostel Area", latitude=31.2515, longitude=75.7075, sequence_order=4, estimated_minutes=14),
            ]
            db.add_all(stops_c)

        # 3. Seed Carts if not present
        if db.query(Cart).count() == 0:
            cart1 = Cart(
                id="a1111111-aaaa-1111-aaaa-111111111111",
                cart_number="LPU-GC-001",
                name="Express Green 1",
                model="Club Car Transporter 6",
                total_passenger_seats=6,
                luggage_capacity_small=4,
                luggage_capacity_medium=3,
                luggage_capacity_large=2,
                current_route_id="11111111-1111-1111-1111-111111111111",
                driver_id="88888888-8888-8888-8888-888888888888",
                battery_percentage=94,
                cart_status="AVAILABLE",
                gps_status="LIVE"
            )
            cart2 = Cart(
                id="a2222222-aaaa-2222-aaaa-222222222222",
                cart_number="LPU-GC-002",
                name="Express Green 2",
                model="Club Car Transporter 6",
                total_passenger_seats=6,
                luggage_capacity_small=4,
                luggage_capacity_medium=3,
                luggage_capacity_large=2,
                current_route_id="11111111-1111-1111-1111-111111111111",
                battery_percentage=88,
                cart_status="AVAILABLE",
                gps_status="LIVE"
            )
            cart3 = Cart(
                id="a3333333-aaaa-3333-aaaa-333333333333",
                cart_number="LPU-GC-003",
                name="Hostel Shuttle 1",
                model="Club Car Transporter 6",
                total_passenger_seats=6,
                luggage_capacity_small=4,
                luggage_capacity_medium=3,
                luggage_capacity_large=2,
                current_route_id="22222222-2222-2222-2222-222222222222",
                battery_percentage=72,
                cart_status="AVAILABLE",
                gps_status="LIVE"
            )
            cart4 = Cart(
                id="a4444444-aaaa-4444-aaaa-444444444444",
                cart_number="LPU-GC-004",
                name="Hostel Shuttle 2",
                model="Club Car Transporter 6",
                total_passenger_seats=6,
                luggage_capacity_small=4,
                luggage_capacity_medium=3,
                luggage_capacity_large=2,
                current_route_id="22222222-2222-2222-2222-222222222222",
                battery_percentage=100,
                cart_status="AVAILABLE",
                gps_status="OFFLINE"
            )
            db.add_all([cart1, cart2, cart3, cart4])
            db.flush()

            for c in [cart1, cart2, cart3, cart4]:
                for s in range(1, c.total_passenger_seats + 1):
                    seat = CartSeat(
                        cart_id=c.id,
                        seat_number=s,
                        seat_label=f"S{s}",
                        is_accessible=(s == 1)
                    )
                    db.add(seat)

        db.commit()
        logger.info("[SEED] Database seed completed successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"[SEED] Error seeding database: {e}")
    finally:
        if close_at_end:
            db.close()

if __name__ == "__main__":
    seed_database()
