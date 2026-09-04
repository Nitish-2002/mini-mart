---
daksh:
  type: architecture
  subtype: null
  stage: "30a"
  module: null
---

# System Architecture

Mini Mart's [BRD](business-requirements.md) fixed *what* the system must do — eleven use cases, twenty-eight requirements, a canonical order-status vocabulary; this document fixes *what shape it's built in*, the shared rules every module (CATALOG, ORDERS, AUTH) and every future doc inherits without re-deciding. It exists because "Next.js frontend, FastAPI backend, Postgres database" is a starting point, not an architecture — the real content here is the module boundaries, the one network seam between them, and the platform choices (auth model, ORM, background jobs) that would be expensive to disagree about per-module later. The audience is whoever writes a module Solution, System, or TRD next; they should be able to open this file cold and know exactly what's already decided versus still theirs to design.

<details>
<summary>Graph: What shared system shape and rules does every module inherit?</summary>

```items
---
id: 30a-architecture-cognition
title: Architecture — Shared Shape and Rules
default_open_depth: 1
default_color_by: kind
color_palette_source: .daksh/color-palette.json
width: 95vw
---
id: 30a-architecture-cognition
title: Architecture — Shared Shape and Rules
Components:
  - component-01 :: FRONTEND_STOREFRONT | kind: component | summary: "The End User-facing Next.js views: browse, cart, checkout, order tracking." | spec: [Frontend Architecture](system-architecture.md#frontend-architecture) | boundary: "Owns rendering and client-side state for UC-001 through UC-005; owns no business logic — every write goes through BACKEND_API."
  - component-02 :: FRONTEND_ADMIN | kind: component | summary: "The Admin-facing Next.js views: catalog, stock, orders, agent approval." | spec: [Frontend Architecture](system-architecture.md#frontend-architecture) | boundary: "Owns rendering for UC-006 through UC-009's admin side; same backend, same deployable, different route group and auth guard."
  - component-03 :: FRONTEND_AGENT | kind: component | summary: "The Delivery Agent-facing Next.js views: registration, assignment, delivery, COD confirmation." | spec: [Frontend Architecture](system-architecture.md#frontend-architecture) | boundary: "Owns rendering for UC-009 and UC-010's agent side; same deployable as the other two frontend components (decision-13, vision.md)."
  - component-04 :: CATALOG_SERVICE | kind: component | summary: "Owns items, categories, stock quantities, and the reserve/release stock operation every order depends on." | spec: [Module Decomposition](system-architecture.md#module-decomposition) | boundary: "In: item/category CRUD, bulk import, stock reservation and release, low-stock flagging. Out: no knowledge of orders, payment, or delivery — ORDERS calls in, CATALOG never calls out to ORDERS."
  - component-05 :: ORDERS_SERVICE | kind: component | summary: "Owns cart, checkout, the order status lifecycle, agent assignment, and stale-order release — the one deep Order Lifecycle module vision's decision-12 argued for." | spec: [Module Decomposition](system-architecture.md#module-decomposition) | boundary: "In: cart, checkout, cancellation, status transitions, agent assignment/reassignment, COD confirmation. Out: calls CATALOG for stock, calls AUTH for identity — owns no catalog or credential data itself."
  - component-06 :: AUTH_SERVICE | kind: component | summary: "Owns identity for all three roles — End User, Delivery Agent, Admin — OTP issuance/verification, and session tokens." | spec: [Module Decomposition](system-architecture.md#module-decomposition) | boundary: "In: account creation, OTP, login, session issuance, agent approval gate, admin password reset. Out: no knowledge of catalog or orders — every other module calls in to verify who's asking."
Infrastructure:
  - infra-01 :: DATABASE | kind: infrastructure | summary: "The single Postgres instance holding every module's tables — no per-module database split at this scale." | spec: [Database Architecture](system-architecture.md#database-architecture) | kind_detail: managed_db | size: "small — single instance, Phase 1 order volume" | count: 1 | availability: single_zone | evidence: assumed
  - infra-02 :: EMAIL_PROVIDER (Resend) | kind: infrastructure | summary: "Resend — transactional email service for OTP codes and order-status notifications (decision-17, vision.md). 3,000 emails/month free, comfortably covers Phase 1 volume." | spec: [Cross-Cutting Concerns](system-architecture.md#shared-platform-rules-and-cross-cutting-concerns) | kind_detail: external_saas | size: "low volume — OTP + status emails only" | count: 1 | availability: single_zone | evidence: decided
  - infra-03 :: OBJECT_STORAGE (AWS S3) | kind: infrastructure | summary: "AWS S3 — stores catalog item photos uploaded via bulk import or admin edit, referenced by URL, not stored as database blobs." | spec: [Database Architecture](system-architecture.md#database-architecture) | kind_detail: object_storage | size: "small — a single mart's item photos" | count: 1 | availability: single_zone | evidence: decided
  - infra-04 :: LOGGING_MONITORING | kind: infrastructure | summary: "Centralized application logs and error tracking — provider TBD, requirement is not." | spec: [Project-Wide Quality Requirements](system-architecture.md#project-wide-quality-requirements) | kind_detail: observability | size: "small-scale, single deployable" | count: 1 | availability: single_zone | evidence: assumed
  - infra-05 :: BACKEND_COMPUTE | kind: infrastructure | summary: "The compute substrate running the single FastAPI process (CATALOG + ORDERS + AUTH together) — specific host deferred (oq-27)." | spec: [Backend Architecture](system-architecture.md#backend-architecture) | kind_detail: instance_or_container | size: "small — single small instance/container, Phase 1 scale" | count: 1 | availability: single_zone | evidence: assumed
  - infra-06 :: FRONTEND_HOSTING | kind: infrastructure | summary: "The hosting substrate for the Next.js app — specific host deferred (oq-27)." | spec: [Frontend Architecture](system-architecture.md#frontend-architecture) | kind_detail: static_or_edge | size: "small — single Next.js deployment" | count: 1 | availability: single_zone | evidence: assumed
Environments:
  - env-01 :: LOCAL | kind: environment | summary: "Developer machines — Docker Compose running Postgres and the FastAPI app locally." | spec: [Deployment Architecture](system-architecture.md#deployment-architecture) | purpose: dev | region: "on developer machine" | access: "any engineer"
  - env-02 :: PREVIEW | kind: environment | summary: "Ephemeral per-branch/PR environment for review before merge — confirmed worth keeping (decision-42), exact host still TBD (oq-27)." | spec: [Deployment Architecture](system-architecture.md#deployment-architecture) | purpose: preview | region: "host TBD (oq-27)" | access: "PTL and reviewers"
  - env-03 :: PRODUCTION | kind: environment | summary: "The live environment real End Users, Admin, and Delivery Agents use." | spec: [Deployment Architecture](system-architecture.md#deployment-architecture) | purpose: prod | region: "host TBD (oq-27)" | access: "PTL deploys; Admin/agents/end users use, no deploy access"
Pipelines:
  - pipeline-01 :: CI (GitHub Actions) | kind: pipeline | summary: "GitHub Actions workflow on every push and pull request: install, lint, typecheck, test, both frontend and backend." | spec: [Deployment Architecture](system-architecture.md#deployment-architecture) | trigger: "push or pull request to any branch" | stages: "install -> lint -> typecheck -> unit tests" | duration: "target under 5 minutes"
  - pipeline-02 :: CD_PREVIEW (GitHub Actions) | kind: pipeline | summary: "GitHub Actions workflow deploying a pull request's branch to an ephemeral PREVIEW environment for review." | spec: [Deployment Architecture](system-architecture.md#deployment-architecture) | trigger: "pull request opened or updated" | stages: "build -> deploy to PREVIEW" | duration: "target under 5 minutes"
  - pipeline-03 :: CD_PRODUCTION (GitHub Actions) | kind: pipeline | summary: "GitHub Actions workflow deploying `develop` (or `main`, per the branching model) to PRODUCTION after CI passes." | spec: [Deployment Architecture](system-architecture.md#deployment-architecture) | trigger: "merge to the production branch" | stages: "build -> run DB migrations -> deploy to PRODUCTION" | duration: "target under 10 minutes"
Decisions:
  - decision-33 :: Single monolithic backend, not microservices | kind: decision | summary: "CATALOG, ORDERS, and AUTH are Python packages inside one deployable FastAPI process, not three independently deployed services. Deep because one deployable hides three modules' worth of behavior behind one process boundary, with in-process calls instead of network calls between them." | spec: [Backend Architecture](system-architecture.md#backend-architecture) | alternatives: "Microservices per module — rejected; at Phase 1's dozens-of-orders/day scale, network boundaries between CATALOG/ORDERS/AUTH would add latency and deployment overhead with no caller who needs independent scaling or independent deploy cadence yet." | reversal_trigger: "A specific module needs to scale or deploy independently of the others — e.g. a future high-traffic public storefront outgrowing the admin/agent side."
  - decision-34 :: Frontend-backend boundary is a versioned REST API | kind: decision | summary: "One JSON-over-HTTPS REST API is the only seam between the three Next.js frontend components and the backend — deep because it hides all three backend modules' internals behind one contract every frontend view calls the same way." | spec: [Module Interactions](system-architecture.md#module-interactions-and-versioned-logical-interfaces) | alternatives: "GraphQL — more flexible querying, but adds schema/resolver complexity not justified at this scale. tRPC — TypeScript-to-TypeScript only, incompatible with a Python backend." | reversal_trigger: "The frontend needs highly flexible, deeply nested ad-hoc queries that a fixed REST surface makes genuinely awkward."
  - decision-35 :: Stateless JWT sessions, not server-side session store | kind: decision | summary: "After OTP verification, AUTH issues a JWT (role embedded in claims) stored in an httpOnly cookie — no Redis-backed session store." | spec: [Permission Model and Governance](system-architecture.md#permission-model-and-governance) | alternatives: "Server-side session store (e.g. Redis) — enables instant server-side revocation, but is infrastructure this scale doesn't need yet." | reversal_trigger: "A real requirement emerges for instant cross-device logout/revocation that a short-lived JWT plus refresh can't satisfy cleanly."
  - decision-36 :: SQLAlchemy 2.0 (async) + Alembic for ORM and migrations | kind: decision | summary: "The one data-access layer every module uses to reach DATABASE — deep because it hides connection pooling, query construction, and schema migration behind one consistent pattern across CATALOG, ORDERS, and AUTH." | spec: [Database Architecture](system-architecture.md#database-architecture) | alternatives: "SQLModel — nicer Pydantic integration, but a younger project with a less mature migration story. Raw SQL/query builder — more control, more boilerplate, no compelling reason to hand-write what an ORM does well at this scale." | reversal_trigger: "ORM query overhead becomes a measured performance bottleneck — unlikely at Phase 1 order volume."
  - decision-37 :: npm for frontend, uv for backend package management | kind: decision | summary: "Sensible current defaults, not project-specific requirements — npm ships with Node with no setup, uv is the fast modern choice for Python dependency management and lockfiles." | spec: [Technology Baseline](system-architecture.md#technology-baseline) | alternatives: "pnpm/yarn for frontend — no strong reason to add another tool. pip+venv or Poetry for backend — uv is faster and handles locking better with less configuration." | reversal_trigger: "Team tooling preference changes, or a specific constraint (e.g. a host that only supports pip) forces a switch."
  - decision-38 :: Stale-order release runs as an in-process scheduled job | kind: decision | summary: "UC-011's stale-order timeout check runs inside the FastAPI process (e.g. APScheduler), not as a separate task-queue service." | spec: [UC-011, business-requirements.md](business-requirements.md#uc-011-system-releases-stock-for-stale-orders) | alternatives: "A dedicated task queue (Celery + Redis) — real operational complexity (broker, worker process, monitoring) not justified for a periodic check at Phase 1 volume." | reversal_trigger: "Background job volume or complexity grows enough that in-process polling blocks or meaningfully slows the API process."
  - decision-39 :: Resend for transactional email | kind: decision | summary: "Resend is the EMAIL_PROVIDER for OTP and status emails — 3,000/month free tier comfortably covers Phase 1 volume at zero cost." | spec: [Shared Platform Rules](system-architecture.md#shared-platform-rules-and-cross-cutting-concerns) | alternatives: "Brevo — also generous free tier (~9,000/month) but carries unneeded marketing-email features. AWS SES — cheaper at higher volume but needs domain verification and manual sending-limit requests; more setup with no benefit at this volume." | reversal_trigger: "Email volume grows past the free tier meaningfully, making SES's lower per-email cost worth the extra setup."
  - decision-40 :: AWS S3 for object storage | kind: decision | summary: "AWS S3 is OBJECT_STORAGE for catalog item photos." | spec: [Database Architecture](system-architecture.md#database-architecture) | alternatives: "Cloudflare R2 — zero egress fees, which matters more for an image-heavy catalog, but S3 was chosen instead, likely for familiarity/ecosystem fit. Supabase Storage — only relevant if Supabase is chosen for other infrastructure, which it isn't here." | reversal_trigger: "Egress costs from S3 become a real, measured expense once catalog traffic grows."
  - decision-41 :: GitHub Actions for CI/CD | kind: decision | summary: "All three pipelines (CI, CD_PREVIEW, CD_PRODUCTION) run on GitHub Actions — no separate CI service to set up since the code already lives on GitHub." | spec: [Deployment Architecture](system-architecture.md#deployment-architecture) | alternatives: "A separate CI service (CircleCI, GitLab CI, etc.) — no benefit over Actions given the repo is already on GitHub, and would add a second service/account to manage." | reversal_trigger: "A hosting choice (oq-27) comes with its own strongly preferred/integrated CI system that makes Actions redundant."
  - decision-42 :: Keep the PREVIEW environment | kind: decision | summary: "A per-PR ephemeral PREVIEW environment stays in the pipeline design — lets changes be reviewed live before merging to PRODUCTION." | spec: [Deployment Architecture](system-architecture.md#deployment-architecture) | alternatives: "Drop it, keep only LOCAL and PRODUCTION — simpler pipeline, but no pre-merge review environment for the client or reviewers to check a change against." | reversal_trigger: "The eventual hosting choice (oq-27) makes preview environments costly or awkward to provision."
  - decision-43 :: Daily automated Postgres backups, 7-day retention | kind: decision | summary: "DATABASE is backed up daily with backups retained for 7 days — a standard small-business default most managed Postgres hosts provide built in." | spec: [Project-Wide Quality Requirements](system-architecture.md#project-wide-quality-requirements) | alternatives: "Longer retention or more frequent backups — more recovery flexibility, but more storage cost with no stated need yet at Phase 1 data volume." | reversal_trigger: "A real incident requires recovering data older than 7 days, or compliance/client policy later requires longer retention."
OpenQuestions:
  - oq-27 :: Deployment/hosting target | kind: openquestion | summary: "The client has hosting in mind but hasn't shared it yet — BACKEND_COMPUTE, FRONTEND_HOSTING, and both non-LOCAL Environments are placeholders until it's confirmed. Still genuinely open." | spec: [Deployment Architecture](system-architecture.md#deployment-architecture)
  - oq-28 :: Email provider selection | kind: openquestion | summary: "Which transactional email provider? — resolved, see decision-39." | spec: [Architecture Decisions](system-architecture.md#architecture-decisions)
  - oq-29 :: Object storage provider selection | kind: openquestion | summary: "Which object storage provider for item photos? — resolved, see decision-40." | spec: [Architecture Decisions](system-architecture.md#architecture-decisions)
  - oq-30 :: CI/CD tooling | kind: openquestion | summary: "Is GitHub Actions the CI/CD tool? — resolved, see decision-41." | spec: [Architecture Decisions](system-architecture.md#architecture-decisions)
  - oq-31 :: Whether a PREVIEW environment is worth keeping | kind: openquestion | summary: "Is a PREVIEW environment worth keeping? — resolved, see decision-42." | spec: [Architecture Decisions](system-architecture.md#architecture-decisions)
  - oq-32 :: Database backup/retention policy | kind: openquestion | summary: "What's the database backup/retention policy? — resolved, see decision-43." | spec: [Architecture Decisions](system-architecture.md#architecture-decisions)
component-04 -> interface-01 | relation: produces
component-05 -> interface-01 | relation: produces
component-06 -> interface-01 | relation: produces
component-01 -> infra-06 | relation: runs_on
component-02 -> infra-06 | relation: runs_on
component-03 -> infra-06 | relation: runs_on
component-04 -> infra-05 | relation: runs_on
component-05 -> infra-05 | relation: runs_on
component-06 -> infra-05 | relation: runs_on
infra-05 -> env-03 | relation: lives_in
infra-06 -> env-03 | relation: lives_in
infra-01 -> env-03 | relation: lives_in
decision-33 -> infra-05 | relation: governs
decision-34 -> interface-01 | relation: governs
decision-35 -> component-06 | relation: governs
decision-36 -> infra-01 | relation: governs
decision-38 -> component-05 | relation: governs
decision-39 -> oq-28 | relation: decides
decision-40 -> oq-29 | relation: decides
decision-41 -> oq-30 | relation: decides
decision-42 -> oq-31 | relation: decides
decision-43 -> oq-32 | relation: decides
decision-39 -> infra-02 | relation: governs
decision-40 -> infra-03 | relation: governs
decision-41 -> pipeline-01 | relation: governs
decision-42 -> env-02 | relation: governs
decision-43 -> infra-01 | relation: governs
interface-01 :: BACKEND_API | kind: interface | summary: "The one versioned REST contract every frontend component calls and every backend module contributes to — the single network seam in the whole system." | spec: [Module Interactions](system-architecture.md#module-interactions-and-versioned-logical-interfaces) | shape: "OpenAPI schema generated by FastAPI, versioned via a /v1 URL prefix" | version: "v1" | compatibility: additive
```

