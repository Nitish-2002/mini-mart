---
daksh:
  type: vision
  subtype: null
  stage: "10"
  module: null
---

# Vision

Mini Mart's [stage](glossary#stage) 00 [Discovery Context](client-context.md) established who this is for and locked 11 Phase 1 operating decisions; this document is the locked script everything downstream (BRD, architecture, every module spec) treats as ground truth, so it earns its own read even if you just came from that doc. The one-sentence version: Mini Mart becomes a single system that takes a shopper's order online, hands it to a delivery agent, and reconciles the resulting cash-on-delivery payment and stock change automatically — replacing what today is a paper register and nothing else. Everything below is built directly on the three roles, the Phase 1 decisions, and the three unvalidated assumptions already on record, plus 9 new decisions made in a follow-up round once the first draft surfaced them as open questions; nothing here contradicts stage 00, though a few things sharpen it, most notably naming the *one* capability this product actually is, not just what it does.

<details>
<summary>Graph: What is the thesis, what alternatives were rejected, and what would invalidate it?</summary>

```items
---
id: 10-vision-cognition
title: Vision — Thesis, Alternatives, Invalidation
default_open_depth: 1
default_color_by: kind
color_palette_source: .daksh/color-palette.json
width: 95vw
---
id: 10-vision-cognition
title: Vision — Thesis, Alternatives, Invalidation
Goals:
  - goal-00 :: Digitize Mini Mart's manual operations end-to-end | kind: goal | summary: "Replace paper/register-only retail with an online ordering, stock, and delivery system." | spec: [Vision Statement](vision.md#vision-statement) | success_measure: "Admin and end users report both faster checkout and reliable stock visibility within 6 months of launch."
  - goal-01 :: Fast, accurate online checkout | kind: goal | summary: "End users complete checkout quickly with correct pricing and stock deduction." | spec: [Core Capabilities](vision.md#core-capabilities) | success_measure: "Checkout completes with no manual price or stock correction needed."
  - goal-02 :: Real-time stock visibility for admin | kind: goal | summary: "Admin always sees current stock levels without a physical recount." | spec: [Core Capabilities](vision.md#core-capabilities) | success_measure: "Admin answers \"do we have X in stock\" from the app alone, no register or notebook lookup."
  - goal-03 :: Reliable Phase 1 fulfillment via delivery agents | kind: goal | summary: "Orders placed online reach the customer through a delivery agent without manual phone coordination." | spec: [Core Capabilities](vision.md#core-capabilities) | success_measure: "Orders are assigned, delivered, and COD-collected without a phone call between admin and agent."
  - goal-01a :: Minimize time spent per checkout | kind: goal | summary: "Reduce the steps and time an end user needs to place an order." | spec: [Core Capabilities](vision.md#core-capabilities) | success_measure: "Checkout requires no more than browse, cart, confirm."
  - goal-01b :: Eliminate manual billing errors | kind: goal | summary: "Remove the miscounts and wrong-price mistakes that come from register/notebook billing." | spec: [Problem Statements](vision.md#problem-statements) | success_measure: "Line-item price always matches the current catalog price; no manual override."
  - goal-02a :: Prevent overselling out-of-stock items | kind: goal | summary: "The system blocks or flags orders for items that are actually out of stock." | spec: [Core Capabilities](vision.md#core-capabilities) | success_measure: "Zero orders placed against an item recorded at 0 stock."
  - goal-02b :: Surface low-stock items to admin proactively | kind: goal | summary: "Admin is alerted before an item fully runs out, not after." | spec: [Core Capabilities](vision.md#core-capabilities) | success_measure: "Admin sees a low-stock list without querying manually."
  - goal-03a :: Timely order-to-agent handoff | kind: goal | summary: "A placed order reaches an available delivery agent without admin phoning around." | spec: [Core Capabilities](vision.md#core-capabilities) | success_measure: "Time between order placed and agent assigned is short and visible in the system."
  - goal-03b :: Reliable COD collection at the doorstep | kind: goal | summary: "The delivery agent collects cash at delivery and the system reflects the order as paid." | spec: [Core Capabilities](vision.md#core-capabilities) | success_measure: "Every order marked delivered has a matching COD-collected record."
Users:
  - user-01 :: Admin | kind: user | summary: "Runs the mart's catalog, pricing, and stock, and oversees orders and delivery agents." | spec: [Target Users](vision.md#target-users) | role: "Mart Admin/Owner" | audience: client | user_type: operator | status: placeholder
  - user-02 :: Delivery Agent | kind: user | summary: "Picks up assigned orders and delivers them to end users, collecting cash on delivery." | spec: [Target Users](vision.md#target-users) | role: "Delivery Agent" | audience: client | user_type: practitioner | status: placeholder
  - user-03 :: End User | kind: user | summary: "Browses the catalog, places an order, and pays cash on delivery when it arrives." | spec: [Target Users](vision.md#target-users) | role: "Shopper/Customer" | audience: end_customer | user_type: consumer | status: placeholder
Decisions:
  - decision-12 :: Order lifecycle is one deep module, not fragmented tools | kind: decision | summary: "Deep because one Order Lifecycle interface (place → assign → fulfill → collect COD → reconcile stock) hides catalog availability, agent dispatch, and stock reservation/release behind a single coherent state machine — End User's checkout, Admin's dashboard, and Delivery Agent's confirmation each see only their own slice, never the whole reconciliation." | spec: [Vision Statement](vision.md#vision-statement) | alternatives: "Separate, disconnected tools per function — a checkout form, a standalone stock spreadsheet, phone-call-based agent coordination. Deletion test: removing the unified lifecycle doesn't remove the complexity, it just pushes it back onto admin as manual reconciliation — which is exactly today's pain, so the unified module is earning its keep, not decoration." | reversal_trigger: "Walk-in and online sales prove to need genuinely different stock models (see decision-05 in stage 00), which would fracture the \"one\" lifecycle into two and invalidate this thesis."
  - decision-13 :: One integrated product with three role-based views, not three separate apps | kind: decision | summary: "Admin, Delivery Agent, and End User are three views into the same Order Lifecycle data, not three standalone products that would need their own sync layer to agree on order/stock state." | spec: [Vision Statement](vision.md#vision-statement) | alternatives: "Three separate apps/products (admin panel, agent app, customer storefront) built independently. Rejected because they would need to re-derive the same order/stock truth three times, reintroducing the reconciliation problem decision-12 exists to remove." | reversal_trigger: "Delivery agents or admin need an offline-first, native-only experience genuinely incompatible with a shared web-based lifecycle — would force splitting the agent view into its own product."
  - decision-14 :: MVP is single-store, not multi-location | kind: decision | summary: "Phase 1 is scoped to Mini Mart's one physical location and its single fixed delivery radius (see decision-01 in stage 00) — no per-store catalog, stock, or agent-pool partitioning." | spec: [Scope](vision.md#scope) | alternatives: "Design for multi-store from day one. Rejected — there is no second location today, and partitioning catalog/stock/agents per store adds real complexity with no current caller to justify it." | reversal_trigger: "The client opens a second physical location — at that point catalog, stock, and delivery-agent pools need a per-store dimension that this MVP does not have."
  - decision-15 :: End User requires an account (email + OTP), phone collected separately | kind: decision | summary: "Checkout requires an email + OTP account, not guest checkout, so order history, reordering, and address reuse are possible from day one; phone number is still collected as a plain checkout field for the delivery agent to contact the customer, but carries no login/verification role. Revised 2026-09-03 from the original phone+SMS-OTP model — SMS OTP has a real per-message cost the client can't justify; email OTP reuses the same email infrastructure decision-17 already needs for notifications, at near-zero marginal cost." | spec: [Vision Decisions](vision.md#vision-decisions) | alternatives: "Phone + SMS OTP (original decision, rejected on cost). WhatsApp OTP as a cheaper phone-based middle ground — still a per-message cost and a WhatsApp Business API account to set up, rejected in favor of the already-free email channel. Dropping phone entirely — rejected because the delivery agent needs a real-time contact channel at the door that email/in-app can't provide." | reversal_trigger: "Email OTP deliverability or open rates prove unreliable enough to block checkout in practice."
  - decision-16 :: Pre-dispatch cancellation window is 5 minutes | kind: decision | summary: "A customer or admin can cancel an order free of charge only within 5 minutes of it being placed; after that it's treated as committed until dispatch (decision-03, stage 00 covers refusal at the door)." | spec: [Vision Decisions](vision.md#vision-decisions) | alternatives: "Free cancellation any time before dispatch — simpler, but removes any commitment signal once admin starts preparing an order. The 5-minute figure itself is `derived/assumed`, not a figure the client gave directly — chosen as a reasonable default pending confirmation." | reversal_trigger: "Real cancellation patterns after launch show 5 minutes is too short (frequent missed cancellations) or too long (admin already preparing orders customers then cancel)."
  - decision-17 :: Order-status notifications via in-app + email | kind: decision | summary: "End User is notified of order status changes (accepted, assigned, out for delivery) through in-app notifications and email — no SMS." | spec: [Vision Decisions](vision.md#vision-decisions) | alternatives: "SMS — works without an app session but adds per-message cost. Push notifications — richer, but requires an installable app/PWA this product doesn't commit to." | reversal_trigger: "Email deliverability or open rates prove too unreliable for time-sensitive status updates (e.g. \"agent is at your door\")."
  - decision-18 :: Catalog uses categories + search | kind: decision | summary: "The catalog is organized into categories with a search box, not a flat list — admin assigns a category per item during bulk import (decision-06, stage 00)." | spec: [Vision Decisions](vision.md#vision-decisions) | alternatives: "Flat list with search only — less upfront catalog-management work, but harder to browse as the catalog grows past a small size." | reversal_trigger: "The catalog stays small enough that categories add sorting overhead without helping anyone find anything."
  - decision-19 :: Catalog prices are tax-inclusive | kind: decision | summary: "The price shown to End User is the price paid — no separate tax line-item at checkout." | spec: [Vision Decisions](vision.md#vision-decisions) | alternatives: "Calculate and itemize tax separately at checkout — needed only if per-item tax rates turn out to vary or a compliance requirement demands an itemized breakdown." | reversal_trigger: "A tax/compliance requirement surfaces (ties to oq-09, stage 00, already resolved as \"no special regulatory scope assumed\") that requires itemized tax display."
  - decision-20 :: Delivery agents self-register, admin approves | kind: decision | summary: "A prospective delivery agent signs up themselves; they can't receive assignments until admin reviews and approves the registration." | spec: [Vision Decisions](vision.md#vision-decisions) | alternatives: "Admin manually creates every agent account — tighter control, but puts all onboarding effort on admin for a role that doesn't exist yet and may need to scale quickly." | reversal_trigger: "Self-registration attracts unqualified/fraudulent sign-ups faster than admin can review them, forcing a switch to invite-only."
  - decision-21 :: Storefront is English-only at launch | kind: decision | summary: "No localization work in Phase 1 — the End User-facing storefront ships in English only." | spec: [Vision Decisions](vision.md#vision-decisions) | alternatives: "English + a regional language — adds translation and locale-switching work with no named language requirement yet to justify it." | reversal_trigger: "The client names a specific regional-language requirement for their actual customer base."
  - decision-22 :: Admin is a single shared login | kind: decision | summary: "One admin account for the mart in Phase 1 — no per-staff roles or permission levels." | spec: [Vision Decisions](vision.md#vision-decisions) | alternatives: "Role-based access (owner vs. staff) — more setup, justified only once staff need restricted access the owner doesn't want to grant broadly." | reversal_trigger: "The mart brings on staff who need Admin access but shouldn't see everything the owner sees (e.g. financials)."
  - decision-23 :: Mid-delivery reassignment is admin-manual | kind: decision | summary: "If an assigned agent becomes unavailable after pickup, admin manually reassigns the order to another agent — consistent with the manual-assignment model (decision-02, stage 00)." | spec: [Vision Decisions](vision.md#vision-decisions) | alternatives: "Auto-cancel the order and notify the customer — simpler, but wastes an already-picked-up order and forces the customer to re-order from scratch." | reversal_trigger: "Manual reassignment proves too slow in practice once order volume grows, at which point automatic reassignment logic becomes worth building."
OpenQuestions:
  - oq-12 :: Account model for End User | kind: openquestion | summary: "Does an End User need to create an account, or is guest checkout enough for Phase 1? — resolved, see decision-15 (revised 2026-09-03: email + OTP, not phone + SMS OTP, on cost grounds)." | spec: [Vision Decisions](vision.md#vision-decisions)
  - oq-13 :: Cancellation/refund policy before dispatch | kind: openquestion | summary: "What's the policy for a customer or admin cancelling before the order is even dispatched? — resolved, see decision-16." | spec: [Vision Decisions](vision.md#vision-decisions)
  - oq-14 :: Order-status notification channel | kind: openquestion | summary: "How does an End User learn their order was accepted, assigned, or is out for delivery? — resolved, see decision-17." | spec: [Vision Decisions](vision.md#vision-decisions)
  - oq-15 :: Catalog structure — categories/search vs. flat list | kind: openquestion | summary: "Does the catalog need categories and search, or is a flat browsable list sufficient? — resolved, see decision-18." | spec: [Vision Decisions](vision.md#vision-decisions)
  - oq-16 :: Tax handling at checkout | kind: openquestion | summary: "Are catalog prices tax-inclusive, or itemized separately at checkout? — resolved, see decision-19." | spec: [Vision Decisions](vision.md#vision-decisions)
  - oq-17 :: Delivery agent onboarding/identity | kind: openquestion | summary: "How does admin add, verify, and deactivate a delivery agent's access? — resolved, see decision-20." | spec: [Vision Decisions](vision.md#vision-decisions)
  - oq-18 :: Storefront language support | kind: openquestion | summary: "What language(s) does the storefront need to support at launch? — resolved, see decision-21." | spec: [Vision Decisions](vision.md#vision-decisions)
  - oq-19 :: Multi-user access within Admin | kind: openquestion | summary: "Is Admin a single shared login, or does it need role-based access? — resolved, see decision-22." | spec: [Vision Decisions](vision.md#vision-decisions)
  - oq-20 :: Mid-delivery agent reassignment | kind: openquestion | summary: "If an assigned delivery agent becomes unavailable mid-delivery, how does the order get reassigned? — resolved, see decision-23." | spec: [Vision Decisions](vision.md#vision-decisions)
Assumptions:
  - assumption-01 :: Customers will order online instead of visiting in person | kind: assumption | summary: "Enough end users in the service area choose the app over an in-person visit — there is no physical storefront being digitized alongside it." | spec: [Leap-of-Faith Assumptions](vision.md#leap-of-faith-assumptions) | validation_plan: "Track order volume against service-area population after Phase 1 launch; revisit if adoption stalls."
  - assumption-02 :: Cash-on-delivery is sufficient for Phase 1 | kind: assumption | summary: "End users are comfortable paying the delivery agent in cash on arrival, with no online payment step yet." | spec: [Leap-of-Faith Assumptions](vision.md#leap-of-faith-assumptions) | validation_plan: "Monitor COD refusal/cancellation rate after launch; revisit payment model for Phase 2 if refusals are frequent."
  - assumption-03 :: Enough delivery agents will be available | kind: assumption | summary: "The mart can recruit or contract enough delivery agents to fulfill dozens of orders/day within an acceptable time in the service area." | spec: [Leap-of-Faith Assumptions](vision.md#leap-of-faith-assumptions) | validation_plan: "Track average order-to-delivery time against agent headcount after launch."
Risks:
  - risk-01 :: Low online adoption undermines the whole model | kind: risk | summary: "If customers keep expecting an in-person store, digitizing checkout and stock won't matter." | spec: [Leap-of-Faith Assumptions](vision.md#leap-of-faith-assumptions) | likelihood: "unknown — unvalidated" | impact: "high — the product has no orders to serve" | mitigation: "Start in a small, well-known service area and gather real order data before wider rollout." | phase: design
  - risk-02 :: Frequent COD refusal erodes trust and margin | kind: risk | summary: "If customers regularly decline to pay on delivery, agents make wasted trips and cash handling becomes unreliable." | spec: [Leap-of-Faith Assumptions](vision.md#leap-of-faith-assumptions) | likelihood: "unknown — unvalidated" | impact: "medium — lost delivery time and cash-reconciliation overhead" | mitigation: "Track refusal rate from day one; revisit the payment model for Phase 2 if it's high." | phase: design
  - risk-03 :: Delivery agent shortage delays fulfillment | kind: risk | summary: "If too few agents are available, orders queue up and the reliability goal fails even if checkout and stock work perfectly." | spec: [Leap-of-Faith Assumptions](vision.md#leap-of-faith-assumptions) | likelihood: "unknown — unvalidated" | impact: "medium — directly undermines goal-03" | mitigation: "Confirm agent headcount/availability with the client before committing to a service-area size." | phase: design
goal-00 -> goal-01 | relation: decomposes_into
goal-00 -> goal-02 | relation: decomposes_into
goal-00 -> goal-03 | relation: decomposes_into
goal-01 -> goal-01a | relation: decomposes_into
goal-01 -> goal-01b | relation: decomposes_into
goal-02 -> goal-02a | relation: decomposes_into
goal-02 -> goal-02b | relation: decomposes_into
goal-03 -> goal-03a | relation: decomposes_into
goal-03 -> goal-03b | relation: decomposes_into
user-01 -> goal-02 | relation: owns
user-01 -> goal-03 | relation: owns
user-02 -> goal-03b | relation: owns
user-03 -> goal-01 | relation: experiences
user-03 -> goal-01a | relation: experiences
user-03 -> goal-01b | relation: experiences
decision-12 -> goal-00 | relation: governs
decision-13 -> goal-00 | relation: governs
decision-14 -> goal-00 | relation: governs
assumption-01 -> goal-00 | relation: enables
assumption-02 -> goal-03b | relation: enables
assumption-03 -> goal-03 | relation: enables
risk-01 -> goal-00 | relation: threatens
risk-02 -> goal-03b | relation: threatens
risk-03 -> goal-03 | relation: threatens
decision-15 -> oq-12 | relation: decides
decision-16 -> oq-13 | relation: decides
decision-17 -> oq-14 | relation: decides
decision-18 -> oq-15 | relation: decides
decision-19 -> oq-16 | relation: decides
decision-20 -> oq-17 | relation: decides
decision-21 -> oq-18 | relation: decides
decision-22 -> oq-19 | relation: decides
decision-23 -> oq-20 | relation: decides
decision-15 -> goal-01 | relation: governs
decision-16 -> goal-03 | relation: governs
decision-17 -> goal-03a | relation: governs
decision-18 -> goal-01 | relation: governs
decision-19 -> goal-01b | relation: governs
decision-20 -> goal-03a | relation: governs
decision-21 -> goal-01 | relation: governs
decision-22 -> goal-02 | relation: governs
decision-23 -> goal-03 | relation: governs
```

