# SANJOG — PHASE 4 IMPLEMENTATION PLAN: DONOR SURPLUS & FOOD SAFETY SOP MODULE

> **Document Type:** Phase Implementation Plan  
> **Target Phase:** Phase 4 — Donor Surplus Food Listing & Food Safety SOP Evaluation  
> **Status:** READY FOR REVIEW & APPROVAL  
> **Author:** Antigravity AI Engineering Team  
> **Target Application:** `apps.food`  

---

## 1. Executive Summary & Why Phase 4 is Next

### 1.1 Repository State Justification
The technical audit confirms that:
1. **Phase 1 (Django Foundation)** is solid and restructured into clean `backend/`, `frontend/`, and `docs/` boundaries.
2. **Phase 2 (Accounts & RBAC)** provides `CustomUser` with role enforcement, authentication backends, and permission classes.
3. **Phase 3 (Organization Management & Verification)** is completely implemented in `apps/organizations` with rigorous document security, 2-gate verification logic, and immutable audit logs.

With verified donor organizations capable of reaching `APPROVED` status, the core mission of SANJOG — food rescue — requires the capability for verified food donors (restaurants, hotels, messes, caterers) to declare surplus food and submit structured safety assessments.

Without surplus food listings, Receiver Demand Requests (Phase 5), Discovery Maps (Phase 6), and Matching/Allocation (Phases 7–8) have no food supply to operate on. **Phase 4 is the logical, foundational next step.**

---

## 2. Scope & Exclusions

### 2.1 In Scope (Phase 4 Deliverables)
1. **New Django Application:** Create `backend/apps/food/` registered in `LOCAL_APPS`.
2. **Data Models:**
   - `FoodListing`: Surplus food details (title, food category, diet type, servings, weight, cooked timestamp, expiry timestamp, pickup coordinates, listing status, dynamic SLA tier).
   - `FoodSafetyAssessment`: Structured evaluation of preparation hygiene, packaging type, storage temperature, allergens, and automated SOP classification (`ELIGIBLE`, `REVIEW_REQUIRED`, `NOT_ELIGIBLE`).
3. **Business Logic & Service Layer (`FoodService`, `SafetyAssessmentService`):**
   - Donor verification gate: Only donors belonging to an `APPROVED` organization can create or update food listings.
   - Deterministic Food Safety SOP rule engine evaluating safety thresholds.
   - Dynamic SLA urgency calculator: `NORMAL` (> 2 hours remaining), `URGENT` (1 to 2 hours remaining), `CRITICAL` (< 1 hour remaining before expiry).
4. **Presentation & UI (Django Templates + Tailwind + HTMX):**
   - Donor Surplus Listing creation form with safety checklist.
   - Active surplus food inventory dashboard for verified donors.
   - Food listing detail view showing safety badge, remaining time counter, and location.
5. **REST API Endpoints (`/api/v1/food/`):**
   - `GET /api/v1/food/listings/` (Filterable list of available listings).
   - `POST /api/v1/food/listings/` (Create listing + safety assessment).
   - `GET /api/v1/food/listings/{id}/` (Detail).
   - `PATCH /api/v1/food/listings/{id}/` (Update available quantity or cancel).
6. **Automated Test Suite:**
   - Complete unit and integration tests covering SOP rule classification, donor verification gating, SLA tier calculations, model constraints, and API permissions.

### 2.2 Explicit Exclusions (Out of Scope for Phase 4)
- **Receiver Demand Claiming / Matching Engine (Deferred to Phases 5 & 7):** Receivers cannot claim listings yet.
- **Multi-Recipient Allocation Locks (Deferred to Phase 8):** Dividing listings across multiple receivers.
- **Volunteer Task Assignment & OTP Verification (Deferred to Phases 9 & 10):** Driver pickup assignment and delivery PINs.
- **Cryptographic Food Passport SHA-256 Chaining (Deferred to Phase 11):** The initial `FoodListing` is designed to link cleanly to `FoodPassport` in Phase 11.
- **Asynchronous Periodic Celery Auto-Expiry Tasks (Deferred to Phase 12):** SLA tiers will be dynamically computed via model properties/service logic in Phase 4; background periodic worker will automate status updates in Phase 12.

