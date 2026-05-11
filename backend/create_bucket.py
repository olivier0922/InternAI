import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = f"{os.environ['SUPABASE_URL']}/storage/v1/bucket"
headers = {
    "Authorization": f"Bearer {os.environ['SUPABASE_KEY']}",
    "apikey": os.environ['SUPABASE_KEY']
}
data = {
    "id": "resumes",
    "name": "resumes",
    "public": True
}
res = requests.post(url, headers=headers, json=data)
print(res.status_code, res.text)
