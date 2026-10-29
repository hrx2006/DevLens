# DevLens AI — Intelligent Website Audit & Quality Assurance Platform

DevLens AI is a comprehensive, production-grade **Website Audit and Quality Assurance Platform** designed for modern web developers, QA engineers, and compliance assessors. It evaluates website health across five active categories: **Search Engine Optimization (SEO)**, **Accessibility (WCAG 2.2 heuristics)**, **Performance**, **Passive Security Posture**, and **Structural Functionality**.

The platform is designed with a strict **evidence-first architecture**: deterministic technical scanners collect observable DOM and HTTP network evidence from live target websites. The normalized findings are then enriched by an **AI Reasoning Layer (Google Gemini 2.5 Flash)** or its built-in **Deterministic Fallback Engine** to deliver actionable root-cause diagnoses, user-impact assessments, and developer remediation steps.

---

## 1. Executive Summary & Problem Statement

### Problem Statement
Modern web applications must meet stringent standards for search visibility, accessibility compliance, performance, security header hygiene, and functional link/form integrity. However:
1. Traditional audit tools often produce raw, cryptic errors without contextual guidance or prioritization.
2. Naive AI-powered auditing tools frequently "hallucinate" technical defects without verifying underlying HTML markup or HTTP headers.
3. Untrusted user-supplied URLs pose severe infrastructure risks (Server-Side Request Forgery, SSRF) to audit infrastructure.
4. Developers and evaluators lack unified, isolated reporting platforms that bridge technical findings with executive summaries and branded PDF exports.

### DevLens AI Solution
DevLens AI solves these challenges through:
- **Zero-Hallucination AI Architecture**: The AI Reasoning Layer is strictly constrained to interpret scanner-verified evidence. It does not invent phantom issues.
- **Dual-Engine AI Reliability**: Integrates Google Gemini 2.5 Flash with an automatic deterministic fallback engine. An API key is never required for core auditing, reporting, or health scoring.
- **Multi-Layer SSRF Defense**: Rigorous pre-connection URL validation, private RFC1918 and loopback address blocking, cloud metadata rejection, and re-validation on every redirect hop.
- **Strict Data Isolation**: Enterprise-grade Argon2id password hashing, HttpOnly session cookies, and database ownership checks that prevent cross-user data leakage.
- **Five-Category Transparent Scoring**: Fully auditable, predictable 0–100 health scoring and priority calculations.

---

## 2. System Architecture & Flow

```text
                               Target Website URL
                                       │
                                       ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                        Multi-Layer SSRF Defense                        │
  │  • Scheme Validation (HTTP/HTTPS only)                                 │
  │  • Port Range Validation (1–65535)                                     │
  │  • Prohibited Hostname & Cloud Metadata Defense (169.254.169.254)      │
  │  • RFC1918 Private & Loopback IP Blocking (IPv4 & IPv6)                │
  │  • DNS Pre-Resolution & Re-validation on Every Redirect Hop            │
  └───────────────────────────────────┬────────────────────────────────────┘
                                       │ Safe Target
                                       ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                           Safe Web Crawler                             │
  │  • Streaming Response Size Capping (5MB limit)                         │
  │  • Bounded Redirect Limit (max 5 hops) with Loop Detection             │
  │  • Connection and Read Timeout Protection (20s)                        │
  └───────────────────────────────────┬────────────────────────────────────┘
                                       │ DOM & Response Headers
                                       ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                   5 Active Deterministic Scanners                      │
  │  ┌──────────────┬──────────────┬──────────────┬──────────────┬──────┐  │
  │  │     SEO      │Accessibility │ Performance  │   Security   │ Func │  │
  │  └──────────────┴──────────────┴──────────────┴──────────────┴──────┘  │
  └───────────────────────────────────┬────────────────────────────────────┘
                                       │ Normalized Findings with Evidence
                                       ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                         AI Reasoning Layer                             │
  │  • Evidence Normalization & Input Validation                           │
  │  • Google Gemini 2.5 Flash Analysis (Structured JSON Schema)           │
  │  • Automatic Deterministic Fallback Engine (No API Key Required)       │
  │  • Engine Attribution Tagging (Gemini vs. Fallback)                    │
  └───────────────────────────────────┬────────────────────────────────────┘
                                       │ Enriched Insights
                                       ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                     Priority & Health Score Engine                     │
  │  • Category Weights: Security (1.05), SEO (0.95), Func/Acc/Perf (1.0)  │
  │  • Priority Mapping (0–100) based on Severity & Category               │
  │  • Transparent 5-Category Arithmetic Health Score (0–100)              │
  └───────────────────────────────────┬────────────────────────────────────┘
                                       │
                         ┌─────────────┴─────────────┐
                         ▼                           ▼
            SQLite Database Persistence      React 18 Dashboard &
            (Strict User ID Isolation)       ReportLab PDF Export
```

