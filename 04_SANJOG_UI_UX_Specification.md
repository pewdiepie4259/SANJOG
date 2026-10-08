# SANJOG — UI/UX Design Specification
## Full-Stack Interface Blueprint & Design System

---

### 1. BRAND IDENTITY & VISUAL DESIGN SYSTEM

#### 1.1 Brand Essence & Design Philosophy
**SANJOG** represents the meaningful connection between excess food abundance and humanitarian need. The visual identity avoids generic or industrial looks, embodying warmth, trust, urgency, and ecological responsibility. 

#### 1.2 Color Palette Tokens
| Token Name | Hex Code | Purpose / Usage |
| :--- | :--- | :--- |
| **`Primary-900`** | `#14532D` | Main navigation headers, primary branding |
| **`Primary-700`** | `#15803D` | Primary action buttons, active links, safe statuses |
| **`Primary-500`** | `#22C55E` | Highlights, success states, safe indicators |
| **`Secondary-700`** | `#B45309` | Warning text, sub-headers |
| **`Secondary-500`** | `#F59E0B` | Secondary buttons, warning badges (1-2hr spoilage) |
| **`Urgent-600`** | `#DC2626` | Urgent countdown timers (<1hr), destructive alerts |
| **`Neutral-900`** | `#0F172A` | Primary typography text |
| **`Neutral-100`** | `#F8FAFC` | Main application canvas background |
| **`Surface-White`**| `#FFFFFF` | Card backgrounds, modal windows |

#### 1.3 Typography System
- **Primary Font:** Inter / Outfit (Google Fonts)
- **Heading Styles:** Semibold / Bold (`h1`: 32px, `h2`: 24px, `h3`: 20px)
- **Body Text:** Regular 15px / 1.6 line height for optimal legibility.
- **Monospace Font:** JetBrains Mono (Used for OTP displays, hash IDs, status codes).

---

### 2. PAGE SPECIFICATIONS (COMPLETE 42-PAGE MATRIX)

#### PUBLIC PAGES (1–6)

##### Page 1: Landing Page (Public Home)
- **Purpose:** Introduce SANJOG vision, real-time live impact metrics counter, and direct registration CTAs for Donors, Receivers, and Volunteers.
- **Layout:** Hero section with background hero illustration, 3-step explanation card grid, live impact counter banner, donor showcase carousel, call-to-action footer.
- **Components:** Primary Nav Header, Live Impact Counter (HTMX polling), Interactive Leaflet Preview Map (Public view without exact pin addresses), Role Selector Modal.
- **Buttons:** "Donate Food Now" (Primary Green), "Claim Food as NGO" (Secondary Orange), "Become a Volunteer" (Outline Dark).
- **Empty / Loading / Error States:** Skeleton loader on impact counter during initial fetch; fallback static metrics if API fails.
- **Responsive Behavior:** Navigation collapses to burger drawer on mobile; hero visual stacks vertically beneath text.

##### Page 2: About SANJOG
- **Purpose:** Detail the mission, founding vision, food waste statistics, legal disclaimer, and operational framework.
- **Layout:** Single column content layout with sidebar navigation to sub-sections.

##### Page 3: How It Works
- **Purpose:** Visual step-by-step breakdown of the 4 user roles (Donor, Receiver, Volunteer, Admin).
- **Layout:** 4-tab interactive panel switching user workflow diagrams.

##### Page 4: Contact & Support
- **Purpose:** Provide platform support, NGO query forms, and emergency platform contact options.
- **Forms:** Name, Email, Role dropdown, Subject, Message body. Client-side HTML5 validation.

##### Page 5: Login Page
- **Purpose:** Universal entry point for all platform user roles.
- **Layout:** Centered glassmorphism card over branded gradient background.
- **Forms:** Username/Email, Password, Remember Me toggle.
- **Validation:** Instant JS pattern validation; server error toast on invalid credentials.

##### Page 6: Registration Page (Role Selector & Profile Creation)
- **Purpose:** Onboard new users into Donor, Receiver, or Volunteer roles.
- **Layout:** Step 1: Role Selection Cards. Step 2: Account Details. Step 3: Organization Details & Document Upload.
- **Forms:** User credentials + Organization Title, Reg Number, Address, PostGIS Location Picker, Document PDF upload.

---

#### DONOR PAGES (7–15)

