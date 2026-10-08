# SANJOG — Software Requirements Specification (SRS)
## Surplus Food Redistribution & Community Connection Platform

---

### 1. INTRODUCTION
This Software Requirements Specification (SRS) document details the complete functional and non-functional requirements for **SANJOG**, an enterprise-grade surplus food redistribution platform. It follows standard IEEE 830-1998 / ISO/IEC/IEEE 29148 structure to ensure software engineering compliance, traceability, and implementation precision.

---

### 2. PURPOSE
The purpose of this specification is to define all system boundaries, data contracts, security constraints, role-based workflows, API requirements, and operational rules required to build the SANJOG backend (Django / DRF / PostGIS / Celery) and frontend (Django Templates / HTMX / Leaflet.js / Tailwind CSS).

---

### 3. SCOPE
The scope encompasses four primary user domains:
1. **Donor Ecosystem:** Registration, verification document submission, food listing creation, spoilage management, OTP handoff validation, CSR certificate download.
2. **Receiver Ecosystem:** Organization onboarding, distance-based geospatial map search, claim submission, claim state tracking, delivery OTP validation.
3. **Volunteer Ecosystem:** Task discovery, delivery acceptance, route mapping, dual-stage OTP input, volunteer impact metrics.
4. **Admin Ecosystem:** Superuser governance, organization document verification, state machine oversight, system-wide analytics, audit logs, and settings management.

---

### 4. DEFINITIONS & ABBREVIATIONS
- **SRS:** Software Requirements Specification
- **RBAC:** Role-Based Access Control
- **PostGIS:** Spatial database extension for PostgreSQL
- **DRF:** Django REST Framework
- **OTP:** One-Time Password (cryptographic handoff key)
- **HTMX:** High-power HTML extension engine for AJAX/DOM updates without heavy JS frameworks
- **CSR:** Corporate Social Responsibility
- **FSSAI:** Food Safety and Standards Authority of India (or equivalent food authority)

---

### 5. SYSTEM OVERVIEW
SANJOG is a multi-tier web application. The frontend utilizes server-rendered Django templates enhanced with HTMX for micro-interactions and Leaflet.js for interactive GIS mapping. The backend is powered by Django 5.x REST Framework backed by a PostGIS database. Celery workers handle asynchronous background jobs (auto-expiry of listings, OTP cleanup, email alerts, PDF generation).

---

### 6. PRODUCT PERSPECTIVE
SANJOG operates as an independent self-contained web platform. It interfaces with external mapping services (OpenStreetMap tiles), email servers (SMTP), and optionally SMS/WhatsApp gateways.

---

### 7. USER CLASSES & CHARACTERISTICS
| User Class | Technical Proficiency | Access Frequency | Rights Level |
| :--- | :--- | :--- | :--- |
| **Donor Staff** | Basic to Moderate | Daily / Per Event | Restricted to Donor Module |
| **Receiver Coordinator** | Basic to Moderate | Daily | Restricted to Receiver Module |
| **Volunteer** | Moderate | On-Demand | Restricted to Volunteer Module |
| **Platform Administrator** | High | Daily | Full Administrative System Access |

---

### 8. FUNCTIONAL REQUIREMENTS

#### 8.1 Authentication & Authorization
- **FR-AUTH-001:** The system shall support a unified custom user model extending `AbstractUser` with specific role flags (`role = DONOR | RECEIVER | VOLUNTEER | ADMIN`).
- **FR-AUTH-002:** The system shall enforce mandatory email verification upon initial user registration.
- **FR-AUTH-003:** The system shall enforce strong password complexity (min 8 chars, 1 uppercase, 1 numeric, 1 special character).
- **FR-AUTH-004:** The system shall issue HTTP-only, secure CSRF tokens for all session-based and HTMX state-changing requests.
- **FR-AUTH-005:** The system shall provide JWT/Token-based authentication endpoints for REST API access.

