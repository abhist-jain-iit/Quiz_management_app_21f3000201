from .models import db, User, Role, Subject, Chapter, Quiz, Question, Score
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

def create_default_data():
    try:
        if User.query.count() > 1:
            return
        dummy_user = User.query.filter_by(username='dummy').first()
        if not dummy_user:
            user_role = Role.query.filter_by(name='user').first()
            dummy_user = User(
                username='dummy',
                email='dummy@example.com',
                full_name='Dummy Test User',
                qualification='Bachelor of Science',
                date_of_birth=date(1995, 5, 15),
                is_active=True
            )
            dummy_user.set_password('dummy123')
            if user_role:
                dummy_user.roles.append(user_role)
            
            db.session.add(dummy_user)
            db.session.commit()

        subject = Subject.query.filter_by(name='Computer Science Fundamentals').first()
        if not subject:
            subject = Subject(
                name='Computer Science Fundamentals',
                description='Basic concepts of computer science including programming, data structures, and algorithms'
            )
            db.session.add(subject)
            db.session.commit()
        
        # 3. Create test chapter
        logger.info("Creating default chapter...")
        chapter = Chapter.query.filter_by(name='Introduction to Programming').first()
        if not chapter:
            chapter = Chapter(
                name='Introduction to Programming',
                description='Learn the basics of programming concepts, variables, and control structures',
                subject_id=subject.id
            )
            db.session.add(chapter)
            db.session.commit()
            logger.info("Chapter created: Introduction to Programming")
        
        # 4. Create test quiz
        logger.info("Creating default quiz...")
        quiz = Quiz.query.filter_by(title='Programming Basics Quiz').first()
        if not quiz:
            quiz = Quiz(
                title='Programming Basics Quiz',
                remarks='Test your knowledge of basic programming concepts',
                time_duration='30:00',  # 30 minutes
                chapter_id=chapter.id
            )
            db.session.add(quiz)
            db.session.commit()
            logger.info("Quiz created: Programming Basics Quiz")
        
        # 5. Create test questions
        logger.info("Creating default questions...")
        existing_questions = Question.query.filter_by(quiz_id=quiz.id).count()
        if existing_questions == 0:
            questions_data = [
                {
                    'question_statement': 'What is a variable in programming?',
                    'option1': 'A container that stores data values',
                    'option2': 'A type of loop',
                    'option3': 'A programming language',
                    'option4': 'A computer hardware component',
                    'correct_option': 1,
                    'marks': 25
                },
                {
                    'question_statement': 'Which of the following is a programming language?',
                    'option1': 'HTML',
                    'option2': 'CSS',
                    'option3': 'Python',
                    'option4': 'JSON',
                    'correct_option': 3,
                    'marks': 25
                },
                {
                    'question_statement': 'What does "if-else" represent in programming?',
                    'option1': 'A loop structure',
                    'option2': 'A conditional statement',
                    'option3': 'A function definition',
                    'option4': 'A variable declaration',
                    'correct_option': 2,
                    'marks': 25
                },
                {
                    'question_statement': 'What is the purpose of comments in code?',
                    'option1': 'To execute additional code',
                    'option2': 'To make the program run faster',
                    'option3': 'To explain what the code does',
                    'option4': 'To create variables',
                    'correct_option': 3,
                    'marks': 25
                }
            ]
            
            for i, q_data in enumerate(questions_data, 1):
                question = Question(
                    question_statement=q_data['question_statement'],
                    option1=q_data['option1'],
                    option2=q_data['option2'],
                    option3=q_data['option3'],
                    option4=q_data['option4'],
                    correct_option=q_data['correct_option'],
                    marks=q_data['marks'],
                    quiz_id=quiz.id
                )
                db.session.add(question)
            
            db.session.commit()
            logger.info(f"Created {len(questions_data)} default questions")
        
        # 6. Create sample quiz attempt
        logger.info("Creating sample quiz attempt...")
        existing_score = Score.query.filter_by(user_id=dummy_user.id, quiz_id=quiz.id).first()
        if not existing_score:
            sample_score = Score(
                user_id=dummy_user.id,
                quiz_id=quiz.id,
                total_scored=75,  # 75 out of 100 marks
                total_questions=4,  # 4 questions
                time_taken="15:30"  # 15 minutes 30 seconds
            )
            db.session.add(sample_score)
            db.session.commit()
            logger.info("Sample quiz attempt created")
        
        # 7. Create additional subjects and chapters for variety
        logger.info("Creating additional subjects...")
        additional_subjects = [
            {
                'name': 'Mathematics',
                'description': 'Mathematical concepts and problem solving',
                'chapters': [
                    {
                        'name': 'Algebra Basics',
                        'description': 'Introduction to algebraic expressions and equations'
                    }
                ]
            },
            {
                'name': 'Data Structures',
                'description': 'Learn about arrays, linked lists, stacks, and queues',
                'chapters': [
                    {
                        'name': 'Arrays and Lists',
                        'description': 'Understanding linear data structures'
                    }
                ]
            }
        ]
        
        for subj_data in additional_subjects:
            existing_subj = Subject.query.filter_by(name=subj_data['name']).first()
            if not existing_subj:
                new_subject = Subject(
                    name=subj_data['name'],
                    description=subj_data['description']
                )
                db.session.add(new_subject)
                db.session.commit()
                
                # Add chapters for this subject
                for chap_data in subj_data['chapters']:
                    new_chapter = Chapter(
                        name=chap_data['name'],
                        description=chap_data['description'],
                        subject_id=new_subject.id
                    )
                    db.session.add(new_chapter)
                
                db.session.commit()
                logger.info(f"Created subject: {subj_data['name']} with chapters")
        
        # Final summary
        user_count = User.query.count()
        subject_count = Subject.query.count()
        chapter_count = Chapter.query.count()
        quiz_count = Quiz.query.count()
        question_count = Question.query.count()
        score_count = Score.query.count()
        
        logger.info("Default data initialization complete!")
        logger.info(f"Summary: {user_count} users, {subject_count} subjects, {chapter_count} chapters, {quiz_count} quizzes, {question_count} questions, {score_count} attempts")

        # Log default credentials for development
        logger.info("Default login credentials created:")
        logger.info("Admin: admin / Admin@123")
        logger.info("Student: dummy / dummy123")
        
    except Exception as e:
        logger.error(f"Error creating default data: {e}")
        db.session.rollback()
        raise e

def reset_database():
    """Reset database and recreate with default data"""
    logger.info("Resetting database...")
    db.drop_all()
    db.create_all()
    
    # Import and run admin user creation
    from .auth import init_admin_user
    init_admin_user()
    
    # Create default data
    create_default_data()
    
    logger.info("Database reset complete with default data!")
