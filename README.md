<div align="center">

# Arogya — Hospital Management System

**A secure, full-stack Hospital Management System built with React and Flask, featuring healthcare interoperability through HL7 v2 and FHIR standards.**

[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)](https://react.dev/)
[![Flask](https://img.shields.io/badge/Flask-Python-000000?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io/)
[![HL7](https://img.shields.io/badge/HL7-v2-E8412A?style=flat-square)](https://www.hl7.org/)
[![FHIR](https://img.shields.io/badge/FHIR-R4-FF6600?style=flat-square)](https://hl7.org/fhir/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[Live Demo](https://arogya-hms-sharancreates.vercel.app/) · [Report a Bug](https://github.com/sharancreates/hospital-management-system/issues) · [Request a Feature](https://github.com/sharancreates/hospital-management-system/issues)

![Arogya HMS Dashboard Preview](<img width="1516" height="700" alt="image" src="https://github.com/user-attachments/assets/56a90b53-56cc-44db-ac25-2c8d8e1ddd6c" />
)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Healthcare Interoperability](#healthcare-interoperability)
- [Performance](#performance)
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
- **HL7 v2 ADT** — generates A01 (Admit), A02 (Transfer), A03 (Discharge) segments
- **FHIR R4** — exports Patient, Encounter, and Condition resources as compliant JSON
- Designed to integrate with external EHR platforms via standard messaging

---

## Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| React 18 (Vite) | SPA framework |
| TailwindCSS | Utility-first styling |
| React Router 6 | Client-side routing |
| React Hook Form + Zod | Form management and schema validation |
| React Context API | Global state management |
| Socket.IO Client | Real-time updates |

### Backend
| Technology | Purpose |
|---|---|
| Python + Flask | RESTful API server |
| Flask-SQLAlchemy | ORM and database abstraction |
| PostgreSQL | Primary production database |
| SQLite | Development / test database |
| Alembic | Database migration management |
| Celery + Redis | Async background task processing |
| Waitress / Gunicorn | WSGI production server |

### DevOps & Testing
| Technology | Purpose |
|---|---|
| GitHub Actions | CI/CD pipeline |
| pytest | Backend unit and integration tests |
| Docker | Containerised local development |

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
│  └───────────────────────────────┘                      │
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
- Python ≥ 3.10
- PostgreSQL ≥ 14
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

Start the Flask API:

```bash
flask run
# or for production:
waitress-serve --port=5000 app:create_app()
```

### 3. Start Celery worker

In a separate terminal (with venv activated):

```bash
celery -A app.celery worker --loglevel=info
```

### 4. Set up the frontend

```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:5173`.

### Demo Credentials

| Role | Email | Password |
|---|---|---|
| Patient | patient@demo.com | demo1234 |
| Doctor | doctor@demo.com | demo1234 |
| Admin | admin@demo.com | demo1234 |

---

## Environment Variables

Create a `.env` file in `/backend` using `.env.example` as a template:

```env
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/arogya_db

# Redis / Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-here
JWT_ACCESS_TOKEN_EXPIRES=3600

# Mail (for appointment reminders)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your@email.com
MAIL_PASSWORD=your-app-password
```

---

## Healthcare Interoperability

Arogya implements two major healthcare data standards for clinical data exchange:

### HL7 v2 ADT Messages

The export module generates ADT (Admit, Discharge, Transfer) messages conforming to HL7 v2.5 specifications. Example A01 (Admit) segment structure:

```
MSH|^~\&|AROGYA|FACILITY|EHR|DEST|20240101120000||ADT^A01|MSG001|P|2.5
EVN|A01|20240101120000
PID|1||P00123^^^AROGYA||Doe^John||19900101|M|||123 Main St^^City^ST^10001
PV1|1|I|ICU^101^A|||DR001^Smith^Jane|||SUR|||||||||V001
```

### FHIR R4 Resources

Clinical data is exportable as FHIR R4 JSON bundles containing Patient, Encounter, and Condition resources:

```json
{
  "resourceType": "Patient",
  "id": "P00123",
  "name": [{ "family": "Doe", "given": ["John"] }],
  "birthDate": "1990-01-01",
  "gender": "male",
  "address": [{ "line": ["123 Main St"], "city": "City", "postalCode": "10001" }]
}
```

These exports allow Arogya to act as a data source for external EHR platforms, telemedicine systems, and health information exchanges (HIEs).

---

## Performance

One of the more interesting engineering challenges was the **appointment reminder dispatch latency**.

The initial implementation used Python's standard threading model to dispatch reminders. Under load, database session locking caused reminder jobs to queue behind each other, resulting in dispatch latencies of **up to 32 seconds**.

**Solution:** Replaced the threading approach with Celery workers backed by Redis as the message broker. Each reminder job is now dispatched independently as an async task, fully decoupled from the request lifecycle.

**Result: Dispatch latency dropped from 32 seconds → 20 milliseconds** — a ~1,600× improvement.

---

## Security

Arogya implements multiple layers of security appropriate for a healthcare platform:

| Layer | Implementation |
|---|---|
| Authentication | JWT tokens with expiry and refresh rotation |
| Authorisation | Role-based access control (RBAC) — Patient, Doctor, Admin |
| CSRF Protection | Flask-WTF CSRF tokens on all state-changing requests |
| API Rate Limiting | Flask-Limiter with per-endpoint and per-IP thresholds |
| Session Security | Secure, HttpOnly, SameSite cookie flags |
| Input Validation | Zod (frontend) + Marshmallow/Pydantic (backend) |
| Password Storage | bcrypt hashing with per-user salt |

---

## CI/CD

GitHub Actions runs on every push and pull request to `main`:

```yaml
# .github/workflows/ci.yml
- Lint: flake8 (Python), ESLint (JS)
- Test: pytest with coverage report
- Build: Vite production build check
```

To run tests locally:

```bash
# Backend
cd backend
pytest --cov=app tests/

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
│   │   ├── components/        # Shared UI components
│   │   ├── pages/             # Route-level page components
│   │   │   ├── patient/       # Patient dashboard views
│   │   │   ├── doctor/        # Doctor dashboard views
│   │   │   └── admin/         # Admin dashboard views
│   │   ├── context/           # React Context providers
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API call abstractions
│   │   └── utils/             # Helpers and validators
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── routes/            # Flask Blueprint routes
│   │   │   ├── auth.py
│   │   │   ├── appointments.py
│   │   │   ├── inpatient.py
│   │   │   ├── billing.py
│   │   │   └── export.py      # HL7 + FHIR export endpoints
│   │   ├── tasks/             # Celery background tasks
│   │   ├── services/          # Business logic layer
│   │   └── utils/
│   │       ├── hl7_builder.py # HL7 v2 segment generator
│   │       └── fhir_builder.py # FHIR R4 JSON builder
│   ├── migrations/            # Alembic migration files
│   ├── tests/                 # pytest test suite
│   └── requirements.txt
│
└── .github/
    └── workflows/
        └── ci.yml
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

</div>
