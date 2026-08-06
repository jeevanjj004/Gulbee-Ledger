# Gulbee Ledger

A Django-based ledger and loan management system for tracking income, expenses, debit accounts, and EMI repayments with automated EMI generation, scheduled reminder emails, and comprehensive financial reports.

---

# 🚀 Features

- **User Authentication**
  - Secure login and logout system
  - Session-based authentication

- **Income Management**
  - Add, edit, delete, and view income records
  - Search and filter income entries

- **Expense Management**
  - Record daily expenses
  - Update and delete expenses
  - Search and filter expenses

- **Debit (Loan) Management**
  - Add and manage debit/loan details
  - Track lenders and repayment information
  - View complete debit history

- **Automated EMI Generation**
  - Automatically generates EMI schedules from debit entries
  - Supports installment tracking
  - Tracks pending and paid EMIs

- **Automated Email Reminder System**
  - Sends reminder emails **5 days before EMI due date**
  - Sends reminder emails **on the EMI due date**
  - Duplicate reminder prevention
  - Secure internal cron endpoint
  - Uses **Brevo Transactional Email API**
  - Works automatically without user interaction

- **Dashboard**
  - Financial summary
  - Income overview
  - Expense overview
  - Active debit summary
  - Pending EMI statistics

- **Reports**
  - Export reports as PDF
  - Export reports as Excel
  - Income reports
  - Expense reports
  - Debit reports
  - EMI reports

- **Search & Filtering**
  - Filter by dates
  - Search records
  - View categorized financial data

- **Background Automation**
  - Daily scheduled EMI reminder execution
  - Internal protected job endpoint
  - Automated database updates after successful reminders

---

# 🛠️ Tech Stack

### Backend

- Python
- Django 5
- Django ORM

### Database

- PostgreSQL (Supabase)

### Frontend

- HTML
- CSS
- JavaScript
- Bootstrap

### Deployment

- Render

### Email Service

- Brevo Transactional Email API

### Server

- Gunicorn
- WhiteNoise

---

# 💻 Installation / Setup

```bash
# Clone the repository
git clone https://github.com/jeevanjj004/Gulbee-Ledger.git

# Navigate to project folder
cd Gulbee-Ledger

# Create virtual environment
python -m venv venv

# Activate virtual environment

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver

# Open browser
http://127.0.0.1:8000/
```

---

# 🔐 Environment Variables

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=your_secret_key

DEBUG=True

ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=5432

BREVO_API_KEY=your_brevo_api_key

DEFAULT_FROM_EMAIL=your_verified_sender_email

CRON_JOB_SECRET=your_secure_random_secret
```

---

# 📧 Automated EMI Reminder System

The project includes a fully automated reminder system.

### Reminder Types

- Reminder sent **5 days before** EMI due date
- Reminder sent **on the EMI due date**

### Features

- Prevents duplicate emails
- Uses Brevo HTTP API
- Secure internal endpoint protected by a secret token
- Updates reminder status after successful delivery
- Can be scheduled using Render Cron Jobs or any external scheduler

---

# 📁 Project Structure

```
Gulbee-Ledger/

├── debit/
├── emi/
├── expense/
├── income/
├── reports/
├── user/
├── exp_tracker/
│   ├── settings.py
│   ├── urls.py
│   └── utils/
│       └── brevo_mail.py
├── templates/
├── static/
├── media/
├── manage.py
└── requirements.txt
```

---

# 📊 Main Modules

- User Management
- Income Management
- Expense Management
- Debit Management
- EMI Management
- Reports
- Email Reminder Service

---

# 🔒 Security

- Environment variables for sensitive credentials
- Secure internal cron endpoint using authentication token
- Session-based authentication
- CSRF protection
- Django security middleware

---

# 🚀 Deployment

Production deployment uses

- Render Web Service
- Supabase PostgreSQL
- Gunicorn
- WhiteNoise
- Brevo Transactional Email API

---

# 📌 Future Enhancements

- SMS Notifications
- WhatsApp Notifications
- Push Notifications
- Analytics Dashboard
- Budget Planning
- Monthly Financial Insights
- Mobile Application
- Multi-user Organization Support

---

# 👨‍💻 Author

**Thomas Jacob**

GitHub:
https://github.com/jeevanjj004

---

# ⭐ Project Status

✅ Active Development

Current Version includes:

- Income Management
- Expense Management
- Debit Management
- Automated EMI Generation
- Scheduled EMI Reminder Emails
- PDF & Excel Reports
- Render Deployment
- Supabase PostgreSQL
- Brevo Email Integration
- Secure Cron Endpoint
