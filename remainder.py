
from app import celery, app, db, mail
from flask_mail import Message
from models import Quiz, Score, User
from datetime import datetime, time
from celery.schedules import crontab


def send_email_reminder(user, quizzes):
    quiz_titles = "\n".join(f"• {q.name}" for q in quizzes)
    body = (
        f"Hi {user.username},\n\n"
        f"New quizzes have been added today:\n{quiz_titles}\n\n"
      
    )
    try:
        msg = Message(
            subject="Daily Quiz Reminder",
            sender=app.config['MAIL_USERNAME'],
            recipients=[user.email],
            body=body
        )
        mail.send(msg)
        print(" Reminder sent to {user.email}")
    except Exception as e:
        print(f"Failed to send email to {user.email}: {e}")


@celery.task(name='daily_quiz_reminder_task')
def daily_quiz_reminder_task():
    with app.app_context():
        today = datetime.utcnow().date()
        quizzes_today = Quiz.query.filter(Quiz.date_of_quiz == today).all()
        if not quizzes_today:
            print("No quizzes today.")
            return

        users = User.query.all()
        email_count = 0
        for user in users:
            attempted = Score.query.filter_by(user_id=user.id).filter(
                Score.time_stamp >= datetime.combine(today, time.min)
            ).count()
            if attempted == 0:
                send_email_reminder(user, quizzes_today)
                email_count += 1
        print(f" Daily reminder task completed. Emails sent: {email_count}")


@celery.task(name='monthly_user_report_task')
def monthly_user_report_task():
    with app.app_context():
        users = User.query.all()

        for user in users:
            scores = Score.query.filter_by(user_id=user.id).all()

            if not scores:
                continue

            total = sum(score.total_score for score in scores)
            avg_score = total / len(scores)

            quiz_details = "".join(
                f"<li>{score.quiz.name}: {score.total_score} out of 100 </li>"
                for score in scores if score.quiz 
            )

            html_body = f"""
            <h3>Your Activity Report (All Time)</h3>
            <p>Hello {user.username},</p>
            <p>Here's your quiz performance so far:</p>
            <ul>
                <li>Total Quizzes Taken: {len(scores)}</li>
                {quiz_details}
            </ul>
            <p>Keep learning and improving!</p>
            """

            try:
                msg = Message(
                    subject=f" Your Quiz Report - {datetime.utcnow().strftime('%B %Y')}",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[user.email],
                    html=html_body
                )
                mail.send(msg)
                print(" Monthly report sent to {user.email}")
            except Exception as e:
                print(" Failed to send report to {user.email}: {e}")



celery.conf.beat_schedule = {
    'daily-quiz-reminder': {
        'task': 'daily_quiz_reminder_task',
        'schedule': crontab(hour=17, minute=40), 
    },
    'monthly-user-report': {
        'task': 'monthly_user_report_task',
        'schedule': crontab(hour=19, minute=14, day_of_month='28'),  
    }
}
celery.conf.timezone = 'Asia/Kolkata'
