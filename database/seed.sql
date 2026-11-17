-- ==============================================================================
-- LPU GoCart - Campus Seed Data (PostgreSQL)
-- Lovely Professional University (LPU), Phagwara, Punjab
-- ==============================================================================

-- 1. Insert Campus Routes
INSERT INTO routes (id, name, code, start_point, destination, description, fare_amount, estimated_duration_minutes, distance_km, is_active)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'Main Gate - UniMall Express', 'ROUTE-A', 'Main Gate (Gate 1)', 'UniMall & Food Court', 'Express shuttle connecting Gate 1 with UniMall and Academic Blocks', 10.00, 10, 1.8, true),
    ('22222222-2222-2222-2222-222222222222', 'Hostels - Central Academic Loop', 'ROUTE-B', 'Boys Hostels (BH 1-8)', 'Girls Hostels (GH 1-6)', 'Frequent service connecting student residential hostels with library and lecture halls', 10.00, 15, 2.4, true),
    ('33333333-3333-3333-3333-333333333333', 'Campus Perimeter Green Line', 'ROUTE-C', 'Main Gate (Gate 1)', 'Gate 4 / Residential Area', 'Circumnavigates campus via Unipolis, stadium, and residential blocks', 15.00, 20, 3.5, true)
ON CONFLICT (code) DO NOTHING;

-- 2. Insert Stops for ROUTE-A
INSERT INTO route_stops (route_id, name, latitude, longitude, sequence_order, estimated_minutes)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'Main Gate (Gate 1)', 31.25380000, 75.70120000, 1, 0),
    ('11111111-1111-1111-1111-111111111111', 'Block 32 (Engineering)', 31.25450000, 75.70400000, 2, 3),
    ('11111111-1111-1111-1111-111111111111', 'UniMall & Food Court', 31.25290000, 75.70480000, 3, 6),
    ('11111111-1111-1111-1111-111111111111', 'Central Library / Block 34', 31.25520000, 75.70580000, 4, 10)
ON CONFLICT DO NOTHING;

-- 3. Insert Stops for ROUTE-B
INSERT INTO route_stops (route_id, name, latitude, longitude, sequence_order, estimated_minutes)
VALUES
    ('22222222-2222-2222-2222-222222222222', 'Boys Hostels (BH 1-8)', 31.25680000, 75.70820000, 1, 0),
    ('22222222-2222-2222-2222-222222222222', 'Central Library / Block 34', 31.25520000, 75.70580000, 2, 4),
    ('22222222-2222-2222-2222-222222222222', 'Girls Hostels (GH 1-6)', 31.25150000, 75.70750000, 3, 8),
    ('22222222-2222-2222-2222-222222222222', 'UniMall & Food Court', 31.25290000, 75.70480000, 4, 14)
ON CONFLICT DO NOTHING;

-- 4. Insert Carts (LPU-GC-001 through LPU-GC-004)
INSERT INTO carts (id, cart_number, name, model, total_passenger_seats, luggage_capacity_small, luggage_capacity_medium, luggage_capacity_large, current_route_id, battery_percentage, cart_status, gps_status)
VALUES
    ('a1111111-aaaa-1111-aaaa-111111111111', 'LPU-GC-001', 'Express Green 1', 'Club Car Transporter 6', 6, 4, 3, 2, '11111111-1111-1111-1111-111111111111', 94, 'AVAILABLE', 'LIVE'),
    ('a2222222-aaaa-2222-aaaa-222222222222', 'LPU-GC-002', 'Express Green 2', 'Club Car Transporter 6', 6, 4, 3, 2, '11111111-1111-1111-1111-111111111111', 88, 'ON_TRIP', 'LIVE'),
    ('a3333333-aaaa-3333-aaaa-333333333333', 'LPU-GC-003', 'Hostel Shuttle 1', 'Club Car Transporter 6', 6, 4, 3, 2, '22222222-2222-2222-2222-222222222222', 72, 'AVAILABLE', 'LIVE'),
    ('a4444444-aaaa-4444-aaaa-444444444444', 'LPU-GC-004', 'Hostel Shuttle 2', 'Club Car Transporter 6', 6, 4, 3, 2, '22222222-2222-2222-2222-222222222222', 100, 'AVAILABLE', 'OFFLINE')
ON CONFLICT (cart_number) DO NOTHING;

-- 5. Insert 6 Seats for Each Registered Cart (S1 through S6)
DO $$
DECLARE
    cart_row RECORD;
    seat_i INT;
BEGIN
    FOR cart_row IN SELECT id FROM carts LOOP
        FOR seat_i IN 1..6 LOOP
            INSERT INTO cart_seats (cart_id, seat_number, seat_label, is_accessible)
            VALUES (
                cart_row.id,
                seat_i,
                'S' || seat_i,
                CASE WHEN seat_i = 1 THEN true ELSE false END
            )
            ON CONFLICT (cart_id, seat_number) DO NOTHING;
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
