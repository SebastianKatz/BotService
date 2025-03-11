import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Connected to Supabase successfully")
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        raise e
else:
    raise ValueError("Supabase URL or key not provided. Please check your .env file.")

def is_connected():
    """
    Check if Supabase connection is established
    """
    return supabase is not None

def get_client():
    """
    Get the Supabase client
    """
    return supabase 