# SANJOG — Quality Assurance & Test Plan
## Verification Suite & Comprehensive Test Cases

---

### 1. TESTING STRATEGY & OBJECTIVES
The testing strategy for **SANJOG** provides end-to-end quality assurance across all four user roles (Donor, Receiver, Volunteer, Admin). It covers business logic validation, state machine integrity, geospatial query precision, concurrent claim locking, cryptographic OTP security, and asynchronous background worker execution.

---

### 2. SCOPE & TESTING TYPES
- **Unit Testing:** PyTest / Django `TestCase` testing model methods, signals, validators, and custom managers.
- **Integration Testing:** DRF `APITestCase` evaluating REST API endpoint contracts and permission classes.
- **Geospatial Testing:** PostGIS spatial radius calculation verification.
- **Concurrency & Locking Testing:** Simulated parallel claims on identical food listings using multi-threaded test clients.
- **Security & RBAC Testing:** OWASP Top 10 mitigation verification, unauthorized access attempts, XSS/CSRF payload execution.
- **Performance & Load Testing:** Locust load scripts testing 100 concurrent requests on PostGIS spatial discovery endpoints.

---

### 3. COMPREHENSIVE TEST CASE SUITE (56 TEST CASES)

#### MODULE 1: AUTHENTICATION & ROLE-BASED ACCESS CONTROL (8 TEST CASES)

| Test ID | Module | Scenario | Precondition | Steps | Test Data | Expected Result | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-AUTH-001** | Auth | User Registration with Valid Data | DB clean | Submit POST `/api/v1/auth/register/` | `{email:"donor@sanjog.org", role:"DONOR", pass:"Secure#123"}` | `201 Created`, user instance created in DB | **P0** |
| **TC-AUTH-002** | Auth | Registration with Duplicate Email | User exists | Submit POST `/api/v1/auth/register/` | Existing email | `400 Bad Request`, error "Email already exists" | **P0** |
| **TC-AUTH-003** | Auth | Registration with Weak Password | DB clean | Submit POST `/api/v1/auth/register/` | Password: `"123"` | `400 Bad Request`, password policy validation error | **P1** |
| **TC-AUTH-004** | Auth | Login with Valid Credentials | User registered | Submit POST `/api/v1/auth/login/` | Valid credentials | `200 OK`, JWT access & refresh tokens returned | **P0** |
| **TC-AUTH-005** | Auth | Login with Invalid Password | User registered | Submit POST `/api/v1/auth/login/` | Incorrect password | `401 Unauthorized`, error "Invalid credentials" | **P0** |
| **TC-AUTH-006** | RBAC | Receiver Accessing Donor Listing Creation API | Logged in as Receiver | Send POST `/api/v1/food/` | Valid food payload | `403 Forbidden`, permission class blocks request | **P0** |
| **TC-AUTH-007** | RBAC | Donor Accessing Admin Verification Queue | Logged in as Donor | Send GET `/api/v1/organizations/` | None | `403 Forbidden`, admin access required | **P0** |
| **TC-AUTH-008** | Auth | JWT Token Expiration Enforcement | Token expired | Send GET `/api/v1/users/me/` | Expired Bearer header | `401 Unauthorized`, token expired message | **P1** |

---

#### MODULE 2: ORGANIZATION ONBOARDING & VERIFICATION (6 TEST CASES)

| Test ID | Module | Scenario | Precondition | Steps | Test Data | Expected Result | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-ORG-001** | Org | Submit Org Profile & PDF Document | User registered | Submit POST `/api/v1/organizations/` | Valid org details + PDF FSSAI doc | `201 Created`, status set to `PENDING` | **P0** |
| **TC-ORG-002** | Org | Submit Executable File as Document | User registered | Upload `.exe` file as document | `malicious.exe` payload | `400 Bad Request`, invalid file extension | **P0** |
| **TC-ORG-003** | Org | Admin Approves Pending Organization | Org in `PENDING` | Admin sends PATCH `/verify/` | `{status: "VERIFIED"}` | `200 OK`, org status set to `VERIFIED` | **P0** |
| **TC-ORG-004** | Org | Admin Rejects Organization with Notes | Org in `PENDING` | Admin sends PATCH `/verify/` | `{status: "REJECTED", notes: "FSSAI Expired"}` | `200 OK`, status `REJECTED`, rejection note saved | **P1** |
| **TC-ORG-005** | Org | Unverified Donor Attempts to Post Food | Org `PENDING` | Donor submits POST `/api/v1/food/` | Valid food payload | `403 Forbidden`, "Organization not verified" | **P0** |
| **TC-ORG-006** | Org | Verified Donor Posts Food Successfully | Org `VERIFIED` | Donor submits POST `/api/v1/food/` | Valid food payload | `201 Created`, listing published | **P0** |

