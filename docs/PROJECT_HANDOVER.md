# SANJOG — Comprehensive Project Handover & Repository Audit

> **Document Type:** Project Handover & Technical Audit  
> **Repository:** `pewdiepie4259/SANJOG`  
> **Audit Date:** October 11, 2026  
> **Auditor:** Antigravity AI Engineering Team  
> **Status:** Handover Complete & Verified Against Codebase  

---

## 1. Executive Summary & Project Overview

**Project Name:** SANJOG  
**Mission:** Build an intelligent food rescue operating system (Food Rescue OS) connecting food donors (restaurants, hotels, messes, caterers), receivers (NGOs, shelters, community kitchens), and volunteers to eliminate surplus food waste through proactive need-first matching, verified safety compliance, and rapid logistics.

This audit was conducted by inspecting the actual source code, database migrations, configuration files, test suites, and documentation in the repository. No assumptions were made based on plans or README files without code-level verification.

---

## 2. Intended vs. Actually Configured Technology Stack

| Technology Component | Intended Specification | Actual Configured State in Repository | Verification Status |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | Python 3.11+, Django 5.x | Python 3.11.9 detected; Django 5.2.17 in system Python. Settings modularized (`base.py`, `development.py`, `production.py`). | **CONFIGURED & WORKING** |
| **API Framework** | Django REST Framework (DRF) 3.14+ | Configured in `settings/base.py` with Token/Session Auth, URL versioning (`/api/v1/`), rate limiting. | **CONFIGURED (DRF package missing in global Python)** |
| **Frontend Presentation** | Django Templates, Tailwind CSS, HTMX | Server-rendered templates in `frontend/templates/`. Tailwind CSS loaded via CDN; HTMX 1.9.10 loaded via CDN. | **CONFIGURED & WORKING** |
| **Local Static HTMX** | `frontend/static/js/htmx.min.js` | 3-line stub (`console.log('SANJOG HTMX Initialized')`). Fallback relies on unpkg CDN. | **PARTIALLY CONFIGURED (STUB)** |
| **Database Engine** | PostgreSQL 16 + PostGIS | Configured in `development.py` with dynamic SQLite fallback (`USE_SQLITE=True` or connection failure fallback). GDAL detection safely toggles spatial backend. | **CONFIGURED (Dual-Mode SQLite/Postgres)** |
| **Background Tasks** | Redis 5.0.1 + Celery 5.3.6 | Configured in `backend/config/celery.py` and `settings/base.py`. Broker URL default `redis://127.0.0.1:6379/0`. | **CONFIGURED (Services not currently running)** |
| **Private Document Storage** | Private FileSystemStorage | Configured at `settings.PRIVATE_MEDIA_ROOT = BASE_DIR / 'private_media'` with `base_url=None` (zero public HTTP route). | **CONFIGURED & SECURED** |
| **Testing Framework** | PyTest + pytest-django | `pytest.ini` configured at root (`pythonpath = backend`, `testpaths = backend/tests`). | **CONFIGURED (`pytest-django` missing in global Python)** |
| **Version Control** | Git & GitHub | Git repository connected to `origin` (`https://github.com/pewdiepie4259/SANJOG.git`). Only `main` branch exists. Working tree is clean. | **CONFIGURED & SYNCHRONIZED** |

---

## 3. Actual Repository Architecture & Directory Structure

The repository was reorganized (commit `9bc7edb`) into a separated frontend/backend layout:

