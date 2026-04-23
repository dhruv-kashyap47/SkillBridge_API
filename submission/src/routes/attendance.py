from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import dependencies, models, schemas

router = APIRouter(prefix="/attendance", tags=["attendance"])


def _get_session_or_404(db: Session, session_id: int) -> models.Session:
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


def _get_student_or_404(db: Session, student_id: int) -> models.User:
    student = (
        db.query(models.User)
        .filter(models.User.id == student_id, models.User.role == "student")
        .first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.post("/mark")
def mark_attendance(
    attendance: schemas.AttendanceMark,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.require_role(["student", "trainer"])),
):
    session = _get_session_or_404(db, attendance.session_id)
    student = _get_student_or_404(db, attendance.student_id)
    batch = db.query(models.Batch).filter(models.Batch.id == session.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    if current_user.role == "student" and current_user.id != student.id:
        raise HTTPException(status_code=403, detail="Students can only mark their own attendance")

    if current_user.role == "trainer":
        is_trainer = (
            db.query(models.BatchTrainer)
            .filter(
                models.BatchTrainer.batch_id == batch.id,
                models.BatchTrainer.trainer_id == current_user.id,
            )
            .first()
        )
        if not is_trainer:
            raise HTTPException(status_code=403, detail="Not a trainer for this batch")

    is_student = (
        db.query(models.BatchStudent)
        .filter(
            models.BatchStudent.batch_id == batch.id,
            models.BatchStudent.student_id == student.id,
        )
        .first()
    )
    if not is_student:
        raise HTTPException(status_code=403, detail="Student not in this batch")

    existing = (
        db.query(models.Attendance)
        .filter(
            models.Attendance.session_id == session.id,
            models.Attendance.student_id == student.id,
        )
        .first()
    )
    if existing:
        existing.status = attendance.status
        db.commit()
        db.refresh(existing)
        return existing

    record = models.Attendance(
        session_id=session.id,
        student_id=student.id,
        status=attendance.status,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
