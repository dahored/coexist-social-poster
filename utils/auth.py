# utils/auth.py
from fastapi import Header, HTTPException
import os

async def validate_token(authorization: str = Header(None)):
    expected_token = os.getenv("PERSONAL_ACCESS_TOKEN")

    if authorization != expected_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