---

#### MODULE 3: FOOD LISTING & SAFETY COMPLIANCE (8 TEST CASES)

| Test ID | Module | Scenario | Precondition | Steps | Test Data | Expected Result | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-FOOD-001** | Food | Create Food Listing with All Requirements | Verified Donor | Post listing with safety checklist checked | Expiry: +4 hours, Servings: 50 | `201 Created`, status `AVAILABLE`, spatial point stored | **P0** |
| **TC-FOOD-002** | Food | Listing Creation Without Safety Checklist | Verified Donor | Post listing with safety checklist = `False` | Unchecked safety checkbox | `400 Bad Request`, safety checklist mandatory | **P0** |
| **TC-FOOD-003** | Food | Listing Expiry Timestamp in the Past | Verified Donor | Post listing with past expiry timestamp | Expiry: -30 mins | `400 Bad Request`, expiry must be in future | **P0** |
| **TC-FOOD-004** | Food | Zero or Negative Servings Entered | Verified Donor | Post listing with servings = 0 | Servings: 0 | `400 Bad Request`, servings must be > 0 | **P1** |
| **TC-FOOD-005** | Food | Image Upload Exceeding 5MB Limit | Verified Donor | Upload 10MB image | 10MB PNG file | `400 Bad Request`, file size exceeds 5MB limit | **P1** |
| **TC-FOOD-006** | Food | Correct Spoilage Status `SAFE` (>2 hours) | Listing published | Query listing detail | Expiry: +3 hours | Status badge equals `SAFE` | **P1** |
| **TC-FOOD-007** | Food | Correct Spoilage Status `WARNING` (1-2 hours) | Listing published | Query listing detail | Expiry: +90 mins | Status badge equals `WARNING` | **P1** |
| **TC-FOOD-008** | Food | Correct Spoilage Status `URGENT` (<1 hour) | Listing published | Query listing detail | Expiry: +40 mins | Status badge equals `URGENT` | **P1** |

---

#### MODULE 4: GEOSPATIAL POSTGIS DISCOVERY (5 TEST CASES)

| Test ID | Module | Scenario | Precondition | Steps | Test Data | Expected Result | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-GEO-001** | PostGIS | Find Listings Within 5km Radius | Listings at 2km & 10km | Receiver queries `/food/nearby/?radius_km=5` | Lat/Lon center point | Only 2km listing returned in result list | **P0** |
| **TC-GEO-002** | PostGIS | Find Listings Within 15km Radius | Listings at 2km & 10km | Receiver queries `/food/nearby/?radius_km=15` | Lat/Lon center point | Both 2km & 10km listings returned | **P0** |
| **TC-GEO-003** | PostGIS | Query with Invalid Coordinates | Verified Receiver | Query `/food/nearby/?lat=999&lon=999` | Invalid lat/lon | `400 Bad Request`, coordinate validation error | **P1** |
| **TC-GEO-004** | PostGIS | Exclude Expired Listings from Geo Search | Expired listing nearby | Query `/food/nearby/?radius_km=10` | Valid lat/lon | Expired listing omitted from GeoJSON result | **P0** |
| **TC-GEO-005** | PostGIS | Verify Leaflet Pin Spatial Accuracy | Listing posted | Fetch map pins | Donor Lat/Lon | Pin coordinates match database PostGIS point | **P1** |

---

