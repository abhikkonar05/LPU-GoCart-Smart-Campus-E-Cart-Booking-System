# LPU GoCart – Master Project Guide
> **Smart Campus E-Cart Transit & Booking Website**  
> **Lovely Professional University (LPU), Phagwara, Punjab**

---

## 1. Project Mission
LPU GoCart is a unified web-based campus transit management platform tailored specifically for Lovely Professional University.
It delivers:
1. **Customer Web Portal**: Seat booking, luggage reservations, whole-cart reservations, digital QR tickets, demo payments, and live map tracking.
2. **Driver Web Portal**: Mobile browser GPS location sharing via the HTML5 Geolocation API, passenger manifest, and QR ticket boarding scanner.
3. **Admin Web Portal**: Fleet inventory (unique cart numbers like `LPU-GC-001`), route configuration, fare management, booking logs, payment audit, and reports.

---

## 2. Monorepo Architecture
```
LPU-GoCart/
├── frontend/    # React.js + Vite + Tailwind CSS + Leaflet (Customer, Driver & Admin)
├── backend/     # Python FastAPI + SQLAlchemy + WebSockets + Pydantic
├── database/    # schema.sql and seed.sql for Render PostgreSQL
├── scripts/     # setup.ps1, start.ps1, backup.ps1, restore.ps1
├── docs/        # Complete guides
└── render.yaml  # Infrastructure-as-code blueprint for Render
```

---

## 3. Core Roles
- **CUSTOMER**: Can register publicly, book seats/luggage/full-carts, view tickets, and track active carts.
- **DRIVER**: Created and managed by Admin; logs in to start trips, broadcast GPS telemetry, and scan passenger boarding QR codes.
- **ADMIN**: Manages drivers, carts, routes, luggage policies, cancellations, and financial records.
