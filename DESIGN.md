# Section 2 – Async Email Queue Design

## Architecture

The queue is implemented using:

- Django REST Framework
- Celery
- Redis
- PostgreSQL

Flow:

Client
    │
    ▼
Django API
    │
    ▼
PostgreSQL (EmailJob)
    │
    ▼
Celery Queue (Redis Broker)
    │
    ▼
Celery Worker
    │
    ▼
Redis Rate Limiter
    │
    ▼
Email Provider