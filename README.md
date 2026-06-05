# Arogya — Hospital Management System

A secure, full-stack Hospital Management System built with React 19 and Flask, featuring healthcare interoperability through HL7 v2 and FHIR standards.

[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react)](https://react.dev/)
[![Flask](https://img.shields.io/badge/Flask-Python-000000?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io/)
[![HL7](https://img.shields.io/badge/HL7-v2-E8412A?style=flat-square)](https://www.hl7.org/)
[![FHIR](https://img.shields.io/badge/FHIR-R4-FF6600?style=flat-square)](https://hl7.org/fhir/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[Live Demo](https://arogya-hms-sharancreates.vercel.app/) · [Report a Bug](https://github.com/sharancreates/hospital-management-system/issues) · [Request a Feature](https://github.com/sharancreates/hospital-management-system/issues)

Dashboard preview:
<img width="1516" height="717" alt="image" src="https://github.com/user-attachments/assets/3020ff61-e728-4f5d-b80b-44f47fda0984" />

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Healthcare Interoperability](#healthcare-interoperability)
- [Performance & Optimizations](#performance--optimizations)
- [Security](#security)
- [CI/CD](#cicd)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Arogya is a production-grade Hospital Management System that coordinates the full lifecycle of hospital operations — from patient registration and appointment scheduling to inpatient bed management, billing, and clinical data export.

Built as a Single Page Application on the frontend and a modular RESTful API on the backend, Arogya supports three distinct user roles (Patient, Doctor, Administrator) with role-based dashboards, real-time ward occupancy tracking, and PDF prescription generation.

What sets Arogya apart from typical HMS projects is its **healthcare interoperability layer** — the system generates compliant **HL7 v2 ADT segments** and **FHIR R4 Patient/Encounter JSON** resources, allowing clinical data to be exchanged with external EHR and EMR platforms using industry-standard formats.

---

## Key Features

### Patient Dashboard
- Book, reschedule, and cancel appointments online
- View consultation history and active prescriptions
- Download PDF prescriptions and billing invoices
- Real-time appointment status updates via WebSocket

### Doctor Dashboard
- View and manage daily appointment queue
- Write and digitally sign prescriptions (auto-generated as PDF)
- Access complete patient consultation history
- Admit patients to wards and manage inpatient care

### Admin Dashboard
- Real-time bed occupancy dashboard across ICU, General, and Private wards
- Insurance claims processing and payment status management
- User and role management across the system
- HL7 and FHIR clinical data export controls

### Healthcare Interoperability
- **HL7 v2 ADT** — generates A08 (Update) segments and formats clinical data with MSH/PID segments
- **FHIR R4** — exports Patient resources as compliant JSON
- Designed to integrate with external EHR platforms via standard messaging

---

## Tech Stack

### Frontend
- **React 19 (Vite)**: SPA framework
- **TailwindCSS**: Utility-first styling
- **React Router 7**: Client-side routing
- **React Hook Form + Zod**: Form management and schema validation
- **React Context API**: Global state management
- **Socket.IO Client**: Real-time updates
- **Recharts**: Data visualization & analytics

### Backend
- **Python + Flask**: RESTful API server
- **Flask-SQLAlchemy**: ORM and database abstraction
- **PostgreSQL**: Primary production database
- **SQLite**: Development / test database
- **Alembic (Flask-Migrate)**: Database migration management
- **Celery + Redis**: Async background task processing
- **Waitress / Gunicorn**: WSGI production servers

### DevOps & Testing
- **GitHub Actions**: CI/CD pipeline
- **pytest**: Backend unit and integration tests
- **Docker**: Containerised local development

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     React SPA (Vite)                    │
│         Patient · Doctor · Admin Dashboards             │
└──────────────────────┬──────────────────────────────────┘
                       │ REST + WebSocket
┌──────────────────────▼──────────────────────────────────┐
│              Flask RESTful API (Python)                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │Scheduling│ │Inpatient │ │ Billing  │ │  Export   │  │
│  │ Module   │ │  Module  │ │  Module  │ │  Module   │  │
│  └──────────┘ └──────────┘ └──────────┘ └─────┬─────┘  │
│                                               │         │
│                                    ┌──────────▼──────┐  │
│                                    │  HL7 v2 + FHIR  │  │
│  ┌───────────────────────────────┐ │  R4 Generators  │  │
│  │     Celery Workers + Redis    │ └─────────────────┘  │
│  │  (Background task processing) │                      │
│  └───────────────────────────────┐                      │
└──────────────────────┬──────────────────────────────────┘
                       │
              ┌────────▼────────┐
              │   PostgreSQL    │
              └─────────────────┘
```

---

## Getting Started

### Prerequisites

- Node.js ≥ 18
- Python ≥ 3.11
- PostgreSQL ≥ 15
- Redis ≥ 7

### 1. Clone the repository

```bash
git clone https://github.com/sharancreates/hospital-management-system.git
cd hospital-management-system
```

### 2. Set up the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Run database migrations:

```bash
flask db upgrade
```

Start the Flask API production server:

```bash
python run_prod.py
```

### 3. Start Celery worker

In a separate terminal (with venv activated):

```bash
celery -A celery_app.celery worker --loglevel=info
```

### 4. Set up the frontend

```bash
cd ../frontend
npm install
npm run dev
```

The application will be available at `http://localhost:5173`.

### Demo Credentials

| Role | Email | Password |
|---|---|---|
| Patient | pat1@gmail.com | pat123 |
| Doctor | doc1@arogya.com | doc123 |
| Admin | admin@arogya.com | adminadmin123 |

---

## Environment Variables

Create a `.env` file in `/backend` using `.env.example` as a template:

```env
# Flask
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/arogya_db

# Redis / Celery / Socket.IO
REDIS_URL=redis://localhost:6379/0

# Mail (for appointment reminders)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your@email.com
MAIL_PASSWORD=your-app-password
```

---

## Healthcare Interoperability

Arogya implements major healthcare data standards for clinical data exchange:

### HL7 v2 Messages
The export module generates valid `MSH` and `PID` segments conforming to HL7 v2 specifications for clinical updates.

### FHIR R4 Resources
Clinical data is exportable as FHIR R4 JSON containing structured patient resource schemas.

These exports allow Arogya to interface with external EMR platforms, telemedicine systems, and health exchanges.

---

## Performance & Optimizations

### 1. Appointment Reminder Latency
The initial implementation used Python's standard threading model to dispatch reminders. Under load, database session locking caused reminder jobs to queue behind each other, resulting in dispatch latencies of **up to 32 seconds**.

- **Solution**: Replaced the local threading approach with Celery workers backed by Redis as the message broker. Each reminder job is now dispatched independently as an async task, fully decoupled from the request lifecycle.
- **Result**: Dispatch latency dropped from **32 seconds to 20 milliseconds** (~1,600× improvement).

### 2. Patient API N+1 Query Fix
- **Problem**: Loading the patient dashboard initially ran separate lazy-load queries for every single appointment's doctor and treatment details, causing massive backend latency. Similarly, checking slot availability queried the database for every single individual slot.
- **Solution**: Implemented eager loading (`joinedload`) for all relational models on the dashboard and consolidated availability checks into a single grouped query (`func.count` grouped by date/time).
- **Result**: Reduced database roundtrips for availability checks from `O(N)` down to `O(1)`.

---

## Security

Arogya implements multiple layers of security appropriate for a healthcare platform:

| Layer | Implementation |
|---|---|
| Authentication | Token-based session authentication serialized via `itsdangerous` |
| Authorisation | Role-based access control (RBAC) — Patient, Doctor, Admin |
| CSRF Protection | Flask-WTF CSRF tokens on all state-changing requests |
| API Rate Limiting | Flask-Limiter with per-endpoint and per-IP thresholds |
| Session Security | Secure, HttpOnly, SameSite cookie flags |
| Input Validation | Zod (frontend) + built-in custom schemas (backend) |
| Password Storage | bcrypt hashing with per-user salt |

---

## CI/CD

GitHub Actions runs on every push and pull request to `main`:
- **Lint**: ESLint (JS)
- **Test**: pytest with coverage report
- **Build**: Vite production build check

To run tests locally:

```bash
# Backend
cd backend
pytest backend/tests

# Frontend
cd frontend
npm run lint
npm run build
```

---

## Project Structure

```
hospital-management-system/
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Page components
│   │   │   └── admin/         # Sub-components/panels for the Admin dashboard
│   │   ├── context/           # App state contexts (auth context)
│   │   ├── App.jsx            # Main app router
│   │   ├── api.ts             # Axios API client configuration
│   │   ├── main.jsx           # App entrypoint
│   │   └── index.css          # Global Tailwind styles
│   └── package.json
│
├── backend/
│   ├── app.py                 # Flask app factory
│   ├── config.py              # App configuration
│   ├── extensions.py          # Extension instances (db, socketio, cors, etc.)
│   ├── models.py              # SQLAlchemy DB models
│   ├── celery_app.py          # Celery configuration
│   ├── requirements.txt
│   ├── routes/                # Blueprint routes
│   │   ├── admin_routes.py
│   │   ├── auth_routes.py
│   │   ├── doctor_routes.py
│   │   ├── enterprise_routes.py
│   │   ├── health_routes.py
│   │   ├── patient_routes.py
│   │   └── utils.py
│   ├── services/              # Core business services
│   │   ├── admin_service.py
│   │   ├── audit_service.py
│   │   ├── doctor_service.py
│   │   ├── enterprise_service.py # Generates HL7 v2 and FHIR R4
│   │   ├── patient_service.py
│   │   └── reminders.py       # Dispatches reminders (Celery task & thread fallback)
│   ├── tests/                 # pytest test suite
│   └── run_prod.py            # Waitress production script
```

---

## Contributing

Contributions are welcome. Please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

Built by [Sharanya Nagar](https://sharanyanagar.vercel.app/) · [LinkedIn](https://linkedin.com/in/sharanya-nagar)

*If this project helped you, a ⭐ on GitHub goes a long way.*
