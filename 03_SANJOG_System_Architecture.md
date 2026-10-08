# SANJOG — System Design & Architecture Specification
## Technical Blueprint & Architectural Specification

---

### 1. ARCHITECTURE OVERVIEW
**SANJOG** is built as a high-performance, modular, multi-tenant monolithic architecture with API-first extensibility. It utilizes Django 5.x as the core web frame, Django REST Framework (DRF) for headless API integrations, PostgreSQL with PostGIS for spatial data indexing, Redis as an in-memory cache & Celery broker, and HTMX with Leaflet.js for interactive frontend rendering.

---

### 2. HIGH-LEVEL ARCHITECTURE (MERMAID)

```mermaid
graph TD
    subgraph Client Layer
        A1[Desktop Web Browser - Donor / Receiver / Admin]
        A2[Mobile Web / PWA - Volunteer / Ground Staff]
    end

    subgraph Presentation & Routing Layer
        B1[Nginx Web Server / Reverse Proxy]
        B2[Django Static & Media File Storage]
    end

    subgraph Core Application Layer - Django WSGI / ASGI
        C1[Django Core App - HTMX Views & Templates]
        C2[DRF API Engine - REST Endpoints]
        C3[RBAC & Auth Middleware]
        C4[State Machine & Spoilage Engine]
    end

    subgraph Asynchronous Task Processing
        D1[Redis Message Broker]
        D2[Celery Worker Cluster]
        D3[Celery Beat Scheduler]
    end

    subgraph Persistence Layer
        E1[(PostgreSQL + PostGIS Database)]
        E2[(Redis In-Memory Cache & OTP Store)]
    end

    subgraph External Services
        F1[OpenStreetMap / Tile Server]
        F2[SMTP Email Gateway]
    end

    A1 -->|HTTPS / WSS| B1
    A2 -->|HTTPS / WSS| B1
    B1 --> C1
    B1 --> C2
    C1 --> C3
    C2 --> C3
    C3 --> C4
    C4 -->|ORM Spatial Queries| E1
    C4 -->|Cache / Sessions| E2
    C4 -->|Task Dispatch| D1
    D1 --> D2
    D3 -->|Scheduled Expiry Check| D1
    D2 -->|Async DB Update| E1
    D2 -->|PDF / Email Generation| F2
    A1 -->|Leaflet Tiles| F1
    A2 -->|Leaflet Tiles| F1
```

---

### 3. COMPONENT DIAGRAM (MERMAID)

```mermaid
graph TB
    subgraph Django App Modules
        subgraph Accounts App
            M1[CustomUser Model]
            M2[Authentication Views]
        end
        
        subgraph Organizations App
            M3[OrganizationProfile]
            M4[Verification Service]
        end
        
        subgraph Food App
            M5[FoodListing Model]
            M6[Spoilage Countdown Manager]
        end
        
        subgraph Claims App
            M7[Claim Model]
            M8[Locking & Allocation Service]
        end

        subgraph Pickups App
            M9[PickupRequest & Delivery Models]
            M10[OTP Verification Engine]
        end

        subgraph Notifications App
            M11[Notification Manager]
            M12[Email Service]
        end

        subgraph Certificates App
            M13[WeasyPrint PDF Renderer]
        end
        
        subgraph Analytics App
            M14[Impact Metrics Engine]
        end
    end

    M1 --> M3
    M3 --> M5
    M5 --> M7
    M7 --> M9
    M9 --> M10
    M5 --> M6
    M9 --> M11
    M9 --> M13
    M5 --> M14
```

---

### 4. USER ROLE DIAGRAM (MERMAID)

```mermaid
graph LR
    subgraph Roles & Permissions
        U[User] -->|Inherits| R1[DONOR]
        U -->|Inherits| R2[RECEIVER]
        U -->|Inherits| R3[VOLUNTEER]
        U -->|Inherits| R4[ADMIN]

        R1 -->|Permissions| P1[Create Listing / View Pickup OTP / Download Certificates]
        R2 -->|Permissions| P2[Discover Food / Claim Listing / Provide Delivery OTP]
        R3 -->|Permissions| P3[Accept Delivery Task / Validate Pickup OTP / Validate Delivery OTP]
        R4 -->|Permissions| P4[Approve Documents / Manage Users / Override States / View Audit Logs]
    end
```

