# SANJOG Food Rescue OS — Django Admin Panel Implementation & Superuser Setup Plan

> **Document Type:** Technical Audit, Security Specification & Implementation Plan (Completed)  
> **Status:** APPROVED, FULLY IMPLEMENTED & VERIFIED  
> **Target Date:** October 2026  
> **Repository:** `pewdiepie4259/SANJOG` (`F:\SANJOG`)  
> **Implementation Note:** Approved with `APPROVED — PROCEED`. All admin models, privilege escalation defenses, Gate 2 verification actions, secure streaming endpoints, and 28 automated test cases have been implemented and verified.

---

## 1. Executive Summary & Repository Audit Baseline

An exhaustive, non-destructive technical audit of the repository located at `F:\SANJOG` was conducted to establish the baseline state of Django Administration, authentication, user models, organizational models, storage backends, and testing pipelines.

### 1.1 Technical Architecture & Environment
- **Operating System:** Windows (Shell: PowerShell)
- **Python Virtual Environment:** `F:\SANJOG\venv\Scripts\python.exe` (Python 3.11.9)
- **Django Version:** Django 5.1.15
- **Django REST Framework:** DRF 3.14.0
- **Active Settings Module:** `config.settings.development` (configured in root `manage.py`, `backend/manage.py`, and `pytest.ini`)
- **Settings Hierarchy:**
  - `backend/config/settings/base.py`:
    - `DJANGO_APPS`: Includes `'django.contrib.admin'`, `'django.contrib.auth'`, `'django.contrib.contenttypes'`, `'django.contrib.sessions'`, `'django.contrib.messages'`, `'django.contrib.staticfiles'`.
    - `MIDDLEWARE`: Standard Django security, sessions, auth, messages, CSRF, and clickjacking protection.
    - `TEMPLATES`: Configures DjangoTemplates with auth, messages, request, and debug context processors.
    - `AUTH_USER_MODEL = 'accounts.CustomUser'`.
    - `AUTHENTICATION_BACKENDS`: Configures `apps.accounts.backends.EmailOrUsernameModelBackend` and `django.contrib.auth.backends.ModelBackend`.
    - `PRIVATE_MEDIA_ROOT = BASE_DIR / 'private_media'` (`F:\SANJOG\backend\private_media`).
  - `backend/config/settings/development.py`:
    - `DEBUG = True`, `ALLOWED_HOSTS = ['*']`.
    - `USE_SQLITE = env.bool('USE_SQLITE', default=False)`.
    - Target database defaults to PostgreSQL (`sanjog_db`) if PostgreSQL is active; falls back to SQLite (`backend/db.sqlite3` or repo root `db.sqlite3`) when `USE_SQLITE=True` is provided.
  - `backend/config/settings/production.py`:
    - Hardened production profile (`DEBUG = False`, HSTS, secure cookies, SSL redirects, PostgreSQL via `DATABASE_URL`).
- **Repository Structure:** Multi-tier directory layout:
  - `backend/`: Django core configuration (`config/`), domain applications (`apps/accounts`, `apps/organizations`), test suite (`tests/`), SQLite database (`db.sqlite3`), private document repository (`private_media/`).
  - `frontend/`: Server-rendered presentation templates (`templates/`), static CSS/JS assets (`static/`).
  - Root Directory: Contains management proxy `manage.py` (which prepends `backend/` to `sys.path` and delegates to `django.core.management`), project configuration (`pytest.ini`, `requirements.txt`), and documentation (`docs/`).

### 1.2 Root URLs & Route Mapping
- **Root URLConf:** `backend/config/urls.py`
  - Line 17: `path('', include('apps.organizations.urls'))`
  - Line 18: `path('admin/', admin.site.urls)`
  - Line 19: `path('health/', health_check, name='health_check')`
  - Line 20: `path('', include('apps.accounts.urls'))`
- **Route Coexistence & Shadowing Audit:**
  - `apps.organizations.urls` defines custom HTML and HTMX endpoints prefixed with `admin/organizations/queue/`, `admin/organizations/<uuid:org_id>/review/`, etc.
  - Django Admin routes are hosted under `/admin/` and map models under `/admin/<app_label>/<model_name>/` (e.g., `/admin/organizations/organizationprofile/`, `/admin/organizations/organizationdocument/`, `/admin/accounts/customuser/`).
  - Because `admin/organizations/organizationprofile/` and `admin/organizations/organizationdocument/` are distinct sub-paths from `admin/organizations/queue/` and `admin/organizations/<uuid:org_id>/review/`, they coexist without URL collision. Standard Django Admin remains the canonical interface for data model governance.