#### MODULE 5: CLAIMING & LOCKING SYSTEM (6 TEST CASES)

| Test ID | Module | Scenario | Precondition | Steps | Test Data | Expected Result | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-CLAIM-001** | Claim | Successful Claim by Verified Receiver | Listing `AVAILABLE` | Receiver submits POST `/api/v1/claims/` | `{food_listing_id: "<id>"}` | `201 Created`, listing status transitions to `CLAIMED` | **P0** |
| **TC-CLAIM-002** | Claim | Concurrent Double Claim (Race Condition) | Listing `AVAILABLE` | 2 Receivers submit claim simultaneously | Identical listing ID | 1 claim succeeds (`201`), 1 claim fails (`409 Conflict`) | **P0** |
| **TC-CLAIM-003** | Claim | Attempt to Claim Already Claimed Listing | Listing `CLAIMED` | Receiver submits POST `/api/v1/claims/` | Claimed listing ID | `409 Conflict`, error "Listing already claimed" | **P0** |
| **TC-CLAIM-004** | Claim | Attempt to Claim Expired Listing | Listing `EXPIRED` | Receiver submits POST `/api/v1/claims/` | Expired listing ID | `400 Bad Request`, error "Cannot claim expired food" | **P0** |
| **TC-CLAIM-005** | Claim | Unverified Receiver Claims Food | Receiver `PENDING` | Receiver submits POST `/api/v1/claims/` | Valid listing ID | `403 Forbidden`, receiver not verified | **P0** |
| **TC-CLAIM-006** | Claim | Self-Pickup Claim Option Selected | Listing `AVAILABLE` | Receiver submits claim with `is_self_pickup: true` | `{is_self_pickup: true}` | Claim created, volunteer dispatch bypassed | **P1** |

---

#### MODULE 6: VOLUNTEER LOGISTICS & OTP HANDOFF (8 TEST CASES)

| Test ID | Module | Scenario | Precondition | Steps | Test Data | Expected Result | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-OTP-001** | OTP | Volunteer Accepts Unassigned Pickup Request | Pickup `UNASSIGNED` | Volunteer POST `/volunteers/<id>/accept/` | Pickup ID | Status updates to `PICKUP_ASSIGNED` | **P0** |
| **TC-OTP-002** | OTP | Valid Pickup OTP Entry at Donor Site | Pickup `ASSIGNED` | Volunteer enters valid 4-digit Pickup OTP | Valid OTP code | `200 OK`, listing status updates to `PICKED_UP` | **P0** |
| **TC-OTP-003** | OTP | Invalid Pickup OTP Entry (Attempt 1) | Pickup `ASSIGNED` | Volunteer enters wrong 4-digit OTP | Wrong OTP `"0000"` | `422 Unprocessable`, remaining attempts = 2 | **P0** |
| **TC-OTP-004** | OTP | Exceed Max Failed OTP Attempts (3 Fails) | Pickup `ASSIGNED` | Volunteer inputs 3 consecutive wrong OTPs | Wrong OTPs | Account verification locked 15m, Admin flagged | **P0** |
| **TC-OTP-005** | OTP | Valid Delivery OTP Entry at Receiver Site | Status `PICKED_UP` | Volunteer inputs valid Receiver Delivery OTP | Valid OTP code | `200 OK`, status updates to `DELIVERED` | **P0** |
| **TC-OTP-006** | OTP | Attempt Delivery OTP Before Pickup | Status `ASSIGNED` | Volunteer inputs Delivery OTP | Delivery OTP | `400 Bad Request`, food not yet picked up | **P1** |
| **TC-OTP-007** | OTP | Expired OTP Submission (>30 mins) | OTP expired | Volunteer inputs expired OTP | Expired code | `422 Unprocessable`, error "OTP expired" | **P1** |
| **TC-OTP-008** | OTP | Verified OTP Key Cleared from Redis | OTP verified | Inspect Redis key store | `otp:<id>` key | Key deleted immediately after successful handoff | **P1** |

---

#### MODULE 7: SPOILAGE COUNTDOWN & CELERY AUTO-EXPIRY (5 TEST CASES)