---

## 3. Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Data Validation & Schemas**: Pydantic v2
- **Database & ORM**: SQLite (Default) with SQLAlchemy 2.0 (Foreign key pragma enforcement)
- **Security & Cryptography**: `argon2-cffi` (Argon2id password hashing), `PyJWT` (JWT session tokens), HttpOnly SameSite=Lax cookies
- **Crawling & HTML Parsing**: `httpx` (async HTTP client with streaming), `BeautifulSoup4`, `lxml`
- **PDF Report Generation**: `ReportLab 4.x`, `Pillow`
- **AI Integration**: Google Gemini 2.5 Flash via REST Interactions API with automatic deterministic fallback
- **Test Framework**: `pytest`, `pytest-asyncio`

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Component Icons**: `lucide-react`
- **Charting & Gauges**: Custom responsive SVG health score gauges and metric cards

---

## 4. Completed Feature Matrix

| Feature / Module | Status | Description |
| :--- | :---: | :--- |
| **User Registration** | Verified | Argon2id hashing, email normalization, password length & complexity validation |
| **Authentication & Sessions** | Verified | Timing-safe login, HttpOnly SameSite cookies, JWT bearer support, and strict Login-First route guard |
| **User Data Isolation** | Verified | Backend ownership verification on all audits, rerun, deletion, and PDF export (returns 404 for foreign IDs) |
| **User Profile Management** | Verified | Profile inspection, authenticated password-change workflow |
| **SSRF Hardening** | Verified | IPv4/IPv6 private IP blocking, cloud metadata rejection, port validation, redirect revalidation & loop detection |
| **SEO Scanner** | Verified | Title presence/length, meta description, heading hierarchy skips, canonical URL checks, robots directives |
| **Accessibility Scanner** | Verified | WCAG 2.2 image alts, decorative image handling, form control labels, page language, button & link names |
| **Performance Scanner** | Verified | TTFB/latency measurement, HTML payload size, render-blocking scripts, asset counts, native lazy-loading |
| **Security Scanner** | Verified | Passive HTTPS check, HSTS, CSP, nosniff, Clickjacking (X-Frame / frame-ancestors), mixed-content, cookie flags |
| **Functionality Scanner** | Verified | Dead anchor targets (`#`, `javascript:void(0)`), malformed links, form action/method hygiene, password-over-GET detection |
| **AI Reasoning Layer** | Verified | Gemini 2.5 Flash with structured schema validation + zero-credential deterministic fallback engine |
| **Scoring & Priority Engine** | Verified | Deterministic priority calculation (0–100) and transparent 5-category health scoring (0–100) |
| **PDF Report Generation** | Verified | Branded ReportLab PDF generation with XML escaping, AI root causes, recommendations, and disclaimers |
| **Interactive Dashboard** | Verified | Login-First authentication gating, 7 responsive views/screens, real-time sequential progress tracker, category filters, and history search |
| **Demo Target Suite** | Verified | Built-in safe demo website with intentional test issues across all 5 scanner categories |
| **Automated Test Suite** | Verified | **47 passing Pytest tests** covering auth, endpoint protection, isolation, SSRF, scanners, scoring, PDF, and 5 integration workflows |

---

## 5. Active Auditing Categories & Checks

### A. SEO Scanner (`SEOScanner`)
1. **Page Title Tag**: Checks for absence of `<title>`, short titles (< 10 characters), and overly long titles (> 65 characters).
2. **Meta Description**: Checks for missing description tags, short descriptions (< 50 characters), and long descriptions (> 165 characters).
3. **Heading Structure**: Checks for missing `<h1>` tags, multiple `<h1>` tags on a single page, and skipped hierarchical levels (e.g., `<h1>` immediately followed by `<h3>`).
4. **Canonical Tag**: Validates presence of `<link rel="canonical">` and flags malformed or relative canonical URLs.
5. **Robots Directives**: Detects `noindex` directives in `<meta name="robots">`.
6. **Open Graph Metadata**: Checks for standard social sharing tags (`og:title`, `og:description`, `og:image`).

