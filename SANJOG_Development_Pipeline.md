# SANJOG — Development Pipeline & Implementation Roadmap
## Phase-by-Phase Execution Plan, Git Workflow & Milestone Pipeline

---

### 1. DEVELOPMENT PIPELINE OVERVIEW
This document provides an exhaustive, step-by-step implementation blueprint for building **SANJOG**. It breaks down the system into 20 distinct execution phases (Phase 0 to Phase 19), detailing exact Django apps, models, APIs, frontend screens, dependencies, and Definition of Done (DoD) for each stage.

---

### 2. EXECUTABLE DEVELOPMENT PHASES (PHASE 0 — PHASE 19)

#### PHASE 0 — Planning & Specification
- **Objective:** Finalize all requirements, database schemas, UI blueprints, and API contracts.
- **Tasks:** Review PRD, SRS, System Architecture, UI/UX specs, and Database Design documents.
- **Django Apps Involved:** N/A (Documentation phase).
- **Expected Output:** Complete set of 6 architectural documents + README + Pipeline.
- **Definition of Done (DoD):** All 6 documents approved and committed to git repo.

#### PHASE 1 — Project Infrastructure Setup
- **Objective:** Initialize Django 5.x project, Virtual Environment, PostgreSQL/PostGIS database, Celery, and Redis integration.
- **Tasks:** Set up `config/` app, install `requirements.txt`, configure PostGIS spatial backend, configure Tailwind CSS & HTMX static assets.
- **Django Apps Involved:** `config`, static assets setup.
- **Dependencies:** Python 3.11, PostgreSQL, PostGIS, Redis.
- **Expected Output:** Running Django app connecting to PostGIS and Redis without errors.
- **DoD:** `python manage.py migrate` executes cleanly; basic home template loads.

#### PHASE 2 — Authentication & RBAC Core
- **Objective:** Build custom user model, registration, login, logout, and role permission wrappers.
- **Tasks:** Create `accounts` app, extend `AbstractUser`, implement JWT & session login endpoints, build RBAC permission decorators.
- **Django Apps Involved:** `accounts`.
- **Models Involved:** `CustomUser`.
- **APIs Involved:** `/api/v1/auth/register/`, `/api/v1/auth/login/`, `/api/v1/users/me/`.
- **Frontend Screens:** Login Page (Page 5), Registration Page (Page 6).
- **DoD:** Users can register as Donor/Receiver/Volunteer/Admin and authenticate securely.

#### PHASE 3 — Organization Management & Document Verification
- **Objective:** Build organization profile registration and legal document upload workflow.
- **Tasks:** Create `organizations` app, implement document file upload sanitization, build Admin verification queue.
- **Django Apps Involved:** `organizations`.
- **Models Involved:** `OrganizationProfile`, `OrganizationDocument`.
- **APIs Involved:** `POST /api/v1/organizations/`, `PATCH /api/v1/organizations/<id>/verify/`.
- **Frontend Screens:** Org Profile Settings (Page 15, 24), Admin Verification Queue (Page 35).
- **DoD:** Donors/Receivers cannot post/claim food until profile status equals `VERIFIED`.

#### PHASE 4 — Donor Module & Surplus Food Posting
- **Objective:** Enable verified Donors to post surplus food entries with safety checklists.
- **Tasks:** Create `food` app, build `FoodListing` model, implement mandatory safety check validation.
- **Django Apps Involved:** `food`, `organizations`.
- **Models Involved:** `FoodListing`.
- **APIs Involved:** `POST /api/v1/food/`, `GET /api/v1/food/`.
- **Frontend Screens:** Donor Dashboard (Page 7), Create Food Listing (Page 8), My Donations (Page 9).
- **DoD:** Donors can post food listings with mandatory safety checklist validation.

#### PHASE 5 — Receiver Module & Discovery Engine
- **Objective:** Enable verified Receivers to view available food listings near their facility.
- **Tasks:** Create `claims` app, build receiver discovery dashboard and detail view.
- **Django Apps Involved:** `food`, `claims`, `organizations`.
- **Models Involved:** `FoodListing`, `Claim`.
- **Frontend Screens:** Receiver Dashboard (Page 16), Nearby Donations (Page 17), Food Details View (Page 19).
- **DoD:** Receivers can search and inspect food details.

#### PHASE 6 — Volunteer Module & Task Management
- **Objective:** Onboard individual volunteers and enable delivery availability toggles.
- **Tasks:** Create `pickups` app, build `VolunteerProfile` model, implement task feed.
- **Django Apps Involved:** `organizations`, `pickups`.
- **Models Involved:** `VolunteerProfile`, `PickupRequest`.
- **APIs Involved:** `GET /api/v1/volunteers/available/`, `POST /api/v1/volunteers/<id>/accept/`.
- **Frontend Screens:** Volunteer Dashboard (Page 25), Available Deliveries Feed (Page 26).
- **DoD:** Volunteers can view and accept delivery tasks.

