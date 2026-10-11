# SANJOG — Frontend Stream Documentation

> **Branch:** `frontend`  
> **Primary Scope:** `frontend/` directory  
> **Technologies:** Django Templates, Tailwind CSS (Utility classes), HTMX (AJAX swaps), Leaflet.js (Map radar)

---

## 1. Directory Structure

```
frontend/
├── templates/
│   ├── base.html                     # Core layout shell with CSRF and HTMX headers
│   ├── accounts/                     # Authentication views (login, register, password reset)
│   ├── admin_verification/           # Admin verification queue & review detail
│   ├── components/                   # Reusable UI components (navbar, badges, dialogs)
│   ├── dashboards/                   # Role-based dashboards (donor, receiver, volunteer, admin)
│   ├── organizations/                # Organization profile & document management views
│   └── partials/                     # Layout partials (head, scripts)
├── static/
│   ├── css/input.css                 # Custom Tailwind CSS entrypoint
│   └── js/htmx.min.js                # HTMX JavaScript library
└── README.md                         # This guide
```

---

## 2. Frontend Developer Workflow

### Running the Local Development Server
From the repository root:
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` to test server-rendered templates and HTMX interactions.

### Development Rules
1. **Commit Boundaries:** Keep all commits strictly confined to `frontend/` (and frontend documentation).
2. **Zero Database Modifications:** Never modify database models, migrations, or backend settings.
3. **API Integration:** Consume approved endpoints as documented in `docs/API_CONTRACT.md`.
4. **CSRF Handling:** All mutating forms and HTMX calls inherit CSRF headers configured on `<body>` in `frontend/templates/base.html`.
5. **Branch Synchronization:**
   ```bash
   git checkout frontend
   git fetch origin
   git merge origin/main
   ```