##### Page 7: Donor Dashboard
- **Purpose:** Overview of active listings, pending pickups, completed donations, and quick post food action.
- **Layout:** Top stat cards (Total Meals Saved, Active Listings, Pending Pickups) + Main Active Listings Grid + Recent Activity Timeline.
- **Components:** Spoilage Badge (`SAFE`/`WARNING`/`URGENT`), Pickup OTP Card, Quick Action Floating Button.

##### Page 8: Create Food Listing
- **Purpose:** Post new surplus food entry with mandatory safety compliance.
- **Layout:** 2-column form. Left: Food metadata. Right: Location & Mandatory Safety Checklist.
- **Forms:** Title, Category dropdown, Food Type (Veg/Non-Veg), Servings count, Quantity (kg), Cooked Time, Expiry Timestamp, Address, Map Pin adjustment, 5-point Safety Checkboxes.
- **Validation:** Expiry timestamp must be at least 1 hour into the future; all 5 safety checkboxes mandatory.

##### Page 9: My Donations (Listing Management)
- **Purpose:** Tabbed data table of all historical and current listings created by the donor.
- **Layout:** Tabs (`ALL`, `AVAILABLE`, `CLAIMED`, `DELIVERED`, `EXPIRED`). Search + Filter bar.

##### Page 10: Food Listing Detail View (Donor View)
- **Purpose:** Full inspect view of a specific listing, including claim status and assigned receiver/volunteer details.
- **Components:** Spoilage Countdown Timer, Assigned Receiver Card, Assigned Volunteer Card, Pickup OTP Display Box.

##### Page 11: Claims Overview (Donor View)
- **Purpose:** Display active claims waiting for donor handoff.

##### Page 12: Pickup Tracking (Donor View)
- **Purpose:** Real-time map displaying volunteer en-route to donor location.
- **Components:** Leaflet map with volunteer marker update via HTMX poll, Pickup OTP validator button.

##### Page 13: Donor Impact Dashboard
- **Purpose:** Advanced metrics detailing total food weight donated, total meals served, carbon emission reduction, and monthly graphs.

##### Page 14: CSR / Donation Certificates
- **Purpose:** List of downloadable PDF impact certificates for completed donations.
- **Buttons:** "Download PDF Certificate" (Triggers backend WeasyPrint file stream).

##### Page 15: Donor Profile & Document Settings
- **Purpose:** Manage business details, update FSSAI license documents, change password.

---

#### RECEIVER PAGES (16–24)

##### Page 16: Receiver Dashboard
- **Purpose:** High-level overview of nearby available food, active claims, and incoming deliveries.
- **Components:** Nearby Food Radar (Listings within selected radius), Quick Claim Card, Active Delivery Status Bar.

##### Page 17: Nearby Donations (Grid & List View)
- **Purpose:** Browse available food with sorting by distance, quantity, and time remaining.
- **Filters:** Radius (2km, 5km, 10km, 15km), Food Type (Veg/Non-Veg), Expiry Urgency.

##### Page 18: Interactive Map Discovery View
- **Purpose:** Full-screen Leaflet.js GIS map displaying available donations as urgency-colored markers.
- **Interactions:** Clicking a map pin opens a drawer with food summary, servings, countdown, and "Claim Now" button.

##### Page 19: Food Details & Safety Checklist View (Receiver View)
- **Purpose:** Inspect detailed food listing, donor profile, cooked timestamp, and donor hygiene declaration prior to claiming.

##### Page 20: Claim Confirmation Modal / Screen
- **Purpose:** Final step to lock food claim.
- **Forms:** Radio selector: `Self-Pickup` vs `Request Volunteer Transport`. Optional delivery notes.

##### Page 21: Receiver Active Claims Page
- **Purpose:** Monitor state of claimed listings (Awaiting Volunteer → Pickup Assigned → In Transit → Arrived).

##### Page 22: Delivery Tracking View (Receiver View)
- **Purpose:** Track incoming volunteer/food on Leaflet map + Display Delivery OTP card.
- **Components:** 4-Digit Delivery OTP Display (Provided to volunteer upon food arrival).

##### Page 23: Received Food History
- **Purpose:** Historical log of all successfully received donations with donor names and quantities.

##### Page 24: Receiver Profile & Document Management
- **Purpose:** Update NGO registration details, 80G/12A certificates, and shelter capacity metrics.

---

#### VOLUNTEER PAGES (25–32)

##### Page 25: Volunteer Dashboard
- **Purpose:** Mobile-optimized view displaying availability toggle, current assigned delivery, and volunteer impact stats.

##### Page 26: Available Deliveries Feed
- **Purpose:** List of unassigned pickup requests requiring volunteer transport.
- **Cards:** Display Pickup Address, Dropoff Address, Total Distance (km), Food Volume (kg), Servings.
- **Buttons:** "Accept Delivery Task" (Primary Green).

