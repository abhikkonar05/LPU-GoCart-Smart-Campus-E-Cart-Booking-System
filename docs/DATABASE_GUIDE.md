# LPU GoCart – Database Guide

---

## 1. Relational Model & Tables
1. `users`: Customer, Driver, and Admin authentication records with hashed passwords and roles.
2. `routes`: Defined shuttle paths with start/end points and base fares.
3. `route_stops`: Ordered stops (Gate 1, Block 32, UniMall, Library, Girls Hostels, Boys Hostels).
4. `carts`: Fleet records with unique `cart_number` (e.g., `LPU-GC-001`), seats, and luggage capacity.
5. `cart_seats`: 6 seats per cart (`S1` to `S6`).
6. `trips`: Active and scheduled journey runs.
7. `seat_locks`: 5-minute atomic holds on individual seats during checkout.
8. `cart_locks`: 5-minute atomic holds on an entire cart for full-cart bookings.
9. `bookings`: Confirmed and pending bookings with unique booking codes (`LPU-BK-XXXXXX`).
10. `luggage_bookings`: Small, medium, and large bag allowances per booking.
11. `payments`: Transactions recorded under Demo or Razorpay gateways.
12. `qr_tickets`: Tamper-proof digital boarding passes with cryptographic signatures.
13. `gps_locations`: Live coordinates emitted by driver smartphone browsers.
14. `notifications`: Rider and driver alert records.
15. `audit_logs`: Security and admin change ledger.

---

## 2. Concurrency Safety & Double-Booking Prevention
- **Atomic Locks**: Before confirming payment, a 5-minute lock is acquired on the seat or cart in a database transaction.
- **Unique Constraint**: `idx_uq_confirmed_seat` guarantees that the database will reject any second booking for the same seat on the same trip.
- **Full-Cart Conflict Rules**: If an active cart lock or full-cart booking exists, individual seat bookings are blocked; vice versa, if any seat is booked, full-cart booking is rejected.
