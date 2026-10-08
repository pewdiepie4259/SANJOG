# SANJOG
### Surplus Food Redistribution & Community Connection Platform

![SANJOG Banner](https://img.shields.io/badge/SANJOG-Surplus%20Food%20Redistribution-166534?style=for-the-badge)
![Django Version](https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-PostGIS-4169E1?style=for-the-badge&logo=postgresql)
![Celery](https://img.shields.io/badge/Celery-Async%20Tasks-37814A?style=for-the-badge&logo=celery)
![HTMX](https://img.shields.io/badge/HTMX-Dynamic%20UI-336699?style=for-the-badge)

---

### 1. PROJECT OVERVIEW
**SANJOG** is a multi-role, real-time, geo-intelligent surplus food redistribution platform engineered to bridge the gap between commercial food establishments (restaurants, hotels, messes, caterers) with edible surplus food and non-profit organizations (NGOs, shelters, orphanages) serving food-insecure communities. Supported by on-demand volunteer logistics and central platform administration, SANJOG automates surplus food discovery, claim verification, safe transport, and social impact tracking.

---

### 2. PROBLEM STATEMENT
Thousands of kilograms of untouched, high-quality edible food are discarded daily by commercial food businesses due to over-preparation, event cancellations, or short shelf lives. Simultaneously, local charitable organizations struggle with severe food budget shortages. Traditional redistribution fails due to:
- Lack of real-time visibility before food spoils.
- Transport logistics bottlenecks for NGOs without vehicles.
- Absence of chain-of-custody verification and food safety accountability.

---

### 3. THE SANJOG SOLUTION
SANJOG introduces a streamlined digital platform combining:
- **Geospatial PostGIS Matching:** Receivers discover surplus food within 2km to 15km radii.
- **Live Spoilage Countdown:** Automated timers flagging food as `SAFE`, `WARNING`, `URGENT`, or `EXPIRED`.
- **Dual-Stage OTP Verification:** Cryptographic 4-digit handoffs (Donor → Volunteer → Receiver) preventing fake pickers.
- **Automated CSR Certificates:** Instant PDF impact receipts generated for corporate donors upon successful delivery.

---

### 4. KEY FEATURES
1. **Multi-Role RBAC System:** Role-restricted dashboards for Donors, Receivers, Volunteers, and Admins.
2. **Organization Document Verification:** Mandatory admin review of FSSAI and NGO registration certificates before platform activation.
3. **Interactive Leaflet.js GIS Mapping:** Urgency-coded map markers dynamically updated via HTMX without full-page reloads.
4. **Atomic Claim Locking:** Database transaction locking (`select_for_update`) ensuring zero double-claiming.
5. **Asynchronous Background Processing:** Celery + Redis automated task execution for food auto-expiry checks, email alerts, and PDF rendering.
6. **Impact & CSR Dashboard:** Real-time metrics tracking total meals saved, food weight diverted (kg), and CO2 emission offset.

---

### 5. USER ROLES
- 🍲 **DONOR:** Restaurants, Hotels, Messes, Caterers. (Create listings, validate pickup OTP, download CSR certificates).
- 🏥 **RECEIVER:** NGOs, Shelters, Orphanages, Community Kitchens. (Discover nearby food, claim listings, validate delivery OTP).
- 🚴 **VOLUNTEER:** Community delivery partners. (Accept pickup requests, navigate using maps, execute dual OTP handoffs).
- 🛡️ **ADMIN:** Platform governance. (Approve/reject organizations, monitor live state machine, inspect audit logs).

---

### 6. SYSTEM WORKFLOW
```
[DONOR] Create Listing + Safety Checklist
   │
   ▼
[SYSTEM] Status: AVAILABLE (Live Spoilage Clock Started)
   │
   ▼
[RECEIVER] Discovers via Map (Filter Radius) ──► Claims Food
   │
   ▼
[SYSTEM] Status: CLAIMED (Atomic Transaction Lock)
   │
   ▼
[VOLUNTEER] Accepts Task ──► Status: PICKUP_ASSIGNED
   │
   ▼
[DONOR & VOLUNTEER] Handoff at Pickup Location ──► Verify Pickup OTP ──► Status: PICKED_UP
   │
   ▼
[VOLUNTEER & RECEIVER] Handoff at Receiver Location ──► Verify Delivery OTP ──► Status: DELIVERED
   │
   ▼
[SYSTEM] Update Impact Metrics + Generate PDF CSR Certificate
```

---

### 7. TECHNOLOGY STACK

#### Backend
- **Language:** Python 3.11+
- **Framework:** Django 5.x
- **API Framework:** Django REST Framework (DRF)
- **Database:** PostgreSQL 16 with PostGIS 3.4 spatial extension
- **Task Queue & Cache:** Celery + Redis

#### Frontend
- **Templating:** Django Templates
- **Interactivity:** HTMX (AJAX DOM updates without heavy JS SPA frameworks)
- **Styling:** Tailwind CSS (Utility-first responsive design)
- **Mapping:** Leaflet.js + OpenStreetMap tiles

#### Utilities & Security
- **PDF Generation:** WeasyPrint / ReportLab
- **Authentication:** Django Custom User Model + JWT / Session RBAC
- **Deployment Target:** Gunicorn + Nginx on VPS / Railway / Render

---

### 8. PROJECT ARCHITECTURE & STRUCTURE

```
sanjog/
├── config/                  # Django project configuration (settings, urls, wsgi, celery)
├── accounts/                # Custom User Model & RBAC Authentication
├── organizations/           # Donor, Receiver, Volunteer Profiles & Verification
├── food/                    # Surplus Food Listing & Spoilage Engine
├── claims/                  # Claim Management & Atomic Locking System
├── pickups/                 # Volunteer Dispatch, Transport & OTP Verification Engine
├── notifications/           # In-app & Email Notification System
├── analytics/               # Real-Time Impact Aggregation & Metrics
├── certificates/            # WeasyPrint PDF CSR Certificate Generator
├── templates/               # Django HTML Templates (HTMX integration)
├── static/                  # CSS (Tailwind), JS (Leaflet setup), Images
├── media/                   # Uploaded Organization Documents & Food Images
├── tests/                   # Automated PyTest / Django Test Suite
├── manage.py                # Django CLI tool
└── requirements.txt         # Project dependencies
```

---

### 9. DATABASE OVERVIEW (POSTGIS)
SANJOG stores geographical locations using PostGIS geography points (`GEOGRAPHY(POINT,4326)`).
Primary entities:
- `CustomUser` & `OrganizationProfile`
- `OrganizationDocument` & `VolunteerProfile`
- `FoodListing` (Stores PostGIS point, expiry time, safety checklist)
- `Claim`, `PickupRequest`, `OTPVerification`, `Delivery`
- `DonationCertificate`, `AuditLog`, `ImpactRecord`

---

### 10. API ENDPOINTS OVERVIEW

| Method | Endpoint URL | Description | Auth / Role |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register/` | Register user account | Public |
| `POST` | `/api/v1/auth/login/` | Authenticate user & receive tokens | Public |
| `GET` | `/api/v1/food/` | Public food listings feed | Public |
| `GET` | `/api/v1/food/nearby/` | Spatial PostGIS nearby food lookup | Receiver |
| `POST` | `/api/v1/food/` | Create surplus food listing | Verified Donor |
| `POST` | `/api/v1/claims/` | Atomic claim execution | Verified Receiver |
| `POST` | `/api/v1/pickups/<id>/verify-pickup/` | Validate donor pickup OTP | Volunteer/Donor |
| `POST` | `/api/v1/pickups/<id>/verify-delivery/` | Validate receiver delivery OTP | Volunteer/Receiver |
| `GET` | `/api/v1/analytics/impact/` | Global impact statistics | Public |
| `GET` | `/api/v1/certificates/<id>/download/` | Download PDF CSR receipt | Donor/Admin |

---

### 11. INSTALLATION & LOCAL ENVIRONMENT SETUP (WINDOWS / VS CODE)

#### Prerequisites
1. Python 3.11+ installed and added to PATH.
2. PostgreSQL 16+ with PostGIS extension installed locally.
3. Redis Server running locally or via Docker/Memurai.
4. VS Code (Recommended editor).

#### Step 1: Clone Repository & Create Virtual Environment
```bash
# Open Terminal / PowerShell in VS Code
cd f:\SANJOG

# Create Python Virtual Environment
python -m venv venv

# Activate Virtual Environment (Windows)
venv\Scripts\activate
```

#### Step 2: Install Project Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 3: Configure Environment Variables
Create a `.env` file in the root directory `f:\SANJOG\.env`:
```env
DEBUG=True
SECRET_KEY=django-insecure-sanjog-dev-key-change-in-production-2026
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=sanjog_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://127.0.0.1:6379/0
CELERY_BROKER_URL=redis://127.0.0.1:6379/0

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

#### Step 4: PostgreSQL + PostGIS Database Setup
In PostgreSQL Command Line (`psql`) or pgAdmin:
```sql
CREATE DATABASE sanjog_db;
\c sanjog_db;
CREATE EXTENSION IF NOT EXISTS postgis;
```

#### Step 5: Run Database Migrations & Create Superuser
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

#### Step 6: Start Celery Worker & Scheduler (Separate Terminals)
```bash
# Terminal 2 (Activate venv first)
celery -A config worker --loglevel=info -P threads

# Terminal 3 (Activate venv first)
celery -A config beat --loglevel=info
```

#### Step 7: Run Django Development Server
```bash
python manage.py runserver
```
Visit application at: `http://127.0.0.1:8000/`

---

### 12. RUNNING AUTOMATED TESTS
Execute the full test suite using PyTest:
```bash
pytest
```
Or run native Django tests:
```bash
python manage.py test
```

---

### 13. SCREENSHOTS PLACEHOLDER
- `[Screenshot: Public Landing Page & Live Impact Counter]`
- `[Screenshot: Leaflet.js Interactive Discovery Map with Urgency Markers]`
- `[Screenshot: Donor Food Listing Form & Safety Checklist]`
- `[Screenshot: Receiver Claim Confirmation Modal]`
- `[Screenshot: Volunteer Mobile OTP Verification Interface]`
- `[Screenshot: Generated PDF CSR Impact Certificate]`
- `[Screenshot: Admin Verification Queue & Audit Logs]`

---

### 14. SECURITY & COMPLIANCE
- Zero plain-text OTP storage (Salted SHA-256 in Redis TTL cache).
- OWASP Top 10 mitigation (CSRF, XSS auto-escaping, parameterized ORM queries).
- Role-based permissions enforcing document verification before transaction access.

---

### 15. CONTRIBUTORS & CREDITS
- **Lead Software Architect & PM:** Senior Architecture Team
- **Stack:** Django, PostGIS, Celery, Redis, HTMX, Tailwind CSS, Leaflet.js

---

### 16. LICENSE
This project is licensed under the MIT License — see the `LICENSE` file for details.
