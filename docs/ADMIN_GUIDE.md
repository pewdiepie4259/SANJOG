# SANJOG Food Rescue OS — Administration & Governance Guide

> **Document Type:** Operational Administration Manual  
> **Target Audience:** Platform Administrators, Site Reliability Engineers, and Reviewers  
> **System:** SANJOG Food Rescue Operating System  
> **Version:** 1.0.0  

---

## 1. Overview

The SANJOG Administration Panel provides secure, role-guarded governance over user accounts, compliance verification for Food Donors and Receivers, and tamper-evident audit history for regulatory oversight.

---

## 2. Local Environment & Development Server Setup

### 2.1 Virtual Environment Activation

On Windows (PowerShell):
```powershell
cd F:\SANJOG
.\venv\Scripts\activate
```

On Linux / macOS:
```bash
cd /path/to/sanjog
source venv/bin/activate
```

### 2.2 Environment Variables Configuration

Ensure the `.env` file exists at the repository root or configure session environment variables:
```powershell
# For SQLite local development (fallback mode)
$env:USE_SQLITE="True"
$env:DJANGO_SETTINGS_MODULE="config.settings.development"

# For PostgreSQL + PostGIS (production / standard dev)
# DATABASE_URL=postgis://postgres:postgres@localhost:5432/sanjog_db
```

### 2.3 Starting the Development Server

Execute using the root management proxy:
```powershell
$env:USE_SQLITE="True"
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```
- **Public Portal:** `http://127.0.0.1:8000/`
- **Django Admin Portal:** `http://127.0.0.1:8000/admin/`

---

## 3. Superuser Account Setup & Safe Credential Recovery

### 3.1 Existing Local Superuser Account
The local development database (`backend/db.sqlite3`) comes provisioned with an initial administrator:
- **Username:** `admin`
- **Email:** `admin@sanjog.org`
- **Role:** `ADMIN` (`CustomUser.RoleChoices.ADMIN`)
- **Status:** Active, Staff, Superuser

### 3.2 Safe Password Recovery
If the local password for `admin` is forgotten or lost, reset it interactively using Django's secure command:
```powershell
$env:USE_SQLITE="True"
.\venv\Scripts\python.exe manage.py changepassword admin
```
*Note: This interactively prompts for the password with hidden input and applies PBKDF2/Argon2 hashing. No plaintext credentials are ever stored in source files, environment variables, or logs.*

### 3.3 Creating an Additional Superuser
To provision a new administrator:
```powershell
$env:USE_SQLITE="True"
.\venv\Scripts\python.exe manage.py createsuperuser
```
Follow the interactive prompts for username, email, and password.

---

## 4. Models Available in Django Admin

| Model | Application | Primary Function | Available Controls |
| :--- | :--- | :--- | :--- |
| **`CustomUser`** | `apps.accounts` | User identity, authentication, and role assignment. | Search by username/email/phone; filter by role/staff/superuser; read-only timestamps; server-side privilege escalation defense. |
| **`OrganizationProfile`** | `apps.organizations` | Legal donor/receiver entity profiles and operational status. | Filter by verification status/type/city; search by trade name/registration; document and event inlines; Gate 2 approval and rejection actions. |
| **`OrganizationDocument`** | `apps.organizations` | Compliance accreditation documents (FSSAI licenses, 80G certificates). | Filter by document type/review status; authorized streaming links; individual approval and rejection actions. |
| **`OrganizationVerificationEvent`** | `apps.organizations` | Immutable verification audit log. | Search and filter events; strictly read-only (add, edit, and delete disabled; bulk delete removed). |
| **`Group`** | `django.contrib.auth` | Django permission groups. | Standard Django permission management. |
| **`TokenProxy`** | `rest_framework.authtoken` | DRF REST API tokens. | API key inspection. |

---

## 5. Administrative Verification Workflows

