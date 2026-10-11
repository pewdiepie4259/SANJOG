# SANJOG — Development Pipeline & Implementation Roadmap
## Phase-by-Phase Execution Plan, Git Workflow & Milestone Pipeline (Food Rescue OS)

---

### 1. REVISED DEVELOPMENT PHASES (PHASE 0 — PHASE 19)

#### PHASE 0 — Architecture Finalization (COMPLETE)
- **Objective:** Finalize all requirements, database schemas, UI specs, API contracts, and Food Rescue OS positioning.
- **Deliverables:** Approved PRD, SRS, System Architecture, UI/UX, DB Design, Test Plan, README, Master Index.

#### PHASE 1 — Project Infrastructure Setup
- **Objective:** Initialize Django 5.x project, Virtual Environment, PostgreSQL/PostGIS, Redis, and Celery task broker.
- **Deliverables:** Working `config` package, database spatial extension enabled, basic home template rendered.

#### PHASE 2 — Authentication & RBAC Core
- **Objective:** Custom user model, registration, login, logout, and role permission wrappers (`DONOR`, `RECEIVER`, `VOLUNTEER`, `ADMIN`).
- **Deliverables:** `accounts` app, JWT & session auth endpoints, working login/registration templates.

#### PHASE 3 — Organization Verification Pipeline
- **Objective:** Organization profiles, FSSAI / 80G document upload, and Admin verification queue.
- **Deliverables:** `organizations` app, document upload sanitization, admin approval workflow.

#### PHASE 4 — Donor Surplus & Food Safety SOP Module
- **Objective:** Surplus food posting with preparation timestamp, storage conditions, and safety SOP rule evaluation.
- **Deliverables:** `food` app, `FoodListing` and `FoodSafetyAssessment` models, SOP classification engine (`ELIGIBLE`, `REVIEW_REQUIRED`, `NOT_ELIGIBLE`).

#### PHASE 5 — Receiver Need-First Demand Module
- **Objective:** Enable Receivers to log active meal requirements (`DemandRequest`).
- **Deliverables:** `demand` app, `DemandRequest` model, meal demand creation forms.

#### PHASE 6 — Food Discovery & PostGIS Geolocation
- **Objective:** Spatial radius filtering (2km to 15km) and interactive Leaflet.js map markers.
- **Deliverables:** PostGIS `ST_DWithin` spatial query implementation, HTMX dynamic pin updates.

#### PHASE 7 — Deterministic Need-First Matching Engine
- **Objective:** Weighted scoring algorithm matching surplus listings to active demand requests.
- **Deliverables:** `rescue` app, matching ranking service (`score = distance + urgency + quantity + diet`).

#### PHASE 8 — Multi-Recipient Rescue Allocation Engine
- **Objective:** Split single surplus listings across multiple receivers with atomic reservation locks.
- **Deliverables:** `RescueAllocation` model, PostgreSQL `select_for_update()` transaction locking logic.

#### PHASE 9 — Volunteer Logistics & Task Feed
- **Objective:** Volunteer availability toggles, task discovery feed sorted by SLA urgency.
- **Deliverables:** `pickups` app, `VolunteerProfile` model, available rescues feed.

#### PHASE 10 — Dual OTP Verification Engine
- **Objective:** Cryptographic 4-digit Donor Pickup OTP and Receiver Delivery OTP validation.
- **Deliverables:** `OTPVerification` and `Delivery` models, Redis TTL cache, max 3-attempt lockouts.

#### PHASE 11 — Food Passport Chain-of-Custody Execution
- **Objective:** Immutable digital lifecycle logging and SHA-256 state hashing.
- **Deliverables:** `FoodPassport` model, auto-logging signals on lifecycle events.

#### PHASE 12 — Rescue SLA & Celery Auto-Expiry Worker
- **Objective:** Dynamic SLA tier monitoring (`NORMAL`, `URGENT`, `CRITICAL`) and auto-expiry task execution.
- **Deliverables:** Celery Beat periodic worker running every 60 seconds, automated SLA alert broadcasts.

#### PHASE 13 — Authoritative Impact Ledger & Analytics
- **Objective:** Transactional impact ledger recording delivered servings, weight (kg), and CO2 offset.
- **Deliverables:** `analytics` app, `ImpactLedger` model, public metrics API.

#### PHASE 14 — AI/ML Demand & Surplus Forecasting (P1)
- **Objective:** Scikit-Learn regression models predicting upcoming surplus volume and receiver demand.
- **Deliverables:** `ml_engine` app, prediction models with moving average fallback.

#### PHASE 15 — WeasyPrint PDF CSR Certificates
- **Objective:** Server-side PDF generation for corporate donor impact receipts.
- **Deliverables:** `certificates` app, `DonationCertificate` model, PDF download endpoint.

#### PHASE 16 — Admin Command Center Dashboard
- **Objective:** Real-time operational command center map, SLA breach monitor, audit logs.
- **Deliverables:** Admin command center screens, audit log viewer.

#### PHASE 17 — Automated Testing Suite Execution
- **Objective:** Run complete PyTest suite covering all 62 specified test cases.
- **Deliverables:** 100% test pass rate across all modules.

#### PHASE 18 — Security Hardening
- **Objective:** Production security enforcement (HTTPS, HSTS, upload sanitization, OWASP).
- **Deliverables:** Security audit clearance.

#### PHASE 19 — Cloud Deployment & Final Presentation
- **Objective:** Production build deployment and final viva presentation setup.
- **Deliverables:** Deployed application, master index verified.

---

### 2. TEAM PARALLELIZATION TRACKS (POST PHASE 3)

```
                  ┌──► TRACK A: Food, Safety & Passport (App: food) ───────────────┐
                  │                                                                │
PHASE 1 to 3 ─────┼──► TRACK B: Demand & Matching Engine (Apps: demand, rescue) ───┼──► PHASE 8 (Integration)
(Base Auth & Org) │                                                                │
                  └──► TRACK C: Volunteer & OTP Logistics (App: pickups) ──────────┘
```

---

### 3. PROJECT MILESTONES (M1 — M15)

| Milestone | Target Output | Scope |
| :--- | :--- | :--- |
| **M1** | Documentation & Architecture Complete (Food Rescue OS) | Phase 0 |
| **M2** | Project Infrastructure & DB Ready | Phase 1 |
| **M3** | Authentication & RBAC Complete | Phase 2 |
| **M4** | Organization Document Verification Complete | Phase 3 |
| **M5** | Surplus Food Listing & Safety SOP Engine Complete | Phase 4 |
| **M6** | Receiver Demand Requests & Need-First Feed Complete | Phase 5 |
| **M7** | PostGIS Geo-Matching & Leaflet Map Complete | Phase 6 |
| **M8** | Deterministic Matching & Multi-Recipient Allocations Complete | Phase 7 & 8 |
| **M9** | Volunteer Dispatch & Task Feed Complete | Phase 9 |
| **M10** | Dual OTP Verification & Food Passport Complete | Phase 10 & 11 |
| **M11** | Celery SLA Engine & Auto-Expiry Complete | Phase 12 |
| **M12** | Impact Ledger & WeasyPrint CSR PDF Engine Complete | Phase 13 & 15 |
| **M13** | AI Demand/Surplus Forecasting Engine Complete | Phase 14 |
| **M14** | Admin Command Center & Testing Complete | Phase 16 & 17 |
| **M15** | Production Deployment & Final Submission | Phase 18 & 19 |
