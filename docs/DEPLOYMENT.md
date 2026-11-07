# LPU GoCart – Zero-Cost Deployment Guide

This guide outlines step-by-step production deployment using free-tier services.

---

## 1. Architecture Overview
- **Database & Auth**: Supabase PostgreSQL (Free Tier: 500MB DB, 50,000 MAU).
- **Backend API**: Render Web Service (Free Tier: Python 3.11+, automatic SSL, 512MB RAM).
  *Note on Free Tier*: Render spins down inactive services after 15 minutes. The first request takes 30-50 seconds to warm up.
- **Admin Dashboard**: Vercel (Free Tier: Global CDN, automatic previews, zero-config Vite deployments).
- **Mobile Applications**: Expo Application Services (EAS Build - Free Tier: 30 Android builds/month) or Local APK builds via Android SDK.

---

## 2. Supabase Cloud Setup
1. Create a free account at [supabase.com](https://supabase.com).
2. Click **New Project**, Name: `lpu-gocart`, Region: `South Asia (Mumbai) / ap-south-1`.
3. Save your generated Database Password securely.
4. Navigate to **SQL Editor** -> Click **New Query** -> Paste contents of `supabase/migrations/001_initial_schema.sql` -> Click **Run**.
5. Paste contents of `supabase/seed.sql` -> Click **Run**.
6. Navigate to **Project Settings -> API**:
   - Copy `Project URL`
   - Copy `anon public` key
   - Copy `service_role` secret key

---

## 3. Backend Deployment (Render)
1. Fork or push this repository to your GitHub account.
2. Sign in to [render.com](https://render.com).
3. Click **New +** -> **Web Service** -> Connect your GitHub repo.
4. Settings:
   - **Root Directory**: `backend`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, add:
   - `SUPABASE_URL`: `<your-supabase-url>`
   - `SUPABASE_ANON_KEY`: `<your-anon-key>`
   - `SUPABASE_SERVICE_ROLE_KEY`: `<your-service-role-key>`
   - `SUPABASE_DB_URL`: `<your-supabase-db-url>`
   - `PAYMENT_MODE`: `demo`
   - `ENVIRONMENT`: `production`
6. Click **Create Web Service**. Your service URL will be `https://lpu-gocart-api.onrender.com`.

---

## 4. Admin Dashboard Deployment (Vercel)
1. Sign in to [vercel.com](https://vercel.com) using GitHub.
2. Click **Add New** -> **Project** -> Select your repository.
3. Configure Project:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click edit -> Select `apps/admin-dashboard`.
4. Under **Environment Variables**, add:
   - `VITE_API_BASE_URL`: `https://lpu-gocart-api.onrender.com/api/v1`
   - `VITE_WS_TRACKING_URL`: `wss://lpu-gocart-api.onrender.com/ws/tracking`
   - `VITE_SUPABASE_URL`: `<your-supabase-url>`
   - `VITE_SUPABASE_ANON_KEY`: `<your-anon-key>`
5. Click **Deploy**. Vercel will output a live URL (e.g., `https://lpu-gocart-admin.vercel.app`).

---

## 5. Mobile APK Generation (Expo EAS)
1. Install EAS CLI globally:
   ```powershell
   npm install -g eas-cli
   ```
2. Log in with your Expo account:
   ```powershell
   eas login
   ```
3. Navigate to either app directory:
   ```powershell
   cd apps/student-app
   eas build:configure
   eas build -p android --profile preview
   ```
4. EAS builds the standalone APK on Expo cloud infrastructure and delivers an installable `.apk` download link.
