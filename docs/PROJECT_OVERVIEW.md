# LPU GoCart – Smart Campus E-Cart Booking & Tracking System
## Project Overview & Mission

### 1. Executive Summary
**LPU GoCart** is a modern, real-time campus mobility and fleet management platform custom-engineered for **Lovely Professional University (LPU)**, Phagwara, Punjab. Spanning over 600 acres with tens of thousands of active students, faculty, and visitors daily, campus transit via electric carts (e-carts) is essential. However, riders struggle with:
1. Long waits without visibility into cart availability.
2. Unpredictable arrival times and packed carts.
3. Inability to reserve seats in advance.
4. Lack of transparent digital ticketing.
5. Inefficient fleet management and oversight for campus security and transit administrators.

LPU GoCart resolves these challenges by coupling a cloud-native **FastAPI** backend, **Supabase PostgreSQL** real-time database, an interactive **React Admin Web Dashboard**, and dedicated **React Native (Expo)** apps for Students and Drivers.

---

### 2. Core Pillars of the Platform
- **Real-Time GPS Tracking**: Leveraging the driver's smartphone GPS without expensive third-party hardware modules. Location telemetry streams via WebSockets and Supabase Realtime to riders and dispatchers every 3 seconds.
- **Atomic Concurrency-Safe Seat Reservation**: Strict PostgreSQL-level atomic locking (`SELECT FOR UPDATE`) prevents double bookings. Selected seats are locked for 5 minutes, allowing students to complete payment seamlessly.
- **Flexible Modular Payment Architecture**: Pluggable payment gateway abstraction supporting instant zero-cost **Demo Mode** for local development and testing, with clean configuration-driven transition to **Razorpay** for production collections.
- **Paperless Boarding with QR Validation**: Confirmed bookings generate tamper-proof QR tickets that drivers scan using their smartphone camera, instantly verifying passenger manifest records.
- **Fleet & CCTV Monitoring**: Central dashboard for university administration to monitor fleet health, route bottlenecks, driver shifts, and authorized onboard CCTV camera connectivity status.

---

### 3. User Personas & Roles
| Role | App / Interface | Key Capabilities |
| :--- | :--- | :--- |
| **Student** | Android App (Expo / React Native) | Discover nearby carts on campus map, view seat layouts, hold seats, complete demo/online payments, view live cart ETA, generate boarding QR tickets. |
| **Driver** | Android App (Expo / React Native) | Authenticate, inspect assigned cart & route, broadcast high-precision GPS telemetry in real-time, view passenger manifests, scan QR boarding codes. |
| **Admin** | Web Dashboard (Vite / React / Tailwind) | Comprehensive live fleet telemetry map, cart/driver assignment, route optimization, financial audit logs, CCTV camera management, user governance. |

---

### 4. Technical Constraints & Design Principles
- **Cost**: Built entirely on free-tier, modern open-source stacks (Supabase Free Tier, Render Free Tier, Vercel Free Tier, Expo Free EAS/Local Build).
- **Security**: Supabase Row Level Security (RLS) policies enforce least privilege at the database layer. Backend services communicate via privileged service roles while mobile clients use restricted anonymous keys.
- **Platform**: Fully configured for native Windows 11 development with PowerShell automation.

