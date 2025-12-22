from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from datetime import date, timedelta
from emi.models import EMI


class Command(BaseCommand):
    help = 'Send EMI reminder emails 5 days before due date and on due date'

    def handle(self, *args, **kwargs):
        today = date.today()
        five_days_before = today + timedelta(days=5)

        # =====================================================
        # 5 DAYS BEFORE DUE DATE REMINDER
        # =====================================================
        five_day_emis = EMI.objects.select_related('user', 'debit').filter(
            due_date=five_days_before,
            status='pending',
            reminder_5_days_sent=False
        )

        for emi in five_day_emis:
            debit_id = emi.debit.debit_id if emi.debit else "N/A"
            lender = emi.debit.lender_name if emi.debit else "N/A"

            subject = "⏰ EMI Payment Reminder – Upcoming Due Date"

            text_message = (
                f"Dear {emi.user.first_name},\n\n"
                f"This is a reminder that your EMI payment is due in 5 days.\n\n"
                f"Debit ID: {debit_id}\n"
                f"Lender: {lender}\n"
                f"Amount: ₹{emi.amount}\n"
                f"Due Date: {emi.due_date}\n\n"
                f"Please ensure timely payment to avoid late fees or penalties.\n\n"
                f"Regards,\n"
                f"GulbeeLedger Team"
            )

            html_message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2 style="color:#2c3e50;">EMI Payment Reminder</h2>

                <p>Dear <strong>{emi.user.first_name}</strong>,</p>

                <p>
                    This is a friendly reminder that your EMI payment is
                    <strong style="color:#e67e22;">due in 5 days</strong>.
                </p>

                <table style="border-collapse: collapse;">
                    <tr>
                        <td><strong>Debit ID</strong></td>
                        <td style="padding-left:10px;">{debit_id}</td>
                    </tr>
                    <tr>
                        <td><strong>Lender</strong></td>
                        <td style="padding-left:10px;">{lender}</td>
                    </tr>
                    <tr>
                        <td><strong>EMI Amount</strong></td>
                        <td style="padding-left:10px;">₹ {emi.amount}</td>
                    </tr>
                    <tr>
                        <td><strong>Due Date</strong></td>
                        <td style="padding-left:10px; color:#d35400;">
                            {emi.due_date}
                        </td>
                    </tr>
                </table>

                <p>
                    Kindly complete the payment on or before the due date to avoid
                    <strong>late fees or penalties</strong>.
                </p>

                <p style="margin-top:30px;">
                    Regards,<br>
                    <strong>GulbeeLedger</strong><br>
                    <small>EMI & Expense Management System</small>
                </p>
            </body>
            </html>
            """

            send_mail(
                subject,
                text_message,
                'gulbeeledger@gmail.com',
                [emi.user.email],
                html_message=html_message
            )

            emi.reminder_5_days_sent = True
            emi.save(update_fields=['reminder_5_days_sent'])

            self.stdout.write(self.style.SUCCESS(
                f"5-day reminder sent to {emi.user.email}"
            ))

        # =====================================================
        # DUE DATE REMINDER (TODAY)
        # =====================================================
        due_today_emis = EMI.objects.select_related('user', 'debit').filter(
            due_date=today,
            status='pending',
            reminder_due_day_sent=False
        )

        for emi in due_today_emis:
            debit_id = emi.debit.debit_id if emi.debit else "N/A"
            lender = emi.debit.lender_name if emi.debit else "N/A"

            subject = "🚨 EMI Due Today – Immediate Attention Required"

            text_message = (
                f"Dear {emi.user.first_name},\n\n"
                f"Your EMI payment is due TODAY.\n\n"
                f"Debit ID: {debit_id}\n"
                f"Lender: {lender}\n"
                f"Amount: ₹{emi.amount}\n"
                f"Due Date: {emi.due_date}\n\n"
                f"Please make the payment today to avoid penalties or service issues.\n\n"
                f"Regards,\n"
                f"GulbeeLedger Team"
            )

            html_message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2 style="color:#c0392b;">EMI Due Today</h2>

                <p>Dear <strong>{emi.user.first_name}</strong>,</p>

                <p>
                    This is to notify you that your EMI payment is
                    <strong style="color:#c0392b;">due today</strong>.
                </p>

                <table style="border-collapse: collapse;">
                    <tr>
                        <td><strong>Debit ID</strong></td>
                        <td style="padding-left:10px;">{debit_id}</td>
                    </tr>
                    <tr>
                        <td><strong>Lender</strong></td>
                        <td style="padding-left:10px;">{lender}</td>
                    </tr>
                    <tr>
                        <td><strong>EMI Amount</strong></td>
                        <td style="padding-left:10px;">₹ {emi.amount}</td>
                    </tr>
                    <tr>
                        <td><strong>Due Date</strong></td>
                        <td style="padding-left:10px; color:#c0392b;">
                            {emi.due_date}
                        </td>
                    </tr>
                </table>

                <p style="margin-top:15px;">
                    Please complete the payment today to avoid
                    <strong>late fees, penalties, or service disruption</strong>.
                </p>

                <p style="margin-top:30px;">
                    Regards,<br>
                    <strong>GulbeeLedger</strong><br>
                    <small>EMI & Expense Management System</small>
                </p>
            </body>
            </html>
            """

            send_mail(
                subject,
                text_message,
                'gulbeeledger@gmail.com',
                [emi.user.email],
                html_message=html_message
            )

            emi.reminder_due_day_sent = True
            emi.save(update_fields=['reminder_due_day_sent'])

            self.stdout.write(self.style.SUCCESS(
                f"Due-date reminder sent to {emi.user.email}"
            ))
