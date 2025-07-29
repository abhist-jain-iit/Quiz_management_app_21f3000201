# Quiz Master V2 - Production Ready MAD II Project

A comprehensive quiz management application built with Flask API backend, Vue.js frontend, featuring automated background jobs, Redis caching, and production-ready deployment.

## Features

- User Management: Registration, authentication, and role-based access control
- Admin Dashboard: Complete management of subjects, chapters, quizzes, and questions
- User Dashboard: Interactive quiz taking with real-time timer and performance tracking
- Automated Background Jobs: Daily reminders, monthly reports, and file cleanup
- Performance Optimization: Redis caching and optimized database queries
- Data Export: CSV export functionality for users and admins
- Real-time Analytics: Charts and statistics for performance monitoring

## Technology Stack

### Backend

- Flask - Python web framework
- SQLAlchemy - Database ORM
- Flask-JWT-Extended - Authentication
- Redis - Caching and message broker
- Celery - Background task processing
- SQLite - Database
- MailHog - Email testing (development)

### Frontend

- Vue.js 3 - Progressive JavaScript framework
- Bootstrap 5 - CSS framework
- Chart.js - Data visualization
- Axios - HTTP client

## Prerequisites

- Python 3.8+
- Node.js 16+
- Redis Server
- Git

## Project Structure

```
Quiz_management_app_21f3000201/
├── backend/                    # Flask API
│   ├── app/                   # Application modules
│   │   ├── api/              # API endpoints
│   │   ├── models/           # Database models
│   │   ├── tasks.py          # Celery tasks
│   │   └── ...
│   ├── .env.example          # Environment template
│   ├── requirements.txt      # Python dependencies
│   └── run.py               # Application entry point
├── frontend/                  # Vue.js UI
│   ├── src/                  # Source code
│   │   ├── components/       # Vue components
│   │   ├── views/           # Page views
│   │   └── services/        # API services
│   ├── package.json         # Node dependencies
│   └── vite.config.js       # Build configuration
├── Redis-x64-3.0.504/        # Redis server files
├── .gitignore               # Git ignore rules
└── README.md               # This file
```

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

### Step 3: Configure Environment

Edit the `.env` file in the backend directory:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///quiz_master.db

# Redis Configuration
REDIS_URL=redis://localhost:6379/1
CACHE_REDIS_URL=redis://localhost:6379/1
CACHE_DEFAULT_TIMEOUT=300

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Configuration (MailHog for development)
SMTP_SERVER=localhost
SMTP_PORT=1025
SMTP_USERNAME=
SMTP_PASSWORD=
MAIL_DEFAULT_SENDER=noreply@quizmaster.com

# Google Chat Webhook (Optional)
GOOGLE_CHAT_WEBHOOK=

# Application Settings
CREATE_DEFAULT_DATA=True
```

## Running the Application

### Method 1: Using VSCode (Recommended)

Open 5 terminals in VSCode (Ctrl + Shift + `) and run each command in a separate terminal:

**Terminal 1 - Redis Server:**

```bash
.\Redis-x64-3.0.504\redis-server.exe
```

**Terminal 2 - Flask API:**

```bash
cd backend
python run.py
```

**Terminal 3 - Vue.js Frontend:**

```bash
cd frontend
npm run dev
```

**Terminal 4 - Celery Worker:**

```bash
cd backend
python -m celery -A app.celery_worker worker --loglevel=info --pool=solo
```

**Terminal 5 - Celery Beat Scheduler:**

```bash
cd backend
python -m celery -A app.celery_worker beat --loglevel=info
```

### Method 2: Using MailHog for Email Testing (Optional)

Download and run MailHog to test email functionality:

**Terminal 6 - MailHog (Optional):**

```bash
# Download MailHog from https://github.com/mailhog/MailHog/releases
# Run the executable
mailhog.exe
```

### Method 3: Quick Start (All in One)

For quick testing, you can run all servers manually in separate command prompts.

## Access Points

- Frontend Application: http://localhost:8080
- Backend API: http://localhost:5000
- MailHog Web UI: http://localhost:8025 (if running)

## Default Credentials

Admin Account:

- Email: admin@quizmaster.com
- Password: Admin@123

## Testing the Application

### 1. Frontend Testing

1. **User Registration**:

   - Go to http://localhost:8080
   - Click "Register" and create a new user account
   - Verify email validation and form submission

2. **User Dashboard**:

   - Login with user credentials
   - Check dashboard statistics and charts
   - Attempt available quizzes
   - Verify timer functionality and score calculation

