-- ==============================================================================
-- LPU GoCart - Smart Campus E-Cart Database Schema (PostgreSQL)
-- Lovely Professional University (LPU), Phagwara, Punjab
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    role VARCHAR(20) NOT NULL DEFAULT 'CUSTOMER' CHECK (role IN ('ADMIN', 'DRIVER', 'CUSTOMER')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. ROUTES TABLE
CREATE TABLE IF NOT EXISTS routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    start_point VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    description TEXT,
    fare_amount DECIMAL(8,2) NOT NULL DEFAULT 10.00,
    estimated_duration_minutes INT NOT NULL DEFAULT 15,
    distance_km DECIMAL(5,2) NOT NULL DEFAULT 2.50,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. ROUTE STOPS TABLE
CREATE TABLE IF NOT EXISTS route_stops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_id UUID NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    sequence_order INT NOT NULL,
    estimated_minutes INT NOT NULL DEFAULT 2,
    CONSTRAINT uq_route_stop_seq UNIQUE (route_id, sequence_order)
);

-- 4. CARTS TABLE
CREATE TABLE IF NOT EXISTS carts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_number VARCHAR(30) UNIQUE NOT NULL, -- e.g., "LPU-GC-001"
    name VARCHAR(100) NOT NULL,
    model VARCHAR(50) NOT NULL DEFAULT 'Club Car Transporter 8',
    total_passenger_seats INT NOT NULL DEFAULT 6 CHECK (total_passenger_seats > 0),
    luggage_capacity_small INT NOT NULL DEFAULT 4,
    luggage_capacity_medium INT NOT NULL DEFAULT 3,
    luggage_capacity_large INT NOT NULL DEFAULT 2,
    current_route_id UUID REFERENCES routes(id) ON DELETE SET NULL,
    driver_id UUID REFERENCES users(id) ON DELETE SET NULL,
    battery_percentage INT NOT NULL DEFAULT 100 CHECK (battery_percentage BETWEEN 0 AND 100),
    cart_status VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE' CHECK (cart_status IN ('AVAILABLE', 'ASSIGNED', 'ON_TRIP', 'FULL', 'MAINTENANCE', 'OFFLINE')),
    gps_status VARCHAR(20) NOT NULL DEFAULT 'OFFLINE' CHECK (gps_status IN ('LIVE', 'STOPPED', 'OFFLINE')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. CART SEATS TABLE
CREATE TABLE IF NOT EXISTS cart_seats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id UUID NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    seat_number INT NOT NULL,
    seat_label VARCHAR(10) NOT NULL,
    is_accessible BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_cart_seat UNIQUE (cart_id, seat_number)
);

-- 6. TRIPS TABLE
CREATE TABLE IF NOT EXISTS trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id UUID NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    driver_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    route_id UUID NOT NULL REFERENCES routes(id) ON DELETE RESTRICT,
    status VARCHAR(20) NOT NULL DEFAULT 'SCHEDULED' CHECK (status IN ('SCHEDULED', 'ACTIVE', 'COMPLETED', 'CANCELLED')),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. SEAT LOCKS (5-MINUTE TEMPORARY LOCKS)
CREATE TABLE IF NOT EXISTS seat_locks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    seat_id UUID NOT NULL REFERENCES cart_seats(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    locked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    is_released BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_uq_active_seat_lock 
    ON seat_locks (trip_id, seat_id) 
    WHERE is_released = FALSE;

-- 8. CART LOCKS (FOR FULL CART BOOKING)
CREATE TABLE IF NOT EXISTS cart_locks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    cart_id UUID NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    locked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    is_released BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_uq_active_cart_lock 
    ON cart_locks (trip_id, cart_id) 
    WHERE is_released = FALSE;

-- 9. BOOKINGS TABLE
CREATE TABLE IF NOT EXISTS bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_code VARCHAR(25) UNIQUE NOT NULL, -- e.g., "LPU-BK-981203"
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE RESTRICT,
    cart_id UUID NOT NULL REFERENCES carts(id) ON DELETE RESTRICT,
    booking_type VARCHAR(20) NOT NULL DEFAULT 'SEAT' CHECK (booking_type IN ('SEAT', 'FULL_CART')),
    pickup_stop_id UUID NOT NULL REFERENCES route_stops(id) ON DELETE RESTRICT,
    drop_stop_id UUID NOT NULL REFERENCES route_stops(id) ON DELETE RESTRICT,
    seat_id UUID REFERENCES cart_seats(id) ON DELETE SET NULL,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 10.00,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'CONFIRMED', 'CHECKED_IN', 'COMPLETED', 'CANCELLED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Crucial: Unique constraint preventing double confirmation of same seat on same trip
CREATE UNIQUE INDEX IF NOT EXISTS idx_uq_confirmed_seat 
    ON bookings (trip_id, seat_id) 
    WHERE status IN ('CONFIRMED', 'CHECKED_IN');

-- 10. LUGGAGE BOOKINGS TABLE
CREATE TABLE IF NOT EXISTS luggage_bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    small_bags INT NOT NULL DEFAULT 0,
    medium_bags INT NOT NULL DEFAULT 0,
    large_bags INT NOT NULL DEFAULT 0,
    luggage_fee DECIMAL(8,2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 11. PAYMENTS TABLE
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    gateway VARCHAR(20) NOT NULL DEFAULT 'demo',
    gateway_order_id VARCHAR(100),
    gateway_payment_id VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- 12. QR TICKETS TABLE
CREATE TABLE IF NOT EXISTS qr_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID UNIQUE NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    qr_token TEXT UNIQUE NOT NULL,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    verified_by_driver_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 13. GPS LOCATIONS TABLE
CREATE TABLE IF NOT EXISTS gps_locations (
    id BIGSERIAL PRIMARY KEY,
    cart_id UUID NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    driver_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    trip_id UUID REFERENCES trips(id) ON DELETE SET NULL,
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    accuracy_meters DECIMAL(6,2),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 14. NOTIFICATIONS TABLE
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 15. AUDIT LOGS TABLE
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(50),
    details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
