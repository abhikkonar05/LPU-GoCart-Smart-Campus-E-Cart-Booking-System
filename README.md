# LPU GoCart – Smart Campus E-Cart Booking & Live Tracking Website
> **Lovely Professional University (LPU), Phagwara, Punjab**  
> *Production-Ready, Streamlined Full-Stack Web Platform*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9-199900.svg)](https://leafletjs.com/)
[![Render](https://img.shields.io/badge/Deploy-Render_Blueprint-46E3B7.svg)](https://render.com/)

---

## 1. Project Overview
LPU GoCart is a responsive campus transportation website designed for Lovely Professional University.
- **Customers**: Browse campus routes, check cart battery and seat availability, lock individual seats (5-min atomic holds), book luggage capacity, reserve entire carts, complete demo payments, and view digital QR boarding tickets.
- **Drivers**: View assigned cart (`LPU-GC-001`), share live mobile browser GPS coordinates using the HTML5 Geolocation API, inspect passenger manifests, and scan passenger QR passes.
- **Admins**: Fleet monitoring, cart management, driver assignment, route configuration, and payment auditing.

---

## 2. Clean Monorepo Structure

```
LPU-GoCart/
├── frontend/        # React + Vite + Tailwind + Leaflet Web Application
├── backend/         # FastAPI + SQLAlchemy + WebSockets Backend Engine
├── database/        # schema.sql and seed.sql for Render PostgreSQL
├── scripts/         # Windows 11 PowerShell automation scripts
├── docs/            # Guides for setup, database, API, and Render deployment
├── render.yaml      # Render blueprint for zero-cost deployment
└── README.md
```

---

## 3. Quickstart (Windows 11)

### Step 1: Install Dependencies
Run the automated Windows setup script:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

### Step 2: Start Both Applications
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start.ps1
```
- **Frontend**: `http://localhost:5173`
- **Backend API**: `http://localhost:8000` (Docs at `/docs`)

---

## 4. Development Workflow

- **[x] PHASE 1: Project Foundation & Clean Monorepo Setup**
- **[ ] PHASE 2: PostgreSQL Database & Models**
- **[ ] PHASE 3: Authentication & Role Permissions (Admin, Driver, Customer)**
- **[ ] PHASE 4: Admin & Cart Management (LPU-GC-001 numbers, routes)**
- **[ ] PHASE 5: Customer Website (Search, seat layout, map)**
- **[ ] PHASE 6: Driver Website (Mobile browser GPS sharing, QR scanner)**
- **[ ] PHASE 7: Booking System (Seat locking, luggage, full cart)**
- **[ ] PHASE 8: Payment & Tickets (Demo gateway, QR verification)**
- **[ ] PHASE 9: Real-Time Tracking (HTML5 Geolocation + WebSockets)**
- **[ ] PHASE 10: Admin Dashboard (Metrics & fleet control)**
- **[ ] PHASE 11: Testing & Concurrency Verification**
- **[ ] PHASE 12: Zero-Cost Render Deployment**
