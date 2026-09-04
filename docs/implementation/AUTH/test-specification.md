---
daksh:
  type: test-specification
  subtype: null
  stage: "50b"
  module: AUTH
---

# AUTH Test Specification

AUTH's [Solution](solution.md), [System](system.md), and [TRD](trd.md) promised five business flows, fourteen testable behaviors, and fifteen technical requirements; this document is the evidence plan proving each one — every `SS-AUTH-NNN`, `SY-AUTH-NNN`, and `TRD-AUTH-NNN`, plus every `DS-AUTH-NNN` screen from [experience-design.md](experience-design.md), maps to at least one stable `TEST-AUTH-NNN` case below. Coverage spans five layers: unit (pure functions, no DB), integration (real Postgres, fake email), interface/contract (HTTP-level schema conformance), end-to-end (full journeys through a real app instance), and frontend/accessibility (per-screen, against [experience-design.md](experience-design.md#usability-and-accessibility-criteria)'s own numeric targets). Test IDs are stable identifiers; a revision changes a case's body, never its identity.

<details>
<summary>Graph: What evidence proves each promised behavior?</summary>

```items
---
id: 50b-auth-test-cognition
title: AUTH Test Specification — Evidence and Proof
default_open_depth: 1
default_color_by: kind
color_palette_source: .daksh/color-palette.json
width: 95vw
---
id: 50b-auth-test-cognition
title: AUTH Test Specification — Evidence and Proof
Flows:
  - ss-auth-001 :: Email + OTP identity verification | kind: flow | summary: "Reused from solution.md — the shared End User/Agent signup+login mechanism this stage's Area A tests cover." | spec: [Traceability](test-specification.md#traceability) | actor: "End User or Delivery Agent" | trigger: "Someone enters an email to sign up or log in" | outcome: "A verified session exists for that email, scoped to whichever role it was entered under"
  - ss-auth-002 :: Delivery Agent registration and approval gate | kind: flow | summary: "Reused from solution.md — covered by this stage's Area B tests." | spec: [Traceability](test-specification.md#traceability) | actor: "Delivery Agent, Admin" | trigger: "Prospective agent submits registration details" | outcome: "Agent status is `approved` or `rejected`"
  - ss-auth-003 :: Admin credential login | kind: flow | summary: "Reused from solution.md — covered by this stage's Area C tests." | spec: [Traceability](test-specification.md#traceability) | actor: "Admin" | trigger: "Admin enters credentials" | outcome: "A verified Admin session exists, or the attempt is rejected"
  - ss-auth-004 :: Admin password recovery | kind: flow | summary: "Reused from solution.md — covered by this stage's Area D tests." | spec: [Traceability](test-specification.md#traceability) | actor: "Admin" | trigger: "Admin requests a password reset" | outcome: "Admin sets a new password via the emailed link, or the request expires unused"
  - ss-auth-005 :: Session issuance and role-scoped authorization | kind: flow | summary: "Reused from solution.md — covered by this stage's Area E tests, the cross-cutting mechanism CATALOG/ORDERS depend on." | spec: [Traceability](test-specification.md#traceability) | actor: "System (invisible to the end user)" | trigger: "A verified login completes, or a protected request arrives" | outcome: "The requesting role is known and enforced, or the request is rejected"
Interfaces:
  - interface-auth-identity :: Identity & OTP interface | kind: interface | summary: "Reused from system.md/trd.md — contract-tested by TEST-AUTH-022/023." | spec: [Interface and Contract Tests](test-specification.md#interface-and-contract-tests) | shape: "[trd.md API Contracts](trd.md#api-contracts)" | version: "v1" | compatibility: additive
  - interface-auth-agent-mgmt :: Agent registration & lifecycle interface | kind: interface | summary: "Reused from system.md/trd.md — contract-tested by TEST-AUTH-024/025." | spec: [Interface and Contract Tests](test-specification.md#interface-and-contract-tests) | shape: "[trd.md API Contracts](trd.md#api-contracts)" | version: "v1" | compatibility: additive
  - interface-auth-admin-login :: Admin login & recovery interface | kind: interface | summary: "Reused from system.md/trd.md — contract-tested by TEST-AUTH-026/027/028/029." | spec: [Interface and Contract Tests](test-specification.md#interface-and-contract-tests) | shape: "[trd.md API Contracts](trd.md#api-contracts)" | version: "v1" | compatibility: additive
Invariants:
  - inv-auth-singleton-admin :: Exactly one row in auth_admin_accounts, always | kind: invariant | summary: "Reused from trd.md — proved by TEST-AUTH-014." | spec: [Unit and Integration Tests](test-specification.md#unit-tests) | violation_signal: "A second row in auth_admin_accounts, or a successful INSERT attempting to create one."
  - inv-auth-audit-atomicity :: Every agent status write and its audit-log row commit together | kind: invariant | summary: "Reused from trd.md — proved by TEST-AUTH-013." | spec: [Integration Tests](test-specification.md#integration-tests) | violation_signal: "A status value with no corresponding log row, or vice versa."
  - inv-auth-no-secrets-in-logs :: No plaintext password, OTP code, or reset token ever appears in application logs | kind: invariant | summary: "Reused from trd.md — proved by TEST-AUTH-038, the one test that inspects captured log output rather than a return value." | spec: [Edge, Failure, Security, Performance, and Recovery Tests](test-specification.md#edge-failure-security-performance-and-recovery-tests) | violation_signal: "Any captured log line containing a raw OTP digit string, admin password, or reset token."
  - inv-auth-single-use-tokens :: A consumed OTP or reset token can never validate again | kind: invariant | summary: "Reused from trd.md — proved by TEST-AUTH-009 (OTP) and TEST-AUTH-018 (reset token)." | spec: [Integration Tests](test-specification.md#integration-tests) | violation_signal: "A successful verify/confirm against a row whose consumed_at/used_at is already non-null."
Risks:
  - risk-auth-email-outage :: EMAIL_PROVIDER outage blocks OTP-based login, signup, and Admin recovery | kind: risk | summary: "Reused from trd.md — watched (not proved, since Phase 1 has no automated failover) by TEST-AUTH-039." | spec: [Edge, Failure, Security, Performance, and Recovery Tests](test-specification.md#edge-failure-security-performance-and-recovery-tests) | likelihood: "unknown — unvalidated" | impact: "high — blocks nearly all authentication" | mitigation: "No automated failover in Phase 1; the resend button is the only retry path." | phase: runtime
Metrics:
  - metric-otp-completion :: OTP entry completion rate | kind: metric | summary: "Reused from experience-design.md — watched by TEST-AUTH-034's frontend suite; the actual field measurement happens post-launch, not in this test spec." | spec: [Frontend and Accessibility Tests](test-specification.md#frontend-and-accessibility-tests) | baseline: "unmeasured" | target: "85%+ first-attempt success" | current: "not yet measured"
  - metric-a11y-contrast :: Text contrast ratio | kind: metric | summary: "Reused from experience-design.md — proved (not just watched) by TEST-AUTH-034 through TEST-AUTH-037's axe-core contrast checks, which run automatically and fail the build on violation." | spec: [Frontend and Accessibility Tests](test-specification.md#frontend-and-accessibility-tests) | baseline: "n/a — design-time target" | target: "WCAG AA, 4.5:1 minimum" | current: "met in the prototype's token contract"
Tests:
  - test-otp-flow :: Email+OTP flow test suite | kind: test | summary: "Bundles TEST-AUTH-007 through 011, 022, 023, 030, 034 — issuance, verify (correct/wrong/expired), rate limiting, session issuance, contract conformance, the full e2e journey, and the frontend/a11y pass." | spec: [Unit and Integration Tests](test-specification.md#unit-tests) | trigger: "Runs on every push/PR via pipeline-01 (CI)"
  - test-agent-lifecycle :: Agent registration and lifecycle test suite | kind: test | summary: "Bundles TEST-AUTH-012, 013, 024, 025, 031, 035 — registration, dupe rejection, every status transition with its audit-log write, contract conformance, e2e onboarding journey, frontend/a11y." | spec: [Integration Tests](test-specification.md#integration-tests) | trigger: "Runs on every push/PR via pipeline-01 (CI)"
  - test-admin-login :: Admin credential login test suite | kind: test | summary: "Bundles TEST-AUTH-015, 026, 036 — correct/incorrect credentials, no-lockout confirmation, contract conformance, frontend/a11y." | spec: [Integration Tests](test-specification.md#integration-tests) | trigger: "Runs on every push/PR via pipeline-01 (CI)"
  - test-admin-recovery :: Admin password recovery test suite | kind: test | summary: "Bundles TEST-AUTH-016 through 018, 027, 028, 032, 036 — request/confirm, single-use enforcement, enumeration resistance, e2e journey, frontend/a11y." | spec: [Integration Tests](test-specification.md#integration-tests) | trigger: "Runs on every push/PR via pipeline-01 (CI)"
  - test-authorization :: Session and authorization test suite | kind: test | summary: "Bundles TEST-AUTH-019 through 021, 029, 033, 037, 040 — revocation, role-gating, logout scope, session-expired interrupt, generic error state, and the sub-100ms overhead budget." | spec: [Integration Tests](test-specification.md#integration-tests) | trigger: "Runs on every push/PR via pipeline-01 (CI); TEST-AUTH-040 also runs on a schedule against PREVIEW"
  - test-security-hardening :: Security-property test suite | kind: test | summary: "Bundles TEST-AUTH-001 through 003, 014, 038, 042 — hashing round-trips, constant-time comparison (code review, not runtime), the admin singleton, no-secrets-in-logs, and admin-login IP rate limiting." | spec: [Unit Tests](test-specification.md#unit-tests) | trigger: "Runs on every push/PR via pipeline-01 (CI); TEST-AUTH-003 runs as a code-review checklist item, not an automated suite"
  - test-accessibility :: Cross-screen accessibility test suite | kind: test | summary: "Bundles TEST-AUTH-034 through 037 — axe-core + Playwright against all 12 DS-AUTH screens, keyboard-only completion, and aria-live error announcement." | spec: [Frontend and Accessibility Tests](test-specification.md#frontend-and-accessibility-tests) | trigger: "Runs on every push/PR via pipeline-01 (CI)"
  - test-otp-latency :: OTP delivery latency test | kind: test | summary: "TEST-AUTH-041 — confirms the 60-second OTP delivery budget (system.md's Module Quality Budgets) once EMAIL_PROVIDER is wired up in a real environment; cannot run against a fake email double." | spec: [Edge, Failure, Security, Performance, and Recovery Tests](test-specification.md#edge-failure-security-performance-and-recovery-tests) | trigger: "Runs against PREVIEW only, not CI's fake-email LOCAL run"
test-otp-flow -> ss-auth-001 | relation: proves
test-otp-flow -> interface-auth-identity | relation: proves
test-otp-flow -> inv-auth-single-use-tokens | relation: proves
test-agent-lifecycle -> ss-auth-002 | relation: proves
test-agent-lifecycle -> interface-auth-agent-mgmt | relation: proves
test-agent-lifecycle -> inv-auth-audit-atomicity | relation: proves
test-admin-login -> ss-auth-003 | relation: proves
test-admin-login -> interface-auth-admin-login | relation: proves
test-admin-recovery -> ss-auth-004 | relation: proves
test-admin-recovery -> interface-auth-admin-login | relation: proves
test-admin-recovery -> inv-auth-single-use-tokens | relation: proves
test-authorization -> ss-auth-005 | relation: proves
test-security-hardening -> inv-auth-singleton-admin | relation: proves
test-security-hardening -> inv-auth-no-secrets-in-logs | relation: proves
test-accessibility -> metric-a11y-contrast | relation: proves
test-accessibility -> metric-otp-completion | relation: watches
test-otp-latency -> risk-auth-email-outage | relation: watches
```

