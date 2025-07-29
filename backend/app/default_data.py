from .models import db, User, Role, Subject, Chapter, Quiz, Question, Score
from datetime import date
import logging

logger = logging.getLogger(__name__)

def create_default_data():
    try:
        if User.query.count() > 1:
            return

        user_role = Role.query.filter_by(name='user').first()
        if not User.query.filter_by(username='dummy').first():
            dummy_user = User(
                username='dummy',
                email='dummy@example.com',
                full_name='Test Student',
                qualification='Bachelor of Science',
                date_of_birth=date(1995, 5, 15),
                is_active=True
            )
            dummy_user.set_password('dummy123')
            if user_role:
                dummy_user.roles.append(user_role)
            db.session.add(dummy_user)
            db.session.commit()

        if not Subject.query.filter_by(name='Computer Science').first():
            subject = Subject(
                name='Computer Science',
                description='Fundamental computer science concepts'
            )
            db.session.add(subject)
            db.session.commit()
        else:
            subject = Subject.query.filter_by(name='Computer Science').first()

        if not Chapter.query.filter_by(name='Programming Basics').first():
            chapter = Chapter(
                name='Programming Basics',
                description='Introduction to programming concepts',
                subject_id=subject.id
            )
            db.session.add(chapter)
            db.session.commit()
        else:
            chapter = Chapter.query.filter_by(name='Programming Basics').first()

        if not Quiz.query.filter_by(title='Basic Programming Quiz').first():
            quiz = Quiz(
                title='Basic Programming Quiz',
                remarks='Test your programming knowledge',
                time_duration='30:00',
                chapter_id=chapter.id
            )
            db.session.add(quiz)
            db.session.commit()
        else:
            quiz = Quiz.query.filter_by(title='Basic Programming Quiz').first()

        if Question.query.filter_by(quiz_id=quiz.id).count() == 0:
            questions = [
                ('What is a variable in programming?', 'A container for data', 'A type of loop', 'A programming language', 'Hardware component', 1, 25),
                ('Which is a programming language?', 'HTML', 'CSS', 'Python', 'JSON', 3, 25),
                ('What does "if-else" represent?', 'A loop', 'A conditional statement', 'A function', 'A variable', 2, 25),
                ('Purpose of comments in code?', 'Execute code', 'Make code faster', 'Explain code', 'Create variables', 3, 25)
            ]

            for q_data in questions:
                question = Question(
                    question_statement=q_data[0],
                    option1=q_data[1],
                    option2=q_data[2],
                    option3=q_data[3],
                    option4=q_data[4],
                    correct_option=q_data[5],
                    marks=q_data[6],
                    quiz_id=quiz.id
                )
                db.session.add(question)
            db.session.commit()

        dummy_user = User.query.filter_by(username='dummy').first()
        if dummy_user and not Score.query.filter_by(user_id=dummy_user.id, quiz_id=quiz.id).first():
            sample_score = Score(
                user_id=dummy_user.id,
                quiz_id=quiz.id,
                total_scored=75,
                total_questions=4,
                time_taken="15:30"
            )
            db.session.add(sample_score)
            db.session.commit()

        additional_subjects = [
            ('Mathematics', 'Mathematical concepts', [('Algebra', 'Basic algebra')]),
            ('Data Structures', 'Data organization', [('Arrays', 'Linear structures')])
        ]

        for name, desc, chapters in additional_subjects:
            if not Subject.query.filter_by(name=name).first():
                new_subject = Subject(name=name, description=desc)
                db.session.add(new_subject)
                db.session.commit()

                for ch_name, ch_desc in chapters:
                    new_chapter = Chapter(name=ch_name, description=ch_desc, subject_id=new_subject.id)
                    db.session.add(new_chapter)
                db.session.commit()

        logger.info("Default data created successfully")

    except Exception as e:
        logger.error(f"Error creating default data: {e}")
        db.session.rollback()
        raise

def reset_database():
    logger.info("Resetting database...")
    db.drop_all()
    db.create_all()

    from .auth import init_admin_user
    init_admin_user()
    create_default_data()

    logger.info("Database reset complete")
