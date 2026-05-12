import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path('.') / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

try:
    from supabase import create_client, Client
except ImportError:
    print("Supabase package not installed. Skipping database clean up.")
    sys.exit(0)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Supabase credentials not found. Skipping clean up.")
    sys.exit(0)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def clean_expired_jobs(days: int = 30):
    print(f"Cleaning jobs older than {days} days...")
    cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    # We delete in batches to avoid URL too long issues or hitting limits
    offset = 0
    batch = 500
    all_jobs_to_delete = []

    # Fetch all jobs to delete
    while True:
        res = supabase.table("jobs").select("id").lt("created_at", cutoff_date).range(offset, offset + batch - 1).execute()
        if not res.data:
            break
        
        all_jobs_to_delete.extend([row["id"] for row in res.data])
        
        if len(res.data) < batch:
            break
        offset += batch

    print(f"Found {len(all_jobs_to_delete)} expired jobs.")

    if not all_jobs_to_delete:
        print("No jobs to delete.")
        return

    # Delete in batches of 100
    deleted_count = 0
    for i in range(0, len(all_jobs_to_delete), 100):
        batch_ids = all_jobs_to_delete[i:i + 100]
        supabase.table("jobs").delete().in_("id", batch_ids).execute()
        deleted_count += len(batch_ids)
        
    print(f"Successfully deleted {deleted_count} expired jobs.")

if __name__ == "__main__":
    # Default is 30 days, can be overridden with EXPIRE_DAYS env var
    days_to_keep = int(os.getenv("EXPIRE_DAYS", "30"))
    clean_expired_jobs(days=days_to_keep)
