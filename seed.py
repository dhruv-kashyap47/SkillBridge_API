from datetime import date, time

from src import auth, database, models


def seed():
    db = database.SessionLocal()

    models.Base.metadata.drop_all(bind=database.engine)
    models.Base.metadata.create_all(bind=database.engine)

    institutions = [
        models.User(
            name="Institution One",
            email="inst1@test.com",
            hashed_password=auth.get_password_hash("pass"),
            role="institution",
            institution_id=1,
        ),
        models.User(
            name="Institution Two",
            email="inst2@test.com",
            hashed_password=auth.get_password_hash("pass"),
            role="institution",
            institution_id=2,
        ),
    ]
    programme_manager = models.User(
        name="Programme Manager",
        email="pm@test.com",
        hashed_password=auth.get_password_hash("pass"),
        role="programme_manager",
    )
    monitoring_officer = models.User(
        name="Monitoring Officer",
        email="monitor@test.com",
        hashed_password=auth.get_password_hash("pass"),
        role="monitoring_officer",
    )

    trainers = [
        models.User(name=f"Trainer {i}", email=f"trainer{i}@test.com", hashed_password=auth.get_password_hash("pass"), role="trainer")
        for i in range(1, 5)
    ]
    students = [
        models.User(name=f"Student {i}", email=f"student{i}@test.com", hashed_password=auth.get_password_hash("pass"), role="student")
        for i in range(1, 16)
    ]

    db.add_all(institutions + [programme_manager, monitoring_officer] + trainers + students)
    db.commit()

    batches = [
        models.Batch(name="Batch 1", institution_id=1),
        models.Batch(name="Batch 2", institution_id=1),
        models.Batch(name="Batch 3", institution_id=2),
    ]
    db.add_all(batches)
    db.commit()

    sessions = []
    batch_links = [
        (batches[0].id, trainers[0].id),
        (batches[1].id, trainers[1].id),
        (batches[2].id, trainers[2].id),
    ]
    for batch_id, trainer_id in batch_links:
        db.add(models.BatchTrainer(batch_id=batch_id, trainer_id=trainer_id))

    student_links = [
        (batches[0].id, students[0].id),
        (batches[0].id, students[1].id),
        (batches[0].id, students[2].id),
        (batches[0].id, students[3].id),
        (batches[0].id, students[4].id),
        (batches[1].id, students[5].id),
        (batches[1].id, students[6].id),
        (batches[1].id, students[7].id),
        (batches[1].id, students[8].id),
        (batches[1].id, students[9].id),
        (batches[2].id, students[10].id),
        (batches[2].id, students[11].id),
        (batches[2].id, students[12].id),
        (batches[2].id, students[13].id),
        (batches[2].id, students[14].id),
    ]
    for batch_id, student_id in student_links:
        db.add(models.BatchStudent(batch_id=batch_id, student_id=student_id))

    db.commit()

    for index in range(8):
        batch = batches[index % 3]
        trainer_id = batch_links[index % 3][1]
        session = models.Session(
            batch_id=batch.id,
            trainer_id=trainer_id,
            title=f"Session {index + 1}",
            date=date.today(),
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        db.add(session)
        sessions.append(session)

    db.commit()

    db.add(models.Attendance(session_id=sessions[0].id, student_id=students[0].id, status="present"))
    db.add(models.Attendance(session_id=sessions[0].id, student_id=students[1].id, status="absent"))
    db.add(models.Attendance(session_id=sessions[1].id, student_id=students[5].id, status="present"))
    db.commit()

    db.close()
    print("Database seeded successfully.")


if __name__ == "__main__":
    seed()
