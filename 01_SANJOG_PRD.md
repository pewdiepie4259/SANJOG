# SANJOG — Product Requirements Document (PRD)
## Surplus Food Redistribution & Community Connection Platform

---

### 1. COVER PAGE
- **Project Name:** SANJOG (Surplus Food Redistribution & Community Connection Platform)
- **Document Title:** Product Requirements Document (PRD)
- **Version:** 1.0.0
- **Status:** Approved / Architecture Phase
- **Author:** Senior Technical Architecture & Product Team
- **Date:** October 2026
- **Target Audience:** Developers, System Architects, QA Engineers, Project Stakeholders, Evaluators

---

### 2. DOCUMENT CONTROL
| Version | Date | Author | Summary of Changes | Status |
| :--- | :--- | :--- | :--- | :--- |
| **v0.1.0** | 2026-10-01 | Product Team | Initial draft & requirements outline | Draft |
| **v0.5.0** | 2026-10-05 | Technical Architect | Added user stories, state transitions, security constraints | Review |
| **v1.0.0** | 2026-10-08 | Lead Architect | Finalized blueprint for SANJOG complete suite | Approved |

---

### 3. EXECUTIVE SUMMARY
**SANJOG** is an end-to-end, real-time, geo-intelligent surplus food redistribution platform engineered to bridge the gap between commercial food establishments with edible surplus and non-profit organizations catering to food-insecure communities. Utilizing a robust three-sided ecosystem—**Donors**, **Receivers**, and **Volunteers** under centralized **Admin** governance—SANJOG optimizes food rescue operations using real-time countdown timers, PostGIS geospatial proximity matching, OTP-verified multi-stage handoffs, and automated impact/CSR tracking.

---

### 4. PROBLEM STATEMENT
Food waste and food insecurity represent a critical paradox in modern society:
1. **Massive Commercial Food Surplus:** Restaurants, banquet halls, hostel messes, caterers, and corporate canteens daily dispose of tons of untouched, high-quality edible food due to over-preparation or unfulfilled bookings.
2. **Severe Resource Scarcity for Beneficiaries:** Nearby NGOs, orphanages, shelter homes, and community kitchens constantly struggle with budget constraints and unpredictable food supplies.
3. **Lack of Technological Bridge:** Traditional redistribution relies on ad-hoc phone calls or informal networking, which fails due to short food shelf-lives, transport logistics bottlenecks, and lack of real-time visibility.
4. **Accountability & Trust Deficit:** Donors fear liability or misallocation, while receivers lack assurances regarding food hygiene and safe handling standards.

---

### 5. BACKGROUND
Global food waste statistics indicate that over one-third of all food produced is lost or wasted. In urban centers, thousands of meals are discarded daily within a few kilometers of underfunded care facilities. Existing tech solutions either target bulk logistics (unsuitable for quick urban surplus) or lack secure verification protocols. SANJOG addresses these structural failures by introducing hyper-local discovery, automated spoilage alerts, and verified chain-of-custody delivery.

---

### 6. VISION
To create a zero-food-waste urban ecosystem where no edible surplus food is discarded, and every vulnerable community member has access to nutritious meals through seamlessly coordinated technology.

---

### 7. MISSION
To empower food businesses, charitable institutions, and socially conscious citizens with an intuitive, reliable, and transparent digital platform that automates surplus food discovery, claim verification, safe transport, and measurable social impact.

---

### 8. GOALS
- **Diverting Surplus:** Divert 100% of edible surplus food posted on the platform to verified receivers before expiry.
- **Minimizing Response Time:** Reduce the average time between surplus creation and claim confirmation to under 15 minutes.
- **Ensuring Food Safety:** Maintain zero incidents of spoiled food delivery by implementing mandatory hygiene declarations and strict automated time-to-spoilage enforcement.
- **Verifiable Transparency:** Provide 100% auditable pickup-to-delivery handoffs via cryptographically backed OTP verification.

---

### 9. OBJECTIVES
1. Achieve an average pickup turnaround time of under 45 minutes for urgent food listings.
2. Maintain a 95%+ successful delivery rate across all claimed donations.
3. Onboard and verify 50+ donors, 30+ receiver organizations, and 100+ active volunteers within the target operational zone.
4. Automate CSR certificate generation to incentivize corporate donor participation.

---