---

### 5. FOOD DONATION FLOW (MERMAID)

```mermaid
sequenceDiagram
    autonumber
    actor Donor
    participant System as Django Backend
    participant DB as PostGIS DB
    participant Broker as Redis / Celery

    Donor->>System: Submit Food Listing + Safety Checklist
    System->>System: Validate Expiry > Current Time
    System->>DB: Save FoodListing (status = AVAILABLE)
    System->>Broker: Schedule Expiry Monitor Task (Celery)
    System-->>Donor: Confirmation + Live Spoilage Countdown Started
```

---

### 6. CLAIM FLOW (MERMAID)

```mermaid
sequenceDiagram
    autonumber
    actor Receiver
    participant System as Django Backend
    participant DB as PostGIS DB
    actor Volunteer

    Receiver->>System: Claim Food Listing (ID)
    System->>DB: Transaction Begin (select_for_update)
    alt Listing is AVAILABLE
        System->>DB: Update FoodListing status = CLAIMED
        System->>DB: Create Claim Record + PickupRequest
        System->>DB: Transaction Commit
        System-->>Receiver: Claim Confirmed (30-min Volunteer Window Started)
        System->>Volunteer: Broadcast Nearby Pickup Request Alert
    else Listing is Already CLAIMED or EXPIRED
        System->>DB: Transaction Rollback
        System-->>Receiver: Error 409: Listing No Longer Available
    end
```

---

### 7. PICKUP & DELIVERY FLOW (MERMAID)

```mermaid
sequenceDiagram
    autonumber
    actor Donor
    actor Volunteer
    actor Receiver
    participant System as Django Backend
    participant DB as PostGIS DB

    Volunteer->>System: Accept Delivery Task
    System->>DB: Update Status = PICKUP_ASSIGNED
    Volunteer->>Donor: Arrive at Donor Location
    Donor->>System: Generate Pickup OTP (Displays to Donor)
    Volunteer->>System: Input Pickup OTP on Mobile
    System->>System: Verify OTP Match & Expiry
    System->>DB: Update Status = PICKED_UP
    
    Volunteer->>Receiver: Transport & Arrive at Receiver Facility
    Receiver->>System: Generate Delivery OTP (Displays to Receiver)
    Volunteer->>System: Input Delivery OTP on Mobile
    System->>System: Verify OTP Match & Expiry
    System->>DB: Update Status = DELIVERED
    System->>DB: Trigger Impact Metrics Update & Certificate Generation
```

---

### 8. OTP FLOW (MERMAID)

```mermaid
graph TD
    A[Handoff Initiated] --> B{Step Type}
    B -->|Pickup| C[Generate 4-Digit Pickup OTP]
    B -->|Delivery| D[Generate 4-Digit Delivery OTP]
    C --> E[Store Salted Hash in Redis TTL=30m]
    D --> F[Store Salted Hash in Redis TTL=60m]
    E --> G[Display Plaintext to Verification Provider]
    F --> G
    G --> H[Delivery Person Enters OTP]
    H --> I{Attempts <= 3?}
    I -->|No| J[Lock OTP Verification for 15 mins + Flag Admin]
    I -->|Yes| K{Hash Matches Redis Store?}
    K -->|No| L[Increment Failed Attempts Counter]
    K -->|Yes| M[Mark Step Verified & Delete Redis Key]
```

---

### 9. NOTIFICATION FLOW (MERMAID)

```mermaid
graph LR
    A[State Machine Event] --> B{Notification Type}
    B -->|Urgent Expiry| C[Celery Task: Dispatch Urgent Email to Nearby Receivers]
    B -->|Claimed| D[Celery Task: Dispatch Claim Confirmation to Donor]
    B -->|Delivered| E[Celery Task: Dispatch Receipt & Certificate Link to All Parties]
    C --> F[In-App Notification Record Created]
    D --> F
    E --> F
```

