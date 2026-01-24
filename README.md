# Gulbee Ledger
Django-based ledger and loan management system for tracking income, expenses, and loan repayments with automated EMI calculations and notifications.

---

## 🚀 Features
- **User Authentication:** Secure login and role-based access  
- **CRUD Operations:** Add, update, delete, and view income, expenses, and debit entries  
- **Automated EMI Generation:** EMIs automatically generated from debit entries  
- **Notifications:** Automatic reminders for due and upcoming payments (5 days before) using background tasks  
- **Reports:** Export income, expenses, and loan data in PDF and Excel formats  
- **Dashboard:** Interactive dashboard with filters and search for easy tracking  
- **Background Tasks:** Automated operations like notifications and EMI calculations  

---

## 🛠️ Tech Stack
- **Backend:** Python, Django  
- **Database:** MySQL  
- **Frontend:** HTML, CSS, JavaScript, Bootstrap  
- **Other:** Background tasks for notifications and automated processes  

---

## 💻 Installation / Setup
```bash
# Clone the repository
git clone https://github.com/jeevanjj004/Gulbee-Ledger.git

# Navigate to project folder
cd Gulbee-Ledger

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows
venv\Scripts\activate
# Linux / Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Run the development server
python manage.py runserver

# Open in browser
http://127.0.0.1:8000/