### 10. TARGET USERS
1. **Food Donors:** Restaurant owners, hotel banquet managers, hostel mess wardens, catering managers, corporate canteen heads, event managers.
2. **Food Receivers:** NGO directors, shelter home administrators, orphanage caretakers, community kitchen supervisors, charitable trust coordinators.
3. **Volunteers:** College students, youth activists, independent delivery partners, corporate CSR volunteers.
4. **Platform Administrators:** Platform managers, compliance officers, verification agents, community coordinators.

---

### 11. USER PERSONAS

#### Persona A: Donor — Chef Rajesh Sharma (Executive Chef, Grand Palace Hotel)
- **Background:** Manages banquet dining producing 50–200 extra portions after evening events.
- **Needs:** Fast 2-minute food posting workflow, reliable pickup coordination, official CSR/donation receipts for management.
- **Pain Points:** Discarding good food causes guilt; cannot manage phone calls during late hours; needs legal/hygiene disclaimers.

#### Persona B: Receiver — Sister Maria (Director, Hope Children's Shelter)
- **Background:** Operates a shelter housing 80 children with limited daily food budget.
- **Needs:** Real-time notifications of nearby food, distance transparency, volunteer transport assistance.
- **Pain Points:** Unpredictable supply; no dedicated transport vehicles; cannot afford spoiled or unsafe food.

#### Persona C: Volunteer — Aniket Verma (College Student & Social Worker)
- **Background:** Owns a two-wheeler, has 2–3 free hours in the evening, wants to serve the community.
- **Needs:** Easy-to-use mobile web view, clear map navigation, hassle-free OTP verification.
- **Pain Points:** Wasting time waiting at donor locations; unclear drop-off directions.

---

### 12. USER PAIN POINTS & SOLUTIONS MATRIX
| User Pain Point | Existing Reality | SANJOG Solution |
| :--- | :--- | :--- |
| **Short Food Shelf Life** | Food spoils before receiver is notified | Real-time PostGIS proximity alerts + Spoilage Countdown |
| **Transport Failure** | Receivers lack vehicles for pickup | On-demand Volunteer Dispatch Network |
| **Verification & Trust** | Unverified claims / fake pickers | Dual 4/6-Digit OTP Handoff (Donor ↔ Volunteer ↔ Receiver) |
| **Legal/Hygiene Liability** | Donors worry about liability | Mandatory Food Safety Checklist + Automated Platform Disclaimer |
| **Lack of Recognition** | Donors receive no formal record | Automated CSR & Impact Certificate PDF Generator |

---

### 13. PROPOSED SOLUTION
SANJOG is a unified Django/DRF web application powered by PostGIS, Leaflet.js, HTMX, Tailwind CSS, Redis, and Celery. It provides:
1. **Multi-Role RBAC:** Role-restricted dashboards for Donors, Receivers, Volunteers, and Admins.
2. **Geo-Discovery:** Spatial querying allowing Receivers to discover food within 2km, 5km, 10km, or 15km radii.
3. **State Machine Workflow:** Strict transitions (`AVAILABLE` → `CLAIMED` → `PICKUP_ASSIGNED` → `PICKED_UP` → `DELIVERED` / `EXPIRED` / `CANCELLED`).
4. **Secure OTP Handoffs:** Time-limited OTP validation at both pickup and delivery checkpoints.
5. **Real-Time Spoilage Engine:** Background Celery tasks enforcing dynamic state updates based on expiry timestamps.

---

### 14. PRODUCT SCOPE
- Complete organization registration and document verification workflow.
- Surplus food listing creation with image upload, dietary tags, quantity, shelf life, and safety checklist.
- Geospatial mapping with interactive Leaflet.js markers for food discovery.
- Claim management and lock mechanisms to prevent duplicate claims.
- Volunteer dispatch, request acceptance, and dual-stage OTP verification.
- Automated Celery workers for food expiry monitoring and notification emails.
- Impact analytics dashboard and PDF CSR certificate generator via WeasyPrint/ReportLab.
- Comprehensive Django Admin and custom platform admin panel for audit logging.

---

### 15. OUT OF SCOPE (FOR INITIAL RELEASE)
- Paid commercial food transactions or monetization features (100% free community platform).
- Direct integration with third-party commercial courier APIs (e.g., Dunzo/Swiggy API).
- Native iOS/Android apps (Responsive PWA/HTMX mobile web view is used).
- Automated AI food spoilage detection via computer vision (relies on donor declaration and timer).

