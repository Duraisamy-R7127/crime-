from fastapi import APIRouter, Depends
from typing import Dict, Any, Optional
import models, auth
from ai import prediction, voice_nlp
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/forecast")
def get_forecast(district: Optional[str] = None, category: Optional[str] = None, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    return prediction.generate_forecast(db, district, category)

@router.get("/voice")
def process_voice_command(query: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    return voice_nlp.parse_voice_query(query, db)
