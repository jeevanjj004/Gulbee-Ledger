"""
File:
    emi/management/commands/send_emi_reminders.py

Purpose
-------
This Django management command automatically sends EMI reminder emails.

It sends two reminders:
1. 5 days before the EMI due date.
2. On the EMI due date.

The command is designed to be executed automatically by Linux Cron,
so reminder emails are sent even if the website is not open or
no users are logged in.

Example:
    python manage.py send_emi_reminders

Cron (Runs every day at 12:30 AM)

30 0 * * * /home/thomas/THOMAS/django/Gulbee-Ledger/venv/bin/python /home/thomas/THOMAS/django/Gulbee-Ledger/manage.py send_emi_reminders >> /home/thomas/THOMAS/django/Gulbee-Ledger/emi_reminder.log 2>&1

Author:
    Thomas

Project:
    GulbeeLedger
"""

from datetime import date, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from emi.models import EMI, EmiStatus


class Command(BaseCommand):
    help = "Send EMI reminder emails"

    def handle(self, *args, **kwargs):

        # ============================================================
        # START OF COMMAND
        # ============================================================

        self.stdout.write("=" * 60)
        self.stdout.write("EMI Reminder Command Started")
        self.stdout.write("=" * 60)


        # TEMP SMTP DEBUG
        self.stdout.write(f"EMAIL HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"EMAIL PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"EMAIL USER: {settings.EMAIL_HOST_USER}")

        
        # Today's date
        today = date.today()

        # Date after 5 days
        five_days_before = today + timedelta(days=5)

        self.stdout.write(f"Today's Date        : {today}")
        self.stdout.write(f"5 Days Reminder Date: {five_days_before}")

        # ============================================================
        # FIND EMIs DUE IN 5 DAYS
        # ============================================================

        five_day_emis = EMI.objects.select_related(
            "user",
            "debit"
        ).filter(
            due_date=five_days_before,
            status=EmiStatus.PENDING,
            reminder_5_days_sent=False
        )

        self.stdout.write(
            f"5-Day Reminder EMIs Found : {five_day_emis.count()}"
        )

        # ============================================================
        # SEND 5 DAY REMINDER
        # ============================================================

        for emi in five_day_emis:

            debit_id = emi.debit.debit_id if emi.debit else "N/A"
            lender = emi.debit.lender_name if emi.debit else "N/A"

            subject = "⏰ EMI Payment Reminder – Upcoming Due Date"

            text_message = f"""
Dear {emi.user.first_name},

This is a friendly reminder that one of your EMI payments is due in 5 days.

-------------------------------------------------
Debit ID      : {debit_id}
Lender        : {lender}
EMI Amount    : ₹{emi.amount:,.2f}
Due Date      : {emi.due_date.strftime("%d-%m-%Y")}
-------------------------------------------------

Please make your payment on or before the due date to avoid any late fees or penalties.

Thank you for using GulbeeLedger.

Regards,
GulbeeLedger Team
"""

            html_message = f"""
<html>
<body style="font-family:Arial,sans-serif;background:#f4f4f4;padding:20px;">

<div style="background:white;padding:25px;border-radius:8px;max-width:650px;margin:auto;">

<h2 style="color:#0d6efd;">
EMI Payment Reminder
</h2>

<p>Dear <b>{emi.user.first_name}</b>,</p>

<p>
This is a friendly reminder that your EMI payment is due in
<b style="color:#e67e22;">5 days</b>.
</p>

<table cellpadding="8" cellspacing="0"
style="border-collapse:collapse;width:100%;">

<tr>
<td><b>Debit ID</b></td>
<td>{debit_id}</td>
</tr>

<tr>
<td><b>Lender</b></td>
<td>{lender}</td>
</tr>

<tr>
<td><b>EMI Amount</b></td>
<td>₹ {emi.amount:,.2f}</td>
</tr>

<tr>
<td><b>Due Date</b></td>
<td>{emi.due_date.strftime("%d-%m-%Y")}</td>
</tr>

</table>

<p>
Please ensure your payment is completed on or before the due date to avoid penalties.
</p>

<hr>

<p>
Thank you for choosing <b>GulbeeLedger</b>.
</p>

<p>
Regards,<br>
<b>GulbeeLedger Team</b>
</p>



<hr>

<p style="font-size:12px;color:#777;">
This is an automated email from GulbeeLedger.
Please do not reply to this email.
</p>
</div>

</body>
</html>
"""

            try:
                # Send reminder email
                send_mail(
                    subject=subject,
                    message=text_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[emi.user.email],
                    html_message=html_message,
                    fail_silently=False,
                )

                # Mark reminder as sent only if email was sent successfully
                emi.reminder_5_days_sent = True
                emi.save(update_fields=["reminder_5_days_sent"])

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ 5-Day Reminder Sent -> {emi.user.email}"
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Failed to send 5-day reminder to {emi.user.email}"
                    )
                )
                self.stdout.write(
                    self.style.ERROR(str(e))
                )
                continue

        # ============================================================
        # FIND EMIs DUE TODAY
        # ============================================================

        due_today_emis = EMI.objects.select_related(
            "user",
            "debit"
        ).filter(
            due_date=today,
            status=EmiStatus.PENDING,
            reminder_due_day_sent=False
        )

        self.stdout.write(
            f"Today's Reminder EMIs Found : {due_today_emis.count()}"
        )

        # ============================================================
        # SEND DUE TODAY REMINDER
        # ============================================================

        for emi in due_today_emis:

            debit_id = emi.debit.debit_id if emi.debit else "N/A"
            lender = emi.debit.lender_name if emi.debit else "N/A"




            subject = "🚨 EMI Due Today - Payment Required"

            text_message = f"""
Dear {emi.user.first_name},

This is an important reminder that your EMI payment is due TODAY.

-------------------------------------------------
Debit ID      : {debit_id}
Lender        : {lender}
EMI Amount    : ₹{emi.amount:,.2f}
Due Date      : {emi.due_date.strftime("%d-%m-%Y")}
-------------------------------------------------

Please complete your payment today to avoid late fees and penalties.

Thank you for using GulbeeLedger.

Regards,
GulbeeLedger Team
"""

            html_message = f"""
<html>
<body style="font-family:Arial,sans-serif;background:#f4f4f4;padding:20px;">

<div style="background:white;padding:25px;border-radius:8px;max-width:650px;margin:auto;">

<h2 style="color:#dc3545;">
EMI Due Today
</h2>

<p>Dear <b>{emi.user.first_name}</b>,</p>

<p>
Your EMI payment is
<b style="color:red;">Due Today</b>.
</p>

<table cellpadding="8" cellspacing="0"
style="border-collapse:collapse;width:100%;">

<tr>
<td><b>Debit ID</b></td>
<td>{debit_id}</td>
</tr>

<tr>
<td><b>Lender</b></td>
<td>{lender}</td>
</tr>

<tr>
<td><b>EMI Amount</b></td>
<td>₹ {emi.amount:,.2f}</td>
</tr>

<tr>
<td><b>Due Date</b></td>
<td>{emi.due_date.strftime("%d-%m-%Y")}</td>
</tr>

</table>

<p>
Please complete your EMI payment today to avoid late charges.
</p>

<hr>

<p>
Thank you for choosing <b>GulbeeLedger</b>.
</p>

<p>
Regards,<br>
<b>GulbeeLedger Team</b>
</p>


<hr>

<p style="font-size:12px;color:#777;">
This is an automated email from GulbeeLedger.
Please do not reply to this email.
</p>
</div>

</body>
</html>
"""

            try:
                send_mail(
                    subject=subject,
                    message=text_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[emi.user.email],
                    html_message=html_message,
                    fail_silently=False,
                )

                # Mark reminder as sent only after successful email delivery
                emi.reminder_due_day_sent = True
                emi.save(update_fields=["reminder_due_day_sent"])

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Due Date Reminder Sent -> {emi.user.email}"
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Failed to send due date reminder to {emi.user.email}"
                    )
                )
                self.stdout.write(
                    self.style.ERROR(
                        f"Reason: {e}"
                    )
                )

                # Skip this EMI and continue with the next one
                continue

        # ============================================================
        # END OF COMMAND
        # ============================================================

        self.stdout.write("=" * 60)
        self.stdout.write(
            self.style.SUCCESS("EMI Reminder Command Finished Successfully")
        )
        self.stdout.write("=" * 60)