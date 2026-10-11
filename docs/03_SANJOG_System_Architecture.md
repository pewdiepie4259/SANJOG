# SANJOG — System Design & Architecture Specification
## Technical Blueprint & Architectural Specification

---

### 1. ARCHITECTURE OVERVIEW
**SANJOG** is architected as an **Intelligent Food Rescue Operating System (Food Rescue OS)**. It uses a high-performance modular Django 5.x core, Django REST Framework (DRF) for headless APIs, PostgreSQL with PostGIS for spatial spatial indexing, Redis as an in-memory cache & Celery task broker, and HTMX with Leaflet.js for real-time frontend interactivity.

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
        C4[Food Safety SOP & SLA Engine]
        C5[Need-First Matching & Multi-Recipient Allocation Engine]
    end

    subgraph Asynchronous Task Processing & AI Engine
        D1[Redis Message Broker]
        D2[Celery Worker Cluster]
        D3[Celery Beat Scheduler]
        D4[Scikit-Learn ML Forecasting Engine]
    end

    subgraph Persistence Layer
        E1[(PostgreSQL 16 + PostGIS 3.4 DB)]
        E2[(Redis In-Memory Cache & OTP Store)]
    end

    subgraph External Services
        F1[OpenStreetMap / Tile Server]
        F2[SMTP Email Gateway]
    end

    A1 -->|HTTPS| B1
    A2 -->|HTTPS| B1
    B1 --> C1
    B1 --> C2
    C1 --> C3
    C2 --> C3
    C3 --> C4
    C4 --> C5
    C5 -->|ORM Spatial Queries| E1
    C5 -->|Cache / Sessions / OTP| E2
    C5 -->|Task Dispatch| D1
    D1 --> D2
    D3 -->|Periodic SLA & Expiry Check| D1
    D2 -->|Async DB Updates| E1
    D2 -->|PDF / Email Generation| F2
    C5 -->|Inference Query| D4
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
            M2[Auth & RBAC Middleware]
        end
        
        subgraph Organizations App
            M3[OrganizationProfile]
            M4[Verification Queue]
        end
        
        subgraph Food App
            M5[FoodListing Model]
            M6[FoodSafetyAssessment SOP]
            M7[FoodPassport Ledger Engine]
        end

        subgraph Demand App
            M8[DemandRequest Model]
        end
        
        subgraph Rescue App
            M9[Deterministic Matching Engine]
            M10[Multi-Recipient RescueAllocation]
        end

        subgraph Pickups App
            M11[PickupRequest & Delivery Models]
            M12[Dual OTP Verification Engine]
        end

        subgraph Analytics & Certs
            M13[ImpactLedger Engine]
            M14[WeasyPrint PDF Renderer]
        end

        subgraph ML Engine
            M15[Demand & Surplus Forecaster]
        end
    end

    M1 --> M3
    M3 --> M5
    M3 --> M8
    M5 --> M6
    M5 --> M7
    M5 & M8 --> M9
    M9 --> M10
    M10 --> M11
    M11 --> M12
    M11 --> M13
    M13 --> M14
    M8 & M5 --> M15
```

---

### 4. END-TO-END FOOD RESCUE FLOW (MERMAID)

```mermaid
sequenceDiagram
    autonumber
    actor Donor
    participant System as Django Backend
    actor Receiver
    actor Volunteer

    Donor->>System: Submit Food Listing + Safety SOP Details
    System->>System: Execute Safety SOP Check (Status: ELIGIBLE)
    System->>System: Initialize FoodPassport & Start Spoilage Clock
    System->>System: Execute Need-First Matching Algorithm
    System->>Receiver: Proactive Allocation Alert (Multi-Recipient Split)
    Receiver->>System: Confirm Allocation (Servings Reserved)
    System->>System: Lock Servings via select_for_update()
    System->>Volunteer: Broadcast Pickup Task (Urgency: NORMAL/URGENT)
    Volunteer->>System: Accept Pickup Task
    Volunteer->>Donor: Arrive at Donor Location
    Donor->>System: Generate 4-Digit Pickup OTP
    Volunteer->>System: Enter Pickup OTP
    System->>System: Update Status = PICKED_UP & Log to FoodPassport
    Volunteer->>Receiver: Transport & Arrive at Receiver
    Receiver->>System: Generate 4-Digit Delivery OTP
    Volunteer->>System: Enter Delivery OTP
    System->>System: Update Status = DELIVERED & Log to FoodPassport
    System->>System: Update ImpactLedger & Generate WeasyPrint PDF Certificate
