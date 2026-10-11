# SANJOG — UI/UX Design Specification
## Intelligent Food Rescue Operating System (Food Rescue OS) Interface Blueprint

---

### 1. BRAND IDENTITY & DESIGN SYSTEM

#### 1.1 Visual Identity & Philosophy
**SANJOG** as a **Food Rescue Operating System** moves away from traditional, passive marketplace aesthetics. It presents a clean, operational, high-visibility interface optimized for rapid action, real-time tracking, and administrative clarity.

#### 1.2 Color Palette Tokens
| Token Name | Hex Code | Purpose / Usage |
| :--- | :--- | :--- |
| **`Primary-900`** | `#14532D` | Main navigation, operational headers |
| **`Primary-700`** | `#15803D` | Primary action buttons, `SAFE` status indicators |
| **`Primary-500`** | `#22C55E` | Highlights, success states, verified badges |
| **`Secondary-700`** | `#B45309` | SLA Warning headers, sub-navigation |
| **`Secondary-500`** | `#F59E0B` | `WARNING` status badges (1-2hr spoilage), caution alerts |
| **`Urgent-600`** | `#DC2626` | `URGENT` / `CRITICAL` SLA badges (<1hr), SLA breach alerts |
| **`Neutral-900`** | `#0F172A` | Primary typography text |
| **`Neutral-100`** | `#F8FAFC` | Application canvas background |
| **`Surface-White`**| `#FFFFFF` | Card backgrounds, modal surfaces |

#### 1.3 Typography & Components
- **Primary Font:** Inter / Outfit (Google Fonts).
- **Monospace Font:** JetBrains Mono (Used for Food Passport Hashes, OTP displays, SLA clocks).

---

### 2. CORE OPERATING DASHBOARDS & 42-PAGE MATRIX

#### DONOR OPERATING SCREENS (Pages 7–15)
- **Page 7: Donor Operating Dashboard:** Overview of active rescues, pending pickup OTPs, live Food Passports, quick "Report Surplus" action button.
- **Page 8: Report Surplus & Safety SOP Screen:** 2-column form. Left: Surplus details (servings, weight, cooked time, expiry). Right: Structured Food Safety SOP checklist & storage method input.
- **Page 9: My Surplus Listings:** Data table with filters for `ACTIVE`, `ALLOCATED`, `DELIVERED`, `EXPIRED`.
- **Page 10: Food Passport Detail View:** Full interactive view displaying the JSON lifecycle log, chain-of-custody timeline, and SHA-256 state hash.
- **Page 11: Multi-Recipient Allocations Overview:** View showing how a large surplus listing has been split across multiple receiver organizations.
- **Page 12: Pickup Tracking & OTP Display:** Real-time Leaflet map displaying incoming volunteer ETA + 4-digit Pickup OTP card.
- **Page 13: Donor Impact Dashboard:** Visual charts detailing total kg rescued, meals served, carbon offset, and monthly trends.
- **Page 14: CSR PDF Certificates:** Downloadable list of WeasyPrint PDF impact certificates with verification hashes.
- **Page 15: Donor Profile & FSSAI Settings:** Business profile management and legal document status.

#### RECEIVER OPERATING SCREENS (Pages 16–24)
- **Page 16: Receiver Operating Dashboard:** Quick "Log Meal Demand" action, active incoming rescue allocations, nearby surplus radar.
- **Page 17: Log Meal Demand Screen:** Form allowing receiver to specify servings needed, food category preference, required-by timestamp, and facility address.
- **Page 18: Interactive Map & Demand Discovery:** Full-screen Leaflet.js map showing both available surplus markers and active demand clusters.
- **Page 19: Food Listing & Safety Assessment View:** Detailed inspection of donor listing, preparation time, and safety SOP compliance status.
- **Page 20: Allocation Confirmation Modal:** Screen allowing receiver to confirm allocated servings and specify self-pickup vs volunteer transport.
- **Page 21: Active Rescue Allocations:** Real-time progress bar of matched rescues (`Matched` → `Pickup Assigned` → `In Transit` → `Arrived`).
- **Page 22: Delivery Tracking & Delivery OTP Screen:** Leaflet map with volunteer marker + 4-digit Delivery OTP display box.
- **Page 23: Received Rescue History:** Historical log of all successfully delivered food rescues with donor names and nutritional volume.
- **Page 24: Receiver Profile & 80G Settings:** NGO accreditation document management and shelter capacity parameters.

