# Artikate Studio Backend Developer Assessment

Backend Developer Technical Assessment completed using **Python**, **Django**, **PostgreSQL**, **Celery**, and **Redis**.

---

## Tech Stack

- Python 3.11+
- Django 5.x
- Django REST Framework
- PostgreSQL
- Celery
- Redis
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
cd artikate_backend
```

---

## 2. Create Virtual Environment

Windows

```bash
python -m venv venv

venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. PostgreSQL

Create a PostgreSQL database.

Example:

```
Database : artikate_db
User     : postgres
Password : postgres
Host     : localhost
Port     : 5432
```

Update `config/settings.py` if required.

---

## 5. Redis

Start Redis.

Linux/macOS

```bash
redis-server
```

Windows (Redis service)

```bash
redis-server
```

Verify:

```bash
redis-cli ping
```

Expected output:

```
PONG
```

---

## 6. Apply Migrations

```bash
python manage.py migrate
```

---

## 7. Seed Sample Data (Section 1)

```bash
python manage.py seed_data
```

---

## 8. Start Django

```bash
python manage.py runserver
```

Application:

```
http://127.0.0.1:8000/
```

---

## 9. Start Celery Worker

Open another terminal.

```bash
celery -A config worker -l info
```

---

# API Endpoints

## Section 1

### Order Summary

```
GET /api/orders/summary/
```

---

## Section 2

### Queue Email

```
POST /api/email/
```

Example

```json
{
    "recipient":"user@test.com",
    "subject":"Hello",
    "body":"Testing Email"
}
```

---

## Section 3

### Tenant Orders

```
GET /api/tenant/orders/
```

Header

```
X-Tenant: TenantA
```

---

# Silk Profiler

Silk is enabled for profiling Section 1.

Open:

```
http://127.0.0.1:8000/silk/
```

The profiler demonstrates the reduction in SQL queries before and after applying `select_related()` and `prefetch_related()`.

---

# Running Tests

Run all tests:

```bash
python manage.py test
```

Run individual sections:

```bash
python manage.py test section1

python manage.py test section2

python manage.py test section3
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
- Query count verified with django-silk

---

## Section 2

- Celery + Redis architecture
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

- PostgreSQL and Redis are running locally.
- Tenant identification is performed using the `X-Tenant` request header for simplicity.
- Email delivery is mocked for demonstration and testing purposes.

---

# Notes

This project was developed as part of the **Artikate Studio Backend Developer Assessment**. The focus is on clean architecture, correctness, systems thinking, ORM optimization, reliable background processing, and automated testing rather than production deployment.