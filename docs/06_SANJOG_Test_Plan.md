# SANJOG — Quality Assurance & Test Plan
## Verification Suite & Comprehensive Test Cases (Food Rescue OS)

---

### 1. TESTING STRATEGY & OBJECTIVES
The testing suite for **SANJOG (Food Rescue OS)** provides comprehensive validation across all 11 Django application modules. It validates Need-First demand logging, food safety SOP evaluations, deterministic weighted matching, multi-recipient allocation transaction locks (`select_for_update`), Food Passport SHA-256 chain-of-custody hashes, dual OTP handoffs, Celery SLA background workers, and ML forecasting fallbacks.

---

### 2. REVISED TEST CASE SUITE (62 TEST CASES)

#### MODULE 1: AUTHENTICATION & RBAC (8 TEST CASES)
- **TC-AUTH-001:** User Registration with Valid Data (`201 Created`).
- **TC-AUTH-002:** Registration with Duplicate Email (`400 Bad Request`).
- **TC-AUTH-003:** Registration with Weak Password (`400 Bad Request`).
- **TC-AUTH-004:** Login with Valid Credentials (`200 OK`, JWT Tokens).
- **TC-AUTH-005:** Login with Invalid Password (`401 Unauthorized`).
- **TC-AUTH-006:** Receiver Accessing Donor Surplus Creation API (`403 Forbidden`).
- **TC-AUTH-007:** Donor Accessing Admin Verification Queue (`403 Forbidden`).
- **TC-AUTH-008:** JWT Token Expiration Enforcement (`401 Unauthorized`).

#### MODULE 2: ORGANIZATION ONBOARDING & VERIFICATION (6 TEST CASES)
- **TC-ORG-001:** Submit Org Profile & PDF FSSAI Document (`201 Created`, status `PENDING`).
- **TC-ORG-002:** Submit Executable File as Document (`400 Bad Request`).
- **TC-ORG-003:** Admin Approves Pending Organization (`200 OK`, status `VERIFIED`).
- **TC-ORG-004:** Admin Rejects Organization with Notes (`200 OK`, status `REJECTED`).
- **TC-ORG-005:** Unverified Donor Attempts to Post Food (`403 Forbidden`).
- **TC-ORG-006:** Verified Donor Posts Food Successfully (`201 Created`).

#### MODULE 3: FOOD SAFETY SOP & SURPLUS LISTING (6 TEST CASES)
- **TC-SAFETY-001:** Create Food Listing with Valid Safety SOP (`201 Created`, SOP status `ELIGIBLE`).
- **TC-SAFETY-002:** Create Listing with High Temp Storage (>4h ambient) (`400 Bad Request`, SOP status `NOT_ELIGIBLE`).
- **TC-SAFETY-003:** Create Listing without Safety Checklist (`400 Bad Request`, SOP check mandatory).
- **TC-SAFETY-004:** Listing Expiry Timestamp in the Past (`400 Bad Request`).
- **TC-SAFETY-005:** Image Upload Exceeding 5MB Limit (`400 Bad Request`).
- **TC-SAFETY-006:** Correct Initial SLA Urgency Assignment (`SAFE` / `NORMAL` for >2h expiry).

#### MODULE 4: RECEIVER NEED-FIRST DEMAND REQUESTS (4 TEST CASES)
- **TC-DEMAND-001:** Verified Receiver Logs Valid DemandRequest (`201 Created`, status `ACTIVE`).
- **TC-DEMAND-002:** Log DemandRequest with Zero Servings (`400 Bad Request`, servings > 0 required).
- **TC-DEMAND-003:** Log DemandRequest with Expired Required-By Timestamp (`400 Bad Request`).
- **TC-DEMAND-004:** Query Active Nearby Demand via PostGIS (`200 OK`, lists active demands within radius).

#### MODULE 5: DETERMINISTIC NEED-FIRST MATCHING ENGINE (4 TEST CASES)
- **TC-MATCH-001:** System Matches Surplus Listing to Nearby Active Demand (`200 OK`, returns ranked demand list).
- **TC-MATCH-002:** Matching Engine Filters Out Incompatible Dietary Types (Veg vs Non-Veg).
- **TC-MATCH-003:** Matching Engine Prioritizes Higher Urgency SLA Listings over Normal Listings.
- **TC-MATCH-004:** Matching Engine Handles Zero Matched Demand Gracefully (Returns empty match array).

