# Setup Guide

This guide covers the minimal steps needed to run the backend and frontend locally.

## Prerequisites
- Python 3.9+
- Node.js 16+
- npm

> For Python 3.13 compatibility, the backend uses pinned Pydantic packages: `pydantic==2.13.4` and `pydantic-core==2.46.4`.

## Backend
1. Create a Python virtual environment:

```bash
cd backend
python -m venv venv
source venv/bin/activate
```

2. Install Python dependencies:

```bash
pip install -r ../requirements.txt
```

3. (Optional) Install development and ML dependencies:

```bash
pip install -r ../requirements-dev.txt
pip install -r ../requirements-ml.txt
```

3. Create the database and tables:

```bash
python init_db.py
```

5. Install development dependencies for testing:

```bash
pip install -r ../requirements-dev.txt
```

6. Start the backend server:

```bash
uvicorn main:app --reload --port 8000
```

The backend API will be available at `http://localhost:8000`.

## Frontend
1. Install frontend dependencies:

```bash
cd frontend
npm install
```

2. Start the React app:

```bash
REACT_APP_API_BASE=http://localhost:8000/api npm start
```

The frontend will start on `http://localhost:3000`.

## Notes
- The frontend is configured to connect to `http://localhost:8000/api` by default.
- If you want to use a different backend port, set `REACT_APP_API_BASE` before starting the frontend.
- A sample environment file is available at `.env.example`.
- If running tests, use `requirements-dev.txt` so `httpx==0.27.2` is installed for the FastAPI test client.
