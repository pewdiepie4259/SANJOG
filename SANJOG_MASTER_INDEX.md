# SANJOG — Master Documentation Index & Architectural Directory
## Intelligent Food Rescue Operating System (Food Rescue OS) Blueprint Suite

---

### 1. OVERVIEW
This Master Index serves as the central directory and architectural map for the entire **SANJOG (Food Rescue OS)** platform documentation suite. It organizes all engineering blueprints, software requirements, visual design systems, database schemas, test cases, and implementation roadmaps into a structured reference for developers, system architects, QA engineers, and evaluators.

---

### 2. MASTER DOCUMENTATION REGISTRY

| # | Document Title | File Name | Key Focus / Scope |
| :-: | :--- | :--- | :--- |
| **01** | **Product Requirements Document (PRD)** | [`01_SANJOG_PRD.md`](file:///f:/SANJOG/01_SANJOG_PRD.md) | Vision, 6 Strategic Pillars (PREDICT, RESCUE, MATCH, ROUTE, VERIFY, PROVE), Personas, Need-First Matching, Multi-Recipient Allocations, Food Passport, Safety SOPs, SLA Tiers, ML Forecasting, P0/P1/P2 Scopes. |
| **02** | **Software Requirements Specification (SRS)** | [`02_SANJOG_SRS.md`](file:///f:/SANJOG/02_SANJOG_SRS.md) | IEEE 830-style specification with unique requirement IDs (`FR-DEMAND-001`, `FR-SAFETY-001`, `FR-MATCH-001`, `FR-ALLOC-001`, `FR-PASSPORT-001`, `FR-SLA-001`, `FR-ML-001`, `NFR-SEC-001`). |
| **03** | **System Design & Architecture** | [`03_SANJOG_System_Architecture.md`](file:///f:/SANJOG/03_SANJOG_System_Architecture.md) | High-level technical blueprint featuring 10 Mermaid diagrams (Architecture, Data Flow, Sequence, Multi-Recipient Split, Food Passport Flow, Deployment) and DRF REST API endpoint tables. |
| **04** | **UI/UX Design Specification** | [`04_SANJOG_UI_UX_Specification.md`](file:///f:/SANJOG/04_SANJOG_UI_UX_Specification.md) | Visual design system (Color tokens, typography) and complete specifications for all 42 operating screens across Donor, Receiver, Volunteer, and Admin roles. |
| **05** | **Database Design Document** | [`05_SANJOG_Database_Design.md`](file:///f:/SANJOG/05_SANJOG_Database_Design.md) | Relational PostGIS database schema, ER diagrams, state machine rules, and comprehensive data dictionary for 16 core entities. |
| **06** | **Quality Assurance & Test Plan** | [`06_SANJOG_Test_Plan.md`](file:///f:/SANJOG/06_SANJOG_Test_Plan.md) | QA strategy and 62 detailed test cases covering Auth, PostGIS, Demand Requests, Matching Engine, Multi-Recipient Locks, Food Passport Hashes, SLA Urgency, Dual OTPs, and Security. |
| **07** | **Project README & Setup Guide** | [`README.md`](file:///f:/SANJOG/README.md) | Project overview, technology stack, Windows VS Code installation guide, PostgreSQL/PostGIS setup, Redis/Celery configuration, and execution instructions. |
| **08** | **Development Pipeline & Roadmap** | [`SANJOG_Development_Pipeline.md`](file:///f:/SANJOG/SANJOG_Development_Pipeline.md) | 20 execution phases (Phases 0 to 19), 3 parallel development tracks, Git branching workflow, 15 milestones (M1–M15), and P0/P1/P2 feature priority matrix. |

---

### 3. RECOMMENDED IMPLEMENTATION ORDER

```
[PHASE 0] Architecture Finalization (Complete)
   │
   ▼
[PHASE 1] Project Setup (Django 5.x, PostGIS, Redis, Celery)
   │
   ▼
[PHASE 2] CustomUser & RBAC Authentication (accounts)
   │
   ▼
[PHASE 3] Organization Management & Verification Queue (organizations)
   │
   ├───────────────────────────────┬───────────────────────────────┐
   ▼                               ▼                               ▼
[TRACK A: Food & Safety]    [TRACK B: Demand & Match]   [TRACK C: Volunteer Logistics]
(App: food)                 (Apps: demand, rescue)      (App: pickups)
   │                               │                               │
   └───────────────────────────────┼───────────────────────────────┘
                                   ▼
[PHASE 8] Multi-Recipient Rescue Allocations (Integration)
   │
   ▼
[PHASE 11 & 12] Food Passport & Celery SLA Auto-Expiry Workers
   │
   ▼
[PHASE 13 & 14] Impact Ledger & AI ML Demand/Surplus Forecasting
   │
   ▼
[PHASE 15 & 16] WeasyPrint PDF CSR Certificates & Admin Command Center
   │
   ▼
[PHASE 17, 18 & 19] Automated Testing (62 Test Cases), Security & Cloud Deployment
```

---

### 4. CORE ARCHITECTURAL PRINCIPLES RECAP

1. **Intelligent Food Rescue Operating System Positioning:** Shifts surplus food management from passive marketplace browsing to proactive, automated need-first matching and rapid dispatch.
2. **Multi-Recipient Allocation Engine:** Atomically divides large surplus food listings across multiple receiver organizations using PostgreSQL `select_for_update()` transaction locks.
3. **Immutable Food Passport:** Generates auditable digital chain-of-custody logs with cryptographic SHA-256 state hashes for every rescue lifecycle event.
4. **Structured Food Safety SOP Evaluation:** Classifies food safety into `ELIGIBLE`, `REVIEW_REQUIRED`, or `NOT_ELIGIBLE` based on preparation time, storage temperature, and hygiene compliance.
5. **Dynamic SLA Urgency Escalation:** Dynamic SLA monitoring (`NORMAL` <2h, `URGENT` <60m, `CRITICAL` <30m) triggering automated volunteer broadcast alerts.
6. **Authoritative Impact Ledger:** Financial and social impact metrics are computed strictly from verified transactional delivery records.

---

### 5. SUMMARY STATEMENT
The **SANJOG (Food Rescue OS)** platform documentation suite represents a complete, professional, and internally consistent software engineering blueprint. Every requirement, schema, API endpoint, and UI component defined across these 9 documents maps 1-to-1 with the target Django 5.x/PostGIS/Celery implementation.

*Documentation updated and approved on October 8, 2026.*