### 1.3 Database & Migration State
- **Active Local Database:** `backend/db.sqlite3` (~217 KB).
- **Migration Status Audit (`python manage.py showmigrations` under `USE_SQLITE="True"`):**
  - `admin`: All 3 migrations applied (`0001_initial`, `0002_logentry_remove_auto_add`, `0003_logentry_add_action_flag_choices`).
  - `auth`: All 12 migrations applied.
  - `authtoken`: All 4 migrations applied.
  - `contenttypes`: All 2 migrations applied.
  - `organizations`: `0001_initial` applied.
  - `sessions`: `0001_initial` applied.
  - `accounts`: `0001_initial` is **APPLIED**; `0002_alter_customuser_user_permissions` is **UNAPPLIED** in `backend/db.sqlite3`.

---

## 2. In-Depth Technical Analysis & Security Specifications

### 2.1 Superuser Account Status & Authentication
A read-only query of `backend/db.sqlite3` confirms that an active superuser account already exists:
- **Username:** `admin`
- **Email:** `admin@sanjog.org`
- **Role:** `ADMIN` (`CustomUser.RoleChoices.ADMIN`)
- **Status Flags:** `is_active=True`, `is_staff=True`, `is_superuser=True`
- **Password Usability:** `True` (Argon2/PBKDF2 password hash present)
- **Last Login:** `2026-10-10 17:55:25 UTC`

#### Strict Superuser Provisioning Policy:
1. **No Automatic Account Creation:** No new accounts will be generated automatically. The existing `admin` account is already provisioned in the local development database.
2. **No Custom Management Commands:** The previously proposed `createsuperuser_dev` command has been completely removed. We rely exclusively on Django's native, battle-tested administrative CLI tools.
3. **No Credential Shortcuts:** Plaintext passwords, script substitutions, and environment variable credentials are strictly prohibited. Interactive password entry via Python's `getpass` interface is mandatory.

#### Standard CLI Procedures:
- **To use or recover the existing superuser:**
  If the local password for `admin` is unknown, reset it interactively using Django's built-in command:
  ```powershell
  $env:USE_SQLITE="True"
  .\venv\Scripts\python.exe manage.py changepassword admin
  ```
- **To create an additional administrator interactively:**
  ```powershell
  $env:USE_SQLITE="True"
  .\venv\Scripts\python.exe manage.py createsuperuser
  ```
  This prompts interactively for username, email, and password with standard Django validation and hidden input.

---

### 2.2 Pending Migration Analysis & Future Protocol (`accounts.0002_alter_customuser_user_permissions`)

#### Purpose & Origin of the Migration:
Inspection of `backend/apps/accounts/migrations/0002_alter_customuser_user_permissions.py` (generated on 2026-10-12) reveals:
```python
migrations.AlterField(
    model_name='customuser',
    name='user_permissions',
    field=models.ManyToManyField(
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='user_set',
        related_query_name='user',
        to='auth.permission',
        verbose_name='user permissions'  # Aligned: 'user permissions' (with space)
    ),
)
```
In `accounts/migrations/0001_initial.py`, line 34 defined:
`verbose_name='user_permissions'` (with an underscore).  
Django 5.1's `makemigrations` detected that Django's built-in `AbstractUser` defines `verbose_name=_('user permissions')` (with a space) and generated migration `0002` to align the field's verbose name metadata with core Django.

#### Is It Required for Django Admin?
- **No.** The junction table `accounts_customuser_user_permissions` was already constructed and indexed by `0001_initial`.
- Migration `0002` executes no SQL DDL changes on SQLite or PostgreSQL; it solely updates model field metadata in Django's migration tracker (`django_migrations`).
- Django Admin functions identically with or without this migration applied.
- Therefore, **this migration will NOT be applied during the admin implementation.**

#### Isolated Future Migration & Recovery Protocol:
If and when the project owner authorizes applying this migration in the future, the following rigorous, isolated procedure must be followed:
1. **Target Database Verification:**
   Confirm target database path: `F:\SANJOG\backend\db.sqlite3` (or active PostgreSQL connection via `DATABASE_URL`).
2. **Exact Timestamped Backup (PowerShell Safe Syntax):**
   ```powershell
   New-Item -ItemType Directory -Force -Path "backups"
   $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
   $backupFileName = "db_backup_pre_migration_${timestamp}.sqlite3"
   $backupPath = Join-Path (Get-Location) "backups" $backupFileName
   Copy-Item "backend\db.sqlite3" $backupPath
   ```
3. **Backup Integrity Verification:**
   Verify that `$backupPath` exists, is non-empty, and passes SQLite integrity check:
   ```powershell
   if (-not (Test-Path $backupPath)) { throw "Backup file does not exist at $backupPath" }
   if ((Get-Item $backupPath).Length -le 0) { throw "Backup file is empty at $backupPath" }
   .\venv\Scripts\python.exe -c "import sqlite3; con = sqlite3.connect(r'$backupPath'); result = con.execute('PRAGMA integrity_check;').fetchone()[0]; con.close(); assert result == 'ok', f'Integrity check failed: {result}'; print('Backup integrity verified: ok')"
   # Expected output: Backup integrity verified: ok
   ```
4. **Execute Targeted Migration Command:**
   ```powershell
   $env:USE_SQLITE="True"
   .\venv\Scripts\python.exe manage.py migrate accounts 0002
   ```
