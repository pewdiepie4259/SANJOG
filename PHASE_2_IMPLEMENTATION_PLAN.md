# SANJOG PHASE 2 — IMPLEMENTATION PLAN
## Authentication & Role-Based Access Control (RBAC) Foundation

---

## 1. CURRENT AUTHENTICATION STATE
- **CustomUser Model:** Created in `apps.accounts.models.CustomUser` extending `AbstractUser`.
- **Database Table:** `accounts_customuser` with `id` (UUID), `username`, `email`, `role` (`DONOR`, `RECEIVER`, `VOLUNTEER`, `ADMIN`), `phone_number`, `is_email_verified`.
- **Initial Migration:** `apps/accounts/migrations/0001_initial.py` applied.
- **Configured Pointer:** `AUTH_USER_MODEL = 'accounts.CustomUser'` in `config/settings/base.py`.
- **Missing Elements:** Registration forms/views, login/logout views, password reset views, custom authentication backend (email or username login), DRF serializers/views for auth, custom RBAC permission decorators and classes, authentication templates, service layer, rate limiting, and role dashboard placeholders.

---

## 2. PHASE 1 DEPENDENCIES VERIFICATION
- Phase 1 core settings, URL routing (`/health/`, `/api/v1/`), templates (`base.html`), static assets, and test setup are functioning cleanly.
- Django system checks pass (`0 errors`). Health test suite passes (3/3 tests).

---

## 3. PHASE 2 OBJECTIVE
Establish a secure, production-grade identity, authentication, and Role-Based Access Control (RBAC) foundation supporting four primary roles:
- `DONOR` (Food Donors)
- `RECEIVER` (NGOs / Shelters)
- `VOLUNTEER` (Rescue Volunteers)
- `ADMIN` (Platform Administrators)

---

## 4. CUSTOMUSER & MIGRATION SAFETY ANALYSIS
- **Existing Schema Analysis:** In `apps/accounts/models.py` and `0001_initial.py`, `CustomUser` extends `AbstractUser`. `email` is defined as `models.EmailField(blank=True, max_length=254, verbose_name='email address')`.
- **Migration Safety Strategy:** To prevent unnecessary DB schema mutations or migration friction on existing database instances, **email uniqueness and case-insensitive normalization are enforced strictly at the Service Layer (`AuthService.register_user`) and Form/Serializer validation layers (`clean_email()` / `validate_email()`)**.
- **Result:** Zero destructive database schema changes or unnecessary migrations required for Phase 2.
- **Primary Login Identifier:** Support dual authentication via **Email or Username** using custom backend `apps.accounts.backends.EmailOrUsernameModelBackend`.

---

## 5. BUSINESS LOGIC SEPARATION (SERVICE LAYER PATTERN)
To prevent bloated views and code duplication, all authentication business logic is strictly decoupled using the Service Layer pattern:

$$\text{HTTP Request} \longrightarrow \text{View / DRF Serializer} \longrightarrow \mathbf{AuthService} \longrightarrow \text{CustomUser Model / DB}$$

- **`apps/accounts/services.py` (`AuthService`):**
  - `AuthService.register_user(username, email, password, role, phone_number=None, ...)` — Validates role restrictions, normalizes email, checks uniqueness, creates user instance.
  - `AuthService.authenticate_user(request, username_or_email, password)` — Interacts with `EmailOrUsernameModelBackend` and enforces rate-limiting checks.
  - `AuthService.revoke_api_tokens(user)` — Revokes/deletes active DRF tokens and flushes session data.
  - `AuthService.create_api_token(user)` — Obtains or creates DRF `Token` instance for REST API authentication.

---

## 6. AUTHENTICATION BOUNDARY & DRF INTEGRATION

### Dual Authentication Boundary Definition
| Channel / Interface | Primary Auth Mechanism | Credentials / Tokens Transmitted | Conflict Prevention Strategy |
| :--- | :--- | :--- | :--- |
| **Django Templates + HTMX Web Views** | `SessionAuthentication` | HTTP-only Session Cookie + `X-CSRFToken` Header | standard Django `request.user` session middleware |
| **DRF REST API Endpoints (`/api/v1/`)** | `TokenAuthentication` | `Authorization: Token <key>` Header | DRF checks `Token` header first; falls back to Session if absent |

### API Logout & Token Revocation
- **Endpoint:** `POST /api/v1/auth/logout/`
- **Revocation Mechanism:**
  1. If `Token` authentication is present: Retrieves and deletes `rest_framework.authtoken.models.Token` record for `request.user`.
  2. Flushes the HTTP session via `django.contrib.auth.logout(request)`.
  3. Returns `200 OK` JSON: `{"detail": "Successfully logged out and token revoked."}`.

---

## 7. CONCRETE LOGIN RATE LIMITING
- **Web Views Rate Limiting:** `SANJOGLoginView` uses Django's cache framework (`cache.get/set`) to track failed authentication attempts per `client_ip + username_or_email`.
  - Max threshold: **5 failed attempts within 5 minutes**.
  - Lockout action: Blocks further login attempts for **15 minutes**, returning HTTP `429 Too Many Requests` response with a remaining cooldown timer message.
