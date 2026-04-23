from datetime import datetime, timedelta, timezone
import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import dependencies, models, schemas

router = APIRouter(prefix="/batches", tags=["batches"])


def _get_batch_or_404(db: Session, batch_id: int) -> models.Batch:
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


def _get_institution_or_404(db: Session, institution_id: int) -> models.User:
    institution = (
        db.query(models.User)
        .filter(models.User.role == "institution", models.User.institution_id == institution_id)
        .first()
    )
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    return institution


def _require_batch_access(db: Session, current_user: models.User, batch: models.Batch) -> None:
    if current_user.role == "programme_manager":
        return
    if current_user.role == "institution":
        if current_user.institution_id != batch.institution_id:
            raise HTTPException(status_code=403, detail="Can only access your own institution batches")
        return
    if current_user.role == "trainer":
        is_linked = (
            db.query(models.BatchTrainer)
            .filter(
                models.BatchTrainer.batch_id == batch.id,
                models.BatchTrainer.trainer_id == current_user.id,
            )
            .first()
        )
        if not is_linked:
            raise HTTPException(status_code=403, detail="Not linked to this batch")
        return
    raise HTTPException(status_code=403, detail="Operation not permitted")


@router.post("/")
def create_batch(
    batch: schemas.BatchCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.require_role(["institution", "programme_manager"])),
):
    _get_institution_or_404(db, batch.institution_id)

    if current_user.role == "institution" and current_user.institution_id != batch.institution_id:
        raise HTTPException(status_code=403, detail="Can only create batches for your own institution")

    new_batch = models.Batch(name=batch.name, institution_id=batch.institution_id)
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    return new_batch


@router.post("/{id}/invite")
def create_invite(
    id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.require_role(["institution", "trainer", "programme_manager"])),
):
    batch = _get_batch_or_404(db, id)
    _require_batch_access(db, current_user, batch)

    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(days=7)

    invite = models.BatchInvite(
        batch_id=id,
        token=token,
        created_by=current_user.id,
        expires_at=expires,
    )
    db.add(invite)
    db.commit()
    return {"invite_token": token, "expires_at": expires}


@router.post("/join")
def join_batch(
    req: schemas.JoinBatchRequest,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.require_role(["student", "trainer"])),
):
    invite = db.query(models.BatchInvite).filter(models.BatchInvite.token == req.token).first()
    if not invite:
        raise HTTPException(status_code=404, detail="Invalid invite token")
    if invite.used:
        raise HTTPException(status_code=400, detail="Invite already used")
    if invite.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invite token expired")

    batch = _get_batch_or_404(db, invite.batch_id)

    if current_user.role == "student":
        link = models.BatchStudent(batch_id=batch.id, student_id=current_user.id)
    else:
        link = models.BatchTrainer(batch_id=batch.id, trainer_id=current_user.id)

    try:
        db.add(link)
        invite.used = True
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="User already in batch")

    return {"message": "Successfully joined batch", "batch_id": batch.id}


@router.get("/{id}/summary")
def get_batch_summary(
    id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.require_role(["institution", "trainer", "programme_manager"])),
):
    batch = _get_batch_or_404(db, id)
    _require_batch_access(db, current_user, batch)

    students = db.query(models.BatchStudent).filter(models.BatchStudent.batch_id == id).count()
    trainers = db.query(models.BatchTrainer).filter(models.BatchTrainer.batch_id == id).count()
    sessions = db.query(models.Session).filter(models.Session.batch_id == id).count()

    return {
        "id": batch.id,
        "name": batch.name,
        "students_count": students,
        "trainers_count": trainers,
        "sessions_count": sessions,
    }