5. **Post-Migration Verification:**
   ```powershell
   $env:USE_SQLITE="True"
   .\venv\Scripts\python.exe manage.py showmigrations accounts
   # Expected output: [X] 0002_alter_customuser_user_permissions
   ```
6. **Unambiguous Restoration / Rollback Procedure:**
   If rollback is needed:
   ```powershell
   $env:USE_SQLITE="True"
   .\venv\Scripts\python.exe manage.py migrate accounts 0001
   # Or restore verified snapshot:
   # Copy-Item $backupPath "backend\db.sqlite3" -Force
   ```

---

### 2.3 Server-Side Protection Against Privilege & Application-Role Escalation

#### The Threat Vector: Application-Role (`role`) Escalation:
Inspection of `backend/apps/accounts/models.py:39-40` reveals:
```python
@property
def is_admin_user(self):
    return self.role == self.RoleChoices.ADMIN or self.is_staff or self.is_superuser
```
Furthermore, across the application codebase:
- `@admin_required` (`backend/apps/accounts/decorators.py:45-46`) grants access if `request.user.role == 'ADMIN'` or `is_superuser`.
- Administrative review views (`AdminVerificationQueueView`, `AdminOrganizationReviewDetailView`) and API views grant access if `request.user.is_admin_user`.
- Private document streaming (`OrganizationDocumentDownloadView`) grants access if `request.user.is_admin_user`.

**Critical Vulnerability if Unchecked:** If a non-superuser staff user can change their own `role` or another user's `role` to `RoleChoices.ADMIN`, they immediately grant full application-level administrative access. Therefore, **`role` must be protected alongside `is_superuser`, `is_staff`, `groups`, and `user_permissions`.**

#### Architecture for Request-Aware Custom User Forms:
How does Django 5.1 instantiate ModelAdmin forms?
- In `ModelAdmin.changeform_view()`, Django calls `ModelForm = self.get_form(request, obj, change=not add)`.
- It then instantiates the form via `form = ModelForm(request.POST, request.FILES, instance=obj)` or `form = ModelForm(instance=obj)`.
- `ModelAdmin` **does not** automatically pass `request` or `request.user` to `ModelForm.__init__()`.
- Furthermore, returning `functools.partial(FormClass, current_user=request.user)` from `get_form()` is a known Django trap because Django internals check `issubclass(ModelForm, BaseModelForm)`, which raises a `TypeError` on `partial` objects.

#### Concrete, Django-Compatible Implementation:
In `CustomUserAdmin`, we override `get_form()` to dynamically construct a proper Python subclass of the generated `ModelForm`:
```python
def get_form(self, request, obj=None, change=False, **kwargs):
    BaseFormClass = super().get_form(request, obj, change=change, **kwargs)
    
    class RequestBoundCustomUserForm(BaseFormClass):
        def __init__(self, *args, **form_kwargs):
            form_kwargs['current_user'] = request.user
            super().__init__(*args, **form_kwargs)
            
    return RequestBoundCustomUserForm
```
This guarantees:
1. `issubclass(RequestBoundCustomUserForm, forms.ModelForm)` remains `True`.
2. Both `add_form` (`CustomUserCreationForm` inheriting `AdminUserCreationForm`) and change form (`CustomUserChangeForm` inheriting `UserChangeForm`) reliably receive `current_user = request.user`.
3. Standard Django password hashing and `ReadOnlyPasswordHashField` behavior remain 100% intact.

#### Defense-in-Depth Lifecycle Implementation:

1. **Form-Level Defense (`CustomUserCreationForm`, `CustomUserChangeForm` in `backend/apps/accounts/forms.py`):**
   - In `__init__(self, *args, current_user=None, **kwargs)`: Stores `self.current_user = current_user`.
     - If `not self.current_user or not self.current_user.is_superuser`:
       - Restrict `self.fields['role'].choices` to exclude `RoleChoices.ADMIN`.
       - If viewing an existing account with `role == RoleChoices.ADMIN`, disable the `role` field.
   - In `clean_role(self)`:
     `role = self.cleaned_data.get('role')`
     If `role == CustomUser.RoleChoices.ADMIN`:
       If `not self.current_user or not self.current_user.is_superuser`:
         raise forms.ValidationError("Only superusers are authorized to assign the Platform Administrator (ADMIN) role.")
     return role
   - In `clean()`:
     If `not self.current_user or not self.current_user.is_superuser`:
       - Explicitly strip or reject any attempted modifications to `is_superuser`, `is_staff`, `groups`, or `user_permissions` present in `cleaned_data`.
       - For existing records (`self.instance.pk`), re-bind the instance's existing database values.
   - In `_save_m2m()`:
     If `not self.current_user or not self.current_user.is_superuser`:
       - Suppress saving `groups` and `user_permissions` from cleaned data; preserve pre-existing database relationships unchanged.