### B. Accessibility Scanner (`AccessibilityScanner`)
1. **Image Alternative Text (WCAG 1.1.1)**: Detects missing `alt` attributes. Distinguishes decorative images (`alt=""`) from suspicious empty `alt` on hero/banner graphics.
2. **Form Control Labels (WCAG 1.3.1 / 4.1.2)**: Verifies `<label for="id">`, enclosing `<label>`, `aria-label`, `aria-labelledby`, or `title` attributes on all non-hidden inputs.
3. **Document Language (WCAG 3.1.1)**: Checks for the `lang` attribute on the root `<html>` element.
4. **Link Purpose (WCAG 2.4.4)**: Detects empty links lacking accessible names and non-descriptive anchor text (e.g., "click here", "read more").
5. **Button Accessible Names (WCAG 4.1.2)**: Flags icon-only or blank `<button>` elements lacking readable inner text or ARIA labels.
6. **Frame Titles**: Validates descriptive `title` attributes on `<iframe>` elements.

### C. Performance Scanner (`PerformanceScanner`)
1. **Server Latency / TTFB**: Measures live HTTP response latency (flags > 1.2s as Moderate, > 2.5s as Slow).
2. **HTML Payload Size**: Measures raw document byte size (flags > 100 KB and > 250 KB).
3. **Render-Blocking Scripts**: Detects `<script src="...">` in `<head>` lacking `defer`, `async`, or `type="module"`.
4. **Asset Request Counts**: Counts total external scripts, stylesheets, and images (flags > 35 assets).
5. **Native Lazy Loading**: Detects `<img>` elements lacking the `loading="lazy"` attribute.

### D. Security Scanner (`SecurityScanner`)
1. **Transport Encryption**: Enforces HTTPS and verifies automatic redirect from HTTP to HTTPS.
2. **Strict-Transport-Security (HSTS)**: Checks for `Strict-Transport-Security` header on secure connections.
3. **Content-Security-Policy (CSP)**: Checks for presence of `Content-Security-Policy` header.
4. **MIME-Sniffing Defense**: Validates `X-Content-Type-Options: nosniff`.
5. **Clickjacking Defense**: Checks for `X-Frame-Options` or CSP `frame-ancestors`.
6. **Referrer-Policy**: Checks for explicit `Referrer-Policy` header.
7. **Permissions-Policy**: Checks for `Permissions-Policy` or `Feature-Policy`.
8. **Insecure Mixed Content**: Scans HTTPS documents for active or passive assets loaded via insecure `http://`.
9. **Cookie Security Attributes**: Inspects `Set-Cookie` for `HttpOnly`, `Secure`, and `SameSite` flags.

### E. Functionality Scanner (`FunctionalityScanner`)
1. **Placeholder Dead Anchors**: Flags hyperlinks targeting `#`, `javascript:void(0)`, or empty fragments.
2. **Malformed Hyperlink Targets**: Flags unparseable URI schemes.
3. **Form Action Hygiene**: Flags `<form>` elements missing an explicit `action` destination.
4. **Form Method Hygiene**: Flags `<form>` elements lacking an explicit `method` attribute.
5. **Password over HTTP GET**: Detects `<input type="password">` inside forms submitting via `method="GET"`, exposing credentials in URLs and access logs.
6. **Unnamed Form Controls**: Flags form inputs missing `name` attributes which would be omitted from submission payloads.
7. **Broken Internal Links**: Identifies known broken or 404 targets in internal anchor references.

---

## 6. Multi-Layer SSRF Defense Architecture

Target validation is enforced before any network connection is initiated:

1. **Scheme Whitelist**: Strictly permits `http` and `https`. Rejects `file:`, `ftp:`, `gopher:`, `data:`, etc.
2. **Port Range Enforcement**: Rejects invalid port numbers outside 1–65535 (preventing unhandled ValueError exceptions).
3. **Prohibited Hostnames**: Explicitly blocks `localhost`, `localhost.localdomain`, `metadata.google.internal`, `instance-data`, and `.internal`/`.local` top-level domains (with safe exception for internal demo testing).
4. **IP Network Blacklisting**:
   - Loopback: `127.0.0.0/8`, `::1/128`
   - Private RFC1918: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`
   - Cloud Metadata / Link-Local: `169.254.0.0/16`, `fe80::/10`
   - Carrier-Grade NAT: `100.64.0.0/10`
   - IPv6 Unique Local: `fc00::/7`
   - Multicast & Reserved: `224.0.0.0/4`, `240.0.0.0/4`, `ff00::/8`
5. **Pre-Connection DNS Resolution**: Resolves target hostnames via `socket.getaddrinfo` and verifies every returned IPv4 and IPv6 address against the blacklist.
6. **Manual Redirect Re-Validation**: Follows up to 5 HTTP redirects manually, re-checking the destination URL through the full SSRF validation engine before each hop.
7. **Redirect Loop Defense**: Tracks visited URLs in a set and aborts immediately if a destination loop (A → B → A) is detected.
8. **Streaming Size Limit**: Streams response bodies with a hard 5MB limit to prevent memory exhaustion from zip bombs or large binary streams.

---

## 7. Priority Engine & Health Scoring

### Priority Engine
The priority engine maps each finding's severity and category to an actionable score from 0 to 100:

$$\text{Priority} = \text{clamp}\big(\text{round}(\text{Base Severity} \times \text{Category Multiplier}), 0, 100\big)$$

#### Severity Weights:
- **Critical**: 95
- **High**: 80
- **Medium**: 55
- **Low**: 30
- **Info**: 15

#### Category Multipliers:
- **Security**: 1.05 (Elevates critical security vulnerabilities, e.g., Critical Security = 100)
- **Functionality**: 1.0
- **Accessibility**: 1.0
- **Performance**: 1.0
- **SEO**: 0.95

### Transparent Health Scoring
Each category begins at **100.0 points**, with deductions applied based on detected findings:

$$\text{Category Score} = \max(0.0, \min(100.0, 100.0 - \sum \text{Deductions}))$$

The overall website health score is calculated as the arithmetic mean of all five active categories:

$$\text{Overall Health Score} = \text{round}\left(\frac{\text{SEO} + \text{Accessibility} + \text{Performance} + \text{Security} + \text{Functionality}}{5}, 1\right)$$

- **Good Health**: 80.0 – 100.0
- **Moderate Health**: 60.0 – 79.9
- **Needs Attention**: 0.0 – 59.9

---

## 8. AI Reasoning Workflow & Deterministic Fallback

```text
Scanner Findings (Category, Title, Evidence, Severity)
                      │
                      ▼
            Evidence Normalization
                      │
                      ▼
            AI Input Schema Validation
                      │
           ┌──────────┴──────────┐
           │ API Key Configured? │
           └──────────┬──────────┘
             Yes      │      No / Network Timeout
       ┌──────────────┘      └──────────────┐
       ▼                                    ▼
Google Gemini 2.5 Flash             DevLens Deterministic
(Structured Schema Prompt)          Fallback Reasoning Engine
       │                                    │
       └──────────────┬─────────────────────┘
                      │
                      ▼
           Engine Attribution Tagging
     ("Google Gemini" vs. "Fallback Engine")
                      │
                      ▼
      Dashboard Display & PDF Export