</details>

> [!note]
> This graph carries 43 nodes across 6 groups. `Goals`, `Users`, `Assumptions`, and `Risks` are the same entities as stage 00's graph, redrawn here by the same IDs (per the cross-doc continuity rule) because the vision's leap-of-faith assumptions and target users *are* those exact nodes, not a fresh set — restating them here is lineage, not duplication. `decision-12` through `decision-14` are this stage's depth-claim and scope decisions; `decision-15` through `decision-23` resolve the 9 open questions this vision draft originally raised, each with an inbound `decides` edge from its resolving decision, mirroring how stage 00 closed its own open questions. `user-03` carries outbound `experiences` edges to the checkout goals — the vision stage explicitly asks for User→Goal `experiences` edges, which stage 00's graph could not legally draw for an `end_customer` User.

## Vision Statement

Mini Mart becomes one system that turns a shopper's online order into cash in a delivery agent's hand and an accurate stock count on admin's screen, without anyone making a phone call to make that happen `[derived/decided · alt: describe the vision as three separate tools — a checkout app, a stock tracker, a delivery coordination process — rejected per decision-12: that framing hides the one thing that actually has to work, which is that all three agree on the same order at every moment]`.

## Target Users

Three roles carry the product, and each experiences a different slice of the same underlying order lifecycle. **Admin** ([user-01](#), `user_type: operator`) is the mart's owner/operator — before this product, they ran catalog, pricing, and stock entirely on paper, and after, they run the same responsibilities from one screen with real-time visibility, through a single shared login (decision-22). **Delivery Agent** ([user-02](#), `user_type: practitioner`) is a role that doesn't formally exist today — orders and deliveries are currently unmanaged — so this product doesn't digitize an old workflow for them, it creates the workflow, starting with self-registration and admin approval (decision-20). **End User** ([user-03](#), `user_type: consumer`) is the shopper — before, their only option was a physical visit; after, they create an email+OTP account (decision-15, with phone collected separately for delivery contact) and browse a categorized, searchable catalog (decision-18) to order and pay on delivery from wherever they are. All three remain `status: placeholder` in the graph — none have been interviewed yet, only described by the client acting as stakeholder.

There is no single "most important" user here worth forcing into a false hierarchy: Admin commissioned this product to fix their own operations, but the client was explicit that checkout speed (End User's experience) and stock visibility (Admin's experience) are success measures held together, not ranked. Admin is the one whose day-to-day workflow this product exists to replace; End User and Delivery Agent are the two roles that workflow now has to serve well for it to actually work.

## Problem Statements

1. **Admin has no real-time stock visibility and makes billing errors.** Today's constraint: a physical register and paper tracking mean any stock question requires a manual recount, and pricing/billing mistakes come from human transcription, not calculation `[canonical/given · src: discovery conversation, 2026-09-03]`. Known risk: if the digital stock count silently drifts from physical reality (e.g. a walk-in sale not recorded — see decision-05 in stage 00), the product recreates the exact problem it exists to solve.
2. **End User cannot order remotely at all.** The only option today is an in-person visit `[canonical/given · src: discovery conversation, 2026-09-03]`. Known risk: [risk-01](#) — if end users don't actually switch to ordering online, this problem statement stays unsolved regardless of how well checkout is built, because there's no one using it.
3. **Delivery Agent's workflow doesn't exist yet — it has to be created, not digitized.** There is no current process for assigning, tracking, or confirming deliveries `[canonical/given · src: discovery conversation, 2026-09-03]`. Known risk: [risk-03](#) — if too few agents are recruited or contracted, this newly-created workflow becomes the bottleneck for every order regardless of how well checkout and stock work.

## Core Capabilities

High-level only — no tech stack, no schema, no screen detail; those belong to stage 30a/30c/40 once this thesis is locked.

- **Catalog browsing and ordering** for End User, organized into categories with search (decision-18), backed by a shared stock pool across online and walk-in sales (decision-05, stage 00).
- **Account-based checkout** (email + OTP, decision-15) with a tiered delivery fee — minimum order to check out, free delivery above a threshold, a smaller fee below it (decision-04, stage 00) — and tax-inclusive pricing (decision-19).
- **Admin catalog and stock management**, populated by bulk import rather than one-by-one entry (decision-06, stage 00), through a single shared login (decision-22).
- **Order-to-agent assignment**, done by admin manually in Phase 1 (decision-02, stage 00), including manual reassignment if an agent becomes unavailable mid-delivery (decision-23).
- **Delivery agent self-registration**, gated by admin approval before an agent can receive assignments (decision-20), with in-app COD collection confirmation at drop-off (decision-09, stage 00).
- **Order-status notifications** to End User via in-app + email (decision-17), and a 5-minute pre-dispatch cancellation window (decision-16).
- **Automatic stock release** for orders that go stale before confirmation or pickup (decision-10, stage 00).

Every one of these ties back to the single Order Lifecycle [decision-12](#) argues for — none of them is a standalone feature with its own separate state.

## Scope

**In scope (Phase 1):** everything above — English-only storefront (decision-21), account-based checkout with the ₹10/₹49 fee tiers, categorized catalog, admin catalog/stock/order management on a single shared login, agent self-registration with admin approval, manual agent assignment and reassignment, in-app COD confirmation, in-app + email notifications, a 5-minute cancellation window, stale-order stock release, and continued walk-in sales sharing the same stock pool. Single store, single fixed delivery radius (see [decision-14](#)).

**Out of scope (Phase 2, deferred until the client asks for it — decision-11, stage 00):** digital payment methods beyond COD, expanded or multi-radius service areas, additional languages, and role-based Admin access beyond a single shared login — and anything else the client has not yet raised. Nothing beyond the Phase 2 deferrals already on record is being cut from this engagement.

## Leap-of-Faith Assumptions

These three, carried forward unchanged from stage 00, are the beliefs this product's success rests on — if any is wrong, the product doesn't degrade, it fails at the thing it exists to do. None are validated yet.

1. **[assumption-01](#) — Customers will order online instead of visiting in person.** Unvalidated. If wrong, there's no order volume for any of the rest of this vision to matter against — see [risk-01](#).
2. **[assumption-02](#) — Cash-on-delivery is acceptable and sufficient for Phase 1.** Unvalidated. If wrong, delivery agents absorb the cost of refused payments and [decision-12](#)'s "reconcile stock" step in the lifecycle never cleanly closes — see [risk-02](#).
3. **[assumption-03](#) — Enough delivery agents will be available to cover order volume**, now specifically dozens of orders per day at launch. Unvalidated. If wrong, [goal-03](#) (reliable fulfillment) fails structurally, not just occasionally — see [risk-03](#).

## Success Metrics

**At handoff:** a working Phase 1 app is live in production, not a demo — an End User can create an account, complete a real order, and pay COD, an Admin can manage catalog/stock/orders end to end from one login, and a Delivery Agent can self-register, get approved, receive an assignment, deliver, and confirm collection, all reflected correctly in shared stock state.

**At user adoption (post-launch):** order volume trends toward the "dozens per day" estimate ([decision-07](#), stage 00) rather than staying near zero (which would falsify [assumption-01](#)); COD refusal rate stays low enough not to trigger [risk-02](#)'s mitigation review; admin-reported stock accuracy holds without manual reconciliation, which is the actual test of whether [decision-12](#)'s depth claim was correct; and the 5-minute cancellation window ([decision-16](#)) and in-app/email notifications ([decision-17](#)) don't generate complaints that force an early revisit.

## Vision Decisions

The 9 open questions from the first vision draft were each closed in a follow-up round with the same stakeholder. Each decision below names what was rejected and why, and what would trigger revisiting it.

1. **End User requires an email + OTP account, not guest checkout** ([decision-15](#)) — enables order history and reordering from day one. Phone number is still collected as a plain checkout field so the delivery agent can contact the customer, but it plays no role in login. *Revised 2026-09-03:* originally decided as phone + SMS OTP; changed on cost grounds — SMS carries a real per-message cost, while email OTP reuses the same infrastructure decision-17 already needs. Revisit if email OTP deliverability proves unreliable.
2. **Orders can be cancelled free of charge only within 5 minutes of placement** ([decision-16](#)) — the 5-minute figure is `derived/assumed`, a reasonable default rather than a client-specified number; flagged for confirmation during BRD or TRD rather than treated as final. Revisit once real cancellation timing data exists.
3. **Order-status updates go out via in-app notification and email, not SMS** ([decision-17](#)) — avoids per-message SMS cost. Revisit if email proves too slow/unreliable for time-sensitive updates like "agent is at your door."
4. **The catalog is organized into categories with search** ([decision-18](#)) — chosen over a flat list to stay browsable as the catalog grows. Revisit if the catalog stays small enough that categories add overhead without helping.
5. **Catalog prices are tax-inclusive** ([decision-19](#)) — no separate tax line-item at checkout. Revisit only if a tax/compliance requirement surfaces (stage 00 already concluded no special regulatory scope applies).
6. **Delivery agents self-register and admin approves them** ([decision-20](#)) — lower onboarding effort for admin than manually creating every account. Revisit if self-registration attracts sign-ups faster than admin can vet them.
7. **The storefront ships English-only** ([decision-21](#)) — no named language requirement yet to justify localization work. Revisit the moment the client names a specific regional-language need.
8. **Admin is a single shared login** ([decision-22](#)) — no role-based access in Phase 1. Revisit once staff need Admin access without seeing everything the owner sees.
9. **Mid-delivery agent reassignment is admin-manual** ([decision-23](#)) — consistent with the manual-assignment model already in place. Revisit if manual reassignment becomes too slow as order volume grows.

## Open Questions

None remain open from this vision draft — all 9 were resolved in the follow-up above; see [Vision Decisions](#vision-decisions). Any new open items that surface during `/daksh brd` get numbered and tracked in this section's future revisions.

## Approval

Approved by: Bhargav
Role:        PTL
Date:        2026-09-03
Hash:        c6b90c9544bb�
