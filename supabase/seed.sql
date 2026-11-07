-- ==============================================================================
-- LPU GoCart - Campus Seed Data
-- Lovely Professional University (LPU), Phagwara, Punjab
-- Populates default routes, geo-stops, active e-carts, and 8-seat configurations.
-- ==============================================================================

-- 1. Insert Campus Routes
INSERT INTO public.routes (id, name, code, description, fare_amount, is_active)
VALUES 
    ('11111111-1111-1111-1111-111111111111', 'Main Gate - UniMall Express', 'ROUTE-A', 'Direct express loop connecting Gate 1 with UniMall and Engineering Blocks', 10.00, true),
    ('22222222-2222-2222-2222-222222222222', 'Hostels - Academic Loop', 'ROUTE-B', 'Frequent shuttle servicing Boys Hostels (BH-1 to BH-8) and Girls Hostels (GH-1 to GH-6)', 10.00, true),
    ('33333333-3333-3333-3333-333333333333', 'Campus Perimeter Green Line', 'ROUTE-C', 'Circumnavigates campus via Unipolis, Sports Complex, and Gate 4', 15.00, true)
ON CONFLICT (code) DO NOTHING;

-- 2. Insert Route Stops for ROUTE-A (Main Gate - UniMall Express)
INSERT INTO public.route_stops (route_id, name, latitude, longitude, sequence_order, estimated_minutes)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'Main Gate (Gate 1)', 31.25380000, 75.70120000, 1, 0),
    ('11111111-1111-1111-1111-111111111111', 'Block 32 (Engineering)', 31.25450000, 75.70400000, 2, 3),
    ('11111111-1111-1111-1111-111111111111', 'UniMall & Food Court', 31.25290000, 75.70480000, 3, 6),
    ('11111111-1111-1111-1111-111111111111', 'Central Library / Block 34', 31.25520000, 75.70580000, 4, 9)
ON CONFLICT DO NOTHING;

-- 3. Insert Route Stops for ROUTE-B (Hostels - Academic Loop)
INSERT INTO public.route_stops (route_id, name, latitude, longitude, sequence_order, estimated_minutes)
VALUES
    ('22222222-2222-2222-2222-222222222222', 'Boys Hostel (BH-1 to BH-8)', 31.25680000, 75.70820000, 1, 0),
    ('22222222-2222-2222-2222-222222222222', 'Central Library / Block 34', 31.25520000, 75.70580000, 2, 4),
    ('22222222-2222-2222-2222-222222222222', 'Girls Hostel (GH-1 to GH-6)', 31.25150000, 75.70750000, 3, 8),
    ('22222222-2222-2222-2222-222222222222', 'UniMall & Food Court', 31.25290000, 75.70480000, 4, 12)
ON CONFLICT DO NOTHING;

-- 4. Insert Route Stops for ROUTE-C (Perimeter Green Line)
INSERT INTO public.route_stops (route_id, name, latitude, longitude, sequence_order, estimated_minutes)
VALUES
    ('33333333-3333-3333-3333-333333333333', 'Main Gate (Gate 1)', 31.25380000, 75.70120000, 1, 0),
    ('33333333-3333-3333-3333-333333333333', 'Unipolis & Sports Complex', 31.25300000, 75.70250000, 2, 4),
    ('33333333-3333-3333-3333-333333333333', 'Gate 4 / Residential Area', 31.25100000, 75.70050000, 3, 8),
    ('33333333-3333-3333-3333-333333333333', 'Girls Hostel Area', 31.25150000, 75.70750000, 4, 13)
ON CONFLICT DO NOTHING;

-- 5. Insert LPU Electric Carts Fleet
INSERT INTO public.carts (id, cart_number, model, total_seats, battery_percentage, status, current_route_id, has_cctv)
VALUES
    ('a1111111-aaaa-1111-aaaa-111111111111', 'LPU-CART-01', 'Club Car Transporter 8', 8, 92, 'ACTIVE', '11111111-1111-1111-1111-111111111111', true),
    ('a2222222-aaaa-2222-aaaa-222222222222', 'LPU-CART-02', 'Club Car Transporter 8', 8, 85, 'ACTIVE', '11111111-1111-1111-1111-111111111111', true),
    ('a3333333-aaaa-3333-aaaa-333333333333', 'LPU-CART-03', 'Club Car Transporter 8', 8, 78, 'ACTIVE', '22222222-2222-2222-2222-222222222222', true),
    ('a4444444-aaaa-4444-aaaa-444444444444', 'LPU-CART-04', 'Club Car Transporter 8', 8, 45, 'ACTIVE', '22222222-2222-2222-2222-222222222222', false),
    ('a5555555-aaaa-5555-aaaa-555555555555', 'LPU-CART-05', 'Club Car Transporter 8', 8, 100, 'CHARGING', '33333333-3333-3333-3333-333333333333', true),
    ('a6666666-aaaa-6666-aaaa-666666666666', 'LPU-CART-06', 'Club Car Transporter 8', 8, 18, 'MAINTENANCE', NULL, false)
ON CONFLICT (cart_number) DO NOTHING;

-- 6. Insert 8 Seats for Each Registered Cart (S1 through S8)
DO $$
DECLARE
    cart_record RECORD;
    seat_num INT;
BEGIN
    FOR cart_record IN SELECT id FROM public.carts LOOP
        FOR seat_num IN 1..8 LOOP
            INSERT INTO public.cart_seats (cart_id, seat_number, seat_label, is_accessible)
            VALUES (
                cart_record.id,
                seat_num,
                'S' || seat_num,
                CASE WHEN seat_num = 1 THEN true ELSE false END
            )
            ON CONFLICT (cart_id, seat_number) DO NOTHING;
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 7. Insert CCTV Hardware Metadata for equipped carts
INSERT INTO public.cctv_devices (cart_id, device_serial, stream_url, stream_protocol, is_online, last_heartbeat)
VALUES
    ('a1111111-aaaa-1111-aaaa-111111111111', 'CP-PLUS-LPU-CAM-01', 'https://demo-cctv.lpu.in/live/cart01.m3u8', 'HLS', true, NOW()),
    ('a2222222-aaaa-2222-aaaa-222222222222', 'CP-PLUS-LPU-CAM-02', 'https://demo-cctv.lpu.in/live/cart02.m3u8', 'HLS', true, NOW()),
    ('a3333333-aaaa-3333-aaaa-333333333333', 'CP-PLUS-LPU-CAM-03', 'https://demo-cctv.lpu.in/live/cart03.m3u8', 'HLS', false, NOW() - INTERVAL '15 minutes'),
    ('a5555555-aaaa-5555-aaaa-555555555555', 'CP-PLUS-LPU-CAM-05', 'https://demo-cctv.lpu.in/live/cart05.m3u8', 'HLS', true, NOW())
ON CONFLICT (cart_id) DO NOTHING;
