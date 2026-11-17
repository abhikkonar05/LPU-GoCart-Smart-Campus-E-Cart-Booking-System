# LPU GoCart – Zero-Cost Render Deployment Guide

---

## 1. Overview
The platform deploys onto Render using free-tier services defined in `render.yaml`:
- **Frontend**: Render Static Site (dist directory, SPA rewrite)
- **Backend**: Render Python Web Service (FastAPI + Uvicorn)
- **Database**: Render Free PostgreSQL Database

---

## 2. Step-by-Step Render Deployment
1. Push this repository to your GitHub account.
2. Sign in to [render.com](https://render.com).
3. Click **Blueprints** -> **New Blueprint Instance**.
4. Connect your GitHub repository.
5. Render reads `render.yaml` and provisions:
   - `lpu-gocart-db` (PostgreSQL)
   - `lpu-gocart-api` (FastAPI)
   - `lpu-gocart-web` (React Static Site)
6. Click **Apply**.
7. In the Render PostgreSQL dashboard, run `database/schema.sql` and `database/seed.sql` via the built-in web shell or external psql connection.

---

## 3. Render Free Plan Limitations & Backup Strategy
- **Service Sleep**: Free web services sleep after 15 minutes of inactivity; initial wakeup takes ~30-50 seconds.
- **30-Day PostgreSQL Expiration**: Free Render databases expire after 30 days.
  - Run `.\scripts\backup.ps1` before the 30-day window to export your data.
  - When recreating a new database, run `.\scripts\restore.ps1 -BackupFile <file>` to restore all tables and bookings instantly!