---

## 3. Data Models & Database Architecture

### 3.1 Model 1: `FoodListing` (`backend/apps/food/models.py`)

```python
class FoodListing(models.Model):
    class FoodCategory(models.TextChoices):
        COOKED_MEAL = 'COOKED_MEAL', 'Cooked Meal / Prepared Food'
        BAKERY = 'BAKERY', 'Bakery / Bread Items'
        PACKAGED = 'PACKAGED', 'Packaged / Canned Food'
        RAW_PRODUCE = 'RAW_PRODUCE', 'Raw Fruits & Vegetables'

    class FoodType(models.TextChoices):
        VEG = 'VEG', 'Vegetarian'
        NON_VEG = 'NON_VEG', 'Non-Vegetarian'
        JAIN = 'JAIN', 'Jain (No Root Veg)'
        VEGAN = 'VEGAN', 'Vegan'

    class ListingStatus(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available for Rescue'
        PARTIALLY_ALLOCATED = 'PARTIALLY_ALLOCATED', 'Partially Allocated'
        FULLY_ALLOCATED = 'FULLY_ALLOCATED', 'Fully Allocated'
        EXPIRED = 'EXPIRED', 'Expired / Past Safe Window'
        CANCELLED = 'CANCELLED', 'Cancelled by Donor'

    class SLATier(models.TextChoices):
        NORMAL = 'NORMAL', 'Normal SLA (> 2 hours)'
        URGENT = 'URGENT', 'Urgent SLA (1–2 hours)'
        CRITICAL = 'CRITICAL', 'Critical SLA (< 1 hour)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor_organization = models.ForeignKey(
        'organizations.OrganizationProfile',
        on_delete=models.CASCADE,
        related_name='food_listings',
        help_text="Verified donor organization offering the surplus food"
    )
    title = models.CharField(max_length=200, help_text="e.g. 50 Portions Veg Biryani & Curry")
    food_category = models.CharField(max_length=50, choices=FoodCategory.choices)
    food_type = models.CharField(max_length=20, choices=FoodType.choices)
    description = models.TextField(blank=True, default='')

    # Quantities
    total_servings = models.PositiveIntegerField(help_text="Initial total estimated meal portions")
    remaining_servings = models.PositiveIntegerField(db_index=True, help_text="Remaining portions available for rescue")
    total_weight_kg = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Time Bounds
    cooked_at = models.DateTimeField(help_text="Timestamp when food was prepared")
    expires_at = models.DateTimeField(db_index=True, help_text="Safe consumption deadline")

    # Physical Pickup Coordinates (DecimalField for engine portability)
    pickup_address = models.CharField(max_length=255)
    pickup_city = models.CharField(max_length=100, db_index=True)
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6)

    # Status & Urgency
    status = models.CharField(
        max_length=30,
        choices=ListingStatus.choices,
        default=ListingStatus.AVAILABLE,
        db_index=True
    )
    sla_tier = models.CharField(
        max_length=20,
        choices=SLATier.choices,
        default=SLATier.NORMAL,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 3.2 Model 2: `FoodSafetyAssessment` (`backend/apps/food/models.py`)

```python
class FoodSafetyAssessment(models.Model):
    class SafetyStatus(models.TextChoices):
        ELIGIBLE = 'ELIGIBLE', 'Eligible for Direct Rescue'
        REVIEW_REQUIRED = 'REVIEW_REQUIRED', 'Safety Review Required'
        NOT_ELIGIBLE = 'NOT_ELIGIBLE', 'Rejected: Fails Food Safety Standards'

    class StorageTemperature(models.TextChoices):
        HOT = 'HOT', 'Hot Holding (> 60°C)'
        ROOM_TEMP = 'ROOM_TEMP', 'Ambient / Room Temperature (20–25°C)'
        REFRIGERATED = 'REFRIGERATED', 'Refrigerated (< 5°C)'
        FROZEN = 'FROZEN', 'Frozen (< -18°C)'

    class PackagingType(models.TextChoices):
        SEALED_CONTAINER = 'SEALED_CONTAINER', 'Food-Grade Sealed Container'
        ALUMINUM_FOIL = 'ALUMINUM_FOIL', 'Aluminum Foil Pack'
        ORIGINAL_PACKAGING = 'ORIGINAL_PACKAGING', 'Original Manufacturer Packaging'
        OPEN_VESSEL = 'OPEN_VESSEL', 'Open Vessel / Unsealed Tray'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    food_listing = models.OneToOneField(
        FoodListing,
        on_delete=models.CASCADE,
        related_name='safety_assessment'
    )
    storage_temperature = models.CharField(max_length=50, choices=StorageTemperature.choices)
    packaging_type = models.CharField(max_length=50, choices=PackagingType.choices)
    has_allergens = models.BooleanField(default=False)
    allergen_details = models.CharField(max_length=255, blank=True, default='')
    hygiene_checklist_passed = models.BooleanField(
        default=False,
        help_text="Confirms prepared in clean environment, covered, clean utensils used"
    )
    safety_status = models.CharField(
        max_length=30,
        choices=SafetyStatus.choices,
        default=SafetyStatus.REVIEW_REQUIRED,
        db_index=True
    )
    assessment_notes = models.TextField(blank=True, default='')
    assessed_at = models.DateTimeField(auto_now_add=True)
