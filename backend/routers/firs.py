import csv
from io import StringIO
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional

import models, schemas, auth
from database import get_db
from datetime import datetime

router = APIRouter(prefix="/firs", tags=["firs"])

@router.get("/", response_model=List[schemas.FIRResponse])
def get_firs(
    skip: int = 0,
    limit: int = 100,
    district: Optional[str] = None,
    city: Optional[str] = None,
    area: Optional[str] = None,
    crime_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    query = db.query(models.FIR)
    if district:
        query = query.filter(models.FIR.district == district)
    if city:
        query = query.filter(models.FIR.city == city)
    if area:
        query = query.filter(models.FIR.area == area)
    if crime_type:
        query = query.filter(models.FIR.crime_type == crime_type)
    if status_filter:
        query = query.filter(models.FIR.status == status_filter)
    return query.order_by(models.FIR.date_reported.desc()).offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.FIRResponse)
def create_fir(fir: schemas.FIRCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    if not fir.district or not fir.crime_type or not fir.incident_description:
        raise HTTPException(status_code=400, detail="Missing required fields: district, crime_type, incident_description")

    # Generate FIR Number: TN-<DIST>-YYYY-XXXXXX
    dist_code = fir.district[:3].upper()
    year = datetime.now().year
    
    count = db.query(models.FIR).count() + 1
    fir_number = f"TN-{dist_code}-{year}-{str(count).zfill(6)}"
    
    # Check duplicate
    existing = db.query(models.FIR).filter(models.FIR.fir_number == fir_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="FIR number already exists")
    
    fir_data = fir.model_dump()
    db_fir = models.FIR(**fir_data, fir_number=fir_number)
    
    db.add(db_fir)
    db.commit()
    db.refresh(db_fir)
    
    # Generate an Alert for new crimes
    alert = models.Alert(
        message=f"New FIR {fir_number} registered for {fir.crime_type} in {fir.area or fir.city or fir.district}.",
        severity=models.SeverityEnum.low,
        source=fir.police_station,
        state="Tamil Nadu",
        district=fir.district,
        city=fir.city,
        area=fir.area
    )
    db.add(alert)
    db.commit()
    
    return db_fir

@router.get("/search", response_model=List[schemas.FIRResponse])
def search_firs(
    q: str = "",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    if not q:
        return []
    search_query = f"%{q}%"
    return db.query(models.FIR).filter(
        (models.FIR.district.ilike(search_query)) |
        (models.FIR.city.ilike(search_query)) |
        (models.FIR.area.ilike(search_query)) |
        (models.FIR.police_station.ilike(search_query)) |
        (models.FIR.incident_description.ilike(search_query)) |
        (models.FIR.fir_number.ilike(search_query))
    ).order_by(models.FIR.date_reported.desc()).limit(50).all()

@router.get("/export")
def export_firs(
    district: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    query = db.query(models.FIR)
    if district:
        query = query.filter(models.FIR.district == district)
    
    firs = query.order_by(models.FIR.date_reported.desc()).limit(1000).all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["FIR Number", "District", "City", "Area", "Crime Type", "Status", "Date Reported", "Complainant Name", "Victim Details", "Suspect Details"])
    
    for fir in firs:
        writer.writerow([
            fir.fir_number,
            fir.district,
            fir.city or "",
            fir.area or "",
            fir.crime_type,
            fir.status.value,
            fir.date_reported.strftime("%Y-%m-%d %H:%M:%S"),
            fir.complainant_name or "",
            fir.victim_details or "",
            fir.suspect_details or ""
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=firs_{district or 'TN'}.csv"}
    )

@router.get("/{fir_id}", response_model=schemas.FIRResponse)
def get_fir(fir_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    fir = db.query(models.FIR).filter(models.FIR.id == fir_id).first()
    if not fir:
        raise HTTPException(status_code=404, detail="FIR not found")
    return fir