#### 8.2 Donor Module
- **FR-DONOR-001:** Donors shall be required to submit an Organization Profile including name, business registration number, contact person, phone, and address.
- **FR-DONOR-002:** Donors shall upload verification documents (e.g., FSSAI license / business registration PDF/Image) upon profile creation.
- **FR-DONOR-003:** Donors shall be prevented from posting food listings until their profile verification status is set to `VERIFIED` by an Admin.
- **FR-DONOR-004:** Verified Donors shall be able to create surplus food listings containing food title, food category (Perishable/Cooked/Bakery/Packaged), food type (Veg/Non-Veg/Jain), estimated quantity (kg/liters), estimated servings, preparation time, expiry timestamp, pickup address, and map coordinates (latitude/longitude).
- **FR-DONOR-005:** Donors shall be required to complete a 5-point Food Safety Checklist prior to submitting any listing.
- **FR-DONOR-006:** Donors shall be able to view active, claimed, picked up, delivered, and expired food listings on their dashboard.
- **FR-DONOR-007:** Donors shall be able to view generated pickup OTPs for claimed listings and validate them when the volunteer/receiver arrives.
- **FR-DONOR-008:** Donors shall be able to download PDF CSR/Donation certificates for successfully delivered listings.

#### 8.3 Receiver Module
- **FR-RECEIVER-001:** Receivers shall register as an organization (NGO, shelter, orphanage, community kitchen) and upload legal accreditation documents (e.g., 80G/12A/NGO Darpan).
- **FR-RECEIVER-002:** Receivers shall be blocked from claiming food until profile status is marked `VERIFIED` by an Admin.
- **FR-RECEIVER-003:** Receivers shall be able to view available food listings within specified radial distances (2km, 5km, 10km, 15km) from their organization location using PostGIS spatial queries.
- **FR-RECEIVER-004:** Receivers shall view food listings on an interactive Leaflet.js map with color-coded markers based on spoilage urgency.
- **FR-RECEIVER-005:** Receivers shall be able to claim an available food listing. Upon claiming, the system shall atomically transition the food status from `AVAILABLE` to `CLAIMED` and create an associated `PickupRequest`.
- **FR-RECEIVER-006:** The system shall enforce atomic claim locking, preventing two receivers from claiming the same listing simultaneously.
- **FR-RECEIVER-007:** Receivers shall be able to specify whether they will arrange self-pickup or request platform volunteer dispatch.
- **FR-RECEIVER-008:** Receivers shall receive a secure 4-digit Delivery OTP upon arrival of the food, which must be provided to the delivery party to complete the handoff.

#### 8.4 Volunteer Module
- **FR-VOL-001:** Volunteers shall register with basic personal details and government identity proof uploads.
- **FR-VOL-002:** Verified Volunteers shall be able to toggle their availability status (`AVAILABLE` / `UNAVAILABLE`).
- **FR-VOL-003:** Volunteers shall view open pickup requests requiring transport within their operational radius.
- **FR-VOL-004:** Volunteers shall be able to accept an open pickup request. The listing status shall immediately update to `PICKUP_ASSIGNED`.
- **FR-VOL-005:** Volunteers shall receive turn-by-turn map navigation links (donor address to receiver address).
- **FR-VOL-006:** At the donor site, the volunteer shall request the pickup OTP from the donor and submit it to transition the status to `PICKED_UP`.
- **FR-VOL-007:** At the receiver site, the volunteer shall obtain the delivery OTP from the receiver and submit it to transition the status to `DELIVERED`.

#### 8.5 Admin Module
- **FR-ADMIN-001:** Admins shall have access to a centralized metrics dashboard displaying total users, active listings, successful deliveries, pending verifications, and expired food metrics.
- **FR-ADMIN-002:** Admins shall review organization documents and approve or reject registrations with optional rejection reasons.
- **FR-ADMIN-003:** Admins shall be able to manually override listing states (e.g., cancel a stuck claim or mark spoiled food as `CANCELLED`).
- **FR-ADMIN-004:** Admins shall view comprehensive Audit Logs recording every critical user action, document approval, status transition, and OTP attempt.
- **FR-ADMIN-005:** Admins shall be able to configure system-wide parameters (spoilage threshold hours, default pickup radius, maximum failed OTP attempts).

