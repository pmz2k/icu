from typing import Optional

from sqlalchemy.orm import Session

from app import models, schemas
from app.hashing import generate_pseudonym, hash_nhs_number


def get_patient_by_nhs_hash(db: Session, nhs_hash: str) -> Optional[models.Patient]:
    """Get patient by NHS number hash."""
    return db.query(models.Patient).filter(models.Patient.nhs_hash == nhs_hash).first()


def get_patient_by_id(db: Session, patient_id: str) -> Optional[models.Patient]:
    """Get patient by ID."""
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()


def create_patient(db: Session, patient: schemas.PatientCreate) -> models.Patient:
    """Create a new patient."""
    nhs_hash = hash_nhs_number(patient.nhs_number)

    existing = get_patient_by_nhs_hash(db, nhs_hash)
    if existing:
        raise ValueError("Patient with this NHS number already exists")

    count = db.query(models.Patient).count()
    pseudonym = generate_pseudonym(count + 1)

    db_patient = models.Patient(
        nhs_hash=nhs_hash,
        pseudonym=pseudonym,
        sex=patient.sex,
        age_band=patient.age_band,
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


def get_observations(db: Session, patient_id: str) -> list[models.Observation]:
    """Get all observations for a patient."""
    return (
        db.query(models.Observation)
        .filter(models.Observation.patient_id == patient_id)
        .order_by(models.Observation.performed_date.desc())
        .all()
    )


def create_observation(db: Session, obs: schemas.ObservationCreate) -> models.Observation:
    """Create observation."""
    db_obs = models.Observation(**obs.model_dump())
    db.add(db_obs)
    db.commit()
    db.refresh(db_obs)
    return db_obs


def get_medications(db: Session, patient_id: str) -> list[models.Medication]:
    """Get all medications for a patient."""
    return (
        db.query(models.Medication)
        .filter(models.Medication.patient_id == patient_id)
        .order_by(models.Medication.start_date.desc())
        .all()
    )


def create_medication(db: Session, med: schemas.MedicationCreate) -> models.Medication:
    """Create medication."""
    db_med = models.Medication(**med.model_dump())
    db.add(db_med)
    db.commit()
    db.refresh(db_med)
    return db_med


def get_all_patients(db: Session) -> list[models.Patient]:
    """Get all patients."""
    return db.query(models.Patient).all()


def create_export_job(db: Session, patient_id: Optional[str] = None) -> models.ExportJob:
    """Create export job."""
    db_job = models.ExportJob(patient_id=patient_id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def update_export_job(db: Session, job_id: str, csv_path: Optional[str], status: str) -> Optional[models.ExportJob]:
    """Update export job status/path."""
    job = db.query(models.ExportJob).filter(models.ExportJob.id == job_id).first()
    if job:
        job.csv_path = csv_path
        job.status = status
        db.commit()
        db.refresh(job)
    return job


def get_export_job(db: Session, job_id: str) -> Optional[models.ExportJob]:
    """Get export job by ID."""
    return db.query(models.ExportJob).filter(models.ExportJob.id == job_id).first()
