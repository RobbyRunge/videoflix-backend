# Videoflix Backend

A Django REST Framework based backend for a video streaming platform with authentication, video management, and HLS streaming support.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Local Installation](#local-installation)
  - [Docker Installation](#docker-installation)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Database Setup](#database-setup)
- [Usage](#usage)
  - [Starting the Server](#starting-the-server)
  - [Admin Panel](#admin-panel)
- [API Documentation](#api-documentation)
  - [Authentication](#authentication)
  - [Video Endpoints](#video-endpoints)
- [Data Models](#data-models)
- [Background Tasks](#background-tasks)
- [Tests](#tests)
  - [Running Tests](#running-tests)
  - [Code Coverage](#code-coverage)
- [Deployment](#deployment)
- [Security](#security)
- [Development](#development)
  - [Adding New Features](#adding-new-features)
  - [Code Quality](#code-quality)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Project Overview

Videoflix Backend is a modern video streaming platform designed to securely manage and stream videos via HLS (HTTP Live Streaming). The project provides a complete REST API with authentication, user management, and video management.

## Features

### Authentication & User Management
- ✅ User registration with email verification
- ✅ Login/Logout with JWT authentication (cookie-based)
- ✅ Token refresh mechanism
- ✅ Password reset functionality
- ✅ Account activation via email

### Video Management
- ✅ Video upload and management
- ✅ Video categorization (Action, Comedy, Drama, etc.)
- ✅ Thumbnail support
- ✅ HLS streaming with multiple resolutions
- ✅ Video segmentation for adaptive streaming

### Security
- ✅ CORS support
- ✅ CSRF protection
- ✅ Secure password storage
- ✅ Token-based authentication

### Performance
- ✅ Redis caching
- ✅ Django-RQ for background tasks
- ✅ PostgreSQL database
- ✅ WhiteNoise for static files

## Technologie-Stack

| Kategorie | Technologie | Version |
|-----------|-------------|---------|
| **Framework** | Django | 5.2.9 |
| **REST API** | Django REST Framework | 3.16.1 |
| **Datenbank** | PostgreSQL | latest |
| **Cache** | Redis | latest |
| **Auth** | SimpleJWT | 5.5.1 |
| **Task Queue** | Django-RQ | 3.2.1 |
| **Server** | Gunicorn | 23.0.0 |
| **Container** | Docker & Docker Compose | - |
| **Testing** | Pytest | 9.0.1 |
| **Code Coverage** | pytest-cov | 7.0.0 |

## Projektstruktur

```
modul-11.2-videoflix-backend/
├── auth_app/                    # Authentication app
│   ├── api/                     # API-specific code
│   │   ├── authentication.py    # Custom authentication
│   │   ├── serializers.py       # DRF serializers
│   │   ├── signals.py           # Django signals
│   │   ├── urls.py              # URL routing
│   │   └── views.py             # API views
│   ├── migrations/              # Database migrations
│   ├── static/                  # Static files
│   ├── templates/               # Email templates
│   └── tests/                   # Unit tests
│
├── video_content_app/           # Video content app
│   ├── api/                     # API-specific code
│   │   ├── serializers.py       # DRF serializers
│   │   ├── signals.py           # Django signals
│   │   ├── urls.py              # URL routing
│   │   └── views.py             # API views
│   ├── migrations/              # Database migrations
│   ├── models.py                # Video model
│   ├── tasks.py                 # Background tasks
│   └── tests/                   # Unit tests
│
├── core/                        # Django project configuration
│   ├── settings.py              # Settings
│   ├── urls.py                  # Main URL configuration
│   ├── asgi.py                  # ASGI configuration
│   └── wsgi.py                  # WSGI configuration
│
├── media/                       # Uploaded media files
├── static/                      # Static files
├── htmlcov/                     # Coverage reports
│
├── backend.Dockerfile           # Docker image for backend
├── backend.entrypoint.sh        # Docker entrypoint script
├── docker-compose.yml           # Docker Compose configuration
├── manage.py                    # Django management tool
├── pytest.ini                   # Pytest configuration
├── requirements.txt             # Python dependencies
└── .env                         # Environment variables (not in repo)
```

## Prerequisites

### Local Development
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- pip
- virtualenv (recommended)

### Docker-based Development
- Docker 20.10+
- Docker Compose 2.0+

## Installation

### Local Installation

1. **Clone repository**
```bash
git clone <repository-url>
cd modul-11.2-videoflix-backend
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Create and fill .env file (see Configuration)
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

5. **Run database migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Start server**
```bash
python manage.py runserver
```

### Docker Installation

1. **Clone repository**
```bash
git clone <repository-url>
cd modul-11.2-videoflix-backend
```

2. **Configure environment variables**
```bash
# Create .env file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

3. **Start containers**
```bash
docker-compose up -d
```

4. **Run migrations**
```bash
docker-compose exec web python manage.py migrate
```

5. **Create superuser**
```bash
docker-compose exec web python manage.py createsuperuser
```

The server is now accessible at `http://localhost:8000`.

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:5500

# CORS
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5500
CORS_ALLOW_CREDENTIALS=True

# Database
DB_NAME=videoflix_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Frontend URL (for email links)
FRONTEND_URL=http://127.0.0.1:5500
```

### Database Setup

**PostgreSQL locally:**
```bash
# PostgreSQL Installation (Windows with Chocolatey)
choco install postgresql

# Create database
psql -U postgres
CREATE DATABASE videoflix_db;
CREATE USER videoflix_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE videoflix_db TO videoflix_user;
\q
```

**With Docker:**
The database is automatically created via `docker-compose.yml`.

## Usage

### Starting the Server

**Locally (Development):**
```bash
# Terminal 1: Django Server
python manage.py runserver

# Terminal 2: Redis (if installed locally)
redis-server

# Terminal 3: RQ Worker for Background Tasks
python manage.py rqworker default
```

**With Docker:**
```bash
docker-compose up
```

### Admin Panel

The Django Admin is accessible at: `http://localhost:8000/admin/`

Use the previously created superuser for login.

**Admin Functions:**
- Manage users
- Upload and manage videos
- Edit categories
- Monitor RQ tasks (`/django-rq/`)

## API Documentation

Base URL: `http://localhost:8000/api/`

### Authentication

#### Registration
```http
POST /api/register/
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "secure_password",
  "password2": "secure_password"
}
```

**Response:** 201 Created
```json
{
  "user": {
    "id": 1,
    "email": "test@example.com"
  },
  "token": "token"
}
```

#### Account Activation
```http
GET /api/activate/<uidb64>/<token>/
```
The link is sent via email.

#### Login
```http
POST /api/login/
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "secure_password"
}
```

**Response:** 200 OK (sets JWT cookies)
```json
{
  "detail": "Login successful",
  "user": {
    "id": 1,
    "username": "testuser"
  }
}
```

#### Token Refresh
```http
POST /api/token/refresh/
```
Automatically renews the access token via the refresh token cookie.

#### Logout
```http
POST /api/logout/
```
Deletes the JWT cookies.

#### Request Password Reset
```http
POST /api/password_reset/
Content-Type: application/json

{
  "email": "test@example.com"
}
```

#### Confirm Password Reset
```http
POST /api/password_confirm/<uidb64>/<token>/
Content-Type: application/json

{
  "password": "new_password",
  "password2": "new_password"
}
```

### Video Endpoints

#### Get Video List
```http
GET /api/video/
Authorization: Bearer <token> (via Cookie)
```

**Response:** 200 OK
```json
[
  {
    "id": 1,
    "created_at": "2023-01-01T12:00:00Z",
    "title": "Movie Title",
    "description": "Movie Description",
    "thumbnail_url": "http://example.com/media/thumbnail/image.jpg",
    "category": "Drama"
  },
]
```

#### Video-Manifest (HLS)
```http
GET /api/video/<movie_id>/<resolution>/index.m3u8
Authorization: Bearer <token> (via Cookie)
```

**Available Resolutions:**
- `480p`
- `720p`
- `1080p`

**Response:** 200 OK (M3U8 Playlist)

#### Video Segment
```http
GET /api/video/<movie_id>/<resolution>/<segment>/
Authorization: Bearer <token> (via Cookie)
```

Delivers individual video segments for HLS streaming.

## Data Models

### Video Model

```python
class Video(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='thumbnail/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    video_file = models.FileField(upload_to='videos/')
```

**Categories:**
- Action
- Comedy
- Drama
- Romance
- Horror
- Sci-Fi
- Documentary
- Animation

### User Model

Uses Django's standard User model with the following extensions:
- Email verification
- Active/Inactive status
- Password reset functionality

## Background Tasks

The project uses Django-RQ for asynchronous background tasks.

**RQ Dashboard:** `http://localhost:8000/django-rq/`

### Available Tasks

Tasks are located in `video_content_app/tasks.py`:
- Video transcoding
- Thumbnail generation
- HLS segment creation

### Starting Workers

```bash
# Locally
python manage.py rqworker default

# Docker
docker-compose exec web python manage.py rqworker default
```

## Tests

The project uses Pytest for unit and integration tests.

### Running Tests

```bash
# All tests
pytest

# With verbose output
pytest -v

# Specific test file
pytest auth_app/tests/test_login.py

# Specific test
pytest auth_app/tests/test_login.py::TestLogin::test_successful_login
```

**With Docker:**
```bash
docker-compose exec web pytest
```

### Code Coverage

```bash
# Generate coverage report
pytest --cov=. --cov-report=html

# Open report
# Windows
start htmlcov/index.html
# Linux/Mac
open htmlcov/index.html
```

The coverage reports are located in the `htmlcov/` directory.

### Test Structure

```
auth_app/tests/
├── conftest.py                 # Pytest fixtures
├── test_login.py               # Login tests
├── test_register.py            # Registration tests
├── test_password_reset.py      # Password reset tests
├── test_token_refresh.py       # Token refresh tests
├── test_serializers.py         # Serializer tests
└── test_signals.py             # Signal tests

video_content_app/tests/
├── conftest.py                 # Pytest fixtures
├── test_models.py              # Model tests
├── test_serializers.py         # Serializer tests
├── test_video_list.py          # Video list tests
└── test_video_streaming.py     # Streaming tests
```

## Deployment

### Production Checklist

- [ ] `DEBUG = False` in `.env`
- [ ] Generate strong `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS` correctly
- [ ] Use HTTPS
- [ ] Secure database passwords
- [ ] Test email configuration
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Use Gunicorn instead of runserver
- [ ] Configure Redis for production
- [ ] Implement backup strategy
- [ ] Set up monitoring
- [ ] Configure logs

### Starting Gunicorn

```bash
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Docker Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Security

### Best Practices

1. **Authentication:**
   - JWT tokens in httpOnly cookies
   - Access Token: 15 minutes lifetime
   - Refresh Token: 1 day lifetime

2. **CORS:**
   - Only allow trusted origins
   - Credentials only when needed

3. **CSRF:**
   - CSRF protection enabled
   - Trusted origins configured

4. **Passwords:**
   - Django's pbkdf2_sha256 hashing
   - Password validation enabled

5. **Rate Limiting:**
   - Implementation recommended for API endpoints
   - Django-ratelimit can be used

### Check for Known Vulnerabilities

```bash
# Check dependencies for security vulnerabilities
pip install safety
safety check

# Django-specific security checks
python manage.py check --deploy
```

## Development

### Adding New Features

1. **Create new Django app:**
```bash
python manage.py startapp new_app
```

2. **Register app in `INSTALLED_APPS`:**
```python
# core/settings.py
INSTALLED_APPS = [
    # ...
    'new_app',
]
```

3. **Create models and migrate:**
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Write tests:**
```bash
# new_app/tests/test_models.py
```

5. **Implement API endpoints:**
```python
# new_app/api/views.py
# new_app/api/urls.py
# new_app/api/serializers.py
```

### Code Quality

**Recommended Tools:**

```bash
# Linting
pip install flake8
flake8 .

# Code formatting
pip install black
black .

# Import sorting
pip install isort
isort .

# Type Checking
pip install mypy
mypy .
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Commit changes
git add .
git commit -m "feat: Add new feature"

# Create pull request
git push origin feature/new-feature
```

## Troubleshooting

### Common Issues

#### Port already in use
```bash
# Windows: Release port
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

#### Database connection error
```bash
# Check PostgreSQL status
# Windows
sc query postgresql-x64-14

# Docker
docker-compose ps
docker-compose logs db
```

#### Migration errors
```bash
# Reset migrations
python manage.py migrate app_name zero

# Restart
python manage.py makemigrations
python manage.py migrate
```

#### Redis connection issues
```bash
# Test Redis connection
redis-cli ping

# Docker Redis logs
docker-compose logs redis
```

#### Static files not found
```bash
# Collect static files
python manage.py collectstatic --noinput
```

#### JWT token errors
- Clear cookies in browser
- Ensure CORS is configured correctly
- `CORS_ALLOW_CREDENTIALS = True` is set

### Debug Mode

```python
# settings.py
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

### Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Use Django Debug Toolbar
3. Use Django Shell: `python manage.py shell`

## License

This project was created as part of the Developer Akademie.

---

Last updated: December 2025