---

### 16. USER ROLES & PERMISSION SUMMARY
| Role | Registration Type | Document Verification Required | Key Responsibilities |
| :--- | :--- | :--- | :--- |
| **DONOR** | Organization / Business | Yes (FSSAI/Business License) | Post surplus, validate pickup OTP, download CSR certificates |
| **RECEIVER** | NGO / Shelter / Charity | Yes (80G/12A/NGO Darpan/Registration) | Discover food, claim listings, validate delivery OTP |
| **VOLUNTEER** | Individual | Yes (Govt ID Proof) | Accept delivery requests, execute pickup/drop, verify OTPs |
| **ADMIN** | System Superuser | Manual Admin Grant | Verify documents, monitor state machine, review analytics |

---

### 17. USER STORIES

#### Category: Authentication & Verification
- **US-AUTH-01:** As a new Donor/Receiver, I want to upload my organization's legal registration documents so that the Admin can verify my legitimacy.
- **US-AUTH-02:** As an Admin, I want to review submitted documents and approve or reject organization profiles so that unverified entities cannot access food listings.

#### Category: Surplus Food Listing & Discovery
- **US-FOOD-01:** As a Donor, I want to create a surplus food listing with estimated servings, cooked time, expiry time, and safety declaration so that nearby receivers are informed.
- **US-FOOD-02:** As a Receiver, I want to view active food listings on an interactive map filtered by distance (2km to 15km) so that I can find food close to my facility.

#### Category: Claiming & Lock System
- **US-CLAIM-01:** As a Receiver, I want to claim an available food listing so that it is locked immediately and cannot be claimed by another NGO.

#### Category: Volunteer Logistics & OTP Handoff
- **US-VOL-01:** As a Volunteer, I want to view pending pickup requests near me and accept a delivery task.
- **US-VOL-02:** As a Volunteer, I want the Donor to enter a 4-digit pickup OTP on my device so that the system confirms I have received the food.
- **US-VOL-03:** As a Volunteer, I want the Receiver to enter a 4-digit delivery OTP on my device so that the system marks the food as delivered.

---

### 18. FUNCTIONAL REQUIREMENTS OVERVIEW
1. **Multi-Tenant User Management:** Custom user model supporting role flags (`is_donor`, `is_receiver`, `is_volunteer`, `is_admin_user`).
2. **Organization Verification Pipeline:** Multi-step upload with document status tracking (`PENDING`, `VERIFIED`, `REJECTED`).
3. **Geo-Location Engine:** PostGIS point field support for precise latitude/longitude calculation and spatial radius querying.
4. **Spoilage Countdown Component:** HTMX/JS live countdown clock updating statuses (`SAFE`, `WARNING`, `URGENT`, `EXPIRED`).
5. **OTP Verification System:** Cryptographically random 4 or 6-digit OTP generation with rate-limiting (max 3 wrong attempts).
6. **PDF Certificate Engine:** Server-side PDF rendering of donation impact receipts.

---

### 19. NON-FUNCTIONAL REQUIREMENTS OVERVIEW
- **Performance:** Page load under 1.5 seconds; API response time under 200ms; spatial query execution under 50ms.
- **Security:** OWASP Top 10 compliance, Django CSRF protection, RBAC permissions, encrypted media file storage paths, zero plain-text OTP storage.
- **Availability:** 99.5% uptime target for web and background worker processes.
- **Scalability:** Stateless DRF backend supporting horizontal scaling; PostgreSQL connections managed via connection pooling.

---

### 20. FEATURE SPECIFICATION (KEY HIGHLIGHTS)

#### Feature 1: Spoilage Countdown Engine
- **Logic:**
  - `Remaining Time > 2 Hours` → Status: **SAFE** (Green badge `#16A34A`)
  - `1 Hour < Remaining Time <= 2 Hours` → Status: **WARNING** (Yellow/Amber badge `#D97706`)
  - `0 Hours < Remaining Time <= 1 Hour` → Status: **URGENT** (Red badge `#DC2626`)
  - `Remaining Time <= 0` → Status: **EXPIRED** (Gray badge `#4B5563`, listing auto-disabled)

#### Feature 2: PostGIS Geo-Based Discovery
- Spatial lookup: `ST_DWithin(donor_location, receiver_location, radius_in_meters)`
- Interactive Leaflet.js map with custom pin icons (Green = Safe, Amber = Warning, Red = Urgent).

