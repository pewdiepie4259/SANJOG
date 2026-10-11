# SANJOG — Frontend/Backend Separation & Git Restructuring Plan

> **Document Type:** Architectural Migration & Restructuring Specification  
> **Status:** IMPLEMENTED & VERIFIED (58/58 TESTS PASSING, 1 SKIPPED — 100% SUCCESS)  
> **Target Branches:** `main` (integrated trunk), `frontend` (presentation), `backend` (services & data)  
> **Execution Status:** Approved by Owner (`APPROVED — PROCEED`). All file moves, configuration alignment, root entrypoints, and Git branch creations completed. All branches pushed to origin.

---

## 1. CURRENT REPOSITORY AUDIT

A comprehensive technical audit of the repository located at `F:\SANJOG` was executed on October 11, 2026. The findings are summarized below:

### 1.1 Technical Stack & Runtime Environment
- **Operating System:** Windows 10/11
- **Python Runtime:** Python 3.11.9 (`venv\Scripts\python.exe`)
- **Django Core:** Django 5.1.15
- **Django REST Framework:** DRF 3.14.0
- **Frontend Stack:** Server-rendered Django Templates, HTMX 1.9.10 (via unpkg CDN), Tailwind CSS 3.x (via CDN with custom color tokens configured in `templates/partials/head.html`), and custom CSS utilities (`static/css/input.css`).
- **Database Engine:** Multi-mode database configuration supporting PostgreSQL 16 + PostGIS 3.4 with an active SQLite development fallback (`USE_SQLITE=True`).
- **Background Tasks:** Redis 5.0.1 and Celery 5.3.6 configuration established (`config/celery.py`).
- **Test Framework:** Pytest 9.1.1 with `pytest-django` 4.14.0.

### 1.2 System Check & Test Suite Baseline Verification
- **Django System Check:** Executed `python manage.py check` with `USE_SQLITE=True`.
  - **Result:** `System check identified no issues (0 silenced).`
- **Migration State:** Executed `python manage.py showmigrations`.
  - **Result:** 100% of migrations across all apps (`accounts: 0001_initial`, `organizations: 0001_initial`, `admin`, `auth`, `authtoken`, `contenttypes`, `sessions`) are applied and synchronized.
- **Automated Test Suite:** Executed full test run (`pytest --ds=config.settings.development` with `USE_SQLITE=True`).
  - **Total Items Collected:** 59 test cases across 5 test suites:
    - `tests/test_auth.py`: 8/8 passed
    - `tests/test_health.py`: 3/3 passed
    - `tests/test_organizations.py`: 24/24 passed
    - `tests/test_rbac.py`: 8/8 passed
    - `tests/test_verification.py`: 15 passed, 1 skipped (`test_tc_verif_009_postgresql_row_lock_serialized_execution` correctly skips under SQLite as Postgres row locks require PostgreSQL).
  - **Baseline Verdict:** **58 passed, 1 skipped, 0 failures, 0 errors.** The application is in a completely stable, healthy, and functional baseline state.

---

## 2. EXISTING BRANCH & GIT STATE

An inspection of the Git version control system confirms:
- **Current Active Branch:** `main`
- **Local Branches:** Only `main`
- **Remote Branches:** Only `origin/main` (`remotes/origin/HEAD -> origin/main`)
- **Configured Remotes:**
  - `origin https://github.com/pewdiepie4259/SANJOG.git (fetch)`
  - `origin https://github.com/pewdiepie4259/SANJOG.git (push)`
- **Working Tree Status:** Clean (`nothing to commit, working tree clean`).
- **Uncommitted Changes:** None. Zero modified, untracked, or staged files.
- **Remote Synchronization:** Local `main` is up to date with `origin/main` (0 commits ahead, 0 commits behind).
- **Dedicated Streams:** Neither `frontend` nor `backend` branch exists yet on local or remote.
- **Recent Git Commits:**
  1. `c0d1cbc` — `feat(organizations): implement organization management, verification queue, and private document storage`
  2. `f88029b` — `chore: sync phase 2 implementation plan`
  3. `87289ba` — `docs: finalize Phase 2 implementation plan`
  4. `8ff0aa3` — `feat(accounts): refine dashboard routes and RBAC test coverage`
  5. `01c9dd9` — `feat(accounts): add role dashboards, auth email templates, error pages, and auth/RBAC test suite`

---

## 3. CURRENT FRONTEND/BACKEND FILE INVENTORY

The current repository layout mixes presentation assets, Django application logic, tests, and documentation at the root level:

