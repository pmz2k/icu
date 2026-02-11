# NHS Mock EPR Streamlit Frontend

## Overview
This frontend is a clinician-facing Streamlit interface for a mock NHS-style Electronic Patient Record (EPR). It connects to the existing FastAPI backend and supports:

- Login via OAuth2 token flow
- Patient lookup by NHS number
- New patient registration
- Patient record view (demographics, medications, test results)
- Add observations/test results
- Prescribe medications
- Export pseudonymised CSV ZIP files
- Admin tools for simulation and system checks

## Architecture
- Backend: FastAPI service (deployed on Render)
- Frontend: Streamlit multipage app (`streamlit_app`)
- API integration: `app/api_client.py`
- Session and auth state: `app/session.py`

## Security
- NHS numbers are used only for lookup/registration requests and are never displayed in record views.
- Backend pseudonymises patient identity (`PAT-xxxxxx`) and frontend surfaces pseudonyms only.
- OAuth2 bearer token is attached to protected API calls.
- Session logout clears token/user context.
- Backend log redaction and hashed NHS identifiers remain enforced server-side.

## Setup Instructions

### Backend (Render)
1. Deploy backend service to Render.
2. Confirm health endpoint is available:
   - `https://<your-backend>/health`
3. Confirm Swagger docs:
   - `https://<your-backend>/docs`

### Frontend (Local Development)
1. Open terminal in `streamlit_app`.
2. Create and activate a virtual environment.
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Copy env template:
   - `copy .env.example .env` (Windows)
5. Set `API_BASE_URL` in `.env`.
6. Run app:
   - `streamlit run Home.py`

### Frontend (Streamlit Cloud)
1. Push repository to GitHub.
2. In Streamlit Cloud, create app from repo.
3. Set main file path to:
   - `streamlit_app/Home.py`
4. Add secret/environment variable:
   - `API_BASE_URL=https://your-backend.onrender.com`
5. Deploy and validate all pages.

## User Guide

### Login
- Open `1_🔐_Login` page.
- Sign in with clinician/admin credentials.

### Search Patients
- Open `2_🔍_Patient_Lookup`.
- Enter 10-digit NHS number and search.
- If not found, register new patient using sex and age band.

### View Patient Record
- Open `3_👤_Patient_Record`.
- Review demographics, medications, and test results in tabbed tables.

### Add Test Results
- Open `4_📊_Add_Test_Result`.
- Select test type, value, interpretation, and performed date.

### Prescribe Medication
- Open `5_💊_Prescribe_Medication`.
- Select common medication or custom drug, set dose/dates, and submit.

### Export Data
- Open `6_📥_Export_Data`.
- Export for selected patient or all patients.
- Download ZIP containing `patients.csv`, `medications.csv`, `events.csv`.

### Admin Tools
- Open `7_⚙️_Admin_Tools` (admin role only).
- Generate simulated events.
- Run API connectivity test.
- View session-level operational stats.

## Test Credentials
- Clinician: `clinician / password123`
- Admin: `admin / admin123`

## API Documentation
- Swagger UI: `https://<your-backend>/docs`
- ReDoc: `https://<your-backend>/redoc`

## Data Protection
- Frontend uses pseudonymous IDs for display and workflows.
- NHS numbers are not shown in patient summary or record pages.
- Exports include pseudonymous identifiers only.
- Sensitive identifiers remain protected by backend hashing/redaction controls.

