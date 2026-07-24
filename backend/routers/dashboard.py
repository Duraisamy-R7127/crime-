from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, case, extract
import models, schemas, auth
from database import get_db
from datetime import datetime, timedelta
from typing import Optional, List

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(
    district: Optional[str] = None,
    city: Optional[str] = None,
    area: Optional[str] = None,
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
        
    total_crimes_ytd = query.count()
    active_cases = query.filter(models.FIR.status != models.StatusEnum.resolved).count()
    
    avg_response_time_min = 11.4
    if total_crimes_ytd == 0:
        disposal_rate_pct = 0.0
    else:
        resolved_count = query.filter(models.FIR.status == models.StatusEnum.resolved).count()
        disposal_rate_pct = (resolved_count / total_crimes_ytd) * 100

    return schemas.DashboardStats(
        total_crimes_ytd=total_crimes_ytd,
        active_cases=active_cases,
        avg_response_time_min=avg_response_time_min,
        disposal_rate_pct=round(disposal_rate_pct, 1)
    )

@router.get("/alerts", response_model=list[schemas.AlertResponse])
def get_alerts(
    district: Optional[str] = None,
    city: Optional[str] = None,
    area: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    query = db.query(models.Alert)
    if district:
        query = query.filter(models.Alert.district == district)
    if city:
        query = query.filter(models.Alert.city == city)
    if area:
        query = query.filter(models.Alert.area == area)
    return query.order_by(models.Alert.created_at.desc()).limit(10).all()

@router.get("/deployments", response_model=list[schemas.DeploymentResponse])
def get_deployments(
    district: Optional[str] = None,
    city: Optional[str] = None,
    area: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    query = db.query(models.DeploymentRecommendation).filter(models.DeploymentRecommendation.status == "pending")
    if district:
        query = query.filter(models.DeploymentRecommendation.district == district)
    if city:
        query = query.filter(models.DeploymentRecommendation.city == city)
    if area:
        query = query.filter(models.DeploymentRecommendation.area == area)
    return query.all()

@router.get("/districts", response_model=list[schemas.DistrictResponse])
def get_districts(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    """Return all districts for populating dropdowns and map."""
    return db.query(models.District).order_by(models.District.name).all()

@router.get("/district-summary")
def get_district_summary(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    """Return per-district crime counts for state-wide overview / comparison."""
    results = db.query(
        models.FIR.district,
        func.count(models.FIR.id).label("total"),
        func.sum(case((models.FIR.status == 'open', 1), else_=0)).label("open_cases"),
        func.sum(case((models.FIR.status == 'resolved', 1), else_=0)).label("resolved")
    ).group_by(models.FIR.district).all()
    
    return [
        {"district": r[0], "total": r[1], "open_cases": r[2], "resolved": r[3]}
        for r in results
    ]

@router.get("/cities")
def get_cities(district: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    """Return unique cities in a district for cascading dropdown."""
    cities = db.query(distinct(models.FIR.city)).filter(
        models.FIR.district == district, models.FIR.city != None
    ).all()
    return [c[0] for c in cities if c[0]]

@router.get("/areas")
def get_areas(district: str, city: Optional[str] = None, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    """Return unique areas in a district/city for cascading dropdown."""
    query = db.query(distinct(models.FIR.area)).filter(
        models.FIR.district == district, models.FIR.area != None
    )
    if city:
        query = query.filter(models.FIR.city == city)
    areas = query.all()
    return [a[0] for a in areas if a[0]]

@router.get("/crime-by-type")
def get_crime_by_type(
    district: Optional[str] = None,
    city: Optional[str] = None,
    area: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Crime breakdown by type for charts."""
    query = db.query(
        models.FIR.crime_type,
        func.count(models.FIR.id).label("count"),
        func.sum(case((models.FIR.status == 'open', 1), else_=0)).label("open_cases"),
        func.sum(case((models.FIR.status == 'investigating', 1), else_=0)).label("investigating_cases"),
        func.sum(case((models.FIR.status == 'resolved', 1), else_=0)).label("resolved_cases")
    )
    if district:
        query = query.filter(models.FIR.district == district)
    if city:
        query = query.filter(models.FIR.city == city)
    if area:
        query = query.filter(models.FIR.area == area)
    
    results = query.group_by(models.FIR.crime_type).order_by(func.count(models.FIR.id).desc()).all()
    return [{"crime_type": r[0], "count": r[1], "open_cases": r[2], "investigating_cases": r[3], "resolved_cases": r[4]} for r in results]

@router.get("/crime-trend")
def get_crime_trend(
    district: Optional[str] = None,
    city: Optional[str] = None,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Daily crime count for trend chart, padded with zeros for missing days."""
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days - 1)
    
    # Convert start_date to datetime to match database filter behavior
    start_dt = datetime.combine(start_date, datetime.min.time())
    
    query = db.query(
        func.date(models.FIR.date_reported).label("day"),
        func.count(models.FIR.id).label("count")
    ).filter(models.FIR.date_reported >= start_dt)
    
    if district:
        query = query.filter(models.FIR.district == district)
    if city:
        query = query.filter(models.FIR.city == city)
    
    results = query.group_by(func.date(models.FIR.date_reported)).all()
    data_dict = {str(r[0]): r[1] for r in results if r[0]}
    
    final_results = []
    for i in range(days):
        current_day = start_date + timedelta(days=i)
        day_str = current_day.strftime("%Y-%m-%d")
        final_results.append({
            "day": day_str,
            "count": data_dict.get(day_str, 0)
        })
        
    return final_results

@router.get("/most-wanted")
def get_most_wanted(
    district: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Most wanted criminals (high/critical risk)."""
    query = db.query(models.Criminal).filter(
        models.Criminal.risk_level.in_([models.SeverityEnum.high, models.SeverityEnum.critical])
    )
    if district:
        query = query.filter(models.Criminal.district == district)
    return query.limit(10).all()

@router.get("/missing-persons")
def get_missing_persons(
    district: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Missing persons FIRs."""
    query = db.query(models.FIR).filter(models.FIR.crime_type == "Missing Persons")
    if district:
        query = query.filter(models.FIR.district == district)
    return query.order_by(models.FIR.date_reported.desc()).limit(20).all()

@router.get("/risk-ranking")
def get_risk_ranking(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    """Calculate and return district risk ranking based on active cases."""
    results = db.query(
        models.FIR.district,
        func.count(models.FIR.id).label("total"),
        func.sum(case((models.FIR.status == 'open', 1), else_=0)).label("open_cases"),
        func.sum(case((models.FIR.status == 'investigating', 1), else_=0)).label("investigating_cases")
    ).group_by(models.FIR.district).all()
    
    ranking = []
    for r in results:
        dist = r[0]
        total = r[1]
        open_cases = r[2]
        investigating_cases = r[3]
        
        if total > 0:
            # Weight: open cases count fully, investigating cases count 50%
            weighted_active = open_cases + (investigating_cases * 0.5)
            risk = min(100, int((weighted_active / total) * 100))
        else:
            risk = 0
            
        confidence = min(0.99, 0.70 + (total / 1000.0) * 0.25)
        ranking.append({"district": dist, "risk": risk, "confidence": round(confidence, 2)})
        
    ranking.sort(key=lambda x: x["risk"], reverse=True)
    return ranking

@router.get("/festival-impact")
def get_festival_impact(
    district: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Calculate real crime uplift % during festival windows vs baseline."""
    # Festival windows (month, day range)
    festivals = [
        {"name": "Pongal", "month": 1, "start_day": 13, "end_day": 16},
        {"name": "Holi",   "month": 3, "start_day": 24, "end_day": 27},
        {"name": "Diwali", "month": 11, "start_day": 1,  "end_day": 5},
        {"name": "New Year","month": 1, "start_day": 1,  "end_day": 3},
    ]
    
    base_query = db.query(func.count(models.FIR.id))
    if district:
        base_query = base_query.filter(models.FIR.district == district)
    
    total_days = db.query(
        func.count(func.distinct(func.date(models.FIR.date_reported)))
    )
    if district:
        total_days = total_days.filter(models.FIR.district == district)
    day_count = total_days.scalar() or 1
    total_crimes = base_query.scalar() or 0
    baseline_per_day = total_crimes / max(day_count, 1)
    
    result = []
    for f in festivals:
        q = db.query(func.count(models.FIR.id)).filter(
            extract('month', models.FIR.date_reported) == f['month'],
            extract('day', models.FIR.date_reported) >= f['start_day'],
            extract('day', models.FIR.date_reported) <= f['end_day']
        )
        if district:
            q = q.filter(models.FIR.district == district)
        festival_crimes = q.scalar() or 0
        window_days = f['end_day'] - f['start_day'] + 1
        festival_per_day = festival_crimes / window_days
        
        if baseline_per_day > 0:
            uplift = round(((festival_per_day - baseline_per_day) / baseline_per_day) * 100, 1)
        else:
            uplift = 0.0
        
        result.append({"festival": f["name"], "uplift": max(0, uplift), "crimes": festival_crimes})
    
    return result

@router.get("/map-markers")
def get_map_markers(
    district: Optional[str] = None,
    city: Optional[str] = None,
    area: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Return latest FIR locations for map rendering."""
    query = db.query(models.FIR).filter(models.FIR.latitude != None, models.FIR.longitude != None)
    if district:
        query = query.filter(models.FIR.district == district)
    if city:
        query = query.filter(models.FIR.city == city)
    if area:
        query = query.filter(models.FIR.area == area)
        
    results = query.order_by(models.FIR.date_reported.desc()).limit(500).all()
    
    return [
        {
            "id": r.id,
            "fir_number": r.fir_number,
            "crime_type": r.crime_type,
            "district": r.district,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "date_reported": r.date_reported
        } for r in results
    ]

@router.get("/analytics/yoy")
def get_analytics_yoy(
    district: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(
        extract('year', models.FIR.date_reported).label('year'),
        extract('month', models.FIR.date_reported).label('month'),
        func.count(models.FIR.id).label('count')
    )
    if district:
        query = query.filter(models.FIR.district == district)
    
    results = query.group_by(
        extract('year', models.FIR.date_reported),
        extract('month', models.FIR.date_reported)
    ).all()

    data = {2024: [0]*12, 2025: [0]*12, 2026: [0]*12}
    for r in results:
        y, m, c = int(r[0]), int(r[1]), r[2]
        if y in data and 1 <= m <= 12:
            data[y][m-1] = c
            
    return data

@router.get("/analytics/seasonal")
def get_analytics_seasonal(
    district: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(
        extract('month', models.FIR.date_reported).label('month'),
        func.count(models.FIR.id).label('count')
    )
    if district:
        query = query.filter(models.FIR.district == district)
        
    results = query.group_by(extract('month', models.FIR.date_reported)).all()
    
    q_data = [0, 0, 0, 0]
    for r in results:
        m, c = int(r[0]), r[1]
        if 1 <= m <= 3: q_data[0] += c
        elif 4 <= m <= 6: q_data[1] += c
        elif 7 <= m <= 9: q_data[2] += c
        elif 10 <= m <= 12: q_data[3] += c
        
    return q_data
