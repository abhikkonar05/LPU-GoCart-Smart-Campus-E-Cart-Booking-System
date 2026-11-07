# LPU GoCart – Supabase Configuration & Migrations

This directory contains the database migration scripts, initial schema definitions, and seed data for Lovely Professional University's GoCart platform.

---

## Migrations Overview
- `migrations/001_initial_schema.sql`: Contains the creation of all 16 tables, foreign key constraints, indexes, and triggers.
- `migrations/002_row_level_security.sql`: Defines strict Row Level Security (RLS) policies for Student, Driver, and Administrator roles.
- `seed.sql`: Realistic demo data for testing: LPU campus routes, stops, carts (8-seat configurations), and demo profiles.

---

## Applying Migrations to Supabase (Zero-Cost Free Tier)

1. Log in to [Supabase Console](https://supabase.com/dashboard).
2. Open your project (e.g. `lpu-gocart`).
3. Click on **SQL Editor** in the left sidebar navigation.
4. Click **+ New Query**.
5. Copy and paste the contents of `migrations/001_initial_schema.sql` and click **Run**.
6. Repeat for `migrations/002_row_level_security.sql`.
7. Repeat for `seed.sql` to populate sample carts and LPU campus stops.

