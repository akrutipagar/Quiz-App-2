from app import celery  # Only import celery app
from remainder import daily_quiz_reminder_task  # ✅ import the task function
from remainder import monthly_user_report_task
