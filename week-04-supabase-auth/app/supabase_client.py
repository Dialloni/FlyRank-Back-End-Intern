"""One Supabase client, built from environment variables. Never hardcode keys."""
import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]  # anon (public) key — never service_role

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
