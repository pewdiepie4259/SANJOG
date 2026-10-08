# SANJOG — Software Requirements Specification (SRS)
## Intelligent Food Rescue Operating System (Food Rescue OS)

---

### 1. INTRODUCTION & PURPOSE
This Software Requirements Specification (SRS) details all functional, technical, and operational requirements for **SANJOG**, an enterprise-grade **Intelligent Food Rescue Operating System (Food Rescue OS)**. It conforms to IEEE 830-1998 / ISO/IEC/IEEE 29148 standards, providing 100% traceability for all backend (Django 5.x / DRF / PostGIS / Celery / Redis) and frontend (Django Templates / HTMX / Tailwind CSS / Leaflet.js) components.

---

### 2. SYSTEM OVERVIEW & SCOPE
SANJOG governs four primary user ecosystems:
1. **Donor Ecosystem:** Surplus posting, food safety SOP evaluation, active rescue tracking, digital Food Passport access, CSR PDF certificate download.
2. **Receiver Ecosystem:** Need-First demand logging (`DemandRequest`), multi-recipient rescue allocation confirmation, PostGIS map discovery, delivery OTP validation.
3. **Volunteer Ecosystem:** Task feed inspection, SLA urgency sorting (`NORMAL`, `URGENT`, `CRITICAL`), route navigation, dual-stage OTP verification.
4. **Admin Command Center:** Superuser governance, organization document verification, real-time rescue operations map, audit logs, and system settings.

---

### 3. FUNCTIONAL REQUIREMENTS SPECIFICATION

#### 3.1 Authentication & RBAC Requirements
- **FR-AUTH-001:** System shall utilize a custom user model extending `AbstractUser` with role flags (`role = DONOR | RECEIVER | VOLUNTEER | ADMIN`).
- **FR-AUTH-002:** System shall enforce mandatory email verification upon user registration.
- **FR-AUTH-003:** System shall issue secure HTTP-only CSRF tokens for session frontend requests and JWT tokens for REST API access.
- **FR-AUTH-004:** System shall restrict API endpoints using custom DRF permission classes (`IsVerifiedDonor`, `IsVerifiedReceiver`, `IsVolunteer`, `IsAdminUser`).

#### 3.2 Organization & Verification Requirements
- **FR-ORG-001:** Donors shall upload FSSAI license / business registration documents; Receivers shall upload 80G / NGO accreditation documents.
- **FR-ORG-002:** System shall maintain an Admin Verification Queue (`PENDING`, `VERIFIED`, `REJECTED`). Unverified entities shall be prevented from posting surplus or receiving allocations.

#### 3.3 Surplus Food & Safety SOP Requirements
- **FR-FOOD-001:** Donors shall create surplus food listings specifying category, food type (Veg/Non-Veg), estimated servings, quantity (kg), preparation timestamp, storage conditions, and expiry timestamp.
- **FR-SAFETY-001:** System shall execute an automated Food Safety SOP evaluation engine classifying listings as `ELIGIBLE`, `REVIEW_REQUIRED`, or `NOT_ELIGIBLE`.
- **FR-SAFETY-002:** Listings marked `NOT_ELIGIBLE` shall be blocked from publication and flagged for donor review.

#### 3.4 Receiver Need-First Demand Requirements
- **FR-DEMAND-001:** Verified Receivers shall create active meal demand requests (`DemandRequest`) specifying required servings, dietary preference, required-by timestamp, and PostGIS location coordinates.
- **FR-DEMAND-002:** Demand requests shall expire automatically once the required-by timestamp passes or when fulfilled by allocations.

#### 3.5 Matching & Multi-Recipient Allocation Requirements
- **FR-MATCH-001:** System shall execute a deterministic weighted scoring algorithm calculating compatibility scores between surplus listings and active demand requests based on distance, urgency, capacity, and dietary constraints.
- **FR-MATCH-002:** System shall support Multi-Recipient Rescue Allocation (`RescueAllocation`), splitting large surplus donations across multiple receivers.
- **FR-ALLOC-001:** System shall execute PostgreSQL `select_for_update()` transaction locks on `FoodListing.remaining_servings` during allocation creation to guarantee zero over-allocation or race conditions.

