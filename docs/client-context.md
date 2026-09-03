---
daksh:
  type: client-context
  subtype: null
  stage: "00"
  module: null
---

# Discovery Context

Mini Mart is moving from a fully manual, walk-in retail operation to an online ordering and delivery service — Phase 1 launches with cash-on-delivery only, with any wider payment or service-area expansion deferred to a Phase 2 the client will ask for later `[derived/decided · alt: build digital payments and wider rollout into Phase 1 (rejected: no client ask for it yet, and it widens scope before the basics are proven)]`. This document is the Daksh [stage](glossary#stage) 00 output — it captures what the client, acting as both stakeholder and PTL for this engagement, has said so far about who the product is for, what a successful first release looks like, and the 11 operating decisions made in a follow-up round once the first draft surfaced them as open questions — and it feeds directly into `/daksh vision`. Three roles carry the product end to end: Admin runs the mart's catalog, stock, and order assignment; Delivery Agent fulfills orders and collects cash on arrival; End User browses, orders, and pays on delivery. Everything below comes from two discovery rounds with the same stakeholder — no prior client documents, meeting recordings, or transcripts exist in `docs/conversations/client/` yet, so the reader should still treat personas and numbers as a first pass, not field-validated.

<details>
<summary>Graph: Who is this for, what do they need, and what did we decide?</summary>

```items
---
id: 00-onboarding-cognition
title: Client Onboarding — Who, What, Decisions
default_open_depth: 1
default_color_by: kind
color_palette_source: .daksh/color-palette.json
width: 95vw
---
id: 00-onboarding-cognition
title: Client Onboarding — Who, What, Decisions
Goals:
  - goal-00 :: Digitize Mini Mart's manual operations end-to-end | kind: goal | summary: "Replace paper/register-only retail with an online ordering, stock, and delivery system." | spec: [Product Summary](client-context.md#product-summary) | success_measure: "Admin and end users report both faster checkout and reliable stock visibility within 6 months of launch."
  - goal-01 :: Fast, accurate online checkout | kind: goal | summary: "End users complete checkout quickly with correct pricing and stock deduction." | spec: [Product Summary](client-context.md#product-summary) | success_measure: "Checkout completes with no manual price or stock correction needed."
  - goal-02 :: Real-time stock visibility for admin | kind: goal | summary: "Admin always sees current stock levels without a physical recount." | spec: [Product Summary](client-context.md#product-summary) | success_measure: "Admin answers \"do we have X in stock\" from the app alone, no register or notebook lookup."
  - goal-03 :: Reliable Phase 1 fulfillment via delivery agents | kind: goal | summary: "Orders placed online reach the customer through a delivery agent without manual phone coordination." | spec: [Product Summary](client-context.md#product-summary) | success_measure: "Orders are assigned, delivered, and COD-collected without a phone call between admin and agent."
  - goal-01a :: Minimize time spent per checkout | kind: goal | summary: "Reduce the steps and time an end user needs to place an order." | spec: [Product Summary](client-context.md#product-summary) | success_measure: "Checkout requires no more than browse, cart, confirm."
  - goal-01b :: Eliminate manual billing errors | kind: goal | summary: "Remove the miscounts and wrong-price mistakes that come from register/notebook billing." | spec: [Constraints](client-context.md#constraints) | success_measure: "Line-item price always matches the current catalog price; no manual override."
  - goal-02a :: Prevent overselling out-of-stock items | kind: goal | summary: "The system blocks or flags orders for items that are actually out of stock." | spec: [Product Summary](client-context.md#product-summary) | success_measure: "Zero orders placed against an item recorded at 0 stock."
  - goal-02b :: Surface low-stock items to admin proactively | kind: goal | summary: "Admin is alerted before an item fully runs out, not after." | spec: [Product Summary](client-context.md#product-summary) | success_measure: "Admin sees a low-stock list without querying manually."
  - goal-03a :: Timely order-to-agent handoff | kind: goal | summary: "A placed order reaches an available delivery agent without admin phoning around." | spec: [Product Summary](client-context.md#product-summary) | success_measure: "Time between order placed and agent assigned is short and visible in the system."
  - goal-03b :: Reliable COD collection at the doorstep | kind: goal | summary: "The delivery agent collects cash at delivery and the system reflects the order as paid." | spec: [Unvalidated Assumptions](client-context.md#unvalidated-assumptions) | success_measure: "Every order marked delivered has a matching COD-collected record."
Users:
  - user-01 :: Admin | kind: user | summary: "Runs the mart's catalog, pricing, and stock, and oversees orders and delivery agents." | spec: [User Types](client-context.md#user-types) | role: "Mart Admin/Owner" | audience: client | status: placeholder
  - user-02 :: Delivery Agent | kind: user | summary: "Picks up assigned orders and delivers them to end users, collecting cash on delivery." | spec: [User Types](client-context.md#user-types) | role: "Delivery Agent" | audience: client | status: placeholder
  - user-03 :: End User | kind: user | summary: "Browses the catalog, places an order, and pays cash on delivery when it arrives." | spec: [User Types](client-context.md#user-types) | role: "Shopper/Customer" | audience: end_customer | status: placeholder
Assumptions:
  - assumption-01 :: Customers will order online instead of visiting in person | kind: assumption | summary: "Enough end users in the service area choose the app over an in-person visit — there is no physical storefront being digitized alongside it." | spec: [Unvalidated Assumptions](client-context.md#unvalidated-assumptions) | validation_plan: "Track order volume against service-area population after Phase 1 launch; revisit if adoption stalls."
  - assumption-02 :: Cash-on-delivery is sufficient for Phase 1 | kind: assumption | summary: "End users are comfortable paying the delivery agent in cash on arrival, with no online payment step yet." | spec: [Unvalidated Assumptions](client-context.md#unvalidated-assumptions) | validation_plan: "Monitor COD refusal/cancellation rate after launch; revisit payment model for Phase 2 if refusals are frequent."
  - assumption-03 :: Enough delivery agents will be available | kind: assumption | summary: "The mart can recruit or contract enough delivery agents to fulfill orders within an acceptable time in the service area." | spec: [Unvalidated Assumptions](client-context.md#unvalidated-assumptions) | validation_plan: "Track average order-to-delivery time against agent headcount after launch."
Risks:
  - risk-01 :: Low online adoption undermines the whole model | kind: risk | summary: "If customers keep expecting an in-person store, digitizing checkout and stock won't matter." | spec: [Unvalidated Assumptions](client-context.md#unvalidated-assumptions) | likelihood: "unknown — unvalidated" | impact: "high — the product has no orders to serve" | mitigation: "Start in a small, well-known service area and gather real order data before wider rollout." | phase: design
  - risk-02 :: Frequent COD refusal erodes trust and margin | kind: risk | summary: "If customers regularly decline to pay on delivery, agents make wasted trips and cash handling becomes unreliable." | spec: [Unvalidated Assumptions](client-context.md#unvalidated-assumptions) | likelihood: "unknown — unvalidated" | impact: "medium — lost delivery time and cash-reconciliation overhead" | mitigation: "Track refusal rate from day one; revisit the payment model for Phase 2 if it's high." | phase: design
  - risk-03 :: Delivery agent shortage delays fulfillment | kind: risk | summary: "If too few agents are available, orders queue up and the reliability goal fails even if checkout and stock work perfectly." | spec: [Unvalidated Assumptions](client-context.md#unvalidated-assumptions) | likelihood: "unknown — unvalidated" | impact: "medium — directly undermines goal-03" | mitigation: "Confirm agent headcount/availability with the client before committing to a service-area size." | phase: design
OpenQuestions:
  - oq-01 :: Delivery service area for Phase 1 | kind: openquestion | summary: "What radius or which neighborhoods does Phase 1 delivery actually cover? — resolved, see decision-01." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions)
  - oq-02 :: Order-to-agent assignment method | kind: openquestion | summary: "Are delivery agents assigned by admin manually, or automatically? — resolved, see decision-02." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions)
  - oq-03 :: COD refusal handling | kind: openquestion | summary: "What happens when a customer refuses to pay on delivery? — resolved, see decision-03." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions)
  - oq-04 :: Minimum order value / delivery fee | kind: openquestion | summary: "Is there a minimum order value or a delivery fee? — resolved, see decision-04." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions)
  - oq-05 :: Phase 2 trigger and scope | kind: openquestion | summary: "What specifically triggers Phase 2, and what does it add? — resolved, see decision-11." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions)
  - oq-06 :: Walk-in purchases alongside online orders | kind: openquestion | summary: "Will Mini Mart still take in-person purchases? — resolved, see decision-05." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions)
  - oq-07 :: Catalog ownership | kind: openquestion | summary: "Who enters and maintains the product catalog? — resolved, see decision-06." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions)
  - oq-08 :: Expected order volume | kind: openquestion | summary: "What order volume is Mini Mart expecting at launch? — resolved, see decision-07." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions)
  - oq-09 :: Regulatory/licensing requirements | kind: openquestion | summary: "Are there licensing or regulatory requirements for selling stocked items online? — resolved, see decision-08." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions)
  - oq-10 :: COD collection verification | kind: openquestion | summary: "How does admin verify a delivery agent actually collected the cash? — resolved, see decision-09." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions)
  - oq-11 :: Stale-order stock release | kind: openquestion | summary: "If an order sits uncollected, is its reserved stock released back? — resolved, see decision-10." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions)
Decisions:
  - decision-01 :: Service area = single fixed radius | kind: decision | summary: "Phase 1 delivery covers a single fixed radius around the store, not a named-area list or citywide coverage." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions) | alternatives: "Named neighborhood/pincode list — more precise but more setup to maintain. Citywide with no limit — simplest to state, but risks promising coverage delivery agents can't reliably reach." | reversal_trigger: "Real order geography after launch shows the radius is too small or too large for actual demand."
  - decision-02 :: Dispatch = admin assigns manually | kind: decision | summary: "Admin manually picks a delivery agent for each order; no automatic assignment in Phase 1." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions) | alternatives: "Automatic proximity/availability-based assignment — deferred; added complexity not justified at Phase 1 volume." | reversal_trigger: "Order volume grows enough that manual assignment becomes a bottleneck for admin."
  - decision-03 :: COD refusal = cancel and restock | kind: decision | summary: "If a customer refuses to pay on delivery, the order is cancelled and its items return to stock — no retry, no cost recovery." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions) | alternatives: "Retry once before cancelling — adds agent scheduling complexity. Charge the customer for the wasted trip — needs a billing/penalty mechanism, likely Phase 2." | reversal_trigger: "Refusal rate proves high enough after launch (see risk-02) that a wasted trip becomes a real cost problem."
  - decision-04 :: Delivery fee = tiered free-delivery threshold | kind: decision | summary: "Minimum order value of ₹10 to check out at all; orders ₹49 and above ship free; orders between ₹10 and ₹48 have a delivery fee added, with checkout messaging inviting the customer to add more for free delivery." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions) | alternatives: "No minimum, always-free delivery — simplest, but no margin protection on tiny orders. Flat delivery fee on every order — simpler pricing, but no incentive to grow basket size." | reversal_trigger: "Real basket sizes and delivery margins after launch show the ₹49 threshold is set too high or too low."
  - decision-05 :: Walk-in sales continue, one shared stock pool | kind: decision | summary: "Mini Mart keeps taking in-person purchases alongside online orders; both channels draw from and update the same stock count." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions) | alternatives: "Online-only, no walk-in sales — simpler stock model, but drops a revenue channel the mart already has today." | reversal_trigger: "Recording walk-in sales in the app becomes a real bottleneck for counter staff."
  - decision-06 :: Catalog entry = bulk import | kind: decision | summary: "The product catalog (items, prices, photos) is maintained via spreadsheet/CSV bulk import, not one-by-one manual entry." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions) | alternatives: "Admin enters items by hand one at a time — simpler to build, slow for a catalog of any real size." | reversal_trigger: "Catalog stays small and rarely changes, making a manual entry screen worth adding alongside import."
  - decision-07 :: Plan for moderate launch volume | kind: decision | summary: "Delivery agent headcount and system capacity are sized for dozens of orders per day at launch, not a handful." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions) | alternatives: "Small/handful-per-day estimate — would undersize agent headcount. Leave volume unestimated — would leave capacity planning ungrounded." | reversal_trigger: "Real order data in the first weeks after launch shows the estimate was significantly off."
  - decision-08 :: No special regulatory scope assumed | kind: decision | summary: "Mini Mart is treated as a standard local retail business with no grocery-specific online licensing called out." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions) | alternatives: "Assume specific grocery/food-safety licensing applies — would add compliance scope with no concrete requirement named yet." | reversal_trigger: "A specific licensing requirement is identified by the client's local authority before launch."
  - decision-09 :: COD verified via in-app agent confirmation | kind: decision | summary: "The delivery agent confirms cash collection in-app at drop-off, giving a timestamped record admin can check." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions) | alternatives: "Trust-based, reconciled manually later — simpler to build, weaker evidence trail, harder to catch discrepancies." | reversal_trigger: "In-app confirmation proves unreliable in practice (agents skipping the step)."
  - decision-10 :: Stale orders auto-release reserved stock | kind: decision | summary: "An order not confirmed or picked up within a timeout window automatically releases its reserved stock back to inventory; the exact timeout value is left for the System spec (stage 30d) to set." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions) | alternatives: "No auto-release, admin manually clears stale orders — simpler logic, but risks stock sitting reserved against a dead order indefinitely." | reversal_trigger: "The chosen timeout proves too aggressive or too lax once stage 30d sets a concrete value and it runs in practice."
  - decision-11 :: Phase 2 scope stays undefined until requested | kind: decision | summary: "Digital payments, wider service area, and any other beyond-COD capability are explicitly deferred — Phase 2 is scoped only once the client asks for it." | spec: [Phase 1 Decisions](client-context.md#phase-1-decisions) | alternatives: "Pre-define a Phase 2 scope now — rejected; the client was explicit that Phase 2 is defined later, on request, not guessed at during Phase 1 discovery." | reversal_trigger: "The client raises Phase 2 — this decision is revisited immediately and a fresh discovery/vision pass scopes it."
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
assumption-01 -> goal-00 | relation: enables
assumption-02 -> goal-03b | relation: enables
assumption-03 -> goal-03 | relation: enables
risk-01 -> goal-00 | relation: threatens
risk-02 -> goal-03b | relation: threatens
risk-03 -> goal-03 | relation: threatens
decision-01 -> oq-01 | relation: decides
decision-02 -> oq-02 | relation: decides
decision-03 -> oq-03 | relation: decides
decision-04 -> oq-04 | relation: decides
decision-05 -> oq-06 | relation: decides
decision-06 -> oq-07 | relation: decides
decision-07 -> oq-08 | relation: decides
decision-08 -> oq-09 | relation: decides
decision-09 -> oq-10 | relation: decides
decision-10 -> oq-11 | relation: decides
decision-11 -> oq-05 | relation: decides
decision-01 -> goal-03 | relation: governs
decision-02 -> goal-03a | relation: governs
decision-03 -> goal-03b | relation: governs
decision-04 -> goal-01 | relation: governs
decision-05 -> goal-02 | relation: governs
decision-06 -> goal-01 | relation: governs
decision-07 -> goal-03a | relation: governs
decision-09 -> goal-03b | relation: governs
decision-10 -> goal-02a | relation: governs
decision-11 -> goal-00 | relation: governs
```

</details>

> [!note]
> This graph sits at 6 entity groups and 41 nodes fully expanded — inside the 30–60 node floor, but under the usual 10–16 root-group guidance, which assumes more entity kinds than a two-round, document-free onboarding pass actually produced. End User (`user-03`) is drawn with no outgoing edge: the vocabulary has no legal edge from an `end_customer` User to a `Goal` at this stage — that connective tissue (Flow) doesn't exist until later stages. Every `OpenQuestion` now carries an inbound `decides` edge from the `Decision` that resolved it, per the methodology's rule that a resolved OpenQuestion is signaled by that edge, not by deleting the node — the ID stays valid for any later doc that references it.

## Product Summary

Mini Mart today runs entirely on paper and a physical register — there is no existing software, spreadsheet, or third-party tool in place `[canonical/given · src: discovery conversation, 2026-09-03]`. The product being built replaces that with an online ordering and delivery service: an end user browses the catalog, places an order, and pays the delivery agent in cash when it arrives, while admin manages catalog, pricing, stock, and order-to-agent assignment from one place `[derived/decided · alt: in-store billing/POS as the primary flow with delivery as an add-on (rejected: the three stated roles — admin, delivery agent, end user — only make sense if online ordering with delivery is the primary flow, not a register-first shop)]`. In-person purchases at the physical store continue alongside online orders and draw from the same stock pool — see [decision-05](#phase-1-decisions) — so "digitizing" the mart means adding an online/delivery channel on top of the existing counter, not replacing it. The client named two things as the definition of success at the 6-month mark, together, not separately: checkout that's fast and error-free, and stock counts admin can trust without walking the aisles `[canonical/given · src: discovery conversation, 2026-09-03]`. Phase 1 is deliberately narrow — cash on delivery only, no digital payment integration — with Phase 2 scope explicitly left undefined until the client asks for it — see [decision-11](#phase-1-decisions).

## User Types

| Role | Primary Pain Today |
|---|---|
| **Admin** (Mart Admin/Owner) — [user-01](#) | No visibility into real stock levels without a manual recount; billing errors from register/notebook tracking. |
| **Delivery Agent** — [user-02](#) | No role or workflow exists yet — orders and deliveries are entirely unmanaged; this is a new function for the business, not a digitized old one. |
| **End User** (Shopper) — [user-03](#) | Cannot order remotely at all today; the only option is physically visiting a location. |

All three are stubs, not full personas — none have been interviewed yet, so `status: placeholder` on every [User](glossary#user) node in the graph above. Full personas are only worth writing once the client can't proceed without them.

## Constraints

1. **No hard deadline or fixed budget stated** — the client gave no launch date or budget ceiling to plan around `[canonical/given · src: discovery conversation, 2026-09-03]`.
2. **Standard modern web stack** — `backend/`, `frontend/`, and `devops/` folders exist but are empty; no existing framework, language, or hosting choice constrains the build `[derived/observed · src: repo root, 2026-09-03]`.
3. **Phase 1 payment is cash-on-delivery only** — no online payment gateway is in scope for this phase; see [assumption-02](#unvalidated-assumptions) `[canonical/given · src: discovery conversation, 2026-09-03]`.
4. **No prior system to migrate from or integrate with** — everything is manual today, so there is no legacy data, no existing API, and no cutover risk from a running system `[canonical/given · src: discovery conversation, 2026-09-03]`.
5. **No Jira project configured** — `manifest.jira.project_key` and `manifest.jira.board_id` stay `null`; the client is not using Jira for this engagement `[canonical/given · src: discovery conversation, 2026-09-03]`.
6. **Both online and walk-in sales draw from one stock pool** — see [decision-05](#phase-1-decisions); the stock model can't assume online orders are the only thing depleting inventory `[derived/decided · src: discovery follow-up, 2026-09-03]`.
7. **Catalog is populated by bulk import, not one-by-one entry** — see [decision-06](#phase-1-decisions) `[derived/decided · src: discovery follow-up, 2026-09-03]`.
8. **Launch capacity is sized for moderate volume (dozens of orders/day)**, not a small pilot trickle — see [decision-07](#phase-1-decisions) `[derived/decided · src: discovery follow-up, 2026-09-03]`.

## Unvalidated Assumptions

1. **Customers will order online instead of visiting in person** ([assumption-01](#)) — the entire model depends on end users in the service area choosing the app over an in-person visit, and there is no existing storefront to fall back on if they don't. If wrong, the product has nothing to serve, however good checkout and stock tracking are — see [risk-01](#).
2. **Cash-on-delivery is acceptable and sufficient for Phase 1** ([assumption-02](#)) — end users are assumed comfortable paying in cash at the door with no online payment option offered. If refusal is common, delivery agents make wasted trips and cash reconciliation becomes unreliable — see [risk-02](#).
3. **Enough delivery agents will be available to cover order volume** ([assumption-03](#)) — the mart is assumed able to recruit or contract enough agents to fulfill orders within an acceptable window in the service area, now sized for dozens of orders/day (see [decision-07](#phase-1-decisions)). If not, orders queue up regardless of how well checkout and stock work — see [risk-03](#).

## Phase 1 Decisions

The 11 open questions from the first discovery pass were each closed in a follow-up round with the same stakeholder. Each decision below is stamped `derived/decided`, names what was rejected and why, and states what would trigger revisiting it — the same discipline the graph's `Decision` nodes carry as `alternatives` and `reversal_trigger`.

1. **Service area is a single fixed radius around the store** ([decision-01](#)) — not a named-neighborhood list (more precise, more upkeep) or citywide (simplest to say, hardest to actually cover). Revisit once real order geography after launch shows the radius is wrong.
2. **Admin manually assigns each order to a delivery agent** ([decision-02](#)) — automatic proximity/availability-based dispatch is deferred as unjustified complexity at Phase 1 volume. Revisit if manual assignment becomes a bottleneck.
3. **A refused COD order is cancelled and its stock restored** ([decision-03](#)) — no retry, no cost recovery from the customer; both were considered and deferred as unnecessary complexity for Phase 1. Revisit if refusal rate is high enough to matter (tracked via [risk-02](#)).
4. **Checkout requires a ₹10 minimum order, ships free at ₹49+, and adds a delivery fee below that** — with UI copy inviting the customer to add more for free delivery ([decision-04](#)). Chosen over always-free delivery (no margin protection) and a flat fee on every order (no incentive to grow the basket). Revisit if real basket sizes and margins say ₹49 is set wrong.
5. **Walk-in, in-person purchases continue alongside online orders, sharing one stock pool** ([decision-05](#)) — going online-only would drop a channel the mart already has. Revisit if recording walk-in sales in the app becomes a burden on counter staff.
6. **The product catalog is populated by spreadsheet/CSV bulk import** ([decision-06](#)) — manual one-by-one entry was rejected as too slow for a real catalog. Revisit (add a manual entry screen alongside import) if the catalog turns out small and rarely changes.
7. **Launch capacity plans for dozens of orders per day**, not a handful ([decision-07](#)) — sizing too small was rejected as a way to guarantee an early bottleneck. Revisit once real order data from the first weeks after launch is in.
8. **No grocery-specific licensing or regulatory scope is assumed** ([decision-08](#)) — treated as standard local retail unless the client's local authority says otherwise. Revisit the moment a specific requirement is identified.
9. **Delivery agents confirm COD cash collection in-app at drop-off** ([decision-09](#)) — chosen over trust-based manual reconciliation for a cleaner, timestamped record. Revisit toward a hybrid if agents skip the confirmation step in practice.
10. **Orders that sit unconfirmed or uncollected past a timeout auto-release their reserved stock** ([decision-10](#)) — manual-only clearing was rejected as a way for stock to stay silently locked against a dead order. The exact timeout window is left for the System spec (stage 30d) to set as a concrete value; this decision fixes the *behavior*, not the number.
11. **Phase 2 (digital payments, wider service area, or both) stays undefined until the client explicitly asks for it** ([decision-11](#)) — pre-defining it now was rejected because the client was clear this is deliberate, not an oversight. Revisit the moment the client raises it.

## Open Questions

None remain open from this discovery round — all 11 were resolved in the follow-up above; see [Phase 1 Decisions](#phase-1-decisions). Any new open items that surface during `/daksh vision` or `/daksh brd` get numbered and tracked in this section's future revisions, per the usual Daksh convention of never silently deferring an open question.

## Approval

Approved by: Bhargav
Role:        PTL
Date:        2026-09-03
Hash:        eebc92565327�
