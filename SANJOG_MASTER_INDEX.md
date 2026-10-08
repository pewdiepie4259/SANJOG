# SANJOG — Master Documentation Index & Architectural Directory
## Complete Software Engineering Blueprint Suite

---

### 1. OVERVIEW
This Master Index serves as the central directory and architectural map for the entire **SANJOG** platform documentation suite. It organizes all engineering blueprints, requirements specifications, visual design systems, database schemas, test cases, and implementation roadmaps into a structured reference for developers, system architects, QA engineers, and evaluators.

---

### 2. MASTER DOCUMENTATION REGISTRY

| # | Document Title | File Name | Key Focus / Scope |
| :-: | :--- | :--- | :--- |
| **01** | **Product Requirements Document (PRD)** | [`01_SANJOG_PRD.md`](file:///f:/SANJOG/01_SANJOG_PRD.md) | Vision, Problem Statement, User Personas, Feature List (Spoilage Clock, Geo-Search, Safety Check, OTP, Impact, CSR Certs), Risks, and Success KPIs. |
| **02** | **Software Requirements Specification (SRS)** | [`02_SANJOG_SRS.md`](file:///f:/SANJOG/02_SANJOG_SRS.md) | Standard IEEE-style specification detailing functional requirements (`FR-DONOR-001`, `FR-RECEIVER-001`, etc.), non-functional rules, and acceptance criteria. |
| **03** | **System Design & Architecture** | [`03_SANJOG_System_Architecture.md`](file:///f:/SANJOG/03_SANJOG_System_Architecture.md) | High-level technical blueprint featuring 10 complete Mermaid diagrams (Architecture, Data Flow, Sequence, Deployment) and DRF REST API endpoint tables. |
| **04** | **UI/UX Design Specification** | [`04_SANJOG_UI_UX_Specification.md`](file:///f:/SANJOG/04_SANJOG_UI_UX_Specification.md) | Visual design system (Color tokens, typography) and complete specifications for all 42 platform pages across Public, Donor, Receiver, Volunteer, and Admin roles. |
| **05** | **Database Design Document** | [`05_SANJOG_Database_Design.md`](file:///f:/SANJOG/05_SANJOG_Database_Design.md) | Relational PostGIS database schema, ER diagrams, state machine rules, and comprehensive data dictionary for all 13 core entities. |
| **06** | **Quality Assurance & Test Plan** | [`06_SANJOG_Test_Plan.md`](file:///f:/SANJOG/06_SANJOG_Test_Plan.md) | QA strategy and 56 detailed test cases covering Auth, PostGIS, Claims, Race Conditions, OTP validation, Auto-expiry, CSR PDFs, and Security. |
| **07** | **Project README & Setup Guide** | [`README.md`](file:///f:/SANJOG/README.md) | Project overview, technology stack, Windows VS Code installation guide, PostgreSQL/PostGIS setup, Redis/Celery configuration, and execution instructions. |
| **08** | **Development Pipeline & Roadmap** | [`SANJOG_Development_Pipeline.md`](file:///f:/SANJOG/SANJOG_Development_Pipeline.md) | 20 execution phases (Phase 0 to 19), Git branching workflow, 15 milestones (M1–M15), and P0/P1/P2 feature priority matrix. |

---

### 3. RECOMMENDED IMPLEMENTATION ORDER

To ensure structured, bug-free development, follow this sequential execution path:

```
[PHASE 0] Documentation & Architecture Review (Complete)
   │
   ▼
[PHASE 1] Project Setup (Django 5.x, PostGIS, Redis, Celery)
   │
   ▼
[PHASE 2] CustomUser & RBAC Authentication (Accounts App)
   │
   ▼
[PHASE 3] Organization Management & Verification Queue (Organizations App)
   │
   ▼
[PHASE 4 & 5] Donor Surplus Food Posting & Safety Checklist (Food App)
   │
   ▼
[PHASE 7] PostGIS Spatial Radius Search & Leaflet.js Mapping
   │
   ▼
[PHASE 8] Receiver Claim & Atomic Database Locking (Claims App)
   │
   ▼
[PHASE 6, 9 & 10] Volunteer Logistics & Dual OTP Verification (Pickups App)
   │
   ▼
[PHASE 11 & 12] Celery Auto-Expiry Worker & Notifications
   │
   ▼
[PHASE 13 & 14] Impact Analytics & WeasyPrint CSR PDF Engine
   │
   ▼
[PHASE 15] Central Admin Dashboard & Audit Logs
   │
   ▼
[PHASE 16 & 17] PyTest Execution (56 Test Cases) & Security Hardening
   │
   ▼
[PHASE 18 & 19] Deployment & Final Viva / Submission
```

---

### 4. CORE ARCHITECTURAL PRINCIPLES RECAP

1. **DRY & Modular Design:** Business logic is encapsulated in modular services (`food.services`, `pickups.services`), avoiding monolithic views or bloated models.
2. **API-First Extensibility:** Every web view is backed by clean DRF REST endpoints, allowing future mobile app integrations without refactoring backend logic.
3. **Atomic Data Integrity:** Race conditions during food claiming are strictly prevented using PostgreSQL `select_for_update()` transaction locks.
4. **Zero Trust OTP Handoff:** Plaintext OTPs are never stored permanently; salted hashes are cached in Redis with strict 3-attempt limits and TTL expirations.
5. **Real-Time Spoilage Engine:** Background Celery tasks automatically enforce state transitions to `EXPIRED` for unclaimed food past safety timestamps.
6. **Strict Role Governance:** Unverified organizations are isolated from creating listings or claiming food until explicit Admin document approval.

---

### 5. SUMMARY STATEMENT
The **SANJOG** platform documentation suite represents a complete, professional, and internally consistent software engineering blueprint. Every requirement, schema, API endpoint, and UI component defined across these documents maps 1-to-1 with the target Django/PostGIS/Celery implementation.

*Documentation completed and verified on October 8, 2026.*