```

### Deterministic Fallback Guarantee
- When no Gemini API key is configured or when network limits occur, DevLens AI **automatically and transparently activates its deterministic reasoning engine**.
- The fallback engine interprets technical scanner evidence to generate root-cause diagnoses, user impact assessments, and remediation steps without making external API requests.
- Every report clearly indicates the reasoning engine utilized (`ai_source`).

---

## 9. API Reference

### Authentication Endpoints
- `POST /api/auth/register`: Register user account with Argon2id password hashing. Returns JWT and sets HttpOnly session cookie.
- `POST /api/auth/login`: Authenticates credentials with timing-attack mitigation. Returns JWT and sets HttpOnly cookie.
- `POST /api/auth/logout`: Clears the session cookie.
- `GET /api/auth/me`: Retrieves current authenticated user profile (`id`, `email`, `full_name`, `created_at`). Requires authentication.
- `PUT /api/auth/password`: Changes user password after verifying current credentials. Requires authentication.

### Audit Endpoints
- `POST /api/audits`: Initiates a 5-category website audit. Strictly requires authentication (returns 401 if unauthenticated) and scopes findings to the current user.
- `GET /api/audits`: Lists audits belonging to the authenticated user (returns 401 if unauthenticated). Supports `?q=` URL search filtering.
- `GET /api/audits/{id}`: Retrieves detailed findings, category scores, and AI reasoning for an audit. Requires authentication; returns 404 if owned by another user or nonexistent.
- `DELETE /api/audits/{id}`: Deletes an audit and cascades deletion to associated findings and category scores. Requires authentication and user ownership.
- `POST /api/audits/{id}/rerun`: Reruns an existing audit target. Requires authentication and user ownership.
- `GET /api/audits/{id}/export-pdf`: Generates and streams a branded ReportLab PDF report. Requires authentication and user ownership.
- `GET /api/demo-target`: Serves the internal demo evaluation web page.
- `GET /healthz`: Application health check probe.

---

## 10. Environment Configuration

Copy the example environment configuration:

```bash
cp .env.example .env
```

| Variable | Type | Default | Description |
| :--- | :---: | :---: | :--- |
| `PROJECT_NAME` | string | `DevLens AI` | Application branding name |
| `ENVIRONMENT` | string | `development` | Deployment environment (`development`, `production`) |
| `DATABASE_URL` | string | `sqlite:///./devlens.db` | Database connection string (SQLite or PostgreSQL) |
| `JWT_SECRET` | string | `devlens_super_secret...` | Cryptographic secret for signing session JWT tokens |
| `JWT_ALGORITHM` | string | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | `1440` | Session expiration duration (24 hours) |
| `COOKIE_SECURE` | bool | `false` | Set `true` in production with HTTPS |
| `FRONTEND_ORIGIN` | string | `http://localhost:5173` | Allowed CORS origin for frontend |
| `AI_PROVIDER` | string | `gemini` | AI reasoning provider |
| `AI_API_KEY` | string | `""` | Google Gemini API key (optional; fallback engine used if empty) |
| `AI_MODEL` | string | `gemini-2.5-flash` | Gemini model identifier |
| `MAX_CRAWL_PAGES` | int | `10` | Maximum pages for link discovery |
| `CRAWL_TIMEOUT` | int | `20` | HTTP request timeout in seconds |
| `MAX_RESPONSE_BYTES` | int | `5242880` | Maximum streamed response payload (5 MB) |
| `SSRF_ALLOW_DEMO` | bool | `true` | Allows safe `demo.local` target for local evaluation |
| `HOST` | string | `127.0.0.1` | Backend bind host |
| `PORT` | int | `8000` | Backend bind port |

---

## 11. Local Installation & Run Instructions

### Prerequisites
- Python 3.10+
- Node.js v18+ & npm

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API is available at `http://127.0.0.1:8000`.
- Interactive OpenAPI / Swagger documentation is available at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node modules
npm install

# Start Vite development server
npm run dev
```
- Dashboard is available at `http://localhost:5173`.

---

## 12. Automated Testing Suite

DevLens AI includes a comprehensive automated test suite consisting of **47 passing Pytest tests**:

```bash
cd backend
venv\Scripts\pytest tests -v
```

### Test Suite Structure:
- `tests/test_auth.py` (7 tests): Registration, duplicate rejection, weak password rejection, password mismatch, login, timing attack mitigation, logout.
- `tests/test_protected_endpoints.py` (4 tests): Verification of 401 Unauthorized across all protected audit and auth endpoints, duplicate user handling, credential validation, and session refresh.
- `tests/test_authorization.py` (2 tests): Multi-user data isolation, cross-user viewing/deletion/rerun/PDF export 404 enforcement, audit deletion.
- `tests/test_ssrf.py` (7 tests): Loopback rejection, private RFC1918 rejection, cloud metadata rejection, unsupported schemes, demo target bypass, out-of-range port rejection, IPv6 link-local/loopback rejection.
- `tests/test_scanners.py` (3 tests): SEO title/meta detection, Accessibility alt-text detection, Performance latency heuristics.
- `tests/test_security_scanner.py` (2 tests): Insecure HTTP detection, missing HSTS, CSP, Clickjacking headers, mixed-content detection.
- `tests/test_functionality_scanner.py` (2 tests): Password-over-GET detection, dead anchor links, unnamed form controls.
- `tests/test_scoring.py` (7 tests): Priority severity mapping, category multipliers, boundary clamping, all-passing, all-failing, mixed categories, empty inputs.
- `tests/test_pdf_export.py` (2 tests): Valid ReportLab binary PDF generation, export ownership enforcement.
- `tests/test_ai_fallback.py` (1 test): Evidence-based reasoning execution without Gemini API credentials.
- `tests/test_validation.py` (1 test): URL scheme and netloc format validation.
- `tests/test_api.py` (4 tests): Health check, demo audit execution with auth, unauthenticated rejection (401), invalid URL rejection.
- `tests/test_workflows.py` (5 tests):
  - **Workflow A**: Register → Login → Submit URL → Complete Audit → View Findings → Export PDF.
  - **Workflow B**: Login → Run Audit → Logout → Login Again → View Audit History.
  - **Workflow C**: Create two users → Generate separate audits → Verify strict isolation across records.
  - **Workflow D**: Disable AI credentials → Run Audit → Verify deterministic scanning & fallback reasoning.
  - **Workflow E**: Submit invalid and prohibited URLs → Verify safe rejection (SSRF defense).