2. **ModelAdmin UI & Fieldset Restrictions (`CustomUserAdmin`):**
   - `get_readonly_fields(self, request, obj=None)`:
     - Always read-only: `('id', 'date_joined', 'last_login')`.
     - If `not request.user.is_superuser`:
       Appends `('is_superuser', 'is_staff', 'groups', 'user_permissions')`.
       If `obj and obj.role == CustomUser.RoleChoices.ADMIN`:
         Appends `('role',)` as well.
   - `get_fieldsets(self, request, obj=None)`:
     - For non-superusers, excludes the permissions block from the editable fieldsets.

3. **ModelAdmin Record-Level Guards (`CustomUserAdmin`):**
   - `has_change_permission(self, request, obj=None)`:
     If `obj and not request.user.is_superuser`:
       - If `obj.is_superuser`: returns `False`. Non-superusers cannot edit superuser accounts.
       - If `obj.role == CustomUser.RoleChoices.ADMIN`: returns `False`. Non-superusers cannot edit accounts holding the `ADMIN` role.
   - `has_delete_permission(self, request, obj=None)`:
     If `obj and not request.user.is_superuser`:
       - If `obj.is_superuser`: returns `False`. Non-superusers cannot delete superuser accounts.
       - If `obj.role == CustomUser.RoleChoices.ADMIN`: returns `False`. Non-superusers cannot delete accounts holding the `ADMIN` role.

4. **ModelAdmin Instance Save Guard (`save_model`):**
   - In `save_model(self, request, obj, form, change)`:
     If `not request.user.is_superuser`:
       - If `not change`:
         If `obj.role == CustomUser.RoleChoices.ADMIN`:
           raise PermissionDenied("Only superusers can create accounts with the Platform Administrator role.")
         obj.is_superuser = False
       - If `change`:
         original = CustomUser.objects.get(pk=obj.pk)
         if original.role != CustomUser.RoleChoices.ADMIN and obj.role == CustomUser.RoleChoices.ADMIN:
           raise PermissionDenied("Only superusers can assign the Platform Administrator role.")
         if original.role == CustomUser.RoleChoices.ADMIN:
           obj.role = original.role
         obj.is_superuser = original.is_superuser
         obj.is_staff = original.is_staff

5. **ModelAdmin M2M Save Guard (`save_related`):**
   - In `save_related(self, request, form, formsets, change)`:
     If `not request.user.is_superuser` and `change`:
       - Retrieve original `groups` and `user_permissions` IDs from database prior to M2M save.
       - Execute `super().save_related(request, form, formsets, change)`.
       - Explicitly re-synchronize `obj.groups.set(original_groups)` and `obj.user_permissions.set(original_perms)` to guarantee no forged POST payload can overwrite permissions.

6. **Legitimate Superuser Administration:**
   - Active superusers (`request.user.is_superuser == True`) retain full, unhindered authority to assign `role = RoleChoices.ADMIN`, toggle `is_staff`, `is_superuser`, assign groups, and grant user permissions.

---

### 2.4 Private Document Storage & Secure Download Inspection

An audit of document handling in `backend/apps/organizations/` confirms:

1. **Storage Backend Configuration:**
   - In `backend/apps/organizations/models.py`:
     ```python
     def get_private_document_storage():
         return FileSystemStorage(
             location=settings.PRIVATE_MEDIA_ROOT,
             base_url=None  # Explicitly prevents public URL generation
         )
     ```
   - Because `base_url=None`, invoking `doc.file.url` raises a `ValueError: This storage backend cannot provide an URL.`.
   - **Critical Admin Requirement:** Django Admin's default file widget calls `value.url`. If left unhandled, opening an `OrganizationDocument` change page or inline will throw an unhandled `ValueError` 500 error. The `file` field in `OrganizationDocumentAdmin` and `OrganizationDocumentInline` must use a custom read-only presentation that never accesses `file.url`.

2. **Verified URL Route & View:**
   - In `backend/apps/organizations/urls.py`, line 14:
     ```python
     path('organizations/documents/<uuid:doc_id>/download/', views.OrganizationDocumentDownloadView.as_view(), name='organization_document_download'),
     ```
   - **Confirmed URL Name:** `'organization_document_download'`
   - **Confirmed Parameter:** `doc_id` (UUID)

3. **View Implementation & Security Headers (`OrganizationDocumentDownloadView`):**
   - In `backend/apps/organizations/views.py`, lines 240–259:
     - **Authentication Check:** `@method_decorator(login_required(login_url='/login/'))`
     - **Authorization Check:**
       `if doc.organization.user != request.user and not request.user.is_admin_user:` -> returns HTTP 403.
     - **Admin Access:** `request.user.is_admin_user` is defined on `CustomUser` as:
       `self.role == self.RoleChoices.ADMIN or self.is_staff or self.is_superuser`.
       All Django Admin staff and superusers satisfy this condition.
     - **Streaming Response:** Returns `FileResponse(file_handle, content_type=doc.content_type)`.
     - **Security Response Headers:**
       - `Content-Disposition: attachment; filename="{doc.original_filename}"`
       - `X-Content-Type-Options: nosniff`
       - `Cache-Control: private, no-cache, no-store, must-revalidate`
       - `Content-Security-Policy: default-src 'none'`

