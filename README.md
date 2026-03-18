# Job Tracker API

A Django REST API for tracking job postings from major tech companies with OAuth authentication, automated scraping, user preferences, and daily recap notifications.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

## Features

- **JWT & OAuth Authentication** - Email/password login with Google and GitHub OAuth support
- **Job Management** - CRUD operations for job postings with filtering and pagination
- **Company Management** - Track companies and their career pages
- **Saved Jobs** - Users can save and track job applications
- **User Preferences** - Customizable job recommendations based on preferences
- **Daily Recaps** - Automated daily job recommendation emails
- **Job Scraping** - Automated scraping from Apple, Nvidia, and other tech companies

## Tech Stack

- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL
- **Cache/Broker**: Redis
- **Task Queue**: Celery + Celery Beat
- **Authentication**: JWT (SimpleJWT) + OAuth (django-allauth)
- **Documentation**: drf-spectacular (OpenAPI/Swagger)
- **Containerization**: Docker + Docker Compose

## Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)

## Local Development

### 1. Clone and Navigate

```bash
cd job_tracker_root
```

### 2. Create Environment File

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Build and Start Services

```bash
docker-compose -f docker-compose-dev.yml build
docker-compose -f docker-compose-dev.yml up -d
```

### 4. Run Migrations

```bash
docker-compose -f docker-compose-dev.yml exec api python manage.py migrate
```

### 5. Seed Initial Data

```bash
docker-compose -f docker-compose-dev.yml exec api python manage.py seed_companies
```

### 6. Create Superuser (Optional)

```bash
docker-compose -f docker-compose-dev.yml exec api python manage.py createsuperuser
```

### Access Points

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/api/docs/ |
| ReDoc | http://localhost:8000/api/redoc/ |
| Admin Panel | http://localhost:8000/admin/ |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost` |
| `DB_NAME` | Database name | `job_tracker_db` |
| `DB_USER` | Database user | `user` |
| `DB_PASSWORD` | Database password | Required |
| `DB_HOST` | Database host | `db` |
| `DB_PORT` | Database port | `5432` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `FRONTEND_URL` | Frontend URL for OAuth redirects | `http://localhost:3000` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated CORS origins | `http://localhost:3000` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | - |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | - |
| `GITHUB_CLIENT_ID` | GitHub OAuth client ID | - |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth client secret | - |

## API Documentation

### Base URL

```
http://localhost:8000/api/
```

### Authentication

All endpoints (except registration, login, and OAuth) require JWT authentication:

```
Authorization: Bearer <access_token>
```

---

### Users API (`/api/users/`)

#### Register User

```http
POST /api/users/register/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:** `201 Created`
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "auth_provider": "email",
    "is_active": true,
    "date_joined": "2024-01-15T10:30:00Z",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

#### Login

```http
POST /api/users/login/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "user": { ... },
  "tokens": {
    "access": "...",
    "refresh": "..."
  }
}
```

#### Logout

```http
POST /api/users/logout/
```

**Request Body:**
```json
{
  "refresh": "<refresh_token>"
}
```

**Response:** `200 OK`

#### Refresh Token

```http
POST /api/users/token/refresh/
```

**Request Body:**
```json
{
  "refresh": "<refresh_token>"
}
```

**Response:** `200 OK`
```json
{
  "access": "<new_access_token>"
}
```

#### Get Profile

```http
GET /api/users/me/
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "auth_provider": "email",
  "is_active": true,
  "date_joined": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Update Profile

```http
PUT /api/users/me/
```

**Request Body:**
```json
{
  "username": "newusername",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

#### Change Password

```http
POST /api/users/me/change-password/
```

**Request Body:**
```json
{
  "old_password": "OldPass123!",
  "new_password": "NewPass456!",
  "new_password_confirm": "NewPass456!"
}
```

#### OAuth - Google Login

```http
GET /api/users/oauth/google/login/
```

**Response:** `200 OK`
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?..."
}
```

#### OAuth - GitHub Login

```http
GET /api/users/oauth/github/login/
```

**Response:** `200 OK`
```json
{
  "authorization_url": "https://github.com/login/oauth/authorize?..."
}
```

---

### Jobs API (`/api/jobs/`)

#### List Jobs