---

## 13. Docker Deployment

Deploy the complete containerized stack using Docker Compose:

```bash
# Build and start containers
docker compose up -d --build

# View container logs
docker compose logs -f

# Verify service health
docker compose ps
```

- Frontend is served at `http://localhost` (port 80) via Nginx with API reverse proxy.
- Backend API runs at `http://localhost:8000`.
- SQLite database persists in the named Docker volume `devlens_storage`.

---

## 14. Live Demonstration Procedure

Follow this step-by-step sequence when presenting DevLens AI to evaluators:

1. **Start Services**: Run backend on port 8000 and frontend on port 5173.
2. **Open Application**: Navigate to `http://localhost:5173` in a web browser.
   - Unauthenticated visitors are immediately greeted with the branded **Login / Welcome Back** page.
   - All protected dashboard screens, audit controls, and history are strictly guarded.
3. **Account Registration & Password Strength**:
   - Click **"Create an account"** to transition to the Registration view.
   - Enter full name, email, and password. Observe the dynamic password-strength checklist (minimum 8 characters, uppercase, lowercase, number, special character).
   - Complete registration. The system automatically signs in the user and transitions cleanly into the protected dashboard with zero flashing of protected content.
4. **Run Demo Target Audit**:
   - Click **"Test Built-In Demo Website"** on the home screen.
   - Observe the live sequential progress pipeline: SSRF validation → Crawler → SEO → Accessibility → Performance → Security → Functionality → AI Reasoning.
5. **Examine 5-Category Results**:
   - Inspect the Overall Health Score gauge and individual category score cards.
   - Review detected findings: Missing title, duplicate headings, missing image alt, unoptimized images, mixed content, and password-over-GET form submission.
   - Inspect the **Technical Evidence** snippet and **AI Reasoning & Root Cause** explanation (attributed to the active engine).
6. **Demonstrate SSRF Protection**:
   - In the URL input bar, attempt to submit: `http://127.0.0.1:8000/api` or `http://169.254.169.254/latest/meta-data/`.
   - Observe immediate security rejection by the SSRF defense engine.
7. **Demonstrate Audit History & PDF Export**:
   - Click the **"Audit History"** tab to view your saved audit log.
   - Click **"Export PDF"** to download the branded ReportLab audit report.
   - Open the generated PDF to review the executive overview, category breakdown table, severity distribution, technical evidence, and limitations disclaimer.
8. **Demonstrate Strict Multi-User Isolation**:
   - Direct requests to `/api/audits` without credentials immediately return HTTP 401 Unauthorized.
   - Opening an audit ID belonging to another user returns HTTP 404 Not Found (preventing resource enumeration).
9. **Demonstrate Profile Security & Logout**:
   - Click the user avatar in the navigation bar to open the **User Profile Modal**.
   - Change your password and verify success feedback.
   - Click **"Logout"** to clear session cookies and `sessionStorage`. The user is immediately returned to the Login page.

---

## 15. Audit Methodology & Limitations Disclaimer

- **Automated Heuristics Scope**: DevLens AI scanners evaluate observable DOM structures, HTTP response headers, payload metrics, and transport encryption. Automated scans do not replace exhaustive human accessibility assessments (e.g., screen reader manual navigation) or active penetration testing.
- **Evidence-Grounded AI**: The AI reasoning layer is strictly constrained to interpret scanner findings and cannot independently discover defects outside scanner evidence.
- **Passive Inspection**: Scanners operate passively and non-destructively; they do not perform intrusive vulnerability exploitation or arbitrary state mutations.

---

## 16. Academic Project Information

- **Project Title**: DevLens AI — Intelligent Website Audit & Quality Assurance Platform
- **Project Type**: Final-Year / Semester Engineering Capstone Project
- **Primary Domain**: Full-Stack Web Engineering, Application Security, Automated Software Testing, Artificial Intelligence
- **Status**: Stable, Tested, Documented, and Submission-Ready