#### 3.6 Food Passport Chain-of-Custody Requirements
- **FR-PASSPORT-001:** System shall generate an immutable `FoodPassport` record for every published surplus food listing.
- **FR-PASSPORT-002:** System shall append timestamps, actor IDs, and cryptographic SHA-256 state hashes to the Food Passport upon every lifecycle event (Listing Created, Safety Verified, Allocations Confirmed, Pickup OTP Validated, Delivery OTP Validated).

#### 3.7 Volunteer Logistics & SLA Requirements
- **FR-VOL-001:** Verified Volunteers shall toggle real-time availability (`AVAILABLE` / `UNAVAILABLE`).
- **FR-SLA-001:** System shall assign Rescue SLA Urgency Tiers:
  - Expiry > 2 hours → `NORMAL`
  - Expiry 1–2 hours → `URGENT`
  - Expiry < 1 hour → `CRITICAL`
- **FR-SLA-002:** Urgency tiers shall dynamically update volunteer task display badges and trigger priority broadcast alerts as expiry approaches.

#### 3.8 Dual-Stage OTP Handoff Requirements
- **FR-OTP-001:** System shall generate cryptographically secure 4-digit numeric OTPs stored as salted SHA-256 hashes in Redis cache with TTL expiration.
- **FR-OTP-002:** Donor Pickup OTP validation shall transition listing allocation status to `PICKED_UP`.
- **FR-OTP-003:** Receiver Delivery OTP validation shall transition allocation status to `DELIVERED`.
- **FR-OTP-004:** System shall enforce a maximum limit of 3 failed OTP attempts before locking the handoff step and alerting Admin.

#### 3.9 Impact Ledger & CSR Certificate Requirements
- **FR-ANALYTICS-001:** System shall record all completed rescues in an authoritative `ImpactLedger` table storing delivered servings, weight (kg), and CO2 offset.
- **FR-CERT-001:** System shall render server-side PDF certificates using WeasyPrint for completed donations, embedding a unique SHA-256 verification hash.

#### 3.10 AI/ML Forecasting Requirements (P1)
- **FR-ML-001:** System shall execute ML regression models (Scikit-Learn) to forecast upcoming donor surplus and receiver demand.
- **FR-ML-002:** If ML inference fails or lacks historical data, system shall fall back seamlessly to deterministic moving averages.

---

### 4. NON-FUNCTIONAL REQUIREMENTS

#### 4.1 Security Requirements (NFR-SEC)
- **NFR-SEC-001:** HTTPS enforcement with HSTS headers in production environments.
- **NFR-SEC-002:** Password hashing using PBKDF2 with SHA-256 / Argon2.
- **NFR-SEC-003:** Input sanitization and OWASP Top 10 mitigation (CSRF tokens, template auto-escaping, ORM parameterized queries).
- **NFR-SEC-004:** Restrict uploaded media file extensions to PDF, PNG, JPG, WEBP (Max size: 5MB).

#### 4.2 Performance Requirements (NFR-PERF)
- **NFR-PERF-001:** PostGIS spatial radius queries over 10,000 active listings must execute in under 50ms.
- **NFR-PERF-002:** Dashboard page render speed under 1.2 seconds on standard connections.
- **NFR-PERF-003:** Async background worker execution (Celery) for emails, auto-expiries, and PDF rendering.

#### 4.3 Availability & Scalability Requirements (NFR-AVAIL / NFR-SCALE)
- **NFR-AVAIL-001:** Target 99.5% operational uptime.
- **NFR-SCALE-001:** Database normalized to 3rd Normal Form with GiST spatial indexes on PostGIS columns.

---

### 5. ERROR HANDLING SPECIFICATION
- `ERR-400 (Bad Request):` Validation failure (e.g., expiry timestamp in past, safety SOP incomplete).
- `ERR-401 (Unauthorized):` Unauthenticated API call.
- `ERR-403 (Forbidden):` RBAC permission failure or unverified organization profile.
- `ERR-409 (Conflict):` Race condition during multi-recipient allocation reservation.
- `ERR-422 (Unprocessable):` Invalid or expired 4-digit OTP code entered.
