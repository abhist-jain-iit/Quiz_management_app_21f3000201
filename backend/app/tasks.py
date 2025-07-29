from celery import current_task
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
import logging

logger = logging.getLogger(__name__)

def send_email(to_email, subject, body, attachment_path=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@quizmaster.com')
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
                msg.attach(part)

        smtp_server = os.environ.get('SMTP_SERVER', 'localhost')
        smtp_port = int(os.environ.get('SMTP_PORT', '1025'))
        smtp_username = os.environ.get('SMTP_USERNAME', '')
        smtp_password = os.environ.get('SMTP_PASSWORD', '')

        logger.info(f"Sending email to {to_email} via {smtp_server}:{smtp_port}")

        server = smtplib.SMTP(smtp_server, smtp_port)
        if smtp_username and smtp_password:
            server.starttls()
            server.login(smtp_username, smtp_password)

        server.sendmail(msg['From'], to_email, msg.as_string())
        server.quit()
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Email send failed to {to_email}: {e}")
        return False

def send_webhook_notification(message):
    webhook_url = os.environ.get('GOOGLE_CHAT_WEBHOOK')
    if not webhook_url:
        return False
    try:
        response = requests.post(webhook_url, json={'text': message})
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Webhook send failed: {e}")
        return False
@celery.task(bind=True)
def send_daily_reminders(self):
    try:
        from app import create_app
        from app.models import User, Score, Quiz

        app = create_app()
        with app.app_context():
            users = User.query.filter_by(is_active=True).all()
            reminder_count = 0

            for user in users:
                if user.is_admin():
                    continue

                # Send reminder to all active non-admin users
                last_score = Score.query.filter_by(user_id=user.id).order_by(Score.time_stamp_of_attempt.desc()).first()

                if not last_score:
                    reason = "Start your learning journey with available quizzes!"
                else:
                    days_since = (datetime.utcnow() - last_score.time_stamp_of_attempt).days
                    if days_since >= 1:
                        reason = f"It's been {days_since} days since your last quiz. Keep learning!"
                    else:
                        reason = "Continue your learning momentum with more quizzes!"

                available_quizzes = Quiz.query.filter_by(is_active=True).count()
                if available_quizzes > 0:
                    reason += f" {available_quizzes} quizzes are waiting for you."

                logger.info(f"Sending reminder to {user.email}: {reason}")

                if send_email_reminder(user, reason):
                    reminder_count += 1
                    logger.info(f"Reminder sent successfully to {user.email}")
                else:
                    logger.error(f"Failed to send reminder to {user.email}")

                send_webhook_notification(f"Learning reminder for {user.full_name}: {reason}")

            logger.info(f"Daily reminders sent to {reminder_count} users")
            return {'status': 'SUCCESS', 'reminders_sent': reminder_count}

    except Exception as e:
        logger.error(f"Daily reminders failed: {e}")
        return {'status': 'FAILURE', 'error': str(e)}

@celery.task(bind=True)
def generate_monthly_reports(self):
    try:
        from app import create_app
        from app.models import User, Score, Quiz, Chapter, Subject
        from calendar import monthrange

        app = create_app()
        with app.app_context():
            users = User.query.filter_by(is_active=True).all()
            report_count = 0

            today = datetime.utcnow()
            if today.month == 1:
                month_start = datetime(today.year - 1, 12, 1)
                month_end = datetime(today.year - 1, 12, monthrange(today.year - 1, 12)[1], 23, 59, 59)
                month_name = "December"
                year = today.year - 1
            else:
                month_start = datetime(today.year, today.month - 1, 1)
                month_end = datetime(today.year, today.month - 1, monthrange(today.year, today.month - 1)[1], 23, 59, 59)
                month_name = month_start.strftime("%B")
                year = today.year

            for user in users:
                if user.is_admin():
                    continue

                scores = Score.query.filter(
                    Score.user_id == user.id,
                    Score.time_stamp_of_attempt >= month_start,
                    Score.time_stamp_of_attempt <= month_end
                ).all()

                if not scores:
                    continue

                total_attempts = len(scores)
                total_percentage = sum((s.total_scored / s.total_questions * 100) for s in scores if s.total_questions > 0)
                avg_percentage = total_percentage / total_attempts if total_attempts > 0 else 0

                html_report = generate_monthly_report_html(user, month_name, year, total_attempts, avg_percentage, scores)

                if send_email(user.email, f"Monthly Report - {month_name} {year}", html_report):
                    report_count += 1

            logger.info(f"Monthly reports sent to {report_count} users")
            return {'status': 'SUCCESS', 'reports_sent': report_count, 'month': f"{month_name} {year}"}

    except Exception as e:
        logger.error(f"Monthly reports failed: {e}")
        return {'status': 'FAILURE', 'error': str(e)}

def generate_monthly_report_html(user, month, year, total_quizzes, avg_score, scores):
    best_score = max(scores, key=lambda s: s.total_scored / s.total_questions if s.total_questions > 0 else 0)
    best_percentage = (best_score.total_scored / best_score.total_questions * 100) if best_score.total_questions > 0 else 0

    quiz_rows = ""
    for score in scores:
        quiz = score.quiz
        percentage = (score.total_scored / score.total_questions * 100) if score.total_questions > 0 else 0
        quiz_rows += f"""
        <tr>
            <td>{quiz.title if quiz else 'Unknown'}</td>
            <td>{quiz.chapter.subject.name if quiz and quiz.chapter and quiz.chapter.subject else 'Unknown'}</td>
            <td>{quiz.chapter.name if quiz and quiz.chapter else 'Unknown'}</td>
            <td>{score.total_scored}/{score.total_questions}</td>
            <td>{percentage:.1f}%</td>
            <td>{score.time_stamp_of_attempt.strftime('%Y-%m-%d')}</td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; }}
            .header {{ background: linear-gradient(135deg, #007bff, #0056b3); color: white; padding: 30px; text-align: center; }}
            .summary {{ padding: 20px; background-color: #f8f9fa; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 8px; text-align: center; }}
            .stat-number {{ font-size: 24px; font-weight: bold; color: #007bff; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #007bff; color: white; }}
            .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Monthly Quiz Report</h1>
                <h2>{month} {year}</h2>
            </div>
            <div class="summary">
                <h3>Hello {user.full_name}!</h3>
                <p>Your quiz performance summary for {month} {year}:</p>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{total_quizzes}</div>
                        <div>Quizzes Completed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{avg_score:.1f}%</div>
                        <div>Average Score</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{best_percentage:.1f}%</div>
                        <div>Best Score</div>
                    </div>
                </div>
            </div>
            <div style="padding: 20px;">
                <h3>Quiz Details</h3>
                <table>
                    <thead>
                        <tr><th>Quiz</th><th>Subject</th><th>Chapter</th><th>Score</th><th>Percentage</th><th>Date</th></tr>
                    </thead>
                    <tbody>{quiz_rows}</tbody>
                </table>
            </div>
            <div class="footer">
                <p>Keep learning! <a href="http://localhost:8080">Continue your journey</a></p>
            </div>
        </div>
    </body>
    </html>
    """

@celery.task(bind=True)
def export_user_csv(self, user_id):
    try:
        from app import create_app
        from app.models import User, Quiz, Score, Chapter, Subject

        app = create_app()
        with app.app_context():
            user = User.query.get(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")

            os.makedirs('exports', exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'user_{user_id}_quizzes_{timestamp}.csv'
            filepath = os.path.join('exports', filename)

            scores = Score.query.filter_by(user_id=user_id).order_by(Score.time_stamp_of_attempt.desc()).all()

            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Quiz ID', 'Quiz Title', 'Subject', 'Chapter', 'Score', 'Total Questions', 'Percentage', 'Date'])

                for score in scores:
                    quiz = score.quiz
                    percentage = (score.total_scored / score.total_questions * 100) if score.total_questions > 0 else 0

                    writer.writerow([
                        score.quiz_id,
                        quiz.title if quiz else 'Unknown',
                        quiz.chapter.subject.name if quiz and quiz.chapter and quiz.chapter.subject else 'Unknown',
                        quiz.chapter.name if quiz and quiz.chapter else 'Unknown',
                        score.total_scored,
                        score.total_questions,
                        f"{percentage:.1f}%",
                        score.time_stamp_of_attempt.strftime('%Y-%m-%d %H:%M')
                    ])

            send_email(user.email, "CSV Export Ready", f"Your quiz data export is ready: {filename}")
            logger.info(f"CSV exported for user {user.email}")

            return {'status': 'SUCCESS', 'filename': filename, 'total_records': len(scores)}

    except Exception as e:
        logger.error(f"CSV export failed for user {user_id}: {e}")
        raise

@celery.task(bind=True)
def export_admin_csv(self, admin_user_id):
    try:
        from app import create_app
        from app.models import User, Score

        app = create_app()
        with app.app_context():
            admin_user = User.query.get(admin_user_id)
            if not admin_user or not admin_user.is_admin():
                raise ValueError("Admin access required")

            os.makedirs('exports', exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'admin_users_performance_{timestamp}.csv'
            filepath = os.path.join('exports', filename)

            users = User.query.filter(~User.roles.any(name='admin')).all()

            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['User ID', 'Name', 'Email', 'Qualification', 'Total Quizzes', 'Average Score', 'Performance'])

                for user in users:
                    scores = Score.query.filter_by(user_id=user.id).all()
                    quizzes_taken = len(scores)

                    if quizzes_taken > 0:
                        total_percentage = sum((s.total_scored / s.total_questions * 100) for s in scores if s.total_questions > 0)
                        avg_percentage = total_percentage / quizzes_taken

                        if avg_percentage >= 80:
                            rating = "Excellent"
                        elif avg_percentage >= 60:
                            rating = "Good"
                        elif avg_percentage >= 40:
                            rating = "Average"
                        else:
                            rating = "Needs Improvement"
                    else:
                        avg_percentage = 0
                        rating = "No Activity"

                    writer.writerow([
                        user.id,
                        user.full_name,
                        user.email,
                        user.qualification or 'Not specified',
                        quizzes_taken,
                        f"{avg_percentage:.1f}%",
                        rating
                    ])

            send_email(admin_user.email, "Admin CSV Export Ready", f"User performance export ready: {filename}")
            logger.info(f"Admin CSV exported: {filename}")

            return {'status': 'SUCCESS', 'filename': filename, 'total_records': len(users)}

    except Exception as e:
        logger.error(f"Admin CSV export failed: {e}")
        raise

@celery.task(bind=True)
def cleanup_old_results(self):
    try:
        exports_dir = 'exports'
        if os.path.exists(exports_dir):
            cutoff_time = datetime.now() - timedelta(days=7)
            cleaned_files = 0

            for filename in os.listdir(exports_dir):
                file_path = os.path.join(exports_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        cleaned_files += 1

            logger.info(f"Cleaned {cleaned_files} old files")
            return f"Cleanup completed. Removed {cleaned_files} files"

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise

def send_email_reminder(user, reason):
    subject = "Quiz Master - Daily Reminder"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; margin: 20px;">
        <div style="background-color: #007bff; color: white; padding: 20px; text-align: center; border-radius: 5px;">
            <h2>Quiz Master Daily Reminder</h2>
        </div>
        <div style="padding: 20px;">
            <h3>Hello {user.full_name}!</h3>
            <p>{reason}</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:8080" style="background-color: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Start Learning Now
                </a>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(user.email, subject, body)