---

### 10. DEPLOYMENT ARCHITECTURE (MERMAID)

```mermaid
graph TD
    subgraph Internet Edge
        DNS[Cloudflare / Route 53]
    end

    subgraph Application Server (VPS / Render / Railway)
        Nginx[Nginx Reverse Proxy & SSL Termination]
        Gunicorn[Gunicorn WSGI App Server - 4 Workers]
        CeleryWorker[Celery Task Worker Process]
        CeleryBeat[Celery Beat Scheduler Process]
    end

    subgraph Managed Database Services
        PostgresDB[(PostgreSQL 16 + PostGIS 3.4)]
        RedisCache[(Redis 7.x Cache & Broker)]
    end

    DNS --> Nginx
    Nginx --> Gunicorn
    Gunicorn --> PostgresDB
    Gunicorn --> RedisCache
    Gunicorn --> CeleryWorker
    CeleryBeat --> RedisCache
    CeleryWorker --> RedisCache
    CeleryWorker --> PostgresDB
```

---

### 11. DATA FLOW DIAGRAM (DFD LEVEL 1) (MERMAID)

```mermaid
graph TD
    P1[Donor] -->|1. Post Surplus Food + Checklist| D1[FoodListing Data Store]
    D1 -->|2. Geospatial Indexing| P2[Spatial Engine - PostGIS]
    P3[Receiver] -->|3. Discover & Claim| P2
    P2 -->|4. Lock Listing| D2[Claims Data Store]
    D2 -->|5. Create Task| D3[Pickup/Delivery Data Store]
    P4[Volunteer] -->|6. Accept Task & Input OTP| D3
    D3 -->|7. Verify OTP| P5[OTP Verification Engine]
    P5 -->|8. Handoff Success| D4[Impact & Audit Data Store]
```

---

### 12. REST API ARCHITECTURE & ENDPOINT BLUEPRINT

#### 12.1 Authentication Endpoints
| HTTP Method | Endpoint URL | Auth | Role | Request Body | Success Response | Validation Rules | Error Codes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **POST** | `/api/v1/auth/register/` | None | Any | `{username, email, password, role, phone}` | `201 Created` `{user_id, token}` | Email unique, password strong | `400` Bad Request |
| **POST** | `/api/v1/auth/login/` | None | Any | `{username, password}` | `200 OK` `{access, refresh, user}` | Credentials valid | `401` Unauthorized |
| **POST** | `/api/v1/auth/logout/` | JWT | Any | `{refresh_token}` | `205 Reset Content` | Token valid | `400` Bad Request |
| **GET** | `/api/v1/users/me/` | JWT | Any | None | `200 OK` User profile details | Must be logged in | `401` Unauthorized |

#### 12.2 Organization Endpoints
| HTTP Method | Endpoint URL | Auth | Role | Request Body | Success Response | Validation Rules | Error Codes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GET** | `/api/v1/organizations/` | JWT | Admin | None | `200 OK` List of orgs | Admin access | `403` Forbidden |
| **POST** | `/api/v1/organizations/` | JWT | Donor/Receiver | `{name, reg_number, address, lat, lon, docs}` | `201 Created` Org profile | Reg number unique, files valid | `400` Validation Err |
| **PATCH** | `/api/v1/organizations/<id>/verify/` | JWT | Admin | `{status: "VERIFIED"|"REJECTED", notes}` | `200 OK` Updated status | Status in enum | `403` Forbidden |

#### 12.3 Food Listing Endpoints
| HTTP Method | Endpoint URL | Auth | Role | Request Body | Success Response | Validation Rules | Error Codes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GET** | `/api/v1/food/` | None/JWT | Any | Query params: `radius`, `lat`, `lon` | `200 OK` GeoJSON/List | Radius 1..50km | `400` Bad Request |
| **POST** | `/api/v1/food/` | JWT | Verified Donor | `{title, servings, expiry_time, safety_checked: true}` | `201 Created` Food object | Safety checklist required | `403` Unverified |
| **GET** | `/api/v1/food/nearby/` | JWT | Receiver | Query params: `lat`, `lon`, `radius_km` | `200 OK` Filtered listings | PostGIS ST_DWithin query | `400` Invalid Coords |

#### 12.4 Claims & Pickup Endpoints
| HTTP Method | Endpoint URL | Auth | Role | Request Body | Success Response | Validation Rules | Error Codes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **POST** | `/api/v1/claims/` | JWT | Verified Receiver | `{food_listing_id, self_pickup: bool}` | `201 Created` Claim object | Listing status = AVAILABLE | `409` Already Claimed |
| **POST** | `/api/v1/pickups/<id>/verify-pickup/` | JWT | Volunteer/Donor | `{otp_code: "1234"}` | `200 OK` Status = PICKED_UP | Max 3 attempts, unexpired | `422` Invalid OTP |
| **POST** | `/api/v1/pickups/<id>/verify-delivery/` | JWT | Volunteer/Receiver | `{otp_code: "5678"}` | `200 OK` Status = DELIVERED | Max 3 attempts, unexpired | `422` Invalid OTP |

#### 12.5 Analytics & Certificates Endpoints
| HTTP Method | Endpoint URL | Auth | Role | Request Body | Success Response | Validation Rules | Error Codes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GET** | `/api/v1/analytics/impact/` | None/JWT | Any | None | `200 OK` Total meals, weight, deliveries | Public view | `200` OK |
| **GET** | `/api/v1/certificates/<id>/download/` | JWT | Donor/Admin | None | `200 OK` PDF File Stream | Certificate exists | `404` Not Found |

---

### 13. DATABASE ARCHITECTURE (POSTGIS SPECIFICATION)
- **Spatial Reference System:** WGS 84 (`EPSG:4326`).
- **Spatial Field Types:** `gis_models.PointField(srid=4326, geography=True)`.
- **Spatial Indexing:** GiST (Generalized Search Tree) indexes on location columns (`CREATE INDEX idx_food_location ON food_foodlisting USING GIST (location);`).

---

### 14. BACKGROUND PROCESSING ARCHITECTURE (CELERY & REDIS)
- **Worker Queues:**
  1. `default`: General asynchronous operations.
  2. `expiry_queue`: High-priority periodic food listing expiry monitoring.
  3. `notifications`: Email rendering and SMTP dispatch.
  4. `certificates`: PDF generation via WeasyPrint.
- **Beat Periodic Schedules:**
  - `check-food-expirations`: Runs every 60 seconds.
  - `clean-expired-otps`: Runs every 15 minutes.
  - `aggregate-daily-analytics`: Runs daily at 00:00 UTC.

---

### 15. AUTHENTICATION & AUTHORIZATION ARCHITECTURE
- Custom Django Permissions Classes:
  - `IsVerifiedDonor`: Checks `request.user.role == 'DONOR'` and `request.user.organization.verification_status == 'VERIFIED'`.
  - `IsVerifiedReceiver`: Checks `request.user.role == 'RECEIVER'` and `request.user.organization.verification_status == 'VERIFIED'`.
  - `IsVolunteer`: Checks `request.user.role == 'VOLUNTEER'`.
  - `IsAdminUser`: Checks `request.user.is_staff` or `request.user.role == 'ADMIN'`.

---

### 16. SECURITY ARCHITECTURE
- **CSRF:** Standard Django CSRF token enforcement for session frontend; JWT headers (`Authorization: Bearer <token>`) for API.
- **Data Protection:** Media root directory protected from direct script execution; user upload filenames randomized using UUIDs.
- **Audit Logging:** Database-driven `AuditLog` table capturing actor, action string, target model ID, timestamp, and IP address.

---

### 17. LOGGING & MONITORING
- Standard Python `logging` configuration writing to:
  - `logs/sanjog_info.log` (Info events, claims, deliveries)
  - `logs/sanjog_security.log` (Failed logins, document approvals, OTP failures)
  - `logs/sanjog_error.log` (Unhandled exceptions, 500 errors)
