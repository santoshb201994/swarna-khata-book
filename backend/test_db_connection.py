"""
Diagnostic utility to test PostgreSQL connection to Neon from local terminal.
"""
import os
import sys
import socket
from urllib.parse import urlparse, parse_qsl
from pathlib import Path
from dotenv import load_dotenv

# Load environment
base_dir = Path(__file__).resolve().parent
load_dotenv(base_dir / '.env')
load_dotenv(base_dir.parent / '.env')

db_url = os.getenv("DATABASE_URL")

print("=" * 60)
print("  Neon PostgreSQL Connection Diagnostic")
print("=" * 60)

if not db_url:
    print("[ERROR] DATABASE_URL is not set in backend/.env or root .env")
    sys.exit(1)

parsed = urlparse(db_url)
host = parsed.hostname
port = parsed.port or 5432
dbname = parsed.path.replace('/', '')
user = parsed.username

print(f"Host:     {host}")
print(f"Port:     {port}")
print(f"Database: {dbname}")
print(f"User:     {user}")
print("-" * 60)

# Step 1: TCP Network Check
print("1. Testing TCP network reachability to Neon port 5432...")
try:
    with socket.create_connection((host, port), timeout=5) as sock:
        print("   --> TCP Network connection SUCCESSFUL! (Port is open and reachable)")
except Exception as e:
    print(f"   --> TCP Network connection FAILED: {e}")
    print("   Please check your firewall / VPN / proxy settings.")
    sys.exit(1)

# Step 2: Database Authentication Check
print("\n2. Testing PostgreSQL authentication & query...")
try:
    import psycopg2
    conn = psycopg2.connect(db_url, connect_timeout=10)
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print("   --> Authentication SUCCESSFUL!")
        print(f"   --> Server Version: {version}")
        cur.execute("SELECT current_user, current_database();")
        curr_user, curr_db = cur.fetchone()
        print(f"   --> Logged in as: '{curr_user}' on database '{curr_db}'")
    conn.close()
    print("\n[SUCCESS] Neon database is fully connected and ready to use!")
except Exception as e:
    print("   --> Authentication / Database connection FAILED:")
    print(f"       {e}")
    print("\n[ACTION REQUIRED] If this is a password authentication failure, please verify or reset")
    print("                  your password in the Neon console (Roles & Databases) and update DATABASE_URL.")
    sys.exit(1)
