-- ==============================================================================
-- LPU GoCart - Row Level Security (RLS) Migration
-- Enforces least-privilege role-based access for STUDENT, DRIVER, and ADMIN.
-- ==============================================================================

-- Helper function: Check if current authenticated user is an ADMIN
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.profiles 
        WHERE id = auth.uid() AND role = 'ADMIN'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper function: Check current user's role
CREATE OR REPLACE FUNCTION public.get_my_role()
RETURNS TEXT AS $$
DECLARE
    user_role TEXT;
BEGIN
    SELECT role INTO user_role FROM public.profiles WHERE id = auth.uid();
    RETURN user_role;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ==============================================================================
-- ENABLE RLS ON ALL TABLES
-- ==============================================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.students ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.drivers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.carts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.routes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.route_stops ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cart_seats ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trips ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.seat_locks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.gps_locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.qr_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cctv_devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- ==============================================================================
-- 1. PROFILES POLICIES
-- ==============================================================================
-- Users can view their own profile
CREATE POLICY "profiles_select_own" ON public.profiles
    FOR SELECT TO authenticated
    USING (auth.uid() = id OR public.is_admin() OR role = 'DRIVER');

-- Users can update their own profile (cannot change their own role)
CREATE POLICY "profiles_update_own" ON public.profiles
    FOR UPDATE TO authenticated
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id AND role = (SELECT role FROM public.profiles WHERE id = auth.uid()));

-- Admins can update any profile (e.g. assign roles)
CREATE POLICY "profiles_admin_all" ON public.profiles
    FOR ALL TO authenticated
    USING (public.is_admin());

-- ==============================================================================
-- 2. STUDENTS POLICIES
-- ==============================================================================
CREATE POLICY "students_select_own" ON public.students
    FOR SELECT TO authenticated
    USING (auth.uid() = id OR public.is_admin());

CREATE POLICY "students_insert_own" ON public.students
    FOR INSERT TO authenticated
    WITH CHECK (auth.uid() = id);

CREATE POLICY "students_update_own" ON public.students
    FOR UPDATE TO authenticated
    USING (auth.uid() = id OR public.is_admin());

-- ==============================================================================
-- 3. DRIVERS POLICIES
-- ==============================================================================
-- Anyone authenticated can view driver info (e.g., driver name for an approaching cart)
CREATE POLICY "drivers_select_authenticated" ON public.drivers
    FOR SELECT TO authenticated
    USING (true);

-- Drivers can update their own availability
CREATE POLICY "drivers_update_own" ON public.drivers
    FOR UPDATE TO authenticated
    USING (auth.uid() = id OR public.is_admin());

CREATE POLICY "drivers_admin_all" ON public.drivers
    FOR ALL TO authenticated
    USING (public.is_admin());

-- ==============================================================================
-- 4. CARTS POLICIES
-- ==============================================================================
-- Anyone authenticated or anonymous can view active campus carts
CREATE POLICY "carts_read_public" ON public.carts
    FOR SELECT TO anon, authenticated
    USING (true);

-- Only Admins can modify fleet inventory
CREATE POLICY "carts_admin_write" ON public.carts
    FOR ALL TO authenticated
    USING (public.is_admin());

-- ==============================================================================
-- 5. ROUTES & ROUTE_STOPS POLICIES
-- ==============================================================================
CREATE POLICY "routes_read_public" ON public.routes
    FOR SELECT TO anon, authenticated
    USING (true);

CREATE POLICY "routes_admin_write" ON public.routes
    FOR ALL TO authenticated
    USING (public.is_admin());

CREATE POLICY "route_stops_read_public" ON public.route_stops
    FOR SELECT TO anon, authenticated
    USING (true);

CREATE POLICY "route_stops_admin_write" ON public.route_stops
    FOR ALL TO authenticated
    USING (public.is_admin());

-- ==============================================================================
-- 6. CART_SEATS POLICIES
-- ==============================================================================
CREATE POLICY "cart_seats_read_public" ON public.cart_seats
    FOR SELECT TO anon, authenticated
    USING (true);

CREATE POLICY "cart_seats_admin_write" ON public.cart_seats
    FOR ALL TO authenticated
    USING (public.is_admin());

-- ==============================================================================
-- 7. TRIPS POLICIES
-- ==============================================================================
CREATE POLICY "trips_read_public" ON public.trips
    FOR SELECT TO anon, authenticated
    USING (true);

