from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, dependencies

router = APIRouter(tags=["monitoring"])

@router.get("/monitoring/attendance")
def get_monitoring_attendance(
    db: Session = Depends(dependencies.get_db),
    monitoring_token_payload: dict = Depends(dependencies.get_monitoring_token)
):
    # This specifically uses get_monitoring_token, which restricts to the special token.
    records = db.query(models.Attendance).all()
    return records

@router.get("/institutions/{id}/summary")
def get_institution_summary(
    id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.require_role(["institution", "programme_manager"]))
):
    if current_user.role == "institution" and current_user.institution_id != id:
        raise HTTPException(status_code=403, detail="Can only view your own institution")
    institution = db.query(models.User).filter(
        models.User.role == "institution",
        models.User.institution_id == id
    ).first()
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
        
    batches_count = db.query(models.Batch).filter(models.Batch.institution_id == id).count()
    return {"institution_id": id, "total_batches": batches_count}

@router.get("/institutions")
def list_institutions(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.require_role(["programme_manager"]))
):
    institutions = db.query(models.User).filter(models.User.role == "institution").all()
    seen = set()
    unique_institutions = []
    for institution in institutions:
        key = institution.institution_id
        if key in seen:
            continue
        seen.add(key)
        unique_institutions.append(institution)
    return [
        {
            "id": institution.id,
            "name": institution.name,
            "email": institution.email,
            "institution_id": institution.institution_id
        }
        for institution in unique_institutions
    ]

@router.get("/programme/summary")
def get_programme_summary(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.require_role(["programme_manager"]))
):
    institutions = db.query(models.User).filter(models.User.role == "institution").count()
    total_students = db.query(models.User).filter(models.User.role == "student").count()
    total_batches = db.query(models.Batch).count()
    
    return {
        "total_institutions": institutions,
        "total_students": total_students,
        "total_batches": total_batches
    }