</details>

> [!note]
> This graph carries 37 nodes across 6 groups, plus `interface-01` (`BACKEND_API`) as a single ungrouped root item rather than a fake "Interfaces" group of one — it's the only real network seam in the system; every other module boundary (CATALOG↔ORDERS, anything↔AUTH) is in-process per [decision-33](#) and deliberately carries no Interface node, only a documented function-level contract in prose. A follow-up round resolved 5 of the 6 original open questions into `decision-39` through `decision-43` (email/storage vendor, CI/CD tool, keeping the preview environment, backup policy); only `oq-27` (the hosting target itself) remains genuinely open, pending the client.

## Context and Architectural Drivers

Three things shape every choice below. First, [decision-12](vision.md#vision-decisions) (vision.md) argued the product *is* one deep Order Lifecycle — that thesis extends here as decision-33's monolith: fragmenting CATALOG/ORDERS/AUTH into network-separated services would reintroduce the reconciliation cost the whole product exists to remove, just at the infrastructure layer instead of the business layer. Second, cost-consciousness has been a real, repeated constraint since onboarding — SMS OTP was rejected for it, and every technology choice below defaults to the cheapest option that doesn't compromise the requirement, not the most sophisticated one. Third, this is genuinely greenfield: `backend/`, `frontend/`, and `devops/` are empty directories with no code, no CI/CD config, and no deployed substrate `[derived/observed · src: repo root, 2026-09-03]` — nothing here is retrofitted, everything is a forward decision.

## Frontend Architecture

Next.js 15 (App Router) with TypeScript, one deployable serving three role-scoped route groups — [component-01](#) `FRONTEND_STOREFRONT`, [component-02](#) `FRONTEND_ADMIN`, [component-03](#) `FRONTEND_AGENT` — rather than three separate applications, directly implementing [decision-13](vision.md#vision-decisions)'s "one integrated product with three role-based views." Each route group is guarded by the JWT role claim [decision-35](#) issues; a request to `/admin/*` without an `admin` claim is rejected before rendering, not just hidden in the UI. All three components call the same [interface-01](#) `BACKEND_API` — none of them talk to `DATABASE` or any other infrastructure directly.

## Backend Architecture

One FastAPI process, Python 3.12, organized as three internal packages — `app/catalog`, `app/orders`, `app/auth` — matching [component-04](#), [component-05](#), [component-06](#) exactly, per [decision-33](#)'s single-monolith call. Module boundaries are enforced by import discipline, not network calls: `ORDERS` imports and calls `CATALOG`'s `reserve_stock()` / `release_stock()` / `get_availability()` functions directly, and every module calls `AUTH`'s `get_current_user()` dependency to resolve who's asking — these are Python-level contracts, not versioned Interfaces, because they're in-process (see the graph note above). `AUTH` is the only module allowed to read or write credential/OTP data; `CATALOG` is the only module allowed to write stock quantities; `ORDERS` owns the order/cart tables and calls out to the other two rather than duplicating their data.

## Database Architecture

One Postgres 16 instance ([infra-01](#) `DATABASE`), one schema, tables owned per-module by convention (`catalog_*`, `orders_*`, `auth_*` prefixes) rather than physically separate databases — consistent with the single-monolith decision, since splitting the database without splitting the deployable would add operational cost with no isolation benefit. Item photos go to AWS S3 ([infra-03](#) `OBJECT_STORAGE`, [decision-40](#)), referenced from the `catalog_items` table by URL — not stored as database blobs, keeping the database itself small and backups fast. `DATABASE` is backed up daily with 7-day retention ([decision-43](#)). `Order.status` and `DeliveryAgent.status` persist exactly the canonical vocabulary [business-requirements.md locked](business-requirements.md#domain-vocabulary) — no module is permitted to store a status value not in that list.

## Permission Model and Governance

Three roles, one shared `AUTH_SERVICE`: End User and Delivery Agent both authenticate via email + OTP ([decision-15](vision.md#vision-decisions), [decision-27](business-requirements.md#brd-decisions)); Admin authenticates via the single shared username/password login ([decision-22](vision.md#vision-decisions)). On successful authentication, `AUTH_SERVICE` issues a JWT ([decision-35](#)) carrying the role (`end_user` / `delivery_agent` / `admin`) as a claim, stored in an httpOnly cookie so the frontend never handles the raw token in JavaScript. Every `BACKEND_API` route declares which role(s) it accepts; a Delivery Agent token can never call an Admin-only route, and vice versa, enforced server-side on every request — the frontend route guard from [Frontend Architecture](#frontend-architecture) is a UX convenience, not the actual security boundary.

## Technology Baseline

| Layer | Choice | Version |
|---|---|---|
| Frontend framework | Next.js, App Router | 15.x |
| Frontend language | TypeScript | 5.x |
| Frontend package manager | npm ([decision-37](#)) | bundled with Node 20 LTS |
| Backend framework | FastAPI | latest stable |
| Backend language | Python | 3.12 |
| Backend package manager | uv ([decision-37](#)) | latest stable |
| ORM / migrations | SQLAlchemy 2.0 (async) + Alembic ([decision-36](#)) | latest stable |
| Database | PostgreSQL | 16 |

Exact patch versions are pinned in each package's lockfile at first `npm install` / `uv sync`, not hand-picked here — this table fixes the *major* choices every module inherits, not a version-pin ceremony that goes stale the day it's written.

## Module Decomposition

| Module | Owns | Does not own |
|---|---|---|
| [CATALOG](#) ([component-04](#)) | Items, categories, stock quantities, bulk import, low-stock threshold | Orders, payments, delivery, identity |
| [ORDERS](#) ([component-05](#)) | Cart, checkout, order status lifecycle, agent assignment, stale-order release | Item/stock data (calls CATALOG), identity (calls AUTH) |
| [AUTH](#) ([component-06](#)) | End User/Delivery Agent/Admin identity, OTP, sessions, agent approval gate | Catalog or order data |

This maps directly to the BRD: `CATALOG` owns UC-002, UC-006, and UC-007's stock side; `ORDERS` owns UC-003 through UC-005, UC-008, UC-010, and UC-011; `AUTH` owns UC-001 and UC-009's approval gate. No use case spans more than one module's *ownership*, even though most call across module boundaries — that's the point of the boundaries.

## Module Interactions and Versioned Logical Interfaces

**[interface-01](#) `BACKEND_API` (v1, additive compatibility)** — the one interface external callers (all three frontend components) use. Producers: `CATALOG_SERVICE`, `ORDERS_SERVICE`, `AUTH_SERVICE`, each contributing their own route prefix (`/v1/catalog/*`, `/v1/orders/*`, `/v1/auth/*`) to one OpenAPI schema. Compatibility is `additive`: a new field or endpoint doesn't break existing frontend calls; removing or renaming one does, and requires a version bump — this is the contract every module TRD must honor.

**Internal, in-process contracts (no Interface node, per [decision-33](#)):** `ORDERS` → `CATALOG.reserve_stock(item_id, qty) / release_stock(order_id) / get_availability(item_id)`; any module → `AUTH.get_current_user(token) / require_role(role)`. These are Python function signatures owned by their module, versioned implicitly by the deployable's own version — not independently versioned, because there is and will only ever be one caller-visible surface (`BACKEND_API`) for anything outside the process.

## Shared Platform Rules and Cross-Cutting Concerns

- **Domain vocabulary is law.** Every module reuses `business-requirements.md`'s canonical `Order.status`, cancellation-reason, and `DeliveryAgent.status` values verbatim — see [Database Architecture](#database-architecture).
- **Email is the only outbound notification channel** ([infra-02](#) `EMAIL_PROVIDER` — Resend, [decision-39](#)) — OTP codes ([decision-28](business-requirements.md#brd-decisions)) and order-status updates ([decision-17](vision.md#vision-decisions)) both go through it; no SMS integration exists anywhere in this architecture.
- **All monetary and quantity fields are integers or fixed-point, never floats** — a baseline correctness rule for a system whose whole premise is eliminating billing errors ([goal-01b](vision.md#vision-statement)).
- **English only, no i18n scaffolding** in Phase 1 ([decision-21](vision.md#vision-decisions)) — no translation-key indirection to maintain that nothing currently uses.

## Project-Wide Quality Requirements

| Concern | Target |
|---|---|
| Performance | ~2s page loads under normal conditions ([BRD NFR-1](business-requirements.md#non-functional-requirements)) — no formal SLA |
| Availability | Standard hosting availability, no 99.9%-style uptime guarantee ([BRD NFR-2](business-requirements.md#non-functional-requirements)) |
| Security — credentials | Admin password and any future credential stored hashed, never plaintext ([BRD NFR-4](business-requirements.md#non-functional-requirements)) |
| Security — OTP | 10-minute expiry, 60-second resend cooldown, rate-limited ([decision-28](business-requirements.md#brd-decisions)) |
| Load | No load-testing requirement at Phase 1's dozens-of-orders/day scale ([BRD NFR-1](business-requirements.md#non-functional-requirements)) — deferred until real volume data exists |
| Logging | Centralized application logs via [infra-04](#) `LOGGING_MONITORING`, provider TBD |
| Monitoring | Error tracking via the same `LOGGING_MONITORING` piece — no separate APM tool planned at this scale |
| Testing | `pipeline-01` (`CI`, GitHub Actions — [decision-41](#)) runs lint, typecheck, and unit tests on every push/PR — coverage target deferred to each module's Test Specification (stage 50b) |
| Backup | Daily automated backups, 7-day retention ([decision-43](#)) |

## Decisions

See the graph above for the full `alternatives`/`reversal_trigger` pairs; summarized here for a scanning reader:

| Decision | Choice | Owner |
|---|---|---|
| [decision-33](#) | Single monolithic backend, not microservices | PTL |
| [decision-34](#) | Frontend-backend boundary is a versioned REST API | PTL |
| [decision-35](#) | Stateless JWT sessions, not a server-side session store | PTL |
| [decision-36](#) | SQLAlchemy 2.0 (async) + Alembic | PTL |
| [decision-37](#) | npm (frontend) / uv (backend) package managers | PTL |
| [decision-38](#) | Stale-order release runs as an in-process scheduled job | PTL |
| [decision-39](#) | Resend for transactional email | PTL |
| [decision-40](#) | AWS S3 for object storage | PTL |
| [decision-41](#) | GitHub Actions for CI/CD | PTL |
| [decision-42](#) | Keep the PREVIEW environment | PTL |
| [decision-43](#) | Daily automated Postgres backups, 7-day retention | PTL |

## Architecture Decisions

The 5 of 6 open questions this stage's first draft raised that didn't depend on the still-pending hosting choice were closed in a follow-up round.

1. **Resend handles transactional email** ([decision-39](#)) — free tier comfortably covers Phase 1 OTP and notification volume. Revisit if volume outgrows the free tier.
2. **AWS S3 handles item-photo storage** ([decision-40](#)). Revisit if egress costs become a measured expense as catalog traffic grows.
3. **GitHub Actions runs all three pipelines** ([decision-41](#)) — no separate CI service needed since the code's already on GitHub. Revisit only if the eventual host bundles its own strongly-preferred CI.
4. **The PREVIEW environment stays** ([decision-42](#)) — pre-merge review before PRODUCTION. Revisit if the eventual host makes preview environments costly.
5. **DATABASE backs up daily, 7-day retention** ([decision-43](#)) — a standard small-business default. Revisit if a real recovery need or compliance requirement demands longer retention.

## Deployment Architecture

Three environments — [env-01](#) `LOCAL` (Docker Compose, any developer machine), [env-02](#) `PREVIEW` (ephemeral, per-PR, confirmed worth keeping — [decision-42](#)), [env-03](#) `PRODUCTION` (the live system) — and three GitHub Actions pipelines ([decision-41](#)) — [pipeline-01](#) `CI`, [pipeline-02](#) `CD_PREVIEW`, [pipeline-03](#) `CD_PRODUCTION` — but the actual hosting substrate behind `PREVIEW` and `PRODUCTION` ([infra-05](#) `BACKEND_COMPUTE`, [infra-06](#) `FRONTEND_HOSTING`) is still a placeholder: the client has a hosting target in mind and will share it ([oq-27](#)), so nothing here commits to a specific vendor. What *is* fixed regardless of host: `CD_PRODUCTION` always runs database migrations before deploying new code, and `PRODUCTION` is the only environment real End Users, Admin, and Delivery Agents touch.

## Open Questions

Only one question remains open from this stage — the other five were resolved in the follow-up above; see [Architecture Decisions](#architecture-decisions).

1. **What is the actual hosting target?** ([oq-27](#)) The client has one in mind but hasn't shared it yet — blocks finalizing `BACKEND_COMPUTE`, `FRONTEND_HOSTING`, and both non-`LOCAL` environments. This stage cannot be approved until it resolves, since `open_questions: mandatory` applies project-wide.

## Approval

Approved by:
Role:
Date:
