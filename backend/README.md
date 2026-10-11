# SANJOG — Backend Stream Documentation

> **Branch:** `backend`  
> **Primary Scope:** `backend/` directory  
> **Technologies:** Django 5.x, Django REST Framework, PostgreSQL 16 + PostGIS 3.4 (SQLite dev fallback), Celery, Redis

---

## 1. Directory Structure

```
backend/
├── manage.py                         # Canonical Django CLI entrypoint
├── db.sqlite3                        # Local Development Database (Preserved)
├── private_media/                    # Confidential uploaded documents (Non-public storage)
├── config/                           # Core Django settings, URLs, ASGI, WSGI, Celery
│   ├── settings/
│   │   ├── base.py                   # Shared configuration (Frontend paths wired)
│   │   ├── development.py            # Development configuration (SQLite dev mode)
│   │   └── production.py             # Production hardened configuration
│   └── urls.py                       # Root URL routing & API namespaces
├── apps/                             # Django application modules
│   ├── accounts/                     # User model, Auth service, RBAC, Tokens
│   └── organizations/                # Organization profiles, Document verification
├── tests/                            # Automated Pytest test suites
├── requirements/                     # Canonical dependency specifications
│   ├── base.txt                      # Core production dependencies
│   ├── development.txt               # Testing & linting tools
│   └── production.txt                # Deployment tools (gunicorn)
└── README.md                         # This guide
```

---

## 2. Backend Developer Workflow

### Running Tests
From the repository root:
```bash
pytest
```
Or with explicit settings:
```bash
pytest backend/tests
```

### Running Management Commands
From root:
```bash
python manage.py <command>
```
Or directly from `backend/`:
```bash
python backend/manage.py <command>
```

### Development Rules
1. **Database Ownership:** Sole authority for models, migrations, and database schema changes.
2. **Commit Boundaries:** Keep commits strictly within `backend/` and backend documentation.
3. **API Contracts:** Document new or modified endpoints in `docs/API_CONTRACT.md` before merging into `main`.
4. **Branch Synchronization:**
   ```bash
   git checkout backend
   git fetch origin
   git merge origin/main
   ```
