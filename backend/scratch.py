import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models
from sqlalchemy import func, case

db = SessionLocal()

# This is the original failing query
try:
    results = db.query(
        models.FIR.district,
        func.count(models.FIR.id).label("total"),
        func.count(models.FIR.id).filter(models.FIR.status == models.StatusEnum.open).label("open_cases")
    ).group_by(models.FIR.district).all()
    print("Original risk query works!")
except Exception as e:
    print(f"Original query failed: {e}")

# This is the proposed fix
try:
    results = db.query(
        models.FIR.district,
        func.count(models.FIR.id).label("total"),
        func.sum(case((models.FIR.status == 'open', 1), else_=0)).label("open_cases")
    ).group_by(models.FIR.district).all()
    print("Fixed risk query works!")
    print(results[:2])
except Exception as e:
    print(f"Fixed query failed: {e}")