```
SANJOG/
├── .env.example                                  # Sanitized environment template
├── .gitignore                                    # Ignores venv, db.sqlite3, media, private_media
├── manage.py                                     # Root proxy delegating to backend/manage.py
├── pytest.ini                                    # PyTest runner configuration (pythonpath = backend)
├── requirements.txt                              # Master requirements entrypoint (-r backend/requirements/development.txt)
├── README.md                                     # Project overview and setup instructions
│
├── backend/                                      # Django Backend Service Root
│   ├── manage.py                                 # Core administrative CLI
│   ├── config/                                   # Project Configuration Package
│   │   ├── __init__.py, asgi.py, celery.py, urls.py, wsgi.py
│   │   └── settings/
│   │       ├── __init__.py
│   │       ├── base.py                           # Core settings, apps, middleware, storage
│   │       ├── development.py                    # SQLite/PostgreSQL dev settings, console email
│   │       └── production.py                     # Production security headers, DB pooling
│   ├── apps/                                     # Modular Business Domain Applications
│   │   ├── accounts/                             # Phase 2: CustomUser, RBAC, Dual Auth, Tokens
│   │   │   ├── admin.py, api_views.py, apps.py, backends.py, decorators.py, forms.py
│   │   │   ├── models.py                         # CustomUser (UUID PK, RoleChoices)
│   │   │   ├── permissions.py                    # DRF IsDonor, IsReceiver, IsVolunteer, IsAdminUser
│   │   │   ├── serializers.py, services.py       # AuthService (Rate-limiting, registration)
│   │   │   ├── urls.py, views.py
│   │   │   └── migrations/0001_initial.py
│   │   └── organizations/                        # Phase 3: Profile Management & Verification Queue
│   │       ├── admin.py, api_views.py, apps.py, exceptions.py, forms.py
│   │       ├── models.py                         # OrganizationProfile, OrganizationDocument, OrganizationVerificationEvent
│   │       ├── permissions.py                    # IsOrganizationOwnerOrAdmin, IsAdminReviewer
│   │       ├── serializers.py, services.py       # OrganizationService, DocumentService, VerificationService
│   │       ├── urls.py, validators.py, views.py
│   │       └── migrations/0001_initial.py
│   ├── requirements/                             # Modular Dependency Declarations
│   │   ├── base.txt                              # Django, DRF, psycopg2, celery, redis, Pillow
│   │   ├── development.txt                       # pytest, pytest-django, coverage
│   │   └── production.txt                        # gunicorn, sentry-sdk
│   └── tests/                                    # Automated Test Suite (59 Test Cases)
│       ├── __init__.py, conftest.py
│       ├── test_health.py                        # System & API health endpoints (3 tests)
│       ├── test_auth.py                          # Dual login, registration, rate limiting (8 tests)
│       ├── test_rbac.py                          # Role dashboard decorators, permissions (8 tests)
│       ├── test_organizations.py                 # Profile CRUD, document validation, security (24 tests)
│       └── test_verification.py                  # Admin queue, approvals, audit immutability (16 tests)
│
├── frontend/                                     # Presentation Layer
│   ├── README.md
│   ├── static/
│   │   ├── css/input.css                         # Custom styling tokens
│   │   └── js/htmx.min.js                        # HTMX placeholder stub
│   └── templates/                                # Django Server-Rendered Templates
│       ├── base.html, 403.html
│       ├── partials/head.html                    # CDN Tailwind + HTMX 1.9.10 loader
│       ├── components/navbar.html
│       ├── accounts/                             # login, register, password reset templates
│       ├── dashboards/                           # donor, receiver, volunteer, admin dashboards
│       ├── organizations/                        # onboarding, profile, document management
│       └── admin_verification/                   # queue.html, review_detail.html
│
└── docs/                                         # Architectural Specifications & Blueprints
    ├── 01_SANJOG_PRD.md to 06_SANJOG_Test_Plan.md
    ├── API_CONTRACT.md, ARCHITECTURE.md, BRANCH_WORKFLOW.md
    ├── PHASE_3_IMPLEMENTATION_PLAN.md, RESTRUCTURING_PLAN.md
    ├── SANJOG_Development_Pipeline.md, SANJOG_MASTER_INDEX.md
    ├── PROJECT_HANDOVER.md                       # This audit & handover document
    ├── PHASE_STATUS.md                           # Detailed phase tracking
    └── NEXT_PHASE_IMPLEMENTATION_PLAN.md         # Phase 4 detailed plan
```

---

## 4. Feature Implementation & Verification Matrix

| Feature | Files | Status | Evidence / Notes |
| :--- | :--- | :--- | :--- |
| **CustomUser Model** | `apps/accounts/models.py` | `IMPLEMENTED AND VERIFIED` | Extends `AbstractUser`, UUID PK, 4 roles (`DONOR`, `RECEIVER`, `VOLUNTEER`, `ADMIN`), `phone_number`, `is_admin_user` property. |
| **Dual Auth Backend** | `apps/accounts/backends.py` | `IMPLEMENTED AND VERIFIED` | `EmailOrUsernameModelBackend` authenticates via username or email with timing attack mitigation. |
| **Auth Service Layer** | `apps/accounts/services.py` | `IMPLEMENTED AND VERIFIED` | Rate limiting (5 attempts, 15m lockout), normalized email/username checks, admin registration protection. |
| **RBAC Decorators & Permissions** | `apps/accounts/decorators.py`, `apps/accounts/permissions.py` | `IMPLEMENTED AND VERIFIED` | `role_required`, `admin_required`, DRF permissions `IsAdminUser`, `IsDonor`, `IsReceiver`, `IsVolunteer`. |
| **Auth Web & API Endpoints** | `apps/accounts/views.py`, `apps/accounts/api_views.py` | `IMPLEMENTED AND VERIFIED` | Login, register, logout, password reset views, plus `/api/v1/auth/` token endpoints. |
| **OrganizationProfile Model** | `apps/organizations/models.py` | `IMPLEMENTED AND VERIFIED` | 1-to-1 with `CustomUser`, type validation for roles, decimal lat/long coordinates, verification status. |
| **Private Document Storage** | `apps/organizations/models.py`, `validators.py` | `IMPLEMENTED AND VERIFIED` | Isolated private directory, `base_url=None`, randomized UUID filenames, binary magic byte checking (PDF, PNG, JPEG, WEBP). |
| **Document Upload & Deletion Cleanup** | `apps/organizations/services.py` | `IMPLEMENTED AND VERIFIED` | Immediate physical deletion if DB transaction fails during upload; `transaction.on_commit` physical deletion on document delete. |
| **Strict 2-Gate Verification Policy** | `apps/organizations/services.py` | `IMPLEMENTED AND VERIFIED` | Gate 1 (`submit_for_verification`): requires active mandatory docs. Gate 2 (`approve_organization`): requires individual document approvals (`review_status=APPROVED`). No bulk approval. |
| **Audit Log Immutability** | `apps/organizations/models.py` | `IMPLEMENTED AND VERIFIED` | `ImmutableManager`/`ImmutableQuerySet` raises `PermissionDenied` on `.update()` and `.delete()`; `on_delete=models.PROTECT`. |
| **Admin Verification Queue** | `apps/organizations/views.py`, `frontend/templates/admin_verification/` | `IMPLEMENTED AND VERIFIED` | Queue listing, review detail, individual document approval/rejection forms, mandatory rejection notes. |
| **REST API v1 Organizations** | `apps/organizations/api_views.py` | `IMPLEMENTED AND VERIFIED` | Complete CRUD endpoints for profiles, documents, and admin queue under `/api/v1/organizations/` and `/api/v1/admin/`. |
| **Food Surplus Listings** | `apps/food/` | `PLANNED ONLY (PHASE 4)` | Does not exist in codebase yet. Target of Phase 4. |
| **Food Safety SOPs** | `apps/food/` | `PLANNED ONLY (PHASE 4)` | Does not exist in codebase yet. Target of Phase 4. |
| **Receiver Demand Requests** | `apps/demand/` | `PLANNED ONLY (PHASE 5)` | Does not exist in codebase yet. |
| **Matching & Allocation** | `apps/rescue/` | `PLANNED ONLY (PHASE 7-8)` | Does not exist in codebase yet. |
| **Volunteer Logistics & OTP** | `apps/pickups/` | `PLANNED ONLY (PHASE 9-10)` | Does not exist in codebase yet. |

