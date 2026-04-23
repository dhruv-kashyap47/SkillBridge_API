# SkillBridge

SkillBridge is a FastAPI attendance management API with a simple web UI.

## What is included

- User signup and login
- Batch, session, and attendance management
- Monitoring endpoint
- Basic frontend in `frontend/`

## Run from the command line

1. Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables:

- Copy `.env.example` to `.env`
- Update `DATABASE_URL`, `SECRET_KEY`, and `MONITORING_API_KEY`

If `DATABASE_URL` is not set, the app uses a local SQLite database file.

3. Start the API:

```bash
uvicorn src.main:app --reload
```

4. Run the tests:

```bash
pytest
```

5. Open the UI:

- Visit `http://127.0.0.1:8000/app`