```

---

### 5. MULTI-RECIPIENT ALLOCATION FLOW (MERMAID)

```mermaid
graph TD
    A[Donor Posts 500 Meals] --> B[Safety Assessment: ELIGIBLE]
    B --> C[Matching Engine Scans Active DemandRequests]
    C --> D[Selects Top Matched Receivers]
    D --> E[Allocation 1: NGO A - 200 Meals]
    D --> F[Allocation 2: Shelter B - 150 Meals]
    D --> G[Allocation 3: Kitchen C - 150 Meals]
    E --> H[Atomic select_for_update Lock]
    F --> H
    G --> H
    H --> I[3 Independent PickupRequests & Volunteer Routes Generated]
```

---

### 6. FOOD PASSPORT LEDGER FLOW (MERMAID)

```mermaid
graph LR
    A[Surplus Listed] -->|Event 1: CREATED| P[(FoodPassport Log)]
    B[Safety Evaluated] -->|Event 2: SAFETY_PASSED| P
    C[Allocations Confirmed] -->|Event 3: ALLOCATED| P
    D[Donor OTP Verified] -->|Event 4: PICKED_UP| P
    E[Receiver OTP Verified] -->|Event 5: DELIVERED| P
    P --> F[Generate SHA-256 State Hash]
    F --> G[Render Final Audit Receipt]
```

---

### 7. REST API ENDPOINT BLUEPRINT

#### 7.1 Demand & Matching Endpoints
| HTTP Method | Endpoint URL | Auth | Role | Request Body | Success Response | Validation Rules | Error Codes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **POST** | `/api/v1/demand/` | JWT | Verified Receiver | `{servings, food_type, required_by, lat, lon}` | `201 Created` Demand object | Servings > 0, required_by in future | `400` Validation Err |
| **GET** | `/api/v1/demand/active/` | JWT | Admin/System | Query params: `lat`, `lon`, `radius_km` | `200 OK` List of active demands | PostGIS spatial radius lookup | `400` Bad Request |
| **POST** | `/api/v1/rescue/match/` | JWT | System/Admin | `{food_listing_id}` | `200 OK` Ranked matched demand list | Listing must be AVAILABLE | `404` Not Found |
| **POST** | `/api/v1/rescue/allocations/` | JWT | Receiver/System | `{food_listing_id, demand_request_id, servings}` | `201 Created` Allocation object | Atomic reservation check | `409` Conflict |

#### 7.2 Food & Food Passport Endpoints
| HTTP Method | Endpoint URL | Auth | Role | Request Body | Success Response | Validation Rules | Error Codes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **POST** | `/api/v1/food/` | JWT | Verified Donor | `{title, servings, cooked_at, expires_at, safety_sop}` | `201 Created` Listing + Safety result | Safety SOP complete | `400` Safety Failed |
| **GET** | `/api/v1/food/<id>/passport/` | JWT | Any | None | `200 OK` Complete Passport JSON + Hash | Valid listing ID | `404` Not Found |

#### 7.3 Logistics, OTP & Impact Endpoints
| HTTP Method | Endpoint URL | Auth | Role | Request Body | Success Response | Validation Rules | Error Codes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **POST** | `/api/v1/pickups/<id>/verify-pickup/` | JWT | Volunteer/Donor | `{otp_code: "1234"}` | `200 OK` Status = PICKED_UP | Max 3 attempts, unexpired | `422` Invalid OTP |
| **POST** | `/api/v1/pickups/<id>/verify-delivery/` | JWT | Volunteer/Receiver | `{otp_code: "5678"}` | `200 OK` Status = DELIVERED | Max 3 attempts, unexpired | `422` Invalid OTP |
| **GET** | `/api/v1/analytics/ledger/` | None/JWT | Any | None | `200 OK` Authoritative Impact JSON | Public feed | `200` OK |

---

### 8. DEPLOYMENT ARCHITECTURE (MERMAID)

```mermaid
graph TD
    subgraph Internet Edge
        DNS[Cloudflare / Route 53]
    end

    subgraph Application Server (VPS / Render / Railway)
        Nginx[Nginx Reverse Proxy & SSL Termination]
        Gunicorn[Gunicorn WSGI Server - 4 Workers]
        CeleryWorker[Celery Worker Cluster]
        CeleryBeat[Celery Beat Scheduler]
    end

    subgraph Database Layer
        Postgres[(PostgreSQL 16 + PostGIS 3.4 DB)]
        RedisCache[(Redis 7.x Cache & Broker)]
    end

    DNS --> Nginx
    Nginx --> Gunicorn
    Gunicorn --> Postgres
    Gunicorn --> RedisCache
    Gunicorn --> CeleryWorker
    CeleryBeat --> RedisCache
    CeleryWorker --> RedisCache
    CeleryWorker --> Postgres
```
