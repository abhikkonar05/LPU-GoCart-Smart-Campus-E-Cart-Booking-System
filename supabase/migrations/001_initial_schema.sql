-- ==============================================================================
-- LPU GoCart - Initial Database Schema Migration
-- Lovely Professional University (LPU) Smart Campus E-Cart System
-- Creates all 16 core relational tables, constraints, indexes, and triggers.
-- ==============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Function to automatically update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- 1. PROFILES (Base User Table linked to Supabase Auth)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    phone_number VARCHAR(15),
    role VARCHAR(20) NOT NULL DEFAULT 'STUDENT' CHECK (role IN ('STUDENT', 'DRIVER', 'ADMIN')),
    avatar_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==============================================================================
-- 2. STUDENTS (Student Specific Data)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.students (
    id UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
    registration_number VARCHAR(20) UNIQUE NOT NULL,
    department VARCHAR(100),
    hostel_block VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==============================================================================
-- 3. DRIVERS (Driver Specific Data & Availability)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.drivers (
    id UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    assigned_cart_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==============================================================================
-- 4. ROUTES (Campus Shuttle Lines)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    fare_amount DECIMAL(6,2) NOT NULL DEFAULT 10.00 CHECK (fare_amount >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==============================================================================
-- 5. ROUTE_STOPS (Waypoints and Stops for Each Route)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.route_stops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_id UUID NOT NULL REFERENCES public.routes(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    sequence_order INTEGER NOT NULL,
    estimated_minutes INTEGER NOT NULL DEFAULT 2,
    CONSTRAINT unique_route_stop_order UNIQUE (route_id, sequence_order)
);

CREATE INDEX IF NOT EXISTS idx_route_stops_route_id ON public.route_stops(route_id);

-- ==============================================================================
-- 6. CARTS (Electric Vehicles Fleet)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.carts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_number VARCHAR(20) UNIQUE NOT NULL,
    model VARCHAR(50) NOT NULL DEFAULT 'Club Car Transporter 8',
    total_seats INTEGER NOT NULL DEFAULT 8 CHECK (total_seats > 0 AND total_seats <= 14),
    battery_percentage INTEGER NOT NULL DEFAULT 100 CHECK (battery_percentage BETWEEN 0 AND 100),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'MAINTENANCE', 'OFFLINE', 'CHARGING')),
    current_route_id UUID REFERENCES public.routes(id) ON DELETE SET NULL,
    has_cctv BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_carts_status ON public.carts(status);
CREATE INDEX IF NOT EXISTS idx_carts_current_route ON public.carts(current_route_id);

-- Add foreign key reference from drivers to carts
ALTER TABLE public.drivers
    DROP CONSTRAINT IF EXISTS fk_driver_cart,
    ADD CONSTRAINT fk_driver_cart FOREIGN KEY (assigned_cart_id) REFERENCES public.carts(id) ON DELETE SET NULL;

-- ==============================================================================
-- 7. CART_SEATS (Bookable Seats inside each Cart)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.cart_seats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id UUID NOT NULL REFERENCES public.carts(id) ON DELETE CASCADE,
    seat_number INTEGER NOT NULL CHECK (seat_number > 0),
    seat_label VARCHAR(10) NOT NULL,
    is_accessible BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT unique_cart_seat UNIQUE (cart_id, seat_number)
);

CREATE INDEX IF NOT EXISTS idx_cart_seats_cart_id ON public.cart_seats(cart_id);

-- ==============================================================================
-- 8. TRIPS (Journeys in Progress or Completed)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id UUID NOT NULL REFERENCES public.carts(id) ON DELETE CASCADE,
    driver_id UUID NOT NULL REFERENCES public.drivers(id) ON DELETE CASCADE,
    route_id UUID NOT NULL REFERENCES public.routes(id) ON DELETE RESTRICT,
    status VARCHAR(20) NOT NULL DEFAULT 'SCHEDULED' CHECK (status IN ('SCHEDULED', 'IN_TRANSIT', 'COMPLETED', 'CANCELLED')),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trips_cart_id ON public.trips(cart_id);
CREATE INDEX IF NOT EXISTS idx_trips_status ON public.trips(status);

-- ==============================================================================
-- 9. SEAT_LOCKS (Temporary 5-Minute Atomic Holds)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.seat_locks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES public.trips(id) ON DELETE CASCADE,
    seat_id UUID NOT NULL REFERENCES public.cart_seats(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES public.students(id) ON DELETE CASCADE,
    locked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    is_released BOOLEAN NOT NULL DEFAULT FALSE
);

-- Crucial: Prevents locking an already active locked seat
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_seat_lock 
    ON public.seat_locks (trip_id, seat_id) 
    WHERE is_released = FALSE;

CREATE INDEX IF NOT EXISTS idx_seat_locks_expires_at ON public.seat_locks(expires_at);

