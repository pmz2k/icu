from datetime import datetime, timedelta

from app import crud, models, schemas
from app.database import SessionLocal


def seed_database() -> None:
    """Seed DB with 3 patients, observations, and medications."""
    db = SessionLocal()

    if db.query(models.Patient).count() > 0:
        print("Database already seeded. Skipping.")
        db.close()
        return

    print("Seeding database...")

    patient1 = crud.create_patient(db, schemas.PatientCreate(nhs_number="1234567890", sex="M", age_band="26-35"))
    observations_p1 = [
        {"type": "HbA1c", "value": 42, "unit": "mmol/mol", "interpretation": "NORMAL", "days_ago": 10},
        {"type": "Weight", "value": 85.5, "unit": "kg", "interpretation": "NORMAL", "days_ago": 10},
        {"type": "ECG", "value": 520, "unit": "ms", "interpretation": "CRITICAL", "days_ago": 11},
        {"type": "FBC", "value": 6.5, "unit": "x10^9/L", "interpretation": "NORMAL", "days_ago": 15},
        {"type": "LFT", "value": 25, "unit": "U/L", "interpretation": "NORMAL", "days_ago": 15},
        {"type": "Weight", "value": 86.0, "unit": "kg", "interpretation": "NORMAL", "days_ago": 30},
        {"type": "HbA1c", "value": 45, "unit": "mmol/mol", "interpretation": "NORMAL", "days_ago": 60},
        {"type": "ECG", "value": 420, "unit": "ms", "interpretation": "NORMAL", "days_ago": 60},
        {"type": "FBC", "value": 7.0, "unit": "x10^9/L", "interpretation": "NORMAL", "days_ago": 90},
        {"type": "LFT", "value": 30, "unit": "U/L", "interpretation": "NORMAL", "days_ago": 90},
    ]
    for obs_data in observations_p1:
        crud.create_observation(
            db,
            schemas.ObservationCreate(
                patient_id=patient1.id,
                type=obs_data["type"],
                value=obs_data["value"],
                unit=obs_data["unit"],
                interpretation=obs_data["interpretation"],
                performed_date=datetime.utcnow() - timedelta(days=obs_data["days_ago"]),
            ),
        )
    crud.create_medication(
        db,
        schemas.MedicationCreate(
            patient_id=patient1.id,
            drug_name="Olanzapine",
            dose="10mg",
            start_date=datetime.utcnow() - timedelta(days=180),
            stop_date=None,
        ),
    )
    crud.create_medication(
        db,
        schemas.MedicationCreate(
            patient_id=patient1.id,
            drug_name="Metformin",
            dose="500mg",
            start_date=datetime.utcnow() - timedelta(days=90),
            stop_date=None,
        ),
    )

    patient2 = crud.create_patient(db, schemas.PatientCreate(nhs_number="2345678901", sex="F", age_band="46-55"))
    observations_p2 = [
        {"type": "HbA1c", "value": 52, "unit": "mmol/mol", "interpretation": "ABNORMAL", "days_ago": 7},
        {"type": "Weight", "value": 72.0, "unit": "kg", "interpretation": "NORMAL", "days_ago": 7},
        {"type": "ECG", "value": 410, "unit": "ms", "interpretation": "NORMAL", "days_ago": 8},
        {"type": "FBC", "value": 5.8, "unit": "x10^9/L", "interpretation": "NORMAL", "days_ago": 14},
        {"type": "LFT", "value": 35, "unit": "U/L", "interpretation": "NORMAL", "days_ago": 14},
        {"type": "Weight", "value": 71.5, "unit": "kg", "interpretation": "NORMAL", "days_ago": 30},
        {"type": "HbA1c", "value": 48, "unit": "mmol/mol", "interpretation": "ABNORMAL", "days_ago": 60},
        {"type": "ECG", "value": 400, "unit": "ms", "interpretation": "NORMAL", "days_ago": 60},
        {"type": "FBC", "value": 6.2, "unit": "x10^9/L", "interpretation": "NORMAL", "days_ago": 90},
        {"type": "LFT", "value": 28, "unit": "U/L", "interpretation": "NORMAL", "days_ago": 90},
    ]
    for obs_data in observations_p2:
        crud.create_observation(
            db,
            schemas.ObservationCreate(
                patient_id=patient2.id,
                type=obs_data["type"],
                value=obs_data["value"],
                unit=obs_data["unit"],
                interpretation=obs_data["interpretation"],
                performed_date=datetime.utcnow() - timedelta(days=obs_data["days_ago"]),
            ),
        )
    crud.create_medication(
        db,
        schemas.MedicationCreate(
            patient_id=patient2.id,
            drug_name="Quetiapine",
            dose="200mg",
            start_date=datetime.utcnow() - timedelta(days=200),
            stop_date=None,
        ),
    )
    crud.create_medication(
        db,
        schemas.MedicationCreate(
            patient_id=patient2.id,
            drug_name="Atorvastatin",
            dose="20mg",
            start_date=datetime.utcnow() - timedelta(days=120),
            stop_date=None,
        ),
    )

    patient3 = crud.create_patient(db, schemas.PatientCreate(nhs_number="3456789012", sex="Other", age_band="36-45"))
    observations_p3 = [
        {"type": "HbA1c", "value": 38, "unit": "mmol/mol", "interpretation": "NORMAL", "days_ago": 5},
        {"type": "Weight", "value": 68.0, "unit": "kg", "interpretation": "NORMAL", "days_ago": 5},
        {"type": "ECG", "value": 390, "unit": "ms", "interpretation": "NORMAL", "days_ago": 6},
        {"type": "FBC", "value": 6.0, "unit": "x10^9/L", "interpretation": "NORMAL", "days_ago": 10},
        {"type": "LFT", "value": 22, "unit": "U/L", "interpretation": "NORMAL", "days_ago": 10},
        {"type": "Weight", "value": 67.5, "unit": "kg", "interpretation": "NORMAL", "days_ago": 30},
        {"type": "HbA1c", "value": 40, "unit": "mmol/mol", "interpretation": "NORMAL", "days_ago": 60},
        {"type": "ECG", "value": 395, "unit": "ms", "interpretation": "NORMAL", "days_ago": 60},
        {"type": "FBC", "value": 5.5, "unit": "x10^9/L", "interpretation": "NORMAL", "days_ago": 90},
        {"type": "LFT", "value": 25, "unit": "U/L", "interpretation": "NORMAL", "days_ago": 90},
    ]
    for obs_data in observations_p3:
        crud.create_observation(
            db,
            schemas.ObservationCreate(
                patient_id=patient3.id,
                type=obs_data["type"],
                value=obs_data["value"],
                unit=obs_data["unit"],
                interpretation=obs_data["interpretation"],
                performed_date=datetime.utcnow() - timedelta(days=obs_data["days_ago"]),
            ),
        )
    crud.create_medication(
        db,
        schemas.MedicationCreate(
            patient_id=patient3.id,
            drug_name="Risperidone",
            dose="4mg",
            start_date=datetime.utcnow() - timedelta(days=150),
            stop_date=None,
        ),
    )
    crud.create_medication(
        db,
        schemas.MedicationCreate(
            patient_id=patient3.id,
            drug_name="Simvastatin",
            dose="40mg",
            start_date=datetime.utcnow() - timedelta(days=100),
            stop_date=None,
        ),
    )

    print(f"Created {patient1.pseudonym}: {len(observations_p1)} observations, 2 medications")
    print(f"Created {patient2.pseudonym}: {len(observations_p2)} observations, 2 medications")
    print(f"Created {patient3.pseudonym}: {len(observations_p3)} observations, 2 medications")
    print("Database seeded successfully!")

    db.close()


if __name__ == "__main__":
    seed_database()