#### PHASE 7 — Food Discovery & PostGIS Geolocation
- **Objective:** Implement spatial radius filtering and interactive Leaflet.js maps.
- **Tasks:** Configure PostGIS `ST_DWithin` spatial queries, render Leaflet markers with urgency colors.
- **Django Apps Involved:** `food`, `organizations`.
- **APIs Involved:** `GET /api/v1/food/nearby/`.
- **Frontend Screens:** Interactive Map Discovery View (Page 18).
- **DoD:** Receivers can filter listings by 2km, 5km, 10km, 15km radii with working map pins.

#### PHASE 8 — Claim & Atomic Locking System
- **Objective:** Implement atomic claim execution preventing race conditions.
- **Tasks:** Use PostgreSQL `select_for_update()` transaction locks when creating claims.
- **Django Apps Involved:** `claims`, `food`.
- **Models Involved:** `Claim`, `PickupRequest`.
- **APIs Involved:** `POST /api/v1/claims/`.
- **Frontend Screens:** Claim Confirmation Modal (Page 20), Receiver Active Claims (Page 21).
- **DoD:** Concurrent claims on the same listing return `409 Conflict` for the second attempt.

#### PHASE 9 — Pickup & Dual OTP Verification Engine
- **Objective:** Implement cryptographic 4-digit OTP handoff between Donor and Volunteer.
- **Tasks:** Build OTP generation service with Redis TTL cache and max 3-attempt limit.
- **Django Apps Involved:** `pickups`.
- **Models Involved:** `OTPVerification`, `PickupRequest`.
- **APIs Involved:** `POST /api/v1/pickups/<id>/verify-pickup/`.
- **Frontend Screens:** Pickup Tracking (Page 12), Pickup Verification Screen (Page 28).
- **DoD:** Valid Donor OTP transitions listing status to `PICKED_UP`.

#### PHASE 10 — Delivery Handoff Execution
- **Objective:** Implement 4-digit OTP handoff between Volunteer and Receiver.
- **Tasks:** Build delivery verification endpoint, record distance traveled, set status to `DELIVERED`.
- **Django Apps Involved:** `pickups`.
- **Models Involved:** `Delivery`, `PickupRequest`.
- **APIs Involved:** `POST /api/v1/pickups/<id>/verify-delivery/`.
- **Frontend Screens:** Delivery Tracking (Page 22), Delivery Verification Screen (Page 29).
- **DoD:** Valid Receiver OTP transitions status to `DELIVERED`.

#### PHASE 11 — Notification System (Email & In-App)
- **Objective:** Automated notifications for food availability, claims, and delivery completions.
- **Tasks:** Create `notifications` app, configure Celery email tasks.
- **Django Apps Involved:** `notifications`.
- **Models Involved:** `Notification`.
- **DoD:** Email and in-app alerts sent cleanly on state machine events.

#### PHASE 12 — Spoilage Countdown & Celery Auto-Expiry
- **Objective:** Real-time spoilage clock display and automated background listing expiration.
- **Tasks:** Celery Beat task scanning expired listings every 60 seconds.
- **Django Apps Involved:** `food`.
- **DoD:** Listings reaching expiry auto-update to `EXPIRED` within 60 seconds.

#### PHASE 13 — Impact Analytics Engine
- **Objective:** Aggregate platform metrics (meals saved, weight diverted, CO2 offset).
- **Tasks:** Create `analytics` app, build aggregation services.
- **Django Apps Involved:** `analytics`.
- **Models Involved:** `ImpactRecord`.
- **APIs Involved:** `GET /api/v1/analytics/impact/`.
- **Frontend Screens:** Donor Impact (Page 13), Admin Analytics (Page 39).
- **DoD:** Metrics accurately update after each delivered transaction.

#### PHASE 14 — CSR PDF Certificate System
- **Objective:** Server-side PDF generation for corporate donor impact receipts.
- **Tasks:** Create `certificates` app, integrate WeasyPrint PDF renderer with SHA256 hashes.
- **Django Apps Involved:** `certificates`.
- **Models Involved:** `DonationCertificate`.
- **APIs Involved:** `GET /api/v1/certificates/<id>/download/`.
- **Frontend Screens:** Certificates Page (Page 14).
- **DoD:** Donors can download official PDF receipts for delivered donations.

