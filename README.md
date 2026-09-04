# ⚙️ StarClinch - Notification Management System Backend API

[![Django](https://img.shields.io/badge/Django-6.1-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.18-red?style=for-the-badge&logo=django)](https://www.django-rest-framework.org/)
[![Celery](https://img.shields.io/badge/Celery-5.6-37B24D?style=for-the-badge&logo=celery)](https://docs.celeryq.dev/)
[![Redis](https://img.shields.io/badge/Redis-8.1-DC382D?style=for-the-badge&logo=redis)](https://redis.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?style=for-the-badge&logo=render)](https://render.com/)

A high-performance, service-oriented Django REST Framework API powering the **StarClinch Multi-Channel Notification Engine**. Handles async notification dispatch via Celery & Redis across **WhatsApp (Meta Graph API)**, **SMTP Email / Postmark**, and **Web Push (OneSignal)** with real-time audit logging and matrix configuration.

---

## 🌟 Architecture & Core Features

### 🔀 1. Multi-Channel Notification Dispatcher
- **WhatsApp Integration**: Sends structured Meta WhatsApp Business API messages with variable substitution.
- **Email Delivery Engine**: Supports both standard SMTP and transactional Email providers (Postmark).
- **Web Push Engine**: Native browser push notifications powered by OneSignal REST API.
- **Asynchronous Task Queue**: Background job execution using Celery workers backed by Redis broker for zero latency on web requests.

### 🎛️ 2. Dynamic Matrix & Event Trigger System
- **Event Triggers**: System event triggers (e.g., `BOOKING_CREATED`, `PAYMENT_SUCCESS`, `ARTIST_CONFIRMED`).
- **Channel Mapping**: Configurable matrix linking event triggers with active channels and templates.
- **Status Toggles**: Dynamic activation/deactivation of trigger events system-wide without code deployment.

### 📝 3. Dynamic Template Manager
- **Channel-Specific Fields**: Supports WhatsApp template names, Email subjects, and Web Push titles & bodies.
- **Variable Mapping**: Flexible JSON variable injection (e.g. `{ user_name, order_id, amount }`).
- **Template Status Lifecycle**: Track template states (`DRAFT`, `ACTIVE`, `DISABLED`, `FAILED`).

### 📜 4. Audit & Delivery Logs
- **Comprehensive Audit Trail**: Records status (`PENDING`, `SENT`, `FAILED`, `SKIPPED`) for every delivery attempt.
- **Diagnostics**: Captures provider message IDs, error strings, and timestamp logs for real-time debugging.

### 🔒 5. JWT Authentication & Access Control
- **SimpleJWT Auth**: Bearer token authentication with sliding token refresh mechanics.
- **Custom User Model**: Role-based access for Admins (`is_staff`, `is_superuser`) and end users.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Framework** | Django 6.1 + Django REST Framework 3.18 |
| **Authentication** | djangorestframework-simplejwt (JWT) |
| **Background Tasks** | Celery 5.6 + Redis 8.1 |
| **Database** | PostgreSQL (Production) / SQLite3 (Development) |
| **CORS Middleware** | django-cors-headers |
| **WSGI Server** | Gunicorn |

---

## 📁 Directory Structure

```
backend/
├── apps/
│   ├── authentication/   # Custom User model, JWT Login/Logout endpoints
│   ├── core/             # Base models & shared utility functions
│   ├── notifications/    # Trigger matrix, Templates, Delivery Logs, Celery tasks
│   └── webpush/          # Web Push subscriptions & payload handlers
├── config/               # Django project settings, URLs, WSGI, Celery config
│   ├── settings.py       # Central configuration with env overrides
│   ├── urls.py           # Master API routing table
│   ├── celery.py         # Celery task queue setup
│   └── wsgi.py           # Production WSGI entry point
├── Dockerfile            # Container deployment specification
├── render.yaml           # Infrastructure-as-code for Render deployment
├── requirements.txt      # Python dependencies
├── .env.example           # Environment configuration template
├── manage.py             # Django CLI runner
└── .gitignore            # Git exclusion rules
```

---

## ⚙️ Getting Started

### 1. Prerequisites
- **Python**: 3.12+
- **Redis Server**: Required for Celery background tasks

### 2. Virtual Environment Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/macOS
# or
venv\Scripts\activate    # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the `backend/` directory by copying `.env.example`:

```bash
cp .env.example .env
```

Configure your environment variables in `.env`:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=*

# Optional: PostgreSQL Database (Defaults to SQLite if omitted)
# DATABASE_URL=postgresql://user:password@localhost:5432/notification_db

# Redis / Celery Config
REDIS_URL=redis://localhost:6379/0

# Notification Providers
WHATSAPP_ACCESS_TOKEN=your-whatsapp-token
WHATSAPP_PHONE_NUMBER_ID=your-whatsapp-phone-id
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
ONESIGNAL_APP_ID=your-onesignal-app-id
ONESIGNAL_REST_API_KEY=your-onesignal-api-key
```

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 7. Start Development Server & Celery Worker

Terminal 1 (Django API):
```bash
python manage.py runserver 8000
```

Terminal 2 (Celery Background Worker):
```bash
celery -A config worker --loglevel=info
```

The API will be available at [http://localhost:8000/api/](http://localhost:8000/api/).

---

## 🔌 API Endpoints Summary

| Method | Endpoint | Description | Permission |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/login/` | Obtain JWT Access & Refresh Tokens | Public |
| `POST` | `/api/auth/logout/` | Blacklist refresh token & logout | Authenticated |
| `GET` | `/api/notifications/admin/matrix/` | Fetch Trigger Event Matrix | Admin |
| `POST` | `/api/notifications/templates/` | Create notification channel template | Admin |
| `PATCH` | `/api/notifications/templates/{id}/` | Update template or toggle status | Admin |
| `GET` | `/api/notifications/deliveries/` | Fetch delivery audit trail logs | Authenticated |
| `POST` | `/api/notifications/admin/test-send/` | Dispatch test notification | Admin |
| `POST` | `/api/webpush/subscribe/` | Register browser push token | Authenticated |

---

## 🌐 Deployment

### Deploy on Render (Recommended)
This repository includes a `render.yaml` Blueprint specification:

1. Connect your repository to **Render Blueprints**.
2. Render will automatically provision:
   - **Web Service** (Django Gunicorn API)
   - **Celery Worker** (Background Task Execution)
   - **PostgreSQL Database** (`notification-db`)
3. Set your live secrets under Environment Variables.

### Deploy with Docker
```bash
# Build Docker image
docker build -t starclinch-backend .

# Run container
docker run -p 8000:8000 --env-file .env starclinch-backend
```

---

## 📄 License

This project is proprietary software created for **StarClinch**. All rights reserved.
