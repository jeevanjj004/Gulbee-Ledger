from background_task import background
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import EMI  # Your EMI model

@background(schedule=0)  # schedule=0 → run immediately first
def send_emi_reminders():
    today = timezone.now().date()
    five_days_before = today + timedelta(days=5)

    # EMIs due in 5 days
    upcoming_emis = EMI.objects.filter(due_date=five_days_before, status='pending')
    for emi in upcoming_emis:
        subject = "EMI Reminder: Upcoming Payment"
        message = f"""
Hello {emi.user.first_name},

Your EMI of amount {emi.amount} is due on {emi.due_date}.
Please prepare to pay within 5 days to avoid penalties.

Thank you.
"""
        send_mail(subject, message, 'internshipidk456@gmail.com', [emi.user.email])
        print(f"5-days reminder sent to {emi.user.email}")

    # EMIs due today
    today_emis = EMI.objects.filter(due_date=today, status='pending')
    for emi in today_emis:
        subject = "EMI Reminder: Due Today!"
        message = f"""
Hello {emi.user.first_name},

Your EMI of amount {emi.amount} is due TODAY ({emi.due_date}).
Please pay immediately to avoid penalties.

Thank you.
"""
        send_mail(subject, message, 'internshipidk456@gmail.com', [emi.user.email])
        print(f"Today reminder sent to {emi.user.email}")