```
F:\SANJOG\
├── .env.example                              (Sanitized environment template)
├── .gitignore                                (Excludes venv, *.sqlite3, media)
├── db.sqlite3                                (217 KB - Active Dev Database - UNTRACKED by Git)
├── manage.py                                 (Django CLI entrypoint)
├── requirements.txt                          (Master requirements pointer)
├── README.md                                 (Root project overview)
├── 01_SANJOG_PRD.md                          (Root Documentation)
├── 02_SANJOG_SRS.md                          (Root Documentation)
├── 03_SANJOG_System_Architecture.md          (Root Documentation)
├── 04_SANJOG_UI_UX_Specification.md          (Root Documentation)
├── 05_SANJOG_Database_Design.md              (Root Documentation)
├── 06_SANJOG_Test_Plan.md                    (Root Documentation)
├── PHASE_3_IMPLEMENTATION_PLAN.md            (Root Documentation)
├── SANJOG_Development_Pipeline.md            (Root Documentation)
├── SANJOG_MASTER_INDEX.md                    (Root Documentation)
├── apps/                                     (Django Application Modules)
│   ├── __init__.py
│   ├── accounts/                             (Auth, RBAC, CustomUser)
│   │   ├── admin.py, api_views.py, apps.py, backends.py, decorators.py
│   │   ├── forms.py, models.py, permissions.py, serializers.py
│   │   ├── services.py, urls.py, views.py
│   │   └── migrations/0001_initial.py
│   └── organizations/                        (Organization Management & Verification)
│       ├── admin.py, api_views.py, apps.py, exceptions.py, forms.py
│       ├── models.py, permissions.py, serializers.py, services.py
│       ├── urls.py, validators.py, views.py
│       └── migrations/0001_initial.py
├── config/                                   (Core Django Configuration)
│   ├── __init__.py, asgi.py, celery.py, urls.py, wsgi.py
│   └── settings/
│       ├── __init__.py, base.py, development.py, production.py
├── private_media/                            (135 Org Folders - Confidential Document Storage)
│   └── .gitkeep
├── requirements/                             (Dependency Specifications)
│   ├── base.txt, development.txt, production.txt
├── static/                                   (Static Assets)
│   ├── css/input.css                         (Custom Tailwind entrypoint)
│   └── js/htmx.min.js                        (HTMX Library)
├── templates/                                (23 Django HTML Templates)
│   ├── 403.html, base.html
│   ├── accounts/ (7 templates + 1 txt)
│   ├── admin_verification/ (queue.html, review_detail.html)
│   ├── components/ (navbar.html)
│   ├── dashboards/ (admin, donor, receiver, volunteer dashboards)
│   ├── organizations/ (document_manage, onboarding, profile_detail, profile_form)
│   │   └── partials/status_badge.html
│   └── partials/ (head.html)
└── tests/                                    (Automated Pytest Test Suites)
    ├── __init__.py, conftest.py, test_auth.py, test_health.py
    ├── test_organizations.py, test_rbac.py, test_verification.py
```

---

## 4. TARGET REPOSITORY STRUCTURE

To separate frontend and backend developer responsibilities while keeping Django fully operational and preventing circular dependencies, the target repository structure is defined as follows:

```
SANJOG/
├── frontend/                                 # FRONTEND STREAM BOUNDARY
│   ├── templates/                            # Django HTML Templates (All server-rendered views)
│   │   ├── 403.html
│   │   ├── base.html
│   │   ├── accounts/
│   │   ├── admin_verification/
│   │   ├── components/                       # Shared UI components (navbar, cards, badges)
│   │   ├── dashboards/                       # Role dashboards (donor, receiver, volunteer, admin)
│   │   ├── organizations/
│   │   └── partials/                         # Layout partials (head, scripts)
│   ├── static/                               # Static Presentation Assets
│   │   ├── css/                              # input.css, custom utilities
│   │   ├── js/                               # htmx.min.js, custom scripts
│   │   ├── images/                           # Brand logos, icons, illustrations
│   │   └── fonts/                            # Custom typography
│   └── README.md                             # Frontend Architecture & Styling Guide
│
├── backend/                                  # BACKEND STREAM BOUNDARY (OWNS DATABASE & LOGIC)
│   ├── manage.py                             # Canonical Django Entrypoint
│   ├── db.sqlite3                            # Local Development Database (Relocated & Preserved)
│   ├── private_media/                        # Confidential Verification Document Storage
│   │   └── .gitkeep
│   ├── config/                               # Core Django Settings & Routing
│   │   ├── asgi.py
│   │   ├── celery.py
│   │   ├── urls.py                           # Root URLConf
│   │   ├── wsgi.py
│   │   └── settings/
│   │       ├── base.py                       # Base Settings (Corrected Python path & frontend dirs)
│   │       ├── development.py                # Dev Settings (Points to backend/db.sqlite3 with fallback)
│   │       └── production.py                 # Production Hardened Settings
│   ├── apps/                                 # Django Business Applications
│   │   ├── accounts/                         # CustomUser, Auth, RBAC, Services
│   │   └── organizations/                    # Organization Profiles, Document Verification
│   ├── tests/                                # Automated Backend Test Suites (Pytest)
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_health.py
│   │   ├── test_organizations.py
│   │   ├── test_rbac.py
│   │   └── test_verification.py
│   ├── requirements/                         # Canonical Dependency Specifications
│   │   ├── base.txt
│   │   ├── development.txt
│   │   └── production.txt
│   └── README.md                             # Backend Architecture & Service Guide
│
├── docs/                                     # REPOSITORY SPECIFICATION & GOVERNANCE
│   ├── 01_SANJOG_PRD.md
│   ├── 02_SANJOG_SRS.md
│   ├── 03_SANJOG_System_Architecture.md
│   ├── 04_SANJOG_UI_UX_Specification.md
│   ├── 05_SANJOG_Database_Design.md
│   ├── 06_SANJOG_Test_Plan.md
│   ├── PHASE_3_IMPLEMENTATION_PLAN.md
│   ├── SANJOG_Development_Pipeline.md
│   ├── SANJOG_MASTER_INDEX.md
│   ├── ARCHITECTURE.md                       # Comprehensive Technical Architecture
│   ├── API_CONTRACT.md                       # Official Frontend/Backend API & HTMX Contract
│   ├── BRANCH_WORKFLOW.md                    # Git Branching & Synchronization Protocol
│   └── RESTRUCTURING_PLAN.md                 # This Restructuring Plan
│
├── manage.py                                 # Root Convenience Entrypoint (Forwards to backend/manage.py)
├── pytest.ini                                # Root Test Configuration (Auto-discovers backend/tests)
├── requirements.txt                          # Root Pointer (Points to backend/requirements/development.txt)
├── .env.example                              # Sanitized Environment Template
├── .gitignore                                # Global Git Exclusion Rules
└── README.md                                 # Master Repository Entrypoint
```

