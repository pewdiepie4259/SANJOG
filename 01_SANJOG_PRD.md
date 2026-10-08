# SANJOG — Product Requirements Document (PRD)
## Intelligent Food Rescue Operating System (Food Rescue OS)

---

### 1. COVER PAGE
- **Project Name:** SANJOG (Surplus Food Redistribution & Community Connection Platform)
- **Product Vision:** Intelligent Food Rescue Operating System (Food Rescue OS)
- **Document Title:** Product Requirements Document (PRD)
- **Version:** 2.0.0 (Evolved Architecture)
- **Status:** Approved / Architecture Phase
- **Author:** Senior Technical Architecture & Product Team
- **Date:** October 2026
- **Target Audience:** Developers, System Architects, QA Engineers, Project Stakeholders, Evaluators

---

### 2. DOCUMENT CONTROL
| Version | Date | Author | Summary of Changes | Status |
| :--- | :--- | :--- | :--- | :--- |
| **v1.0.0** | 2026-10-08 | Lead Architect | Initial surplus donation marketplace blueprint | Superceded |
| **v2.0.0** | 2026-10-08 | Technical Architect | Evolved to Intelligent Food Rescue OS (6 Strategic Pillars, Need-First Matching, Multi-Recipient Allocations, Food Passport, Safety SOP Engine, SLA Tiers, ML Forecasting) | Approved |

---

### 3. EXECUTIVE SUMMARY
**SANJOG** is an end-to-end **Intelligent Food Rescue Operating System (Food Rescue OS)** engineered to transform surplus food management from an ad-hoc donation marketplace into an automated, data-driven food rescue network. Built on Python 3.11+, Django 5.x, DRF, PostGIS, Celery, Redis, HTMX, Tailwind CSS, and Leaflet.js, SANJOG connects commercial **Donors** (restaurants, hotels, messes, caterers) with **Receivers** (NGOs, shelters, orphanages) and **Volunteers** under centralized **Admin** governance.

Key capabilities of the Food Rescue OS include:
- **Need-First Receiver Demand Requests:** Receivers proactively register live meal needs.
- **Deterministic Need-First Matching Engine:** Weighted scoring matching surplus to active hunger demand.
- **Multi-Recipient Rescue Allocation Engine:** Automatically splits large surplus donations (e.g., 500 meals) across multiple receivers.
- **Food Passport Chain-of-Custody:** Immutable digital lifecycle ledger with SHA-256 state hashing.
- **Structured Food Safety SOP Engine:** Compliance classification (`ELIGIBLE`, `REVIEW_REQUIRED`, `NOT_ELIGIBLE`).
- **Rescue Urgency SLA Tiers:** Dynamic SLA monitoring (`NORMAL` <2h, `URGENT` <60m, `CRITICAL` <30m).
- **AI/ML Demand & Surplus Forecasting:** Machine learning regression predicting upcoming surplus and receiver demand patterns.

---

### 4. STRATEGIC PILLARS (THE 6 PILLARS OF FOOD RESCUE OS)
1. **PREDICT:** AI/ML forecasting predicting upcoming donor surplus and receiver meal demand before food is even cooked.
2. **RESCUE:** Structured food safety SOP assessment ensuring 100% edible compliance before listing publication.
3. **MATCH:** Deterministic weighted scoring algorithm matching surplus listings to active receiver demand based on distance, dietary compatibility, and capacity.
4. **ROUTE:** Multi-recipient allocation engine and volunteer route dispatch ensuring rapid, optimized transport.
5. **VERIFY:** Dual 4-digit cryptographic OTP handoff (Donor → Volunteer → Receiver) preventing unauthorized pickers or lost deliveries.
6. **PROVE:** Immutable Food Passport lifecycle ledger, transactional Impact Ledger, and downloadable WeasyPrint PDF CSR certificates.

---

