# Quiz Master V2 - MAD II Project

A comprehensive quiz management application built with Flask API backend and Vue.js frontend for Modern Application Development II course.

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
│   ├── requirements.txt      # Python dependencies
│   └── run.py               # Application entry point
├── frontend/                 # Vue.js Frontend
│   ├── src/                  # Source files
│   │   ├── components/       # Reusable Vue components
│   │   ├── views/           # Page components
│   │   ├── services/        # API service layer
│   │   ├── router/          # Vue Router configuration
│   │   ├── App.vue          # Root component
│   │   └── main.js          # Application entry point
│   ├── package.json         # Node.js dependencies
│   └── vite.config.js       # Vite build configuration
└── README.md               # Project documentation
```

## Technology Stack

- **Backend**: Flask, SQLAlchemy, JWT, Celery, Redis
- **Frontend**: Vue.js 3, Bootstrap 5, Chart.js
- **Database**: SQLite
- **Caching**: Redis
- **Background Jobs**: Celery

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Redis Server

### Installation

1. **Backend Setup**

   ```bash
   cd backend
   pip install -r requirements.txt
   python run.py
   ```

2. **Frontend Setup** (in new terminal)

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Start Redis** (in new terminal)

   ```bash
   redis-server
   ```

4. **Start Celery Worker** (in new terminal)
   ```bash
   cd backend
   celery -A app.celery_worker worker --loglevel=info
   ```

### Default Admin Credentials

- Username: `admin`
- Password: `Admin@123`

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