#### Feature 3: Food Safety Checklist & Disclaimer
- 5-point mandatory checkbox array required before listing submission.
- Standard platform disclaimer displayed on all listings and receipts.

#### Feature 4: Dual-Stage OTP Handoff
- Stage 1: Donor → Volunteer (Generates `pickup_otp`, expires in 30 mins).
- Stage 2: Volunteer → Receiver (Generates `delivery_otp`, expires in 60 mins).

#### Feature 5: Impact Analytics Dashboard
- Aggregates total meals saved, total weight (kg), completed deliveries, and carbon footprint reduction equivalent.

#### Feature 6: Downloadable CSR Certificate
- Generates official PDF receipt containing unique Certificate Hash ID, Organization details, and total impact metrics.

---

### 21. CORE USER JOURNEYS
```
[DONOR] Create Listing + Safety Checklist
   │
   ▼
[SYSTEM] Status: AVAILABLE (Spoilage Clock Started)
   │
   ▼
[RECEIVER] Discovers via Map (Filter 5km) ──► Claims Listing
   │
   ▼
[SYSTEM] Status: CLAIMED (Lock Enforced, Pickup Request Created)
   │
   ▼
[VOLUNTEER] Accepts Pickup Task ──► Status: PICKUP_ASSIGNED
   │
   ▼
[DONOR & VOLUNTEER] Arrive at Pickup ──► Donor Enters Pickup OTP ──► Status: PICKED_UP
   │
   ▼
[VOLUNTEER & RECEIVER] Arrive at Dropoff ──► Receiver Enters Delivery OTP ──► Status: DELIVERED
   │
   ▼
[SYSTEM] Update Impact Metrics + Trigger Donor CSR Certificate
```

---

### 22. SUCCESS METRICS
- **Redistribution Efficiency:** Ratio of total food listed vs. total food successfully delivered (> 90%).
- **Time-to-Claim:** Average time taken for a posted listing to be claimed by an NGO (< 15 mins).
- **Volunteer Engagement:** Active volunteer response rate within 10 minutes of claim creation (> 80%).
- **Verification Precision:** Zero false approvals of unverified donor or receiver organizations.

---

### 23. KEY PERFORMANCE INDICATORS (KPIS)
- Monthly Meals Saved (Target: 10,000+ meals/month)
- Total Active Donors & Verified Receivers
- Average Delivery Duration (Pickup to Delivery < 45 mins)
- Expiry Rate (Unclaimed expired food < 5% of total listings)

---

### 24. RISKS & MITIGATION STRATEGIES
| Identified Risk | Risk Severity | Mitigation Strategy |
| :--- | :--- | :--- |
| **Spoiled Food Delivery** | Critical | Mandatory Safety Checklist + Strict Expiry Enforcement + Immediate reporting flag |
| **No Volunteer Available** | High | Fallback mechanism allowing Receiver direct self-pickup option |
| **Fake Organization Profiles** | High | Mandatory multi-document admin verification prior to active platform access |
| **Unresponsive Receivers / No-Show** | Medium | Claim expiration timer (30 mins to confirm pickup arrangements or claim auto-cancels) |

---

### 25. ASSUMPTIONS
1. Donors possess basic internet access via smartphone/desktop to create listings.
2. Receivers have smartphone access to inspect map listings and verify delivery OTPs.
3. Donors provide accurate, honest declarations regarding food preparation time and estimated shelf life.

---

### 26. CONSTRAINTS
- **Technology Stack:** Must strictly utilize Python 3.11+, Django 5.x, DRF, PostgreSQL/PostGIS, Leaflet.js, HTMX, Tailwind CSS, Celery, and Redis.
- **Budget & Hosting:** Designed for economical deployment on cloud VPS / Railway / Render.
- **Legal:** SANJOG functions strictly as a facilitator platform and does not hold food inventory or operate central warehouses.

---

### 27. FUTURE ENHANCEMENTS
- **Smart Volunteer Route Optimization:** Multi-stop pickup bundling for volunteers.
- **Machine Learning Demand Forecasting:** Predictive analytics forecasting surplus food availability by weekday/season.
- **Mobile Native PWA Push Notifications:** WebPush API for instant browser/mobile alerts.
- **Multilingual Support:** Local language options (Hindi, Marathi, Regional dialects) for ground staff.
