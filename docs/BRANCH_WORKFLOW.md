# SANJOG — Git Branch & Collaboration Workflow Specification

> **Document Type:** Team Collaboration & Branch Governance Specification  
> **Status:** OFFICIAL WORKFLOW SPECIFICATION (REVISED & ALIGNED)  
> **Audience:** Frontend Engineers, Backend Engineers, Tech Leads, Repository Owners  
> **Target Branches:** `main`, `frontend`, `backend`  
> **Core Principle:** Strict folder isolation (`frontend/` vs `backend/`) enables independent work without merge collision.

---

## 1. REPOSITORY REALITY: BRANCHES ARE FULL REPOSITORY SNAPSHOTS

A vital architectural fact of Git: **Git branches contain complete snapshots of the entire repository.**
- Checking out `frontend` branch does **not** hide or remove backend Python code, settings, or database files.
- Checking out `backend` branch does **not** hide or remove HTML templates or static assets.
- Both branches contain the entire runnable SANJOG project.

This design is deliberate and beneficial:
- The **frontend developer** can run the local development server (`python manage.py runserver`), inspect server-rendered templates, trigger HTMX requests, and test live UI behavior.
- The **backend developer** can execute template rendering tests, verify form contexts, and validate full request/response flows.

The separation of concerns is maintained by **file modification boundaries**:
- The frontend developer commits changes **only to `frontend/`** and frontend documentation.
- The backend developer commits changes **only to `backend/`** and backend-owned configuration or documentation.

Because each developer edits files in separate directories, Git merges both branches into `main` without file collisions.

---

## 2. BRANCH TOPOLOGY & LIFECYCLE

SANJOG uses a dedicated two-stream integration model anchored by a protected `main` branch.

```
                         [feature/be-*]
                               │
                               ▼
      backend ────────► [Reviewed PR] ──┐
         ▲                              │
         │                              ▼
         │                            main (Protected Trunk)
         │                              │
         │                              ▼
      frontend ───────► [Reviewed PR] ──┘
         ▲
         │
  [feature/fe-*]
```

### Branch Definitions
1. **`main` (Production & Integration Trunk):**
   - Contains the stable, thoroughly verified codebase.
   - **Direct commits and direct pushes to `main` are strictly forbidden.**
   - All changes enter `main` exclusively via reviewed Pull Requests / Merges.
   - Passing automated tests (`pytest`) and system check (`python manage.py check`) are mandatory prerequisites for merging into `main`.

2. **`backend` (Backend Development Stream):**
   - Dedicated long-lived branch for Python, Django, database, API, and service layer development.
   - **Primary Scope:** `backend/` directory, `backend/apps/`, `backend/config/`, `backend/tests/`, migrations, dependency configurations.
   - Owned by the Backend Developer.

3. **`frontend` (Frontend Development Stream):**
   - Dedicated long-lived branch for Django HTML templates, HTMX attributes, Tailwind CSS styling, and client-side JavaScript.
   - **Primary Scope:** `frontend/` directory, `frontend/templates/`, `frontend/static/`, UI layouts, responsive styling, client forms.
   - Owned by the Frontend Developer.

---

## 3. DEVELOPER ROLES & RESPONSIBILITY MATRIX

| Responsibility / Area | Frontend Stream (`frontend`) | Backend Stream (`backend`) | Shared / Review Required |
| :--- | :---: | :---: | :---: |
| HTML Templates (`frontend/templates/`) | **Primary Owner** | Read-Only | Mutual review on major partial changes |
| Static Assets (`frontend/static/`) | **Primary Owner** | Read-Only | - |
| Tailwind CSS & UI Styling | **Primary Owner** | Read-Only | - |
| HTMX Attributes & Swaps | **Primary Owner** | Read-Only | Contract compliance required |
| Django Models & Fields | Forbidden | **Primary Owner** | - |
| Database Migrations | Forbidden | **Primary Owner** | Zero frontend migrations allowed |
| Database Config & PostGIS | Forbidden | **Primary Owner** | - |
| DRF Views, Serializers, APIs | Request via Contract | **Primary Owner** | Document in `docs/API_CONTRACT.md` |
| Business Services & SOPs | Forbidden | **Primary Owner** | - |
| Core Django Settings | Forbidden | **Primary Owner** | Template/static path changes reviewed |
| Root URL Wiring (`backend/config/urls.py`) | Propose route | **Primary Owner** | Mutual review |
| Tests (`backend/tests/`) | Template/UI tests | **Primary Owner** | All tests must pass before merge |
| Shared Docs (`docs/`) | UI & Contract docs | Architecture docs | Mutual review |

---

## 4. SAFE SYNCHRONIZATION WORKFLOW (AVOIDING CROSS-CONTAMINATION)

### The Triangular Synchronization Rule
To prevent PRs from unintentionally containing unfinished or dirty commits from the other stream:
- **Never merge `frontend` directly into `backend`.**
- **Never merge `backend` directly into `frontend`.**
- **All synchronization flows strictly through `main`.**

