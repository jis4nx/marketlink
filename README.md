## Infrastructure

**Docker Compose**: One setup for web, Celery worker, and Redis. Easy to run locally and consistent across environments.

**Environment-based config**: All sensitive values come from environment variables via `python-decouple`. Different configs for dev/staging/prod without code changes.

**Redis multi-purpose**: Redis handles Celery broker, result backend, Django cache, and stock reservations. One service, multiple uses.

## Setup Guide

### Prerequisites
- Docker and Docker Compose installed
- SSLCommerz account credentials (for payment processing)

### Steps

1. **Clone the repository** (if not already done)

2. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

3. **Configure environment variables**:
   Edit `.env` and fill in your values:
   - `SECRET_KEY`: Django secret key (generate a new one for production)
   - `SSLCOMMERZ_*`: Your SSLCommerz credentials
   - `BASE_DOMAIN`: Your domain (for payment callbacks)
   - `WEBHOOK_SECRET`: SSLCommerz store password (used for webhook validation)
   - Redis settings can usually stay as defaults for local development

4. **Build and start services**:
   ```bash
   docker-compose up --build
   ```
   This starts:
   - Django web server (port 8000)
   - Celery worker
   - Redis

5. **Run migrations**:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

6. **Create superuser** (optional):
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

7. **Access the application**:
   - API: http://localhost:8000
   - Admin: http://localhost:8000/admin

### Development

To run commands inside the container:
```bash
docker-compose exec web python manage.py <command>
```

To view logs:
```bash
docker-compose logs -f web
docker-compose logs -f celery_worker
```

To stop services:
```bash
docker-compose down
```

To stop and remove volumes (clears database):
```bash
docker-compose down -v
```

# Test
**Test Cases**
<br>
Test cases are inside the django apps either `tests` or `test.py` file
you can run `test` by `docker compose exec web pytest .`
 

**Custom user model with UUIDs**: Using UUIDs instead of auto-incrementing IDs for better security and easier integration. Email-based auth instead of usernames.

**Role-based system**: Three roles (Customer, Vendor, Admin) handled via a role field on the User model. Simple and extensible. Proxy models (`Customer`, `Vendor`) provide role-specific querysets without extra tables.

**JWT authentication**: Stateless tokens work better for APIs than sessions. 2-day access tokens, 7-day refresh tokens with rotation.

## Database Design

**Separate vendor profile**: Vendor-specific data (business name, address, active status) is in a separate `VendorProfile` model linked via OneToOne. Keeps the User model clean.

**Vendor activation**: Vendors can login and access their account even when `is_active=False`, but they can't create or manage services until an admin activates their account (`is_active=True`). This allows vendors to set up their profile while waiting for approval.

**Service variants**: Services represent the repair type (e.g., "Engine Repair"), variants are pricing tiers (e.g., "Premium", "Basic"). Lets vendors offer multiple options for the same service.

**Payment data separation**: Payment gateway data stored separately from orders. Makes it easy to add more gateways later without cluttering the order model.

## Stock Management & Concurrency Handling

**Dual-layer stock management**: When multiple customers try to buy the last item simultaneously, we need to prevent overselling. The solution uses both Redis and the database.

**Phase 1 - Redis fast check**: First, we decrement stock in Redis (in-memory, very fast). If Redis shows negative stock, we immediately reject the request and roll back. This catches most race conditions quickly without hitting the database.

**Phase 2 - Database atomic update**: Even if Redis allows it, we verify and decrement in the database using Django's `F()` expressions. This does an atomic `UPDATE ... SET stock = stock - 1 WHERE stock > 0`. If the database update affects 0 rows (meaning stock was already 0), we know someone else got it first and we reject.

**Rollback on failure**: If anything fails (payment gateway error, validation failure, etc.), we restore stock in both Redis and the database. The `reject()` method handles this cleanup.

**Why both layers?**: Redis is fast but not the source of truth. Database is authoritative but slower. Using both means we catch most conflicts quickly via Redis, but the database ensures we never oversell even under extreme load. The database's atomic operations and transactions guarantee consistency.

**Transaction safety**: The entire order creation happens in a database transaction. If the payment gateway fails or any error occurs, the transaction rolls back automatically. We also manually restore Redis stock in the exception handler as a safety net.

## Payment Flow

**SSLCommerz integration**: Integrated with SSLCommerz payment gateway for processing payments. The payment service is abstracted so other gateways can be added later.

**Webhook-based confirmation**: SSLCommerz sends webhooks (IPN) instead of polling. More reliable and real-time. Hash validation ensures webhooks are authentic, plus secondary validation via SSLCommerz's validation API.

**Amount verification**: Always verify the paid amount matches the order amount. Critical security check to prevent manipulation. If amounts don't match, the order is rejected and stock is restored.

**Atomic payment confirmation**: Payment confirmation updates order status, creates payment records, and enqueues tasks all in one transaction. Either everything succeeds or nothing does. Tasks are enqueued via `transaction.on_commit()` so they only run after the database transaction commits successfully.

## Async Processing

**Celery for background work**: Payment confirmation triggers invoice generation and repair workflow start. These run as Celery tasks so the webhook can respond quickly. Tasks only run after the database transaction commits to avoid stale data.

## API Design

**Versioned endpoints**: All APIs under `/api/v1/` so we can evolve without breaking existing clients.

**Query optimization**: Using `select_related` to fetch related data in one query instead of N+1 queries. Separate serializers for list vs detail views to keep payloads lean.

## Security

**Custom permissions**: Built permission classes for role-based and ownership checks (`IsCustomer`, `IsVendor`, `IsServiceOwner`, etc.). More flexible than DRF's defaults.

**Model validation**: Business rules enforced at the model level (like "only active vendors can create services"). Works regardless of how the model is created (API, admin, scripts).

# API Documentation
**Postman Collection can be found on** : https://documenter.getpostman.com/view/21282873/2sBXVhBpoS
