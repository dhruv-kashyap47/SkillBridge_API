from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import auth, dependencies, models, schemas

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    if user.role == "institution" and user.institution_id is None:
        raise HTTPException(status_code=422, detail="Institution users must include institution_id")

    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        institution_id=user.institution_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(dependencies.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user or not auth.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = auth.create_access_token(
        data={
            "user_id": user.id,
            "role": user.role,
            "institution_id": user.institution_id,
        }
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "institution_id": user.institution_id,
    }


@router.post("/monitoring-token")
def get_monitoring_token(
    request: schemas.MonitoringTokenRequest,
    current_user: models.User = Depends(dependencies.require_role(["monitoring_officer"])),
):
    if request.api_key != auth.MONITORING_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    token = auth.create_monitoring_token()
    return {"monitoring_token": token, "token_type": "bearer"}