3. **Admin Dashboard**:
   - Login with admin credentials
   - Verify all statistics are displaying correctly
   - Test CRUD operations for subjects, chapters, quizzes, and questions
   - Check user management functionality

### 2. Backend API Testing

Test API endpoints using tools like Postman or curl:

```bash
# Test authentication
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@quizmaster.com","password":"Admin@123"}'

# Test dashboard (replace TOKEN with actual JWT token)
curl -X GET http://localhost:5000/api/dashboard \
  -H "Authorization: Bearer TOKEN"
```

### 3. Background Jobs Testing

#### Daily Reminders

- **Automatic**: Runs daily at 6 PM
- **Manual Test**: Check Celery worker logs for task execution
- **Verification**: Check MailHog for sent emails

#### Monthly Reports

- **Automatic**: Runs on 1st of each month at 9 AM
- **Manual Test**: Monitor Celery beat scheduler logs
- **Verification**: Check MailHog for report emails

#### CSV Export

1. Login as admin or user
2. Click "Export Data" button
3. Monitor Celery worker for task processing
4. Check `backend/exports/` folder for generated CSV files
5. Verify email notification in MailHog

### 4. Redis Testing

```bash
# Connect to Redis CLI (in Redis directory)
.\Redis-x64-3.0.504\redis-cli.exe

# Check cached data
KEYS *
GET dashboard_1_True
```

### 5. Database Testing

```bash
# Check database file
cd backend/instance
# Use SQLite browser or command line to inspect quiz_master.db
```

## Troubleshooting

### Common Issues

1. **Redis Connection Error**:

   - Ensure Redis server is running first
   - Check port 6379 is not blocked

2. **Celery Worker Not Starting**:

   - Use `--pool=solo` flag on Windows
   - Ensure Redis is running before starting Celery

3. **Frontend Not Loading**:

   - Check if port 8080 is available
   - Run `npm install` if dependencies are missing

4. **Database Errors**:

   - Delete `backend/instance/quiz_master.db` to reset
   - Restart backend to recreate with default data

5. **Email Not Sending**:
   - Ensure MailHog is running on port 1025
   - Check SMTP configuration in .env file

## Features Overview

### Admin Features

- **Subject Management**: Create, edit, delete subjects
- **Chapter Management**: Organize chapters under subjects
- **Quiz Management**: Create timed quizzes with multiple questions
- **Question Management**: Add MCQ questions with correct answers
- **User Management**: View and manage registered users
- **Analytics Dashboard**: Real-time charts and statistics
- **Data Export**: CSV export of user performance data

### User Features

- **Registration & Authentication**: Secure user accounts
- **Quiz Taking**: Interactive quiz interface with timer
- **Score Tracking**: Personal performance history
- **Dashboard Analytics**: Personal statistics and progress charts
- **CSV Export**: Export personal quiz history

### Automated Background Jobs

- **Daily Reminders**: Email notifications for inactive users
- **Monthly Reports**: Comprehensive performance reports
- **File Cleanup**: Automatic removal of old export files
- **Cache Management**: Redis-based performance optimization

## Production Deployment

### Environment Variables for Production

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-production-jwt-key
DATABASE_URL=your-production-database-url
REDIS_URL=your-production-redis-url
SMTP_SERVER=your-smtp-server
SMTP_PORT=587
SMTP_USERNAME=your-email@domain.com
SMTP_PASSWORD=your-email-password
```

### Security Considerations

1. Change default admin password
2. Use strong secret keys
3. Enable HTTPS in production
4. Configure proper CORS settings
5. Use environment-specific configurations

## API Documentation

### Authentication Endpoints

- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - User logout

### Admin Endpoints

- `GET/POST /api/subjects` - Manage subjects
- `GET/POST /api/chapters` - Manage chapters
- `GET/POST /api/quizzes` - Manage quizzes
- `GET/POST /api/questions` - Manage questions
- `GET/POST /api/users` - Manage users

### User Endpoints

- `GET /api/dashboard` - Get dashboard data
- `POST /api/quiz-attempt/<quiz_id>` - Submit quiz attempt
- `GET /api/scores` - Get user scores

### Background Job Endpoints

- `POST /api/jobs/export/user` - Export user CSV
- `POST /api/jobs/export/admin` - Export admin CSV
- `GET /api/jobs/status/<task_id>` - Get job status
- `GET /api/jobs/download/<filename>` - Download CSV file

## MAD II Project Requirements Compliance

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

**Quiz Master V2 - Complete MAD II Project with Production-Ready Features**