#### 8.6 Food Listing & Spoilage Engine Requirements
- **FR-FOOD-001:** The system shall compute food listing status based on expiry timestamps:
  - `Time-to-expiry > 120 mins` → `SAFE`
  - `60 mins < Time-to-expiry <= 120 mins` → `WARNING`
  - `0 mins < Time-to-expiry <= 60 mins` → `URGENT`
  - `Time-to-expiry <= 0 mins` → `EXPIRED`
- **FR-FOOD-002:** A scheduled Celery periodic task running every 60 seconds shall scan all `AVAILABLE` and `CLAIMED` listings whose expiry time has passed and update their state to `EXPIRED`.
- **FR-FOOD-003:** Expired listings shall automatically be removed from public discovery maps and receiver feeds.

#### 8.7 Claim & Locking System
- **FR-CLAIM-001:** The system shall use PostgreSQL database transaction locks (`select_for_update()`) during claim execution to guarantee zero double-claiming.
- **FR-CLAIM-002:** When a claim is created, a 30-minute volunteer assignment window shall begin. If no volunteer accepts within 30 minutes and no self-pickup is flagged, the system shall notify the receiver to arrange direct pickup.

#### 8.8 OTP Handoff Verification
- **FR-OTP-001:** The system shall generate cryptographically secure 4-digit or 6-digit numeric OTPs.
- **FR-OTP-002:** OTPs shall have a maximum validity window of 30 minutes for pickup and 60 minutes for delivery.
- **FR-OTP-003:** The system shall enforce a maximum limit of 3 incorrect OTP validation attempts. Exceeding 3 attempts locks the verification for 15 minutes and alerts an Admin.
- **FR-OTP-004:** Plaintext OTPs shall never be stored permanently; values must be salted and hashed or maintained securely in Redis cache with automated TTL expiration.

#### 8.9 Notification System
- **FR-NOTIF-001:** The system shall dispatch email notifications via Celery for:
  - Account verification status updates (Approved/Rejected)
  - New nearby food availability (to Receivers within radius)
  - Successful food claim confirmation (to Donor)
  - Volunteer assignment alert (to Donor and Receiver)
  - Delivery completion receipt (to Donor, Receiver, Volunteer)
- **FR-NOTIF-002:** The system shall maintain an in-app `Notification` table recording unread/read alert logs for each user.

#### 8.10 Analytics & CSR Certificate Engine
- **FR-ANALYTICS-001:** The system shall aggregate impact metrics (meals saved = `servings_count`, food weight = `quantity_kg`, CO2 offset = `quantity_kg * 2.5`).
- **FR-CERT-001:** The system shall render server-side PDF certificates for delivered food listings using WeasyPrint/ReportLab.
- **FR-CERT-002:** Each certificate shall feature a unique SHA256 verification hash, donor organization title, date, impact totals, and SANJOG platform seal.

#### 8.11 Map & Geolocation Engine
- **FR-MAP-001:** The system shall convert user street addresses to PostGIS geography points (`Point(longitude, latitude, srid=4326)`).
- **FR-MAP-002:** The system shall calculate accurate geodesic distance in kilometers between donor point and receiver point using `ST_Distance`.
- **FR-MAP-003:** Leaflet.js maps shall dynamically update pins via HTMX requests without reloading the parent page.

---

### 9. NON-FUNCTIONAL REQUIREMENTS

