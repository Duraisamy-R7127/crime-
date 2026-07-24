from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

import models, schemas, auth
from database import get_db

router = APIRouter(prefix="/emergency", tags=["emergency"])

@router.get("/", response_model=List[schemas.EmergencyIncidentResponse])
def get_emergencies(
    district: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    query = db.query(models.EmergencyIncident)
    if district:
        query = query.filter(models.EmergencyIncident.district == district)
    if status:
        query = query.filter(models.EmergencyIncident.status == status)
    return query.order_by(models.EmergencyIncident.reported_at.desc()).limit(50).all()

@router.post("/", response_model=schemas.EmergencyIncidentResponse)
def create_emergency(incident: schemas.EmergencyIncidentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_incident = models.EmergencyIncident(**incident.model_dump())
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident
