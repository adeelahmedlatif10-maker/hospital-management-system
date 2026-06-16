📄 Project Description
The Hospital Management System (HMS) is a full-stack web application built with Django and MySQL, designed to digitise and streamline the day-to-day operations of a hospital. It covers the complete patient journey — from registration and appointment scheduling through laboratory testing to billing — while enforcing strict role-based access so that Admins, Doctors, Receptionists, and Lab Technicians each see only the data and actions relevant to their role.

Built as a learning-phase capstone project, HMS demonstrates practical application of relational database design, Django ORM-free raw SQL integration, session-based authentication, and modular Django app architecture.

🚀 Features
User Roles
•	Admin — full system access, user management
•	Doctor — patient records, appointments, test orders
•	Receptionist — patient registration, appointment booking
•	Lab Technician — test record entry and result management
Core Modules
•	Patient Management — registration, demographic records, blood group tracking
•	Doctor Management — specialisation profiles linked to user accounts
•	Appointment Scheduling — status tracking (Scheduled → Confirmed → Completed / Cancelled)
•	Laboratory & Tests — multi-lab test catalogue with fee management and result recording
•	Billing & Payments — auto-aggregated bills (consultation + test fees) with payment status
•	Activity Logging — timestamped audit trail for all significant actions
•	Role-based Authentication — session handling with per-role dashboards

🛠️ Tech Stack
Layer	Technology
Backend	Django 6.x (Python)
Database	MySQL 8+ via mysqlclient / PyMySQL
Frontend	Django Templates · HTML5 · CSS3 · Bootstrap
REST API	Django REST Framework 3.15
CORS	django-cors-headers 4.3
Version Control	Git & GitHub

🗄️ Database Schema
The HMS database (hms) contains eight tables with enforced foreign-key relationships:

Table	Purpose
ROLES	Stores the four system roles
USERS	Login credentials linked to a role
DOCTORS	Doctor profiles (name, specialisation) linked to a user
PATIENTS	Patient demographics with age/gender/blood-group constraints
APPOINTMENT	Appointment records linking patient ↔ doctor with status & fee
LABORATORY	Lab entities (name)
TESTS	Test catalogue with fee, linked to a lab
TEST_RECORDS	Test results per patient/doctor/test with status tracking
BILLS	Aggregated billing (consultation + test fees) per patient
ACTIVITY_LOG	Audit log of user actions with timestamps

📁 Project Structure
Hospital_managment/
├── HMSapp/
│   ├── patients_app/      # Patient CRUD views & models
│   ├── doctors_app/       # Doctor management
│   ├── users_app/         # Authentication & session handling
│   ├── appointments_app/  # Appointment scheduling
│   ├── payments_app/      # Billing logic
│   ├── tests_app/         # Lab tests & records
│   ├── roles_app/         # Role definitions
│   └── templates/         # Django HTML templates (Bootstrap)
├── manage.py
├── activity_logger.py     # Global audit logging utility
├── requirements.txt
├── setup.bat              # One-click Windows installer
└── run.bat                # One-click Windows launcher

⚙️ Installation & Setup
Prerequisites
•	Python 3.10 or higher (add to PATH during install)
•	MySQL 8.0 or higher running locally
•	Git
Option A — Automated (Windows)
Run the provided batch script; it handles virtualenv creation, dependency installation, and migrations:
setup.bat
Option B — Manual
1.  Clone the repository:
git clone https://github.com/adeelahmedlatif10-maker/hospital-management-system.git
2.  Create and activate a virtual environment:
python -m venv venv && venv\Scripts\activate
3.  Install dependencies:
pip install -r requirements.txt
4.  Create the MySQL database and run the schema:
mysql -u root -p < HMS_DB.sql
5.  Configure your credentials in settings.py (see Database Configuration below).
6.  Start the development server:
python manage.py runserver

🔧 Database Configuration
Open hms/settings.py and update the DATABASES block:
DATABASES = {
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hms',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

🔐 Authentication
•	Session-based login — credentials validated against the USERS table
•	Each role maps to a dedicated dashboard with restricted navigation
•	Passwords stored as hashed values (Django's built-in hashing pipeline)
•	ACTIVITY_LOG records every significant add / update / delete action with the acting username and timestamp

📌 Future Improvements
•	React.js frontend (replace Django templates)
•	REST API layer using Django REST Framework
•	JWT / OAuth2 authentication
•	Cloud deployment (AWS / Railway / Heroku)
•	Improved UI/UX design system
•	Django ORM migration (replace raw SQL)
•	Automated test suite (pytest-django)

👨‍💻 Developer
Adeel Ahmed Latif
Student — National University of Technology (NUTECH)
Learning Phase  — Open to feedback, contributions, and collaboration!

📜 License
This project is released under the MIT License. See the LICENSE file for full terms.
