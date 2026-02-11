import csv
import os
import zipfile
from typing import Optional

from sqlalchemy.orm import Session

from app import crud


EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)


def generate_csv_export(db: Session, job_id: str, patient_id: Optional[str] = None) -> str:
    """Generate CSV export files and return ZIP path."""
    if patient_id:
        patient = crud.get_patient_by_id(db, patient_id)
        patients = [patient] if patient else []
    else:
        patients = crud.get_all_patients(db)

    patients_csv = os.path.join(EXPORT_DIR, f"{job_id}_patients.csv")
    medications_csv = os.path.join(EXPORT_DIR, f"{job_id}_medications.csv")
    events_csv = os.path.join(EXPORT_DIR, f"{job_id}_events.csv")
    zip_path = os.path.join(EXPORT_DIR, f"{job_id}.zip")

    with open(patients_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["pseudonymous_number", "age_band", "sex"])
        for patient in patients:
            writer.writerow([patient.pseudonym, patient.age_band, patient.sex])

    with open(medications_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["pseudonymous_number", "drug_name", "start_date", "stop_date", "dose"])
        for patient in patients:
            for med in crud.get_medications(db, patient.id):
                writer.writerow([
                    patient.pseudonym,
                    med.drug_name,
                    med.start_date.strftime("%Y-%m-%d"),
                    med.stop_date.strftime("%Y-%m-%d") if med.stop_date else "",
                    med.dose,
                ])

    with open(events_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["pseudonymous_number", "test_type", "performed_date", "value", "unit", "interpretation"])
        for patient in patients:
            for obs in crud.get_observations(db, patient.id):
                writer.writerow([
                    patient.pseudonym,
                    obs.type,
                    obs.performed_date.strftime("%Y-%m-%d"),
                    obs.value,
                    obs.unit,
                    obs.interpretation,
                ])

    with zipfile.ZipFile(zip_path, "w") as zipf:
        zipf.write(patients_csv, "patients.csv")
        zipf.write(medications_csv, "medications.csv")
        zipf.write(events_csv, "events.csv")

    os.remove(patients_csv)
    os.remove(medications_csv)
    os.remove(events_csv)

    return zip_path
