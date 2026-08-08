# CommunityOS.ai - System Architecture

## High-Level Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        A[Mobile Browser] --> B[React PWA]
        C[Desktop Browser] --> B
        D[Tablet Browser] --> B
    end
    
    subgraph "CDN & Hosting - Vercel"
        B --> E[Vercel Edge Network]
        E --> F[Static Assets]
    end
    
    subgraph "Application Layer"
        E --> G[FastAPI Backend]
        G --> H[Authentication Service]
        G --> I[Issue Management Service]
        G --> J[Contractor Service]
        G --> K[Asset Management Service]
        G --> L[Report Generation Service]
        G --> M[Events & Polls Service]
        G --> N[Notification Service]
        G --> O2[Visitor & Water Tanker Service]
        G --> P2[Committee & Guidelines Service]
    end
    
    subgraph "Data Layer - Supabase"
        H --> O[(PostgreSQL Database)]
        I --> O
        J --> O
        K --> O
        L --> O
        M --> O
    end
    
    subgraph "Storage Layer"
        I --> P[AWS S3 Bucket]
        K --> P
        L --> P
        P --> Q[Images]
        P --> R[PDF Reports]
        P --> S[Documents]
    end
    
    subgraph "External Services"
        N --> T[Resend/Amazon SES]
        T --> U[Email Delivery]
        L --> V[PDF Generator]
    end
    
    subgraph "Security & Monitoring"
        G --> W[JWT Auth]
        G --> X[Rate Limiting]
        G --> Y[Logging & Monitoring]
    end

    style B fill:#61dafb
    style G fill:#009688
    style O fill:#3ecf8e
    style P fill:#ff9900
    style T fill:#0073e6
```

---

## Detailed Architecture Components

### 1. Frontend Architecture (React)

```mermaid
graph LR
    A[React App] --> B[Redux Store]
    A --> C[React Router]
    A --> D[Component Library]
    
    subgraph "Pages"
        E[Login Page]
        F[Dashboard]
        G[Issues Page]
        H[Reports Page]
    end
    
    subgraph "Components"
        I[Issue Form]
        J[Photo Upload]
        K[QR Scanner]
        L[Filter Panel]
    end
    
    B --> M[API Middleware]
    M --> N[FastAPI Backend]
    
    D --> E
    D --> F
    D --> G
    D --> H
    F --> I
    G --> J
    G --> K
    G --> L
```

**Frontend Structure:**
```
frontend/
├── public/
│   ├── index.html
│   └── manifest.json (PWA)
├── src/
│   ├── api/
│   │   ├── client.js
│   │   ├── issues.js
│   │   ├── auth.js
│   │   └── contractors.js
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Button.jsx
│   │   │   └── Card.jsx
│   │   ├── issues/
│   │   │   ├── IssueForm.jsx
│   │   │   ├── IssueCard.jsx
│   │   │   └── IssueList.jsx
│   │   ├── qrcode/
│   │   │   ├── QRScanner.jsx
│   │   │   └── QRGenerator.jsx
│   │   └── upload/
│   │       └── PhotoUpload.jsx
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Issues.jsx
│   │   ├── Reports.jsx
│   │   └── Profile.jsx
│   ├── store/
│   │   ├── index.js
│   │   ├── authSlice.js
│   │   ├── issuesSlice.js
│   │   └── contractorsSlice.js
│   ├── utils/
│   │   ├── constants.js
│   │   ├── validators.js
│   │   └── formatters.js
│   ├── App.jsx
│   └── main.jsx
├── package.json
└── vite.config.js
```

---

### 2. Backend Architecture (FastAPI)

```mermaid
graph TB
    A[FastAPI Application] --> B[API Router]
    B --> C[Auth Routes]
    B --> D[Issues Routes]
    B --> E[Contractors Routes]
    B --> F[Assets Routes]
    B --> G[Reports Routes]
    
    C --> H[Auth Controller]
    D --> I[Issues Controller]
    E --> J[Contractors Controller]
    F --> K[Assets Controller]
    G --> L[Reports Controller]
    
    H --> M[Auth Service]
    I --> N[Issues Service]
    J --> O[Contractors Service]
    K --> P[Assets Service]
    L --> Q[Reports Service]
    
    M --> R[(Database)]
    N --> R
    O --> R
    P --> R
    Q --> R
    
    N --> S[S3 Service]
    P --> S
    Q --> S
    
    Q --> T[PDF Service]
    N --> U[Email Service]
