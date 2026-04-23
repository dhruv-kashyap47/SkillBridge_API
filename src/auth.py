import os
from datetime import datetime, timedelta, timezone
from jose import jwt
import bcrypt

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()


def _env_or_dev_default(name: str, default: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    if ENVIRONMENT in {"production", "staging"}:
        raise RuntimeError(f"{name} must be set when ENVIRONMENT={ENVIRONMENT}")
    return default


SECRET_KEY = _env_or_dev_default("SECRET_KEY", "dev-only-change-me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
MONITORING_API_KEY = _env_or_dev_default("MONITORING_API_KEY", "dev-only-monitoring-key")
ACCESS_TOKEN_EXPIRE_HOURS = 24
MONITORING_TOKEN_EXPIRE_HOURS = 1

def verify_password(plain_password, hashed_password):
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except ValueError:
        return False

def get_password_hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_monitoring_token():
    expire = datetime.now(timezone.utc) + timedelta(hours=MONITORING_TOKEN_EXPIRE_HOURS)
    to_encode = {"role": "monitoring_officer_special", "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
