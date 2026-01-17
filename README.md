# Backend Security & IP Tracking

This project implements a robust security and analytics system using Django, Celery, and Redis to monitor, limit, and block IP addresses.

## Features

### 1. IP Logging & Middleware
- **Request Logging:** Captured `ip_address`, `timestamp`, and `path` for every request.
- **How it works:** Uses `request.META['REMOTE_ADDR']` or `HTTP_X_FORWARDED_FOR` (behind proxies) via middleware.

### 2. IP Blacklisting
- **Blocking:** Middleware checks incoming IPs against a `BlockedIP` model. Returns **403 Forbidden** if matched.
- **Management Command:** Block IPs via CLI:
  ```bash
  python manage.py block_ip <ip_address>
  ```

### 3. Geolocation Analytics
- **Integration:** Uses `geoip2` to map IPs to cities and countries.
- **Optimization:** Geolocation data is cached for **24 hours** in Redis to minimize API overhead.

#### Geolocation Setup
1. Create directory: `mkdir -p ip_tracking/geoip/`
2. Download the database: [GeoLite2-City](https://cdn.jsdelivr.net/npm/geolite2-city/GeoLite2-City.mmdb.gz)
3. Decompress and move `GeoLite2-City.mmdb` into `ip_tracking/geoip/`

### 4. Rate Limiting
- **Logic:** Enforced via `django-ratelimit`.
  - **Anonymous:** 5 requests/minute.
  - **Authenticated:** 10 requests/minute.
- **Handling:** Configured with `block=False` to return custom **429 Too Many Requests** responses.

### 5. Anomaly Detection (Celery)
- **Hourly Scan:** A Celery Beat task runs every hour to flag:
  - IPs exceeding **100 requests/hour**.
  - IPs accessing sensitive paths like `/admin` or `/login`.
- **Storage:** Flagged IPs are saved to the `SuspiciousIP` model for review.


## Setup & Execution

### Prerequisites
- Redis (running via Docker)
- Python 3.10+

### Installation
```bash
pip install -r requirements.txt
python manage.py migrate
```

### Running the Services

1.  **Start Redis:**
```bash
docker run -p 6379:6379 redis
```

2.  **Start Django:**
```bash
python manage.py runserver
```

3.  **Start Celery Worker:**
```bash
celery -A alx_backend_security worker -l info --pool=solo
```

4.  **Start Celery Beat (Scheduler):**
```bash
celery -A alx_backend_security beat -l info
```