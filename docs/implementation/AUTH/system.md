---
daksh:
  type: system-spec
  subtype: null
  stage: "30d"
  module: AUTH
---

# AUTH System

[AUTH's Solution spec](solution.md) named five business flows and explicitly deferred three things to this stage: the exact Delivery Agent state machine, concrete validation rules, and the shape of a session. This document answers all three, plus two more the Solution spec didn't anticipate needing: who owns a saved delivery address (not AUTH — see [Scope and Solution Lineage](#scope-and-solution-lineage)), and how ORDERS learns an agent was deactivated without AUTH ever calling into ORDERS (it doesn't need to — see [Logical Interfaces](#logical-interfaces-and-data-flow)). Everything here stays logical: no schemas, no libraries, no code — stage 50a (TRD) picks the hashing algorithm, the JWT library, the exact table layout.

<details>
<summary>Graph: What must AUTH do after each action, and what does it hold to make that possible?</summary>

```items
---
id: 30d-auth-system-cognition
title: AUTH System — Behavior and Data
default_open_depth: 1
default_color_by: kind
color_palette_source: .daksh/color-palette.json
width: 95vw
---
id: 30d-auth-system-cognition
title: AUTH System — Behavior and Data
Components:
  - component-04 :: CATALOG_SERVICE | kind: component | summary: "Owns items, categories, stock — calls AUTH in-process to resolve who's making an admin-only catalog write." | spec: [Logical Interfaces](system.md#logical-interfaces-and-data-flow) | boundary: "Consumes AUTH's authorization check; produces nothing AUTH depends on."
  - component-05 :: ORDERS_SERVICE | kind: component | summary: "Owns cart, checkout, order lifecycle — calls AUTH in-process to resolve identity, and reads Delivery Agent status to flag orders whose agent was deactivated." | spec: [Logical Interfaces](system.md#logical-interfaces-and-data-flow) | boundary: "Consumes AUTH's authorization check and agent-status data; produces nothing AUTH depends on."
  - component-06 :: AUTH_SERVICE | kind: component | summary: "Owns identity, OTP, sessions, and the agent approval/deactivation gate for all three roles." | spec: [Testable Behaviors](system.md#testable-behaviors) | boundary: "Produces the identity/agent-management/admin-login interfaces and the internal authorization check every other module calls."
StateMachines:
  - sm-auth-agent-status :: Delivery Agent status lifecycle | kind: statemachine | summary: "The canonical 4-state lifecycle a Delivery Agent record moves through, fixed in business-requirements.md's Domain Vocabulary (CR-001)." | spec: [State Machines](system.md#state-machines) | entity: "DeliveryAgent" | states: "pending_approval, approved, deactivated, rejected" | initial_state: "pending_approval" | terminal_states: "rejected" | transitions: "pending_approval->approved (admin approves), pending_approval->rejected (admin rejects), approved->deactivated (admin deactivates), deactivated->approved (admin reactivates, decision-55)" | invariants_per_state: "only approved agents can receive new order assignments (enforced by SY-AUTH-014, not by this state machine alone)"
  - sm-auth-session :: Session lifecycle | kind: statemachine | summary: "A verified login's session, valid for 7 days (decision-52) unless explicitly ended sooner." | spec: [State Machines](system.md#state-machines) | entity: "Session" | states: "active, expired, revoked" | initial_state: "active" | terminal_states: "expired, revoked" | transitions: "active->expired (7 days elapse), active->revoked (explicit logout)" | invariants_per_state: "an expired or revoked session is rejected by SY-AUTH-013 exactly like a session that never existed"
  - sm-auth-reset-token :: Password reset token lifecycle | kind: statemachine | summary: "The one-time link Admin's password recovery email carries." | spec: [State Machines](system.md#state-machines) | entity: "PasswordResetToken" | states: "unused, used, expired" | initial_state: "unused" | terminal_states: "used, expired" | transitions: "unused->used (link followed and new password set), unused->expired (time elapses unused)" | invariants_per_state: "a used or expired token can never move to unused again (decision-56)"
DataModels:
  - dm-enduser :: EndUser identity record | kind: datamodel | summary: "An End User's account: email, verified status, and the multiple saved addresses decision-30 (business-requirements.md) already fixed — addresses themselves are ORDERS' data, not AUTH's (see Scope)." | spec: [Logical Data, Ownership, and Invariants](system.md#logical-data-ownership-and-invariants) | shape: "identity fields only — email, account-creation timestamp; no order or address fields"
  - dm-deliveryagent :: Delivery Agent identity record | kind: datamodel | summary: "An agent's account plus its canonical status (sm-auth-agent-status)." | spec: [Logical Data, Ownership, and Invariants](system.md#logical-data-ownership-and-invariants) | shape: "identity fields, contact fields Admin needs to vet them, plus the current status value"
  - dm-adminaccount :: Admin account record | kind: datamodel | summary: "The single shared Admin credential and its registered recovery email — a singleton in Phase 1 (decision-22, vision.md)." | spec: [Logical Data, Ownership, and Invariants](system.md#logical-data-ownership-and-invariants) | shape: "username, hashed password, recovery email — exactly one row exists"
  - dm-otpcode :: OTP code | kind: datamodel | summary: "A short-lived one-time code, hashed at rest, tied to one email and one role (CR-002) — not just one purpose (signup/login), since the same email can hold both an End User and a Delivery Agent identity (decision-49, solution.md)." | spec: [Business Rules and Validation](system.md#business-rules-and-validation) | shape: "hashed code, associated email, role (end_user or delivery_agent, CR-002), issued-at timestamp, expiry (10 minutes, decision-28), consumed flag"
  - dm-session :: Session/token | kind: datamodel | summary: "The artifact issued after any successful login, carrying the resolved role." | spec: [Logical Interfaces](system.md#logical-interfaces-and-data-flow) | shape: "opaque token, resolved role claim, issued-at, expiry (7 days, decision-52)"
  - dm-resettoken :: Password reset token | kind: datamodel | summary: "A short-lived, single-use link token for Admin password recovery." | spec: [Business Rules and Validation](system.md#business-rules-and-validation) | shape: "hashed token, issued-at, expiry, used flag"
  - dm-agent-status-log :: Agent status change log | kind: datamodel | summary: "An append-only history of every Delivery Agent status transition — who changed it and when (decision-60), persisting what event-agent-status-changed marks." | spec: [Logical Data, Ownership, and Invariants](system.md#logical-data-ownership-and-invariants) | shape: "agent identifier, old status, new status, changed-by (Admin), timestamp — one row per transition, never updated or deleted"
Interfaces:
  - interface-auth-identity :: Identity & OTP interface | kind: interface | summary: "End User and Delivery Agent signup/login — request an OTP, verify it, get a session. Carries an explicit role discriminator (CR-002) since one email can resolve to either identity." | spec: [Logical Interfaces](system.md#logical-interfaces-and-data-flow) | shape: "email+role in -> code-sent ack out; email+code+role in -> session out or rejection" | version: "v1" | compatibility: additive
  - interface-auth-agent-mgmt :: Agent registration & lifecycle interface | kind: interface | summary: "Prospective agent registration, and Admin's approve/reject/deactivate/reactivate actions." | spec: [Logical Interfaces](system.md#logical-interfaces-and-data-flow) | shape: "registration details in -> pending record out; admin decision in -> updated agent status out" | version: "v1" | compatibility: additive
  - interface-auth-admin-login :: Admin login & recovery interface | kind: interface | summary: "Admin's password login and password-reset request/confirm." | spec: [Logical Interfaces](system.md#logical-interfaces-and-data-flow) | shape: "credentials in -> session out or rejection; reset request in -> email sent; new password + valid token in -> password updated" | version: "v1" | compatibility: additive
Decisions:
  - decision-55 :: A deactivated agent can be reactivated to approved | kind: decision | summary: "Deactivation is not permanent — Admin can move a `deactivated` agent back to `approved` directly, without them re-registering from scratch." | spec: [State Machines](system.md#state-machines) | alternatives: "Make deactivation permanent, like rejected — simpler state machine, but forces a legitimate returning agent (e.g. back from a break) to re-register and be re-vetted from zero, for no clear benefit over just letting Admin reactivate them directly." | reversal_trigger: "Reactivation is abused to route around a deactivation that should have stuck (e.g. Admin reactivates someone who was cut off for misconduct) — would need an approval step on reactivation itself."
  - decision-56 :: OTP codes and reset tokens are single-use, even within their validity window | kind: decision | summary: "Once an OTP code or password-reset token is successfully used, it's immediately invalidated — it cannot be reused again before its natural expiry." | spec: [State Machines](system.md#state-machines) | alternatives: "Allow reuse until natural expiry — marginally more convenient if a page reloads mid-flow, but weakens security for a negligible convenience gain, and contradicts BRD NFR-3's rate-limiting intent." | reversal_trigger: "A real UX problem surfaces from single-use tokens (e.g. a common double-submit pattern breaks a legitimate attempt)."
  - decision-57 :: Delivery Agent records are never hard-deleted | kind: decision | summary: "A `rejected` or `deactivated` agent's record stays in the system permanently — states are marks on a permanent record, not a substitute for deletion." | spec: [Logical Data, Ownership, and Invariants](system.md#logical-data-ownership-and-invariants) | alternatives: "Hard-delete rejected agent records — rejected; erases the history [oq-45](#) asks about, and complicates decision-49's cross-role email-reuse check (would need to know a deleted record existed)." | reversal_trigger: "A real data-minimization or privacy requirement demands deletion — not raised in this project so far."
  - decision-58 :: Rejected/deactivated agent records are retained indefinitely, no automatic purge | kind: decision | summary: "There is no scheduled cleanup job for old agent records — they stay as long as the system does." | spec: [Logical Data, Ownership, and Invariants](system.md#logical-data-ownership-and-invariants) | alternatives: "Purge after a fixed window (e.g. 1-2 years) — adds a scheduled job with no stated storage-cost or compliance pressure to justify building it yet." | reversal_trigger: "A real data-minimization or storage-cost concern surfaces."
  - decision-59 :: No End User self-service account deletion in Phase 1 | kind: decision | summary: "There is no \"delete my account\" capability for End User — Admin would handle a deletion request manually if one ever came in." | spec: [Logical Data, Ownership, and Invariants](system.md#logical-data-ownership-and-invariants) | alternatives: "Build self-service deletion now — real feature (what happens to past orders/addresses) with no stated demand yet to justify the design and build cost." | reversal_trigger: "A real, recurring deletion request pattern emerges from actual End Users."
  - decision-60 :: Agent status changes are logged with who and when | kind: decision | summary: "Every Delivery Agent status transition is recorded in an append-only log ([dm-agent-status-log](#)), not just reflected in the current status field — accountability for a deactivation decision matters enough to justify the modest extra data." | spec: [Logical Data, Ownership, and Invariants](system.md#logical-data-ownership-and-invariants) | alternatives: "Current-status-only, no history — simpler data model, but leaves no record to check if a deactivation is ever disputed." | reversal_trigger: "The log itself is never once consulted after real usage, suggesting the accountability concern wasn't as real as assumed."
  - decision-67 :: interface-auth-identity carries an explicit role field, not separate per-role endpoints | kind: decision | summary: "OTP request/verify take a role field (`end_user`/`delivery_agent`) rather than exposing `/v1/auth/otp/request/end-user` and a separate agent variant — one shared route pair, disambiguated by a field, matching how the rest of this interface already models both roles identically (CR-002)." | spec: [Logical Interfaces](system.md#logical-interfaces-and-data-flow) | alternatives: "Separate endpoints per role — makes the frontend's app-scoped intent explicit in the URL itself, but duplicates route/handler wiring for a mechanism that's otherwise byte-for-byte identical between roles, and interface-auth-identity was already designed as one shared surface." | reversal_trigger: "The two roles' OTP handling diverges enough in practice (different validation, different rate-limit policy) that sharing one endpoint starts costing more than a field ever saved."
OpenQuestions:
  - oq-43 :: Record retention for rejected/deactivated agents | kind: openquestion | summary: "How long are rejected/deactivated agent records retained? — resolved, see decision-58." | spec: [AUTH System Decisions](system.md#auth-system-decisions)
  - oq-44 :: End User self-service account deletion | kind: openquestion | summary: "Should End User have self-service account deletion? — resolved, see decision-59." | spec: [AUTH System Decisions](system.md#auth-system-decisions)
  - oq-45 :: Audit trail for agent status changes | kind: openquestion | summary: "Is an audit trail needed for agent status changes? — resolved, see decision-60." | spec: [AUTH System Decisions](system.md#auth-system-decisions)
component-06 -> interface-auth-identity | relation: produces
component-06 -> interface-auth-agent-mgmt | relation: produces
component-06 -> interface-auth-admin-login | relation: produces
decision-55 -> sm-auth-agent-status | relation: governs
decision-56 -> sm-auth-reset-token | relation: governs
decision-57 -> dm-deliveryagent | relation: governs
decision-58 -> dm-deliveryagent | relation: governs
decision-59 -> dm-enduser | relation: governs
decision-60 -> dm-agent-status-log | relation: governs
decision-67 -> interface-auth-identity | relation: governs
decision-58 -> oq-43 | relation: decides
decision-59 -> oq-44 | relation: decides
decision-60 -> oq-45 | relation: decides
component-06 -> event-agent-status-changed | relation: produces
event-agent-status-changed :: Agent status changed | kind: event | summary: "Fires whenever a Delivery Agent's status transitions (approve/reject/deactivate/reactivate) — read by ORDERS to flag in-flight orders (decision-54, solution.md), and persisted permanently in dm-agent-status-log (decision-60), not pushed anywhere." | spec: [Logical Interfaces](system.md#logical-interfaces-and-data-flow) | payload_shape: "agent identifier, old status, new status, timestamp"
```

</details>

> [!note]
> This graph carries 27 nodes across 6 groups, plus `event-agent-status-changed` as a single ungrouped root item — one genuine Event, not padded into a fake group of three. Consistent with how thin `system-architecture.md`, `implementation-roadmap.md`, and AUTH's own `solution.md` all ran: a single module's System spec has less raw material than a project-wide document. `Components` are reused from `system-architecture.md` by the same IDs — this stage deepens what they do, it doesn't invent new ones. All 3 original open questions resolved into `decision-58` through `decision-60` in a follow-up round. `decision-67` was added later via [CR-002](change-records/CR-002.md), once drafting AUTH's TRD surfaced a real payload-shape gap in how `interface-auth-identity` disambiguates which role an OTP request is for.

## Scope and Solution Lineage

Every [SY-AUTH-NNN](#testable-behaviors) below traces to the [SS-AUTH-NNN](solution.md#business-flow-inventory) it makes testable: SY-001–004 to [SS-AUTH-001](solution.md#business-flow-inventory), SY-005–008 to [SS-AUTH-002](solution.md#business-flow-inventory), SY-009–010 to [SS-AUTH-003](solution.md#business-flow-inventory), SY-011–012 to [SS-AUTH-004](solution.md#business-flow-inventory), SY-013–014 to [SS-AUTH-005](solution.md#business-flow-inventory).

One scope clarification the Solution spec left implicit: **AUTH does not own delivery addresses.** [business-requirements.md's data model](../../business-requirements.md#data-models) shows an End User with multiple saved addresses, and nothing upstream said which module owns that entity. Addresses are checkout/delivery data — used only at order time — not identity data, so they belong to ORDERS, not AUTH. [dm-enduser](#) above is deliberately identity-only; ORDERS' own future System spec owns the address entity.

## Testable Behaviors

| SY | Behavior | Traces to |
|---|---|---|
| SY-AUTH-001 | System sends an OTP to a valid email on request, honoring the 5-per-hour rate limit (decision-53, business-requirements.md). | SS-AUTH-001 |
| SY-AUTH-002 | System verifies a correct, unexpired OTP and creates/logs into an account tied to that email and role. | SS-AUTH-001 |
| SY-AUTH-003 | System rejects an incorrect or expired OTP and allows a resend after the 60-second cooldown. | SS-AUTH-001 |
| SY-AUTH-004 | System issues a 7-day session (decision-52) on successful OTP verification. | SS-AUTH-001 |
| SY-AUTH-005 | System accepts a prospective agent's registration and creates the record in `pending_approval`. | SS-AUTH-002 |
| SY-AUTH-006 | System lets Admin move a `pending_approval` or `deactivated` agent to `approved`. | SS-AUTH-002 |
| SY-AUTH-007 | System lets Admin move a `pending_approval` agent to `rejected` (terminal). | SS-AUTH-002 |
| SY-AUTH-008 | System lets Admin move an `approved` agent to `deactivated`, immediately preventing new assignments to them (enforced by SY-AUTH-014). | SS-AUTH-002 |
| SY-AUTH-009 | System verifies Admin's username/password and issues a 7-day session, or rejects. | SS-AUTH-003 |
| SY-AUTH-010 | System rejects invalid Admin credentials with no account lockout (decision-51, solution.md). | SS-AUTH-003 |
| SY-AUTH-011 | System sends a single-use password-reset link to Admin's registered recovery email on request. | SS-AUTH-004 |
| SY-AUTH-012 | System accepts a new password via an unused, unexpired reset link, then invalidates that link (decision-56). | SS-AUTH-004 |
| SY-AUTH-013 | System resolves an incoming request's session to a role, or rejects it if the session is missing, expired, or revoked. | SS-AUTH-005 |
| SY-AUTH-014 | System rejects an agent-only action from a Delivery Agent whose current status isn't `approved` — even with a valid, unexpired session. | SS-AUTH-005 |

## Business Rules and Validation

- An OTP code ([dm-otpcode](#)) is valid for exactly 10 minutes and can be resent after a 60-second cooldown (decision-28, business-requirements.md) — both enforced server-side, not left to client trust.
- OTP requests are capped at 5 per hour per email (decision-53, solution.md) — enforced at request time (SY-AUTH-001), not reconciled after the fact.
- OTP codes and reset tokens ([dm-otpcode](#), [dm-resettoken](#)) are stored hashed, never in plaintext, and are single-use (decision-56) — consuming one immediately invalidates it regardless of remaining time-to-expiry.
- [dm-adminaccount](#) is a singleton — exactly one record exists in Phase 1 (decision-22, vision.md); no business rule here accommodates a second Admin.
- A [DeliveryAgent](#) can only occupy one [sm-auth-agent-status](#) state at a time; there is no "partial approval."

## State Machines

See the graph above for the three closed state lists, initial/terminal states, and guarded transitions ([sm-auth-agent-status](#), [sm-auth-session](#), [sm-auth-reset-token](#)). Two business calls made explicitly at this stage, not left implicit: [decision-55](#) (deactivation is reversible) and [decision-56](#) (reset tokens/OTP codes are single-use, not reusable-until-expiry).

## Logical Data, Ownership, and Invariants

AUTH owns seven data shapes, all described in the graph above: [dm-enduser](#), [dm-deliveryagent](#), [dm-adminaccount](#), [dm-otpcode](#), [dm-session](#), [dm-resettoken](#), and [dm-agent-status-log](#). Ownership invariants:

- Only AUTH reads or writes any of these seven shapes — CATALOG and ORDERS never touch AUTH's tables directly, they call AUTH's interfaces ([system-architecture.md's Module Decomposition](../../system-architecture.md#module-decomposition)).
- [dm-deliveryagent](#) records are never hard-deleted ([decision-57](#)) and are retained indefinitely with no automatic purge ([decision-58](#)) — a `rejected` or `deactivated` record is a permanent mark, not an erasure.
- [dm-enduser](#) explicitly excludes saved addresses (see [Scope and Solution Lineage](#scope-and-solution-lineage)); there is no self-service account deletion in Phase 1 ([decision-59](#)).
- Every transition in [sm-auth-agent-status](#) writes one append-only row to [dm-agent-status-log](#) — who (which Admin) changed it, from what status to what, and when ([decision-60](#)). The log is never updated or deleted, only appended to.

## Logical Interfaces and Data Flow

Three interfaces, all producer AUTH ([component-06](#)), all consumed by whichever frontend view needs them — see the graph for shape/version/compatibility: [interface-auth-identity](#) (End User/Agent signup+login), [interface-auth-agent-mgmt](#) (agent registration and Admin's lifecycle actions), [interface-auth-admin-login](#) (Admin's own login+recovery). All three are additive-compatible v1 — a new field never breaks an existing frontend caller.

**Role disambiguation ([CR-002](change-records/CR-002.md)):** [decision-49](solution.md#business-states-decisions-and-recovery) lets one email hold both an End User and a Delivery Agent identity, so [interface-auth-identity](#) cannot resolve which record an OTP request or verify is for from the email alone. [decision-67](#) resolves this with an explicit `role` field on both legs, rather than separate per-role endpoints — the frontend supplies it without any new screen or UI, since it's implicit in which of the two role-scoped frontend apps is calling ([experience-design.md's Information Architecture](experience-design.md#information-architecture-and-navigation)).

**Failure shape**, in business terms (no HTTP status codes, that's TRD's job): a request with no session, an expired session, or a revoked session is rejected identically — the caller cannot distinguish "never logged in" from "session ran out," which is deliberate (leaking that distinction would let an attacker fingerprint valid-but-expired sessions). A request with a valid session but the wrong role is rejected differently — the caller *can* tell "you're not allowed to do this" from "you're not logged in at all," since that distinction is what lets a frontend redirect to the right login screen.

**In-process contract (no Interface node, per [decision-33](../../system-architecture.md#architecture-decisions)):** [component-04](#) (CATALOG) and [component-05](#) (ORDERS) both call AUTH's authorization check (SY-AUTH-013) directly, in-process, on every protected request — this is [system-architecture.md](../../system-architecture.md#module-interactions-and-versioned-logical-interfaces)'s existing contract, not a new one.

**Cross-module data flow for deactivation (resolves a real risk of breaking the build order):** [decision-54](solution.md#auth-decisions) (solution.md) said deactivating an agent auto-flags their in-flight orders for Admin — but AUTH calling into ORDERS to do that flagging would make AUTH *depend on* ORDERS, contradicting the roadmap's dependency graph (AUTH ships first specifically because it depends on nothing). The resolution: AUTH does not call ORDERS. [event-agent-status-changed](#) is not pushed anywhere — it's a marker of what happened, read passively. ORDERS (which already depends on AUTH, per [roadmap.md](../../implementation-roadmap.md#module-dependency-graph)) is the one that checks an assigned agent's current [sm-auth-agent-status](#) whenever it renders its own order/agent-assignment view, and surfaces the flag itself. The actual flagging behavior belongs in ORDERS' own future System spec (stage 30d:ORDERS) — this document only fixes that the dependency direction stays ORDERS→AUTH, never the reverse.

## Module Quality Budgets

Inherited unchanged from [system-architecture.md](../../system-architecture.md#project-wide-quality-requirements): standard ~2s page-load target, no formal uptime SLA, no load-testing requirement at Phase 1 volume. Tightened for AUTH specifically:

- **OTP delivery latency:** the OTP email should arrive within 60 seconds under normal conditions — a login/signup that makes someone wait minutes for a code defeats the point of choosing email over SMS for cost reasons.
- **Authorization check overhead:** SY-AUTH-013 runs on *every* protected request across CATALOG and ORDERS — its added latency should be negligible (sub-100ms) since it's pure overhead on top of whatever the actual request is doing.
- **Credential/secret storage:** passwords, OTP codes, and reset tokens are all stored hashed (extends BRD NFR-4's password-only statement to cover the other two secrets AUTH holds) — the specific algorithm is stage 50a's choice, not fixed here.

## Verification Obligations

| Behavior / Budget | Verification approach (business terms, not test code) |
|---|---|
| SY-AUTH-001–004 (OTP flow) | Exercise signup and login for both End User and Delivery Agent; confirm rate-limit rejection at the 6th request within an hour; confirm session issuance matches the 7-day lifetime. |
| SY-AUTH-005–008 (agent lifecycle) | Exercise every transition in [sm-auth-agent-status](#), including deactivate→reactivate (decision-55); confirm a `deactivated` agent cannot be assigned new orders. |
| SY-AUTH-009–010 (admin login) | Exercise correct and incorrect Admin credentials; confirm no lockout occurs after repeated failures (decision-51). |
| SY-AUTH-011–012 (admin recovery) | Exercise a full reset cycle; confirm the token cannot be reused after success (decision-56) or after expiry. |
| SY-AUTH-013–014 (authorization) | Exercise a request with no session, an expired session, a revoked session, and a valid session with the wrong role; confirm each is rejected per the failure-shape rule above. |
| OTP delivery latency budget | Measure actual email arrival time under normal load once [EMAIL_PROVIDER](../../system-architecture.md#shared-platform-rules-and-cross-cutting-concerns) (Resend) is wired up in stage 50a. |

Formal test cases with setup/data/expected-result live in stage 50b (Test Specification), not here — this table is the obligation, not the test itself.

## AUTH System Decisions

The 3 open questions this stage's first draft raised were closed in a follow-up round.

1. **Rejected/deactivated agent records are retained indefinitely, no automatic purge** ([decision-58](#)) — no scheduled cleanup job to build. Revisit if a real storage-cost or data-minimization concern surfaces.
2. **No End User self-service account deletion in Phase 1** ([decision-59](#)) — Admin handles a deletion request manually if one ever comes in. Revisit if a real, recurring ask emerges.
3. **Agent status changes are logged with who and when** ([decision-60](#), [dm-agent-status-log](#)) — accountability for a deactivation decision justified the extra data over current-status-only. Revisit if the log is never once consulted in practice.

## Open Questions

None remain open from this System draft — all 3 were resolved in the follow-up above; see [AUTH System Decisions](#auth-system-decisions).

## Approval

Approved by: Bhargav
Role:        PTL
Date:        2026-09-04
Hash:        3a093685deef�

Approved by: Bhargav
Role:        PTL
Date:        2026-09-04
Via:         CR-002
