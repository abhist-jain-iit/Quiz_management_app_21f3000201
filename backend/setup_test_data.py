#!/usr/bin/env python3
"""
Setup script to create test data for Quiz Master V2
Creates: dummy user, subject, chapter, quiz with questions
"""

from app import create_app
from app.models import db, User, Role, Subject, Chapter, Quiz, Question, Score
from datetime import datetime, date

def create_test_data():
    app = create_app('development')
    
    with app.app_context():
        print("🚀 Setting up test data for Quiz Master V2...")
        print("=" * 60)
        
        # 1. Create dummy user
        print("👤 Creating dummy user...")
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
            print("✅ Dummy user created!")
            print(f"   Username: dummy")
            print(f"   Password: dummy123")
            print(f"   Email: {dummy_user.email}")
        else:
            print("✅ Dummy user already exists!")
        
        # 2. Create test subject
        print("\n📚 Creating test subject...")
        subject = Subject.query.filter_by(name='Computer Science Fundamentals').first()
        if not subject:
            subject = Subject(
                name='Computer Science Fundamentals',
                description='Basic concepts of computer science including programming, data structures, and algorithms'
            )
            db.session.add(subject)
            db.session.commit()
            print("✅ Subject created: Computer Science Fundamentals")
        else:
            print("✅ Subject already exists!")
        
        # 3. Create test chapter
        print("\n📖 Creating test chapter...")
        chapter = Chapter.query.filter_by(name='Introduction to Programming').first()
        if not chapter:
            chapter = Chapter(
                name='Introduction to Programming',
                description='Learn the basics of programming concepts, variables, and control structures',
                subject_id=subject.id
            )
            db.session.add(chapter)
            db.session.commit()
            print("✅ Chapter created: Introduction to Programming")
        else:
            print("✅ Chapter already exists!")
        
        # 4. Create test quiz
        print("\n📝 Creating test quiz...")
        quiz = Quiz.query.filter_by(name='Programming Basics Quiz').first()
        if not quiz:
            quiz = Quiz(
                name='Programming Basics Quiz',
                description='Test your knowledge of basic programming concepts',
                time_limit=30,  # 30 minutes
                total_marks=100,
                chapter_id=chapter.id
            )
            db.session.add(quiz)
            db.session.commit()
            print("✅ Quiz created: Programming Basics Quiz")
            print(f"   Time limit: {quiz.time_limit} minutes")
            print(f"   Total marks: {quiz.total_marks}")
        else:
            print("✅ Quiz already exists!")
        
        # 5. Create test questions
        print("\n❓ Creating test questions...")
        
        questions_data = [
            {
                'text': 'What is a variable in programming?',
                'option1': 'A container that stores data values',
                'option2': 'A type of loop',
                'option3': 'A programming language',
                'option4': 'A computer hardware component',
                'correct_option': 1,
                'marks': 25
            },
            {
                'text': 'Which of the following is a programming language?',
                'option1': 'HTML',
                'option2': 'CSS',
                'option3': 'Python',
                'option4': 'JSON',
                'correct_option': 3,
                'marks': 25
            },
            {
                'text': 'What does "if-else" represent in programming?',
                'option1': 'A loop structure',
                'option2': 'A conditional statement',
                'option3': 'A function definition',
                'option4': 'A variable declaration',
                'correct_option': 2,
                'marks': 25
            },
            {
                'text': 'What is the purpose of comments in code?',
                'option1': 'To execute additional code',
                'option2': 'To make the program run faster',
                'option3': 'To explain what the code does',
                'option4': 'To create variables',
                'correct_option': 3,
                'marks': 25
            }
        ]
        
        existing_questions = Question.query.filter_by(quiz_id=quiz.id).count()
        if existing_questions == 0:
            for i, q_data in enumerate(questions_data, 1):
                question = Question(
                    text=q_data['text'],
                    option1=q_data['option1'],
                    option2=q_data['option2'],
                    option3=q_data['option3'],
                    option4=q_data['option4'],
                    correct_option=q_data['correct_option'],
                    marks=q_data['marks'],
                    quiz_id=quiz.id
                )
                db.session.add(question)
                print(f"✅ Question {i} created: {q_data['text'][:50]}...")
            
            db.session.commit()
            print(f"✅ All {len(questions_data)} questions created!")
        else:
            print("✅ Questions already exist!")
        
        # 6. Create a sample score (quiz attempt)
        print("\n🏆 Creating sample quiz attempt...")
        existing_score = Score.query.filter_by(user_id=dummy_user.id, quiz_id=quiz.id).first()
        if not existing_score:
            sample_score = Score(
                user_id=dummy_user.id,
                quiz_id=quiz.id,
                score=75,  # 75 out of 100
                total_marks=100,
                time_taken="15:30",  # 15 minutes 30 seconds
                answers={
                    "1": 1,  # Correct
                    "2": 3,  # Correct  
                    "3": 2,  # Correct
                    "4": 2   # Incorrect (should be 3)
                }
            )
            db.session.add(sample_score)
            db.session.commit()
            print("✅ Sample quiz attempt created!")
            print(f"   Score: {sample_score.score}/{sample_score.total_marks}")
            print(f"   Time taken: {sample_score.time_taken}")
        else:
            print("✅ Sample quiz attempt already exists!")
        
        print("\n" + "=" * 60)
        print("🎉 TEST DATA SETUP COMPLETE!")
        print("=" * 60)
        
        print("\n📋 SUMMARY:")
        print(f"👤 Users: {User.query.count()} (admin + dummy)")
        print(f"📚 Subjects: {Subject.query.count()}")
        print(f"📖 Chapters: {Chapter.query.count()}")
        print(f"📝 Quizzes: {Quiz.query.count()}")
        print(f"❓ Questions: {Question.query.count()}")
        print(f"🏆 Quiz Attempts: {Score.query.count()}")
        
        print("\n🔑 LOGIN CREDENTIALS:")
        print("Admin User:")
        print("  Username: admin")
        print("  Password: Admin@123")
        print("\nDummy User:")
        print("  Username: dummy")
        print("  Password: dummy123")
        
        print("\n🧪 TESTING FLOW:")
        print("1. Login as admin to manage content")
        print("2. Login as dummy to take quizzes")
        print("3. Check dashboard for statistics")
        print("4. Test quiz-taking functionality")
        print("5. View performance reports")
        
        print("\n✨ Ready to test 50% of your application!")
        print("=" * 60)

if __name__ == '__main__':
    create_test_data()
