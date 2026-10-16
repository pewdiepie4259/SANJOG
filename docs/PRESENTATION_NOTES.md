# 🌟 SANJOG: Intelligent Food Rescue Operating System (Food Rescue OS)
## Comprehensive Presentation Notes & Live Demonstration Guide

---

## 1. Executive Summary & The 30-Second Elevator Pitch
> *"SANJOG is not just a passive food donation directory—it is a mission-critical **Food Rescue Operating System (OS)**. It connects commercial food donors (hotels, banquet halls, restaurants) with verified NGOs and shelters, coordinated by volunteer logistics partners under centralized platform governance. It solves the real-world food rescue challenge using automated Safety SOPs, need-first allocation algorithms, dynamic SLA urgency escalations, and tamper-proof digital Food Passports."*

### The Problem It Solves:
1. **Massive Food Waste vs. Hunger Paradox:** Tons of edible surplus food are dumped daily from events and caterers while nearby orphanages and shelters go hungry.
2. **The Speed & Safety Gap:** Food perishes quickly (<2–4 hours). Without automated verification, food safety risks and logistical delays prevent timely delivery.
3. **Accountability & Trust:** Donors fear liability; NGOs need reliable quantity & quality; stakeholders need CSR proof.

---

## 2. The 6 Strategic Pillars of SANJOG

| Pillar | Focus | What to Highlight in the Presentation |
| :--- | :--- | :--- |
| **1. PREDICT** | Demand & Surplus Forecasting | Proactive logging of shelter requirements before food surplus expires. |
| **2. RESCUE** | Food Safety SOP Compliance | Structured SOP assessment (`ELIGIBLE`, `REVIEW_REQUIRED`, `NOT_ELIGIBLE`) to prevent food safety violations. |
| **3. MATCH** | Need-First Weighted Scoring | Matches donations by distance, vehicle capacity, urgency, and verified hunger need. |
| **4. ROUTE** | Multi-Recipient Allocation Engine | Atomically splits large bulk donations (e.g. 500 meals) across multiple nearby shelters using PostgreSQL `select_for_update()` concurrency locks. |
| **5. VERIFY** | Dual-Stage Cryptographic OTP | 4-digit OTP verification at both stages: Donor &rarr; Volunteer handoff, then Volunteer &rarr; Receiver delivery. |
| **6. PROVE** | Digital Food Passport & CSR Ledger | Immutable chain-of-custody tracking with SHA-256 state hashing and WeasyPrint PDF CSR certificates. |

---

## 3. Technology Stack & Modern Architecture

### Backend:
- **Framework:** Python 3.11+, Django 5.x, Django REST Framework (DRF)
- **Database:** PostgreSQL 16 with PostGIS 3.4 spatial extension (with seamless SQLite fallback for local development)
- **Concurrency & Locking:** `select_for_update()` transaction blocks to guarantee zero race conditions on meal allocation splitting
- **Task Queue & Caching:** Celery + Redis for auto-expiry alerts, SLA timers, and async notifications

### Frontend & Dual-Stream Innovation:
- **Server-Driven Dynamic UI:** Django Templates + Tailwind CSS + HTMX for instant interactions without heavy SPA overhead.
- **Interactive Mapping:** Leaflet.js with dynamic urgency color-coding (Green: Normal, Amber: Urgent, Red: Critical).
- **Hybrid Micro-Frontend Bundles:**
  - **React 19 Widget:** `DonorAiMatchWidget` and `LiveCourierTrackerWidget` (compiled via `esbuild`).
  - **Angular Widget:** `FoodPassportComponent` and `TelemetryComponent` for real-time monitoring.

---

## 4. Live Demo Walkthrough (Step-by-Step Script)

You can run your demo directly on: **`http://127.0.0.1:8000/`**