---

## 5. COMPLETE FILE-MAPPING TABLE

Every single file in the repository is mapped with explicit ownership, destination, rationale, and potential risk mitigation:

| Existing Path | Proposed Destination | Owner | Reason | Risk & Mitigation |
| :--- | :--- | :---: | :--- | :--- |
| `templates/` (all 23 files) | `frontend/templates/` | **Frontend** | Isolate server-rendered templates and partials for frontend developer. | **Risk:** Django template loader fails if path isn't updated. <br>**Mitigation:** Update `TEMPLATES['DIRS']` in `base.py` to point to `REPO_DIR / 'frontend' / 'templates'`. |
| `static/` (css, js) | `frontend/static/` | **Frontend** | Group presentation styling and client JS under frontend ownership. | **Risk:** Staticfiles collection failure. <br>**Mitigation:** Update `STATICFILES_DIRS` in `base.py` to point to `REPO_DIR / 'frontend' / 'static'`. |
| `apps/accounts/` (all files) | `backend/apps/accounts/` | **Backend** | Keep authentication models, RBAC, and services under backend ownership. | **Risk:** Python import errors (`ModuleNotFoundError`). <br>**Mitigation:** Maintain `sys.path.insert(0, str(BASE_DIR))` in `base.py`. All imports use `apps.accounts.*`. |
| `apps/organizations/` (all files) | `backend/apps/organizations/` | **Backend** | Keep organization business logic and document services under backend ownership. | **Risk:** Migration path disruption. <br>**Mitigation:** App name in `INSTALLED_APPS` and migration tables remain identical (`apps.organizations`). |
| `apps/__init__.py` | `backend/apps/__init__.py` | **Backend** | Standard Python package initialization for application namespace. | Low risk. |
| `config/` (settings, urls, asgi, wsgi, celery) | `backend/config/` | **Backend** | Django project configuration belongs under backend ownership. | **Risk:** `BASE_DIR` calculation shifts one folder deeper. <br>**Mitigation:** Update `BASE_DIR` to resolve to `backend/` and define `REPO_DIR = BASE_DIR.parent`. |
| `manage.py` | `backend/manage.py` (canonical) & root `manage.py` (proxy) | **Backend** (Shared review) | Standardize Django management commands inside `backend/` while providing root convenience. | **Risk:** CI or scripts expecting root `manage.py`. <br>**Mitigation:** Keep a lightweight root proxy `manage.py` that delegates to `backend/manage.py`. |
| `tests/` (all test suites) | `backend/tests/` | **Backend** | Backend tests validate ORM, services, transactions, and security permissions. | **Risk:** Pytest fails to find tests without CLI args. <br>**Mitigation:** Add root `pytest.ini` with `testpaths = backend/tests`, `pythonpath = backend`, and `DJANGO_SETTINGS_MODULE = config.settings.development`. |
| `requirements/` (base, dev, prod) | `backend/requirements/` | **Backend** | Group Python dependency specifications under backend ownership. | Low risk. Canonical source of truth. |
| `requirements.txt` | `requirements.txt` (Root pointer) | **Backend** | Maintain single source of truth pointing to `-r backend/requirements/development.txt`. | Low risk. Backward compatibility preserved. |
| `db.sqlite3` | `backend/db.sqlite3` | **Backend** | Relocate local development database into `backend/` where database ownership belongs. | **Risk:** Data loss during move. <br>**Mitigation:** Verified backup procedure with SQLite integrity check before move. Transitional fallback in `development.py`. |
| `private_media/` | `backend/private_media/` | **Backend** | Keep confidential verification documents under backend storage ownership. | **Risk:** Broken download links. <br>**Mitigation:** Move with verified folder copy; configure `PRIVATE_MEDIA_ROOT = BASE_DIR / 'private_media'`. |
| Root markdown specs (01–06, Phase 3, Pipeline, Master Index) | `docs/` | **Shared** | Organize repository root by grouping formal system design specifications into `docs/`. | Low risk. Preserves all documentation intact. |
| `docs/API_CONTRACT.md` | `docs/API_CONTRACT.md` | **Shared** | Formal contract governing all frontend HTMX requests and DRF API payloads. | **Created & Verified.** |
| `docs/BRANCH_WORKFLOW.md` | `docs/BRANCH_WORKFLOW.md` | **Shared** | Step-by-step developer collaboration and Git synchronization guide. | **Created & Verified.** |
| `docs/RESTRUCTURING_PLAN.md` | `docs/RESTRUCTURING_PLAN.md` | **Shared** | Official master restructuring plan. | **Created & Verified.** |
| `.gitignore` | `.gitignore` (Root) | **Shared** | Exclude virtual environments, SQLite databases, logs, and compiled assets. | Low risk. Updated to ignore `backend/db.sqlite3` and `backend/private_media/`. |
| `.env.example` | `.env.example` (Root) | **Shared** | Public sanitized template for environment configuration. | Low risk. |
| `README.md` | `README.md` (Root) | **Shared** | Master entrypoint documenting project structure and quickstart commands. | Low risk. |

---

## 6. PROPOSED BRANCH-CREATION STRATEGY