```http
GET /api/jobs/
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number (default: 1) |
| `page_size` | int | Items per page (default: 20, max: 100) |
| `company` | int | Filter by company ID |
| `location` | int | Filter by location ID |
| `category` | int | Filter by category ID |
| `is_remote` | bool | Filter remote jobs |
| `is_active` | bool | Filter active jobs |

**Response:** `200 OK`
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/jobs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "company": {
        "id": 1,
        "name": "Apple",
        "logo_url": "https://...",
        "careers_url": "https://jobs.apple.com",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      },
      "location": {
        "id": 1,
        "city": "Cupertino",
        "state": "California",
        "country": "USA",
        "is_remote": false
      },
      "category": {
        "id": 1,
        "name": "Engineering",
        "slug": "engineering"
      },
      "external_id": "APPLE-12345",
      "title": "Senior Software Engineer",
      "description": "...",
      "requirements": "...",
      "employment_type": "full_time",
      "experience_level": "senior",
      "salary_min": "150000.00",
      "salary_max": "200000.00",
      "salary_currency": "USD",
      "external_url": "https://jobs.apple.com/...",
      "is_remote": false,
      "is_active": true,
      "posted_at": "2024-01-10T00:00:00Z",
      "scraped_at": "2024-01-15T06:00:00Z",
      "created_at": "2024-01-15T06:00:00Z",
      "updated_at": "2024-01-15T06:00:00Z"
    }
  ]
}
```

#### Get Job Details

```http
GET /api/jobs/{id}/
```

#### Create Job

```http
POST /api/jobs/create/
```

**Request Body:**
```json
{
  "company_id": 1,
  "location_id": 1,
  "category_id": 1,
  "external_id": "JOB-001",
  "title": "Software Engineer",
  "description": "Job description...",
  "requirements": "Requirements...",
  "employment_type": "full_time",
  "experience_level": "mid",
  "salary_min": 100000,
  "salary_max": 150000,
  "salary_currency": "USD",
  "external_url": "https://example.com/job",
  "is_remote": false
}
```

**Employment Types:** `full_time`, `part_time`, `contract`, `freelance`, `internship`

**Experience Levels:** `entry`, `mid`, `senior`, `executive`

#### Update Job

```http
PUT /api/jobs/{id}/update/
PATCH /api/jobs/{id}/update/
```

#### Delete Job

```http
DELETE /api/jobs/{id}/delete/
```

---

### Saved Jobs API (`/api/jobs/saved/`)

#### List Saved Jobs

```http
GET /api/jobs/saved/
```

**Response:** `200 OK`
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "job": { ... },
      "status": "active",
      "notes": "Applied on 2024-01-15",
      "saved_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### Save Job

```http
POST /api/jobs/saved/create/
```

**Request Body:**
```json
{
  "job_id": 1,
  "status": "fresh",
  "notes": "Looks interesting"
}
```

**Status Options:** `active`, `expired`, `fresh`

#### Get Saved Job

```http
GET /api/jobs/saved/{id}/
```

#### Update Saved Job

```http
PUT /api/jobs/saved/{id}/update/
PATCH /api/jobs/saved/{id}/update/
```

**Request Body:**
```json
{
  "status": "active",
  "notes": "Updated notes"
}
```

#### Delete Saved Job

```http
DELETE /api/jobs/saved/{id}/delete/
```

---

### Companies API (`/api/companies/`)

#### List Companies

```http
GET /api/companies/
```

**Response:** `200 OK`
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Apple",
      "logo_url": "https://...",
      "careers_url": "https://jobs.apple.com",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Get Company

```http
GET /api/companies/{id}/
```

#### Create Company

```http
POST /api/companies/create/
```

**Request Body:**
```json
{
  "name": "TechCorp",
  "logo_url": "https://example.com/logo.png",
  "careers_url": "https://techcorp.com/careers",
  "is_active": true
}
```

#### Update Company

```http
PUT /api/companies/{id}/update/
PATCH /api/companies/{id}/update/
```

#### Delete Company

```http
DELETE /api/companies/{id}/delete/
```

---

### Preferences API (`/api/preferences/`)

#### Get/Update Preferences

```http
GET /api/preferences/
PUT /api/preferences/
PATCH /api/preferences/
```

**Response/Request Body:**
```json
{
  "experience_level": "senior",
  "min_salary": "100000.00",
  "remote_only": true,
  "notification_frequency": "daily",
  "preferred_send_time": "09:00:00"
}
```

**Notification Frequencies:** `daily`, `weekly`, `never`

#### Get Recommended Jobs

```http
GET /api/preferences/recommended/
```

Returns jobs matching user preferences.

#### Daily Recaps

```http
GET /api/preferences/recaps/
```

**Response:** `200 OK`
```json
{
  "count": 7,
  "results": [
    {
      "id": 1,
      "jobs_count": 15,
      "status": "sent",
      "sent_at": "2024-01-15T00:00:00Z",
      "jobs": [...]
    }
  ]
}
```

---

### Preferred Companies

```http
GET    /api/preferences/companies/           # List preferred companies
POST   /api/preferences/companies/add/       # Add preferred company
DELETE /api/preferences/companies/{id}/      # Remove preferred company
```

**Add Request:**
```json
{
  "company_id": 1
}
```