```

**Backend Structure:**
```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── issues.py
│   │   │   │   ├── contractors.py
│   │   │   │   ├── assets.py
│   │   │   │   ├── reports.py
│   │   │   │   └── qrcodes.py
│   │   │   └── api.py
│   │   └── deps.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── models/
│   │   ├── user.py
│   │   ├── issue.py
│   │   ├── contractor.py
│   │   ├── asset.py
│   │   └── qrcode.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── issue.py
│   │   ├── contractor.py
│   │   └── response.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── issue_service.py
│   │   ├── contractor_service.py
│   │   ├── asset_service.py
│   │   ├── s3_service.py
│   │   ├── email_service.py
│   │   ├── pdf_service.py
│   │   └── qrcode_service.py
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── init_db.py
│   └── main.py
├── alembic/
│   ├── versions/
│   └── env.py
├── tests/
│   ├── api/
│   ├── services/
│   └── conftest.py
├── requirements.txt
└── alembic.ini
```

---

### 3. Database Schema (PostgreSQL)

```mermaid
erDiagram
    USERS ||--o{ ISSUES : reports
    USERS ||--o{ CONTRACTORS : manages
    USERS ||--o{ MATERIAL_MOVEMENTS : approves
    ISSUES ||--o{ ISSUE_PHOTOS : contains
    ISSUES }o--|| CONTRACTORS : assigned_to
    ASSETS ||--o{ QR_CODES : has
    CONTRACTORS ||--o{ CONTRACTOR_RATINGS : receives
    ISSUES ||--|| QR_CODES : scanned_from
    
    USERS {
        uuid id PK
        string email
        string password_hash
        string name
        string phone
        enum role
        string unit_number
        timestamp created_at
        timestamp updated_at
    }
    
    ISSUES {
        uuid id PK
        string title
        text description
        enum category
        enum priority
        enum status
        string location
        string unit_number
        uuid reported_by FK
        uuid assigned_to FK
        timestamp created_at
        timestamp updated_at
        timestamp resolved_at
    }
    
    ISSUE_PHOTOS {
        uuid id PK
        uuid issue_id FK
        string photo_url
        timestamp uploaded_at
    }
    
    CONTRACTORS {
        uuid id PK
        string name
        string company
        string trade
        string phone
        string email
        float rating
        string documents_url
        timestamp created_at
    }
    
    ASSETS {
        uuid id PK
        string name
        string type
        string location
        enum condition
        date purchase_date
        date last_maintenance
        uuid qr_code_id FK
    }
    
    QR_CODES {
        uuid id PK
        string code
        enum entity_type
        uuid entity_id
        timestamp created_at
    }
    
    MATERIAL_MOVEMENTS {
        uuid id PK
        enum type
        text description
        integer quantity
        string vehicle_number
        uuid approved_by FK
        timestamp timestamp
    }
    
    CONTRACTOR_RATINGS {
        uuid id PK
        uuid contractor_id FK
        uuid rated_by FK
        integer rating
        text comment
        timestamp created_at
    }
```

---

### 4. API Architecture

**RESTful API Design:**

```
Base URL: https://api.riverdaleconnect.com/api/v1

Authentication: JWT Bearer Token
Header: Authorization: Bearer <token>
```

**Endpoint Groups:**

1. **Authentication** (`/auth`)
   - POST `/auth/register` - User registration
   - POST `/auth/login` - User login
   - POST `/auth/refresh` - Refresh token
   - GET `/auth/me` - Get current user
   - POST `/auth/logout` - Logout

2. **Issues** (`/issues`)
   - POST `/issues` - Create issue
   - GET `/issues` - List issues (paginated, filtered)
   - GET `/issues/{id}` - Get issue details
   - PUT `/issues/{id}` - Update issue
   - DELETE `/issues/{id}` - Delete issue
   - POST `/issues/{id}/photos` - Upload photos
   - PUT `/issues/{id}/assign` - Assign to contractor
   - PUT `/issues/{id}/status` - Update status

3. **Contractors** (`/contractors`)
   - POST `/contractors` - Register contractor
   - GET `/contractors` - List contractors
   - GET `/contractors/{id}` - Get contractor details
   - PUT `/contractors/{id}` - Update contractor
   - POST `/contractors/{id}/ratings` - Add rating

4. **Assets** (`/assets`)
   - POST `/assets` - Register asset
   - GET `/assets` - List assets
   - GET `/assets/{id}` - Get asset details
   - PUT `/assets/{id}` - Update asset
   - POST `/assets/{id}/maintenance` - Log maintenance

5. **Reports** (`/reports`)
   - GET `/reports/weekly` - Generate weekly report
   - GET `/reports/download/{id}` - Download report PDF
   - GET `/reports/analytics` - Get analytics data

6. **QR Codes** (`/qrcodes`)
   - POST `/qrcodes` - Generate QR code
   - GET `/qrcodes/{code}` - Get QR code details
   - GET `/qrcodes/{id}/image` - Get QR code image

---

### 5. Security Architecture

```mermaid
graph TB
    A[User Request] --> B{HTTPS}
    B --> C[Vercel Edge]
    C --> D[Rate Limiter]
    D --> E{Authenticated?}
    E -->|No| F[Return 401]
    E -->|Yes| G[Verify JWT]
    G --> H{Valid Token?}
    H -->|No| F
    H -->|Yes| I[Check RBAC Permissions]
    I --> J{Authorized?}
    J -->|No| K[Return 403]
    J -->|Yes| L[Process Request]
    L --> M[Sanitize Input]
    M --> N[Execute Business Logic]
    N --> O[Return Response]
```

**Security Measures:**

1. **Authentication:**
   - JWT with RS256 algorithm
   - Token expiry: 1 hour
   - Refresh token: 7 days
   - Secure password hashing (bcrypt, cost=12)

2. **Authorization:**
   - Role-based access control (RBAC)
   - Roles: resident, contractor, builder, admin, security, facility
   - Permission matrix per endpoint

3. **Data Security:**
   - All data encrypted in transit (TLS 1.3)
   - Sensitive data encrypted at rest
   - Input validation using Pydantic
   - SQL injection prevention (SQLAlchemy ORM)
   - XSS protection (Content Security Policy)

4. **API Security:**
   - Rate limiting (100 req/min per user)
   - CORS configuration
   - API key rotation
   - Request logging

---

### 6. Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        A[Local Dev] --> B[Git Push]
    end
    
    subgraph "CI/CD Pipeline - GitHub Actions"
        B --> C[Run Tests]
        C --> D[Build Docker Image]
        D --> E[Security Scan]
        E --> F{Tests Pass?}
        F -->|No| G[Notify Dev]
        F -->|Yes| H[Deploy to Staging]
    end
    
    subgraph "Staging Environment"
        H --> I[Vercel Staging]
        I --> J[Integration Tests]
        J --> K{Manual Approval}
    end
    
    subgraph "Production Environment"
        K -->|Approved| L[Vercel Production]
        L --> M[Health Check]
        M --> N{Healthy?}
        N -->|No| O[Rollback]
        N -->|Yes| P[Live]
    end
    
    O --> I
```

**Environment Configuration:**

| Environment | Frontend URL | Backend URL | Database |
|-------------|--------------|-------------|----------|
| Development | localhost:5173 | localhost:8000 | Local PostgreSQL |
| Staging | staging.riverdaleconnect.com | api-staging.riverdaleconnect.com | Supabase (staging) |
| Production | app.riverdaleconnect.com | api.riverdaleconnect.com | Supabase (production) |

---

### 7. Scalability & Performance

**Performance Targets:**
- API response time: <200ms (p95)
- Page load time: <2 seconds
- Time to Interactive: <3 seconds
- Lighthouse Score: >90

**Scalability Strategy:**

1. **Backend Scaling:**
   - Horizontal scaling via Vercel serverless functions
   - Connection pooling for database
   - Redis caching for frequent queries
   - Async task processing for reports

2. **Database Scaling:**
   - Read replicas for analytics
   - Indexing strategy on frequently queried fields
   - Partitioning for large tables (issues, photos)

3. **Storage Scaling:**
   - S3 lifecycle policies for archival
   - CloudFront CDN for image delivery
   - Image compression and optimization

4. **Frontend Optimization:**
   - Code splitting and lazy loading
   - Service worker for offline support
   - Image lazy loading
   - Bundle size optimization

---

### 8. Monitoring & Observability

```mermaid
graph LR
    A[Application] --> B[Logs]
    A --> C[Metrics]
    A --> D[Traces]
    
    B --> E[Vercel Logs]
    C --> F[Prometheus]
    D --> G[Sentry]
    
    E --> H[Monitoring Dashboard]
    F --> H
    G --> H
    
    H --> I[Alerts]
    I --> J[Email/Slack]
```

**Monitoring Tools:**
- **Logs**: Vercel Logs, CloudWatch
- **APM**: Sentry for error tracking
- **Uptime**: UptimeRobot
- **Analytics**: Google Analytics / Mixpanel

**Key Metrics:**
- Request rate, error rate, latency (RED method)
- CPU, memory, database connections
- Active users, session duration
- Issue creation rate, resolution time

---

### 9. Disaster Recovery & Backup

**Backup Strategy:**
1. **Database**: Daily automated backups (Supabase)
2. **Files**: S3 versioning enabled
3. **Configuration**: Infrastructure as Code (IaC)
4. **Recovery Time Objective (RTO)**: 4 hours
5. **Recovery Point Objective (RPO)**: 24 hours

**Disaster Recovery Plan:**
1. Automated daily backups to separate region
2. Point-in-time recovery capability
3. Documented restoration procedures
4. Quarterly disaster recovery drills

---

## Technology Justification

### Why React?
- Large ecosystem and community support
- Component reusability
- Excellent PWA support
- Easy mobile migration path

### Why FastAPI?
- High performance (async support)
- Automatic API documentation
- Type safety with Pydantic
- Modern Python features

### Why PostgreSQL/Supabase?
- ACID compliance for critical data
- Rich query capabilities
- Built-in authentication support
- Easy scaling options

### Why AWS S3?
- Cost-effective storage
- High durability (99.999999999%)
- Seamless scaling
- CDN integration

### Why Vercel?
- Optimized for React/Next.js
- Global edge network
- Automatic SSL
- Serverless function support
- Excellent developer experience

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Final