-- ==============================================================================
-- 10. BOOKINGS (Confirmed or Pending Student Reservations)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_code VARCHAR(20) UNIQUE NOT NULL,
    student_id UUID NOT NULL REFERENCES public.students(id) ON DELETE RESTRICT,
    trip_id UUID NOT NULL REFERENCES public.trips(id) ON DELETE RESTRICT,
    seat_id UUID NOT NULL REFERENCES public.cart_seats(id) ON DELETE RESTRICT,
    pickup_stop_id UUID NOT NULL REFERENCES public.route_stops(id) ON DELETE RESTRICT,
    drop_stop_id UUID NOT NULL REFERENCES public.route_stops(id) ON DELETE RESTRICT,
    fare_amount DECIMAL(6,2) NOT NULL CHECK (fare_amount >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'CONFIRMED', 'BOARDED', 'CANCELLED', 'EXPIRED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER update_bookings_updated_at
    BEFORE UPDATE ON public.bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Crucial: Database-level guarantee that two students can NEVER confirm the same seat on the same trip
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_confirmed_trip_seat 
    ON public.bookings (trip_id, seat_id) 
    WHERE status IN ('CONFIRMED', 'BOARDED');

CREATE INDEX IF NOT EXISTS idx_bookings_student_id ON public.bookings(student_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON public.bookings(status);

-- ==============================================================================
-- 11. PAYMENTS (Financial Ledger: Demo & Razorpay)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES public.bookings(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES public.students(id) ON DELETE RESTRICT,
    amount DECIMAL(8,2) NOT NULL CHECK (amount >= 0),
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    gateway VARCHAR(20) NOT NULL CHECK (gateway IN ('demo', 'razorpay')),
    gateway_order_id VARCHAR(100),
    gateway_payment_id VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_payments_booking_id ON public.payments(booking_id);
CREATE INDEX IF NOT EXISTS idx_payments_student_id ON public.payments(student_id);

-- ==============================================================================
-- 12. GPS_LOCATIONS (Live Real-Time Telemetry Stream)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.gps_locations (
    id BIGSERIAL PRIMARY KEY,
    cart_id UUID NOT NULL REFERENCES public.carts(id) ON DELETE CASCADE,
    driver_id UUID NOT NULL REFERENCES public.drivers(id) ON DELETE CASCADE,
    trip_id UUID REFERENCES public.trips(id) ON DELETE SET NULL,
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    speed_kph DECIMAL(5,2) DEFAULT 0.0,
    heading DECIMAL(5,2),
    accuracy_meters DECIMAL(6,2),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gps_cart_recorded ON public.gps_locations(cart_id, recorded_at DESC);

-- ==============================================================================
-- 13. QR_TICKETS (Cryptographically Validated Boarding Passes)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.qr_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID UNIQUE NOT NULL REFERENCES public.bookings(id) ON DELETE CASCADE,
    qr_token TEXT UNIQUE NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    scanned_at TIMESTAMPTZ,
    scanned_by_driver_id UUID REFERENCES public.drivers(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_qr_tickets_qr_token ON public.qr_tickets(qr_token);

-- ==============================================================================
-- 14. CCTV_DEVICES (Cart Surveillance Hardware Metadata)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.cctv_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id UUID UNIQUE NOT NULL REFERENCES public.carts(id) ON DELETE CASCADE,
    device_serial VARCHAR(100) UNIQUE NOT NULL,
    stream_url TEXT,
    stream_protocol VARCHAR(20) DEFAULT 'RTSP' CHECK (stream_protocol IN ('RTSP', 'HLS', 'WEBRTC')),
    is_online BOOLEAN NOT NULL DEFAULT FALSE,
    last_heartbeat TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==============================================================================
-- 15. NOTIFICATIONS (User Alert & Audit Inbox)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifications_recipient ON public.notifications(recipient_id, is_read);

-- ==============================================================================
-- 16. AUDIT_LOGS (Administrative and Security Ledger)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id BIGSERIAL PRIMARY KEY,
    actor_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(50),
    metadata JSONB DEFAULT '{}'::jsonb,
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at DESC);

-- ==============================================================================
-- AUTOMATIC PROFILE CREATION TRIGGER FOR SUPABASE AUTH
-- When a user signs up via Supabase Auth, automatically insert a row in profiles
-- ==============================================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    user_role VARCHAR(20);
BEGIN
    user_role := COALESCE(NEW.raw_user_meta_data->>'role', 'STUDENT');
    IF user_role NOT IN ('STUDENT', 'DRIVER', 'ADMIN') THEN
        user_role := 'STUDENT';
    END IF;

    INSERT INTO public.profiles (id, email, full_name, phone_number, role)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1)),
        NEW.raw_user_meta_data->>'phone_number',
        user_role
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