#### VOLUNTEER OPERATING SCREENS (Pages 25–32)
- **Page 25: Volunteer Operating Dashboard:** Real-time availability toggle (`AVAILABLE`/`UNAVAILABLE`), active task status, daily impact.
- **Page 26: Available Rescues Feed (SLA Sorted):** List of open rescue missions sorted by SLA Urgency (`CRITICAL` <30m at top with red pulsing badge, `URGENT` <60m, `NORMAL`).
- **Page 27: Rescue Task Details Screen:** Task dashboard showing pickup address, dropoff address, servings, distance (km), and route map link.
- **Page 28: Donor Pickup OTP Verification Screen:** Mobile PIN pad interface to input donor's 4-digit Pickup OTP.
- **Page 29: Receiver Delivery OTP Verification Screen:** Mobile PIN pad interface to input receiver's 4-digit Delivery OTP.
- **Page 30: Delivery History & Miles Logged:** Log of completed missions, total km traveled, and total meals delivered.
- **Page 31: Volunteer Impact & Badges:** Gamified milestone badges and community recognition level.
- **Page 32: Volunteer Profile Settings:** Vehicle type selection, ID proof document status, operational radius settings.

#### ADMIN COMMAND CENTER (Pages 33–42)
- **Page 33: Central Command Center Dashboard:** High-level operational map showing live rescues, SLA performance gauge, verification queue, system health.
- **Page 34: User & Role Governance:** User table with activation/suspension toggles and role permission edits.
- **Page 35: Organization Document Verification Queue:** Side-by-side document previewer (PDF/Image) with "Approve" and "Reject with Reason" actions.
- **Page 36: Live Operations & SLA Breach Monitor:** Real-time tracking of all active rescues with automated alerts for SLA breaches (<30m to expiry).
- **Page 37: Multi-Recipient Allocations Management:** Admin view of all active surplus allocations, enabling manual re-allocation if needed.
- **Page 38: Logistics & Volunteer Route Control:** Dispatch map showing active volunteer markers and route task assignments.
- **Page 39: Impact Ledger & Analytics Engine:** System-wide transactional metrics (meals rescued, kg diverted, CO2 offset) with CSV export.
- **Page 40: System Audit Logs:** Immutable table displaying event logs (`Actor`, `Action`, `Entity ID`, `IP Address`, `Timestamp`).
- **Page 41: System Reports Generator:** Custom report builder for institutional stakeholders.
- **Page 42: Platform System Settings:** Global configuration variables (SLA thresholds, default search radius, max OTP failure limits).

---

### 3. UI COMPONENTS SPECIFICATION

#### 3.1 Live Food Passport Timeline Component (HTMX Rendered)
```html
<div class="bg-white p-4 rounded-xl border border-gray-200 shadow-sm space-y-3">
    <div class="flex items-center justify-between border-b pb-2">
        <span class="text-xs font-mono text-gray-500">PASSPORT ID: {{ passport.passport_id }}</span>
        <span class="px-2 py-0.5 rounded text-xs font-semibold bg-green-100 text-green-800">VERIFIED CHAIN</span>
    </div>
    <div class="relative pl-6 border-l-2 border-green-500 space-y-4">
        {% for event in passport.custody_events %}
        <div class="relative">
            <div class="absolute -left-[31px] top-1.5 w-3 h-3 rounded-full bg-green-600 border-2 border-white"></div>
            <p class="text-xs font-semibold text-gray-900">{{ event.event_title }}</p>
            <p class="text-[11px] text-gray-500">{{ event.actor }} • {{ event.timestamp }}</p>
        </div>
        {% endfor %}
    </div>
    <div class="pt-2 border-t text-[10px] font-mono text-gray-400 truncate">
        HASH: {{ passport.passport_hash }}
    </div>
</div>
```

#### 3.2 SLA Urgency Badge Component
```html
<div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold
            {% if listing.sla_tier == 'NORMAL' %} bg-green-100 text-green-800 border border-green-300
            {% elif listing.sla_tier == 'URGENT' %} bg-amber-100 text-amber-800 border border-amber-300
            {% elif listing.sla_tier == 'CRITICAL' %} bg-red-100 text-red-800 border border-red-300 animate-pulse {% endif %}">
    <span>SLA: {{ listing.sla_tier }} ({{ listing.time_remaining_formatted }})</span>
</div>
```
