# LPU GoCart – API Documentation

Interactive API Swagger UI: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

---

## 1. Authentication
All protected routes require an HTTP Bearer header:
```http
Authorization: Bearer <jwt_token>
```

---

## 2. Key Endpoint Groups
- `POST /api/v1/auth/register`: Public customer registration.
- `POST /api/v1/auth/login`: Authentication returning JWT access token.
- `GET /api/v1/auth/me`: Current user profile.
- `GET /api/v1/routes`: List active campus routes and ordered stops.
- `GET /api/v1/carts`: List carts with available seats and live telemetry.
- `POST /api/v1/bookings/lock-seat`: Atomic 5-minute seat hold.
- `POST /api/v1/bookings/create-pending`: Create pending reservation.
- `POST /api/v1/payments/demo-confirm`: Verify and confirm demo payment.
- `POST /api/v1/drivers/verify-qr`: Driver scans student QR ticket.
- `POST /api/v1/tracking/update`: Ingests driver browser GPS coordinate.
- `WS /ws/tracking`: Live WebSocket stream of campus fleet coordinates.