### 5.1 Document-Level Review (Individual)
1. Navigate to **Organization Documents** (`/admin/organizations/organizationdocument/`).
2. Click **Download File** to securely stream and review the private compliance document.
3. To approve: select the document, choose **Approve selected documents** from the Actions dropdown, and click **Go**.
4. To reject: select the document, choose **Reject selected documents with mandatory reason**, click **Go**, input the reason into the intermediate confirmation form, and confirm.

> [!NOTE]
> Bulk approval of documents without review is strictly prohibited. Each compliance document must be independently inspected.

### 5.2 Organization-Level Approval (Gate 2 Enforcement)
1. Navigate to **Organization Profiles** (`/admin/organizations/organizationprofile/`).
2. Open the pending organization to view its **Organization Documents** and **Verification Audit History** inlines.
3. Ensure every mandatory document required for the organization type (e.g., FSSAI License + Business Registration for Restaurants) has been reviewed and marked **APPROVED**.
4. Select the organization, choose **Approve selected organizations (Gate 2 Check)**, and click **Go**.
   - If any mandatory document is missing or not approved, the action **aborts safely** and displays an error message detailing the missing compliance items.
   - If eligible, the organization transitions to `APPROVED`, records the reviewing administrator, and logs an immutable audit event.

### 5.3 Organization Rejection
1. Select the organization, choose **Reject selected organizations with mandatory reason**, and click **Go**.
2. Enter the specific rejection reason in the intermediate confirmation page.
3. Confirming updates the status to `REJECTED`, records the reason, and logs an audit event.

---

## 6. Security & Authorization Guarantees

1. **Private Media Isolation:** Private documents are stored in `backend/private_media/` with `base_url=None`. No direct static URLs exist. Downloads are streamed strictly through [`organization_document_download`](file:///f:/SANJOG/backend/apps/organizations/views.py#L240) which requires active staff or authorized owner sessions.
2. **Privilege & Role Escalation Defense:**
   - Non-superusers cannot assign `role = RoleChoices.ADMIN`.
   - Non-superusers cannot set `is_superuser`, `is_staff`, `groups`, or `user_permissions` via Django Admin or crafted POST payloads.
   - Non-superusers cannot edit or delete superuser accounts or accounts holding the `ADMIN` role.
   - All M2M permissions and groups are guarded during `save_related()`.
3. **Model Permission Enforcement on Admin Actions:**
   - Organization approval/rejection requires `organizations.change_organizationprofile`.
   - Document review requires `organizations.change_organizationdocument`.
4. **Audit Immutability:** Audit records cannot be created, modified, or deleted via Django Admin or Django ORM.

---

## 7. Database Migrations Policy

Migrations must **never** be run as an incidental enhancement.
- All migrations currently needed for Django Admin are fully synchronized.
- Migration `accounts.0002_alter_customuser_user_permissions` solely aligns verbose name whitespace with Django 5.1 core and requires no SQL DDL changes. It remains unapplied in local development to preserve database integrity.
- If migration application is required in the future:
  ```powershell
  # 1. Create a verified backup
  $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
  $backupPath = Join-Path (Get-Location) "backups" "db_backup_pre_migration_${timestamp}.sqlite3"
  Copy-Item "backend\db.sqlite3" $backupPath

  # 2. Check backup integrity
  .\venv\Scripts\python.exe -c "import sqlite3; con = sqlite3.connect(r'$backupPath'); assert con.execute('PRAGMA integrity_check;').fetchone()[0] == 'ok'"

  # 3. Apply migration
  $env:USE_SQLITE="True"
  .\venv\Scripts\python.exe manage.py migrate accounts 0002
  ```

---

## 8. Running Automated Tests

To execute the Django Admin test suite:
```powershell
$env:USE_SQLITE="True"
.\venv\Scripts\pytest backend/tests/test_admin.py -v
```

To run the full core regression test suite:
```powershell
$env:USE_SQLITE="True"
.\venv\Scripts\pytest backend/tests/test_auth.py backend/tests/test_health.py backend/tests/test_verification.py backend/tests/test_organizations.py backend/tests/test_admin.py
```
*Expected baseline outcome: 78 passed, 1 skipped (`test_tc_verif_009` requires PostgreSQL row locks), 0 errors.*