| Test ID | Module | Scenario | Precondition | Steps | Test Data | Expected Result | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-EXP-001** | Celery | Automatic Expiry Transition Execution | Expiry time reached | Celery beat runs `check-food-expirations` | Listing past expiry | Listing status automatically set to `EXPIRED` | **P0** |
| **TC-EXP-002** | Celery | Expired Listing Removal from Public Map | Listing `EXPIRED` | HTMX map polling request sent | GeoJSON endpoint | Expired listing pin absent from map response | **P0** |
| **TC-EXP-003** | Celery | Expiry Alert Email Sent to Donor | Listing `EXPIRED` | Celery task completes | Expired listing instance | Email sent to donor: "Your listing has expired" | **P1** |
| **TC-EXP-004** | Spoilage | Live Countdown HTMX Update | Page open | Wait 60 seconds | Live page timer | Timer decrements by 1 minute without full page refresh | **P1** |
| **TC-EXP-005** | Celery | Redis OTP Cleanup Worker Task | Expired OTP keys | Celery beat runs `clean-expired-otps` | Stale Redis keys | Expired keys purged from memory | **P2** |

---

#### MODULE 8: ANALYTICS & CSR CERTIFICATE SYSTEM (4 TEST CASES)

| Test ID | Module | Scenario | Precondition | Steps | Test Data | Expected Result | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-CERT-001** | Certificate | Auto PDF Certificate Generation | Listing `DELIVERED` | System executes post-delivery signal | Delivered listing ID | `DonationCertificate` created with SHA256 hash | **P0** |
| **TC-CERT-002** | Certificate | Donor Downloads Valid PDF Certificate | Cert created | Donor GET `/certificates/<id>/download/` | Certificate ID | `200 OK`, valid `application/pdf` stream | **P0** |
| **TC-CERT-003** | Certificate | Certificate Hash Verification | Cert downloaded | Validate SHA256 hash against DB record | SHA256 string | Hashes match perfectly, confirming authenticity | **P1** |
| **TC-CERT-004** | Analytics | Impact Dashboard Metrics Update | Delivery complete | Query GET `/api/v1/analytics/impact/` | Global impact API | `total_meals` incremented by listing servings | **P0** |

---

#### MODULE 9: SECURITY, PERFORMANCE & API INTEGRITY (6 TEST CASES)

| Test ID | Module | Scenario | Precondition | Steps | Test Data | Expected Result | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-SEC-001** | Security | SQL Injection Payload in Search Query | Search endpoint | Query `GET /api/v1/food/?search=' OR 1=1--` | SQL payload | Handled safely by Django ORM, 0 injection | **P0** |
| **TC-SEC-002** | Security | XSS Payload in Food Description | Create listing | Title: `<script>alert('XSS')</script>` | Script tag string | Escaped safely in rendered Django HTML templates | **P0** |
| **TC-SEC-003** | Security | CSRF Token Missing on POST | Session user | Submit POST form without `X-CSRFToken` | Missing token | `403 Forbidden`, CSRF token missing | **P0** |
| **TC-SEC-004** | Perf | Spatial Query Performance Under Load | 1,000 listings | Send 100 concurrent PostGIS requests | Radius 15km | Average response time < 50ms | **P1** |
| **TC-SEC-005** | Audit | Audit Log Record Creation on User Actions | User action | Approve organization in admin | Verification action | Entry inserted into `audit_auditlog` with IP & actor | **P0** |
| **TC-SEC-006** | Perf | Rate Limiting on Login Endpoint | Public user | Submit 20 rapid login attempts | Same IP address | `429 Too Many Requests` triggered | **P1** |

---

### 4. ACCEPTANCE CRITERIA MATRIX & DEFECT CLASSIFICATION
- **Blocker (P0):** Zero P0 defects permitted for production release. (Includes claim race conditions, unverified org access, broken OTP validation).
- **Major (P1):** Max 2 non-critical P1 defects permitted with approved hotfix plan.
- **Minor (P2):** Cosmetic UI layout glitches acceptable for initial sandbox demo.
