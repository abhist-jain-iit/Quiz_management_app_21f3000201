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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SMTP_SERVER = os.environ.get('SMTP_SERVER', 'localhost')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '1025'))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')

GOOGLE_CHAT_WEBHOOK = os.environ.get('GOOGLE_CHAT_WEBHOOK', '')

def send_email(to_email, subject, body, attachment_path=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME or 'noreply@quizmaster.com'
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
        if SMTP_USERNAME and SMTP_PASSWORD:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(msg['From'], to_email, text)
        server.quit()
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

def send_google_chat_message(message):
    if not GOOGLE_CHAT_WEBHOOK:
        return False

    try:
        payload = {'text': message}
        response = requests.post(GOOGLE_CHAT_WEBHOOK, json=payload)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Failed to send Google Chat message: {str(e)}")
        return False
@celery.task(bind=True)
def send_daily_reminders(self):
    try:
        from app import create_app
        from app.models import User, Score, Quiz

        app = create_app()
        with app.app_context():
            users = User.query.filter_by(is_active=True).all()
            total_users = len(users)
            reminder_count = 0

            for i, user in enumerate(users):
                try:
                    if user.is_admin():
                        continue

                    self.update_state(
                        state='PROGRESS',
                        meta={'current': i + 1, 'total': total_users, 'status': f'Processing user {user.email}'}
                    )

                    last_score = Score.query.filter_by(user_id=user.id).order_by(Score.time_stamp_of_attempt.desc()).first()
                    should_send_reminder = False
                    reason = ""
                    new_quizzes = []

                    if not last_score:
                        # User has never taken a quiz
                        should_send_reminder = True
                        reason = "You haven't taken any quizzes yet! Start your learning journey today."
                    else:
                        days_since_last = (datetime.utcnow() - last_score.time_stamp_of_attempt).days

                        if days_since_last >= 1:
                            # User hasn't taken a quiz in the last day
                            should_send_reminder = True
                            if days_since_last == 1:
                                reason = "It's been a day since your last quiz attempt!"
                            else:
                                reason = f"It's been {days_since_last} days since your last quiz attempt!"

                        # Check for new quizzes since last attempt
                        new_quizzes = Quiz.query.filter(
                            Quiz.created_at > last_score.time_stamp_of_attempt,
                            Quiz.is_active == True
                        ).all()

                        if new_quizzes:
                            should_send_reminder = True
                            if reason:
                                reason += f" Plus, there are {len(new_quizzes)} new quizzes available!"
                            else:
                                reason = f"There are {len(new_quizzes)} new quizzes available!"

                    if should_send_reminder:
                        # Send email reminder
                        if send_email_reminder(user, new_quizzes):
                            reminder_count += 1
                            logger.info(f"Reminder sent to {user.email}")
                        else:
                            error_count += 1
                            logger.warning(f"Failed to send email reminder to {user.email}")

                        # Send webhook notification (if configured)
                        if send_webhook_reminder(user, new_quizzes):
                            logger.info(f"Webhook reminder sent for {user.email}")

                except Exception as e:
                    error_count += 1
                    logger.error(f"Error processing user {user.email}: {e}")
                    continue

            result_message = f"Daily reminders completed. Sent {reminder_count} reminders to {total_users} users."
            if error_count > 0:
                result_message += f" {error_count} errors occurred."

            logger.info(result_message)

            return {
                'status': 'SUCCESS',
                'total_users': total_users,
                'reminders_sent': reminder_count,
                'errors': error_count,
                'message': result_message
            }

    except Exception as e:
        logger.error(f"Daily reminders task failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

# Monthly report task
@celery.task(bind=True)
def generate_monthly_reports(self):
    """Generate and send monthly performance reports to all users"""
    try:
        logger.info("Starting monthly reports generation")

        from app import create_app
        from app.models import User, Score, Quiz, Subject, Chapter
        from sqlalchemy import func
        from calendar import monthrange

        app = create_app()
        with app.app_context():
            # Get active users (excluding admins)
            users = User.query.filter_by(is_active=True).all()
            total_users = len(users)
            report_count = 0
            error_count = 0

            logger.info(f"Generating monthly reports for {total_users} users")

            # Calculate date range for the previous month
            today = datetime.utcnow()
            if today.month == 1:
                month_start = datetime(today.year - 1, 12, 1)
                last_day = monthrange(today.year - 1, 12)[1]
                month_end = datetime(today.year - 1, 12, last_day, 23, 59, 59)
                month_name = "December"
                year = today.year - 1
            else:
                month_start = datetime(today.year, today.month - 1, 1)
                last_day = monthrange(today.year, today.month - 1)[1]
                month_end = datetime(today.year, today.month - 1, last_day, 23, 59, 59)
                month_name = month_start.strftime("%B")
                year = today.year

            logger.info(f"Generating reports for {month_name} {year} ({month_start.date()} to {month_end.date()})")

            for i, user in enumerate(users):
                try:
                    if user.is_admin():
                        continue  # Skip admin users

                    # Update task progress
                    progress = int((i + 1) / total_users * 100)
                    self.update_state(
                        state='PROGRESS',
                        meta={'current': i + 1, 'total': total_users, 'status': f'Generating report for {user.email}'}
                    )

                    # Get user's monthly data
                    report_data = generate_user_monthly_data(user, month_start, month_end)

                    # Skip users with no activity
                    if report_data['total_attempts'] == 0:
                        logger.info(f"Skipping {user.email} - no activity in {month_name}")
                        continue

                    # Generate HTML report
                    html_report = generate_html_report(user, report_data, month_start)

                    # Send report via email
                    if send_monthly_report_email(user, html_report, month_start):
                        report_count += 1
                        logger.info(f"Monthly report sent to {user.email}")
                    else:
                        error_count += 1
                        logger.warning(f"Failed to send monthly report to {user.email}")

                except Exception as e:
                    error_count += 1
                    logger.error(f"Error generating report for user {user.email}: {e}")
                    continue

            result_message = f"Monthly reports completed. Sent {report_count} reports to {total_users} users."
            if error_count > 0:
                result_message += f" {error_count} errors occurred."

            logger.info(result_message)

            return {
                'status': 'SUCCESS',
                'total_users': total_users,
                'reports_sent': report_count,
                'errors': error_count,
                'month': f"{month_name} {year}",
                'message': result_message
            }

    except Exception as e:
        logger.error(f"Monthly reports task failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

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
            <h1>Monthly Quiz Report</h1>
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

        <h3>Performance Highlights</h3>
        <ul>
            <li><strong>Best Performance:</strong> {best_percentage:.1f}% ({best_score.total_scored}/{best_score.total_questions})</li>
            <li><strong>Lowest Score:</strong> {worst_percentage:.1f}% ({worst_score.total_scored}/{worst_score.total_questions})</li>
            <li><strong>Your Ranking:</strong> #{rank} out of {total_users} active users</li>
        </ul>

        <h3>Detailed Quiz History</h3>
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
            <p>Keep up the great work!</p>
            <p><a href="http://localhost:5000" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Continue Learning</a></p>
            <p>Generated by Quiz Master V2</p>
        </div>
    </body>
    </html>
    """

# User CSV export with progress tracking
@celery.task(bind=True)
def export_user_csv(self, user_id):
    """Export user quiz data to CSV file"""
    try:
        from app import create_app
        from app.models import User, Quiz, Score, Chapter, Subject

        # Update task progress
        self.update_state(state='PROGRESS', meta={'current': 0, 'total': 100, 'status': 'Starting export...'})

        app = create_app()
        with app.app_context():
            user = User.query.get(user_id)
            if not user:
                raise ValueError(f"User with ID {user_id} not found")

            # Create exports directory if it doesn't exist
            exports_dir = os.path.join(os.getcwd(), 'exports')
            os.makedirs(exports_dir, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'user_{user_id}_quizzes_{timestamp}.csv'
            filepath = os.path.join(exports_dir, filename)

            self.update_state(state='PROGRESS', meta={'current': 20, 'total': 100, 'status': 'Fetching user data...'})

            scores = Score.query.filter_by(user_id=user_id).order_by(Score.time_stamp_of_attempt.desc()).all()
            total_scores = len(scores)

            self.update_state(state='PROGRESS', meta={'current': 40, 'total': 100, 'status': f'Processing {total_scores} quiz attempts...'})

            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Enhanced CSV headers
                writer.writerow([
                    'Quiz ID', 'Quiz Title', 'Subject', 'Chapter', 'Date of Quiz',
                    'Attempt Date', 'Score', 'Total Questions', 'Percentage',
                    'Time Taken', 'Remarks'
                ])

                for i, score in enumerate(scores):
                    quiz = Quiz.query.get(score.quiz_id)
                    chapter = Chapter.query.get(quiz.chapter_id) if quiz else None
                    subject = Subject.query.get(chapter.subject_id) if chapter else None

                    # Calculate percentage
                    percentage = (score.total_scored / score.total_questions * 100) if score.total_questions > 0 else 0

                    writer.writerow([
                        score.quiz_id,
                        quiz.title if quiz else 'Unknown Quiz',
                        subject.name if subject else 'Unknown Subject',
                        chapter.name if chapter else 'Unknown Chapter',
                        quiz.date_of_quiz.strftime('%Y-%m-%d') if quiz and quiz.date_of_quiz else '',
                        score.time_stamp_of_attempt.strftime('%Y-%m-%d %H:%M:%S'),
                        score.total_scored,
                        score.total_questions,
                        f"{percentage:.2f}%",
                        score.time_taken or 'N/A',
                        quiz.remarks if quiz else ''
                    ])

                    # Update progress
                    progress = 40 + int((i + 1) / total_scores * 40)
                    self.update_state(state='PROGRESS', meta={'current': progress, 'total': 100, 'status': f'Processed {i + 1}/{total_scores} records'})

            self.update_state(state='PROGRESS', meta={'current': 90, 'total': 100, 'status': 'Sending notification...'})

            # Send completion email
            if send_csv_export_email(user, filepath, filename):
                logger.info(f"CSV export notification sent to {user.email}")

            logger.info(f"Exported CSV for user {user.email} to {filepath}")

            return {
                'status': 'SUCCESS',
                'filename': filename,
                'filepath': filepath,
                'total_records': total_scores,
                'message': f'Successfully exported {total_scores} quiz attempts to CSV'
            }

    except Exception as e:
        logger.error(f"CSV export failed for user {user_id}: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

# Admin CSV export with progress tracking
@celery.task(bind=True)
def export_admin_csv(self, admin_user_id):
    """Export all users quiz data to CSV file (Admin only)"""
    try:
        from app import create_app
        from app.models import User, Score, Quiz, Chapter, Subject
        from sqlalchemy import func

        # Update task progress
        self.update_state(state='PROGRESS', meta={'current': 0, 'total': 100, 'status': 'Starting admin export...'})

        app = create_app()
        with app.app_context():
            admin_user = User.query.get(admin_user_id)
            if not admin_user or not admin_user.is_admin():
                raise ValueError("Only admin users can perform this export")

            # Create exports directory if it doesn't exist
            exports_dir = os.path.join(os.getcwd(), 'exports')
            os.makedirs(exports_dir, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'admin_all_users_performance_{timestamp}.csv'
            filepath = os.path.join(exports_dir, filename)

            self.update_state(state='PROGRESS', meta={'current': 20, 'total': 100, 'status': 'Fetching user data...'})

            # Get all users (excluding admin)
            users = User.query.filter(~User.roles.any(name='admin')).all()
            total_users = len(users)

            self.update_state(state='PROGRESS', meta={'current': 40, 'total': 100, 'status': f'Processing {total_users} users...'})

            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Enhanced CSV headers for admin export
                writer.writerow([
                    'User ID', 'Full Name', 'Email', 'Qualification', 'Date of Birth',
                    'Member Since', 'Total Quizzes Taken', 'Average Score', 'Average Percentage',
                    'Best Score', 'Best Percentage', 'Total Subjects Attempted',
                    'Last Quiz Date', 'Performance Rating'
                ])

                for i, user in enumerate(users):
                    scores = Score.query.filter_by(user_id=user.id).all()
                    quizzes_taken = len(scores)

                    if quizzes_taken > 0:
                        # Calculate statistics
                        total_scored = sum(s.total_scored for s in scores)
                        total_questions = sum(s.total_questions for s in scores)
                        avg_score = total_scored / quizzes_taken
                        avg_percentage = (total_scored / total_questions * 100) if total_questions > 0 else 0

                        # Find best performance
                        best_score = max(scores, key=lambda s: s.total_scored)
                        best_percentage = (best_score.total_scored / best_score.total_questions * 100) if best_score.total_questions > 0 else 0

                        # Get unique subjects attempted
                        attempted_subjects = set()
                        for score in scores:
                            quiz = Quiz.query.get(score.quiz_id)
                            if quiz and quiz.chapter:
                                attempted_subjects.add(quiz.chapter.subject_id)

                        # Last quiz date
                        last_quiz = max(scores, key=lambda s: s.time_stamp_of_attempt)
                        last_quiz_date = last_quiz.time_stamp_of_attempt.strftime('%Y-%m-%d')

                        # Performance rating
                        if avg_percentage >= 80:
                            rating = "Excellent"
                        elif avg_percentage >= 60:
                            rating = "Good"
                        elif avg_percentage >= 40:
                            rating = "Average"
                        else:
                            rating = "Needs Improvement"
                    else:
                        avg_score = 0
                        avg_percentage = 0
                        best_score = None
                        best_percentage = 0
                        attempted_subjects = set()
                        last_quiz_date = 'Never'
                        rating = "No Activity"

                    writer.writerow([
                        user.id,
                        user.full_name,
                        user.email,
                        user.qualification or 'Not specified',
                        user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else 'Not specified',
                        user.created_at.strftime('%Y-%m-%d') if user.created_at else 'Unknown',
                        quizzes_taken,
                        f"{avg_score:.2f}",
                        f"{avg_percentage:.2f}%",
                        best_score.total_scored if best_score else 0,
                        f"{best_percentage:.2f}%",
                        len(attempted_subjects),
                        last_quiz_date,
                        rating
                    ])

                    # Update progress
                    progress = 40 + int((i + 1) / total_users * 40)
                    self.update_state(state='PROGRESS', meta={'current': progress, 'total': 100, 'status': f'Processed {i + 1}/{total_users} users'})

            self.update_state(state='PROGRESS', meta={'current': 90, 'total': 100, 'status': 'Sending notification...'})

            # Send completion email to admin
            if send_csv_export_email(admin_user, filepath, filename):
                logger.info(f"Admin CSV export notification sent to {admin_user.email}")

            logger.info(f"Exported admin CSV to {filepath}")

            return {
                'status': 'SUCCESS',
                'filename': filename,
                'filepath': filepath,
                'total_records': total_users,
                'message': f'Successfully exported data for {total_users} users to CSV'
            }

    except Exception as e:
        logger.error(f"Admin CSV export failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery.task(bind=True)
def cleanup_old_results(self):
    """Clean up old task results and temporary files"""
    try:
        logger.info("Starting cleanup of old results")

        # Clean up old CSV files (older than 7 days)
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

            logger.info(f"Cleaned up {cleaned_files} old export files")

        return f"Cleanup completed. Removed {cleaned_files} old files"

    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")
        raise

# Helper functions for email and notifications
def send_email_reminder(user, new_quizzes):
    """Send email reminder to user"""
    subject = "Quiz Master - Daily Reminder"

    new_quiz_text = ""
    if new_quizzes:
        new_quiz_text = f"<p><strong>{len(new_quizzes)} new quizzes</strong> have been added!</p>"

    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; margin: 20px;">
        <div style="background-color: #007bff; color: white; padding: 20px; text-align: center; border-radius: 5px;">
            <h2>Quiz Master Daily Reminder</h2>
        </div>

        <div style="padding: 20px;">
            <h3>Hello {user.full_name}!</h3>
            <p>We noticed you haven't taken any quizzes recently. Don't let your learning streak break!</p>

            {new_quiz_text}

            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h4>Why continue learning?</h4>
                <ul>
                    <li>Improve your knowledge and skills</li>
                    <li>Track your progress over time</li>
                    <li>Challenge yourself with new topics</li>
                    <li>Stay ahead in your field</li>
                </ul>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:5000"
                   style="background-color: #007bff; color: white; padding: 15px 30px;
                          text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Start Learning Now
                </a>
            </div>

            <p style="color: #666; font-size: 14px;">
                This is an automated reminder. You can update your notification preferences in your profile.
            </p>
        </div>

        <div style="text-align: center; color: #666; font-size: 12px; margin-top: 30px;">
            <p>Quiz Master V2 - Your Learning Companion</p>
        </div>
    </body>
    </html>
    """

    return send_email(user.email, subject, body)

def send_webhook_reminder(user, new_quizzes):
    """Send webhook notification (Google Chat, Slack, etc.)"""
    if not GOOGLE_CHAT_WEBHOOK:
        return False

    message = f"Learning Reminder for {user.full_name}!" + "\n"
    message += f"It's time to continue your quiz journey. "

    if new_quizzes:
        message += f"{len(new_quizzes)} new quizzes are waiting for you!"
    else:
        message += "Don't let your learning streak break!"

    return send_google_chat_message(message)

def generate_user_monthly_data(user, start_date, end_date):
    """Generate monthly performance data for a user"""
    from app.models import Score, Quiz, Chapter, Subject

    scores = Score.query.filter(
        Score.user_id == user.id,
        Score.time_stamp_of_attempt >= start_date,
        Score.time_stamp_of_attempt <= end_date
    ).all()

    if not scores:
        return {
            'total_attempts': 0,
            'average_percentage': 0,
            'best_score': None,
            'quiz_details': [],
            'subjects_covered': 0
        }

    # Calculate statistics
    total_attempts = len(scores)
    total_percentage = 0
    valid_scores = 0
    subjects_set = set()
    quiz_details = []

    for score in scores:
        score_json = score.convert_to_json()
        if score_json['percentage'] > 0:
            total_percentage += score_json['percentage']
            valid_scores += 1

        # Get quiz details
        if score.quiz and score.quiz.chapter:
            subjects_set.add(score.quiz.chapter.subject_id)
            quiz_details.append({
                'quiz_title': score.quiz.title,
                'subject_name': score.quiz.chapter.subject.name if score.quiz.chapter.subject else 'Unknown',
                'chapter_name': score.quiz.chapter.name,
                'score': score.total_scored,
                'total_questions': score.total_questions,
                'percentage': score_json['percentage'],
                'date': score.time_stamp_of_attempt.strftime('%Y-%m-%d'),
                'time_taken': score.time_taken or 'N/A'
            })

    average_percentage = total_percentage / valid_scores if valid_scores > 0 else 0
    best_score = max(scores, key=lambda s: s.convert_to_json()['percentage'])

    return {
        'total_attempts': total_attempts,
        'average_percentage': round(average_percentage, 2),
        'best_score': best_score,
        'quiz_details': quiz_details,
        'subjects_covered': len(subjects_set)
    }

def generate_html_report(user, report_data, month_date):
    """Generate HTML monthly report"""
    month_name = month_date.strftime('%B %Y')

    # Generate quiz details table
    quiz_rows = ""
    for quiz in report_data['quiz_details']:
        quiz_rows += f"""
        <tr>
            <td>{quiz['quiz_title']}</td>
            <td>{quiz['subject_name']}</td>
            <td>{quiz['chapter_name']}</td>
            <td>{quiz['score']}/{quiz['total_questions']}</td>
            <td style="color: {'green' if quiz['percentage'] >= 70 else 'orange' if quiz['percentage'] >= 50 else 'red'};">
                {quiz['percentage']:.1f}%
            </td>
            <td>{quiz['date']}</td>
            <td>{quiz['time_taken']}</td>
        </tr>
        """

    best_score_info = ""
    if report_data['best_score']:
        best_score_json = report_data['best_score'].convert_to_json()
        best_score_info = f"{best_score_json['percentage']:.1f}% ({report_data['best_score'].total_scored}/{report_data['best_score'].total_questions})"

    # Format the current datetime outside the f-string to avoid % character issues
    current_time = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    br_tag = '<br>'

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Monthly Quiz Report - {month_name}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #007bff, #0056b3); color: white; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 28px; }}
            .header h2 {{ margin: 10px 0 0 0; font-size: 18px; opacity: 0.9; }}
            .summary {{ padding: 30px; background-color: #f8f9fa; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .stat-number {{ font-size: 24px; font-weight: bold; color: #007bff; }}
            .stat-label {{ color: #666; font-size: 14px; margin-top: 5px; }}
            .content {{ padding: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #007bff; color: white; font-weight: 600; }}
            tr:hover {{ background-color: #f8f9fa; }}
            .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; color: #666; }}
            .cta-button {{ display: inline-block; background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
            .highlight {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #ffc107; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Monthly Quiz Report</h1>
                <h2>{month_name}</h2>
            </div>

            <div class="summary">
                <h3>Hello {user.full_name}!</h3>
                <p>Here's your comprehensive quiz performance summary for {month_name}. Keep up the excellent work!</p>

                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{report_data['total_attempts']}</div>
                        <div class="stat-label">Quizzes Completed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{report_data['average_percentage']:.1f}%</div>
                        <div class="stat-label">Average Score</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{report_data['subjects_covered']}</div>
                        <div class="stat-label">Subjects Covered</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{best_score_info}</div>
                        <div class="stat-label">Best Performance</div>
                    </div>
                </div>
            </div>

            <div class="content">
                <div class="highlight">
                    <strong>Performance Insight:</strong>
                    {'Excellent work! You are performing above average.' if report_data['average_percentage'] >= 70
                     else 'Good progress! Keep practicing to improve your scores.' if report_data['average_percentage'] >= 50
                     else 'There is room for improvement. Consider reviewing the topics and practicing more.'}
                </div>

                <h3>Detailed Quiz History</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Quiz Title</th>
                            <th>Subject</th>
                            <th>Chapter</th>
                            <th>Score</th>
                            <th>Percentage</th>
                            <th>Date</th>
                            <th>Time Taken</th>
                        </tr>
                    </thead>
                    <tbody>
                        {quiz_rows}
                    </tbody>
                </table>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:5000" class="cta-button">
                        Continue Your Learning Journey
                    </a>
                </div>
            </div>

            <div class="footer">
                <p>Keep learning, keep growing! Your dedication to continuous improvement is commendable.</p>
                <p style="font-size: 12px; margin-top: 15px;">
                    This report was automatically generated by Quiz Master V2{br_tag}
                    Generated on {current_time}
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    return html_content

def send_monthly_report_email(user, html_report, month_date):
    """Send monthly report via email"""
    month_year = month_date.strftime('%B %Y')
    subject = f"Quiz Master - Monthly Report for {month_year}"
    return send_email(user.email, subject, html_report)

def send_csv_export_email(user, csv_path, filename):
    """Send CSV export completion notification"""
    subject = "Quiz Master - CSV Export Ready"

    # Format the current datetime outside the f-string to avoid % character issues
    current_time = datetime.now().strftime('%B %d, %Y at %I:%M %p')

    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; margin: 20px;">
        <div style="background-color: #28a745; color: white; padding: 20px; text-align: center; border-radius: 5px;">
            <h2>CSV Export Completed</h2>
        </div>

        <div style="padding: 20px;">
            <h3>Hello {user.full_name}!</h3>
            <p>Your CSV export has been completed successfully!</p>

            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>File:</strong> {filename}</p>
                <p><strong>Generated:</strong> {current_time}</p>
                <p><strong>Status:</strong> Ready for download</p>
            </div>

            <p>You can download your file from the dashboard or check your downloads folder.</p>

            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:5000"
                   style="background-color: #007bff; color: white; padding: 15px 30px;
                          text-decoration: none; border-radius: 5px; font-weight: bold;">
                    View Dashboard
                </a>
            </div>
        </div>

        <div style="text-align: center; color: #666; font-size: 12px; margin-top: 30px;">
            <p>Quiz Master V2 - Export Service</p>
        </div>
    </body>
    </html>
    """

    return send_email(user.email, subject, body, csv_path)