from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PatientCreate(BaseModel):
    nhs_number: str = Field(..., description="10-digit NHS number")
    sex: str = Field(..., pattern="^(M|F|Other)$")
    age_band: str = Field(..., description="Age band (e.g., 26-35)")


class PatientResponse(BaseModel):
    id: str
    pseudonym: str
    sex: str
    age_band: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ObservationCreate(BaseModel):
    patient_id: str
    type: str = Field(..., description="Test type (HbA1c, Weight, ECG, etc.)")
    value: float
    unit: str
    interpretation: str = Field(..., pattern="^(NORMAL|ABNORMAL|CRITICAL)$")
    performed_date: datetime


class ObservationResponse(BaseModel):
    id: str
    patient_id: str
    type: str
    value: float
    unit: str
    interpretation: str
    performed_date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MedicationCreate(BaseModel):
    patient_id: str
    drug_name: str
    dose: str
    start_date: datetime
    stop_date: Optional[datetime] = None


class MedicationResponse(BaseModel):
    id: str
    patient_id: str
    drug_name: str
    dose: str
    start_date: datetime
    stop_date: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExportJobResponse(BaseModel):
    id: str
    patient_id: Optional[str]
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
