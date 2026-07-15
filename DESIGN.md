# Section 2 – Async Email Queue Design

## Overview

The goal of this system is to process email requests asynchronously while enforcing a provider rate limit of **200 emails per minute**, supporting automatic retries, handling worker failures safely, and preventing permanent task loss.

The architecture separates the HTTP request lifecycle from email processing by using Celery workers and Redis as a message broker. This allows the API to respond immediately while background workers perform the actual email delivery.

---

# Architecture

The solution consists of the following components:

- **Django REST Framework** – Exposes the API endpoint for queuing email requests.
- **PostgreSQL** – Persists email job metadata and status.
- **Celery** – Executes email delivery asynchronously.
- **Redis** – Serves as the Celery message broker and also stores the rate limiter state.
- **Lua Script** – Executes Redis operations atomically for safe rate limiting under concurrent workers.
- **Celery Workers** – Consume queued jobs, enforce rate limits, retry failures, and update job status.

---

# Request Flow

```text
                    Client
                       │
                       │ POST /api/email/
                       ▼
              Django REST API
                       │
                       │ Validate Request
                       ▼
               EmailJob Created
                 (PostgreSQL)
                       │
                       │ send_email_task.delay(job_id)
                       ▼
              Redis Message Broker
                       │
                       ▼
               Celery Worker
                       │
                       ▼
           Redis Rate Limiter (Lua)
                │            │
         Token Available?    No
            │                │
            ▼                ▼
     EmailService.send()   Retry Later
            │
     ┌──────┴────────┐
     │               │
 Success          Exception
     │               │
     ▼               ▼
Update Status    Exponential Retry
(SUCCESS)             │
                      ▼
             Max Retries Reached?
                │            │
               No           Yes
                │            │
                ▼            ▼
             Retry      Dead Letter Queue
```

---

# Processing Flow

1. The client submits an email request to the API.
2. Django validates the request and stores an `EmailJob` record in PostgreSQL.
3. Instead of sending the email immediately, the API enqueues a Celery task using `send_email_task.delay(job_id)`.
4. The HTTP request returns immediately with a **202 Accepted** response.
5. A Celery worker retrieves the task from Redis.
6. Before sending the email, the worker checks the Redis-based rate limiter.
7. If capacity is available, the email is sent.
8. If the provider fails, Celery retries the task using exponential backoff.
9. After exceeding the retry limit, the job is marked as **DEAD** for later inspection.

---

# Why PostgreSQL?

Email jobs are stored in PostgreSQL because task metadata should survive application restarts and worker failures.

The database stores:

- Recipient
- Subject
- Body
- Current Status
- Retry Count
- Creation Timestamp

Persisting this information enables monitoring, auditing, and recovery without relying solely on the message broker.

---

# Why Redis?

Redis serves two independent purposes:

### 1. Celery Broker

Redis stores queued tasks until a worker is available.

Advantages:

- Very low latency
- High throughput
- Native Celery integration
- Lightweight deployment

### 2. Rate Limiter

Redis maintains the remaining request count for the current time window.

Using Redis allows all Celery workers to share the same global rate limit, ensuring that the provider's limit is respected even when multiple workers process tasks concurrently.

---

# Why Asynchronous Processing?

Sending emails synchronously would block the HTTP request until the provider responds.

Instead:

```text
Client
   │
POST /api/email/
   │
   ▼
API validates request
   │
Creates EmailJob
   │
Queues Celery Task
   │
Returns HTTP 202
```

The client receives an immediate response while the email is processed independently in the background.

Benefits:

- Faster API responses
- Better user experience
- Improved scalability
- Isolation from temporary provider failures

---

# Design Goals

The implementation was designed to achieve the following:

- Non-blocking request handling
- Reliable background processing
- Shared global rate limiting
- Automatic retry with exponential backoff
- Protection against task loss during worker failures
- Persistent job tracking
- Simple and maintainable architecture