from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, Literal
from datetime import date, time, datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Literal["student", "trainer", "institution", "programme_manager", "monitoring_officer"]
    institution_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class MonitoringTokenRequest(BaseModel):
    token: Optional[str] = None
    api_key: str

class BatchCreate(BaseModel):
    name: str
    institution_id: int

class SessionCreate(BaseModel):
    batch_id: int
    title: str
    date: date
    start_time: time
    end_time: time

class AttendanceMark(BaseModel):
    session_id: int
    student_id: int
    status: str

class JoinBatchRequest(BaseModel):
    token: str