### 5. PROBLEM STATEMENT
Global food waste statistics indicate that over one-third of all food produced is lost or wasted. In urban centers, tons of untouched, high-quality edible food are discarded daily by commercial establishments. Simultaneously, local charitable care facilities face chronic food budget shortages.

Traditional redistribution frameworks fail because:
1. **Passive Marketplace Lag:** Receivers must manually browse maps, delaying rescue past food shelf-lives.
2. **Single-Recipient Bottleneck:** Large donations (e.g., 500 meals) cannot be absorbed by a single small shelter.
3. **Lack of Chain-of-Custody Auditability:** Donors fear legal/hygiene liabilities, while receivers lack assurances regarding safe handling.
4. **Uncoordinated Transport:** Volunteer dispatch is unorganized without urgent SLA escalation mechanisms.

---

### 6. PROPOSED SOLUTION: SANJOG FOOD RESCUE OS
SANJOG solves these systemic failures by introducing an operating system model:
- **Need-First Matching:** Flips the paradigm so surplus is routed immediately to active receiver requirements (`DemandRequest`).
- **Multi-Recipient Splitting:** Atomically divides large food listings across multiple receiver allocations (`RescueAllocation`).
- **Digital Food Passport:** Generates an auditable JSON/SHA-256 lifecycle log tracking preparation, safety SOPs, transport handoffs, and final consumption.
- **SLA Escalation Engine:** Background Celery workers monitoring food time-to-expiry and triggering urgent volunteer broadcasts as SLA windows compress.

---

### 7. USER ROLES & CAPABILITIES

#### 1. DONOR (Restaurants, Hotels, Messes, Caterers, Canteens, Event Organizers)
- Register & upload FSSAI license / business registration documents.
- Post surplus food listings with quantity, preparation time, storage conditions, and safety SOP checklist.
- View real-time rescue status, assigned receivers, and active volunteer ETA.
- Validate 4-digit Pickup OTP upon volunteer arrival.
- Access digital Food Passport and download official WeasyPrint PDF CSR certificates.

#### 2. RECEIVER (NGOs, Shelters, Orphanages, Community Kitchens, Charities)
- Register & upload 80G / NGO accreditation documents.
- Log active meal requirements (`DemandRequest`) specifying servings needed, dietary preference, and required-by time.
- Discover nearby surplus food via interactive PostGIS Leaflet.js maps.
- Confirm multi-recipient rescue allocations.
- Validate 4-digit Delivery OTP upon food arrival.
- View received history and nutritional impact statistics.

#### 3. VOLUNTEER (Individual Transport Partners, CSR Volunteers)
- Register with government ID proof & vehicle type details.
- Toggle real-time availability status (`AVAILABLE` / `UNAVAILABLE`).
- View open rescue tasks sorted by SLA urgency (`NORMAL`, `URGENT`, `CRITICAL`).
- Accept rescue missions and access turn-by-turn map directions.
- Perform dual OTP handoffs (Input Donor Pickup OTP & Receiver Delivery OTP).

#### 4. ADMIN (Platform Governance & Dispatch Controllers)
- Review organization registration documents & approve/reject profiles.
- Monitor Central Command Center (Live operations map, active allocations, SLA breach alerts).
- Override stuck claims or reassign canceled volunteer routes.
- Inspect system Audit Logs and authoritative transactional Impact Ledger.

---

### 8. USER PERSONAS

#### Persona A: Donor — Chef Rajesh Sharma (Executive Chef, Grand Palace Hotel)
- **Needs:** 2-minute food posting workflow, automated multi-shelter distribution, official CSR certificates for management.
- **Pain Points:** 300 extra banquet portions cannot be taken by one small NGO; needs legal safety disclaimers.

#### Persona B: Receiver — Sister Maria (Director, Hope Children's Shelter)
- **Needs:** Proactive notification when food matching her shelter's exact 80-meal requirement becomes available.
- **Pain Points:** Lack of transport vehicles; cannot monitor donation websites constantly while managing children.

