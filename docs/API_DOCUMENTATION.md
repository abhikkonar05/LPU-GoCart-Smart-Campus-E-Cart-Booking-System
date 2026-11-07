# LPU GoCart – REST API & WebSocket Documentation

Base URL: `http://localhost:8000/api/v1` (Development)  
Interactive OpenAPI Swagger Docs: `http://localhost:8000/docs`  
Interactive ReDoc: `http://localhost:8000/redoc`

---

## 1. Authentication & Security
All authenticated endpoints require an `Authorization` header containing a valid Supabase JWT Bearer token:
```http
Authorization: Bearer <supabase_jwt_access_token>
```

---

## 2. API Endpoints Overview

### Auth & User (`/auth`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Public | Register new student or driver profile |
| `GET` | `/auth/me` | Authenticated | Retrieve current user profile and role |
| `PATCH` | `/auth/me` | Authenticated | Update user profile phone, hostel, etc. |

### Carts & Routes (`/carts`, `/routes`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/routes` | Public | List all active campus routes and stops |
| `GET` | `/routes/{id}` | Public | Detailed stop sequence and fare for a route |
| `GET` | `/carts` | Public | List available carts, statuses & battery levels |
| `GET` | `/carts/{id}` | Public | Specific cart details with seat layout |
| `GET` | `/carts/{id}/seats` | Public | Current seat layout and real-time availability |

### Trips & Booking Lifecycle (`/trips`, `/bookings`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/trips/active` | Public | List ongoing trips with current positions |
| `POST` | `/bookings/lock-seat` | Student | **Atomic Operation**: Locks a seat for 5 mins |
| `POST` | `/bookings/confirm` | Student | Finalize booking following successful payment |
| `GET` | `/bookings/my` | Student | Fetch active and historical passenger bookings |
| `GET` | `/bookings/{id}/ticket`| Student | Generate signed QR boarding ticket |

### Payments (`/payments`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/payments/create-intent` | Student | Initialize demo or Razorpay order |
| `POST` | `/payments/demo-confirm` | Student | Process simulated test payment |
| `POST` | `/payments/razorpay/webhook` | Public | Webhook listener for Razorpay signature |

### Driver Operations (`/drivers`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/drivers/assigned-cart` | Driver | Fetch cart and route assigned to driver |
| `POST` | `/drivers/trips/start` | Driver | Initiate a new trip run |
| `POST` | `/drivers/trips/end` | Driver | Complete active trip |
| `POST` | `/drivers/verify-qr` | Driver | Scan and validate student QR ticket |

### Administration (`/admin`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/admin/metrics` | Admin | Real-time overview counts (carts, revenue, active trips) |
| `POST` | `/admin/carts` | Admin | Register new e-cart in fleet |
| `PUT` | `/admin/carts/{id}` | Admin | Update cart status or route |
| `GET` | `/admin/cctv` | Admin | List all registered cart CCTV devices |

---

## 3. Real-Time WebSocket Telemetry
**Endpoint:** `ws://localhost:8000/ws/tracking`

### Client Message (Driver emitting location):
```json
{
  "type": "DRIVER_LOCATION",
  "cart_id": "8e3bfa99-231a-4d45-9850-8b17b6dc1a3f",
  "trip_id": "19b5b22b-5f04-4c28-98e1-5e8a0fa6163b",
  "latitude": 31.25365,
  "longitude": 75.70372,
  "speed_kph": 18.5,
  "heading": 142.0,
  "timestamp": "2026-11-08T01:30:00Z"
}
```

### Server Broadcast (Received by Students and Admin Dashboard):
```json
{
  "event": "CART_UPDATE",
  "cart_id": "8e3bfa99-231a-4d45-9850-8b17b6dc1a3f",
  "route_id": "route-a-guid",
  "latitude": 31.25365,
  "longitude": 75.70372,
  "speed_kph": 18.5,
  "heading": 142.0,
  "available_seats": 5,
  "next_stop": "UniMall & Food Court",
  "updated_at": "2026-11-08T01:30:00Z"
}
```