##### Page 27: Delivery Task Details Screen
- **Purpose:** Complete task dashboard for an accepted delivery.
- **Components:** Stepper UI (`Accept` → `Go to Donor` → `Verify Pickup OTP` → `Go to Receiver` → `Verify Delivery OTP`).

##### Page 28: Pickup Verification Screen (Volunteer View)
- **Purpose:** Screen presented at donor location to input donor's 4-digit Pickup OTP.
- **Forms:** 4-digit PIN input box with auto-focus.
- **Validation:** Limits to 3 attempts. Upon success, updates state to `PICKED_UP`.

##### Page 29: Delivery Verification Screen (Volunteer View)
- **Purpose:** Screen presented at receiver location to input receiver's 4-digit Delivery OTP.
- **Forms:** 4-digit PIN input box.
- **Validation:** Limits to 3 attempts. Upon success, updates state to `DELIVERED` and unlocks volunteer points.

##### Page 30: Delivery History (Volunteer View)
- **Purpose:** History of all completed rescue missions with total kilometers traveled and total meals delivered.

##### Page 31: Volunteer Impact & Badges
- **Purpose:** Gamified view displaying volunteer level, completed missions, and community recognition badges.

##### Page 32: Volunteer Profile Settings
- **Purpose:** Update vehicle type (Bike/Car/Van), government ID proof, and preferred operational zones.

---

#### ADMIN PAGES (33–42)

##### Page 33: Central Admin Dashboard
- **Purpose:** Executive overview of total users, active listings, pending organization verifications, delivery success rates, and system health.

##### Page 34: User Management Table
- **Purpose:** Filterable, searchable table of all registered users across all 4 roles. Ability to suspend/activate accounts.

##### Page 35: Organization Verification Queue
- **Purpose:** Dedicated queue for reviewing submitted FSSAI/NGO documents.
- **Components:** Side-by-side document preview (PDF/Image viewer) + "Approve" and "Reject with Notes" buttons.

##### Page 36: Food Listing Management
- **Purpose:** Admin view of all active, claimed, delivered, and expired listings across the platform. Ability to force-cancel suspicious listings.

##### Page 37: Claims Management
- **Purpose:** Monitor active claims and resolve stuck claims.

##### Page 38: Delivery Monitoring & Logistics
- **Purpose:** Live map tracking of all active in-transit volunteer deliveries.

##### Page 39: Analytics & Reporting Engine
- **Purpose:** Aggregate charts (Chart.js / Tailwind cards) showing weekly food rescue volume, top donor rankings, and regional impact.

##### Page 40: System Reports Export
- **Purpose:** Generate and export CSV/PDF reports for government compliance or platform performance evaluation.

##### Page 41: Audit Logs View
- **Purpose:** Immutable table displaying system events (`Actor`, `Role`, `Action`, `Entity ID`, `IP Address`, `Timestamp`).

##### Page 42: Platform System Settings
- **Purpose:** Configure global variables (default radius limit, maximum OTP failure limit, spoilage threshold hours, email template triggers).

---

### 3. COMMON INTERFACE COMPONENTS SPECIFICATION

#### 3.1 Live Spoilage Countdown Badge Component
```html
<!-- Example HTMX-driven Live Spoilage Badge -->
<div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold
            {% if listing.spoilage_status == 'SAFE' %} bg-green-100 text-green-800 border border-green-300
            {% elif listing.spoilage_status == 'WARNING' %} bg-amber-100 text-amber-800 border border-amber-300
            {% elif listing.spoilage_status == 'URGENT' %} bg-red-100 text-red-800 border border-red-300 font-bold animate-pulse
            {% else %} bg-gray-100 text-gray-800 border border-gray-300 {% endif %}">
    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
    <span>Expires in: {{ listing.time_remaining_formatted }}</span>
</div>
```

#### 3.2 Leaflet.js Custom Urgency Marker Config
```javascript
// Custom Leaflet Pin Icons by Urgency Status
const markerIcons = {
    SAFE: L.icon({ iconUrl: '/static/img/markers/pin-green.svg', iconSize: [32, 42] }),
    WARNING: L.icon({ iconUrl: '/static/img/markers/pin-amber.svg', iconSize: [32, 42] }),
    URGENT: L.icon({ iconUrl: '/static/img/markers/pin-red.svg', iconSize: [36, 46], className: 'pulse-marker' })
};
```