4. **Integration with Django Admin:**
   - In `OrganizationDocumentAdmin` and `OrganizationDocumentInline`, implement `secure_download_link(self, obj)`:
     Renders an HTML anchor tag pointing to `reverse('organization_document_download', kwargs={'doc_id': obj.id})`.
   - Protects confidential uploaded documents from public media exposure while providing authorized staff with instant, secure access.

---

### 2.5 Admin Verification Actions & Domain Service Alignment

The admin interface must reuse the established domain service layer without bypassing validation rules or creating ad-hoc state transitions. Furthermore, admin actions must enforce Django's model-level change permissions before execution.

#### Authorization for Admin Actions:
- In `OrganizationProfileAdmin`:
  - `approve_organization_action` and `reject_organization_action` must explicitly verify:
    ```python
    if not self.has_change_permission(request):
        raise PermissionDenied("You do not have permission to modify organization profiles.")
    ```
    This verifies that the user holds the `organizations.change_organizationprofile` permission. Staff users without this permission cannot execute the action.
- In `OrganizationDocumentAdmin`:
  - `approve_document_action` and `reject_document_action` must explicitly verify:
    ```python
    if not self.has_change_permission(request):
        raise PermissionDenied("You do not have permission to modify organization documents.")
    ```
    This verifies that the user holds the `organizations.change_organizationdocument` permission. Staff users without this permission cannot execute the action.

#### Verified Domain Services:
- **`DocumentService.review_document(admin_user, document_id, decision, rejection_reason='')`**
  - Enforces `admin_user.is_admin_user` permission check.
  - Requires non-empty `rejection_reason` when `decision == ReviewStatus.REJECTED`.
  - Atomically updates `review_status`, `reviewed_by`, `reviewed_at`, and `rejection_reason`.
- **`VerificationService.approve_organization(admin_user, org_id)`**
  - Enforces `admin_user.is_admin_user` permission check.
  - Verifies organization is currently in `PENDING` status (raises `ConcurrencyConflictError` if already processed).
  - **Enforces Gate 2:** Verifies that every mandatory document in `REQUIRED_DOCUMENTS_BY_ORG_TYPE[org.org_type]` has at least one document in `review_status == APPROVED`. Raises `ValidationError` if any mandatory document is missing or unapproved.
  - Sets `verification_status = APPROVED`, `verified_by = admin_user`, `verified_at = timezone.now()`.
  - Records an immutable `OrganizationVerificationEvent` (`APPROVED`).
- **`VerificationService.reject_organization(admin_user, org_id, rejection_reason)`**
  - Requires non-empty `rejection_reason` (raises `ValidationError` if blank).
  - Verifies organization is currently in `PENDING` status (raises `ConcurrencyConflictError` if already processed).
  - Sets `verification_status = REJECTED`, `verified_by = admin_user`, `verified_at = timezone.now()`, `rejection_reason = rejection_reason`.
  - Records an immutable `OrganizationVerificationEvent` (`REJECTED`).

#### Admin Action Constraints:
1. **No Bulk Approval of Documents:** Bulk document approval is strictly disallowed. Each compliance document must be individually inspected and approved.
2. **Intermediate Confirmation for Rejections:** Rejecting an organization or document requires a mandatory reason. Admin actions for rejection will present an intermediate confirmation form to capture this reason before calling the service.
3. **Safe Error Handling:** Catch `ValidationError` and `ConcurrencyConflictError` in admin actions and present clear messages to the administrator via `ModelAdmin.message_user()`.

#### Model Field Name Cross-Check:
All model field names have been verified against actual model code:

- **`OrganizationProfile` (`backend/apps/organizations/models.py:24`):**
  - Primary Key: `id` (UUIDField)
  - Fields: `user`, `name`, `org_type`, `registration_number`, `contact_person`, `contact_email`, `contact_phone`, `address_line1`, `address_line2`, `city`, `state`, `postal_code`, `country`, `latitude`, `longitude`, `verification_status`, `rejection_reason`, `verified_by`, `verified_at`, `created_at`, `updated_at`.
  - Reverse Relations: `documents` (related name on `OrganizationDocument`), `verification_events` (related name on `OrganizationVerificationEvent`).
- **`OrganizationDocument` (`backend/apps/organizations/models.py:128`):**
  - Primary Key: `id` (UUIDField)
  - Fields: `organization`, `document_type`, `file`, `original_filename`, `file_size_bytes`, `content_type`, `review_status`, `reviewed_by`, `reviewed_at`, `rejection_reason`, `uploaded_at`.
- **`OrganizationVerificationEvent` (`backend/apps/organizations/models.py:198`):**
  - Primary Key: `id` (UUIDField)
  - Fields: `organization`, `event_type`, `actor`, `previous_status`, `new_status`, `notes`, `created_at`.

