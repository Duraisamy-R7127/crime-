from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

import models, schemas, auth
from database import get_db

router = APIRouter(prefix="/criminals", tags=["criminals"])

@router.get("/", response_model=List[schemas.CriminalResponse])
def get_criminals(
    district: Optional[str] = None,
    city: Optional[str] = None,
    area: Optional[str] = None,
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    query = db.query(models.Criminal)
    if district:
        query = query.filter(models.Criminal.district == district)
    if city:
        query = query.filter(models.Criminal.city == city)
    if area:
        query = query.filter(models.Criminal.area == area)
    if risk_level:
        query = query.filter(models.Criminal.risk_level == risk_level)
    return query.order_by(models.Criminal.risk_level.desc()).limit(100).all()

@router.post("/", response_model=schemas.CriminalResponse)
def create_criminal(criminal: schemas.CriminalCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_criminal = models.Criminal(**criminal.model_dump())
    db.add(db_criminal)
    db.commit()
    db.refresh(db_criminal)
    return db_criminal

@router.get("/{criminal_id}", response_model=schemas.CriminalResponse)
def get_criminal(criminal_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    criminal = db.query(models.Criminal).filter(models.Criminal.id == criminal_id).first()
    if not criminal:
        raise HTTPException(status_code=404, detail="Criminal not found")
    return criminal
