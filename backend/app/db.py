"""
Single shared Supabase client. Every other module imports `supabase` from here
instead of creating its own connection.
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL / SUPABASE_KEY not set. Copy backend/.env.example to "
        "backend/.env and fill in your Supabase project credentials."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