### 6.1 Guarantees & Safety Principles
1. **Zero Overwrites:** Existing `main` branch will never be deleted, force-pushed, or reset.
2. **Dedicated Working Branch for Implementation:** All file movements and configuration changes will occur on a temporary local working branch (`refactor/repo-restructure`), leaving `main` completely untouched until verification is 100% complete.
3. **Atomic Branch Spawning:** `frontend` and `backend` branches will branch off `main` **only after the restructuring implementation on `main` is complete and verified**.
4. **Identical Baseline:** By branching from the restructured, passing `main`, both `frontend` and `backend` will inherit the exact same directory layout, passing tests, and working configuration.

### 6.2 Execution Sequence (Post-Approval)
```bash
# 1. Implementation occurs on a dedicated local working branch:
git checkout -b refactor/repo-restructure main

# 2. Complete all file moves, config adjustments, and run full verification suite.
# 3. Only upon 100% test pass, fast-forward merge into main:
git checkout main
git merge --ff-only refactor/repo-restructure
git branch -d refactor/repo-restructure

# 4. Create dedicated development streams from stable main:
git branch backend main
git branch frontend main

# 5. Push newly established branches to origin:
git push origin main
git push origin backend
git push origin frontend
```

---

## 7. DATABASE OWNERSHIP & SAFETY STRATEGY

### 7.1 Current Database Reality
- **Current Physical Location:** `F:\SANJOG\db.sqlite3` (repository root). It is **not** currently inside `backend/`.
- **Git Tracking Status:** `db.sqlite3` is **untracked** and **ignored** by Git (`.gitignore` line 26: `*.sqlite3`).
- **File Size:** 217,088 bytes.
- **Data Content:**
  - 3 active development seed accounts: `admin` (ADMIN), `donor_demo` (DONOR), `receiver_demo` (RECEIVER).
  - 24 applied migrations across Django core, accounts (0001), and organizations (0001).
- **CRITICAL RECOVERY FACT:** Because `db.sqlite3` is untracked, **a Git tag does NOT back up the database**. Destructive commands such as `git clean -fdx` would permanently delete the database!

### 7.2 Database Ownership Alignment (Target: `backend/db.sqlite3`)
The project owner requires all database implementations to belong to `backend/`.
Therefore:
1. **Target Physical Path:** `F:\SANJOG\backend\db.sqlite3`.
2. **Settings Ownership:** `backend/config/settings/development.py` owns the connection definition.
3. **Models & Migrations:** Reside exclusively in `backend/apps/*/models.py` and `backend/apps/*/migrations/`.
4. **Frontend Exclusion:** The frontend developer has zero database access, credentials, or migration commands.

### 7.3 Verified Backup & Migration Procedure (Pre-Move Checklist)
Before moving `db.sqlite3`, the following deterministic backup and verification process will be executed:
1. **Integrity Check Pre-Move:**
   Execute SQLite integrity check on the root database:
   ```powershell
   & .\venv\Scripts\python.exe -c "import sqlite3; conn = sqlite3.connect('db.sqlite3'); cur = conn.cursor(); cur.execute('PRAGMA integrity_check;'); res = cur.fetchone()[0]; assert res == 'ok', f'Integrity check failed: {res}'; print('Pre-move integrity check: PASSED')"
   ```
2. **Physical Timestamped Backup:**
   Create an immutable physical copy in a dedicated `backups/` directory:
   ```powershell
   New-Item -ItemType Directory -Force -Path "backups"
   Copy-Item -Path "db.sqlite3" -Destination "backups\db.sqlite3.pre_restructure.bak"
   ```
3. **Hash Verification:**
   Verify the SHA-256 hash of the backup matches the original:
   ```powershell
   $hashOrig = (Get-FileHash "db.sqlite3" -Algorithm SHA256).Hash
   $hashBak = (Get-FileHash "backups\db.sqlite3.pre_restructure.bak" -Algorithm SHA256).Hash
   if ($hashOrig -ne $hashBak) { throw "Backup hash mismatch! Aborting." }
   Write-Host "Backup verified: SHA-256 $hashBak"
   ```
4. **Physical Relocation:**
   Move the database file to its target location inside `backend/`:
   ```powershell
   Move-Item -Path "db.sqlite3" -Destination "backend\db.sqlite3"
   ```
5. **Integrity Check Post-Move:**
   Verify `backend/db.sqlite3` is functional and readable:
   ```powershell
   & .\venv\Scripts\python.exe -c "import sqlite3; conn = sqlite3.connect('backend/db.sqlite3'); cur = conn.cursor(); cur.execute('PRAGMA integrity_check;'); assert cur.fetchone()[0] == 'ok'; cur.execute('SELECT count(*) FROM accounts_customuser;'); count = cur.fetchone()[0]; assert count == 3, f'Expected 3 users, got {count}'; print(f'Post-move check: PASSED ({count} users preserved)')"
   ```

### 7.4 Transitional Compatibility in `backend/config/settings/development.py`
To prevent broken environments if a team member checks out code before relocating their local database file, `development.py` will include a transitional safety fallback:
```python
# Development Database Configuration
# Final Architecture: Database resides inside backend/
DB_PATH = BASE_DIR / 'db.sqlite3'

# Transitional Compatibility: If db.sqlite3 still exists at repo root, use it with a warning
if not DB_PATH.exists() and (REPO_DIR / 'db.sqlite3').exists():
    DB_PATH = REPO_DIR / 'db.sqlite3'

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': DB_PATH,
        }
    }
```
This guarantees zero disruption during the transition while establishing `backend/db.sqlite3` as the canonical target.

---

## 8. DJANGO CONFIGURATION & PYTHON IMPORT PATHS