#### 9.1 Security Requirements (NFR-SEC)
- **NFR-SEC-001:** All HTTP traffic must be forced over HTTPS with HSTS enabled in production.
- **NFR-SEC-002:** User passwords must be hashed using PBKDF2 with SHA-256 (Django default) or Argon2.
- **NFR-SEC-003:** API endpoints must validate user permissions via DRF permission classes (`IsAuthenticated`, `IsVerifiedDonor`, `IsVerifiedReceiver`, `IsAdminUser`).
- **NFR-SEC-004:** Uploaded media files must be sanitized. File extensions and MIME types must be restricted to standard document/image types (PDF, PNG, JPG, WEBP). Max file size: 5MB.
- **NFR-SEC-005:** The application must protect against SQL injection (via Django ORM parameterized queries), XSS (via Django auto-escaping templates), and CSRF (via `CsrfViewMiddleware`).

#### 9.2 Performance Requirements (NFR-PERF)
- **NFR-PERF-001:** Geospatial distance searches within a 15km radius over 10,000 active listings must complete in under 50 milliseconds.
- **NFR-PERF-002:** Page render speed for main dashboards must be under 1.2 seconds on standard 3G/4G connections.
- **NFR-PERF-003:** Background tasks (emails, PDF rendering) must execute asynchronously without blocking HTTP response threads.

#### 9.3 Availability & Reliability (NFR-AVAIL)
- **NFR-AVAIL-001:** The application shall maintain 99.5% operational availability.
- **NFR-AVAIL-002:** In the event of a database failover, zero transaction loss shall occur for completed OTP validations.

#### 9.4 Scalability Requirements (NFR-SCALE)
- **NFR-SCALE-001:** The database schema shall maintain 3rd Normal Form (3NF) for transactional tables with appropriate indexes on foreign keys and spatial points.
- **NFR-SCALE-002:** Celery workers shall scale horizontally to process high volumes of concurrent expiry checks and notifications.

#### 9.5 Data & Audit Requirements (NFR-DATA)
- **NFR-DATA-001:** All critical entities (`FoodListing`, `Claim`, `Delivery`, `OrganizationProfile`) must maintain audit fields (`created_at`, `updated_at`, `created_by`).
- **NFR-DATA-002:** Soft-delete patterns shall be used for sensitive entities to preserve audit compliance.

---

### 10. ERROR HANDLING SPECIFICATION
- **ERR-001 (400 Bad Request):** Returned on validation errors (e.g., expiry time set in the past, invalid phone number format).
- **ERR-002 (401 Unauthorized):** Returned when unauthenticated users attempt restricted API calls.
- **ERR-003 (403 Forbidden):** Returned when a user attempts actions outside their role (e.g., Receiver attempting to create a food listing).
- **ERR-004 (404 Not Found):** Returned when accessing non-existent listings, claims, or user profiles.
- **ERR-005 (409 Conflict):** Returned during race conditions (e.g., double claim attempt on an already claimed listing).
- **ERR-006 (422 Unprocessable Entity):** Returned on OTP validation failure or expired OTP entry.

---

### 11. EXTERNAL INTERFACES
- **Mapping Tile Server:** OpenStreetMap standard tile server over HTTPS (`https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`).
- **Email Gateway:** SMTP interface (Console backend in development; SendGrid/Amazon SES in production).
- **PDF Engine:** Local system binary dependencies for WeasyPrint (Cairo/Pango libraries).

---

### 12. ACCEPTANCE CRITERIA
1. **End-to-End Workflow Validation:** A food listing created by a Verified Donor can be discovered by a Verified Receiver, claimed without conflict, picked up via Donor OTP, delivered via Receiver OTP, and recorded in the Impact Dashboard with a valid PDF certificate generated.
2. **Auto-Expiry Execution:** A food listing reaching its expiry time without being claimed automatically updates state to `EXPIRED` within 60 seconds.
3. **Security Audit Pass:** Zero unauthenticated access to organization verification documents or admin functions.

---

### 13. CONSTRAINTS & LIMITATIONS
- System must run seamlessly within standard Python virtual environments on Windows/Linux.
- PostGIS extension must be enabled on target PostgreSQL databases.
