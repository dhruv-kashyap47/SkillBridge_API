# SkillBridge – Attendance Management System API

Backend API for a role-based attendance system built with FastAPI.
Designed and deployed as part of a Python Developer Intern assignment.

---

## 🌐 Live API

Base URL:
[https://skillbridge-api-sm18.onrender.com](https://skillbridge-api-sm18.onrender.com)

Swagger Docs:
[https://skillbridge-api-sm18.onrender.com/docs](https://skillbridge-api-sm18.onrender.com/docs)

---

## 🧠 Overview

A multi-role system with strict server-side access control.

### Roles

* Student → marks attendance
* Trainer → creates sessions, manages batches
* Institution → views batch summaries
* Programme Manager → views cross-institution summaries
* Monitoring Officer → read-only access with scoped token

---

## ⚙️ Tech Stack

* FastAPI
* PostgreSQL (Neon)
* JWT (python-jose)
* Render (deployment)
* Pytest

---

## 🔐 Authentication

### Standard JWT

Issued via `/auth/login`

Payload:
{
"user_id": 1,
"role": "student",
"iat": 1710000000,
"exp": 1710086400
}

* Valid for 24 hours
* Required for all protected endpoints

---

### Monitoring Officer Token

POST /auth/monitoring-token

Requires:

* Valid login JWT
* API key from `.env`

Returns:

* 1-hour scoped token
* Valid only for `/monitoring/*`

---

## 👥 Test Accounts

Student:
email: [student1@test.com](mailto:student1@test.com)
password: 123456

Trainer:
email: [trainer1@test.com](mailto:trainer1@test.com)
password: 123456

Institution:
email: [institution@test.com](mailto:institution@test.com)
password: 123456

Programme Manager:
email: [manager@test.com](mailto:manager@test.com)
password: 123456

Monitoring Officer:
email: [monitor@test.com](mailto:monitor@test.com)
password: 123456

---

## 🚀 Local Setup

```
git clone https://github.com/dhruv-kashyap47/SkillBridge_API.git
cd SkillBridge_API

pip install -r requirements.txt
uvicorn src.main:app --reload
```

---

## 🔑 Environment Variables

DATABASE_URL=your_neon_db_url
SECRET_KEY=your_secret_key
ALLOWED_ORIGINS=[http://localhost:3000](http://localhost:3000)
MONITORING_API_KEY=your_api_key

---

## 📡 API Examples

### Login

curl -X POST [https://skillbridge-api-sm18.onrender.com/auth/login](https://skillbridge-api-sm18.onrender.com/auth/login) 
-H "Content-Type: application/json" 
-d '{"email":"[student1@test.com](mailto:student1@test.com)","password":"123456"}'

---

### Create Session (Trainer)

curl -X POST [https://skillbridge-api-sm18.onrender.com/sessions](https://skillbridge-api-sm18.onrender.com/sessions) 
-H "Authorization: Bearer YOUR_TOKEN" 
-H "Content-Type: application/json" 
-d '{"title":"Session 1","date":"2026-04-23","start_time":"10:00","end_time":"12:00","batch_id":1}'

---

### Mark Attendance (Student)

curl -X POST [https://skillbridge-api-sm18.onrender.com/attendance/mark](https://skillbridge-api-sm18.onrender.com/attendance/mark) 
-H "Authorization: Bearer YOUR_TOKEN" 
-H "Content-Type: application/json" 
-d '{"session_id":1,"status":"present"}'

---

### Monitoring Access

curl -X GET [https://skillbridge-api-sm18.onrender.com/monitoring/attendance](https://skillbridge-api-sm18.onrender.com/monitoring/attendance) 
-H "Authorization: Bearer MONITORING_TOKEN"

---

## 🧱 Design Decisions

* batch_trainers (M:N) → supports multiple trainers per batch
* batch_invites → token-based joining with expiry + single use
* Dual-token system → limits Monitoring Officer access scope

---

## ✅ What’s Working

* JWT authentication
* Role-based access control
* All core endpoints
* Monitoring token flow
* Live deployment
* Seeded data
* Swagger docs

---

## ⚠️ Limitations

* No refresh tokens
* Limited edge-case validation
* No rate limiting
* Minimal frontend

---

## 🔍 Tests

```
pytest
```

Covers:

* signup/login
* session creation
* attendance marking
* monitoring endpoint restriction
* unauthorized access

---

## 🔐 Security Notes

Current limitation:

* Tokens are not revocable

Improvement:

* Token blacklist / Redis
* Refresh tokens
* Rate limiting

---

## 🧠 Future Improvements

* Token lifecycle management
* Better validation
* Caching summaries
* UI improvements
* CI/CD

---

## 👨‍💻 Author

Dhruv Kashyap
[https://github.com/dhruv-kashyap47](https://github.com/dhruv-kashyap47)

---

## requirements.txt

fastapi
uvicorn
sqlalchemy
psycopg2-binary
python-jose
passlib[bcrypt]
python-dotenv
pytest

---

## .env.example

DATABASE_URL=
SECRET_KEY=
ALLOWED_ORIGINS=
MONITORING_API_KEY=
