"""Consistent API errors."""
from fastapi import HTTPException

def api_error(status: int, code: str, message: str, **extra):
    detail = {"code": code, "message": message, **extra}
    raise HTTPException(status_code=status, detail=detail)
