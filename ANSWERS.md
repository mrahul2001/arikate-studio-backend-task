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


# Section 4

## Question A — Django Admin Performance

A primary key index alone is not sufficient to ensure good performance in Django Admin when working with tables containing hundreds of thousands of records. The first issue I would investigate is **N+1 queries** caused by related models displayed in the admin list page. If `list_display` includes foreign key fields, Django may execute additional queries for every row. I would use `list_select_related` in the `ModelAdmin` to fetch related objects using SQL joins. For many-to-many relationships, I would override `get_queryset()` and use `prefetch_related()` to reduce the number of database queries significantly.

The second issue is **inefficient relationship widgets**. By default, Django loads all related objects into dropdowns, which becomes extremely slow for large tables. I would replace these with `autocomplete_fields` or `raw_id_fields` so related records are fetched only when searched, reducing both memory usage and page load time.

The third issue is **expensive search and ordering**. Admin searches configured through `search_fields` generate SQL `LIKE` queries that can become slow on large text columns. I would limit `search_fields` to indexed columns where appropriate and create additional database indexes for frequently searched fields. I would also review `ModelAdmin.ordering` to avoid unnecessary sorting on non-indexed columns.

These optimizations reduce SQL queries, minimize unnecessary data loading, and improve overall admin responsiveness while remaining fully compatible with Django's built-in admin interface.

---

## Question B — Pagination Trade-offs

Offset-based pagination retrieves records using SQL `LIMIT` and `OFFSET`. It is straightforward to implement and allows users to jump directly to any page, making it suitable for administrative dashboards and reporting interfaces. However, as the offset increases, the database must scan and discard an increasing number of rows before returning the requested page. This results in slower queries for large datasets. Additionally, if records are inserted or deleted while a user is paginating, the client may observe duplicate or skipped records because the row positions change.

Cursor-based pagination uses a stable, indexed field such as a primary key or timestamp to identify the last record returned. Instead of requesting page numbers, the client sends the cursor from the previous response. The database continues scanning from that point using indexed lookups, avoiding expensive offset scans. Cursor pagination also provides consistent results when records are inserted or deleted during pagination, making it ideal for continuously changing datasets.

For mobile applications implementing infinite scrolling, I would choose cursor pagination because it offers better scalability, lower query latency, and consistent ordering even under concurrent writes. For internal admin panels or reporting tools where users need direct access to arbitrary pages, offset pagination remains appropriate despite its reduced efficiency on very large datasets. The choice depends on whether scalability and consistency or random page access is the primary requirement.