#### PHASE 15 — Admin Governance Panel
- **Objective:** Central platform administration, user management, and audit log inspection.
- **Tasks:** Build custom admin views, user toggle handlers, and audit log table.
- **Django Apps Involved:** `audit`, `accounts`, `organizations`.
- **Models Involved:** `AuditLog`.
- **Frontend Screens:** Central Admin Dashboard (Pages 33–42).
- **DoD:** Admins can manage users, override states, and inspect audit logs.

#### PHASE 16 — Comprehensive Testing Suite Execution
- **Objective:** Run complete automated PyTest suite covering all 56 specified test cases.
- **Tasks:** Write unit, integration, API, and geospatial test scripts.
- **DoD:** 100% pass rate across all 56 test cases with >85% code coverage.

#### PHASE 17 — Security Hardening
- **Objective:** Enforce production security policies.
- **Tasks:** Force HTTPS, configure HSTS, sanitize file uploads, test rate limits.
- **DoD:** Security audit passes zero high or critical vulnerabilities.

#### PHASE 18 — Cloud Deployment Blueprint
- **Objective:** Prepare production build for Render/Railway/VPS deployment.
- **Tasks:** Configure Gunicorn WSGI, Nginx reverse proxy, static file collection (`collectstatic`).
- **DoD:** App successfully running in production-like container/environment.

#### PHASE 19 — Final Documentation & Presentation
- **Objective:** Finalize project repository documentation and viva presentation slides.
- **Tasks:** Generate master index, verify all file cross-references.
- **DoD:** Complete repository ready for presentation.

---

### 3. GIT WORKFLOW & BRANCHING STRATEGY

#### Branch Hierarchy
- `main` — Production-ready stable release branch.
- `develop` — Integration branch for completed features.
- `feature/*` — Feature development branches (e.g., `feature/donor-food-listing`).
- `bugfix/*` — Bug resolution branches (e.g., `bugfix/otp-expiry-fix`).
- `hotfix/*` — Urgent production patches.

#### Recommended Commit Format
```
feat(food): add PostGIS spatial point index and safety checklist validation
fix(otp): prevent brute force attempts by adding 15m lock out
docs(readme): add Windows virtualenv setup and Celery execution guide
```

---

### 4. PROJECT MILESTONES (M1 — M15)

| Milestone | Target Output | Phase Scope |
| :--- | :--- | :--- |
| **M1** | Documentation & Architecture Complete | Phase 0 |
| **M2** | Project Infrastructure & DB Ready | Phase 1 |
| **M3** | Authentication & RBAC Complete | Phase 2 |
| **M4** | Organization Document Verification Complete | Phase 3 |
| **M5** | Surplus Food Listing & Safety Module Complete | Phase 4 |
| **M6** | Receiver Discovery Dashboard Complete | Phase 5 |
| **M7** | PostGIS Geo-Matching & Leaflet Map Complete | Phase 7 |
| **M8** | Atomic Claim System & Locking Complete | Phase 8 |
| **M9** | Volunteer Dispatch & Task Accept Complete | Phase 6 |
| **M10** | Dual OTP Verification Engine Complete | Phase 9 & 10 |
| **M11** | Celery Spoilage Engine & Auto-Expiry Complete | Phase 12 |
| **M12** | Impact Analytics & CSR PDF Engine Complete | Phase 13 & 14 |
| **M13** | Admin Dashboard & Audit Logs Complete | Phase 15 |
| **M14** | Automated Testing & Security Hardening Complete | Phase 16 & 17 |
| **M15** | Production Deployment & Final Submission | Phase 18 & 19 |

---

### 5. FEATURE DEVELOPMENT PRIORITY MATRIX

#### P0 — MUST HAVE (CRITICAL PATH)
- Authentication & RBAC User Models
- Organization Document Upload & Admin Verification
- Surplus Food Listing Creation & Safety Checklist
- PostGIS Nearby Food Spatial Search
- Atomic Claim Locking (`select_for_update`)
- Pickup OTP & Delivery OTP Verification Engine
- Celery Auto-Expiry Task
- Basic Admin Dashboard

#### P1 — IMPORTANT (HIGH VALUE)
- Leaflet.js Interactive Urgency-Coded Map Markers
- WeasyPrint PDF CSR Certificate Generation
- Email & In-App Notification Engine
- Real-time Spoilage Countdown Component (HTMX)
- System Audit Log Recording

#### P2 — FUTURE ENHANCEMENT (NICE TO HAVE)
- WhatsApp Business API Notification Integration
- Machine Learning Food Surplus Demand Prediction
- Multi-Stop Volunteer Route Optimization Engine
- Progressive Web App (PWA) Offline Caching
