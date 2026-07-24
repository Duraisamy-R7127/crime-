from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models import RoleEnum, StatusEnum, SeverityEnum

# --- Users ---
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: RoleEnum
    state: str = "Tamil Nadu"
    district: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    station: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True

# --- Districts ---
class DistrictResponse(BaseModel):
    id: int
    name: str
    population: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    risk_score: float
    prediction_score: float
    class Config:
        from_attributes = True

# --- Predictions ---
class PredictionResponse(BaseModel):
    id: int
    district_name: str
    category: str
    predicted_cases: int
    confidence_score: float
    forecast_month: str
    risk_level: SeverityEnum
    class Config:
        from_attributes = True

# --- FIRs ---
class FIRBase(BaseModel):
    state: str = "Tamil Nadu"
    district: str
    city: Optional[str] = None
    area: Optional[str] = None
    police_station: str
    crime_type: str
    crime_category: str
    complainant_name: Optional[str] = None
    phone: Optional[str] = None
    incident_description: str
    evidence: Optional[str] = None
    victim_details: Optional[str] = None
    suspect_details: Optional[str] = None
    incident_time: Optional[datetime] = None
    location_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: StatusEnum = StatusEnum.open

class FIRCreate(FIRBase):
    pass

class FIRResponse(FIRBase):
    id: int
    fir_number: str
    date_reported: datetime
    class Config:
        from_attributes = True

# --- Criminals ---
class CriminalBase(BaseModel):
    name: str
    alias: Optional[str] = None
    address: str
    aadhaar: Optional[str] = None
    crime_history: str
    arrest_records: str
    risk_level: SeverityEnum
    state: str = "Tamil Nadu"
    district: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    police_station: Optional[str] = None

class CriminalCreate(CriminalBase):
    pass

class CriminalResponse(CriminalBase):
    id: int
    class Config:
        from_attributes = True

# --- Alerts ---
class AlertResponse(BaseModel):
    id: int
    message: str
    severity: SeverityEnum
    created_at: datetime
    source: str
    acknowledged: bool
    state: str = "Tamil Nadu"
    district: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    class Config:
        from_attributes = True

# --- Analytics ---
class DashboardStats(BaseModel):
    total_crimes_ytd: int
    active_cases: int
    avg_response_time_min: float
    disposal_rate_pct: float

# --- Legal ---
class LegalSectionResponse(BaseModel):
    id: int
    crime_type: str
    category: Optional[str] = None
    ipc_section: str
    bns_section: str
    punishment: str
    is_bailable: bool
    is_cognizable: Optional[bool] = True
    is_compoundable: Optional[bool] = False
    description: Optional[str] = None
    investigation_procedure: Optional[str] = None
    court_jurisdiction: Optional[str] = None
    evidence_required: Optional[str] = None
    legal_notes: Optional[str] = None
    class Config:
        from_attributes = True

# --- Deployment ---
class DeploymentResponse(BaseModel):
    id: int
    state: str = "Tamil Nadu"
    district: str
    city: Optional[str] = None
    area: Optional[str] = None
    location_name: str
    action_type: str
    risk_score: int
    reason: str
    status: str
    class Config:
        from_attributes = True

class MissingPersonBase(BaseModel):
    name: str
    age: int
    gender: str
    description: str
    last_seen_date: datetime
    state: str = "Tamil Nadu"
    district: str
    city: Optional[str] = None
    area: Optional[str] = None
    status: str = "Missing"

class MissingPersonCreate(MissingPersonBase):
    pass

class MissingPersonResponse(MissingPersonBase):
    id: int

    class Config:
        from_attributes = True

class EmergencyIncidentBase(BaseModel):
    incident_type: str
    description: str
    severity: SeverityEnum = SeverityEnum.high
    state: str = "Tamil Nadu"
    district: str
    city: Optional[str] = None
    area: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str = "Active"

class EmergencyIncidentCreate(EmergencyIncidentBase):
    pass

class EmergencyIncidentResponse(EmergencyIncidentBase):
    id: int
    reported_at: datetime

    class Config:
        from_attributes = True
