from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import os
from pydantic import BaseModel

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")

# Initialize client only if url and key are present, to avoid crash on import if missing
supabase: Client = None
if url and key:
    supabase = create_client(url, key)

security = HTTPBearer()

class User(BaseModel):
    id: str
    email: str

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> User:
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase credentials not configured",
        )
        
    token = credentials.credentials
    try:
        response = supabase.auth.get_user(token)
        user_data = response.user
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return User(id=user_data.id, email=user_data.email)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
        )