---

### 2.6 Audit Event Immutability in Standalone Admin and Inlines

`OrganizationVerificationEvent` represents the legal and compliance audit log for food rescue verification.

#### Immutability Controls:
1. **Model Layer (`OrganizationVerificationEvent`):**
   - Overridden `save()` raises `PermissionDenied("OrganizationVerificationEvent records are immutable and cannot be updated.")` when `self.pk` exists.
   - Overridden `delete()` raises `PermissionDenied("OrganizationVerificationEvent records are immutable and cannot be deleted.")`.
   - `objects = ImmutableManager()` where `ImmutableQuerySet.update()` and `ImmutableQuerySet.delete()` raise `PermissionDenied`.
2. **Standalone Admin Layer (`OrganizationVerificationEventAdmin`):**
   - `has_add_permission(self, request) -> False`
   - `has_change_permission(self, request, obj=None) -> False`
   - `has_delete_permission(self, request, obj=None) -> False`
   - `actions = None` (Disables bulk delete or any other action)
   - `readonly_fields = ('id', 'organization', 'event_type', 'actor', 'previous_status', 'new_status', 'notes', 'created_at')`
3. **Inline Admin Layer (`OrganizationVerificationEventInline` in `OrganizationProfileAdmin`):**
   - `model = OrganizationVerificationEvent`
   - `extra = 0`
   - `can_delete = False`
   - `has_add_permission(self, request, obj=None) -> False`
   - `has_change_permission(self, request, obj=None) -> False`
   - `has_delete_permission(self, request, obj=None) -> False`
   - `readonly_fields = ('event_type', 'actor', 'previous_status', 'new_status', 'notes', 'created_at')`

---

### 2.7 Baseline Test Suite Findings & Testing Strategy

#### Baseline Audit Findings:
Execution of the project's test suite via `pytest` with `USE_SQLITE="True"` yielded:
- `backend/tests/test_auth.py`: **8 passed**
- `backend/tests/test_health.py`: **3 passed**
- `backend/tests/test_verification.py`: **15 passed, 1 skipped** (`test_tc_verif_009_postgresql_row_lock_serialized_execution` requires PostgreSQL row locks)
- `backend/tests/test_organizations.py`: **24 passed**
- `backend/tests/test_rbac.py`: **8 failed**

#### Root Cause of Pre-Existing Failures in `test_rbac.py`:
In commit `a813f9f` ("feat: connect all portals and tools into unified single link application"), role-based dashboard view functions in `backend/apps/accounts/views.py` (`donor_dashboard_view`, `receiver_dashboard_view`, `volunteer_dashboard_view`, `admin_dashboard_view`) were modified to redirect to the unified single-page shell (`/?view=...`) unless `?standalone=1` is provided. `test_rbac.py` was written prior to this change and expects direct HTTP 200 / 403 responses.

#### Test Strategy for Admin Implementation:
1. **Isolated Admin Test Suite:** All new tests will be housed in `backend/tests/test_admin.py`.
2. **Honest Reporting:** We will not claim 100% of tests pass while the 8 pre-existing RBAC failures exist.
3. **Regression Prevention:** The core baseline suites (`test_auth.py`, `test_health.py`, `test_verification.py`, `test_organizations.py`) must maintain their passing status (50 passed, 1 skipped).
4. **Targeted Execution:**
   - Admin test suite: `pytest backend/tests/test_admin.py`
   - Full suite check: `pytest backend/tests/test_auth.py backend/tests/test_health.py backend/tests/test_verification.py backend/tests/test_organizations.py backend/tests/test_admin.py`

---

## 3. Step-by-Step Implementation Sequence (Post-Approval)

### Step 1: User Administration & Privilege/Role Guards
- **File:** `backend/apps/accounts/forms.py`
  - Implement `CustomUserCreationForm(AdminUserCreationForm)` bound to `CustomUser`.
  - Implement `CustomUserChangeForm(UserChangeForm)` bound to `CustomUser` with `ReadOnlyPasswordHashField`.
  - In forms, enforce `clean_role()` to block non-superusers from setting `role = RoleChoices.ADMIN`.
  - Add `current_user` inspection and server-side validation in `clean()` and `_save_m2m()` to strip or reject unauthorized privilege escalation attempts (`is_superuser`, `is_staff`, `groups`, `user_permissions`) by non-superusers.
- **File:** `backend/apps/accounts/admin.py`
  - Update `CustomUserAdmin` with:
    - Override `get_form()` using dynamic subclassing to reliably pass `current_user = request.user` into form constructors.
    - `form = CustomUserChangeForm`, `add_form = CustomUserCreationForm`
    - `list_display = ('username', 'email', 'role', 'is_email_verified', 'is_staff', 'is_superuser', 'is_active', 'date_joined')`
    - `list_filter = ('role', 'is_email_verified', 'is_staff', 'is_superuser', 'is_active', 'date_joined')`
    - `search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')`
    - `readonly_fields = ('id', 'date_joined', 'last_login')`
    - Override `get_readonly_fields`, `get_fieldsets`, `has_change_permission`, `has_delete_permission`, `save_model`, and `save_related` for comprehensive privilege and role protection.

