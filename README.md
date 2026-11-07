# LPU GoCart – Smart Campus E-Cart Booking & Tracking System
> **Lovely Professional University (LPU), Phagwara, Punjab**  
> *Production-Grade, Scalable, Full-Stack Real-Time Campus Transit Solution*

[![Node.js](https://img.shields.io/badge/Node.js-v24+-green.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React Native](https://img.shields.io/badge/React_Native-Expo_SDK_51-61DAFB.svg)](https://expo.dev/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL_%2B_Auth-3ECF8E.svg)](https://supabase.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 1. Project Overview

At **Lovely Professional University**, thousands of students, faculty, and campus staff commute daily across an expansive 600+ acre campus. University electric carts (e-carts) provide an eco-friendly mode of transport. However, riders encounter critical hurdles:
- **Zero Real-Time Visibility:** Waiting at stops with no information on cart whereabouts or estimated arrival times.
- **Seat Uncertainty:** Arriving at a cart only to find every seat already occupied.
- **No Pre-Booking Mechanism:** Inability to reserve a seat ahead of time during peak lecture hours.
- **Manual Fare & Cash Hassles:** Lack of automated student fare deductions and digital tickets.
- **Driver & Dispatch Blind Spots:** Fleet managers lack centralized oversight over active carts, route congestion, and battery levels.

**LPU GoCart** delivers a complete digital transportation platform:
- **Student Android App**: Live OpenStreetMap tracking, interactive 8-seat reservation grid, atomic seat locking, demo/Razorpay checkout, and digital QR boarding passes.
- **Driver Android App**: Turn-by-turn route overview, automatic background GPS telemetry broadcast (every 3 seconds), and instant camera-based QR ticket boarding scanner.
- **Admin Fleet Web Dashboard**: Real-time campus-wide telemetry, cart and driver allocation, route optimization, CCTV camera connectivity monitoring, and revenue analytics.
- **Cloud-Native Backend**: High-performance FastAPI engine with PostgreSQL row-level locks (`SELECT FOR UPDATE`) guaranteeing that **no two students can ever book the same seat simultaneously**.

---

## 2. Monorepo Structure

```
LPU-GoCart/
│
├── apps/
│   ├── student-app/         # Expo / React Native Android app for students
│   ├── driver-app/          # Expo / React Native Android app with GPS broadcast & QR scanner
│   └── admin-dashboard/     # React + Vite + Tailwind + Leaflet fleet dashboard
│
├── backend/                 # FastAPI REST API, WebSockets, Payment Gateways & Supabase ORM
│   ├── app/
│   │   ├── core/            # Configuration, JWT security & dependencies
│   │   ├── database/        # Connection pool & SQLAlchemy models
│   │   ├── schemas/         # Pydantic input/output validation models
│   │   ├── api/v1/          # Modular API routes (auth, carts, routes, bookings, etc.)
│   │   ├── services/        # Atomic seat locking, booking & QR code generation
│   │   ├── gateways/        # Pluggable payment abstraction (Demo & Razorpay)
│   │   └── websockets/      # Real-time GPS coordinate streaming
│   ├── render.yaml          # Zero-cost Render deployment blueprint
│   ├── Dockerfile           # Multi-stage production container
│   └── requirements.txt     # Python dependencies
│
├── supabase/                # Cloud PostgreSQL migrations, RLS policies & seed data
│   ├── migrations/          # 16 transactional relational tables with RLS
│   ├── seed.sql             # LPU campus landmarks, routes, and sample carts
│   └── config.toml          # Supabase configuration
│
├── shared/                  # Common TypeScript interfaces & LPU campus constants
│   ├── types/               # Data contracts for User, Cart, Booking, Trip, GPS
│   └── constants/           # LPU coordinates, campus stops, brand colors & fare rules
│
├── docs/                    # Exhaustive engineering documentation
│   ├── PROJECT_OVERVIEW.md  # Detailed requirements & domain model
│   ├── ARCHITECTURE.md      # Data flow & service interaction diagrams
│   ├── DATABASE_SCHEMA.md   # Complete 16-table ER diagram and schema spec
│   ├── API_DOCUMENTATION.md # REST and WebSocket contracts
│   ├── DEPLOYMENT.md        # Step-by-step Render, Vercel & Supabase guide
│   └── USER_GUIDE.md        # Operations handbook for Students, Drivers & Admins
│
├── scripts/                 # Windows 11 PowerShell automation tools
│   ├── check_environment.ps1# Diagnoses Node, Python, Git & local port availability
│   └── setup.ps1            # Automates venv creation and config bootstrapping
│
├── .gitignore               # Clean git exclusions (node_modules, venvs, secrets)
├── .env.example             # Central environment variables template
└── package.json             # Root monorepo configuration with npm workspaces
```

---

## 3. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Student Mobile App** | React Native, Expo SDK 51, TypeScript, Expo Router, React Native Paper, React Native Maps, TanStack Query, Axios |
| **Driver Mobile App** | React Native, Expo SDK 51, TypeScript, Expo Location (Background GPS), Expo Camera (QR Scanner), WebSockets |
| **Admin Web Dashboard** | React 18, Vite, TypeScript, Tailwind CSS, Lucide Icons, Leaflet / React-Leaflet, Recharts |
| **Backend API** | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Uvicorn, WebSockets |
| **Database & Auth** | Supabase PostgreSQL, Supabase Auth, Row Level Security (RLS), Supabase Realtime |
| **Payments** | Pluggable Gateway Pattern: `DemoPaymentGateway` (Zero-cost local testing) & `RazorpayPaymentGateway` |
| **Deployment** | Render (FastAPI Web Service), Vercel (Admin Web Dashboard), Supabase (Database), Expo EAS (Android APK) |

---

## 4. Quickstart Guide (Windows 11)

### Step 1: Diagnose Prerequisites
Run the automated diagnostic tool in PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_environment.ps1
```
Expected output:
- `Node.js`: v20+ LTS
- `NPM`: 10+
- `Python`: 3.11+
- `Git`: Installed and detected
- Ports `8000`, `5173`, and `8081` available.

### Step 2: Automated Workspace Setup
Run the setup script:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```
This automatically configures the Python virtual environment (`backend/.venv`) and creates local `.env` templates.

### Step 3: Install Backend Dependencies
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
```

### Step 4: Install Dashboard Dependencies
```powershell
cd apps/admin-dashboard
npm install
cd ..\..
```

---

## 5. Development Phases

- **[x] PHASE 1: Monorepo Foundation & Environment Verification**
- **[ ] PHASE 2: Supabase Relational Database & Row Level Security Setup**
- **[ ] PHASE 3: FastAPI Backend & Authentication Engine**
- **[ ] PHASE 4: Student Android Mobile Application**
- **[ ] PHASE 5: Driver Android Mobile Application & GPS Broadcast**
- **[ ] PHASE 6: Atomic Seat Locking, Demo Payment & QR Ticket Engine**
- **[ ] PHASE 7: Admin Fleet Web Dashboard & CCTV Health Monitor**
- **[ ] PHASE 8: End-to-End Integration & Concurrency Stress Testing**
- **[ ] PHASE 9: Zero-Cost Cloud Deployment (Render + Vercel + Supabase)**

---

## 6. License
Licensed under the [MIT License](LICENSE). Developed with pride for the **Lovely Professional University (LPU)** community.