#### Persona C: Volunteer — Aniket Verma (College Student & Social Worker)
- **Needs:** Mobile-optimized task feed, clear map navigation, hassle-free OTP validation.
- **Pain Points:** Wasting time waiting at donor locations; unclear drop-off directions.

---

### 9. PRODUCT SCOPE MATRIX (P0 / P1 / P2)

#### P0 — MUST HAVE (Core Operating System MVP)
- User Authentication & Role-Based Access Control (CustomUser).
- Organization Document Verification Queue.
- Surplus Food Listing Creation + Food Safety SOP Assessment (`ELIGIBLE`, `REVIEW_REQUIRED`, `NOT_ELIGIBLE`).
- Receiver Need-First Demand Requests (`DemandRequest`).
- Deterministic Rule-Based Need-First Matching Engine.
- Multi-Recipient Rescue Allocation Engine (`RescueAllocation`) with atomic transaction locks.
- Food Passport Chain-of-Custody Ledger with SHA-256 state hashing.
- Volunteer Logistics & Dual 4-Digit OTP Handoff Verification.
- Dynamic Spoilage & Urgency Status Engine (`SAFE`, `WARNING`, `URGENT`, `EXPIRED`).
- Authoritative Impact Ledger & WeasyPrint PDF CSR Certificate Generator.
- Admin Operations Command Center Dashboard.

#### P1 — IMPORTANT (Advanced Rescue Intelligence)
- AI/ML Surplus & Demand Forecasting (Scikit-Learn/LightGBM).
- Rescue Urgency SLA Tier Escalation Engine (`NORMAL`, `URGENT`, `CRITICAL`).
- Volunteer Route Batching & Waypoint Optimization (OSRM integration).
- Spatial Community Demand Heatmap Layer (Leaflet.js).
- Automated Async Notification System (Celery email dispatch).

#### P2 — FUTURE ENHANCEMENTS
- POS System API Connectors.
- WhatsApp Business API Bot.
- Multilingual Interface (Hindi, Regional Languages).

---

### 10. END-TO-END FOOD RESCUE WORKFLOW

```
SURPLUS DETECTED (Donor posts surplus details)
        ↓
FOOD SAFETY ASSESSMENT (SOP Rules Engine → ELIGIBLE / REVIEW / NOT_ELIGIBLE)
        ↓
SURPLUS LISTING CREATED (Food Passport Initiated, Spoilage Clock Started)
        ↓
URGENCY CALCULATION (SLA Tier Assigned: NORMAL / URGENT / CRITICAL)
        ↓
DEMAND ANALYSIS & NEED-FIRST MATCHING (Algorithm matches nearby DemandRequests)
        ↓
MULTI-RECIPIENT RESCUE ALLOCATION (System splits quantity across Receivers A, B, C)
        ↓
ATOMIC RESERVATION LOCK (Select_for_update reserves allocated quantities)
        ↓
RESCUE PLAN GENERATED (Pickup requests & Volunteer routes created)
        ↓
VOLUNTEER ASSIGNMENT (Volunteer accepts mission / Batch route assigned)
        ↓
PICKUP & OTP HANDOFF (Donor validates 4-digit Pickup OTP → Status: PICKED_UP)
        ↓
DELIVERY & OTP HANDOFF (Receiver validates 4-digit Delivery OTP → Status: DELIVERED)
        ↓
FOOD PASSPORT FINALIZED (Immutable SHA-256 hash appended)
        ↓
IMPACT LEDGER UPDATED (Real-time stats & PDF CSR Certificate generated)
```

---

### 11. KEY PERFORMANCE INDICATORS (KPIS)
- **Median Rescue Duration:** Time from surplus posted to final delivery (< 45 minutes target).
- **Rescue Success Rate:** Ratio of total surplus weight rescued vs. total weight posted (> 92% target).
- **Multi-Recipient Fulfillment Rate:** Percentage of large donations (>200 meals) successfully split and delivered across 2+ receivers (> 95%).
- **Safety Compliance Rate:** Zero incidents of spoiled food delivery.
