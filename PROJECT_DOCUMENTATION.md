# EMI Reminder Email System
Project: GulbeeLedger

Last Updated:
06 August 2026

Author:
Thomas

---

# Purpose

This document explains the entire EMI Reminder Email architecture,
why specific technologies were chosen,
what problems were encountered,
why some solutions were rejected,
and how to maintain this system in the future.

This file exists so future maintenance becomes easier and no time is wasted
debugging problems that have already been solved.

---

# Goal

Automatically send reminder emails

• 5 Days Before EMI Due Date
• On EMI Due Date

without requiring

- Website to be open
- User to be logged in
- Browser running

The reminder must work even if nobody visits the website.

---

# Final Architecture

User
        │
        ▼
Render Cron Job
(Daily Scheduled Request)
        │
        ▼
Protected Internal URL
/emi/internal/jobs/send-emi-reminders/
        │
        ▼
Management Command
send_emi_reminders
        │
        ▼
Brevo HTTP API
        │
        ▼
Recipient Email

---

# Why Cron?

A web application only executes code when requests arrive.

No visitor
=
No code execution.

Therefore reminders cannot happen automatically.

Cron triggers the reminder endpoint once every day.

---

# Why not Background Thread?

Rejected.

Reason:

Render Free instances sleep.

Threads stop when the instance sleeps.

Not reliable.

---

# Why not Celery?

Initially considered.

Rejected because:

Requires

- Redis
- Celery Worker
- Celery Beat

Advantages

- Very scalable
- Queue support

Disadvantages

- Extra infrastructure
- More deployment complexity
- Additional services to monitor

Current project requirements are simple daily reminders.

Celery would unnecessarily increase complexity.

---

# Why not APScheduler?

Rejected.

Reason:

Runs inside the web process.

If Render restarts or sleeps

Scheduler stops.

Not reliable.

---

# Why not Linux Cron on Render?

Render Free instances do not provide OS-level cron access.

Instead Render provides Cron Jobs.

Those trigger an HTTP endpoint.

---

# Initial Email Method

SMTP

Configuration:

smtp-relay.brevo.com

Port:

587

Worked perfectly on

- localhost

Failed on

Render Free

Reason

Render blocks outbound SMTP ports

25

465

587

for Free Web Services.

SMTP connection always timed out.

No issue with Django.

No issue with credentials.

Platform restriction.

---

# Final Email Method

Brevo Transactional Email HTTP API

Advantages

Works on Render Free

No SMTP ports

HTTPS only

Fast

Reliable

Officially supported by Brevo

---

# Why HTTP API is Better

SMTP

Requires

- Port 587
- TLS
- SMTP Authentication

HTTP API

Uses

HTTPS

Port 443

Render allows HTTPS traffic.

No blocked ports.

---

# Email Sending Utility

Location

exp_tracker/utils/brevo_mail.py

Reason

Email sending is a project-level utility.

It may be used by multiple apps.

Keeping it inside an app like emi would tightly couple it.

Project utilities are reusable.

---

# Management Command

Location

emi/management/commands/send_emi_reminders.py

Responsibilities

Find EMIs

Send reminders

Update reminder flags

Prevent duplicate reminders

Log every action

---

# Reminder Flags

Database fields

reminder_5_days_sent

reminder_due_day_sent

Purpose

Prevent duplicate emails.

Once successfully sent

field becomes

True

Future cron executions ignore that EMI.

---

# Security

Cron endpoint is protected.

Requires

X-CRON-TOKEN

Header

Requests without the token

Return

401 Unauthorized

---

# Environment Variables

Current required variables

SECRET_KEY

DEBUG

ALLOWED_HOSTS

Database

DB_NAME

DB_USER

DB_PASSWORD

DB_HOST

DB_PORT

Email

BREVO_API_KEY

DEFAULT_FROM_EMAIL

Cron

CRON_JOB_SECRET

---

# Email Provider

Brevo

Used for

Transactional Emails

Website

https://www.brevo.com/

---

# Brevo API Key

Created

06 August 2026

Expected Expiry

06 August 2027

Before expiry

Generate a new API key

Update

BREVO_API_KEY

inside Render Environment Variables

Redeploy

Delete the old key after confirming the new one works.

---

# Testing

Create EMI

↓

Run

curl

↓

Endpoint executes

↓

Check logs

↓

Verify

Brevo Response

↓

Database flag becomes True

↓

Recipient receives email

---

# Successful Log Example

Sending 5-day reminder to:

user@example.com

Brevo Response

{'messageId': '...'}

✓ Reminder Sent

This confirms

Brevo accepted the email.

---

# Manual Trigger

curl -X POST \
-H "X-CRON-TOKEN: YOUR_SECRET" \
https://gulbee-ledger.onrender.com/emi/internal/jobs/send-emi-reminders/

---

# Future Improvements

Possible future upgrades

• Email templates

• Retry mechanism

• Email history table

• Dashboard showing sent reminders

• SMS reminders

• WhatsApp reminders

• Push notifications

• Celery if large-scale scheduling becomes necessary

---

# Maintenance Notes

If emails stop working

Check

1. Render deployment

2. BREVO_API_KEY

3. CRON_JOB_SECRET

4. Cron schedule

5. Reminder flags

6. Brevo account status

7. Brevo daily quota

8. Render logs

---

# Current Status

SMTP

❌ Not Used

Reason

Blocked by Render Free

Brevo SMTP

❌ Not Used

Reason

SMTP ports blocked

Brevo HTTP API

✅ Active

Render Cron

✅ Active

Management Command

✅ Active

Protected Endpoint

✅ Active

Duplicate Prevention

✅ Active

Production Ready

✅ Yes

---

End of Document

Last Updated

06 August 2026 (the api expire on 06 August 2027)

Author

Thomas