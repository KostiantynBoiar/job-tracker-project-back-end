# Django Job Tracker

A Django-based job tracking application with OAuth authentication, job scraping, user preferences, and email notifications.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Local Deployment

### 1. Clone the Repository

```bash
cd job_tracker_root
```

### 2. Build and Start Services

Build the Docker images and start all services:

```bash
docker-compose -f docker-compose-dev.yml build
docker-compose -f docker-compose-dev.yml up
```

Or run in detached mode:

```bash
docker-compose -f docker-compose-dev.yml up -d
```

### 3. Run Database Migrations

In a new terminal, run migrations:

```bash
docker-compose -f docker-compose-dev.yml exec api python manage.py migrate
```

### 5. Create Superuser (Optional)

To access the Django admin panel:

```bash
docker-compose -f docker-compose-dev.yml exec api python manage.py createsuperuser
```

## Accessing the Application

- **Django API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Common Commands

### View Logs

```bash
docker-compose -f docker-compose-dev.yml logs -f api
```

### Stop Services

```bash
docker-compose -f docker-compose-dev.yml down
```

### Stop Services and Remove Volumes

```bash
docker-compose -f docker-compose-dev.yml down -v
```

### Rebuild After Code Changes

```bash
docker-compose -f docker-compose-dev.yml build --no-cache
docker-compose -f docker-compose-dev.yml up
```

### Access Django Shell

```bash
docker-compose -f docker-compose-dev.yml exec api python manage.py shell
```

### Create New Migrations

```bash
docker-compose -f docker-compose-dev.yml exec api python manage.py makemigrations
```

## Project Structure

```
job_tracker_root/
├── config/              # Django project configuration
│   ├── settings.py      # Django settings
│   ├── urls.py          # Root URL configuration
│   ├── celery.py        # Celery configuration
│   ├── wsgi.py          # WSGI configuration
│   └── asgi.py          # ASGI configuration
├── apps/
│   ├── users/           # User authentication and profiles
│   ├── jobs/            # Job listings and companies
│   └── preferences/    # User preferences and daily recaps
├── scrapers/            # Job scraping logic
│   └── providers/      # Provider-specific scrapers
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker image configuration
└── docker-compose-dev.yml  # Docker Compose configuration
```

## Services

- **api**: Django REST API server
- **db**: PostgreSQL database
- **redis**: Redis cache and Celery broker

## Troubleshooting

### Port Already in Use

If port 8000, 5432, or 6379 is already in use, modify the port mappings in `docker-compose-dev.yml`.

### Database Connection Issues

Ensure the database service is healthy before starting the API:
```bash
docker-compose -f docker-compose-dev.yml ps
```

### Module Not Found Errors

Rebuild the Docker image:
```bash
docker-compose -f docker-compose-dev.yml build --no-cache
```

## Development

The project uses volume mounting for live code reloading. Changes to Python files will automatically reload the Django development server.
