import pytest
from fastapi.testclient import TestClient
from datetime import date, time

from src.main import app
from src import database, models


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    models.Base.metadata.drop_all(bind=database.engine)
    models.Base.metadata.create_all(bind=database.engine)
    yield
    models.Base.metadata.drop_all(bind=database.engine)


def create_user(name, email, password, role, institution_id=None):
    payload = {
        "name": name,
        "email": email,
        "password": password,
        "role": role,
    }
    if institution_id is not None:
        payload["institution_id"] = institution_id
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 200
    return response.json()


def login(email, password="pass"):
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_signup_and_login_works():
    create_user("Test Student", "student@test.com", "pass", "student")
    token = login("student@test.com")
    assert token


def test_trainer_creates_session():
    create_user("Institution 1", "inst@test.com", "pass", "institution", institution_id=1)
    trainer = create_user("Trainer 1", "trainer@test.com", "pass", "trainer")

    db = database.SessionLocal()
    batch = models.Batch(name="Batch A", institution_id=1)
    db.add(batch)
    db.commit()
    db.refresh(batch)
    batch_id = batch.id
    db.add(models.BatchTrainer(batch_id=batch.id, trainer_id=trainer["id"]))
    db.commit()
    db.close()

    token = login("trainer@test.com")
    response = client.post(
        "/sessions",
        json={
            "batch_id": batch_id,
            "title": "Intro Session",
            "date": "2026-04-22",
            "start_time": "10:00:00",
            "end_time": "12:00:00",
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Intro Session"


def test_student_marks_attendance():
    create_user("Institution 1", "inst@test.com", "pass", "institution", institution_id=1)
    trainer = create_user("Trainer 1", "trainer@test.com", "pass", "trainer")
    student = create_user("Student 1", "student@test.com", "pass", "student")

    db = database.SessionLocal()
    batch = models.Batch(name="Batch A", institution_id=1)
    db.add(batch)
    db.commit()
    db.refresh(batch)
    batch_id = batch.id
    db.add(models.BatchTrainer(batch_id=batch.id, trainer_id=trainer["id"]))
    db.add(models.BatchStudent(batch_id=batch.id, student_id=student["id"]))
    db.commit()

    session = models.Session(
        batch_id=batch.id,
        trainer_id=trainer["id"],
        title="Intro Session",
        date=date(2026, 4, 22),
        start_time=time(10, 0),
        end_time=time(12, 0),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    session_id = session.id
    db.close()

    token = login("student@test.com")
    response = client.post(
        "/attendance/mark",
        json={
            "session_id": session_id,
            "student_id": student["id"],
            "status": "present",
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "present"


def test_monitoring_endpoint_rejects_post():
    response = client.post("/monitoring/attendance")
    assert response.status_code == 405


def test_protected_route_without_token():
    response = client.get("/programme/summary")
    assert response.status_code == 401
