# Quiz Master V2 - MAD II Project

A comprehensive quiz management application built with Flask and Vue.js.

## Project Structure

```
Quiz_management_app_21f3000201/
├── backend/                    # Flask API Backend
│   ├── app/                   # Application package
│   │   ├── api/              # REST API endpoints
│   │   ├── models/           # Database models
│   │   ├── __init__.py       # App factory
│   │   ├── auth.py           # Authentication utilities
│   │   ├── celery_worker.py  # Celery configuration
│   │   ├── config.py         # Configuration settings
│   │   ├── database.py       # Database setup
│   │   └── tasks.py          # Background tasks
│   ├── instance/             # Database files
│   ├── celery_worker.py      # Celery worker entry point
│   ├── requirements.txt      # Python dependencies
│   └── run.py               # Application entry point
├── frontend/                 # Vue.js Frontend
│   ├── js/
│   │   └── app.js           # Vue.js application
│   └── index.html           # Main HTML file
└── .gitignore               # Git ignore rules
```

## Features

### Admin Features
- Subject, Chapter, and Quiz management
- Question creation with multiple choice options
- User management and analytics
- Dashboard with statistics and charts
- Search functionality across all entities
- CSV data export

### User Features
- User registration and authentication
- Interactive quiz taking with timer
- Score tracking and history
- Personal dashboard with performance metrics
- Data export functionality

### Technical Features
- JWT-based authentication
- Role-based access control
- Redis caching for performance
- Celery background jobs for:
  - Daily user reminders
  - Monthly performance reports
  - Asynchronous data export
- RESTful API design
- Responsive web interface

## Quick Start

### Prerequisites
- Python 3.8+
- Redis Server

### Installation

1. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Start Redis server**
   ```bash
   redis-server
   ```

3. **Run the application**
   ```bash
   python run.py
   ```

4. **Open frontend**
   - Open `frontend/index.html` in your browser

### Default Admin Credentials
- Username: `admin`
- Password: `Admin@123`

## Technology Stack

- **Backend**: Flask, SQLAlchemy, JWT, Celery, Redis
- **Frontend**: Vue.js 3, Bootstrap 5, Chart.js
- **Database**: SQLite
- **Caching**: Redis
- **Background Jobs**: Celery

## API Endpoints

- `/api/auth/*` - Authentication
- `/api/subjects/*` - Subject management
- `/api/chapters/*` - Chapter management
- `/api/quizzes/*` - Quiz management
- `/api/questions/*` - Question management
- `/api/scores/*` - Score management
- `/api/dashboard` - Dashboard data
- `/api/users/*` - User management
- `/api/search` - Search functionality
- `/api/export/*` - Data export

## Development

The application follows modern development practices:
- Modular architecture
- Separation of concerns
- RESTful API design
- Responsive UI design
- Error handling and validation
- Performance optimization with caching

---

**Modern Application Development II - IIT Madras BS Degree**
