from datetime import datetime, timedelta
import logging
import random
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.auth import ACCESS_TOKEN_EXPIRE_MINUTES, Token, User, authenticate_user, create_access_token, get_current_user
from app.database import engine, get_db
from app.export import generate_csv_export
from app.hashing import hash_nhs_number
from app.redaction import add_redaction_middleware


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NHS Mock EPR System",
    description="Mock Electronic Patient Record system for antipsychotic monitoring",
    version="1.0.0",
)

add_redaction_middleware(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/oauth/token", response_model=Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Mock OAuth2 token endpoint."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/oauth/userinfo", response_model=User, tags=["Authentication"])
async def get_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@app.get("/Patient", response_model=schemas.PatientResponse, tags=["Patient"])
async def search_patient(
    identifier: str = Query(..., description="NHS number"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search for patient by NHS number."""
    logger.info("User %s searching for patient", current_user.username)

    try:
        nhs_hash = hash_nhs_number(identifier)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    patient = crud.get_patient_by_nhs_hash(db, nhs_hash)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    logger.info("Patient found: %s", patient.pseudonym)
    return patient


@app.post("/Patient", response_model=schemas.PatientResponse, status_code=status.HTTP_201_CREATED, tags=["Patient"])
async def create_patient(
    patient: schemas.PatientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new patient."""
    logger.info("User %s creating new patient", current_user.username)
    try:
        db_patient = crud.create_patient(db, patient)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    logger.info("Patient created: %s", db_patient.pseudonym)
    return db_patient


@app.get("/Observation", response_model=list[schemas.ObservationResponse], tags=["Observation"])
async def get_observations(
    patient: str = Query(..., description="Patient ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all observations for a patient."""
    db_patient = crud.get_patient_by_id(db, patient)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    observations = crud.get_observations(db, patient)
    logger.info("Retrieved %s observations for %s", len(observations), db_patient.pseudonym)
    return observations


@app.post(
    "/Observation",
    response_model=schemas.ObservationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Observation"],
)
async def create_observation(
    observation: schemas.ObservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new observation."""
    db_patient = crud.get_patient_by_id(db, observation.patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db_obs = crud.create_observation(db, observation)
    logger.info("Observation created for %s: %s", db_patient.pseudonym, observation.type)
    return db_obs


@app.get("/MedicationRequest", response_model=list[schemas.MedicationResponse], tags=["Medication"])
async def get_medications(
    patient: str = Query(..., description="Patient ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all medications for a patient."""
    db_patient = crud.get_patient_by_id(db, patient)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    medications = crud.get_medications(db, patient)
    logger.info("Retrieved %s medications for %s", len(medications), db_patient.pseudonym)
    return medications


@app.post(
    "/MedicationRequest",
    response_model=schemas.MedicationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Medication"],
)
async def create_medication(
    medication: schemas.MedicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new medication."""
    db_patient = crud.get_patient_by_id(db, medication.patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db_med = crud.create_medication(db, medication)
    logger.info("Medication created for %s: %s", db_patient.pseudonym, medication.drug_name)
    return db_med


@app.post("/export/csv", response_model=schemas.ExportJobResponse, tags=["Export"])
async def create_csv_export(
    patient_id: Optional[str] = Query(None, description="Patient ID (optional - exports all if not provided)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create CSV export job."""
    if patient_id:
        db_patient = crud.get_patient_by_id(db, patient_id)
        if not db_patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        logger.info("Creating export for %s", db_patient.pseudonym)
    else:
        logger.info("Creating export for all patients")

    job = crud.create_export_job(db, patient_id)

    try:
        zip_path = generate_csv_export(db, job.id, patient_id)
        job = crud.update_export_job(db, job.id, zip_path, "COMPLETE") or job
        logger.info("Export job %s completed", job.id)
    except Exception as exc:
        crud.update_export_job(db, job.id, None, "FAILED")
        logger.error("Export job %s failed: %s", job.id, exc)
        raise HTTPException(status_code=500, detail="Export failed") from exc

    return job


@app.get("/export/csv/{job_id}", tags=["Export"])
async def download_csv_export(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download CSV export file."""
    job = crud.get_export_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Export job not found")
    if job.status != "COMPLETE":
        raise HTTPException(status_code=400, detail=f"Export job status: {job.status}")
    if not job.csv_path:
        raise HTTPException(status_code=404, detail="Export file not found")

    logger.info("User %s downloading export %s", current_user.username, job_id)
    return FileResponse(job.csv_path, media_type="application/zip", filename=f"epr_export_{job_id}.zip")


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/simulate/events", tags=["Simulator"])
async def simulate_events(
    patient_id: str = Query(..., description="Patient ID"),
    count: int = Query(10, ge=1, le=50, description="Number of events to generate"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate random observations for a patient."""
    db_patient = crud.get_patient_by_id(db, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    test_types = [
        {"type": "HbA1c", "unit": "mmol/mol", "normal_range": (20, 42)},
        {"type": "Weight", "unit": "kg", "normal_range": (60, 90)},
        {"type": "ECG", "unit": "ms", "normal_range": (350, 450)},
        {"type": "FBC", "unit": "x10^9/L", "normal_range": (4, 11)},
        {"type": "LFT", "unit": "U/L", "normal_range": (10, 40)},
    ]

    for _ in range(count):
        test = random.choice(test_types)
        value = random.uniform(*test["normal_range"])
        rand = random.random()
        if rand < 0.7:
            interpretation = "NORMAL"
        elif rand < 0.9:
            interpretation = "ABNORMAL"
            value *= 1.3
        else:
            interpretation = "CRITICAL"
            value *= 1.8

        obs = schemas.ObservationCreate(
            patient_id=patient_id,
            type=test["type"],
            value=round(value, 2),
            unit=test["unit"],
            interpretation=interpretation,
            performed_date=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
        )
        crud.create_observation(db, obs)

    logger.info("Generated %s simulated events for %s", count, db_patient.pseudonym)
    return {"message": f"Created {count} observations", "patient_pseudonym": db_patient.pseudonym}