### Step 2: Organization Administration & Secure Document Review
- **File:** `backend/apps/organizations/admin.py`
  - Implement `OrganizationDocumentInline` (TabularInline):
    - Lists documents, document type, review status, uploaded timestamp.
    - Provides computed `secure_download_link` pointing to `reverse('organization_document_download', kwargs={'doc_id': obj.id})`.
    - Never accesses `file.url`.
  - Implement `OrganizationVerificationEventInline` (TabularInline):
    - Completely read-only (`has_add_permission=False`, `has_change_permission=False`, `has_delete_permission=False`, `can_delete=False`).
  - Configure `OrganizationProfileAdmin`:
    - `list_display = ('name', 'user', 'org_type', 'city', 'verification_status', 'created_at', 'verified_by')`
    - `list_filter = ('verification_status', 'org_type', 'city', 'state')`
    - `search_fields = ('name', 'registration_number', 'contact_person', 'contact_email', 'contact_phone', 'city', 'user__username')`
    - `readonly_fields = ('id', 'verified_by', 'verified_at', 'rejection_reason', 'created_at', 'updated_at')`
    - `inlines = [OrganizationDocumentInline, OrganizationVerificationEventInline]`
    - Add administrative action `approve_organization_action` (checks `self.has_change_permission(request)`, calls `VerificationService.approve_organization`, enforces Gate 2, handles errors safely).
    - Add intermediate view/action `reject_organization_action` (checks `self.has_change_permission(request)`, prompts for mandatory rejection reason, calls `VerificationService.reject_organization`).
  - Configure `OrganizationDocumentAdmin`:
    - `list_display = ('original_filename', 'organization', 'document_type', 'review_status', 'secure_download_link', 'uploaded_at')`
    - `list_filter = ('document_type', 'review_status', 'uploaded_at')`
    - `search_fields = ('original_filename', 'organization__name', 'organization__registration_number')`
    - `readonly_fields = ('id', 'file_size_bytes', 'content_type', 'uploaded_at', 'reviewed_by', 'reviewed_at', 'rejection_reason')`
    - Provide `secure_download_link` that renders without touching `file.url`.
    - Add administrative action `approve_document_action` (checks `self.has_change_permission(request)`, calls `DocumentService.review_document` with `APPROVED`).
    - Add intermediate action `reject_document_action` (checks `self.has_change_permission(request)`, prompts for rejection reason, calls `DocumentService.review_document` with `REJECTED`).
  - Configure `OrganizationVerificationEventAdmin`:
    - `list_display = ('organization', 'event_type', 'actor', 'previous_status', 'new_status', 'created_at')`
    - `list_filter = ('event_type', 'created_at')`
    - `search_fields = ('organization__name', 'actor__username', 'notes')`
    - `readonly_fields = ('id', 'organization', 'event_type', 'actor', 'previous_status', 'new_status', 'notes', 'created_at')`
    - `actions = None` (No bulk actions).
    - `has_add_permission = False`, `has_change_permission = False`, `has_delete_permission = False`.

### Step 3: Admin Branding
- **File:** `backend/config/urls.py`
  - Set:
    - `admin.site.site_header = "SANJOG Food Rescue OS — Administration"`
    - `admin.site.site_title = "SANJOG Admin"`
    - `admin.site.index_title = "Operational Governance & Verification Portal"`

### Step 4: Automated Testing Suite
- **File:** `backend/tests/test_admin.py`
  - Implement comprehensive automated test cases covering all criteria.

### Step 5: Documentation
- Update `README.md` and create `docs/ADMIN_GUIDE.md` detailing operational workflows, superuser management, and verification policies.

---

## 4. Comprehensive Test Plan & Acceptance Criteria Matrix

### 4.1 Automated Test Cases (`backend/tests/test_admin.py`)

