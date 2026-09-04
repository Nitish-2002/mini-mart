---
daksh:
  type: solution-spec
  subtype: null
  stage: "30c"
  module: AUTH
---

# AUTH Solution

AUTH is the root of Mini Mart's build order ([roadmap.md](../../implementation-roadmap.md#module-dependency-graph)) — the module every other module calls to answer one question: *who is asking, and what are they allowed to do?* This document is the business-level answer to that question for all three roles (Admin, Delivery Agent, End User), traced to the BRD's [UC-001](../../business-requirements.md#uc-001-end-user-creates-an-account), [UC-009](../../business-requirements.md#uc-009-delivery-agent-registers-and-gets-approved), FR-027, and the newly-added FR-029 (CR-001). It stays at business-flow level — no screens (stage 40's job), no schemas or transport (stage 30d/50a's job) — but it does add real business substance the BRD didn't spell out: what happens when identity is ambiguous across roles, how a login differs from a first-time signup, and what "who is asking" actually resolves to for every other module.

<details>
<summary>Graph: What problem does AUTH solve, and how do responsibilities and information move through it?</summary>

```items
---
id: 30c-auth-solution-cognition
title: AUTH Solution — Responsibility Flow
default_open_depth: 1
default_color_by: kind
color_palette_source: .daksh/color-palette.json
width: 95vw
---
id: 30c-auth-solution-cognition
title: AUTH Solution — Responsibility Flow
Users:
  - user-01 :: Admin | kind: user | summary: "Runs the mart's catalog, pricing, and stock, and oversees orders and delivery agents." | spec: [Actors, Needs, Outcomes](solution.md#actors-needs-and-expected-outcomes) | role: "Mart Admin/Owner" | audience: client | user_type: operator | status: placeholder
  - user-02 :: Delivery Agent | kind: user | summary: "Picks up assigned orders and delivers them to end users, collecting cash on delivery." | spec: [Actors, Needs, Outcomes](solution.md#actors-needs-and-expected-outcomes) | role: "Delivery Agent" | audience: client | user_type: practitioner | status: placeholder
  - user-03 :: End User | kind: user | summary: "Browses the catalog, places an order, and pays cash on delivery when it arrives." | spec: [Actors, Needs, Outcomes](solution.md#actors-needs-and-expected-outcomes) | role: "Shopper/Customer" | audience: end_customer | user_type: consumer | status: placeholder
Flows:
  - ss-auth-001 :: Email + OTP identity verification | kind: flow | summary: "The shared mechanism both End User and Delivery Agent use to prove they own an email address — covers first-time signup and every later login identically." | spec: [Business-Flow Inventory](solution.md#business-flow-inventory) | actor: "End User or Delivery Agent" | trigger: "Someone enters an email to sign up or log in" | outcome: "A verified session exists for that email, scoped to whichever role it was entered under"
  - ss-auth-002 :: Delivery Agent registration and approval gate | kind: flow | summary: "A prospective agent submits a registration; they can't act as an agent until admin approves it." | spec: [Business-Flow Inventory](solution.md#business-flow-inventory) | actor: "Delivery Agent, Admin" | trigger: "Prospective agent submits registration details" | outcome: "Agent status is `approved` (can be assigned orders) or `rejected` (cannot)"
  - ss-auth-003 :: Admin credential login | kind: flow | summary: "The single shared Admin account authenticates by username and password, not OTP." | spec: [Business-Flow Inventory](solution.md#business-flow-inventory) | actor: "Admin" | trigger: "Admin enters credentials" | outcome: "A verified Admin session exists, or the attempt is rejected"
  - ss-auth-004 :: Admin password recovery | kind: flow | summary: "If Admin's password is lost, a reset link goes to a pre-registered recovery email." | spec: [Business-Flow Inventory](solution.md#business-flow-inventory) | actor: "Admin" | trigger: "Admin requests a password reset" | outcome: "Admin sets a new password via the emailed link, or the request expires unused"
  - ss-auth-005 :: Session issuance and role-scoped authorization | kind: flow | summary: "Every verified login (ss-auth-001 or ss-auth-003) produces a session that CATALOG and ORDERS use to resolve who's asking and what they're allowed to do — the cross-cutting responsibility the other two modules depend on." | spec: [Integration Intent](solution.md#integration-intent) | actor: "System (invisible to the end user)" | trigger: "A verified login completes, or a protected request arrives at CATALOG/ORDERS" | outcome: "The requesting role is known and enforced, or the request is rejected as unauthenticated/unauthorized"
Decisions:
  - decision-49 :: Same email may hold both an End User and a Delivery Agent identity | kind: decision | summary: "AUTH doesn't enforce cross-role email uniqueness — a person can be a shopper and a delivery agent under the same email, as two separate account records." | spec: [Business States, Decisions, and Recovery](solution.md#business-states-decisions-and-recovery) | alternatives: "Block cross-role reuse, requiring a distinct email per role — rejected; adds a real validation rule with no business reason surfaced yet to justify it." | reversal_trigger: "A real conflict emerges from one person holding both identities (e.g. confusion in notifications, or a fraud pattern) that the simpler model doesn't handle."
  - decision-50 :: OTP is required on every login, no persistent device skip | kind: decision | summary: "There is no \"remember this device\" shortcut in Phase 1 — End User and Delivery Agent verify by OTP every time they log in, not just at first signup." | spec: [Business-Flow Inventory](solution.md#business-flow-inventory) | alternatives: "A longer-lived session or device-trust cookie that skips repeat OTP entry — rejected for Phase 1; adds real complexity (secure device-token storage, revocation) with no evidence yet that repeat-OTP friction is a real problem." | reversal_trigger: "Repeat-login friction becomes a measured drop-off point after launch."
  - decision-51 :: Admin login is password-only, no second factor | kind: decision | summary: "The single Admin account authenticates by password alone in Phase 1 — no OTP or other second factor layered on top." | spec: [Business-Flow Inventory](solution.md#business-flow-inventory) | alternatives: "Add email OTP as a second factor, reusing ss-auth-001's mechanism — more secure for the single most powerful account in the system, but adds a step to every admin login with no specific threat identified yet to justify it." | reversal_trigger: "A real, specific security concern about the Admin account surfaces after launch."
  - decision-52 :: Session lifetime is 7 days | kind: decision | summary: "A verified session (End User, Delivery Agent, or Admin) lasts 7 days before requiring re-authentication." | spec: [Handoff Boundaries](solution.md#handoff-boundaries) | alternatives: "Shorter (hours/same-day) — tighter security, but re-verifying via OTP that often adds real friction for repeat customers and daily-active agents. Longer (30+ days / until logout) — minimal friction, but a lost/shared device stays logged in much longer." | reversal_trigger: "A real security incident traces back to a stale 7-day session, or 7 days proves noticeably annoying in practice."
  - decision-53 :: OTP rate limit is 5 requests per hour per email | kind: decision | summary: "No more than 5 OTP requests per hour are honored for a given email — generous enough for someone who fumbles a code, tight enough to blunt automated abuse driving up email cost." | spec: [Handoff Boundaries](solution.md#handoff-boundaries) | alternatives: "A different threshold wasn't specifically requested; 5/hour is a reasonable default given no stated reason to deviate." | reversal_trigger: "Real usage shows legitimate users hitting the limit, or abuse getting through under it."
  - decision-54 :: Deactivating an agent auto-flags their in-flight order, doesn't auto-reassign or block | kind: decision | summary: "If admin deactivates an agent with an order already assigned or picked up, the order is immediately surfaced to admin as needing attention — using the existing manual reassignment flow (UC-008), not a new automatic one." | spec: [Business-Flow Inventory](solution.md#business-flow-inventory) | alternatives: "Fully automatic reassignment — faster, but risky if the picked-up items/cash state isn't cleanly handed off to a system that can't see it. Blocking deactivation until orders resolve — rejected; would prevent cutting off an agent urgently (e.g. for misconduct) exactly when admin most needs to." | reversal_trigger: "Manual flagging proves too slow in practice, e.g. admin misses the flag and a delivery stalls."
OpenQuestions:
  - oq-40 :: Session/token lifetime | kind: openquestion | summary: "How long does a session last before requiring re-authentication? — resolved, see decision-52." | spec: [AUTH Decisions](solution.md#auth-decisions)
  - oq-41 :: OTP rate-limiting threshold | kind: openquestion | summary: "What's the OTP rate-limiting threshold? — resolved, see decision-53." | spec: [AUTH Decisions](solution.md#auth-decisions)
  - oq-42 :: Does agent deactivation auto-trigger reassignment of in-flight orders? | kind: openquestion | summary: "Does deactivating an agent auto-reassign their in-flight orders? — resolved, see decision-54." | spec: [AUTH Decisions](solution.md#auth-decisions)
user-02 -> ss-auth-001 | relation: experiences
user-02 -> ss-auth-002 | relation: experiences
user-03 -> ss-auth-001 | relation: experiences
user-01 -> ss-auth-002 | relation: owns
user-01 -> ss-auth-003 | relation: owns
user-01 -> ss-auth-004 | relation: owns
decision-49 -> ss-auth-001 | relation: governs
decision-50 -> ss-auth-001 | relation: governs
decision-51 -> ss-auth-003 | relation: governs
decision-52 -> oq-40 | relation: decides
decision-53 -> oq-41 | relation: decides
decision-54 -> oq-42 | relation: decides
decision-52 -> ss-auth-005 | relation: governs
decision-53 -> ss-auth-001 | relation: governs
decision-54 -> ss-auth-002 | relation: governs
```

</details>

> [!note]
> This graph carries 17 nodes across 4 groups — thinner than the 30-node floor other stages hit, consistent with how thin `system-architecture.md` and `implementation-roadmap.md` also ran: a single module's Solution spec has less raw material than a project-wide BRD or Architecture. `Users` are reused from the BRD by the same IDs. `ss-auth-005` (session issuance) has no `User` edges — it's genuinely invisible infrastructure no human directly experiences, so leaving it edge-less is more honest than forcing one. All 3 original open questions resolved into `decision-52` through `decision-54` in a follow-up round.

## Scope and BRD Lineage

AUTH owns identity for all three roles and nothing else — no catalog data, no order data ([system-architecture.md's Module Decomposition](../../system-architecture.md#module-decomposition)). Every business flow below traces to a BRD use case or functional requirement: [ss-auth-001](#) to [UC-001](../../business-requirements.md#uc-001-end-user-creates-an-account) and FR-001–003; [ss-auth-002](#) to [UC-009](../../business-requirements.md#uc-009-delivery-agent-registers-and-gets-approved), FR-020, FR-021, and FR-029 (CR-001's addition); [ss-auth-003](#) to FR-027; [ss-auth-004](#) to decision-29 (business-requirements.md); [ss-auth-005](#) to the cross-cutting permission model in [system-architecture.md](../../system-architecture.md#permission-model-and-governance). Nothing here restates those sources without adding business substance — the additions are: how a login differs from first-time signup ([ss-auth-001](#)), what happens across role boundaries ([decision-49](#)), and how repeat authentication behaves ([decision-50](#), [decision-51](#)).

## Actors, Needs, and Expected Outcomes

**[Admin](#) ([user-01](#))** needs a reliable way in — losing access to the single shared login means losing access to the entire business. Expected outcome: a password-only login that's simple to use daily, with a real recovery path if forgotten ([ss-auth-004](#)).

**[Delivery Agent](#) ([user-02](#))** needs a way to prove they're a legitimate, admin-vetted agent before they can be trusted with orders and cash. Expected outcome: self-registration that doesn't require Admin's manual setup, but a real approval gate before they can act ([ss-auth-002](#)) — and afterward, the same low-friction email+OTP login End User gets ([ss-auth-001](#)).

**[End User](#) ([user-03](#))** needs an account cheap enough (in cost and friction) to create that it doesn't become a checkout blocker, per vision's cost-driven [decision-15](../../vision.md#vision-decisions). Expected outcome: email+OTP that reuses the same infrastructure notifications already need — no separate password to remember, no SMS cost passed on.

## Module Responsibilities, Boundaries, and Dependencies

**Owns:** account creation and verification for all three roles; OTP issuance and verification; Admin credential login and recovery; the Delivery Agent approval (and now deactivation, per FR-029) gate; session issuance and role-scoped authorization for every other module's protected requests.

**Does not own:** catalog data, order data, or any business logic belonging to CATALOG or ORDERS — AUTH answers "who is this" and "what can they do," never "what do they see" or "what did they order."

**Dependencies:** none. AUTH is the root of the module dependency graph ([roadmap.md](../../implementation-roadmap.md#module-dependency-graph)) — every other module depends on it, it depends on nothing else in this system. Its one external dependency is [EMAIL_PROVIDER](../../system-architecture.md#shared-platform-rules-and-cross-cutting-concerns) (Resend) for OTP and recovery-link delivery.

## Business-Flow Inventory

- **[SS-AUTH-001](#) — Email + OTP identity verification.** One [flow](glossary#flow) covers both first-time signup and every later login for End User and Delivery Agent — there is no separate "login" flow, matching how the BRD already described this for End User (UC-001's alternate flow) and how [decision-27](../../business-requirements.md#brd-decisions) extended the identical mechanism to Delivery Agent. [Decision-50](#) fixes that OTP is required every time, not skippable after the first verification.
- **[SS-AUTH-002](#) — Delivery Agent registration and approval gate.** A prospective agent's registration is a request, not an account — [decision-20](../../vision.md#vision-decisions) chose self-registration over admin-created accounts, but the account has no power until Admin approves it. This flow also now owns the deactivation path (FR-029, CR-001): an `approved` agent can be moved to `deactivated`, which is a distinct terminal-ish state from `rejected` (never approved).
- **[SS-AUTH-003](#) — Admin credential login.** The one login that isn't OTP-based — [decision-22](../../vision.md#vision-decisions) fixed Admin as a single shared account, and [decision-51](#) fixes that it authenticates by password alone.
- **[SS-AUTH-004](#) — Admin password recovery.** [Decision-29](../../business-requirements.md#brd-decisions) fixed the mechanism (email link to a registered recovery email) — this flow is the business behavior around it: request, email sent, link used once, old password invalidated.
- **[SS-AUTH-005](#) — Session issuance and role-scoped authorization.** Not a flow an End User, Agent, or Admin ever sees directly — it's what happens after any of the four flows above succeeds, and what CATALOG and ORDERS call on every protected request. This is the business behavior [interface-01](../../system-architecture.md#module-interactions-and-versioned-logical-interfaces) (`BACKEND_API`) rests on.

## Integration Intent

AUTH is one of three producers of [interface-01](../../system-architecture.md#module-interactions-and-versioned-logical-interfaces) `BACKEND_API` (its `/v1/auth/*` route prefix) — the only network-facing surface it exposes. Internally, CATALOG and ORDERS both call AUTH in-process to resolve "who is asking" ([SS-AUTH-005](#)) before honoring any protected write (CATALOG's bulk import, ORDERS' checkout/cancel/assign/fulfill) — this is the same in-process contract [system-architecture.md](../../system-architecture.md#module-interactions-and-versioned-logical-interfaces) already fixed, not a new one. Externally, AUTH is the only module that talks to [EMAIL_PROVIDER](../../system-architecture.md#shared-platform-rules-and-cross-cutting-concerns) for OTP codes and Admin's recovery link — CATALOG and ORDERS' own outbound emails (order-status notifications) are ORDERS' responsibility, not routed through AUTH.

## High-Level Payload Intent

No field names or schemas — the shape of information each flow needs or produces, in business terms:

- **[SS-AUTH-001](#)** needs: an email address, then a one-time code entered back. Produces: a verified session tied to that email and the role it was entered under.
- **[SS-AUTH-002](#)** needs: a prospective agent's identifying details (name, contact, whatever Admin needs to vet them) and, separately, Admin's approve/reject decision. Produces: an agent record in `pending_approval`, `approved`, `deactivated`, or `rejected` status.
- **[SS-AUTH-003](#)** needs: a username and password. Produces: a verified Admin session, or a rejection.
- **[SS-AUTH-004](#)** needs: a reset request, then a new password entered via the emailed link. Produces: an updated Admin password, or an expired/unused request.
- **[SS-AUTH-005](#)** needs: an incoming request's session token. Produces: a resolved role, or a rejection CATALOG/ORDERS can act on.

## Business States, Decisions, and Recovery

Delivery Agent status is the one real state machine AUTH owns, and it's canonical per `business-requirements.md`'s Domain Vocabulary (CR-001): `pending_approval` → `approved` → `deactivated`, or `pending_approval` → `rejected`. `deactivated` and `rejected` are not interchangeable — see the vocabulary entry for why.

Failure and recovery intent, in business terms (not error codes or schemas):
- **Wrong or expired OTP** ([SS-AUTH-001](#)): the attempt is rejected, a new code can be requested — this is already fixed at BRD level (AC-003).
- **Wrong Admin credentials** ([SS-AUTH-003](#)): the attempt is rejected with no account lockout in Phase 1 ([decision-51](#) covers the no-second-factor call; no separate lockout policy exists either, and none is proposed here — a single trusted account with OTP-rate-limited recovery is judged sufficient).
- **Admin forgets password** ([SS-AUTH-004](#)): recovery via the registered email — the *only* recovery path in Phase 1. If that email itself is inaccessible, there is no secondary recovery (already flagged in `system-architecture.md`'s Open Questions as a known gap, not re-litigated here).
- **A rejected or deactivated Delivery Agent tries to log in**: [SS-AUTH-001](#)'s OTP verification still succeeds (it's identity, not authorization) — but [SS-AUTH-005](#)'s authorization step is what actually blocks them from receiving assignments. Identity and authorization are deliberately separate concerns; conflating "can this email prove itself" with "is this person currently allowed to act as an agent" would make the deactivation feature (FR-029) meaningless.

## Handoff Boundaries

**To stage 40 (Experience Design, selected for AUTH per [decision-44](../../implementation-roadmap.md#build-order)):** every screen implied by the five flows above — email entry, OTP entry, agent registration form, Admin login, Admin password-reset request/confirm — plus how errors (wrong OTP, rejected agent, wrong Admin password) actually read to the user. Design also owns whether/how the End User and Delivery Agent share visual/interaction patterns for [SS-AUTH-001](#), since it's the same underlying flow for both roles.

**To stage 30d (System, required):** the exact state machine for Delivery Agent status transitions (who can trigger `deactivated`, whether it's reversible back to `approved`); concrete validation rules (what makes an email or password valid); the precise shape of a session/token carrying the 7-day lifetime ([decision-52](#)) and the 5-per-hour OTP limit ([decision-53](#)); and the mechanics of how a deactivated agent's in-flight order gets flagged to admin ([decision-54](#)).

## AUTH Decisions

The 3 open questions this stage's first draft raised were closed in a follow-up round with the same stakeholder.

1. **Sessions last 7 days before requiring re-authentication** ([decision-52](#)) — balances friction against exposure for a consumer app at this scale. Revisit if a stale session causes a real incident, or 7 days proves annoying in practice.
2. **OTP requests are capped at 5 per hour per email** ([decision-53](#)) — generous for a fumbled code, tight enough to blunt automated abuse. Revisit if legitimate users hit it or abuse gets through under it.
3. **Deactivating an agent auto-flags their in-flight order for admin to manually reassign** ([decision-54](#)) — no silent auto-reassignment, no blocking the deactivation itself. Revisit if manual flagging proves too slow in practice.

## Open Questions

None remain open from this Solution draft — all 3 were resolved in the follow-up above; see [AUTH Decisions](#auth-decisions).

## Approval

Approved by: Bhargav
Role:        PTL
Date:        2026-09-04
Hash:        968b80c7ea89
