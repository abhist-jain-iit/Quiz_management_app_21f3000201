# Quiz Master V2 - MAD II Project

Modern quiz management application built with Flask API, Vue.js frontend, Redis caching, and Celery background jobs.

## Technology Stack

- **Backend:** Flask, SQLAlchemy, JWT, Redis, Celery, SQLite
- **Frontend:** Vue.js 3, Bootstrap 5, Chart.js, Axios
- **Database:** SQLite
- **Caching:** Redis
- **Background Jobs:** Celery

## Prerequisites

- Python 3.8+
- Node.js 16+
- Redis Server
- Git

## Installation & Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd Quiz_management_app_21f3000201
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Environment Configuration

The `.env` file is already configured. Update if needed:

### 5. Download Required Tools

- **Redis:** Download [Redis for Windows](https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip) and extract to project root
- **MailHog:** Download [MailHog](https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_windows_amd64.exe) and rename to `mailhog.exe`

## Running the Application

**You need to run 5 servers in separate terminals:**

### Terminal 1: Redis Server

```bash
.\Redis-x64-3.0.504\redis-server.exe
```

### Terminal 2: MailHog (Email Testing)

```bash
.\mailhog.exe
```

### Terminal 3: Flask Backend API

```bash
cd backend
python run.py
```

### Terminal 4: Vue.js Frontend

```bash
cd frontend
npm run dev
```

### Terminal 5: Celery Worker (Background Jobs)

```bash
cd backend && python -m celery -A app.celery_worker worker --loglevel=info --pool=solo
```

### Optional: Celery Beat (Scheduled Jobs)

```bash
cd backend
python -m celery -A app.celery_worker beat --loglevel=info
```

## Access Points

- **Frontend:** http://localhost:8080
- **Backend API:** http://localhost:5000
- **MailHog:** http://localhost:8025
- **Redis:** localhost:6379

## Default Login Credentials

**Admin:**

- Email: admin@quizmaster.com
- Password: Admin@123

**Test Student:**

- Email: dummy@example.com
- Password: dummy123

## Testing Instructions

### 1. Basic Application Test

1. Start all 5 servers as described above
2. Open http://localhost:8080
3. Login with admin credentials
4. Create subjects, chapters, quizzes, and questions
5. Login as student and attempt quizzes

### 2. Background Jobs Test

```bash
cd backend

# Test daily reminders
python -c "from app.tasks import send_daily_reminders; print(send_daily_reminders())"

# Test monthly reports
python -c "from app.tasks import generate_monthly_reports; print(generate_monthly_reports())"

# Test CSV export
python -c "from app.tasks import export_user_csv; print(export_user_csv(None, 2))"
```

### 3. Email Testing

- All emails are captured by MailHog
- View emails at http://localhost:8025
- No real emails are sent during testing

## Core Features

- User registration and authentication
- Admin dashboard with full CRUD operations
- Interactive quiz system with timer
- Automatic background jobs (reminders, reports, exports)
- Redis caching for performance
- Responsive Bootstrap UI

## Troubleshooting

**Redis Connection Error:**

- Ensure Redis server is running on port 6379

**Celery Worker Issues:**

- Use `--pool=solo` flag on Windows
- Start Redis before Celery

**Email Not Working:**

- Ensure MailHog is running on port 1025
- Check MailHog web UI at http://localhost:8025

**Frontend Issues:**

- Run `npm install` if dependencies missing
- Check port 8080 availability

## MAD II Requirements ✅

✅ Flask API Backend
✅ Vue.js Frontend
✅ SQLite Database
✅ Redis Caching
✅ Celery Background Jobs
✅ Daily Reminders via Email
✅ Monthly HTML Reports
✅ CSV Export Functionality
✅ Bootstrap Styling
✅ Chart.js Integration
✅ Responsive Design
✅ Form Validation

---

**Quiz Master V2 - Complete MAD II Project Implementation**
