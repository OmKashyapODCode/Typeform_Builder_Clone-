"""
Seed script - populates the database with demo data.
Run with: python seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, init_db
from app.models.form import Form, FormStatus
from app.models.question import Question, QuestionType
from app.models.response import Response, ResponseAnswer
from datetime import datetime, timezone, timedelta
import uuid
import random


def seed():
    init_db()
    db = SessionLocal()

    try:
        # Check if already seeded
        existing = db.query(Form).count()
        if existing > 0:
            print(f"Database already has {existing} forms. Skipping seed.")
            return

        print("Seeding database...")

        # ─── Form 1: Customer Feedback Survey (Published) ───────────────────
        form1 = Form(
            id=str(uuid.uuid4()),
            public_id=str(uuid.uuid4()),
            title="Customer Feedback Survey",
            description="We'd love to hear your thoughts on your recent experience with us.",
            status=FormStatus.published,
            published_at=datetime.now(timezone.utc) - timedelta(days=10),
        )
        db.add(form1)
        db.flush()

        f1_questions = [
            Question(id=str(uuid.uuid4()), form_id=form1.id, type=QuestionType.short_text,
                     title="What is your name?", position=0, required=True,
                     settings={"placeholder": "Enter your full name"}),
            Question(id=str(uuid.uuid4()), form_id=form1.id, type=QuestionType.email,
                     title="What is your email address?", position=1, required=True,
                     settings={"placeholder": "you@example.com"}),
            Question(id=str(uuid.uuid4()), form_id=form1.id, type=QuestionType.rating,
                     title="How would you rate your overall experience?",
                     description="1 = Very Poor, 5 = Excellent",
                     position=2, required=True, settings={"max_rating": 5}),
            Question(id=str(uuid.uuid4()), form_id=form1.id, type=QuestionType.long_text,
                     title="What did you like most about our service?",
                     description="Please be as specific as possible.",
                     position=3, required=False, settings={}),
            Question(id=str(uuid.uuid4()), form_id=form1.id, type=QuestionType.yes_no,
                     title="Would you recommend us to a friend or colleague?",
                     position=4, required=True, settings={}),
            Question(id=str(uuid.uuid4()), form_id=form1.id, type=QuestionType.multiple_choice,
                     title="How did you hear about us?",
                     position=5, required=False,
                     settings={"choices": ["Social Media", "Friend/Colleague", "Search Engine", "Advertisement", "Other"],
                               "allow_other": False}),
        ]
        for q in f1_questions:
            db.add(q)
        db.flush()

        # Seed 15 responses for form 1
        names = ["Alice Chen", "Bob Martinez", "Carol Williams", "David Singh", "Eva Johansson",
                 "Frank O'Brien", "Grace Kim", "Henry Brown", "Iris Patel", "Jack Thompson",
                 "Karen Lee", "Liam Garcia", "Mia Wilson", "Noah Davis", "Olivia Johnson"]
        emails = [f"{n.split()[0].lower()}@example.com" for n in names]
        ratings = [5, 4, 5, 3, 5, 4, 4, 5, 3, 4, 5, 5, 4, 3, 5]
        would_recommend = ["Yes", "Yes", "Yes", "No", "Yes", "Yes", "Yes", "Yes", "No", "Yes",
                           "Yes", "Yes", "Yes", "No", "Yes"]
        how_heard = ["Social Media", "Friend/Colleague", "Search Engine", "Advertisement", "Social Media",
                     "Friend/Colleague", "Social Media", "Search Engine", "Friend/Colleague", "Advertisement",
                     "Social Media", "Friend/Colleague", "Search Engine", "Social Media", "Friend/Colleague"]
        feedback_texts = [
            "The team was incredibly responsive and solved my issue quickly.",
            "Great product but the onboarding could be improved.",
            "Absolutely love the interface - so intuitive!",
            "Product is good but support response time was slow.",
            "Best experience I've had with any SaaS product.",
            "The documentation is excellent and the support team is fantastic.",
            "Very impressed with the speed and reliability.",
            "The feature set covers everything I need for my workflow.",
            "Some features are missing but overall it's a solid product.",
            "Customer support went above and beyond to help me.",
            "Clean UI and the product actually works as advertised.",
            "The API is well-documented and easy to integrate.",
            "Good product, would love to see more customization options.",
            "Had a few issues but they were resolved promptly.",
            "Exceptional quality and the team is always helpful.",
        ]

        for i in range(15):
            resp = Response(
                id=str(uuid.uuid4()),
                form_id=form1.id,
                submitted_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 240)),
            )
            db.add(resp)
            db.flush()

            answers_data = [
                (f1_questions[0].id, names[i]),
                (f1_questions[1].id, emails[i]),
                (f1_questions[2].id, str(ratings[i])),
                (f1_questions[3].id, feedback_texts[i] if random.random() > 0.2 else None),
                (f1_questions[4].id, would_recommend[i]),
                (f1_questions[5].id, how_heard[i] if random.random() > 0.15 else None),
            ]
            for q_id, val in answers_data:
                if val:
                    db.add(ResponseAnswer(
                        id=str(uuid.uuid4()),
                        response_id=resp.id,
                        question_id=q_id,
                        answer_value=val,
                    ))

        # ─── Form 2: Developer Skills Survey (Published) ────────────────────
        form2 = Form(
            id=str(uuid.uuid4()),
            public_id=str(uuid.uuid4()),
            title="Developer Skills Survey",
            description="Help us understand the current developer landscape and skill distribution.",
            status=FormStatus.published,
            published_at=datetime.now(timezone.utc) - timedelta(days=5),
        )
        db.add(form2)
        db.flush()

        f2_questions = [
            Question(id=str(uuid.uuid4()), form_id=form2.id, type=QuestionType.short_text,
                     title="What is your name?", position=0, required=True, settings={}),
            Question(id=str(uuid.uuid4()), form_id=form2.id, type=QuestionType.email,
                     title="What is your work email?", position=1, required=True, settings={}),
            Question(id=str(uuid.uuid4()), form_id=form2.id, type=QuestionType.number,
                     title="How many years of software development experience do you have?",
                     position=2, required=True, settings={"min_value": 0, "max_value": 50}),
            Question(id=str(uuid.uuid4()), form_id=form2.id, type=QuestionType.dropdown,
                     title="What is your primary programming language?",
                     position=3, required=True,
                     settings={"choices": ["Python", "JavaScript/TypeScript", "Java", "C/C++", "Go", "Rust", "Ruby", "Other"]}),
            Question(id=str(uuid.uuid4()), form_id=form2.id, type=QuestionType.multiple_choice,
                     title="Which areas do you primarily work in?",
                     position=4, required=True,
                     settings={"choices": ["Frontend", "Backend", "Full Stack", "DevOps/Infrastructure", "Data Engineering", "ML/AI"],
                               "allow_other": False}),
            Question(id=str(uuid.uuid4()), form_id=form2.id, type=QuestionType.rating,
                     title="How would you rate your satisfaction with your current tech stack?",
                     position=5, required=True, settings={"max_rating": 5}),
            Question(id=str(uuid.uuid4()), form_id=form2.id, type=QuestionType.yes_no,
                     title="Are you currently open to new opportunities?",
                     position=6, required=False, settings={}),
            Question(id=str(uuid.uuid4()), form_id=form2.id, type=QuestionType.long_text,
                     title="What technologies are you most excited about in 2025?",
                     position=7, required=False, settings={}),
        ]
        for q in f2_questions:
            db.add(q)
        db.flush()

        # Seed 10 responses for form 2
        dev_names = ["Arjun Sharma", "Sofia Rodriguez", "Mohammed Al-Hassan", "Yuki Tanaka",
                     "Emma O'Sullivan", "Wei Zhang", "Priya Nair", "Lucas Fernandez",
                     "Aisha Okonkwo", "Ryan O'Connor"]
        dev_emails = [f"{n.split()[0].lower()}.dev@techcorp.com" for n in dev_names]
        exp_years = ["3", "7", "12", "5", "2", "8", "15", "4", "6", "9"]
        primary_langs = ["Python", "JavaScript/TypeScript", "Java", "Go", "Python",
                         "JavaScript/TypeScript", "Python", "Rust", "JavaScript/TypeScript", "Python"]
        work_areas = ["Backend", "Full Stack", "Backend", "DevOps/Infrastructure", "Frontend",
                      "Full Stack", "Data Engineering", "Backend", "Full Stack", "Backend"]
        tech_ratings = ["4", "5", "3", "4", "5", "4", "3", "5", "4", "4"]
        open_to_opps = ["Yes", "No", "No", "Yes", "Yes", "No", "Yes", "Yes", "No", "Yes"]
        excited_about = [
            "AI-powered developer tools like Copilot and Cursor are game-changers.",
            "WebAssembly and edge computing are the future of web development.",
            "Kubernetes and platform engineering are transforming how we deploy software.",
            "Rust is finally becoming mainstream for systems programming.",
            "React Server Components and the new Next.js features are fascinating.",
            "LLMs integrated into developer workflows will change everything.",
            "Real-time data streaming with Kafka and Flink.",
            "Formal verification tools making software more reliable.",
            "The rise of AI agents and their integration with existing systems.",
            "Observability tools are becoming more intelligent and actionable.",
        ]

        for i in range(10):
            resp = Response(
                id=str(uuid.uuid4()),
                form_id=form2.id,
                submitted_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 120)),
            )
            db.add(resp)
            db.flush()

            for q_id, val in [
                (f2_questions[0].id, dev_names[i]),
                (f2_questions[1].id, dev_emails[i]),
                (f2_questions[2].id, exp_years[i]),
                (f2_questions[3].id, primary_langs[i]),
                (f2_questions[4].id, work_areas[i]),
                (f2_questions[5].id, tech_ratings[i]),
                (f2_questions[6].id, open_to_opps[i]),
                (f2_questions[7].id, excited_about[i] if random.random() > 0.1 else None),
            ]:
                if val:
                    db.add(ResponseAnswer(
                        id=str(uuid.uuid4()),
                        response_id=resp.id,
                        question_id=q_id,
                        answer_value=val,
                    ))

        # ─── Form 3: Product Onboarding (Draft) ─────────────────────────────
        form3 = Form(
            id=str(uuid.uuid4()),
            public_id=str(uuid.uuid4()),
            title="Product Onboarding Questionnaire",
            description="Help us personalize your experience.",
            status=FormStatus.draft,
        )
        db.add(form3)
        db.flush()

        f3_questions = [
            Question(id=str(uuid.uuid4()), form_id=form3.id, type=QuestionType.short_text,
                     title="What is your first name?", position=0, required=True, settings={}),
            Question(id=str(uuid.uuid4()), form_id=form3.id, type=QuestionType.dropdown,
                     title="What best describes your role?",
                     position=1, required=True,
                     settings={"choices": ["Founder/CEO", "Product Manager", "Engineer", "Designer", "Marketer", "Other"]}),
            Question(id=str(uuid.uuid4()), form_id=form3.id, type=QuestionType.number,
                     title="How large is your team?",
                     position=2, required=False, settings={"min_value": 1}),
            Question(id=str(uuid.uuid4()), form_id=form3.id, type=QuestionType.multiple_choice,
                     title="What are your primary goals with our product?",
                     position=3, required=True,
                     settings={"choices": ["Increase productivity", "Better collaboration", "Data insights", "Cost reduction", "Process automation"],
                               "allow_other": False}),
        ]
        for q in f3_questions:
            db.add(q)

        db.commit()
        print(f"[OK] Seeded 3 forms with questions and {15 + 10} responses successfully!")
        print(f"\nForm 1 (Published): {form1.title}")
        print(f"  Public URL: /form/{form1.public_id}")
        print(f"\nForm 2 (Published): {form2.title}")
        print(f"  Public URL: /form/{form2.public_id}")
        print(f"\nForm 3 (Draft): {form3.title}")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