#### MODULE 6: MULTI-RECIPIENT ALLOCATION & CONCURRENCY (5 TEST CASES)
- **TC-ALLOC-001:** Single Surplus Listing Split Across 2 Receivers (`201 Created`, creates 2 `RescueAllocation` records).
- **TC-ALLOC-002:** Concurrent Allocation Attempt (Race Condition) (`select_for_update` lock prevents over-allocation).
- **TC-ALLOC-003:** Attempt to Allocate More Servings Than Available (`409 Conflict`, error "Insufficient remaining servings").
- **TC-ALLOC-004:** Receiver Confirms Allocation (`200 OK`, status transitions to `CONFIRMED`).
- **TC-ALLOC-005:** Allocation Timeout Auto-Cancellation (Unconfirmed allocation auto-cancels after 15 mins).

#### MODULE 7: FOOD PASSPORT CHAIN-OF-CUSTODY (4 TEST CASES)
- **TC-PASS-001:** Auto-Initialization of FoodPassport on Listing Creation (`FoodPassport` created with event `CREATED`).
- **TC-PASS-002:** Custody Event Appended on Pickup OTP Validation (`200 OK`, event `PICKED_UP` added).
- **TC-PASS-003:** Custody Event Appended on Delivery OTP Validation (`200 OK`, event `DELIVERED` added).
- **TC-PASS-004:** SHA-256 Passport State Hash Verification (State hash recomputed and verified).

#### MODULE 8: VOLUNTEER LOGISTICS & DUAL OTP HANDOFF (8 TEST CASES)
- **TC-OTP-001:** Volunteer Accepts Unassigned Rescue Task (`PickupRequest` status `ASSIGNED`).
- **TC-OTP-002:** Valid Donor Pickup OTP Entry (`200 OK`, status `PICKED_UP`).
- **TC-OTP-003:** Invalid Pickup OTP Entry (Attempt 1) (`422 Unprocessable`, remaining attempts = 2).
- **TC-OTP-004:** Exceed Max Failed OTP Attempts (3 Fails) (Verification locked 15m, Admin flagged).
- **TC-OTP-005:** Valid Receiver Delivery OTP Entry (`200 OK`, status `DELIVERED`).
- **TC-OTP-006:** Attempt Delivery OTP Before Pickup (`400 Bad Request`).
- **TC-OTP-007:** Expired OTP Submission (>30 mins) (`422 Unprocessable`, error "OTP expired").
- **TC-OTP-008:** Redis OTP Key Cleanup Post-Verification (Redis key purged immediately).

#### MODULE 9: RESCUE SLA & CELERY AUTO-EXPIRY (5 TEST CASES)
- **TC-SLA-001:** Automatic SLA Tier Escalation (`NORMAL` → `URGENT` when expiry < 2h).
- **TC-SLA-002:** Dynamic SLA Tier Escalation (`URGENT` → `CRITICAL` when expiry < 1h).
- **TC-SLA-003:** Background Celery Auto-Expiry Execution (Unclaimed listings past expiry set to `EXPIRED`).
- **TC-SLA-004:** Expired Listing Pin Absent from Public Leaflet Map.
- **TC-SLA-005:** Celery Worker Dispatching Urgent Broadcast Alerts.

#### MODULE 10: IMPACT LEDGER & CSR CERTIFICATES (4 TEST CASES)
- **TC-CERT-001:** Transactional ImpactLedger Entry Created on Delivery (`ImpactLedger` row added).
- **TC-CERT-002:** WeasyPrint PDF Certificate Auto-Generation (`DonationCertificate` created with SHA-256 hash).
- **TC-CERT-003:** Donor Downloads Valid PDF Certificate (`200 OK`, valid `application/pdf` stream).
- **TC-CERT-004:** Public Impact Metrics API Returns Accurate Totals.

#### MODULE 11: AI/ML FORECASTING & SECURITY (8 TEST CASES)
- **TC-ML-001:** ML Demand Forecaster Returns Predicted Servings (`200 OK`, predictions generated).
- **TC-ML-002:** ML Engine Graceful Fallback to Moving Average when Data is Sparse.
- **TC-SEC-001:** SQL Injection Payload in Search Query (Handled safely by Django ORM).
- **TC-SEC-002:** XSS Payload in Food Description (Escaped safely in Django templates).
- **TC-SEC-003:** CSRF Token Missing on POST Request (`403 Forbidden`).
- **TC-SEC-004:** PostGIS Spatial Query Performance Under Load (<50ms average).
- **TC-SEC-005:** System AuditLog Record Creation on Verification Events.
- **TC-SEC-006:** Rate Limiting Enforcement on Auth Endpoints (`429 Too Many Requests`).
