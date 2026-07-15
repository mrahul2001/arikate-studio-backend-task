# Artikate Studio Backend Developer Assessment

Backend Developer Technical Assessment completed using **Python**, **Django**, **PostgreSQL**, **Celery**, **Redis**, and **Docker**.

## Assessment Coverage

✔ Section 1 – Diagnose a Broken System

✔ Section 2 – Async Email Queue

✔ Section 3 – Multi-Tenant Data Isolation

✔ Section 4 – Written Design & Architecture Answers

---

# Tech Stack

- Python 3.11+
- Django 5.2.16
- Django REST Framework
- PostgreSQL
- Celery
- Redis (Docker)
- Docker
- django-silk
- unittest (Django TestCase)

---

# Project Structure

```
artikate_backend/
│
├── config/                 # Django project configuration
│
├── section1/               # Diagnose a Broken System
│
├── section2/               # Async Job Queue
│
├── section3/               # Multi-Tenant Data Isolation
│
├── ANSWERS.md
├── DESIGN.md
├── README.md
├── requirements.txt
└── manage.py
```

---

# Features

## Section 1 – Diagnose a Broken System

- Simulated N+1 Query Problem
- Optimized using:
  - `select_related()`
  - `prefetch_related()`
- django-silk profiling
- Incident Investigation Log
- Before/After performance comparison
- Automated tests

---

## Section 2 – Async Email Queue

- Celery background processing
- Redis Broker
- Redis-backed Fixed Window Rate Limiter
- Redis Lua Script for atomic operations
- Exponential Backoff Retry
- Dead Letter Queue
- Email Job Tracking
- Automated tests

---

## Section 3 – Multi-Tenant Data Isolation

- Automatic tenant scoping
- Custom Django Manager
- Thread-local tenant context
- Tenant middleware
- ORM-level tenant isolation
- Automated tests

---

# Installation

## 1. Clone the Repository

```bash
git clone <repository-url>
cd artikate-studio-backend-task

```

---

## 2. Install Dependencies & Configure Environment Variables

```bash
pip install -r requirements.txt
```

Copy the example environment file:

```bash
cp .env.example .env
```

Windows:

```powershell
copy .env.example .env
```

Update the database credentials if they differ from your local PostgreSQL installation.

---

## 3. PostgreSQL

Create a PostgreSQL database.

Example:

```
Database : artikate_db
User     : postgres
Password : <your_password>
Host     : localhost
Port     : 5432
```

Update the values in .env according to your local PostgreSQL configuration.

---

## 4. Start Redis (Docker)

Pull the Redis image (only once):

```bash
docker pull redis
```

Run Redis container:

For Windows, use:

```bash
docker run -d --name redis -p 6379:6379 redis
```

Linux/macOS:

```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis
```

Verify Redis is running:

```bash
docker ps
```

Expected output should contain:

```
redis
```

You can also verify connectivity:

```bash
docker exec -it redis redis-cli ping
```

Expected:

```
PONG
```

---

## 5. Apply Migrations

```bash
python manage.py migrate
```

---

## 6. Seed Sample Data (Section 1)

```bash
python manage.py seed_data
```

---

## 7. Start Django Server

```bash
python manage.py runserver
```

Application:

```
http://127.0.0.1:8000/
```

---

## 8. Start Celery Worker

Open another terminal.

```bash
celery -A config worker -l info
```
Ensure the Redis container is running before starting the Celery worker.

---

# API Endpoints

## Section 1

### Order Summary

```
GET /api/orders/summary/
```

```
GET /api/orders/summary_optimized/
```

<img width="1920" height="1035" alt="Screenshot (292)" src="https://github.com/user-attachments/assets/eb0f2dba-e6f2-445e-b443-4482d354069b" />


---

## Section 2

### Queue Email

```
POST /api/email/
```

Example Request

```json
{
    "recipient": "user@test.com",
    "subject": "Hello",
    "body": "Testing Email"
}
```

---

## Section 3

### Tenant Orders

```
GET /api/tenant/orders/
```

Required Header

```
X-Tenant: TenantA
```

---

# Silk Profiler

Silk is enabled for profiling Section 1.

Access:

```
http://127.0.0.1:8000/silk/
```
Silk is available after starting the Django server. Log in using the Django admin account if authentication is enabled.

The profiler demonstrates the reduction in SQL queries before and after applying `select_related()` and `prefetch_related()`.

---

# Running Tests

Run all tests:

```bash
python manage.py test --settings=config.test_settings
```

Run individual sections:

```bash
python manage.py test --settings=config.test_settings section1

python manage.py test --settings=config.test_settings section2

python manage.py test --settings=config.test_settings section3
```

---

# Documentation

The repository contains:

- **README.md** – Setup and execution instructions
- **DESIGN.md** – Architecture decisions for Section 2
- **ANSWERS.md** – Written answers for all required sections

---

# Design Highlights

## Section 1

- Root cause identified as an N+1 Query problem
- ORM optimization using `select_related()` and `prefetch_related()`
- Query count verified using django-silk

---

## Section 2

- Celery + Redis architecture
- Redis running inside Docker
- Fixed Window Rate Limiter implemented using Redis Lua scripting
- Atomic Redis operations
- Exponential retry strategy
- Dead Letter Queue
- Worker crash recovery using:
  - `CELERY_TASK_ACKS_LATE=True`
  - `CELERY_TASK_REJECT_ON_WORKER_LOST=True`

---

## Section 3

- Automatic tenant isolation using a custom `TenantManager`
- Tenant context maintained using thread-local storage
- Middleware-based tenant resolution
- ORM automatically scopes all queries to the current tenant

---

# Assumptions

- PostgreSQL is running locally.
- Redis is running inside a Docker container.
- Tenant identification is performed using the `X-Tenant` request header for simplicity.
- Email delivery is mocked for demonstration and testing purposes.

---

# Notes

This project was developed as part of the **Artikate Studio Backend Developer Assessment**.

While developed as part of a technical assessment, the project follows production-oriented engineering practices including ORM optimization, asynchronous background processing, automated testing, secure configuration management using environment variables, and multi-tenant data isolation.
