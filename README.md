# SANJOG
### Intelligent Food Rescue Operating System (Food Rescue OS)

![SANJOG Banner](https://img.shields.io/badge/SANJOG-Food%20Rescue%20OS-166534?style=for-the-badge)
![Django Version](https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-PostGIS-4169E1?style=for-the-badge&logo=postgresql)
![Celery](https://img.shields.io/badge/Celery-Async%20Tasks-37814A?style=for-the-badge&logo=celery)
![HTMX](https://img.shields.io/badge/HTMX-Dynamic%20UI-336699?style=for-the-badge)

---

### 1. PROJECT OVERVIEW
**SANJOG** is an **Intelligent Food Rescue Operating System (Food Rescue OS)** engineered to connect commercial food establishments (**Donors**) with charitable institutions (**Receivers**) and volunteer logistics partners (**Volunteers**) under centralized platform governance (**Admin**). Moving beyond passive donation marketplaces, SANJOG automates surplus food discovery, safety SOP compliance, need-first matching, multi-recipient allocation splitting, chain-of-custody tracking via digital Food Passports, and dynamic SLA urgency escalation.

---

### 2. THE 6 STRATEGIC PILLARS
1. **PREDICT:** AI/ML demand & surplus forecasting predicting meal requirements before surplus occurs.
2. **RESCUE:** Structured Food Safety SOP assessment ensuring 100% edible compliance (`ELIGIBLE`, `REVIEW_REQUIRED`, `NOT_ELIGIBLE`).
3. **MATCH:** Need-First deterministic weighted scoring algorithm matching surplus to active receiver demand (`DemandRequest`).
4. **ROUTE:** Multi-Recipient Rescue Allocation Engine (`RescueAllocation`) splitting large donations across multiple receivers.
5. **VERIFY:** Dual-stage cryptographic 4-digit OTP handoff (Donor → Volunteer → Receiver).
6. **PROVE:** Digital Food Passport chain-of-custody ledger, transactional Impact Ledger, and downloadable WeasyPrint PDF CSR certificates.

---

### 3. KEY FEATURES
- **Need-First Receiver Demand Requests:** Receivers proactively register live meal needs.
- **Multi-Recipient Rescue Allocations:** Atomically split 500+ meals across multiple shelters with PostgreSQL `select_for_update()` reservation locks.
- **Digital Food Passport:** Chain-of-custody tracking with SHA-256 state hashing.
- **Tiered Rescue SLA Urgency:** Dynamic SLA monitoring (`NORMAL` <2h, `URGENT` <60m, `CRITICAL` <30m).
- **PostGIS Spatial Matching:** Real-time distance querying using PostGIS geography points (`GEOGRAPHY(POINT,4326)`).
- **Interactive Leaflet.js Maps:** Urgency-coded map markers updated dynamically via HTMX.
- **Asynchronous Task Processing:** Celery + Redis workers for auto-expiries, SLA alerts, email notifications, and PDF rendering.

---

### 4. TECHNOLOGY STACK
- **Backend:** Python 3.11+, Django 5.x, Django REST Framework (DRF)
- **Database:** PostgreSQL 16 with PostGIS 3.4 spatial extension
- **Task Queue & Cache:** Celery + Redis
- **Frontend:** Django Templates + Tailwind CSS + HTMX + Leaflet.js
- **Machine Learning (P1):** Scikit-Learn / LightGBM
- **PDF Generation:** WeasyPrint / ReportLab

---

### 5. PROJECT ARCHITECTURE & STRUCTURE
```
sanjog/
├── config/             # Django project settings, URLs, WSGI, Celery
├── accounts/           # Custom User Model & RBAC Authentication
├── organizations/      # Profiles (Donor, Receiver, Volunteer) & Verification Queue
├── food/               # FoodListing, Safety SOP Assessment & Food Passport Ledger
├── demand/             # Receiver Need-First Demand Requests
├── rescue/             # Matching Engine & Multi-Recipient Allocations
├── pickups/            # Logistics, Transport Tasks & Dual OTP Verification
├── notifications/      # Async Email & In-App Alerts
├── analytics/          # Impact Ledger & Aggregated Metrics
├── certificates/       # WeasyPrint PDF CSR Certificate Generator
├── ml_engine/          # ML Surplus & Demand Forecasting (P1)
├── templates/          # Django HTML Templates (HTMX integration)
├── static/             # CSS (Tailwind), JS (Leaflet), Images
├── media/              # Uploaded Organization Documents & Food Images
├── tests/              # Automated PyTest / Django Test Suite
├── manage.py           # Django CLI tool
└── requirements.txt    # Project dependencies
```

---

### 6. API ENDPOINTS OVERVIEW

| Method | Endpoint URL | Description | Auth / Role |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register/` | Register user account | Public |
| `POST` | `/api/v1/auth/login/` | Authenticate user & receive tokens | Public |
| `POST` | `/api/v1/demand/` | Log active receiver meal demand | Verified Receiver |
| `POST` | `/api/v1/food/` | Post surplus food + Safety SOP | Verified Donor |
| `POST` | `/api/v1/rescue/match/` | Trigger matching algorithm for listing | System / Admin |
| `POST` | `/api/v1/rescue/allocations/` | Create multi-recipient allocations | Receiver / System |
| `GET` | `/api/v1/food/<id>/passport/` | Fetch immutable Food Passport JSON | Any Authenticated |
| `POST` | `/api/v1/pickups/<id>/verify-pickup/` | Validate donor pickup OTP | Volunteer / Donor |
| `POST` | `/api/v1/pickups/<id>/verify-delivery/` | Validate receiver delivery OTP | Volunteer / Receiver |
| `GET` | `/api/v1/analytics/ledger/` | Authoritative impact metrics feed | Public |
| `GET` | `/api/v1/certificates/<id>/download/` | Download PDF CSR receipt | Donor / Admin |

---

### 7. LOCAL ENVIRONMENT SETUP (WINDOWS / VS CODE)

#### Step 1: Clone & Create Virtual Environment
```bash
cd f:\SANJOG
python -m venv venv
venv\Scripts\activate
```

#### Step 2: Install Project Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 3: Configure Environment Variables (`.env`)
```env
DEBUG=True
SECRET_KEY=django-insecure-sanjog-dev-key-2026
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=sanjog_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://127.0.0.1:6379/0
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
```

#### Step 4: PostgreSQL + PostGIS Setup
```sql
CREATE DATABASE sanjog_db;
\c sanjog_db;
CREATE EXTENSION IF NOT EXISTS postgis;
```

#### Step 5: Database Migrations & Superuser
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

#### Step 6: Start Celery & Development Server
```bash
# Terminal 2: Celery Worker
celery -A config worker --loglevel=info -P threads

# Terminal 3: Celery Beat Scheduler
celery -A config beat --loglevel=info

# Terminal 1: Django Server
python manage.py runserver
```
Visit application at: `http://127.0.0.1:8000/`

---

### 8. TESTING & LICENSE
- Run PyTest: `pytest`
- License: MIT License