| Test ID | Scenario | Verification Method | Expected Outcome |
| :--- | :--- | :--- | :--- |
| **TC-ADM-001** | Admin URL resolution | `client.get('/admin/')` | Unauthenticated user receives HTTP 302 redirecting to `/admin/login/?next=/admin/`. |
| **TC-ADM-002** | Superuser authentication | Authenticate with superuser credentials | Receives HTTP 200; access to admin dashboard granted. |
| **TC-ADM-003** | Non-staff user blocked | Authenticate with `donor_demo` (`is_staff=False`) | Access to `/admin/` is denied; redirected to login with staff challenge. |
| **TC-ADM-004** | Inactive account blocked | Authenticate with `is_active=False` account | Authentication fails; admin access denied. |
| **TC-ADM-005** | CustomUser creation via admin | Use `CustomUserCreationForm` via admin client | User created with hashed password, assigned role, and UUID primary key. |
| **TC-ADM-006** | Privilege escalation guard (UI) | Inspect form/readonly fields as non-superuser staff | `is_superuser`, `is_staff`, `groups`, `user_permissions` marked read-only. |
| **TC-ADM-007** | Privilege escalation (Crafted POST - Flags) | Submit crafted POST with `is_superuser=True`, `is_staff=True` as non-superuser | Server-side validation strips/rejects privilege escalation; user remains non-superuser. |
| **TC-ADM-008** | Privilege escalation (Crafted POST - M2M) | Submit crafted POST with `groups` or `user_permissions` as non-superuser | `save_related()` / `_save_m2m()` prevents alterations; M2M relationships remain identical. |
| **TC-ADM-009A**| Role escalation (Self-Promotion) | Non-superuser staff submits crafted POST setting own `role='ADMIN'` | Server-side validation rejects update; stored role remains unchanged; `is_admin_user` is False. |
| **TC-ADM-009B**| Role escalation (Cross-Promotion)| Non-superuser staff submits crafted POST setting other user's `role='ADMIN'` | Server-side validation rejects update; target user's role unchanged; target's `is_admin_user` is False. |
| **TC-ADM-009C**| Admin role account protection | Non-superuser staff attempts to edit or delete user with `role='ADMIN'` | Returns HTTP 403 / permission denied (`has_change_permission` and `has_delete_permission` return `False`). |
| **TC-ADM-009D**| Superuser role assignment works | Active superuser assigns `role='ADMIN'` to an account | Role is successfully updated to `ADMIN`; `is_admin_user` evaluates to `True`. |
| **TC-ADM-010** | Superuser record edit protection | Non-superuser staff attempts to edit superuser | Returns HTTP 403 / permission denied (`has_change_permission` returns `False`). |
| **TC-ADM-011** | Superuser record delete protection | Non-superuser staff attempts to delete superuser | Returns HTTP 403 / permission denied (`has_delete_permission` returns `False`). |
| **TC-ADM-012** | Normal superuser admin works | Active superuser modifies permissions, staff, and groups | Superuser can freely modify staff, groups, and permissions. |
| **TC-ADM-013** | Private storage admin rendering | Render `OrganizationDocument` change page & `OrganizationProfile` change page with inline | Renders with HTTP 200 without throwing `ValueError: This storage backend cannot provide an URL.`. |
| **TC-ADM-014** | Document download endpoint authorization | Authorized admin requests `organization_document_download` | Streams file with HTTP 200 and required security headers (`Content-Disposition: attachment`, `nosniff`, `CSP`). |
| **TC-ADM-015** | Document download endpoint denial | Unauthorized non-owner requests `organization_document_download` | Returns HTTP 403 / permission denied. |
| **TC-ADM-016** | Document review action | Admin with change permission executes document approve action | Document transitions to `APPROVED`; `reviewed_by` and `reviewed_at` updated. |
| **TC-ADM-017A**| Document review permission check | Staff user lacking `organizations.change_organizationdocument` executes approve action | Action execution is refused; returns HTTP 403 / permission denied; document unchanged. |
| **TC-ADM-017B**| Document rejection requires reason | Admin attempts document rejection without note | Rejection is rejected with validation error; status remains unchanged. |
| **TC-ADM-018A**| Organization approval Gate 2 enforced | Admin executes approve on org with missing mandatory docs | Fails with validation error; organization remains `PENDING`. |
| **TC-ADM-018B**| Organization approval permission check | Staff user lacking `organizations.change_organizationprofile` executes approve action | Action execution is refused; returns HTTP 403 / permission denied; org unchanged. |
| **TC-ADM-019** | Organization approval success | Admin with change permission executes approve on eligible org | Status transitions to `APPROVED`; audit event created. |
| **TC-ADM-020** | Organization rejection requires reason | Admin executes reject on org without note | Rejection fails; status remains unchanged. |
| **TC-ADM-021** | Standalone audit event immutability | Admin client attempts POST to add/change/delete event on `OrganizationVerificationEventAdmin` | `has_add_permission`, `has_change_permission`, `has_delete_permission` return `False`; bulk delete disabled. |
| **TC-ADM-022** | Inline audit event immutability | Admin client inspects and attempts edits via `OrganizationVerificationEventInline` | Add, change, and delete permissions are disabled; fields are strictly read-only. |
| **TC-ADM-023** | Core test suite regression baseline | Run `test_auth.py`, `test_verification.py`, `test_organizations.py` | 50 tests pass, 1 skipped (PostgreSQL row locks); zero regressions introduced. |

---

## 5. Strict Stop Condition & Confirmation

> [!IMPORTANT]
> **AWAITING OWNER REVIEW & APPROVAL**  
> In accordance with strict instructions:
> - No application source code has been altered.
> - No database schema migrations have been applied.
> - No new users have been created and no existing passwords have been altered.
> - No Git commits have been made.
>
> To proceed with implementation, reply with:
>
> **`APPROVED — PROCEED`**
