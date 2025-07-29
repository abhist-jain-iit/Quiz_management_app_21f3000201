# Quiz Master V2 - MAD II Project

## Project Folder Structure

```
Quiz_management_app_21f3000201/
├── backend/                    # Flask API
├── frontend/                   # Vue.js UI
├── Redis/                      # Redis server files
└── README.md
```

## How to Run (Windows VSCode)

### Step 1: Open in VSCode

- Open VSCode
- File → Open Folder → Select `Quiz_management_app_21f3000201`

### Step 2: Install Dependencies

Open VSCode terminal (Ctrl + `) and run:

```bash
# Install backend
cd backend
pip install -r requirements.txt
cd ..

# Install frontend
cd frontend
npm install
cd ..
```

### Step 3: Start Services (Open 5 terminals in VSCode)

**Terminal 1 - Redis:**

```bash
.\Redis\redis-server.exe
```

**Terminal 2 - Backend:**

```bash
cd backend
python run.py
```

**Terminal 3 - Frontend:**

```bash
cd frontend
npm run dev
```

**Terminal 4 - Background Jobs:**

```bash
cd backend
python -m celery -A app.celery_worker worker --loglevel=info --pool=solo
```

**Terminal 5 - Scheduled Tasks:**

```bash
cd backend
python -m celery -A app.celery_worker beat --loglevel=info
```

## Access Application

- **Frontend**: http://localhost:8080
- **Admin Login**: admin / Admin@123

## What You Get

### Admin Features

- Create subjects, chapters, quizzes
- Add multiple choice questions
- View user analytics and charts
- Export data to CSV

### User Features

- Register and take quizzes
- View scores and progress
- Personal dashboard

### Background Jobs

- Daily email reminders
- Monthly performance reports
- CSV export processing

## Technology Stack

- **Backend**: Flask + SQLite + Redis + Celery
- **Frontend**: Vue.js + Bootstrap
- **Jobs**: Automatic emails and reports

## Important Notes

- Keep all 5 terminals running
- Redis must start first
- Default data is auto-created
- CSV files saved in `exports/` folder

---

First, ensure you have these 5 terminals running:

Redis: .\Redis\redis-server.exe
Backend: cd backend && python run.py
Frontend: cd frontend && npm run dev
Celery Worker: cd backend && python -m celery -A app.celery_worker worker --loglevel=info --pool=solo
Celery Beat: cd backend && python -m celery -A app.celery_worker beat --loglevel=info

**MAD II Project - Quiz Master V2 with Redis, Celery & Background Jobs**
