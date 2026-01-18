# Arogya Hospital Management System

## Project Overview

Arogya is a comprehensive Hospital Management System (HMS) designed to streamline administrative and clinical operations within healthcare facilities. The application enables seamless interaction between administrators, doctors, and patients through a unified and secure web interface.

Built using a server-side rendering architecture with Flask and Jinja2, the system emphasizes performance, security, and scalability. The user interface is styled with Tailwind CSS to ensure responsiveness and accessibility. Arogya addresses essential healthcare workflows such as role-based access control, appointment scheduling, and digital medical record management.

---

## Key Features

### 1. Role-Based Access Control (RBAC)

The system enforces strict authentication and authorization across three core user roles:

- **Administrators**
  - Manage doctors and patients
  - Monitor hospital operations
  - Configure system-level settings

- **Doctors**
  - Manage appointment schedules
  - Access patient medical histories
  - Issue digital diagnoses and prescriptions

- **Patients**
  - Book and manage appointments
  - View personal medical records
  - Track treatment and prescription history

---

### 2. Appointment Scheduling System

Doctors define their availability through configurable time slots. The scheduling engine validates all appointment requests against real-time availability, preventing conflicts and ensuring efficient utilization of medical resources.

---

### 3. Electronic Health Records (EHR)

Arogya digitizes the complete patient treatment lifecycle. Medical records, diagnoses, and prescriptions are securely stored and remain permanently accessible for future reference, improving continuity of care.

---

### 4. Responsive User Interface

The application is built with Tailwind CSS, delivering a consistent and responsive experience across desktops, tablets, and mobile devices. A dark-mode-first design reduces eye strain for medical professionals during extended working hours.

---

## Technology Stack

### Backend & Core Logic
- **Language:** Python 3.10+
- **Framework:** Flask
- **Authentication:** Session-based authentication (Werkzeug Security)
- **Database:** MongoDB (PyMongo) or SQLAlchemy (configurable)

### Frontend & UI
- **Templating Engine:** Jinja2 (Server-Side Rendering)
- **CSS Framework:** Tailwind CSS
- **JavaScript:** Vanilla JavaScript (DOM manipulation and async requests)

---

## Installation and Setup

Follow the steps below to run the project locally.

### Prerequisites
- Python 3.8 or higher
- pip (Python Package Installer)
- Git

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/sharancreates/hospital-management-system.git
cd hospital-management-system
```
### Step 2: Create a venv

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Create a .env file in the project root and add the following variables:
```bash
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secure_secret_key
DATABASE_URI=your_database_connection_string
```

### Step 5: Run the application
```bash
python app.py
```

### Project Structure

Directory structure:
└── sharancreates-hospital-management-system/
    ├── README.md
    ├── app.py
    ├── config.py
    ├── db_setup.py
    ├── extensions.py
    ├── models.py
    ├── package.json
    ├── requirements.txt
    ├── seed.py
    ├── routes/
    │   ├── __init__.py
    │   ├── admin_routes.py
    │   ├── auth_routes.py
    │   ├── doctor_routes.py
    │   └── patient_routes.py
    ├── static/
    │   ├── style.css
    │   └── src/
    │       └── input.css
    └── templates/
        ├── base.html
        ├── login.html
        ├── admin/
        │   ├── add_appointment.html
        │   ├── add_doctor.html
        │   ├── admin_base.html
        │   ├── dashboard.html
        │   ├── update_doctor.html
        │   ├── update_patient.html
        │   └── view_treatment.html
        ├── doctor/
        │   ├── dashboard.html
        │   ├── doctor_base.html
        │   ├── patient_history.html
        │   ├── set_availability.html
        │   ├── treatment.html
        │   └── view_treatment.html
        └── patient/
            ├── add_appointment.html
            ├── dashboard.html
            ├── doctor_profile.html
            ├── patient_base.html
            ├── patient_details.html
            ├── register.html
            ├── update_patient.html
            └── view_treatment.html

git clone https://github.com/YOUR_USERNAME/arogya-hms.git
cd arogya-hms
