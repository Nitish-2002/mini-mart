---
daksh:
  type: system-spec
  subtype: null
  stage: "30d"
  module: CATALOG
---

# CATALOG System

[CATALOG's Solution spec](solution.md) named four business flows and explicitly deferred three things to this stage: exact import-row validation rules, the concrete low-stock threshold number, and the precise mechanism behind `reserve_stock()` that makes "first to confirm wins" actually true. This document answers all three, plus one real gap grounding against [system-architecture.md](../../system-architecture.md#backend-architecture) surfaced that neither upstream document anticipated: `release_stock(order_id)`'s own signature implies CATALOG can look something up by an order reference — but CATALOG owns no order data, so what exactly does it hold to make that call possible? [Logical Data, Ownership, and Invariants](#logical-data-ownership-and-invariants) resolves it. Everything here stays logical: no schemas, no libraries, no code — stage 50a (TRD) picks the concurrency primitive, the storage engine, the exact table layout.

<details>
<summary>Graph: What must CATALOG do after each action, and what does it hold to make that possible?</summary>

```items
---
id: 30d-catalog-system-cognition
title: CATALOG System — Behavior and Data
default_open_depth: 1
default_color_by: kind
color_palette_source: .daksh/color-palette.json
width: 95vw
---
id: 30d-catalog-system-cognition
title: CATALOG System — Behavior and Data
Components:
  - component-04 :: CATALOG_SERVICE | kind: component | summary: "Owns items, categories, stock quantities, and the reserve/release/availability contract every order depends on." | spec: [Testable Behaviors](system.md#testable-behaviors) | boundary: "Produces the browsing/import/stock interfaces and the in-process stock contract; consumes AUTH's authorization check for every write."
  - component-05 :: ORDERS_SERVICE | kind: component | summary: "Owns cart, checkout, order lifecycle — calls CATALOG in-process on every checkout, cancellation, and stale-order timeout." | spec: [Logical Interfaces](system.md#logical-interfaces-and-data-flow) | boundary: "Consumes CATALOG's stock contract; produces nothing CATALOG depends on."
StateMachines:
  - sm-catalog-reservation :: Stock reservation lifecycle | kind: statemachine | summary: "A single reserve_stock() call's own bookkeeping row — not an Item's state, a ledger entry scoped to one reservation attempt." | spec: [State Machines](system.md#state-machines) | entity: "StockReservation" | states: "active, released" | initial_state: "active" | terminal_states: "released" | transitions: "active->released (release_stock(reference) is called for this reservation's reference)" | invariants_per_state: "an active reservation has already been deducted from Item.stockQuantity — release is what adds it back, never a separate hold layered on top (decision-24, business-requirements.md)"
DataModels:
  - dm-catalog-item :: Item | kind: datamodel | summary: "A catalog item — name, price, current stock quantity, an optional photo reference, and the category it belongs to." | spec: [Logical Data, Ownership, and Invariants](system.md#logical-data-ownership-and-invariants) | shape: "name, price, stockQuantity (never negative), optional photo reference, category reference — no delete, per decision-85 (solution.md)"
  - dm-catalog-category :: Category | kind: datamodel | summary: "A catalog grouping, created implicitly the first time an import row or edit names one (decision-83, solution.md)." | spec: [Logical Data, Ownership, and Invariants](system.md#logical-data-ownership-and-invariants) | shape: "name — no separate admin-managed taxonomy beyond what's been used at least once"
  - dm-catalog-reservation :: Stock reservation ledger row | kind: datamodel | summary: "CATALOG's own bookkeeping for one reserve_stock() call — enough to reverse it later via release_stock(), without CATALOG ever knowing or caring what an 'order' is." | spec: [Logical Data, Ownership, and Invariants](system.md#logical-data-ownership-and-invariants) | shape: "an opaque caller-supplied reference, the item, the quantity deducted, current state (sm-catalog-reservation) — the reference is never interpreted, only matched back on release"
Interfaces:
  - interface-catalog-browse :: Catalog browsing & search interface | kind: interface | summary: "Public, no session required — category/keyword lookup returning items with live stock status." | spec: [Logical Interfaces](system.md#logical-interfaces-and-data-flow) | shape: "category or keyword in -> matching items out, each with a computed stock-status label" | version: "v1" | compatibility: additive
  - interface-catalog-manage :: Catalog & stock management interface | kind: interface | summary: "Admin-only — bulk import, single-item edit, walk-in sale recording, low-stock list." | spec: [Logical Interfaces](system.md#logical-interfaces-and-data-flow) | shape: "catalog file in -> per-row import summary out; single item edit in -> updated item out; walk-in sale in -> updated stock out; stock query in -> low-stock list out" | version: "v1" | compatibility: additive
Decisions:
  - decision-86 :: CATALOG keeps its own minimal reservation ledger, keyed by an opaque caller reference | kind: decision | summary: "reserve_stock() writes one dm-catalog-reservation row per call; release_stock() takes the same reference back and reverses every active row under it. CATALOG never joins against, validates, or interprets the reference as an order — it's an opaque key, resolving the tension in release_stock(order_id)'s own name without CATALOG actually owning order data." | spec: [Logical Data, Ownership, and Invariants](system.md#logical-data-ownership-and-invariants) | alternatives: "Stateless reserve/release — ORDERS re-supplies the same (item, quantity) pairs to release_stock() that it originally reserved, and CATALOG holds no ledger at all. Simpler for CATALOG, but pushes the bookkeeping burden onto ORDERS and doesn't match system-architecture.md's own release_stock(order_id) signature, which already implies a lookup CATALOG must be able to perform." | reversal_trigger: "The ledger table grows large enough (years of reservations, most long since released) that a real archival/pruning policy becomes necessary — not a Phase 1 concern at dozens-of-orders/day scale."
  - decision-87 :: Low-stock threshold is fixed at 5 units | kind: decision | summary: "The fixed default decision-25 (business-requirements.md) called for, made concrete: any item at or below 5 units flags on the low-stock list, regardless of category or historical velocity." | spec: [Business Rules and Validation](system.md#business-rules-and-validation) | alternatives: "A different flat number — 5 is the BRD's own illustrative example (decision-25) and no evidence yet suggests a different figure serves this catalog's actual item mix better." | reversal_trigger: "Admin reports the 5-unit line is meaningfully wrong for real items after launch — decision-25's own reversal_trigger already anticipates this exact correction path."
  - decision-88 :: Bulk-import rows carry a photo URL, not an uploaded file; single-item edit accepts a real upload | kind: decision | summary: "A CSV/spreadsheet row can't embed binary image data — bulk import expects a URL to an already-hosted photo (Admin supplies the link), while the lighter single-item edit path (ss-catalog-002, solution.md) accepts a direct upload to OBJECT_STORAGE, since that's one interactive form, not a batch file. Confirmed with the client rather than assumed." | spec: [Business Rules and Validation](system.md#business-rules-and-validation) | alternatives: "A parallel image-batch upload alongside the CSV (e.g. a zip of files, matched by filename) — supports Admin who has local photos with no hosting of their own, but adds real complexity (matching, format/size validation for many files at once) nothing in decision-84 (solution.md) sized as necessary yet." | reversal_trigger: "Admin has no practical way to get photos hosted at a URL before import, making the CSV-only-URL path a real adoption blocker."
  - decision-89 :: No audit trail for stock changes in Phase 1 | kind: decision | summary: "Walk-in sales and import-driven stock updates leave no change history — only the current stockQuantity is kept, unlike AUTH's agent-status log (decision-60). A stock discrepancy is caught by a physical recount, not a log review, at this scale." | spec: [Logical Data, Ownership, and Invariants](system.md#logical-data-ownership-and-invariants) | alternatives: "Log every stock change with who/when, mirroring decision-60 — real accountability value if discrepancies ever need investigating, but adds a new data model and write path for a need not yet demonstrated." | reversal_trigger: "A real, unexplained stock discrepancy happens after launch that a change log would have made traceable."
OpenQuestions:
  - oq-56 :: Does CATALOG need an audit trail for stock changes? | kind: openquestion | summary: "AUTH logs every Delivery Agent status change with who/when (decision-60) — should walk-in sales and import-driven stock updates get the same accountability treatment, or is the current stock value enough? — resolved, see decision-89." | spec: [CATALOG System Decisions](system.md#catalog-system-decisions)
  - oq-57 :: Is the CSV-URL-only photo path (decision-88) workable for this client, or does bulk import need to support a batch file upload too? | kind: openquestion | summary: "decision-88 assumes Admin can host photos at a URL before importing — confirmed with the client rather than assumed. — resolved, see decision-88." | spec: [CATALOG System Decisions](system.md#catalog-system-decisions)
component-04 -> interface-catalog-browse | relation: produces
component-04 -> interface-catalog-manage | relation: produces
decision-86 -> dm-catalog-reservation | relation: governs
decision-86 -> sm-catalog-reservation | relation: governs
decision-87 -> dm-catalog-item | relation: governs
decision-88 -> dm-catalog-item | relation: governs
decision-89 -> dm-catalog-item | relation: governs
decision-88 -> oq-57 | relation: decides
decision-89 -> oq-56 | relation: decides
```

</details>

> [!note]
> This graph carries 14 nodes across 6 groups — thinner than the 30-node floor other stages hit, consistent with how thin AUTH's own System spec (27 nodes) and CATALOG's own Solution spec (14 nodes) both ran: a single module's System spec has less raw material than a project-wide document. `component-04`/`component-05` are reused from `system-architecture.md` by the same IDs, deepened here rather than reinvented. Unlike AUTH, CATALOG owns no BRD-level multi-state entity (an Item's stock is a number, not an enum) — [sm-catalog-reservation](#) is the one real state machine here, and it's this stage's own internal bookkeeping construct ([decision-86](#)), not something the BRD named. Both open questions this draft raised were confirmed with the client in the same round; see [Open Questions](#open-questions).

## Scope and Solution Lineage

Every [SY-CATALOG-NNN](#testable-behaviors) below traces to the [SS-CATALOG-NNN](solution.md#business-flow-inventory) it makes testable: SY-001–003 to [SS-CATALOG-001](solution.md#business-flow-inventory), SY-004–008 to [SS-CATALOG-002](solution.md#business-flow-inventory), SY-009–011 to [SS-CATALOG-003](solution.md#business-flow-inventory), SY-012–014 to [SS-CATALOG-004](solution.md#business-flow-inventory).

One scope clarification the Solution spec left implicit: **CATALOG does not own order data, even though its own reservation ledger ([dm-catalog-reservation](#)) is keyed by something ORDERS supplies.** [Decision-86](#) below is the resolution — the reference is opaque to CATALOG, never validated or interpreted as an order, exactly the same boundary discipline [system-architecture.md](../../system-architecture.md#module-decomposition) already drew ("CATALOG never calls out to ORDERS"). CATALOG doesn't need to call out to learn anything about the reference — it just remembers it long enough to reverse a reservation later.

## Testable Behaviors

| SY | Behavior | Traces to |
|---|---|---|
| SY-CATALOG-001 | System returns items filtered by category, each carrying a computed stock-status label. | SS-CATALOG-001 |
| SY-CATALOG-002 | System returns items whose name matches a keyword search. | SS-CATALOG-001 |
| SY-CATALOG-003 | System computes stock status (`in_stock` / `low_stock` / `out_of_stock`) live from current `stockQuantity` against the 5-unit threshold (decision-87) — never a cached or stale value. | SS-CATALOG-001 |
| SY-CATALOG-004 | System validates each bulk-import row independently; a failing row is rejected and reported without blocking the rest of the batch. | SS-CATALOG-002 |
| SY-CATALOG-005 | System matches an import row to an existing item by exact name within the same category (decision-82, solution.md); anything else creates a new item. | SS-CATALOG-002 |
| SY-CATALOG-006 | System creates a category the first time an import row or manual edit names one that doesn't already exist (decision-83, solution.md). | SS-CATALOG-002 |
| SY-CATALOG-007 | System accepts an optional photo per item — a URL on bulk-import rows, a direct upload on the single-item edit path (decision-88). | SS-CATALOG-002 |
| SY-CATALOG-008 | System lets Admin edit one item's name, price, category, stock, or photo directly, without a full re-import. | SS-CATALOG-002 |
| SY-CATALOG-009 | System deducts a walk-in sale's quantity from the same `stockQuantity` online orders draw from. | SS-CATALOG-003 |
| SY-CATALOG-010 | System rejects a walk-in sale that would take `stockQuantity` negative — it fails honestly, it doesn't clamp to zero or oversell. | SS-CATALOG-003 |
| SY-CATALOG-011 | System flags every item at or below the 5-unit threshold (decision-87) on the low-stock list without Admin querying for it. | SS-CATALOG-003 |
| SY-CATALOG-012 | System reserves a requested quantity only if currently available, deducting it immediately and atomically — two simultaneous requests for the same last unit never both succeed (decision-24, business-requirements.md). | SS-CATALOG-004 |
| SY-CATALOG-013 | System releases every active reservation under a given reference back to the pool on request. | SS-CATALOG-004 |
| SY-CATALOG-014 | System reports an item's current availability without mutating anything. | SS-CATALOG-004 |

## Business Rules and Validation

- An import row is valid only if: name is a non-empty string, price is a positive number, stock is a non-negative integer, and category is a non-empty string (auto-created per [decision-83](solution.md#business-states-decisions-and-recovery) if new). A photo, when present, must be a URL, not inline binary data (decision-88) — its accessibility is not validated at this stage (that's a network-level concern, stage 50a's job).
- [dm-catalog-item](#)'s `stockQuantity` is never negative — enforced identically whether the deduction comes from a walk-in sale (SY-CATALOG-010) or a reservation (SY-CATALOG-012); both fail the attempt rather than allow it.
- [Reserve_stock()](#) must be atomic with respect to concurrent callers: the check ("is enough available") and the deduction happen as one indivisible operation, so two callers racing for the same last unit can never both see "available" and both succeed — this is the logical requirement solution.md's handoff asked for; the concrete mechanism (row lock, atomic conditional update, or otherwise) is stage 50a's choice, not fixed here.
- The low-stock threshold ([decision-87](#)) is one fixed number across every item and category — no per-item override exists in Phase 1, matching [decision-25](../../business-requirements.md#brd-decisions)'s own model-level call.

## State Machines

See the graph above for [sm-catalog-reservation](#)'s two states and its one transition. This is CATALOG's only state machine — an Item itself has no enum-valued lifecycle (its stock is a plain number), unlike AUTH's Delivery Agent status. [Decision-86](#) is the business call made explicitly at this stage: CATALOG keeps just enough of its own bookkeeping to make `release_stock()` reversible, without ever needing to know what an order is.

## Logical Data, Ownership, and Invariants

CATALOG owns three data shapes, all described in the graph above: [dm-catalog-item](#), [dm-catalog-category](#), and [dm-catalog-reservation](#). Ownership invariants:

- Only CATALOG reads or writes any of these three shapes — AUTH and ORDERS never touch CATALOG's tables directly, they call CATALOG's interfaces or its in-process contract ([system-architecture.md's Module Decomposition](../../system-architecture.md#module-decomposition)).
- [dm-catalog-item](#) rows are never deleted ([decision-85](solution.md#business-states-decisions-and-recovery)) — a discontinued item is left at `stockQuantity: 0` permanently, which is also what keeps historical `OrderLine` references (ORDERS' own data, per the BRD's data model) from ever pointing at a row that no longer exists.
- [dm-catalog-reservation](#) rows are CATALOG's own internal ledger, never exposed through [interface-catalog-browse](#) or [interface-catalog-manage](#) — they exist purely so `release_stock()` has something to reverse. The `reference` field is opaque: CATALOG stores and matches it back exactly, never parses, validates, or joins against it as if it were a real order ([decision-86](#)).
- `reserve_stock()` is called once per line item, so a single caller-supplied reference can own multiple active [dm-catalog-reservation](#) rows (one per item in a multi-item checkout) — `release_stock(reference)` reverses all of them together, not just one.

## Logical Interfaces and Data Flow

Two interfaces, both producer CATALOG ([component-04](#)) — see the graph for shape/version/compatibility: [interface-catalog-browse](#) (public, no session — the storefront's category/search/live-stock view) and [interface-catalog-manage](#) (Admin-only — import, edit, walk-in sale, low-stock list). Both are additive-compatible v1 — a new field never breaks an existing frontend caller.

**Failure shape**, in business terms (no HTTP status codes, that's TRD's job): [interface-catalog-browse](#) never fails on an unmatched search or an empty category — it returns zero items, since "nothing matched" is a normal outcome, not an error. [interface-catalog-manage](#)'s writes fail per-row (import) or per-request (edit, walk-in sale, reservation) with a specific reason — never a silent partial success beyond what SY-CATALOG-004's per-row independence already allows.

**In-process contract (no Interface node, per [decision-33](../../system-architecture.md#architecture-decisions)):** [component-05](#) (ORDERS) calls `reserve_stock()` / `release_stock()` / `get_availability()` directly, in-process, on every checkout attempt, cancellation, and stale-order timeout — this is [system-architecture.md](../../system-architecture.md#module-interactions-and-versioned-logical-interfaces)'s existing contract, made concrete by [decision-86](#)'s reservation-ledger resolution. CATALOG also calls [AUTH](../../implementation/AUTH/solution.md)'s authorization check in-process before honoring any [interface-catalog-manage](#) write — the same contract AUTH's own [SY-AUTH-013](../../implementation/AUTH/system.md#testable-behaviors) already fixed.

**Cross-module data flow for stock reservation (resolves a real gap found grounding against system-architecture.md):** that document's own `release_stock(order_id)` signature implies CATALOG can look something up by an order reference — but [CATALOG's Solution spec](solution.md#module-responsibilities-boundaries-and-dependencies) is explicit that CATALOG owns no order data and never calls out to ORDERS. [Decision-86](#) resolves this without breaking either constraint: CATALOG keeps its own minimal reservation ledger keyed by whatever reference ORDERS supplies (in practice, ORDERS' own order id — but CATALOG never knows or cares that it is one). CATALOG stays a pure answerer, exactly as [solution.md's Integration Intent](solution.md#integration-intent) already described it.

## Module Quality Budgets

Inherited unchanged from [system-architecture.md](../../system-architecture.md#project-wide-quality-requirements): standard ~2s page-load target, no formal uptime SLA, no load-testing requirement at Phase 1 volume. Tightened for CATALOG specifically:

- **Stock-status freshness:** [SY-CATALOG-003](#)'s "live" stock status must reflect the most recent successful reservation or release — a shopper should never see "in stock" for an item another shopper just bought the last unit of moments ago, within normal request latency.
- **Reservation overhead:** `reserve_stock()` runs on every checkout attempt across ORDERS — its added latency should be negligible on top of whatever else checkout is doing, the same sub-100ms framing AUTH's own authorization check budget uses.
- **Import throughput:** no formal target — Phase 1's catalog size (a single store) doesn't need one; revisit if the client's real catalog size makes a full re-import noticeably slow.

## Verification Obligations

| Behavior / Budget | Verification approach (business terms, not test code) |
|---|---|
| SY-CATALOG-001–003 (browsing/search) | Exercise category filtering and keyword search against a seeded catalog; confirm stock-status labels match a freshly-reserved/released item's real quantity, not a stale value. |
| SY-CATALOG-004–008 (import/edit) | Import a file with a mix of valid and invalid rows; confirm valid rows succeed and invalid rows are reported individually, not blocking the batch. Confirm a re-imported row with the same name+category updates rather than duplicates, and a new category name auto-creates. Confirm both photo paths (URL on import, upload on edit). |
| SY-CATALOG-009–011 (stock management) | Record a walk-in sale and confirm the online-visible stock count drops by the same amount; attempt one that would go negative and confirm it's rejected; confirm an item at exactly the 5-unit threshold appears on the low-stock list. |
| SY-CATALOG-012–014 (reservation contract) | Exercise `reserve_stock()` against an item with exactly one unit left from two simultaneous callers — confirm exactly one succeeds; confirm `release_stock()` restores a previously-reserved quantity; confirm `get_availability()` never mutates state. |

Formal test cases with setup/data/expected-result live in stage 50b (Test Specification), not here — this table is the obligation, not the test itself.

## CATALOG System Decisions

Four decisions this stage introduces to fill in what Solution left implicit. [Decision-86](#) and [decision-87](#) are reasoned defaults within this stage's own remit, matching how AUTH's System stage resolved its own cross-module tension directly. [Decision-88](#) and [decision-89](#) also resolve this stage's two open questions, confirmed with the client in the same drafting round:

1. **CATALOG keeps its own minimal reservation ledger, keyed by an opaque reference** ([decision-86](#)) — resolves `release_stock(order_id)`'s own implied lookup without CATALOG ever owning order data. Revisit only if ledger growth becomes a real archival concern.
2. **Low-stock threshold is fixed at 5 units** ([decision-87](#)) — the BRD's own illustrative example, made concrete. Revisit if real usage shows it's wrong for this catalog's actual items.
3. **Bulk import takes a photo URL; single-item edit takes a real upload** ([decision-88](#)) — the only path a CSV can realistically carry image data through, confirmed workable for this client. Revisit if Admin has no practical way to host photos before importing.
4. **No audit trail for stock changes in Phase 1** ([decision-89](#)) — unlike AUTH's agent-status log, walk-in sales and import updates leave no change history; a discrepancy is caught by recount, not log review, at this scale. Revisit if a real unexplained discrepancy happens after launch.

## Open Questions

None remain open from this System draft. [Oq-56](#) (stock audit trail) resolved into [decision-89](#): no audit trail in Phase 1. [Oq-57](#) (bulk photo transport) resolved into [decision-88](#): CSV-URL-only is workable for this client. See [CATALOG System Decisions](#catalog-system-decisions) for the reasoning behind each.

## Approval

Approved by: Bhargav
Role:        PTL
Date:        2026-09-05
Hash:        c7d739f693da…