```

### 3.3 Food Safety SOP Evaluation Rules

The service layer evaluates safety rules deterministically:
1. **`NOT_ELIGIBLE` Conditions:**
   - If `expires_at <= cooked_at` or `expires_at <= timezone.now()`.
   - If `hygiene_checklist_passed is False`.
   - If `cooked_at` was more than 4 hours ago for cooked meals held at `ROOM_TEMP` (danger zone violation).
2. **`REVIEW_REQUIRED` Conditions:**
   - If `packaging_type == OPEN_VESSEL`.
   - If `has_allergens is True` and `allergen_details` is empty.
3. **`ELIGIBLE` Conditions:**
   - `hygiene_checklist_passed is True`, safe temperature maintained, safe time window, and non-open packaging.

---

## 4. Affected Files & Architecture Additions

### 4.1 New Files
- `backend/apps/food/__init__.py`
- `backend/apps/food/apps.py` (`FoodConfig`)
- `backend/apps/food/models.py` (`FoodListing`, `FoodSafetyAssessment`)
- `backend/apps/food/services.py` (`FoodService`, `SafetyAssessmentService`)
- `backend/apps/food/forms.py` (`FoodListingForm`, `SafetyAssessmentForm`)
- `backend/apps/food/views.py` (Listing creation, listing detail, donor inventory dashboard)
- `backend/apps/food/api_views.py` (DRF listing endpoints)
- `backend/apps/food/serializers.py` (DRF serializers)
- `backend/apps/food/permissions.py` (`IsVerifiedDonor`)
- `backend/apps/food/urls.py`
- `backend/apps/food/migrations/0001_initial.py`
- `backend/tests/test_food.py` (Comprehensive unit and API test suite)
- `frontend/templates/food/listing_create.html`
- `frontend/templates/food/listing_detail.html`
- `frontend/templates/food/donor_inventory.html`
- `frontend/templates/food/partials/safety_badge.html`

### 4.2 Configuration Modifications
- `backend/config/settings/base.py`: Add `'apps.food'` to `LOCAL_APPS`.
- `backend/config/urls.py`: Add `path('', include('apps.food.urls'))` and API v1 include.

---

## 5. Security & Access Control Considerations

1. **Strict Organization Verification Gate:**
   - Unverified donors (`OrganizationProfile.verification_status != APPROVED`) are barred from posting surplus listings.
   - Volunteers and Receivers cannot post food listings.
2. **Immutability of Historical Quantities:**
   - Once posted, `total_servings` cannot be reduced below `remaining_servings`.
3. **Data Sanitization:**
   - XSS prevention on `title`, `description`, and `allergen_details` via Django forms and DRF serializers.
4. **GPS Coordinate Precision:**
   - Validate latitude (-90 to +90) and longitude (-180 to +180) boundaries.

---

## 6. Detailed Test Plan (Target: 18+ Tests in `test_food.py`)

| Test Code | Scenario | Expected Outcome |
| :--- | :--- | :--- |
| `TC-FOOD-001` | Verified donor creates valid food listing | `FoodListing` created with `status=AVAILABLE`, initial `remaining_servings == total_servings`. |
| `TC-FOOD-002` | Unverified donor (DRAFT/PENDING/REJECTED) attempts to post | `PermissionDenied` raised; HTTP 403. |
| `TC-FOOD-003` | Non-donor role (RECEIVER / VOLUNTEER) attempts to post | `PermissionDenied` raised; HTTP 403. |
| `TC-FOOD-004` | Safety SOP evaluates compliant hot-held meal | `safety_status == ELIGIBLE`. |
| `TC-FOOD-005` | Safety SOP evaluates unhygienic preparation (`hygiene=False`) | `safety_status == NOT_ELIGIBLE`, listing rejected. |
| `TC-FOOD-006` | Safety SOP evaluates meal past expiry | `ValidationError` raised. |
| `TC-FOOD-007` | Safety SOP evaluates ambient meal > 4 hours old | `safety_status == NOT_ELIGIBLE`. |
| `TC-FOOD-008` | Safety SOP evaluates open vessel packaging | `safety_status == REVIEW_REQUIRED`. |
| `TC-FOOD-009` | Dynamic SLA tier calculation (> 2 hours remaining) | `sla_tier == NORMAL`. |
| `TC-FOOD-010` | Dynamic SLA tier calculation (90 minutes remaining) | `sla_tier == URGENT`. |
| `TC-FOOD-011` | Dynamic SLA tier calculation (45 minutes remaining) | `sla_tier == CRITICAL`. |
| `TC-FOOD-012` | Donor cancels available food listing | `status == CANCELLED`. |
| `TC-FOOD-013` | Non-owner donor attempts to edit/cancel listing | HTTP 403 Forbidden. |
| `TC-FOOD-014` | REST API listing list endpoint with category filter | Returns HTTP 200 with filtered items. |
| `TC-FOOD-015` | REST API listing creation with valid payload | Returns HTTP 201 Created with nested assessment. |
| `TC-FOOD-016` | Coordinate bounds validation (lat 95.0) | `ValidationError` raised. |
| `TC-FOOD-017` | Zero or negative servings validation | `ValidationError` raised. |
| `TC-FOOD-018` | Anonymous user viewing public available listings | Allowed (read-only); HTTP 200. |

---

## 7. Acceptance Criteria

Phase 4 is complete and verified when:
1. `apps.food` is created, integrated into settings, and migration `0001_initial.py` applies cleanly without warnings.
2. Verified donors can successfully submit food listings with automated SOP safety classification.
3. Listings with `NOT_ELIGIBLE` status are blocked from active rescue status.
4. Unverified donors, receivers, and volunteers are blocked from listing food.
5. All 18+ tests in `backend/tests/test_food.py` pass with 0 errors.
6. All 59 existing Phase 1–3 tests continue to pass with 0 regressions.
7. `python manage.py check` reports 0 issues.

---

## 8. Rollback & Data Safety Plan

- Phase 4 introduces only new tables (`food_foodlisting`, `food_foodsafetyassessment`).
- No modifications will be made to `CustomUser`, `OrganizationProfile`, `OrganizationDocument`, or `OrganizationVerificationEvent`.
- If rollback is needed:
  ```powershell
  python manage.py migrate food zero
  ```
  The database will cleanly revert to Phase 3 without affecting existing user or organization verification data.