```
Step 1: Backend implements & tests feature on backend branch.
Step 2: Backend PR into main is reviewed, passes CI, and merges into main.
Step 3: Frontend pulls the integrated main into frontend branch:
        git checkout frontend
        git fetch origin
        git merge origin/main
Step 4: Frontend develops templates against updated backend APIs.
Step 5: Frontend PR into main is reviewed, passes CI, and merges into main.
Step 6: Backend pulls the integrated main into backend branch:
        git checkout backend
        git fetch origin
        git merge origin/main
```

### 4.1 How Frontend Obtains Backend / API Updates
1. Backend merges their tested feature branch into `main`.
2. Frontend developer runs:
   ```bash
   git checkout frontend
   git fetch origin
   git merge origin/main
   ```
3. Frontend now has the latest Django models, serializers, and endpoints in their local repository without any unstaged or foreign commits.

### 4.2 How Backend Obtains Frontend Updates for Integration Testing
1. Frontend merges their template/styling PR into `main`.
2. Backend developer runs:
   ```bash
   git checkout backend
   git fetch origin
   git merge origin/main
   ```
3. Backend now has the latest templates and assets to verify full-stack rendering in tests.

---

## 5. DETECTING & REJECTING CROSS-BOUNDARY CHANGES IN PULL REQUESTS

Every Pull Request must be audited before review to ensure strict adherence to directory ownership boundaries.

### 5.1 Automated Inspection Command for PRs
Run the following Git inspection command against the merge target (`origin/main`):

```bash
# List all files modified in the pull request branch
git diff --name-only origin/main...HEAD
```

### 5.2 Rejection Rules:
1. **Frontend PR Violations:**
   - If `git diff --name-only origin/main...HEAD` includes any files matching:
     - `backend/apps/**`
     - `backend/config/**`
     - `backend/migrations/**`
     - `*.sqlite3`
     - `backend/requirements/**`
   - **Action:** **REJECT PULL REQUEST IMMEDIATELY.** Request that the frontend developer remove backend modifications before re-requesting review.
2. **Backend PR Violations:**
   - If `git diff --name-only origin/main...HEAD` includes any files matching:
     - `frontend/templates/**`
     - `frontend/static/**`
   - **Action:** **FLAG FOR REVIEW.** Ensure template changes were explicitly requested by frontend or restricted to agreed context variables.
3. **Shared File Modifications:**
   - If changes touch `.gitignore`, `requirements.txt`, `manage.py`, or `docs/API_CONTRACT.md`, require explicit signoff from both stream leads.

---

## 6. DAY-TO-DAY COMMAND GUIDE

### 6.1 Backend Developer Daily Flow
```bash
# Start from latest main
git checkout backend
git fetch origin
git merge origin/main

# Create feature branch
git checkout -b feature/be-food-listing

# Implement models, serializers, services, tests in backend/
# Run tests locally
pytest

# Commit changes (strictly within backend/ and docs/)
git add backend/ docs/
git commit -m "feat(food): implement surplus food listing models and safety assessment"

# Push and create PR targeting backend (or main if team lead)
git push origin feature/be-food-listing
```

### 6.2 Frontend Developer Daily Flow
```bash
# Start from latest main
git checkout frontend
git fetch origin
git merge origin/main

# Create feature branch
git checkout -b feature/fe-listing-cards

# Start Django server to preview templates and test HTMX
python manage.py runserver

# Implement templates and styling in frontend/
# Commit changes (strictly within frontend/ and docs/)
git add frontend/ docs/
git commit -m "feat(ui): implement responsive food listing cards with urgency badges"

# Push and create PR targeting frontend (or main if team lead)
git push origin feature/fe-listing-cards
```

---

## 7. RESOLVING MERGE CONFLICTS SAFELY

Because frontend files live in `frontend/` and backend files live in `backend/`, day-to-day code conflicts are eliminated by design.

When conflicts occur in shared infrastructure files (`docs/API_CONTRACT.md`, `urls.py`, `requirements.txt`):
1. **Never use `git push --force`** on shared branches (`main`, `frontend`, `backend`).
2. Pull latest `main`:
   ```bash
   git merge origin/main
   ```
3. Resolve the conflict deliberately:
   - For `urls.py`: Retain both URL inclusions (ensure both frontend route paths and backend API paths are preserved).
   - For `API_CONTRACT.md`: Combine both contract additions.
4. Verify Django check: `python manage.py check`.
5. Run tests: `pytest`.
6. Commit the merge:
   ```bash
   git commit -m "chore(sync): resolve integration merge conflicts from main"
   git push origin <branch-name>
   ```

---

## 8. NON-DESTRUCTIVE ROLLBACK PROCEDURES

If an integrated commit on `main` causes regressions:
1. **Never rewrite history with `git reset --hard` on `origin/main`.**
2. Use non-destructive `git revert`:
   ```bash
   git revert -m 1 <merge_commit_sha>
   git push origin main
   ```
3. The originating developer diagnoses the issue on their dedicated branch, fixes the regression with automated tests, and submits a fresh PR.
