# Quiz Master V2 - MAD II Project

Complete quiz management application with Flask API, Vue.js frontend, Redis caching, and Celery background jobs.

## Technology Stack

**Backend:** Flask, SQLAlchemy, JWT, Redis, Celery, SQLite
**Frontend:** Vue.js 3, Bootstrap 5, Chart.js, Axios

## Prerequisites

- [Python 3.8+](https://python.org/downloads)
- [Node.js 16+](https://nodejs.org/download)
- [Redis Server](https://github.com/microsoftarchive/redis/releases)
- [Git](https://git-scm.com/downloads)

## Quick Setup

### 1. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Configure Environment

Create `backend/.env`:

```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-key
SMTP_SERVER=localhost
SMTP_PORT=1025
SMTP_USERNAME=
SMTP_PASSWORD=
```

### 3. Download Required Tools

- **Redis:** Download [Redis for Windows](https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip) and extract to project root
- **MailHog:** Download [MailHog](https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_windows_amd64.exe) and rename to `mailhog.exe`

## Quick Start Guide

### Step 1: Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd Quiz_management_app_21f3000201

# Setup environment
cd backend
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

### Step 2: Install Dependencies

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..
```

## Running the Application

Open 6 terminals and run:

**Terminal 1: Redis**

```bash
.\Redis-x64-3.0.504\redis-server.exe
```

**Terminal 2: MailHog**

```bash
.\mailhog.exe
```

**Terminal 3: Backend**

```bash
cd backend && python run.py
```

_Note: Minimal logging - only shows server startup and errors_

**Terminal 4: Frontend**

```bash
cd frontend && npm run dev
```

**Terminal 5: Celery Worker**

```bash
cd backend && python -m celery -A app.celery_worker worker --loglevel=info --pool=solo
```

**Terminal 6: Celery Beat**

```bash
cd backend && python -m celery -A app.celery_worker beat --loglevel=info
```

## Access Points

- **Frontend:** http://localhost:8080 (Vue.js UI)
- **Backend API:** http://localhost:5000 (Flask API)
- **MailHog Web UI:** http://localhost:8025 (Email Testing)
- **Redis:** localhost:6379 (Caching & Celery Broker)

## Default Login

**Admin Account:**

- Email: admin@quizmaster.com
- Password: Admin@123

## Email Testing with MailHog

MailHog captures all emails sent by the application for testing:

1. **Download:** [MailHog v1.0.1](https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_windows_amd64.exe)
2. **Rename:** Save as `mailhog.exe` in project root
3. **Start MailHog:** `.\mailhog.exe` (runs on port 1025)
4. **Access Web UI:** http://localhost:8025
5. **View Emails:** All emails appear in MailHog interface
6. **Configuration:** Already set in `.env` (SMTP: localhost:1025)

## Testing Backend Jobs

**Prerequisites:** Start Redis and MailHog first

```bash
# Test email (check MailHog at http://localhost:8025)
cd backend
python -c "from app.tasks import send_email; print('✅ Email sent!' if send_email('test@example.com', 'Test Email', '<h1>Test successful!</h1>') else '❌ Email failed!')"

# Test daily reminders (emails appear in MailHog every 5 minutes when Celery Beat is running)
python -c "from app import create_app; from app.tasks import send_daily_reminders; app=create_app(); app.app_context().push(); print(send_daily_reminders())"

# Test CSV export (files saved to backend/exports/)
python -c "from app import create_app; from app.tasks import export_user_csv; app=create_app(); app.app_context().push(); print(export_user_csv())"
```

**Automatic Jobs (when Celery Beat is running):**

- **Daily Reminders:** Every 5 minutes (for testing)
- **Monthly Reports:** Every 10 minutes (for testing)
- **File Cleanup:** Every 15 minutes (for testing)

## Features

- **User Management:** Registration, authentication, role-based access
- **Quiz System:** Interactive quizzes with timer and scoring
- **Admin Panel:** Complete CRUD operations for content management
- **Background Jobs:** Daily reminders, monthly reports, CSV exports
- **Performance:** Redis caching, optimized queries
- **Analytics:** Charts and statistics with Chart.js

## API Endpoints

```bash
# Authentication
POST /api/auth/login
POST /api/auth/register

# Dashboard
GET /api/dashboard

# Quiz Management
GET /api/subjects
POST /api/subjects
GET /api/quizzes
POST /api/quiz/attempt

# Background Jobs
POST /api/jobs/export/user
POST /api/jobs/export/admin
```

## Troubleshooting

**Redis Connection Error:**

- Ensure Redis server is running
- Check port 6379 availability

**Celery Worker Issues:**

- Use `--pool=solo` flag on Windows
- Start Redis before Celery

**Email Not Working:**

- Ensure MailHog is running on port 1025
- Check MailHog web UI at http://localhost:8025

**Frontend Issues:**

- Run `npm install` if dependencies missing
- Check port 8080 availability

## MAD II Requirements Compliance

- Flask API Backend
- Vue.js Frontend
- SQLite Database
- Redis Caching
- Celery Background Jobs
- Daily Reminders via Email
- Monthly HTML Reports
- CSV Export Functionality
- Performance Caching with Expiry
- Bootstrap Styling
- Chart.js Integration
- Responsive Design
- Form Validation

---

**Quiz Master V2 - Complete MAD II Project**
