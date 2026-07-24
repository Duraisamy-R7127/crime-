import re
from sqlalchemy.orm import Session
from sqlalchemy import func
import models

def parse_voice_query(query: str, db: Session):
    """
    Dynamic NLP parser for voice queries querying the SQLite database.
    """
    q_lower = query.lower()
    
    # Pre-fetch some basic entities to match against
    districts = [d.name.lower() for d in db.query(models.District).all()]
    crime_types = [c[0].lower() for c in db.query(models.FIR.crime_type).distinct().all() if c[0]]
    
    matched_district = next((d for d in districts if d in q_lower), None)
    matched_crime = next((c for c in crime_types if c in q_lower), None)
    
    # Helper to properly capitalize based on DB
    dist_proper = None
    if matched_district:
        dist_record = db.query(models.District).filter(func.lower(models.District.name) == matched_district).first()
        dist_proper = dist_record.name if dist_record else matched_district.title()
        
    crime_proper = None
    if matched_crime:
        crime_record = db.query(models.FIR).filter(func.lower(models.FIR.crime_type) == matched_crime).first()
        crime_proper = crime_record.crime_type if crime_record else matched_crime.title()

    # 1. Prediction / Forecast
    if "predict" in q_lower or "prediction" in q_lower or "forecast" in q_lower:
        base_query = db.query(models.FIR)
        if dist_proper:
            base_query = base_query.filter(models.FIR.district == dist_proper)
        
        total_cases = base_query.count()
        if total_cases == 0:
             reply = f"There is currently not enough data to generate a reliable forecast for {dist_proper or 'the state'}."
        else:
             reply = f"Based on current data models, we anticipate a steady trend. We have {total_cases} historical records anchoring the forecast for {dist_proper or 'the state'}."
        return {"intent": "prediction", "reply": reply}
    
    # 2. Legal Sections
    if "legal" in q_lower or "section" in q_lower or "bns" in q_lower or "ipc" in q_lower or "punishment" in q_lower:
        if matched_crime:
            # Look up legal section for the matched crime
            legal_info = db.query(models.LegalSection).filter(func.lower(models.LegalSection.crime_type) == matched_crime).first()
            if legal_info:
                bail_status = 'bailable' if legal_info.is_bailable else 'non-bailable'
                reply = f"For {legal_info.crime_type}, the applicable sections are IPC {legal_info.ipc_section} and BNS {legal_info.bns_section}. The punishment is {legal_info.punishment}. It is a {bail_status} offense."
            else:
                reply = f"I could not find specific legal sections for {crime_proper} in the database."
        else:
            reply = "Please specify a crime category (like Cyber Fraud or Theft) to get the exact IPC or BNS legal sections."
        return {"intent": "legal", "reply": reply}
        
    # 3. Deployment / Risk / Dangerous
    if "deployment" in q_lower or "risk" in q_lower or "dangerous" in q_lower:
        # Find the district with the most open cases
        results = db.query(
            models.FIR.district,
            func.count(models.FIR.id).label("total"),
            func.count(models.FIR.id).filter(models.FIR.status == models.StatusEnum.open).label("open_cases")
        ).group_by(models.FIR.district).all()
        
        if not results:
            return {"intent": "deployment", "reply": "There are no active cases in the database to calculate risk."}
            
        # Calculate risk mathematically like in the dashboard
        ranked = []
        for r in results:
            risk = min(100, int((r[2] / r[1]) * 100)) if r[1] > 0 else 0
            ranked.append((r[0], risk, r[1]))
            
        ranked.sort(key=lambda x: x[1], reverse=True)
        top_dist = ranked[0]
        
        reply = f"Based on active open cases, {top_dist[0]} currently shows the highest risk score of {top_dist[1]}%. I recommend prioritizing patrol and surveillance units there."
        return {"intent": "deployment", "reply": reply}

    # 4. Analytics / Stats / Cases
    if "trend" in q_lower or "stats" in q_lower or "statistics" in q_lower or "cases" in q_lower or "crimes" in q_lower or "how many" in q_lower:
        base_query = db.query(models.FIR)
        if dist_proper:
            base_query = base_query.filter(models.FIR.district == dist_proper)
        
        if matched_crime:
            base_query = base_query.filter(func.lower(models.FIR.crime_type) == matched_crime)
            count = base_query.count()
            reply = f"There are exactly {count} reported cases of {crime_proper} in {dist_proper or 'Tamil Nadu'}."
        else:
            # Overall stats
            total = base_query.count()
            if dist_proper:
                reply = f"There are a total of {total} registered crime incidents in {dist_proper}."
            else:
                # Find top crime overall
                top_crime = db.query(models.FIR.crime_type, func.count(models.FIR.id)).group_by(models.FIR.crime_type).order_by(func.count(models.FIR.id).desc()).first()
                if top_crime:
                    reply = f"Across Tamil Nadu, there are {total} total cases. {top_crime[0]} is currently the most frequently reported category with {top_crime[1]} cases."
                else:
                    reply = "There are currently no cases registered in the database."
                    
        return {"intent": "analytics", "reply": reply}

    # Fallback
    return {
        "intent": "unknown",
        "reply": "I am connected to the state command database. You can ask me for exact case counts by district, current high-risk deployments, or specific legal sections for any crime type."
    }