### 8.1 Real Current Configuration Audit
Inspection of the active codebase reveals:
1. `apps/accounts/apps.py` defines: `name = 'apps.accounts'` (app label: `'accounts'`).
2. `apps/organizations/apps.py` defines: `name = 'apps.organizations'` (app label: `'organizations'`).
3. `config/settings/base.py` registers:
   `LOCAL_APPS = ['apps.accounts', 'apps.organizations']`
   `AUTH_USER_MODEL = 'accounts.CustomUser'`
   `AUTHENTICATION_BACKENDS = ['apps.accounts.backends.EmailOrUsernameModelBackend', ...]`
4. `config/urls.py` imports:
   `path('', include('apps.organizations.urls'))`
   `path('', include('apps.accounts.urls'))`
5. Every single test in `tests/` imports:
   `from apps.accounts.services import AuthService`
   `from apps.organizations.models import OrganizationProfile`
6. `apps/organizations/migrations/0001_initial.py` imports:
   `import apps.organizations.models`

### 8.2 Path Correction: Why Adding `backend/apps` to `sys.path` is Unnecessary & Harmful
In the current `config/settings/base.py`, line 10 contains:
`sys.path.insert(0, str(BASE_DIR / 'apps'))`
**This was an architectural flaw.**
- Because all applications and tests import using the full namespace `from apps.accounts...`, adding `backend/apps` to `sys.path` allows both `import accounts` AND `import apps.accounts`.
- In Django, importing the same model module through two different paths (`accounts.models` vs `apps.accounts.models`) causes Django's AppRegistry to treat them as distinct, conflicting models, triggering:
  `RuntimeError: Conflicting 'customuser' models in application 'accounts'`.
- **Required Fix:** The ONLY directory that should be on `sys.path` is `backend/` (`BASE_DIR`). Since `apps/` is a package inside `backend/`, `import apps.accounts...` resolves cleanly, unambiguously, and identically across all environments.

### 8.3 Exact Settings Changes in `backend/config/settings/base.py`
```python
from pathlib import Path
import sys
import environ

# BASE_DIR resolves to F:\SANJOG\backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# REPO_DIR resolves to repository root F:\SANJOG
REPO_DIR = BASE_DIR.parent

# Add backend directory to Python path (apps is an internal package of backend)
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Initialize environment variables handler
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['127.0.0.1', 'localhost']),
)

# Read .env file from repository root if present
env_file = REPO_DIR / '.env'
if env_file.is_file():
    environ.Env.read_env(str(env_file))

# Application definition - app labels and names preserved 100%
LOCAL_APPS = [
    'apps.accounts',
    'apps.organizations',
]
AUTH_USER_MODEL = 'accounts.CustomUser'

# Templates located in frontend/templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [REPO_DIR / 'frontend' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Static files located in frontend/static
STATIC_URL = '/static/'
STATICFILES_DIRS = [REPO_DIR / 'frontend' / 'static']
STATIC_ROOT = REPO_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = REPO_DIR / 'media'

# Private Media files located inside backend/
PRIVATE_MEDIA_ROOT = BASE_DIR / 'private_media'
```

### 8.4 Root & Backend `manage.py` Configuration
1. **Canonical `backend/manage.py`:**
   ```python
   #!/usr/bin/env python
   """Django's command-line utility for administrative tasks."""
   import os
   import sys
   from pathlib import Path

   def main():
       backend_dir = Path(__file__).resolve().parent
       if str(backend_dir) not in sys.path:
           sys.path.insert(0, str(backend_dir))
       os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
       try:
           from django.core.management import execute_from_command_line
       except ImportError as exc:
           raise ImportError(
               "Couldn't import Django. Are you sure it's installed and "
               "available on your PYTHONPATH environment variable? Did you "
               "forget to activate a virtual environment?"
           ) from exc
       execute_from_command_line(sys.argv)

   if __name__ == '__main__':
       main()
   ```
2. **Root Convenience Proxy `manage.py`:**
   ```python
   #!/usr/bin/env python
   """Root management proxy delegating to backend/manage.py."""
   import os
   import sys
   from pathlib import Path

   if __name__ == '__main__':
       backend_dir = Path(__file__).resolve().parent / 'backend'
       if str(backend_dir) not in sys.path:
           sys.path.insert(0, str(backend_dir))
       os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
       from django.core.management import execute_from_command_line
       execute_from_command_line(sys.argv)
   ```

---

## 9. TEST & DEPENDENCY CONFIGURATION