-- Drivers can update trip state (e.g., mark IN_TRANSIT, COMPLETED)
CREATE POLICY "trips_driver_update" ON public.trips
    FOR UPDATE TO authenticated
    USING (driver_id = auth.uid() OR public.is_admin());

CREATE POLICY "trips_admin_all" ON public.trips
    FOR ALL TO authenticated
    USING (public.is_admin());

-- ==============================================================================
-- 8. SEAT_LOCKS POLICIES
-- ==============================================================================
-- Any authenticated user can view active locks for a trip to render occupied seat UI
CREATE POLICY "seat_locks_read" ON public.seat_locks
    FOR SELECT TO authenticated
    USING (true);

-- Students can create a lock for themselves
CREATE POLICY "seat_locks_insert_student" ON public.seat_locks
    FOR INSERT TO authenticated
    WITH CHECK (student_id = auth.uid());

-- Students can release their own lock; Admins have full control
CREATE POLICY "seat_locks_delete_student" ON public.seat_locks
    FOR DELETE TO authenticated
    USING (student_id = auth.uid() OR public.is_admin());

-- ==============================================================================
-- 9. BOOKINGS POLICIES
-- ==============================================================================
-- Students can read their own bookings
CREATE POLICY "bookings_student_select" ON public.bookings
    FOR SELECT TO authenticated
    USING (
        student_id = auth.uid() 
        OR public.is_admin()
        OR EXISTS (
            SELECT 1 FROM public.trips t
            WHERE t.id = trip_id AND t.driver_id = auth.uid()
        )
    );

-- Students can insert bookings for their own student id
CREATE POLICY "bookings_student_insert" ON public.bookings
    FOR INSERT TO authenticated
    WITH CHECK (student_id = auth.uid());

-- Admins have full access
CREATE POLICY "bookings_admin_all" ON public.bookings
    FOR ALL TO authenticated
    USING (public.is_admin());

-- ==============================================================================
-- 10. PAYMENTS POLICIES
-- ==============================================================================
-- Students can only inspect their own payment ledger
CREATE POLICY "payments_student_select" ON public.payments
    FOR SELECT TO authenticated
    USING (student_id = auth.uid() OR public.is_admin());

CREATE POLICY "payments_admin_all" ON public.payments
    FOR ALL TO authenticated
    USING (public.is_admin());

-- ==============================================================================
-- 11. GPS_LOCATIONS POLICIES
-- ==============================================================================
-- Riders and admins can view GPS locations
CREATE POLICY "gps_read_public" ON public.gps_locations
    FOR SELECT TO anon, authenticated
    USING (true);

-- Drivers can log GPS telemetry for their driver ID
CREATE POLICY "gps_driver_insert" ON public.gps_locations
    FOR INSERT TO authenticated
    WITH CHECK (driver_id = auth.uid() OR public.is_admin());

-- ==============================================================================
-- 12. QR_TICKETS POLICIES
-- ==============================================================================
-- Students can view their own QR ticket
CREATE POLICY "qr_tickets_student_select" ON public.qr_tickets
    FOR SELECT TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.bookings b 
            WHERE b.id = booking_id AND b.student_id = auth.uid()
        )
        OR public.is_admin()
        OR public.get_my_role() = 'DRIVER'
    );

-- Drivers can update QR ticket (mark as scanned/used)
CREATE POLICY "qr_tickets_driver_update" ON public.qr_tickets
    FOR UPDATE TO authenticated
    USING (public.get_my_role() = 'DRIVER' OR public.is_admin());

-- ==============================================================================
-- 13. CCTV_DEVICES POLICIES
-- ==============================================================================
-- CCTV feeds are restricted strictly to campus security / ADMINS
CREATE POLICY "cctv_admin_only" ON public.cctv_devices
    FOR ALL TO authenticated
    USING (public.is_admin());

-- ==============================================================================
-- 14. NOTIFICATIONS POLICIES
-- ==============================================================================
CREATE POLICY "notifications_user_own" ON public.notifications
    FOR ALL TO authenticated
    USING (recipient_id = auth.uid());

-- ==============================================================================
-- 15. AUDIT_LOGS POLICIES
-- ==============================================================================
CREATE POLICY "audit_logs_admin_only" ON public.audit_logs
    FOR SELECT TO authenticated
    USING (public.is_admin());
