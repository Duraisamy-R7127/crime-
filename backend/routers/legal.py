from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

import models, schemas, auth
from database import get_db

router = APIRouter(prefix="/legal", tags=["legal"])

@router.get("/", response_model=List[schemas.LegalSectionResponse])
def search_legal(
    query: str = "",
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    q = db.query(models.LegalSection)
    if query:
        search_query = f"%{query}%"
        q = q.filter(
            (models.LegalSection.crime_type.ilike(search_query)) |
            (models.LegalSection.ipc_section.ilike(search_query)) |
            (models.LegalSection.bns_section.ilike(search_query)) |
            (models.LegalSection.category.ilike(search_query))
        )
    if category:
        q = q.filter(models.LegalSection.category == category)
    return q.order_by(models.LegalSection.category, models.LegalSection.crime_type).all()

@router.get("/categories")
def get_legal_categories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    results = db.query(models.LegalSection.category).distinct().order_by(models.LegalSection.category).all()
    return [r[0] for r in results if r[0]]

@router.get("/{legal_id}", response_model=schemas.LegalSectionResponse)
def get_legal_detail(
    legal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    item = db.query(models.LegalSection).filter(models.LegalSection.id == legal_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Legal section not found")
    return item