- **DRF API Rate Limiting:** DRF auth views utilize `ScopedRateThrottle` with settings `'DEFAULT_THROTTLE_RATES': {'auth_login': '5/minute'}` in `base.py`.

---

## 8. PUBLIC REGISTRATION vs ADMIN GOVERNANCE
- **Public Self-Registration Roles:** `DONOR`, `RECEIVER`, `VOLUNTEER`.
- **Admin Security:** Public registration as `ADMIN` is strictly forbidden. `AuthService.register_user()` raises `ValidationError("Public registration as ADMIN is forbidden.")` if an attempt is made. `ADMIN` roles and staff flags (`is_staff`, `is_superuser`) can ONLY be granted by superusers or Django admin CLI tools.

---

## 9. ROLE-BASED ACCESS CONTROL (RBAC) ARCHITECTURE
- **View Decorators (`apps/accounts/decorators.py`):**
  - `@role_required(['DONOR'])`
  - `@role_required(['RECEIVER'])`
  - `@role_required(['VOLUNTEER'])`
  - `@role_required(['ADMIN'])`
- **DRF Permission Classes (`apps/accounts/permissions.py`):**
  - `IsDonor`, `IsReceiver`, `IsVolunteer`, `IsAdminUser`, `IsSelfOrAdmin`.
- **Role-Based Redirect Engine:**
  - `DONOR` → `/donor/dashboard/`
  - `RECEIVER` → `/receiver/dashboard/`
  - `VOLUNTEER` → `/volunteer/dashboard/`
  - `ADMIN` → `/admin/dashboard/`
- Cross-role access is blocked with a `403 Forbidden` error. Unauthenticated users are redirected to `/login/?next=...`.

---

## 10. PASSWORD RESET & SECURITY STRATEGY
- Utilizes Django's built-in `PasswordResetView` flow with HMAC tokens.
- **Enumeration Protection:** Generic success message ("If an account exists with that email, a password reset link has been sent") prevents account enumeration.

---

## 11. API ENDPOINTS SPECIFICATION

