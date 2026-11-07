"""
LPU GoCart - Supabase Database & Auth Connectivity Verification Script
Tests both:
1. Supabase REST API connection (using SUPABASE_URL and SUPABASE_ANON_KEY / SERVICE_ROLE_KEY)
2. Direct PostgreSQL connection (using SUPABASE_DB_URL via SQLAlchemy / psycopg2)
"""

import os
import sys
from pathlib import Path

# Load backend/.env if present
env_path = Path(__file__).resolve().parent.parent / "backend" / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY", "")
db_url = os.environ.get("SUPABASE_DB_URL", "")

print("=" * 60)
print("     LPU GoCart - Supabase Connection Health Check")
print("=" * 60)
print(f"Supabase URL: {supabase_url if supabase_url else '[NOT SET]'}")
print(f"Postgres URL: {'[CONFIGURED]' if db_url and 'your-db-password' not in db_url else '[PLACEHOLDER / NOT SET]'}")
print("-" * 60)

# Check if placeholders are still present
if not supabase_url or "your-project-id" in supabase_url or "your-project-ref" in supabase_url:
    print("\n[INFO] Placeholders detected in backend/.env.")
    print("Please follow the Phase 2 instructions to:")
    print("1. Create your free Supabase project at https://supabase.com")
    print("2. Run the SQL migrations from supabase/migrations/001_initial_schema.sql")
    print("3. Run supabase/migrations/002_row_level_security.sql")
    print("4. Run supabase/seed.sql")
    print("5. Paste your real project URL and keys into backend/.env")
    sys.exit(0)

# Test Supabase Python client connection
try:
    from supabase import create_client, Client
    client: Client = create_client(supabase_url, supabase_key)
    # Attempt to query routes
    response = client.table("routes").select("id, code, name").execute()
    print(f"\n[OK] Supabase REST API connected successfully!")
    print(f"     Found {len(response.data)} campus routes in database.")
    for r in response.data:
        print(f"     - Route: {r.get('code')} ({r.get('name')})")
except Exception as e:
    print(f"\n[ERROR] Supabase API connection failed: {e}")

# Test direct PostgreSQL database connection if db_url is configured
if db_url and "your-db-password" not in db_url:
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM public.carts;")).scalar()
            print(f"[OK] Direct PostgreSQL connection verified via SQLAlchemy!")
            print(f"     Total electric carts in fleet: {result}")
    except Exception as e:
        print(f"[WARNING] PostgreSQL direct connection test: {e}")

print("=" * 60)