---

### Preferred Categories

```http
GET    /api/preferences/categories/          # List preferred categories
POST   /api/preferences/categories/add/      # Add preferred category
DELETE /api/preferences/categories/{id}/     # Remove preferred category
```

**Add Request:**
```json
{
  "category_id": 1
}
```

---

### Preferred Locations

```http
GET    /api/preferences/locations/           # List preferred locations
POST   /api/preferences/locations/add/       # Add preferred location
DELETE /api/preferences/locations/{id}/      # Remove preferred location
```

**Add Request:**
```json
{
  "location_id": 1
}
```

---

### Keywords

```http
GET    /api/preferences/keywords/            # List keywords
POST   /api/preferences/keywords/add/        # Add keyword
DELETE /api/preferences/keywords/{id}/       # Remove keyword
```

**Add Request:**
```json
{
  "keyword": "python"
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

| Status Code | Description |
|-------------|-------------|
| `400` | Bad Request - Invalid input data |
| `401` | Unauthorized - Missing or invalid token |
| `403` | Forbidden - Insufficient permissions |
| `404` | Not Found - Resource doesn't exist |
| `500` | Internal Server Error |

---

## Project Structure

```
job_tracker_root/
├── config/                     # Django project configuration
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Root URL configuration
│   ├── celery.py               # Celery configuration
│   └── wsgi.py                 # WSGI configuration
├── apps/
│   ├── users/                  # User authentication & profiles
│   │   ├── models.py           # User model with OAuth fields
│   │   ├── views.py            # Auth views (login, register, OAuth)
│   │   ├── services.py         # Business logic
│   │   ├── serializers.py      # DRF serializers
│   │   └── adapters.py         # OAuth adapters
│   ├── companies/              # Company management
│   │   ├── models.py           # Company model
│   │   ├── views.py            # CRUD views
│   │   ├── services.py         # Business logic
│   │   └── serializers.py      # DRF serializers
│   ├── jobs/                   # Job listings & saved jobs
│   │   ├── models.py           # Job, SavedJob, Location, Category
│   │   ├── views.py            # CRUD views
│   │   ├── services.py         # Business logic
│   │   ├── serializers.py      # DRF serializers
│   │   └── tasks.py            # Celery scraping tasks
│   └── preferences/            # User preferences & recaps
│       ├── models.py           # UserPreference, DailyRecap
│       ├── views.py            # Preference views
│       ├── services.py         # Recommendation logic
│       └── tasks.py            # Daily recap tasks
├── scrapers/                   # Job scraping logic
│   ├── base.py                 # Base scraper class
│   ├── factory.py              # Scraper factory
│   └── providers/              # Provider-specific scrapers
│       ├── apple.py
│       └── nvidia.py
├── nginx/                      # Nginx configuration
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image configuration
├── docker-compose.yml          # Production Docker Compose
└── docker-compose-dev.yml      # Development Docker Compose
```

---

## Common Commands

### View Logs

```bash
docker-compose -f docker-compose-dev.yml logs -f api
docker-compose -f docker-compose-dev.yml logs -f celery-worker
```

### Stop Services

```bash
docker-compose -f docker-compose-dev.yml down
```

### Stop and Remove Volumes

```bash
docker-compose -f docker-compose-dev.yml down -v
```

### Rebuild After Changes

```bash
docker-compose -f docker-compose-dev.yml build --no-cache
docker-compose -f docker-compose-dev.yml up -d
```

### Access Django Shell

```bash
docker-compose -f docker-compose-dev.yml exec api python manage.py shell
```

### Create Migrations

```bash
docker-compose -f docker-compose-dev.yml exec api python manage.py makemigrations
```

### Run Migrations

```bash
docker-compose -f docker-compose-dev.yml exec api python manage.py migrate
```

### Trigger Manual Scrape

```bash
docker-compose -f docker-compose-dev.yml exec api python manage.py shell -c "from apps.jobs.tasks import scrape_all; scrape_all.delay()"
```

---

## Troubleshooting

### Port Already in Use

Modify port mappings in `docker-compose-dev.yml` if ports 8000, 5432, or 6379 are occupied.

### Database Connection Issues

```bash
docker-compose -f docker-compose-dev.yml ps
docker-compose -f docker-compose-dev.yml logs db
```

### Module Not Found Errors

```bash
docker-compose -f docker-compose-dev.yml build --no-cache
```

### CORS Issues

Ensure `CORS_ALLOWED_ORIGINS` in `.env` includes your frontend URL.

### OAuth Not Working

1. Verify OAuth credentials in `.env`
2. Check callback URLs are configured in Google/GitHub developer consoles
3. Ensure `FRONTEND_URL` is set correctly

---

## License

MIT License