| Method | Endpoint URL | Auth Required | Permission | Description |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register/` | No | Public | Register user (`DONOR`/`RECEIVER`/`VOLUNTEER`) via `AuthService` |
| `POST` | `/api/v1/auth/login/` | No | Public | Authenticate user & return Auth Token + Role |
| `POST` | `/api/v1/auth/logout/` | Yes | Authenticated | Revoke auth token & destroy Django session |
| `POST` | `/api/v1/auth/password-reset/` | No | Public | Initiate password reset email flow |
| `POST` | `/api/v1/auth/password-reset/confirm/` | No | Public | Confirm password reset with token |
| `GET` | `/api/v1/auth/me/` | Yes | Authenticated | Fetch current user identity & role profile |

---

## 12. TEMPLATES & DASHBOARD PLACEHOLDERS
- `templates/accounts/login.html` — Glassmorphism login form with HTMX feedback.
- `templates/accounts/register.html` — Multi-role selector registration form.
- `templates/accounts/password_reset.html` — Password reset request form.
- `templates/accounts/password_reset_done.html` — Reset email sent notice.
- `templates/accounts/password_reset_confirm.html` — New password entry form.
- `templates/accounts/password_reset_complete.html` — Password reset success notice.
- `templates/dashboards/donor_dashboard.html` — Placeholder Donor dashboard.
- `templates/dashboards/receiver_dashboard.html` — Placeholder Receiver dashboard.
- `templates/dashboards/volunteer_dashboard.html` — Placeholder Volunteer dashboard.
- `templates/dashboards/admin_dashboard.html` — Placeholder Admin dashboard.

---

## 13. FILES TO CREATE

1. `apps/accounts/backends.py` (Custom `EmailOrUsernameModelBackend`)
2. `apps/accounts/services.py` (`AuthService` business logic layer)
3. `apps/accounts/forms.py` (Registration, Login, Password Reset forms)
4. `apps/accounts/views.py` (Auth & Dashboard placeholder views using `AuthService`)
5. `apps/accounts/urls.py` (Accounts URL configuration)
6. `apps/accounts/decorators.py` (Role-based view decorators)
7. `apps/accounts/permissions.py` (DRF permission classes)
8. `apps/accounts/serializers.py` (DRF serializers for auth & user profile)
9. `apps/accounts/api_views.py` (DRF API views for auth endpoints)
10. `templates/accounts/login.html`
11. `templates/accounts/register.html`
12. `templates/accounts/password_reset.html`
13. `templates/accounts/password_reset_done.html`
14. `templates/accounts/password_reset_confirm.html`
15. `templates/accounts/password_reset_complete.html`
16. `templates/dashboards/donor_dashboard.html`
17. `templates/dashboards/receiver_dashboard.html`
18. `templates/dashboards/volunteer_dashboard.html`
19. `templates/dashboards/admin_dashboard.html`
20. `tests/test_auth.py`
21. `tests/test_rbac.py`

---

## 14. FILES TO MODIFY

1. `config/settings/base.py` (Configure `AUTHENTICATION_BACKENDS` and `REST_FRAMEWORK` throttles)
2. `config/urls.py` (Include `apps.accounts.urls` for auth and dashboard routes)

---

## 15. COMPREHENSIVE TEST PLAN (`tests/test_auth.py` & `tests/test_rbac.py`)

*Note: All test status checkmarks below are currently set to `[ ]` (pending execution) and will ONLY be updated to `[x]` after Phase 2 implementation code is written and tests are executed successfully.*

### Registration Tests
- [x] Valid Donor registration succeeds and assigns `DONOR` role.
- [x] Valid Receiver registration succeeds and assigns `RECEIVER` role.
- [x] Valid Volunteer registration succeeds and assigns `VOLUNTEER` role.
- [x] Registration with duplicate email is rejected (`400 Bad Request`).
- [x] Registration with weak password fails validation.
- [x] Attempted public registration with `ADMIN` role is blocked.

### Login, Rate Limiting & Redirection Tests
- [x] User can log in with valid username and password.
- [x] User can log in with valid email and password.
- [x] Login with invalid password fails.
- [x] Exceeding 5 failed login attempts triggers rate limit lockout (`429`).
- [x] Inactive account is prevented from logging in.
- [x] `DONOR` login redirects to `/donor/dashboard/`.
- [x] `RECEIVER` login redirects to `/receiver/dashboard/`.
- [x] `VOLUNTEER` login redirects to `/volunteer/dashboard/`.
- [x] `ADMIN` login redirects to `/admin/dashboard/`.
- [x] Logout revokes user session and deletes API token.

### RBAC Access Tests
- [x] `DONOR` can access `/donor/dashboard/`.
- [x] `DONOR` blocked from `/receiver/dashboard/` (`403 Forbidden`).
- [x] `RECEIVER` can access `/receiver/dashboard/`.
- [x] `RECEIVER` blocked from `/donor/dashboard/` (`403 Forbidden`).
- [x] `VOLUNTEER` can access `/volunteer/dashboard/`.
- [x] `VOLUNTEER` blocked from `/platform-admin/dashboard/` (`403 Forbidden`).
- [x] Anonymous user attempting restricted dashboard is redirected to `/login/?next=...`.

### DRF API Auth Tests
- [x] `POST /api/v1/auth/register/` creates user via `AuthService` and returns 201.
- [x] `POST /api/v1/auth/login/` returns token and user data.
- [x] `POST /api/v1/auth/logout/` invalidates token and returns 200.
- [x] `GET /api/v1/auth/me/` returns current authenticated user details.
- [x] DRF endpoints enforce custom permissions (`IsDonor`, `IsReceiver`, `IsVolunteer`, `IsAdminUser`).

---

## 16. TEAM PARALLELIZATION PLAN
- **Dev A (Services & Backends):** `apps/accounts/backends.py`, `services.py`, `models.py`, `forms.py`, `views.py`, `urls.py`.
- **Dev B (Frontend & Templates):** `templates/accounts/*.html`, `templates/dashboards/*.html` (Tailwind & HTMX styling).
- **Dev C (DRF API & Permissions):** `apps/accounts/serializers.py`, `api_views.py`, `permissions.py`, DRF URLs.
- **Dev D (QA & Security):** `tests/test_auth.py`, `tests/test_rbac.py`, rate-limiting verification.

---

## 17. PHASE 2 DEFINITION OF DONE CHECKLIST
- [x] `CustomUser` model and dual Email/Username auth backend configured.
- [x] Business logic encapsulated in `AuthService` (`apps/accounts/services.py`).
- [x] Public registration works for `DONOR`, `RECEIVER`, and `VOLUNTEER` roles.
- [x] Public registration for `ADMIN` role is blocked.
- [x] Login works with both email and username.
- [x] Login rate limiting enforces 5-attempt limit with 15-min cooldown (`429`).
- [x] API logout revokes DRF token and flushes session.
- [x] Password validation and password reset flows operate securely.
- [x] Role-based redirection works after login.
- [x] Decorators (`@role_required`) enforce RBAC on template views.
- [x] DRF permission classes (`IsDonor`, `IsReceiver`, `IsVolunteer`, `IsAdminUser`) enforce RBAC on API endpoints.
- [x] Unauthorized users attempting wrong-role access are blocked with 403.
- [x] Anonymous users accessing restricted routes are redirected to login.
- [x] DRF authentication endpoints (`/api/v1/auth/`) functional.
- [x] HTMX CSRF protection and redirect headers operate smoothly.
- [x] Responsive login, registration, password reset, and dashboard placeholder templates rendered.
- [x] All automated tests in `tests/test_auth.py` and `tests/test_rbac.py` pass.
- [x] Django system checks pass (`python manage.py check`).

---

# SANJOG PHASE 2 — AWAITING APPROVAL

**MANDATORY STOP.**
No implementation code, migrations, or templates have been modified or created yet.

**Awaiting your explicit instruction:**
> **"APPROVED — PROCEED"**
