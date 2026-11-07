# LPU GoCart – Operational & End-User Manual

---

## 1. Student User Journey

### A. Discovering Carts & Routes
1. Launch the **LPU GoCart** app on your Android smartphone.
2. Sign in using your university credentials (`registration_number@lpu.in`).
3. The **Home Map** instantly reveals:
   - Your current GPS location inside LPU campus.
   - Moving cart markers with real-time ETA countdowns.
   - Nearest pickup stops (e.g. Block 32, UniMall, Central Library).
   - Remaining free seats on approaching carts.

### B. Reserving a Seat
1. Tap an approaching or scheduled cart on the map or list.
2. Inspect the **Seat Layout Grid** (Seats 1 through 8). Green seats are available; red seats are occupied.
3. Tap an available seat to lock it. An atomic 5-minute timer begins.
4. Review your trip summary and select **Pay via Demo Gateway** (or Razorpay when configured).
5. Upon confirmation, your booking changes to `CONFIRMED` and a **Digital QR Boarding Ticket** is issued.

### C. Boarding the Cart
1. Arrive at the designated pickup point.
2. Present the digital QR code on your screen to the driver.
3. The driver scans your screen; the app marks your ticket `BOARDED`. Enjoy your emission-free ride!

---

## 2. Driver Operational Journey

### A. Shift Initiation
1. Launch the **LPU GoCart Driver** app.
2. Sign in with your registered driver license ID and PIN.
3. Tap **Start Shift** to link with your assigned cart (e.g. `LPU-CART-02`).

### B. Real-Time Telemetry Broadcasting
1. When departing on a route, toggle **Share Live Location**.
2. Grant "Allow background location" permission.
3. The app periodically transmits your coordinate telemetry every 3 seconds to student maps and the university dispatch desk.

### C. Passenger Manifest & Boarding Validation
1. Open the built-in **Passenger Manifest** to view registered bookings at each stop.
2. Tap **Scan Passenger QR** to launch the camera scanner.
3. Align the student's boarding ticket. The app immediately verifies the cryptographic token, displays a green success confirmation, and updates trip occupancy.

---

## 3. Administrative Dispatch & Fleet Monitoring

### A. Live Map & Fleet Control
1. Open the Admin Dashboard in your browser (`http://localhost:5173`).
2. Monitor real-time cart positions across campus with color-coded battery health and trip statuses.
3. In case of route congestion, dynamically re-route carts or adjust dispatch frequency.

### B. CCTV Surveillance Integration
1. Click the **CCTV Monitoring** tab.
2. Inspect operational status across all registered cart camera units.
3. View authorized streaming feeds when connected to campus camera infrastructure.