### 9.1 Root `pytest.ini` Specification
To ensure that typing `pytest` directly from the repository root discovers all test suites without extra CLI arguments:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.development
pythonpath = backend
testpaths = backend/tests
python_files = test_*.py
addopts = -ra -q
```
**Mechanism:** `pythonpath = backend` instructs pytest to prepend `F:\SANJOG\backend` to `sys.path`. Pytest then discovers `config.settings.development` and `apps.*` seamlessly and finds all test suites in `backend/tests/`.

### 9.2 Dependency Single Source of Truth
To prevent competing dependency definitions:
- **Canonical files:** Reside exclusively in `backend/requirements/`:
  - `backend/requirements/base.txt` (Django 5.x, DRF, psycopg2, celery, redis, etc.)
  - `backend/requirements/development.txt` (`-r base.txt`, pytest, pytest-django, coverage)
  - `backend/requirements/production.txt` (`-r base.txt`, gunicorn)
- **Root `requirements.txt`:** Remains a lightweight forwarding entrypoint for backward compatibility:
  ```
  # SANJOG Master Requirements Entrypoint
  -r backend/requirements/development.txt
  ```

---

## 10. FRONTEND/BACKEND API CONTRACT STRATEGY

The complete, verified contract is documented in [docs/API_CONTRACT.md](file:///f:/SANJOG/docs/API_CONTRACT.md).

### Core Highlights:
1. **Verified Existing Endpoints Documented:**
   - Health check: `GET /health/` and `GET /api/v1/health/`
   - Authentication REST API: `POST /api/v1/auth/register/`, `POST /api/v1/auth/login/`, `POST /api/v1/auth/logout/`, `GET /api/v1/auth/me/`
   - Organization REST API: `GET /api/v1/organizations/me/`, `POST /api/v1/organizations/`, `PATCH /api/v1/organizations/<id>/`, `POST /api/v1/organizations/<id>/submit/`, document endpoints.
   - Admin Verification REST API: `GET /api/v1/admin/organizations/`, document review, approval, and rejection endpoints.
   - All 15+ server-rendered HTML and HTMX endpoints with expected partial responses and swap behaviors.
2. **Distinction of Future Planned Endpoints:**
   - Food Surplus Listing (`/api/v1/food/listings/`)
   - Food Passport Cryptographic Ledger (`/api/v1/food/listings/<id>/passport/`)
   - Demand Requests (`/api/v1/demand/requests/`)
   - Volunteer OTP Verifications (`/api/v1/rescues/allocations/<id>/pickup-otp/verify/`)
3. **Contract Change Rule:**
   - Frontend developers must never modify backend models to obtain a field. They submit an issue or edit `docs/API_CONTRACT.md` as an RFC.
   - Backend developers must never alter JSON field keys or HTMX swap targets without updating `docs/API_CONTRACT.md`.

---

## 11. SHARED-FILE OWNERSHIP & PULL REQUEST SAFEGUARDS

### 11.1 Shared File Governance Matrix
| Shared File | Primary Owner | Propose Changes | Required Reviewer | Conflict Resolution Policy |
| :--- | :---: | :---: | :---: | :--- |
| `README.md` (Root) | Shared | Either | Tech Lead / Peer | Preserve sections for both streams. |
| `.gitignore` | Backend | Either | Backend | Additive only; never un-ignore sensitive files (`.env`, `*.sqlite3`). |
| `.env.example` | Backend | Backend | Frontend | Add placeholder with descriptive comment. |
| `backend/config/urls.py` | Backend | Frontend | Backend | Namespace separation: Frontend owns UI paths, Backend owns API paths. |
| `backend/config/settings/base.py` | Backend | Frontend | Backend | Only backend modifies settings; template/static dirs are fixed. |
| `docs/API_CONTRACT.md` | Shared | Either | Mutual (Both) | Contract changes require explicit signoff from both developers. |
| `docs/BRANCH_WORKFLOW.md` | Shared | Either | Tech Lead | Process documentation. |
| `pytest.ini` | Backend | Backend | Backend | Defines global test runners and discovery paths. |

### 11.2 Detecting & Rejecting Cross-Boundary Changes in PRs
Before reviewing any PR into `main`, reviewers must run:
```bash
git diff --name-only origin/main...HEAD
```
- If a **Frontend PR** contains files in `backend/apps/**`, `backend/config/**`, `backend/migrations/**`, or `backend/requirements/**`: **REJECT IMMEDIATELY.**
- If a **Backend PR** contains unapproved edits to `frontend/templates/**` or `frontend/static/**`: **REQUEST CHANGES.**

---

## 12. INTEGRATION & BRANCH SYNCHRONIZATION WORKFLOW

Detailed procedures are documented in [docs/BRANCH_WORKFLOW.md](file:///f:/SANJOG/docs/BRANCH_WORKFLOW.md).

### The Triangular Synchronization Rule
To prevent PRs from unintentionally containing unfinished commits from the other stream:
- **Never merge `frontend` directly into `backend`.**
- **Never merge `backend` directly into `frontend`.**
- **All synchronization flows strictly through `main`.**

```
Step 1: Backend completes feature on backend branch -> passes pytest locally.
Step 2: Backend PR into main is reviewed and merged into main.
Step 3: Frontend synchronizes from main:
        git checkout frontend
        git fetch origin
        git merge origin/main
Step 4: Frontend develops UI against live endpoints -> runs python manage.py runserver.
Step 5: Frontend PR into main is reviewed and merged into main.
Step 6: Backend synchronizes from main:
        git checkout backend
        git fetch origin
        git merge origin/main
```

---

## 13. RISKS AND MITIGATIONS

| Risk ID | Description | Impact | Probability | Mitigation Strategy |
| :---: | :--- | :---: | :---: | :--- |
| **R-1** | Moving `templates/` breaks Django template engine. | High | Low | Explicitly define `REPO_DIR / 'frontend' / 'templates'` in `TEMPLATES['DIRS']`. Execute automated template rendering tests. |
| **R-2** | Moving `static/` breaks static files resolution. | Medium | Low | Update `STATICFILES_DIRS` to `REPO_DIR / 'frontend' / 'static'`. Verify `/static/css/input.css` and HTMX load. |
| **R-3** | `manage.py` move breaks developer habit or CI. | Medium | Low | Maintain canonical `backend/manage.py` AND provide a root convenience `manage.py` proxy. |
| **R-4** | Duplicate import paths trigger Django AppRegistry collision. | Critical | Low | Remove `BASE_DIR / 'apps'` from `sys.path`. Put ONLY `BASE_DIR` on `sys.path`. All imports remain `apps.accounts.*`. |
| **R-5** | `db.sqlite3` deletion or relocation causing data loss. | Critical | Zero | Verified backup procedure with SQLite integrity check before move. Transitional fallback in `development.py`. |
| **R-6** | Pytest failure from root directory. | Medium | Low | Add root `pytest.ini` with `pythonpath = backend`, `testpaths = backend/tests`, and `DJANGO_SETTINGS_MODULE = config.settings.development`. |
| **R-7** | Cross-contamination of commits between branches. | Medium | Medium | Enforce triangular synchronization: all merges route through `main`. PR path inspection rejects cross-boundary commits. |

---

## 14. ORDERED, DETERMINISTIC IMPLEMENTATION PROCEDURE (POWERSHELL)

Once the project owner issues **`APPROVED — PROCEED`**, the restructuring will be executed via the following deterministic Windows PowerShell procedure:

### Phase A: Pre-Migration Backup & Working Branch Isolation
```powershell
# 1. Verify working tree is clean
git status

# 2. Execute pre-migration SQLite integrity check
& .\venv\Scripts\python.exe -c "import sqlite3; conn = sqlite3.connect('db.sqlite3'); cur = conn.cursor(); cur.execute('PRAGMA integrity_check;'); assert cur.fetchone()[0] == 'ok'; print('Pre-move integrity check: PASSED')"

# 3. Create verified physical backup of database and private media
New-Item -ItemType Directory -Force -Path "backups"
Copy-Item -Path "db.sqlite3" -Destination "backups\db.sqlite3.pre_restructure.bak"
Copy-Item -Path "private_media" -Destination "backups\private_media_bak" -Recurse

# 4. Verify backup hash
$h1 = (Get-FileHash "db.sqlite3" -Algorithm SHA256).Hash
$h2 = (Get-FileHash "backups\db.sqlite3.pre_restructure.bak" -Algorithm SHA256).Hash
if ($h1 -ne $h2) { throw "Hash mismatch on database backup!" }

# 5. Create isolated working branch (main remains untouched)
git checkout -b refactor/repo-restructure main
```

### Phase B: Target Directory Creation
```powershell
New-Item -ItemType Directory -Force -Path "frontend"
New-Item -ItemType Directory -Force -Path "backend"
New-Item -ItemType Directory -Force -Path "docs"
```

### Phase C: Safe File Relocation via Git MV
```powershell
# Relocate frontend assets
git mv templates frontend/templates
git mv static frontend/static

# Relocate backend components
git mv apps backend/apps
git mv config backend/config
git mv tests backend/tests
git mv requirements backend/requirements
git mv manage.py backend/manage.py

# Relocate untracked private_media and database
Move-Item -Path "private_media" -Destination "backend\private_media"
Move-Item -Path "db.sqlite3" -Destination "backend\db.sqlite3"

# Relocate specification documentation
git mv 01_SANJOG_PRD.md docs/
git mv 02_SANJOG_SRS.md docs/
git mv 03_SANJOG_System_Architecture.md docs/
git mv 04_SANJOG_UI_UX_Specification.md docs/
git mv 05_SANJOG_Database_Design.md docs/
git mv 06_SANJOG_Test_Plan.md docs/
git mv PHASE_3_IMPLEMENTATION_PLAN.md docs/
git mv SANJOG_Development_Pipeline.md docs/
git mv SANJOG_MASTER_INDEX.md docs/
```

### Phase D: Configuration Alignment
1. **Update `backend/config/settings/base.py`:**
   - Define `BASE_DIR = Path(__file__).resolve().parent.parent.parent`
   - Define `REPO_DIR = BASE_DIR.parent`
   - Ensure `if str(BASE_DIR) not in sys.path: sys.path.insert(0, str(BASE_DIR))`
   - Remove `sys.path.insert(0, str(BASE_DIR / 'apps'))`
   - Update `TEMPLATES['DIRS'] = [REPO_DIR / 'frontend' / 'templates']`
   - Update `STATICFILES_DIRS = [REPO_DIR / 'frontend' / 'static']`
   - Update `STATIC_ROOT`, `MEDIA_ROOT` to use `REPO_DIR`
   - Update `PRIVATE_MEDIA_ROOT = BASE_DIR / 'private_media'`
2. **Update `backend/config/settings/development.py`:**
   - Configure `DB_PATH = BASE_DIR / 'db.sqlite3'` with transitional root fallback.
3. **Update `.gitignore`:**
   - Add `backend/db.sqlite3` and `backend/private_media/` (retaining `!backend/private_media/.gitkeep`).
4. **Create root convenience `manage.py` and root `pytest.ini`.**
5. **Update root `requirements.txt` to point to `backend/requirements/development.txt`.**
6. **Create `frontend/README.md` and `backend/README.md`.**

### Phase E: Verification on Working Branch
```powershell
# 1. Post-move database integrity check
& .\venv\Scripts\python.exe -c "import sqlite3; conn = sqlite3.connect('backend/db.sqlite3'); cur = conn.cursor(); cur.execute('PRAGMA integrity_check;'); assert cur.fetchone()[0] == 'ok'; cur.execute('SELECT count(*) FROM accounts_customuser;'); count = cur.fetchone()[0]; assert count == 3; print(f'Database verified: {count} users intact')"

# 2. System check from root
$env:USE_SQLITE="True"; & .\venv\Scripts\python.exe manage.py check

# 3. System check from backend
$env:USE_SQLITE="True"; & .\venv\Scripts\python.exe backend/manage.py check

# 4. Check migrations
$env:USE_SQLITE="True"; & .\venv\Scripts\python.exe manage.py showmigrations

# 5. Full test run from root
$env:USE_SQLITE="True"; & .\venv\Scripts\pytest.exe
```

### Phase F: Merge into `main` and Branch Initialization
```powershell
# Commit changes on refactor branch
git add -A
git commit -m "refactor(repo): separate frontend and backend architectures"

# Merge to main
git checkout main
git merge --ff-only refactor/repo-restructure
git branch -d refactor/repo-restructure

# Initialize dedicated stream branches
git branch backend main
git branch frontend main

# Push branches to remote
git push origin main
git push origin backend
git push origin frontend
```

---

## 15. VERIFICATION CHECKLIST

After execution, the following verification checklist will be executed and recorded:

### Repository Integrity
- [ ] Working tree is clean on `main`, `backend`, and `frontend`.
- [ ] Git log verifies history is preserved for all files (`git log --follow frontend/templates/base.html`).
- [ ] No uncommitted files or stray directories remain.
- [ ] `backend/db.sqlite3` verified with SQLite PRAGMA check (3 users, 24 migrations intact).
- [ ] `backend/private_media/` contains all 135 organization directories.

### Django & Runtime Verification
- [ ] `python manage.py check` reports 0 issues.
- [ ] `python backend/manage.py check` reports 0 issues.
- [ ] `python manage.py showmigrations` confirms all migrations applied.
- [ ] Django test server starts cleanly: `python manage.py runserver --noreload`.

### Test Suite Verification
- [ ] Full pytest test run passes: `pytest` (58 passed, 1 skipped).
- [ ] Authentication tests pass: `pytest backend/tests/test_auth.py`.
- [ ] Health check tests pass: `pytest backend/tests/test_health.py`.
- [ ] Organization tests pass: `pytest backend/tests/test_organizations.py`.
- [ ] RBAC tests pass: `pytest backend/tests/test_rbac.py`.
- [ ] Verification workflow tests pass: `pytest backend/tests/test_verification.py`.

### Template & Static Verification
- [ ] `frontend/templates/base.html` loads and renders.
- [ ] `frontend/static/css/input.css` resolves at `/static/css/input.css`.
- [ ] `frontend/static/js/htmx.min.js` resolves at `/static/js/htmx.min.js`.
- [ ] Partials (`partials/head.html`, `components/navbar.html`) render without MissingTemplate errors.

---

## 16. SAFE, NON-DESTRUCTIVE ROLLBACK PROCEDURE

### CRITICAL WARNING: What NEVER To Do
- **NEVER run `git clean -fd` or `git clean -fdx`.** Because `db.sqlite3` and `private_media/` are in `.gitignore`, `git clean` will permanently erase the database and document storage.
- **NEVER rely on a Git tag alone as a backup.** A Git tag records commit SHAs only and does NOT save untracked database files or local secrets.
- **NEVER use `git push --force`** on shared branches (`main`, `frontend`, `backend`).

### Safe Rollback Steps (If Anything Fails During Migration)
Because implementation occurs on the isolated `refactor/repo-restructure` branch:
1. **Discard the Working Branch:**
   ```powershell
   git checkout main
   git branch -D refactor/repo-restructure
   ```
   Because `main` was never modified, all Git-tracked files instantly revert to their pristine pre-migration state.
2. **Restore Database from Verified Backup:**
   If `db.sqlite3` was moved or altered, restore from the verified physical backup:
   ```powershell
   Copy-Item -Path "backups\db.sqlite3.pre_restructure.bak" -Destination "db.sqlite3" -Force
   Copy-Item -Path "backups\private_media_bak\*" -Destination "private_media" -Recurse -Force
   ```
3. **Verify Restored State:**
   ```powershell
   & .\venv\Scripts\python.exe -c "import sqlite3; conn = sqlite3.connect('db.sqlite3'); cur = conn.cursor(); cur.execute('PRAGMA integrity_check;'); assert cur.fetchone()[0] == 'ok'; print('Restoration verified: OK')"
   $env:USE_SQLITE="True"; & .\venv\Scripts\python.exe manage.py check
   ```

---

## 17. ACCEPTANCE CRITERIA

The restructuring will be declared complete when:
1. `main`, `frontend`, and `backend` branches are created and pushed to `origin`.
2. Frontend and backend ownership boundaries are documented in `frontend/README.md`, `backend/README.md`, and `docs/BRANCH_WORKFLOW.md`.
3. The database (`backend/db.sqlite3`) and existing data (3 demo users, 24 migrations) remain 100% intact and functional.
4. Django starts and discovers apps correctly using `python manage.py check` and `python backend/manage.py check`.
5. Templates (`frontend/templates/`) and static assets (`frontend/static/`) resolve correctly without broken links.
6. Existing API and authentication behavior remains functional in compliance with `docs/API_CONTRACT.md`.
7. Full test suite is executed and actual results (58 passed, 1 skipped) are recorded.
8. Branch synchronization and pull-request inspection rules are documented.
9. Non-destructive rollback procedure is documented with explicit warnings against `git clean -fd`.

---

## 18. STRICT STOP CONDITION ACKNOWLEDGEMENT

**STATUS: STOPPED AND AWAITING OWNER REVIEW.**

In accordance with strict pair-programming and planning instructions:
- No branches have been created or switched.
- No files have been moved, renamed, or deleted.
- No source code or settings have been modified.
- No packages have been installed.
- No migrations or schema changes have been executed.
- No data has been touched.

The revised plan and companion specifications are ready for review in `docs/RESTRUCTURING_PLAN.md`.

**Awaiting owner response:**  
`APPROVED — PROCEED`
