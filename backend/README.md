# NHS Mock EPR Backend

FastAPI backend for a mock NHS-style Electronic Patient Record workflow, including:
- NHS number hashing with secret salt
- Mock OAuth2 authentication
- Patient, observation, medication APIs
- CSV export to ZIP
- Seed data generator

## Setup

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
```

Set `SECRET_SALT` in `.env`, then:

```bash
python -m app.seed
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Docs:
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
