from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db

router = APIRouter(tags=["Database"])


@router.get("/database")
def database_test(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1 AS ping"))
        row = result.fetchone()
        return {"database": "Connected", "ping": row[0]}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )