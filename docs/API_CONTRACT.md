# SANJOG — Frontend/Backend API & HTMX Contract Specification

> **Status:** OFFICIAL RESTRUCTURING CONTRACT  
> **Architecture:** SANJOG Food Rescue OS  
> **API Version:** v1 (`/api/v1/`)  
> **Frontend Integration Stack:** Django Templates + Tailwind CSS + HTMX  
> **Backend Integration Stack:** Django 5.x + Django REST Framework + PostgreSQL/PostGIS (SQLite dev fallback)

---

## 1. PURPOSE & INTEGRATION ARCHITECTURE

This contract defines the explicit interface boundary between the **Frontend** and **Backend** development streams for SANJOG.

The application utilizes a **hybrid architecture**:
1. **Server-Rendered HTMX Routes:** Server-rendered HTML partials with progressive enhancement, using Django's template engine and CSRF tokens.
2. **Headless REST API v1 (`/api/v1/`):** Token and session authenticated JSON endpoints powering client-side JavaScript, mobile/PWA interfaces, and programmatic interactions.

### Fundamental Integration Rules
1. **Zero Direct Database Access:** The frontend developer works exclusively with templates, CSS, JS, and approved HTTP/HTMX/REST endpoints. Direct database queries, schema edits, or model definitions by the frontend team are strictly prohibited.
2. **Stable Response Payloads:** Any modifications to JSON field keys, status codes, or validation dictionaries require prior mutual review and approval.
3. **CSRF Protection:** All mutating HTML/HTMX requests (`POST`, `PUT`, `PATCH`, `DELETE`) must include the Django CSRF token via standard form input `{% csrf_token %}` or HTMX header `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'` (configured globally on `<body>` in `templates/base.html`).
4. **Authentication Headers for DRF:** REST API calls from client scripts must send:
   `Authorization: Token <user_token>` or include standard Django session cookies when authenticated via browser.

---

## 2. SYSTEM STATUS & HEALTH CHECK (VERIFIED)

### 2.1 Base System Health Check
- **Endpoint:** `GET /health/` and `GET /api/v1/health/`
- **Authentication:** None (Public)
- **Permissions:** `AllowAny`
- **Request Parameters:** None
- **Response Format (200 OK):**
```json
{
  "status": "healthy",
  "system": "SANJOG Food Rescue OS",
  "version": "1.0.0",
  "database": "PostgreSQL/PostGIS"
}
```

---

## 3. AUTHENTICATION & RBAC REST APIs (VERIFIED)

Base Route: `/api/v1/auth/`

### 3.1 User Registration
- **Endpoint:** `POST /api/v1/auth/register/`
- **Authentication:** None (Public)
- **Permissions:** `AllowAny`
- **Request Headers:** `Content-Type: application/json`
- **Request Payload:**
```json
{
  "username": "food_bank_rep",
  "email": "contact@foodbank.org",
  "password": "SecurePassword123!",
  "password_confirm": "SecurePassword123!",
  "role": "RECEIVER",
  "phone_number": "+919876543210"
}
```
  - `role` must be one of: `DONOR`, `RECEIVER`, `VOLUNTEER`. (Note: `ADMIN` registration is blocked through public endpoints).
- **Success Response (201 Created):**
```json
{
  "message": "Registration successful.",
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": "c1f728be-50d4-42b4-82a1-fa3e5900259b",
    "username": "food_bank_rep",
    "email": "contact@foodbank.org",
    "role": "RECEIVER",
    "phone_number": "+919876543210",
    "is_email_verified": false
  }
}
```
- **Error Responses:**
  - `400 Bad Request` (Validation errors):
    ```json
    {
      "password": ["Passwords do not match."],
      "email": ["A user with this email already exists."]
    }
    ```

### 3.2 User Login
- **Endpoint:** `POST /api/v1/auth/login/`
- **Authentication:** None (Public)
- **Throttling:** Scoped rate limit `5/minute` per IP (`auth_login`)
- **Request Payload:**
```json
{
  "username_or_email": "contact@foodbank.org",
  "password": "SecurePassword123!"
}
```
- **Success Response (200 OK):**
```json
{
  "message": "Login successful.",
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": "c1f728be-50d4-42b4-82a1-fa3e5900259b",
    "username": "food_bank_rep",
    "email": "contact@foodbank.org",
    "role": "RECEIVER",
    "phone_number": "+919876543210",
    "is_email_verified": false
  }
}
```
- **Error Responses:**
  - `400 Bad Request`: `{"detail": "Invalid credentials provided."}`
  - `429 Too Many Requests`: `{"detail": "Request was throttled. Expected available in 57 seconds."}`

### 3.3 User Logout
- **Endpoint:** `POST /api/v1/auth/logout/`
- **Authentication:** Token or Session
- **Permissions:** `IsAuthenticated`
- **Request Payload:** `{}`
- **Success Response (200 OK):**
```json
{
  "detail": "Successfully logged out and token revoked."
}
```

### 3.4 Current User Profile
- **Endpoint:** `GET /api/v1/auth/me/`
- **Authentication:** Token or Session
- **Permissions:** `IsAuthenticated`
- **Success Response (200 OK):**
```json
{
  "id": "c1f728be-50d4-42b4-82a1-fa3e5900259b",
  "username": "food_bank_rep",
  "email": "contact@foodbank.org",
  "role": "RECEIVER",
  "phone_number": "+919876543210",
  "is_email_verified": false
}
```

---

## 4. ORGANIZATION MANAGEMENT REST APIs (VERIFIED)

Base Route: `/api/v1/organizations/`

### 4.1 Current User's Organization
- **Endpoint:** `GET /api/v1/organizations/me/`
- **Authentication:** Token or Session
- **Permissions:** `IsAuthenticated`
- **Success Response (200 OK):**
```json
{
  "id": "e891c305-6493-41bb-a4ef-e7c653ff9d21",
  "name": "Helping Hands Food Bank",
  "org_type": "NGO_CHARITY",
  "registration_number": "NGO-2026-KA-9912",
  "contact_person": "Jane Doe",
  "contact_email": "jane@helpinghands.org",
  "contact_phone": "+919876543210",
  "address_line1": "123 Compassion St",
  "address_line2": "Suite 4B",
  "city": "Bengaluru",
  "state": "Karnataka",
  "postal_code": "560001",
  "country": "India",
  "latitude": "12.9716",
  "longitude": "77.5946",
  "verification_status": "DRAFT",
  "rejection_reason": null,
  "documents": []
}
```
- **Error Responses:**
  - `404 Not Found`: `{"detail": "No organization profile found for this account."}`

### 4.2 Verification Status Badge Payload
- **Endpoint:** `GET /api/v1/organizations/me/verification-status/`
- **Authentication:** Token or Session
- **Permissions:** `IsAuthenticated`
- **Success Response (200 OK):**
```json
{
  "verification_status": "PENDING_VERIFICATION",
  "rejection_reason": null,
  "mandatory_documents_complete": true
}
```

### 4.3 Create Organization Profile
- **Endpoint:** `POST /api/v1/organizations/`
- **Authentication:** Token or Session
- **Permissions:** `IsAuthenticated`
- **Request Payload:**
```json
{
  "name": "Grand Palace Banquet",
  "org_type": "RESTAURANT",
  "registration_number": "FSSAI-112233445566",
  "contact_person": "Ramesh Kumar",
  "contact_email": "manager@grandpalace.in",
  "contact_phone": "+919876543200",
  "address_line1": "45 MG Road",
  "address_line2": null,
  "city": "Bengaluru",
  "state": "Karnataka",
  "postal_code": "560001",
  "country": "India",
  "latitude": "12.9750",
  "longitude": "77.6000"
}
```
  - Note: User role must match organization type (e.g., `DONOR` users can only select donor types; `RECEIVER` users can only select receiver types). `VOLUNTEER` accounts cannot create organization profiles (`403 Forbidden`).
- **Success Response (201 Created):** Full organization profile object.

### 4.4 Update Organization Profile
- **Endpoint:** `PATCH /api/v1/organizations/<uuid:org_id>/`
- **Authentication:** Token or Session
- **Permissions:** Owner or Admin
- **Rules:** If `verification_status` is `PENDING_VERIFICATION`, mutations are locked (`400 Bad Request: Profile fields cannot be modified while pending verification`).
- **Success Response (200 OK):** Updated profile object.

### 4.5 Submit Organization for Verification
- **Endpoint:** `POST /api/v1/organizations/<uuid:org_id>/submit/`
- **Authentication:** Token or Session
- **Permissions:** Owner only
- **Rules:** Requires all mandatory documents to be uploaded and validated.
- **Success Response (200 OK):**
```json
{
  "message": "Organization successfully submitted for verification.",
  "status": "PENDING_VERIFICATION"
}
```
- **Error Responses:**
  - `400 Bad Request`: `{"detail": "Cannot submit: Missing mandatory documents: FSSAI_LICENSE."}`

### 4.6 Document Management
- **List & Upload:** `GET` / `POST /api/v1/organizations/<uuid:org_id>/documents/`
  - Multipart upload fields:
    - `doc_type`: e.g., `FSSAI_LICENSE`, `GOVERNMENT_REGISTRATION`, `TAX_EXEMPT_80G`
    - `file`: PDF, PNG, or JPEG file (max 5 MB)
- **Retrieve & Delete:** `GET` / `DELETE /api/v1/organizations/<uuid:org_id>/documents/<uuid:doc_id>/`

---

## 5. ADMIN VERIFICATION REST APIs (VERIFIED)

Base Route: `/api/v1/admin/organizations/`  
Access: Restricted to users with `is_admin_user == True` (`ADMIN` role, staff, or superuser).

### 5.1 Admin Organization List
- **Endpoint:** `GET /api/v1/admin/organizations/`
- **Filters:** `?status=PENDING_VERIFICATION&type=RESTAURANT`

### 5.2 Review Document Action
- **Endpoint:** `POST /api/v1/admin/organizations/<uuid:org_id>/documents/<uuid:doc_id>/review/`
- **Request Payload:**
```json
{
  "review_status": "APPROVED",
  "review_notes": "Verified against FSSAI public database."
}
```
- **Values:** `review_status` can be `APPROVED` or `REJECTED`. If `REJECTED`, `review_notes` is mandatory.

### 5.3 Approve Organization
- **Endpoint:** `POST /api/v1/admin/organizations/<uuid:org_id>/approve/`
- **Rules:** All mandatory documents must be individually `APPROVED`.
- **Response (200 OK):** Organization status transitions to `VERIFIED`.

### 5.4 Reject Organization
- **Endpoint:** `POST /api/v1/admin/organizations/<uuid:org_id>/reject/`
- **Request Payload:**
```json
{
  "rejection_notes": "Registration document unreadable and expired."
}
```
- **Rules:** `rejection_notes` is mandatory.

---

## 6. HTML & HTMX INTERFACE CONTRACT (VERIFIED)

Frontend templates use HTMX attributes for asynchronous interaction without full-page reloads.

### 6.1 Authentication Template Routes
| Route | Method | View / Template | Notes |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | `accounts/login.html` or role dashboard | Redirects authenticated users to role dashboard |
| `/login/` | `GET`, `POST` | `accounts/login.html` | Session authentication form |
| `/register/` | `GET`, `POST` | `accounts/register.html` | Role-based registration form |
| `/logout/` | `POST` | Redirects to `/login/` | Flushes session |
| `/password-reset/` | `GET`, `POST` | `accounts/password_reset.html` | Password recovery workflow |

### 6.2 Role Dashboard Routes
| Route | Role Required | Template |
| :--- | :--- | :--- |
| `/donor/dashboard/` | `DONOR` | `dashboards/donor_dashboard.html` |
| `/receiver/dashboard/` | `RECEIVER` | `dashboards/receiver_dashboard.html` |
| `/volunteer/dashboard/` | `VOLUNTEER` | `dashboards/volunteer_dashboard.html` |
| `/platform-admin/dashboard/` | `ADMIN` / Staff | `dashboards/admin_dashboard.html` |

### 6.3 Organization HTML & HTMX Routes
| Route | Method | Template / Partial | HTMX Target / Interaction |
| :--- | :--- | :--- | :--- |
| `/organizations/onboarding/` | `GET` | `organizations/onboarding.html` | Multi-step onboarding guide |
| `/organizations/create/` | `GET`, `POST` | `organizations/profile_form.html` | Creates organization profile |
| `/organizations/profile/` | `GET` | `organizations/profile_detail.html` | Main profile view |
| `/organizations/profile/edit/` | `GET`, `POST` | `organizations/profile_form.html` | Updates draft profile |
| `/organizations/submit/` | `POST` | Returns status badge partial | HTMX trigger on submission button |
| `/organizations/documents/` | `GET` | `organizations/document_manage.html` | Document table and upload drawer |
| `/organizations/documents/upload/`| `POST` | Document table row partial | `hx-target="#doc-table-body" hx-swap="beforeend"` |
| `/organizations/documents/<id>/download/` | `GET` | Binary `FileResponse` | Secure document streaming with `X-Content-Type-Options: nosniff` |
| `/organizations/documents/<id>/delete/` | `POST` | Empty / Alert partial | `hx-target="closest tr" hx-swap="outerHTML swap:500ms"` |

### 6.4 Admin Verification HTML & HTMX Routes
| Route | Method | Template | HTMX Behavior |
| :--- | :--- | :--- | :--- |
| `/admin/organizations/queue/` | `GET` | `admin_verification/queue.html` | Searchable verification table |
| `/admin/organizations/<id>/review/` | `GET` | `admin_verification/review_detail.html` | Side-by-side document review pane |
| `/admin/organizations/<id>/documents/<doc_id>/review/` | `POST` | Document review badge partial | Instant row update via HTMX |
| `/admin/organizations/<id>/approve/` | `POST` | Verification banner partial | Triggers approval banner swap |
| `/admin/organizations/<id>/reject/` | `POST` | Verification banner partial | Triggers rejection banner swap |

---

## 7. PLANNED APIS (UPCOMING PHASES — CONTRACT SPECIFICATION)

The following endpoints are specified in system architecture documents (`03_SANJOG_System_Architecture.md`, `04_SANJOG_UI_UX_Specification.md`) and are scheduled for backend implementation in subsequent phases. Frontend developers must design against these planned contracts.

### 7.1 Surplus Food Listings (Phase 4 — Planned)
- **`GET /api/v1/food/listings/`** — Filter by `status` (`ACTIVE`, `ALLOCATED`, `EXPIRED`), `category`, `geo_radius`.
- **`POST /api/v1/food/listings/`** — Create surplus listing with Food Safety SOP attributes:
  ```json
  {
    "title": "Fresh Cooked Dal & Rice",
    "servings": 50,
    "approx_weight_kg": 25.0,
    "cooked_at": "2026-10-11T12:00:00Z",
    "expires_at": "2026-10-11T16:00:00Z",
    "food_category": "COOKED_MEAL",
    "storage_condition": "TEMPERATURE_CONTROLLED",
    "fssai_sop_confirmed": true
  }
  ```
- **`GET /api/v1/food/listings/<uuid:id>/passport/`** — Retrieve cryptographic Food Passport lifecycle ledger and SHA-256 integrity hash.

### 7.2 Demand Requests (Phase 5 — Planned)
- **`GET /api/v1/demand/requests/`** — Receiver demand log with location clusters.
- **`POST /api/v1/demand/requests/`** — Log meal requirements:
  ```json
  {
    "meals_needed": 40,
    "required_by": "2026-10-11T15:00:00Z",
    "beneficiary_type": "CHILDREN_SHELTER",
    "special_dietary": "VEGETARIAN"
  }
  ```

### 7.3 Logistics, Allocation & OTP Verification (Phase 6–7 — Planned)
- **`POST /api/v1/rescues/allocations/<uuid:id>/pickup-otp/verify/`** — Volunteer inputs 4-digit pickup OTP.
- **`POST /api/v1/rescues/allocations/<uuid:id>/delivery-otp/verify/`** — Volunteer inputs 4-digit delivery OTP.
- **`GET /api/v1/logistics/active-map/`** — GeoJSON feature collection for Leaflet map integration displaying active surplus nodes, demand points, and in-transit volunteers.

---

## 8. ERROR HANDLING & HTTP STATUS CODES

All API endpoints strictly follow RFC 7807 error patterns:
- `200 OK` — Successful query or idempotent action.
- `201 Created` — Resource successfully created.
- `400 Bad Request` — Field validation error or business rule violation (returns field dictionary).
- `401 Unauthorized` — Authentication credentials missing or invalid token.
- `403 Forbidden` — Authenticated user lacks RBAC role or ownership permissions.
- `404 Not Found` — Resource does not exist.
- `409 Conflict` — Concurrency conflict (e.g., duplicate concurrent admin verification decision).
- `429 Too Many Requests` — Rate limit exceeded (throttle cooldown returned).
- `500 Internal Server Error` — Unhandled server error (logged to backend monitoring).