</details>

> [!note]
> This graph carries 23 nodes across 6 groups — thin relative to the 30-60 ideal, and worth explaining rather than padding: three groups (`Flows`, `Interfaces`) and most of a fourth (`Invariants`, `Risks`, `Metrics`) are pure reuse by ID from `solution.md`/`system.md`/`trd.md`/`experience-design.md` — this stage proves what earlier stages promised, it does not invent new promises. The graph deliberately does **not** carry all 42 `TEST-AUTH-NNN` case IDs as individual nodes; per the graph-vs-schema boundary this project's TRD stage already established, the 8 `Tests` nodes are representative suites, and the full 1:1 case-level detail lives in the tables below, which every `Tests` node's `spec:` link points into. `SY-AUTH-NNN` and `TRD-AUTH-NNN` requirements are not re-promoted as their own graph nodes either — they were never promoted as nodes in `system.md`/`trd.md` in the first place (they exist as table rows and inline tags, not `items`-fence entries), so re-inventing them here as a parallel `Requirement` layer would duplicate, not deepen, what the [Traceability](#traceability) table already does more precisely.

## Scope, Risks, and Test Environments

This spec designs the evidence plan for all five `SS-AUTH-NNN` flows, all fourteen `SY-AUTH-NNN` behaviors, all fifteen `TRD-AUTH-NNN` technical requirements, and all twelve `DS-AUTH-NNN` screens — nothing in CATALOG or ORDERS (AUTH depends on neither), no implementation code (stage 50d), no new business decisions (a gap found here flows back through `/daksh change AUTH`, the same discipline [CR-002](change-records/CR-002.md) and [CR-003](change-records/CR-003.md) already used this module).

**Test environments**, per [system-architecture.md's Deployment Architecture](../../system-architecture.md#deployment-architecture): unit and integration tests run against [env-01](../../system-architecture.md#deployment-architecture) `LOCAL` (Docker Compose Postgres) inside [pipeline-01](../../system-architecture.md#deployment-architecture) `CI` on every push/PR; end-to-end and the OTP-latency test run against [env-02](../../system-architecture.md#deployment-architecture) `PREVIEW` once `oq-27` (hosting) resolves and a real deployment exists there — until then, `TEST-AUTH-030` through `TEST-AUTH-033` and `TEST-AUTH-041` are designed but cannot execute against a real `PREVIEW`, and run against a locally-hosted equivalent instead (flagged in [Open Questions](#open-questions)).

**Boundaries — real, fake, or contract-tested, and why:**
- **DATABASE (Postgres): real**, not mocked, in every unit/integration/contract/e2e test — a disposable per-test-run schema created fresh from the [5a](trd.md#5a-persistence-constraints) DDL. AUTH's correctness rests on real constraint behavior (uniqueness, the singleton `CHECK`, transaction atomicity) that a mock would trivially "pass" without proving anything.
- **EMAIL_PROVIDER (Resend): fake** everywhere except `TEST-AUTH-041` — a double that records "would have sent to X" without a real network call, since real email delivery in CI is slow, costly, and not what most of these tests are proving. `TEST-AUTH-041` is the one deliberate exception, run only against `PREVIEW` with the real provider.
- **OBJECT_STORAGE (AWS S3): fake** — AUTH's own scope is a URL string field (`photo_url`); it never itself talks to S3 (the frontend's upload flow is out of AUTH's scope), so no test here needs a real bucket.
- **CATALOG, ORDERS: not applicable** — AUTH has no dependency on either (roadmap's dependency graph), so no test here calls into them; the reverse (ORDERS reading AUTH's agent status) is ORDERS' own future Test Specification's concern.
- **The in-process authorization dependency (`get_current_user()`/`require_role()`): real**, exercised directly — it's core AUTH logic, not an external boundary to fake.

**Risks this spec is aware of and does not try to eliminate:** [risk-auth-email-outage](#) (watched, not provable in CI — see `TEST-AUTH-039`); risk-auth-jwt-secret-leak ([trd.md](trd.md#10a-deployment-and-operations)) (an operational/configuration risk, not something a test can exercise — mitigated by process, per [10a](trd.md#10a-deployment-and-operations), not tested here).

## Traceability

Every requirement below maps to at least one Test ID; a requirement with no row is a gap that blocks this stage's approval, per [stages/50b-test-specification/CONTEXT.md](.)'s own rule.

| Requirement | Test ID(s) |
|---|---|
| [SS-AUTH-001](solution.md#business-flow-inventory) | TEST-AUTH-007, 008, 009, 010, 011, 022, 023, 030, 034 |
| [SS-AUTH-002](solution.md#business-flow-inventory) | TEST-AUTH-012, 013, 024, 025, 031, 035 |
| [SS-AUTH-003](solution.md#business-flow-inventory) | TEST-AUTH-015, 026, 036 |
| [SS-AUTH-004](solution.md#business-flow-inventory) | TEST-AUTH-016, 017, 018, 027, 028, 032, 036 |
| [SS-AUTH-005](solution.md#business-flow-inventory) | TEST-AUTH-019, 020, 021, 029, 033, 037, 040 |
| [SY-AUTH-001](system.md#testable-behaviors) | TEST-AUTH-007, 010, 022 |
| [SY-AUTH-002](system.md#testable-behaviors) | TEST-AUTH-008, 023 |
| [SY-AUTH-003](system.md#testable-behaviors) | TEST-AUTH-009, 023 |
| [SY-AUTH-004](system.md#testable-behaviors) | TEST-AUTH-011 |
| [SY-AUTH-005](system.md#testable-behaviors) | TEST-AUTH-012, 024 |
| [SY-AUTH-006](system.md#testable-behaviors) | TEST-AUTH-013 |
| [SY-AUTH-007](system.md#testable-behaviors) | TEST-AUTH-013 |
| [SY-AUTH-008](system.md#testable-behaviors) | TEST-AUTH-013, 020 |
| [SY-AUTH-009](system.md#testable-behaviors) | TEST-AUTH-015, 026 |
| [SY-AUTH-010](system.md#testable-behaviors) | TEST-AUTH-015, 026 |
| [SY-AUTH-011](system.md#testable-behaviors) | TEST-AUTH-016, 027 |
| [SY-AUTH-012](system.md#testable-behaviors) | TEST-AUTH-017, 018, 028 |
| [SY-AUTH-013](system.md#testable-behaviors) | TEST-AUTH-019, 040 |
| [SY-AUTH-014](system.md#testable-behaviors) | TEST-AUTH-020 |
| TRD-AUTH-001 ([trd.md](trd.md#data-model)) | TEST-AUTH-014 |
| TRD-AUTH-002 ([trd.md](trd.md#security-design)) | TEST-AUTH-001, 015 |
| TRD-AUTH-003 ([trd.md](trd.md#security-design)) | TEST-AUTH-002 |
| TRD-AUTH-004 ([trd.md](trd.md#security-design)) | TEST-AUTH-019 |
| TRD-AUTH-005 ([trd.md](trd.md#api-contracts)) | TEST-AUTH-010 |
| TRD-AUTH-006 ([trd.md](trd.md#api-contracts)) | TEST-AUTH-042 |
| TRD-AUTH-007 ([trd.md](trd.md#5b-state-machines)) | TEST-AUTH-007, 016 |
| TRD-AUTH-008 ([trd.md](trd.md#5b-state-machines)) | TEST-AUTH-018 |
| TRD-AUTH-009 ([trd.md](trd.md#api-contracts)) | TEST-AUTH-009 |
| TRD-AUTH-010 ([trd.md](trd.md#api-contracts)) | TEST-AUTH-027 |
| TRD-AUTH-011 ([trd.md](trd.md#5b-state-machines)) | TEST-AUTH-013 |
| TRD-AUTH-012 ([trd.md](trd.md#security-design)) | TEST-AUTH-038 |
| TRD-AUTH-013 ([trd.md](trd.md#api-contracts)) | TEST-AUTH-021, 029 |
| TRD-AUTH-014 ([trd.md](trd.md#api-contracts)) | TEST-AUTH-012, 024 |
| TRD-AUTH-015 ([trd.md](trd.md#security-design)) | TEST-AUTH-003 |
| [DS-AUTH-001](experience-design.md#4c-design-execution)–[003](experience-design.md#4c-design-execution) | TEST-AUTH-034 |
| [DS-AUTH-004](experience-design.md#4c-design-execution)–[006](experience-design.md#4c-design-execution) | TEST-AUTH-035 |
| [DS-AUTH-007](experience-design.md#4c-design-execution) | TEST-AUTH-036 |
| [DS-AUTH-008](experience-design.md#4c-design-execution)–[010](experience-design.md#4c-design-execution) | TEST-AUTH-036 |
| [DS-AUTH-011](experience-design.md#4c-design-execution) | TEST-AUTH-033, 037 |
| [DS-AUTH-012](experience-design.md#4c-design-execution) | TEST-AUTH-037 |

## Unit Tests

Pure functions, no database, no network — fastest tier, run first in `pipeline-01`.

| ID | Preconditions | Data | Steps | Expected Result | Layer | Owner | Automation |
|---|---|---|---|---|---|---|---|
| TEST-AUTH-001 | None | A representative 12+ char password string | Hash with Argon2id, then verify against the same plaintext; then verify against a wrong plaintext | Correct plaintext verifies true; wrong plaintext verifies false; the stored hash is never the plaintext itself | Unit | PTL | Automated — pytest |
| TEST-AUTH-002 | None | A 6-digit code string, a reset-token string | HMAC-SHA256-hash each with the pepper, then verify a correct and an incorrect candidate against each hash | Correct candidate verifies true; incorrect verifies false | Unit | PTL | Automated — pytest |
| TEST-AUTH-003 | Source code available | The hash-comparison call site(s) in the OTP/reset-token verify path | Inspect the implementation | Comparison uses `hmac.compare_digest`, never `==` or `is` | Unit (static) | PTL | Manual — code-review checklist item, not a runtime test (per [decision-78](trd.md#security-design)'s own note that this is a code-inspection property) |
| TEST-AUTH-004 | None | A `{sub, role, jti}` claim set | Encode a JWT with PyJWT/HS256, then decode it | Decoded claims exactly match the input; a token signed with a different secret fails to decode | Unit | PTL | Automated — pytest |
| TEST-AUTH-005 | None | Passwords of length 11 and 12 | Run the password-length validator against each | 11-char password rejected; 12-char password accepted (no character-class check applied, per [decision-81](trd.md#api-contracts)) | Unit | PTL | Automated — pytest |
| TEST-AUTH-006 | None | An `otp/request` payload missing the `role` field | Validate against the Pydantic request schema | Validation fails with a field-required error on `role` (per [CR-002](change-records/CR-002.md)) | Unit | PTL | Automated — pytest |

## Integration Tests

Real Postgres (disposable per-run schema), fake `EMAIL_PROVIDER`, real service-layer functions.

| ID | Preconditions | Data | Steps | Expected Result | Layer | Owner | Automation |
|---|---|---|---|---|---|---|---|
| TEST-AUTH-007 | Empty `auth_otp_codes` for the test email+role | `email="a@x.com", role="end_user"` | Request an OTP; request a second OTP for the same email+role before the first is consumed | Two rows exist; only the second is valid on verify — the first no longer verifies (supersession, [decision-74](trd.md#business-rules-and-validation)) | Integration | PTL | Automated — pytest + test DB |
| TEST-AUTH-008 | A valid unconsumed OTP row exists | The matching email, role, and correct code | Call verify | A session is issued; an `AuthEndUser` (or `AuthDeliveryAgent`) row exists for that email if none did before | Integration | PTL | Automated — pytest + test DB |
| TEST-AUTH-009 | A valid unconsumed OTP row exists | The matching email/role, an incorrect code, then the correct code | Call verify with the wrong code, then call verify again with the correct code | First call rejected `401`; `consumed_at` still null after the first call; second call succeeds | Integration | PTL | Automated — pytest + test DB |
| TEST-AUTH-010 | None | 6 sequential OTP requests for the same email+role within one hour | Issue all 6 | Requests 1-5 succeed (`202`); request 6 rejected (`429`) | Integration | PTL | Automated — pytest + test DB |
| TEST-AUTH-011 | A successful OTP verify | — | Inspect the resulting `auth_sessions` row | `role` matches the verify request; `expires_at` is `issued_at` + 7 days ([decision-52](solution.md#business-states-decisions-and-recovery)) | Integration | PTL | Automated — pytest + test DB |
| TEST-AUTH-012 | No existing agent row for the email | Valid name/phone/email/photo_url | Register; register again with the same email | First call succeeds `201 pending_approval`; second call rejected `409 email_already_registered` | Integration | PTL | Automated — pytest + test DB |
| TEST-AUTH-013 | A `pending_approval` agent exists | Admin approve, then deactivate, then reactivate, then a separate `pending_approval` agent rejected | Run each Admin action | Each action updates `status` and inserts exactly one `auth_agent_status_log` row in the same transaction; a forced rollback of the status update also rolls back the log row (proves atomicity, not just co-occurrence) | Integration | PTL | Automated — pytest + test DB |
| TEST-AUTH-014 | `auth_admin_accounts` already seeded with its one row | An attempted second INSERT with a different `id` | Run the insert | Rejected by the `CHECK` constraint | Integration | PTL | Automated — pytest + test DB |
| TEST-AUTH-015 | Admin account seeded | Correct credentials; incorrect username; incorrect password | Attempt login with each | Correct succeeds `200`; both incorrect cases return the identical `401 invalid_credentials` shape | Integration | PTL | Automated — pytest + test DB |
| TEST-AUTH-016 | None | A reset request, then a second reset request before the first is used | Issue both | Second request supersedes the first ([decision-74](trd.md#business-rules-and-validation)) — confirming with the first token's value fails | Integration | PTL | Automated — pytest + test DB |
| TEST-AUTH-017 | A valid unused reset token | A new password ≥12 chars | Confirm | `auth_admin_accounts.password_hash` updates and `auth_reset_tokens.used_at` sets, in one transaction | Integration | PTL | Automated — pytest + test DB |
| TEST-AUTH-018 | A reset token already used once | The same token, a different new password | Confirm again | Rejected `410 token_expired_or_used` | Integration | PTL | Automated — pytest + test DB |
| TEST-AUTH-019 | A valid session issued, then explicitly revoked | The same JWT, still cryptographically valid and unexpired | Call the authorization dependency | Rejected — the JWT's own signature/exp check passes, but the `jti` lookup finds `revoked_at` set ([decision-71](trd.md#architecture-overview)) | Integration | PTL | Automated — pytest + test DB |
| TEST-AUTH-020 | A `deactivated` agent with a valid, unexpired session | A call to an agent-only protected route | Call it | Rejected `403` — identity is proven (valid session) but authorization fails (not `approved`) | Integration | PTL | Automated — pytest + test DB |
| TEST-AUTH-021 | Two active sessions for the same agent account (e.g. two devices) | Logout called on session A | Call logout with session A's token | Session A's `jti` is revoked; session B's session remains valid | Integration | PTL | Automated — pytest + test DB |

## Interface and Contract Tests

Real HTTP calls to a running test instance of the FastAPI app; real Postgres; fake `EMAIL_PROVIDER`. Validates the literal request/response shapes in [trd.md's API Contracts](trd.md#api-contracts) against [experience-design.md's Mock Contracts](experience-design.md#mock-contracts-and-data) — the frontend and backend are never allowed to silently drift apart.

| ID | Preconditions | Data | Steps | Expected Result | Layer | Owner | Automation |
|---|---|---|---|---|---|---|---|
| TEST-AUTH-022 | Running test app | Valid and rate-limit-exceeded request bodies | `POST /v1/auth/otp/request` for each case | Response body/status matches the documented `202`/`429` schema exactly (field names, types) | Contract | PTL | Automated — schemathesis/pytest against the OpenAPI-shaped contract |
| TEST-AUTH-023 | Running test app, a live OTP | Correct code, wrong code, expired code | `POST /v1/auth/otp/verify` for each case | Response matches the documented `200`/`401`/`410` schema exactly | Contract | PTL | Automated |
| TEST-AUTH-024 | Running test app | Valid registration body, duplicate-email body | `POST /v1/auth/agent/register` for each case | Response matches the documented `201`/`409` schema exactly | Contract | PTL | Automated |
| TEST-AUTH-025 | Running test app, an authenticated agent session | — | `GET /v1/auth/agent/status` | Response matches the documented `200` schema; unauthenticated call rejected per the shared session-failure shape | Contract | PTL | Automated |
| TEST-AUTH-026 | Running test app | Valid credentials, invalid credentials, rate-limit-exceeded | `POST /v1/auth/admin/login` for each case | Response matches the documented `200`/`401`/`429` schema exactly | Contract | PTL | Automated |
| TEST-AUTH-027 | Running test app | A matching email, a non-matching email | `POST /v1/auth/admin/password-reset/request` for each | Both return identical `202 {}` | Contract | PTL | Automated |
| TEST-AUTH-028 | Running test app, a live reset token | Valid token+password, expired/used token | `POST /v1/auth/admin/password-reset/confirm` for each case | Response matches the documented `200`/`410` schema exactly | Contract | PTL | Automated |
| TEST-AUTH-029 | Running test app, an authenticated session | — | `POST /v1/auth/logout` | `204` returned; a subsequent authenticated call with the same token is rejected | Contract | PTL | Automated |

## End-to-End Tests

Full journeys through a real (or PREVIEW-equivalent) app instance — see [Scope](#scope-risks-and-test-environments) for the current environment caveat.

| ID | Preconditions | Data | Steps | Expected Result | Layer | Owner | Automation |
|---|---|---|---|---|---|---|---|
| TEST-AUTH-030 | Fresh browser session | A new email | Follow [journey-enduser-signin](experience-design.md#user-journeys): [ds-auth-001](experience-design.md#4c-design-execution) → [ds-auth-002](experience-design.md#4c-design-execution) with a valid code | Lands authenticated; a wrong-code detour to [ds-auth-002](experience-design.md#4c-design-execution)'s inline error and a rate-limited detour to [ds-auth-003](experience-design.md#4c-design-execution) are both exercised as sub-cases | E2E | PTL | Automated — Playwright |
| TEST-AUTH-031 | Fresh browser session (agent app), a separate Admin session | A new email/name/phone/photo | Follow [journey-agent-onboarding](experience-design.md#user-journeys): [ds-auth-004](experience-design.md#4c-design-execution) → [ds-auth-005](experience-design.md#4c-design-execution) → Admin approves → agent logs in via OTP → reaches an approved-only view | Full path succeeds; a parallel sub-case with Admin rejecting instead ends at [ds-auth-006](experience-design.md#4c-design-execution)'s `rejected` state | E2E | PTL | Automated — Playwright |
| TEST-AUTH-032 | Fresh browser session (admin app) | The seeded Admin's recovery email | Follow [journey-admin-recovery](experience-design.md#user-journeys): [ds-auth-008](experience-design.md#4c-design-execution) → emailed link → [ds-auth-009](experience-design.md#4c-design-execution) → new password → login | New password works for a fresh login; the used link revisited lands on [ds-auth-010](experience-design.md#4c-design-execution) | E2E | PTL | Automated — Playwright |
| TEST-AUTH-033 | An authenticated session with `expires_at` forced into the past | Any authenticated page | Reload | [ds-auth-011](experience-design.md#4c-design-execution) interrupts; re-authenticating returns to the same page rather than a generic landing page | E2E | PTL | Automated — Playwright |

## Frontend and Accessibility Tests

Per [experience-design.md's Usability and Accessibility Criteria](experience-design.md#usability-and-accessibility-criteria) — every `DS-AUTH-NNN` screen gets at least one entry here.

| ID | Preconditions | Data | Steps | Expected Result | Layer | Owner | Automation |
|---|---|---|---|---|---|---|---|
| TEST-AUTH-034 | Prototype-equivalent build of [ds-auth-001](experience-design.md#4c-design-execution)–[003](experience-design.md#4c-design-execution) rendered | A valid OTP flow | Complete signup using only keyboard (Tab/Enter); paste a full 6-digit code into the OTP input ([decision-64](experience-design.md#4a-primary-design-primitives)) | Flow completes without a mouse; pasted code auto-fills all 6 boxes; axe-core reports zero violations at `metric-a11y-contrast`'s 4.5:1 threshold | Frontend/A11y | PTL | Automated — Playwright + axe-core |
| TEST-AUTH-035 | Build of [ds-auth-004](experience-design.md#4c-design-execution)–[006](experience-design.md#4c-design-execution) rendered | The 4 agent-status values | Render the status screen in each of the 4 states via the prototype's state switcher equivalent, or real backend data | [dc-auth-001](experience-design.md#4c-design-execution) StatusBadge shows the correct color/label for each; keyboard nav reaches every control; axe-core zero violations | Frontend/A11y | PTL | Automated — Playwright + axe-core |
| TEST-AUTH-036 | Build of [ds-auth-007](experience-design.md#4c-design-execution)–[010](experience-design.md#4c-design-execution) rendered | Admin login + recovery flow | Complete both using only keyboard | Flow completes without a mouse; focus order matches visual top-to-bottom reading order; axe-core zero violations | Frontend/A11y | PTL | Automated — Playwright + axe-core |
| TEST-AUTH-037 | Build of [ds-auth-011](experience-design.md#4c-design-execution)/[012](experience-design.md#4c-design-execution) rendered | A forced session-expiry, a forced network failure | Trigger each shared state | Both states are announced via `aria-live` (verified via the accessibility tree, not just visually) rather than conveyed by color alone, per [constraint-a11y](experience-design.md#4a-primary-design-primitives) | Frontend/A11y | PTL | Automated — Playwright + axe-core |

## Edge, Failure, Security, Performance, and Recovery Tests

| ID | Preconditions | Data | Steps | Expected Result | Layer | Owner | Automation |
|---|---|---|---|---|---|---|---|
| TEST-AUTH-038 | Log capture enabled on a test run | A full OTP request/verify cycle and an Admin login/reset cycle | Run both flows; grep the captured log output | No raw OTP digit string, admin password, or reset token value appears anywhere in the logs ([inv-auth-no-secrets-in-logs](#)) | Security | PTL | Automated — pytest, asserts against captured log stream |
| TEST-AUTH-039 | Fake `EMAIL_PROVIDER` configured to raise on send | An OTP request | Request an OTP while the email double fails | The `auth_otp_codes` row is still created (the OTP exists and would validate if the user somehow learned it, e.g. via a support channel); the request still returns `202`; no exception surfaces to the caller | Recovery | PTL | Automated — pytest, proves the fire-and-forget design in [6a](trd.md#6a-idempotency-and-failure-contracts) |
| TEST-AUTH-040 | Seeded session, warmed test DB | 1,000 sequential authorization checks | Measure wall-clock time per check | p99 under 100ms, per [system.md's Module Quality Budgets](system.md#module-quality-budgets) | Performance | PTL | Automated — pytest-benchmark, run against `PREVIEW` on a schedule, not blocking every PR |
| TEST-AUTH-041 | Real `EMAIL_PROVIDER` (Resend), `PREVIEW` environment | An OTP request | Request an OTP; measure time to inbox arrival (a test mailbox) | Arrives within 60 seconds under normal conditions, per [system.md's Module Quality Budgets](system.md#module-quality-budgets) | Performance | PTL | Automated — scheduled run against `PREVIEW`, not part of `pipeline-01`'s per-PR run |
| TEST-AUTH-042 | Admin account seeded | 11 login attempts from one IP; 1 login attempt from a second IP, all within 15 minutes | Run both sequences | The one IP's 11th attempt is rejected `429`; the second IP's 1st attempt succeeds/fails on its own merits, unaffected by the first IP's count ([decision-73](trd.md#security-design)) | Security | PTL | Automated — pytest + test DB |

## Setup, Fixtures, Factories, Seeds, Mocks, and Cleanup

- **Database:** a fresh Postgres schema per test run, migrated via Alembic from the [5a](trd.md#5a-persistence-constraints) DDL, including the `auth_admin_accounts` singleton seed migration — never a shared, persistent test database, to keep tests independent and order-agnostic.
- **Factories:** one factory per entity (`AuthEndUserFactory`, `AuthDeliveryAgentFactory`, `AuthAdminAccountFactory` — used only for the one singleton seed, not per-test creation — `AuthOtpCodeFactory`, `AuthSessionFactory`, `AuthResetTokenFactory`) producing valid rows with sensible defaults, overridable per test.
- **EMAIL_PROVIDER double:** a recording fake implementing the same interface the real Resend client would, capturing `(to, subject, body)` tuples for assertion, used by every test except `TEST-AUTH-039` (which needs it to raise) and `TEST-AUTH-041` (which needs the real thing).
- **Time control:** tests exercising expiry (`TEST-AUTH-009`, `018`, `033`) freeze or advance a mockable clock rather than sleeping in real time.
- **Cleanup:** the per-run schema is dropped after the run; no manual cleanup step exists or is needed.

## Coverage Targets and Evidence Location

- 100% of `SS-AUTH-NNN`, `SY-AUTH-NNN`, `TRD-AUTH-NNN`, and `DS-AUTH-NNN` requirements have at least one mapped Test ID — see [Traceability](#traceability); this is a gate, not an aspiration.
- `app/auth` line coverage target: 90%+, enforced in [pipeline-01](../../system-architecture.md#deployment-architecture) `CI` once implementation exists (stage 50d) — a target recorded here for the implementer to build against, not yet measured.
- Evidence location: CI test reports and coverage artifacts attach to each `pipeline-01` run in GitHub Actions; no separate test-evidence store exists at this scale.

## Open Questions

None outstanding for the test design itself. Two execution-timing notes, not design gaps:

- `TEST-AUTH-030` through `TEST-AUTH-033` and `TEST-AUTH-041` need a real `PREVIEW` deployment to run as designed; until `oq-27` (hosting, system-architecture.md) resolves, they run against a locally-hosted equivalent instead — the test design doesn't change, only where it executes.
- `TEST-AUTH-040`'s performance budget is measured against `PREVIEW`, not `pipeline-01`'s per-PR run, since a meaningful p99 needs load closer to real conditions than a CI runner reliably provides — this was a judgment call made here, not escalated, since it doesn't change any approved decision.

## Approval

Approved by: Bhargav
Role:        PTL
Date:        2026-09-04
Hash:        7559335c6f24…
