from .celery_worker import celery
import csv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import requests
import json

# Email configuration (you should set these in environment variables)
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', 'your-email@gmail.com')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'your-app-password')

# Google Chat Webhook URL (optional)
GOOGLE_CHAT_WEBHOOK = os.environ.get('GOOGLE_CHAT_WEBHOOK', '')

def send_email(to_email, subject, body, attachment_path=None):
    """Send email with optional attachment"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(attachment_path)}'
                )
                msg.attach(part)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")
        return False

def send_google_chat_message(message):
    """Send message to Google Chat via webhook"""
    if not GOOGLE_CHAT_WEBHOOK:
        print("Google Chat webhook not configured")
        return False

    try:
        payload = {'text': message}
        response = requests.post(GOOGLE_CHAT_WEBHOOK, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send Google Chat message: {str(e)}")
        return False

# Daily reminder task
@celery.task
def send_daily_reminders():
    from app import create_app
    from app.models import User, Score, Quiz

    app = create_app()
    with app.app_context():
        # Find users who haven't visited in the last day
        users = User.query.filter_by(is_active=True).all()
        reminder_count = 0

        for user in users:
            if user.is_admin():
                continue  # Skip admin users

            # Check last quiz attempt
            last_score = Score.query.filter_by(user_id=user.id).order_by(Score.time_stamp_of_attempt.desc()).first()
            should_send_reminder = False

            if not last_score:
                # User has never taken a quiz
                should_send_reminder = True
                reason = "You haven't taken any quizzes yet!"
            elif (datetime.utcnow() - last_score.time_stamp_of_attempt).days >= 1:
                # User hasn't taken a quiz in the last day
                should_send_reminder = True
                reason = "It's been a while since your last quiz attempt!"

            # Check for new quizzes
            if last_score:
                new_quizzes = Quiz.query.filter(
                    Quiz.created_at > last_score.time_stamp_of_attempt,
                    Quiz.is_active == True
                ).count()
                if new_quizzes > 0:
                    should_send_reminder = True
                    reason = f"There are {new_quizzes} new quizzes available!"

            if should_send_reminder:
                # Send email reminder
                subject = "Quiz Master - Daily Reminder"
                body = f"""
                <html>
                <body>
                    <h2>Hello {user.full_name}!</h2>
                    <p>{reason}</p>
                    <p>Visit Quiz Master to continue your learning journey:</p>
                    <ul>
                        <li>Take new quizzes</li>
                        <li>Improve your scores</li>
                        <li>Track your progress</li>
                    </ul>
                    <p><a href="http://localhost:5000" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Visit Quiz Master</a></p>
                    <p>Happy learning!</p>
                    <p>The Quiz Master Team</p>
                </body>
                </html>
                """

                if send_email(user.email, subject, body):
                    reminder_count += 1
                    print(f"Reminder sent to {user.email}")

                # Send Google Chat message (if configured)
                chat_message = f"📚 Reminder for {user.full_name}: {reason} Visit Quiz Master to continue learning!"
                send_google_chat_message(chat_message)

        print(f"Daily reminders task completed. Sent {reminder_count} reminders.")

# Monthly report task
@celery.task
def send_monthly_reports():
    from app import create_app
    from app.models import User, Score, Quiz, Subject, Chapter
    from sqlalchemy import func

    app = create_app()
    with app.app_context():
        users = User.query.filter_by(is_active=True).all()
        report_count = 0

        for user in users:
            if user.is_admin():
                continue  # Skip admin users

            # Calculate date range for the previous month
            today = datetime.utcnow()
            if today.month == 1:
                month_start = datetime(today.year - 1, 12, 1)
                month_end = datetime(today.year, 1, 1)
                month_name = "December"
                year = today.year - 1
            else:
                month_start = datetime(today.year, today.month - 1, 1)
                month_end = datetime(today.year, today.month, 1)
                month_name = month_start.strftime("%B")
                year = today.year

            # Gather monthly stats
            scores = Score.query.filter(
                Score.user_id == user.id,
                Score.time_stamp_of_attempt >= month_start,
                Score.time_stamp_of_attempt < month_end
            ).all()

            if not scores:
                continue  # Skip users with no activity

            total_quizzes = len(scores)
            total_scored = sum(s.total_scored for s in scores)
            total_questions = sum(s.total_questions for s in scores)
            avg_score = total_scored / total_questions * 100 if total_questions > 0 else 0

            # Get best and worst performance
            best_score = max(scores, key=lambda s: s.total_scored / s.total_questions * 100 if s.total_questions > 0 else 0)
            worst_score = min(scores, key=lambda s: s.total_scored / s.total_questions * 100 if s.total_questions > 0 else 0)

            # Get quiz details
            quiz_details = []
            for score in scores:
                quiz = Quiz.query.get(score.quiz_id)
                if quiz:
                    chapter = Chapter.query.get(quiz.chapter_id)
                    subject = Subject.query.get(chapter.subject_id) if chapter else None

                    percentage = (score.total_scored / score.total_questions * 100) if score.total_questions > 0 else 0
                    quiz_details.append({
                        'quiz_title': quiz.title,
                        'subject': subject.name if subject else 'Unknown',
                        'chapter': chapter.name if chapter else 'Unknown',
                        'score': f"{score.total_scored}/{score.total_questions}",
                        'percentage': f"{percentage:.1f}%",
                        'date': score.time_stamp_of_attempt.strftime("%Y-%m-%d")
                    })

            # Calculate ranking (simplified - based on average score)
            all_user_scores = Score.query.filter(
                Score.time_stamp_of_attempt >= month_start,
                Score.time_stamp_of_attempt < month_end
            ).all()

            user_averages = {}
            for score in all_user_scores:
                if score.user_id not in user_averages:
                    user_averages[score.user_id] = {'total_scored': 0, 'total_questions': 0}
                user_averages[score.user_id]['total_scored'] += score.total_scored
                user_averages[score.user_id]['total_questions'] += score.total_questions

            user_rankings = []
            for uid, data in user_averages.items():
                if data['total_questions'] > 0:
                    avg = data['total_scored'] / data['total_questions'] * 100
                    user_rankings.append((uid, avg))

            user_rankings.sort(key=lambda x: x[1], reverse=True)
            user_rank = next((i + 1 for i, (uid, _) in enumerate(user_rankings) if uid == user.id), len(user_rankings))

            # Generate HTML report
            subject = f"Quiz Master - Monthly Report for {month_name} {year}"
            body = generate_monthly_report_html(
                user, month_name, year, total_quizzes, avg_score,
                best_score, worst_score, quiz_details, user_rank, len(user_rankings)
            )

            if send_email(user.email, subject, body):
                report_count += 1
                print(f"Monthly report sent to {user.email}")

        print(f"Monthly reports task completed. Sent {report_count} reports.")

def generate_monthly_report_html(user, month, year, total_quizzes, avg_score, best_score, worst_score, quiz_details, rank, total_users):
    """Generate HTML content for monthly report"""
    best_percentage = (best_score.total_scored / best_score.total_questions * 100) if best_score.total_questions > 0 else 0
    worst_percentage = (worst_score.total_scored / worst_score.total_questions * 100) if worst_score.total_questions > 0 else 0

    quiz_rows = ""
    for quiz in quiz_details:
        quiz_rows += f"""
        <tr>
            <td>{quiz['quiz_title']}</td>
            <td>{quiz['subject']}</td>
            <td>{quiz['chapter']}</td>
            <td>{quiz['score']}</td>
            <td>{quiz['percentage']}</td>
            <td>{quiz['date']}</td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
            .summary {{ background-color: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 5px; }}
            .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .stat-box {{ text-align: center; padding: 15px; background-color: white; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #007bff; color: white; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Monthly Quiz Report</h1>
            <h2>{month} {year}</h2>
        </div>

        <div class="summary">
            <h3>Hello {user.full_name}!</h3>
            <p>Here's your quiz performance summary for {month} {year}:</p>
        </div>

        <div class="stats">
            <div class="stat-box">
                <h3>{total_quizzes}</h3>
                <p>Quizzes Taken</p>
            </div>
            <div class="stat-box">
                <h3>{avg_score:.1f}%</h3>
                <p>Average Score</p>
            </div>
            <div class="stat-box">
                <h3>{best_percentage:.1f}%</h3>
                <p>Best Score</p>
            </div>
            <div class="stat-box">
                <h3>#{rank}</h3>
                <p>Rank (out of {total_users})</p>
            </div>
        </div>

        <h3>📈 Performance Highlights</h3>
        <ul>
            <li><strong>Best Performance:</strong> {best_percentage:.1f}% ({best_score.total_scored}/{best_score.total_questions})</li>
            <li><strong>Lowest Score:</strong> {worst_percentage:.1f}% ({worst_score.total_scored}/{worst_score.total_questions})</li>
            <li><strong>Your Ranking:</strong> #{rank} out of {total_users} active users</li>
        </ul>

        <h3>📋 Detailed Quiz History</h3>
        <table>
            <thead>
                <tr>
                    <th>Quiz Title</th>
                    <th>Subject</th>
                    <th>Chapter</th>
                    <th>Score</th>
                    <th>Percentage</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                {quiz_rows}
            </tbody>
        </table>

        <div class="footer">
            <p>Keep up the great work! 🎉</p>
            <p><a href="http://localhost:5000" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Continue Learning</a></p>
            <p>Generated by Quiz Master V2</p>
        </div>
    </body>
    </html>
    """

# Example: User CSV export
@celery.task
def export_user_csv(user_id):
    from app import create_app
    from app.models import User, Quiz, Score

    app = create_app()
    with app.app_context():
        user = User.query.get(user_id)
        scores = Score.query.filter_by(user_id=user_id).all()
        filename = f'user_{user_id}_quizzes.csv'
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['quiz_id', 'chapter_id', 'date_of_quiz', 'score', 'remarks'])
            for score in scores:
                quiz = Quiz.query.get(score.quiz_id)
                writer.writerow([
                    score.quiz_id,
                    quiz.chapter_id if quiz else '',
                    quiz.date_of_quiz if quiz else '',
                    score.total_scored,
                    quiz.remarks if quiz else ''
                ])
        print(f"Exported CSV for user {user.email} to {filename}")

# Example: Admin CSV export
@celery.task
def export_admin_csv():
    from app import create_app
    from app.models import User, Score

    app = create_app()
    with app.app_context():
        users = User.query.all()
        filename = 'admin_all_users_quizzes.csv'
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['user_id', 'quizzes_taken', 'average_score'])
            for user in users:
                scores = Score.query.filter_by(user_id=user.id).all()
                quizzes_taken = len(scores)
                avg_score = sum(s.total_scored for s in scores) / quizzes_taken if quizzes_taken else 0
                writer.writerow([user.id, quizzes_taken, avg_score])
        print(f"Exported admin CSV to {filename}")