### Instant Persona Quick-Switch Shortcuts:
Use these pre-built one-click URL routes to switch roles seamlessly without typing passwords:
- 👑 **Admin Portal:** [http://127.0.0.1:8000/quick-switch/admin/](http://127.0.0.1:8000/quick-switch/admin/)
- 🍲 **Donor Workspace:** [http://127.0.0.1:8000/quick-switch/testdonor/](http://127.0.0.1:8000/quick-switch/testdonor/)
- 🏢 **NGO / Receiver Workspace:** [http://127.0.0.1:8000/quick-switch/testreceiver/](http://127.0.0.1:8000/quick-switch/testreceiver/)
- 🚴 **Volunteer Courier Workspace:** [http://127.0.0.1:8000/quick-switch/testvolunteer/](http://127.0.0.1:8000/quick-switch/testvolunteer/)

---

### Step-by-Step Presentation Script:

#### Act 1: The Unified Overview & Role Switcher (1 minute)
1. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
2. Show the homepage, modern theme, live impact statistics, and explain the mission.
3. Point out the top bar **Role Switcher** showing how different actors collaborate seamlessly in one unified platform.

#### Act 2: Donor Experience — Posting Surplus Food (1.5 minutes)
1. Switch to Donor ([/quick-switch/testdonor/](http://127.0.0.1:8000/quick-switch/testdonor/)).
2. Show the **Donor Dashboard** with active listings, meals saved, and CSR score.
3. Open **Report Surplus Food** (`/donor/report-surplus/`):
   - Highlight Food Safety SOP checklist (temperature, cooked time, storage hygiene).
   - Show how the AI/Match engine estimates eligible meal counts and suggests optimal distribution.
4. Show **Live Tracking & AI Match** (`/donor/ai-match/` and `/donor/live-tracking/`) powered by the React widgets.

#### Act 3: NGO / Receiver Experience — Demand & Allocations (1.5 minutes)
1. Switch to Receiver ([/quick-switch/testreceiver/](http://127.0.0.1:8000/quick-switch/testreceiver/)).
2. Show the **NGO Dashboard** and **Request Food** (`/ngo/request-food/`):
   - Explain the "Need-First" concept: NGOs publish real-time demand (e.g., "Need 120 meals for evening shelter").
3. View **Nearby Food Map** (`/ngo/nearby-food/` and `/map/`):
   - Show how nearby donations are discovered and allocated with strict SLA urgency timers.

#### Act 4: Volunteer Logistics & Chain of Custody (1.5 minutes)
1. Switch to Volunteer ([/quick-switch/testvolunteer/](http://127.0.0.1:8000/quick-switch/testvolunteer/)).
2. View **Available Rescues** and **Active Delivery** (`/volunteer/active-delivery/`).
3. Explain the **Dual OTP Verification**:
   - Step 1: Volunteer arrives at donor &rarr; enters 4-digit pickup code.
   - Step 2: Volunteer reaches shelter &rarr; receiver enters 4-digit delivery confirmation code.
4. Open the **Digital Food Passport** (`/food-passport/`):
   - Show the SHA-256 cryptographic state hash that guarantees food was never tampered with in transit.

#### Act 5: Governance & Admin Verification (1 minute)
1. Switch to Admin ([/quick-switch/admin/](http://127.0.0.1:8000/quick-switch/admin/)).
2. Open **Platform Admin Dashboard** (`/platform-admin/dashboard/`):
   - Show **NGO Document Verification Queue** (FSSAI licenses, 80G tax exemptions, proof of shelter).
   - Show **Rescue Monitoring & Telemetry** (tracking all live rescues across the city).

---

## 5. Anticipated Questions & Winning Answers

### Q1: "Why not use a standard e-commerce or delivery platform?"
> **Answer:** Standard delivery platforms assume infinite stock and predictable delivery windows. Food rescue deals with perishable batches with hyper-strict SLAs (often under 2 hours before food spoil), variable quantities (50 to 500 meals requiring allocation splitting), and critical food safety regulations that require dual OTP verification and immutable audit logs.

### Q2: "How do you prevent race conditions when multiple shelters request the same surplus?"
> **Answer:** We enforce atomic PostgreSQL `select_for_update()` transaction locks in our `RescueAllocation` engine. When an allocation request begins, the surplus listing record is locked at the database level so concurrent requests cannot over-allocate meals.

### Q3: "What prevents someone from donating spoiled food?"
> **Answer:** SANJOG employs a multi-tiered safety protocol:
> 1. Donor SOP Checklist (mandatory prep time, temperature, hygiene declaration).
> 2. Volunteer visual/smell inspection at pickup.
> 3. Dual-stage OTP verification and SHA-256 Food Passport logging for legal accountability.
> 4. Automated expiry countdown that automatically invalidates listings once safety limits are crossed.

### Q4: "Why did you choose Django + HTMX + React/Angular Micro-frontends?"
> **Answer:** Django provides robust ORM security, authentication, and PostGIS geospatial queries out of the box. HTMX delivers blazing-fast, server-rendered dynamic UI without the bloat of an SPA. For complex interactive elements like the Live Courier Tracker and Food Passport Telemetry, we embedded isolated React and Angular widgets compiled with `esbuild`.

---

## 6. Demo Environment Cheat Sheet

- **App URL:** `http://127.0.0.1:8000/`
- **Health Check:** `http://127.0.0.1:8000/health/`
- **Django Admin:** `http://127.0.0.1:8000/admin/`
- **Default Database Users:**
  - `admin` (Role: ADMIN, email: `admin@sanjog.org`)
  - `testdonor` (Role: DONOR, email: `donor@sanjog.org`)
  - `testreceiver` (Role: RECEIVER, email: `receiver@sanjog.org`)
  - `testvolunteer` (Role: VOLUNTEER, email: `volunteer@sanjog.org`)