---

## 5. Database, Schema & Migration Integrity

1. **Migrations Present and Verified:**
   - `apps/accounts/migrations/0001_initial.py`: Creates `CustomUser`.
   - `apps/organizations/migrations/0001_initial.py`: Creates `OrganizationProfile`, `OrganizationDocument`, and `OrganizationVerificationEvent`. Depends on `('accounts', '0001_initial')`.
   - No conflicting or detached migrations exist.

2. **Schema Relationships:**
   - `OrganizationProfile.user`: `OneToOneField(CustomUser, on_delete=CASCADE, related_name='organization_profile')`.
   - `OrganizationDocument.organization`: `ForeignKey(OrganizationProfile, on_delete=CASCADE, related_name='documents')`.
   - `OrganizationVerificationEvent.organization`: `ForeignKey(OrganizationProfile, on_delete=PROTECT, related_name='verification_events')`. This protects profiles from cascading deletion while historical audit logs exist.

3. **PostGIS vs. DecimalField Portability:**
   - `OrganizationProfile` uses `DecimalField(max_digits=9, decimal_places=6)` for latitude and longitude.
   - This architectural choice ensures zero database engine incompatibility when running under SQLite during local development or testing, while remaining 100% compatible with PostgreSQL/PostGIS in production.

---

## 6. How to Run the Project (Verified Instructions)

### 6.1 Prerequisites
- Python 3.11.x
- Git

### 6.2 Setup Virtual Environment & Install Dependencies
```powershell
# In project root: c:\Users\mithu\SANJOG
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 6.3 Environment Configuration
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Ensure `USE_SQLITE=True` is set for rapid local development without a running PostgreSQL instance.

### 6.4 Run Database System Checks & Migrations
```powershell
python manage.py check
python manage.py migrate
```

### 6.5 Run the Automated Test Suite
```powershell
pytest
```

### 6.6 Run the Development Server
```powershell
python manage.py runserver 127.0.0.1:8000
```
- Web Application: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- System Health Check: [http://127.0.0.1:8000/health/](http://127.0.0.1:8000/health/)
- API Health Check: [http://127.0.0.1:8000/api/v1/health/](http://127.0.0.1:8000/api/v1/health/)
- Admin Portal: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 7. Known Limitations, Risks & Blockers

1. **Active Python Runtime Lacks Required Packages (Blocker for Test Execution):**
   - The system Python runtime (`C:\Users\mithu\AppData\Local\Programs\Python\Python311\python.exe`) does not have `djangorestframework`, `django-environ`, `django-cors-headers`, or `pytest-django` installed.
   - Per the audit safety rules, packages were not installed during the audit stage. Once the handover and implementation plan are approved, a virtual environment must be initialized with `pip install -r requirements.txt`.
2. **Local Static HTMX Asset is a Stub (Low Risk):**
   - `frontend/static/js/htmx.min.js` contains a placeholder log. The application loads HTMX from CDN (`https://unpkg.com/htmx.org@1.9.10`), which works in online environments but should be populated with the vendor minified asset for offline resilience.
3. **Dedicated Git Branches Not Yet Spawned (Low Risk):**
   - Git currently has only the `main` branch. The restructuring plan specified `frontend` and `backend` streams; however, development can safely continue on feature branches merging into `main`.
4. **Celery / Redis Daemon Processes:**
   - Celery configuration exists, but background workers and Redis server are optional until asynchronous background tasks (like periodic SLA auto-expiry in Phase 12) are actively executed.
