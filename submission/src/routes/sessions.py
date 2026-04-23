from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import dependencies, models, schemas

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _get_batch_or_404(db: Session, batch_id: int) -> models.Batch:
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


@router.post("/")
def create_session(
    session: schemas.SessionCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.require_role(["trainer"])),
):
    batch = _get_batch_or_404(db, session.batch_id)

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

    new_session = models.Session(
        batch_id=session.batch_id,
        trainer_id=current_user.id,
        title=session.title,
        date=session.date,
        start_time=session.start_time,
        end_time=session.end_time,
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


@router.get("/{id}/attendance")
def get_session_attendance(
    id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.require_role(["trainer", "institution", "programme_manager"])),
):
    session = db.query(models.Session).filter(models.Session.id == id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    batch = _get_batch_or_404(db, session.batch_id)
    if current_user.role == "trainer" and session.trainer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to view this session")
    if current_user.role == "institution" and current_user.institution_id != batch.institution_id:
        raise HTTPException(status_code=403, detail="Can only view your own institution sessions")

    return db.query(models.Attendance).filter(models.Attendance.session_id == id).all()
