# Section 1

## Incident Investigation Log

### Step 1

Reproduced the issue using a user with more than 200 orders.

Observation:
The endpoint latency increased significantly with dataset size.

Reason:
To verify whether the issue scaled with the amount of data.

---

### Step 2

Enabled django-silk profiling.

Reason:
To determine whether the bottleneck originated from database queries, serialization, or application logic.

---

### Step 3

Observed the SQL profile.

Finding:
More than 2000 SQL queries were executed for a single request.

The profiler showed repeated SELECT statements for Customer, OrderItem, and Product tables.

---

### Step 4

Reviewed the serializer implementation.

Found repeated access to:

- order.customer
- order.items.all()
- item.product

inside iteration.

---

### Step 5

Hypothesis

The ORM was lazily loading related objects, resulting in an N+1 query problem.

---

### Step 6

Applied select_related() for the Customer relationship and prefetch_related() for OrderItem and Product.

---

### Step 7

Re-profiled the endpoint.

Query count reduced from approximately 2000+ queries to 3 queries.

Request latency decreased substantially.

Issue resolved.

## Root Cause

The regression was caused by an N+1 query problem.

Order.objects.all() only retrieves Order objects.

Whenever the serializer accessed order.customer, Django lazily executed another SQL query because the related Customer object had not been loaded.

Similarly, order.items.all() generated another query per order, and item.product generated additional queries per order item.

As the number of orders increased, the number of SQL queries increased linearly (and, with nested relationships, effectively multiplicatively), causing the endpoint to spend most of its execution time waiting on the database.

The fix used select_related("customer"), which performs an SQL JOIN and loads Customer objects in the same query as Order.

For reverse ForeignKey relationships, prefetch_related("items__product") performs separate bulk queries and constructs the relationships in memory, eliminating additional SQL execution during serialization.

This reduced the total query count from thousands of queries to a constant number of queries independent of dataset size.


# Section 2

## Why Celery?

Celery provides reliable background processing, retry support, Redis integration, and worker scalability. Compared to implementing a custom queue, it reduces engineering effort while providing production-grade task execution.

---

## Why Fixed Window instead of Token Bucket?

The assignment allows Token Bucket, Sliding Window, or Fixed Window.

I selected Fixed Window because it is straightforward to implement, has low memory overhead, and satisfies the requirement of enforcing a limit of 200 emails per minute.

Although Token Bucket provides smoother traffic shaping, Fixed Window was sufficient for the required throughput while keeping the implementation simpler.

---

## What happens if the worker receives SIGKILL?

The worker acknowledges tasks only after successful completion because `acks_late=True` is enabled.

If a worker crashes before acknowledging the task, Redis still considers the task unacknowledged. With `CELERY_TASK_REJECT_ON_WORKER_LOST=True`, Celery requeues the task so another worker can execute it.

This prevents in-flight tasks from being lost.


# Section 3

## Why use a custom Manager?

The custom TenantManager automatically scopes every queryset to the current tenant. This prevents developers from accidentally exposing data by forgetting to call `.filter(tenant=...)`.

For example, calling `Order.objects.all()` automatically applies the tenant filter, ensuring only records belonging to the current tenant are returned.

---

## Middleware

TenantMiddleware extracts the tenant from the `X-Tenant` request header and stores it in thread-local storage for the lifetime of the request.

After the response is returned, the middleware clears the tenant context to prevent leakage into subsequent requests handled by the same worker thread.

---

## Failure modes of thread-local storage

Thread-local storage works correctly for synchronous Django views because each request is processed on its own thread.

However, in asynchronous Django views multiple coroutines can execute on the same thread. Since thread-local variables are shared by every coroutine running on that thread, tenant information may leak between concurrent requests.

This could result in one request reading another tenant's context, violating tenant isolation.

---

## Async-safe solution

For asynchronous Django applications I would replace `threading.local()` with Python's `contextvars.ContextVar`.

Unlike thread-local storage, ContextVar maintains values per asynchronous execution context rather than per thread.

Each coroutine receives its own isolated tenant context, preventing data leakage between concurrent async requests while preserving automatic ORM scoping.

Therefore ContextVar is the recommended approach for modern asynchronous Django applications.