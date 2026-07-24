from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum
from database import Base
from datetime import datetime

class RoleEnum(str, enum.Enum):
    super_admin = "super_admin"
    district_admin = "district_admin"
    police_officer = "police_officer"
    crime_analyst = "crime_analyst"
    cyber_cell = "cyber_cell"

class SeverityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class StatusEnum(str, enum.Enum):
    open = "open"
    investigating = "investigating"
    resolved = "resolved"

class District(Base):
    __tablename__ = "districts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    population = Column(Integer, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    risk_score = Column(Float, default=0.0)
    prediction_score = Column(Float, default=0.0)

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    district_name = Column(String, ForeignKey("districts.name"))
    category = Column(String, index=True)
    predicted_cases = Column(Integer)
    confidence_score = Column(Float)
    forecast_month = Column(String) # e.g. "2026-08"
    risk_level = Column(Enum(SeverityEnum))

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(Enum(RoleEnum), default=RoleEnum.police_officer)
    state = Column(String, default="Tamil Nadu")
    district = Column(String, ForeignKey("districts.name"), nullable=True)
    city = Column(String, nullable=True)
    area = Column(String, nullable=True)
    station = Column(String, nullable=True) # E.g., Chennai Central PS
    is_active = Column(Boolean, default=True)

class FIR(Base):
    __tablename__ = "firs"
    id = Column(Integer, primary_key=True, index=True)
    fir_number = Column(String, unique=True, index=True)
    state = Column(String, default="Tamil Nadu")
    district = Column(String, ForeignKey("districts.name"))
    city = Column(String, nullable=True)
    area = Column(String, nullable=True)
    police_station = Column(String)
    crime_type = Column(String, index=True)
    crime_category = Column(String)
    complainant_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    incident_description = Column(Text)
    evidence = Column(Text, nullable=True)
    victim_details = Column(Text, nullable=True)
    suspect_details = Column(Text, nullable=True)
    date_reported = Column(DateTime, default=datetime.utcnow)
    incident_time = Column(DateTime, nullable=True)
    location_name = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.open)

class Criminal(Base):
    __tablename__ = "criminals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    alias = Column(String, nullable=True)
    address = Column(Text)
    aadhaar = Column(String, unique=True, nullable=True)
    crime_history = Column(Text)
    arrest_records = Column(Text)
    risk_level = Column(Enum(SeverityEnum), default=SeverityEnum.low)
    state = Column(String, default="Tamil Nadu")
    district = Column(String, ForeignKey("districts.name"), nullable=True)
    city = Column(String, nullable=True)
    area = Column(String, nullable=True)
    police_station = Column(String, nullable=True)
class MissingPerson(Base):
    __tablename__ = "missing_persons"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    description = Column(Text)
    last_seen_date = Column(DateTime)
    status = Column(String, default="Missing") # Missing, Found
    state = Column(String, index=True)
    district = Column(String, index=True)
    city = Column(String, index=True, nullable=True)
    area = Column(String, index=True, nullable=True)

class EmergencyIncident(Base):
    __tablename__ = "emergency_incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_type = Column(String, index=True)
    description = Column(Text)
    severity = Column(Enum(SeverityEnum), default=SeverityEnum.high)
    status = Column(String, default="Active") # Active, Responded, Resolved
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    reported_at = Column(DateTime, default=datetime.utcnow)
    state = Column(String, index=True)
    district = Column(String, index=True)
    city = Column(String, index=True, nullable=True)
    area = Column(String, index=True, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text)
    severity = Column(Enum(SeverityEnum))
    created_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String)
    acknowledged = Column(Boolean, default=False)
    state = Column(String, default="Tamil Nadu")
    district = Column(String, ForeignKey("districts.name"), nullable=True)
    city = Column(String, nullable=True)
    area = Column(String, nullable=True)
    
class LegalSection(Base):
    __tablename__ = "legal_sections"
    id = Column(Integer, primary_key=True, index=True)
    crime_type = Column(String, index=True)
    category = Column(String, index=True, nullable=True)          # e.g. "Property", "Cyber"
    ipc_section = Column(String)
    bns_section = Column(String)
    punishment = Column(Text)
    is_bailable = Column(Boolean, default=True)
    is_cognizable = Column(Boolean, default=True)
    is_compoundable = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    investigation_procedure = Column(Text, nullable=True)
    court_jurisdiction = Column(Text, nullable=True)
    evidence_required = Column(Text, nullable=True)
    legal_notes = Column(Text, nullable=True)

class DeploymentRecommendation(Base):
    __tablename__ = "deployment_recommendations"
    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, default="Tamil Nadu")
    district = Column(String, ForeignKey("districts.name"))
    city = Column(String, nullable=True)
    area = Column(String, nullable=True)
    location_name = Column(String)
    action_type = Column(String) # e.g. "Extra patrol", "Install CCTV"
    risk_score = Column(Integer)
    reason = Column(Text)
    status = Column(String, default="pending") # pending, approved, rejected
