---
daksh:
  type: solution-spec
  subtype: null
  stage: "30c"
  module: CATALOG
---

# CATALOG Solution

CATALOG is the second module in Mini Mart's build order ([roadmap.md](../../implementation-roadmap.md#module-dependency-graph), [decision-47](../../implementation-roadmap.md#roadmap-decisions)) — it answers one question every other module and every shopper depends on: *what does Mini Mart sell, and how much of it is actually available right now?* This document traces to the BRD's [UC-002](../../business-requirements.md#uc-002-end-user-browses-and-searches-the-catalog), [UC-006](../../business-requirements.md#uc-006-admin-manages-the-catalog), and [UC-007](../../business-requirements.md#uc-007-admin-manages-stock) — the three use cases [system-architecture.md's Module Decomposition](../../system-architecture.md#module-decomposition) already assigns to CATALOG's ownership — plus the cross-cutting `reserve_stock()` / `release_stock()` / `get_availability()` contract that same document fixed as CATALOG's one obligation to ORDERS. It stays at business-flow level — no screens (stage 40's job), no schemas or transport (stage 30d/50a's job) — but adds real business substance the BRD left implicit: what actually makes two catalog rows "the same item" on re-import, whether categories exist before or because of an import, whether an item can ever leave the catalog outright, and what "available right now" means for a module ORDERS calls in-process, never over the network.

<details>
<summary>Graph: What problem does CATALOG solve, and how do responsibilities and information move through it?</summary>

```items
---
id: 30c-catalog-solution-cognition
title: CATALOG Solution — Responsibility Flow
default_open_depth: 1
default_color_by: kind
color_palette_source: .daksh/color-palette.json
width: 95vw
---
id: 30c-catalog-solution-cognition
title: CATALOG Solution — Responsibility Flow
Users:
  - user-01 :: Admin | kind: user | summary: "Runs the mart's catalog, pricing, and stock, and oversees orders and delivery agents." | spec: [Actors, Needs, Outcomes](solution.md#actors-needs-and-expected-outcomes) | role: "Mart Admin/Owner" | audience: client | user_type: operator | status: placeholder
  - user-03 :: End User | kind: user | summary: "Browses the catalog, places an order, and pays cash on delivery when it arrives." | spec: [Actors, Needs, Outcomes](solution.md#actors-needs-and-expected-outcomes) | role: "Shopper/Customer" | audience: end_customer | user_type: consumer | status: placeholder
Flows:
  - ss-catalog-001 :: Catalog browsing and search | kind: flow | summary: "A shopper finds items by category or keyword, with live stock status on every item, before adding anything to cart." | spec: [Business-Flow Inventory](solution.md#business-flow-inventory) | actor: "End User" | trigger: "Shopper opens the storefront or searches" | outcome: "Shopper finds an item and can add it to cart, or sees it's out of stock without it disappearing"
  - ss-catalog-002 :: Catalog maintenance via bulk import | kind: flow | summary: "Admin uploads a spreadsheet/CSV to create or update items in bulk, each optionally carrying a photo; a lighter single-item edit path exists alongside it." | spec: [Business-Flow Inventory](solution.md#business-flow-inventory) | actor: "Admin" | trigger: "Admin uploads a catalog file, or edits one item directly" | outcome: "Catalog reflects current items, prices, categories, and photos; a per-row import summary reports success/failure"
  - ss-catalog-003 :: Stock management across two sales channels | kind: flow | summary: "Admin records walk-in sales against the same stock pool online orders draw from, and sees low-stock items flagged without asking." | spec: [Business-Flow Inventory](solution.md#business-flow-inventory) | actor: "Admin" | trigger: "A walk-in sale happens, or admin checks stock levels" | outcome: "Stock count stays accurate across both channels; items at or below the threshold are flagged"
  - ss-catalog-004 :: Stock reservation and release for order fulfillment | kind: flow | summary: "The in-process contract ORDERS calls on every checkout, cancellation, and stale-order timeout — CATALOG never initiates this, only answers it." | spec: [Integration Intent](solution.md#integration-intent) | actor: "System (invisible to the end user)" | trigger: "ORDERS attempts a checkout, a cancellation, or a stale-order timeout fires" | outcome: "Stock is reserved (checkout succeeds) or found insufficient (checkout fails honestly), or previously-reserved stock is released back to the pool"
Decisions:
  - decision-82 :: Bulk-import matches existing items by exact name within the same category | kind: decision | summary: "A re-imported row updates an existing item only if its name matches exactly (case-sensitive) within the same category already on file; anything else creates a new item." | spec: [Business States, Decisions, and Recovery](solution.md#business-states-decisions-and-recovery) | alternatives: "A separate admin-assigned SKU/code as the real identity key — more robust against renames and typos, but adds a field and a workflow step (assigning codes) nothing in the BRD's data model or FR-014 asked for." | reversal_trigger: "Admin reports frequent accidental duplicate items from minor name variations (extra space, different capitalization) that a code-based identity would have prevented."
  - decision-83 :: Categories are created implicitly from import content, not pre-defined by Admin | kind: decision | summary: "The first time a category name appears in an import file (or a manual item edit), CATALOG creates it; there is no separate \"manage categories\" step Admin must do first." | spec: [Business States, Decisions, and Recovery](solution.md#business-states-decisions-and-recovery) | alternatives: "Admin pre-defines the category list before any import can reference one — gives tighter control over the taxonomy, but adds a setup step before decision-06's bulk-import path (stage 00) can be used at all, for a Phase 1 catalog small enough that a typo'd category is easy to notice and fix." | reversal_trigger: "The catalog grows large enough, or categories drift inconsistent enough (near-duplicate names), that ungoverned auto-creation becomes a real navigation problem for shoppers."
  - decision-84 :: Item photos are in scope for Phase 1, reusing AUTH's object-storage path | kind: decision | summary: "The catalog carries an optional photo per item, resolving stage 00's decision-06 (which named photos) in decision-06's own favor against the BRD's FR-014/data model, which had silently dropped it — a real drift this stage closes by confirming with the client rather than assuming the BRD's silence was deliberate. Photos are stored the same way AUTH's agent-registration photo is (OBJECT_STORAGE, per system-architecture.md), not a new mechanism." | spec: [Business States, Decisions, and Recovery](solution.md#business-states-decisions-and-recovery) | alternatives: "No photos, siding with the BRD's own data model as the more recent/specific source — simpler for Phase 1, but overrides an explicit stage-00 client decision on the strength of an omission that was never confirmed as intentional." | reversal_trigger: "The upload/storage path proves a real build-time cost the client didn't anticipate when confirming this, or bulk-import-with-images turns out meaningfully harder than a plain CSV."
  - decision-85 :: An item is never deleted, only driven to and left at zero stock | kind: decision | summary: "Phase 1 has no \"remove item from catalog\" action — a discontinued item stays visible with `stockQuantity: 0`, reading as permanently out of stock, consistent with UC-002's own \"digitize, don't hide\" model for temporarily out-of-stock items." | spec: [Business States, Decisions, and Recovery](solution.md#business-states-decisions-and-recovery) | alternatives: "A real delete/archive action — cleaner for a catalog with genuine churn, but the BRD never asked for one, and deleting an Item that historical OrderLines still reference (per the BRD's own data model) would orphan past orders' line-item detail." | reversal_trigger: "Admin reports the catalog getting cluttered with permanently-discontinued items that a real archive action would clean up."
OpenQuestions:
  - oq-52 :: What makes a bulk-import row match an existing item vs. create a new one? | kind: openquestion | summary: "FR-014 says import can create or update items, but neither it nor the BRD's data model names an identity key. — resolved, see decision-82." | spec: [CATALOG Decisions](solution.md#catalog-decisions)
  - oq-53 :: Are categories pre-defined by Admin, or created automatically from import content? | kind: openquestion | summary: "Neither the BRD nor vision's decision-18 says who/what creates a Category record the first time. — resolved, see decision-83." | spec: [CATALOG Decisions](solution.md#catalog-decisions)
  - oq-54 :: Does Phase 1's catalog include item photos? | kind: openquestion | summary: "Stage 00's decision-06 mentions photos; the BRD's FR-014 and data model don't. — resolved, see decision-84." | spec: [CATALOG Decisions](solution.md#catalog-decisions)
  - oq-55 :: Can Admin ever remove an item from the catalog outright? | kind: openquestion | summary: "The BRD describes creating/updating items via import and editing price/stock directly, but never removing one. — resolved, see decision-85." | spec: [CATALOG Decisions](solution.md#catalog-decisions)
user-03 -> ss-catalog-001 | relation: experiences
user-01 -> ss-catalog-002 | relation: owns
user-01 -> ss-catalog-003 | relation: owns
decision-82 -> ss-catalog-002 | relation: governs
decision-83 -> ss-catalog-002 | relation: governs
decision-84 -> ss-catalog-002 | relation: governs
decision-85 -> ss-catalog-003 | relation: governs
decision-82 -> oq-52 | relation: decides
decision-83 -> oq-53 | relation: decides
decision-84 -> oq-54 | relation: decides
decision-85 -> oq-55 | relation: decides
```

</details>

> [!note]
> This graph carries 14 nodes across 4 groups — thinner than the 30-node floor other stages hit, matching how thin AUTH's own Solution spec (17 nodes) ran: a single module's Solution has less raw material than a project-wide BRD or Architecture. `Users` are reused from the BRD by the same IDs; only Admin and End User appear — Delivery Agent never touches CATALOG directly. `ss-catalog-004` (the stock-reservation contract) carries no `User` edge, matching AUTH's own honest treatment of `ss-auth-005` — it's genuinely invisible infrastructure no human directly experiences. All 4 open questions this draft raises are answered by this same draft's 4 decisions, pending confirmation (see [Open Questions](#open-questions)).

## Scope and BRD Lineage

CATALOG owns items, categories, and stock quantities — nothing about orders, payment, or delivery ([system-architecture.md's Module Decomposition](../../system-architecture.md#module-decomposition)). Every business flow below traces to a BRD use case: [ss-catalog-001](#) to [UC-002](../../business-requirements.md#uc-002-end-user-browses-and-searches-the-catalog), FR-004–006; [ss-catalog-002](#) to [UC-006](../../business-requirements.md#uc-006-admin-manages-the-catalog), FR-014–015, FR-027; [ss-catalog-003](#) to [UC-007](../../business-requirements.md#uc-007-admin-manages-stock), FR-016–017; [ss-catalog-004](#) to FR-008 and [decision-24](../../business-requirements.md#brd-decisions) (stock reserved at confirmation, not add-to-cart), which is ORDERS' decision to make but CATALOG's contract to fulfill. Nothing here restates those sources without adding business substance — the additions are: what makes an import row match an existing item ([decision-82](#)), where categories come from ([decision-83](#)), whether photos exist ([decision-84](#)), and whether an item can ever truly leave the catalog ([decision-85](#)).

## Actors, Needs, and Expected Outcomes

**[Admin](#) ([user-01](#))** needs to keep the catalog and stock count trustworthy with the least possible manual effort — before this product, both lived on paper or in a register, per [client-context.md](../../client-context.md#phase-1-decisions)'s stage-00 framing. Expected outcome: a bulk-import path that handles the catalog's bulk ([ss-catalog-002](#)), and a stock view that already knows what's low without Admin hunting for it ([ss-catalog-003](#)).

**[End User](#) ([user-03](#))** needs to trust that what they see is what they can actually buy — an item that shows in stock but turns out unavailable at checkout is a broken promise, not a minor bug. Expected outcome: a searchable, categorized catalog ([ss-catalog-001](#)) where stock status is genuinely current, not a stale snapshot from the last sync.

## Module Responsibilities, Boundaries, and Dependencies

**Owns:** item and category data; stock quantities and the one operation allowed to change them; bulk catalog import and its per-row validation; the low-stock threshold check; the `reserve_stock()` / `release_stock()` / `get_availability()` contract every stock-affecting action in the system ultimately calls through.

**Does not own:** orders, carts, checkout, payment, or delivery ([system-architecture.md](../../system-architecture.md#module-decomposition)) — CATALOG answers "what exists and how much," never "who bought it" or "where is it going." CATALOG also never calls out to ORDERS — the dependency runs one way only, matching [system-architecture.md's Backend Architecture](../../system-architecture.md#backend-architecture) ("CATALOG never calls out to ORDERS").

**Dependencies:** [AUTH](../../implementation/AUTH/solution.md) — every write path (import, manual edit, walk-in sale) needs Admin's session resolved first, per [decision-47](../../implementation-roadmap.md#roadmap-decisions)'s build order (CATALOG waits for AUTH to fully finish). Browsing ([ss-catalog-001](#)) needs no session at all — it's public, same as AUTH's own [SS-AUTH-001](../../implementation/AUTH/solution.md#business-flow-inventory) note that browsing requires no account.

## Business-Flow Inventory

- **[SS-CATALOG-001](#) — Catalog browsing and search.** Category and keyword search over the same live data Admin edits — there is no separate "public" copy of the catalog that lags behind. [Decision-18](../../vision.md#vision-decisions) (vision.md) already fixed that categories-plus-search is the structure; this flow is what "browsing" actually means in business terms: find, view, see real stock status, add to cart or don't.
- **[SS-CATALOG-002](#) — Catalog maintenance via bulk import.** [Decision-06](../../client-context.md#phase-1-decisions) (stage 00) fixed bulk import over one-by-one entry, and named photos as part of it; this flow is the business behavior around it — upload, per-row validation (FR-015), a summary of what succeeded and what didn't — plus the lighter single-item edit path FR-014 mentions almost in passing. [Decision-82](#) and [decision-83](#) fix two things the BRD left unstated: what makes a row match an existing item, and where a category comes from the first time it's used. [Decision-84](#) restores photos to scope after confirming stage 00's original intent with the client, against the BRD's own silence.
- **[SS-CATALOG-003](#) — Stock management across two sales channels.** [Decision-05](../../client-context.md#phase-1-decisions) (stage 00) fixed that walk-in and online sales share one stock pool; this flow is Admin's side of keeping that pool honest — recording a walk-in sale, and seeing the low-stock list [decision-25](../../business-requirements.md#brd-decisions) already fixed the threshold model for.
- **[SS-CATALOG-004](#) — Stock reservation and release for order fulfillment.** Not a flow Admin or End User ever directly triggers — it's what ORDERS calls in-process on every checkout attempt, cancellation, and stale-order timeout ([system-architecture.md](../../system-architecture.md#backend-architecture)'s `reserve_stock()` / `release_stock()` / `get_availability()` contract). This is the business behavior [decision-24](../../business-requirements.md#brd-decisions) (stock reserved at confirmation, not cart-add) actually rests on — CATALOG is the module that makes "first to confirm wins" (BRD's own phrasing) a real, enforced outcome rather than a hopeful description.

## Integration Intent

CATALOG is one of three producers of [interface-01](../../system-architecture.md#module-interactions-and-versioned-logical-interfaces) `BACKEND_API` (its `/v1/catalog/*` route prefix), consumed by every frontend view group that needs catalog data — the storefront (browsing) and the admin view (import, stock, edit). Internally, CATALOG calls [AUTH](../../implementation/AUTH/solution.md)'s `get_current_user()` / `require_role()` to resolve who's asking before honoring any write ([ss-catalog-002](#), [ss-catalog-003](#)) — the same in-process contract AUTH's own [SS-AUTH-005](../../implementation/AUTH/solution.md#business-flow-inventory) already fixed. In the other direction, ORDERS calls CATALOG's `reserve_stock()` / `release_stock()` / `get_availability()` in-process ([ss-catalog-004](#)) — CATALOG is a pure answerer here, never an initiator: it has no knowledge of why a reservation is being made or released, only whether it can be. CATALOG has no external, non-Mini-Mart dependency of its own — unlike AUTH (EMAIL_PROVIDER), nothing in CATALOG's scope talks to a third-party system.

## High-Level Payload Intent

No field names or schemas — the shape of information each flow needs or produces, in business terms:

- **[SS-CATALOG-001](#)** needs: a category or search keyword. Produces: a list of matching items, each carrying its name, price, and a stock-status label (in stock / low stock / out of stock).
- **[SS-CATALOG-002](#)** needs: a catalog file (name, price, category, stock, and an optional photo per row) or a single item's edited fields. Produces: created/updated item records and a per-row import summary (succeeded/failed with a reason), or an updated single item.
- **[SS-CATALOG-003](#)** needs: a walk-in sale's item and quantity, or nothing (a stock-level check). Produces: an updated stock quantity, and a low-stock list of items at or below the threshold.
- **[SS-CATALOG-004](#)** needs: an item and a quantity to reserve, or an order reference to release. Produces: a reservation success/failure outcome, a released quantity, or a current availability figure — never a business-level reason for the caller's request, since CATALOG doesn't know what ORDERS is doing with the answer.

## Business States, Decisions, and Recovery

CATALOG owns no multi-state entity lifecycle the way AUTH owns Delivery Agent status — an Item's only meaningful state is its stock quantity (a number, not an enum) and the derived, never-stored [stock status label](../../business-requirements.md#domain-vocabulary) (`in_stock` / `low_stock` / `out_of_stock`, per [decision-25](../../business-requirements.md#brd-decisions)). The four decisions below fill in what the BRD left as implicit business rules, not a state machine:

- **[Decision-82](#)** — a bulk-import row matches an existing item by exact name within the same category; anything else is treated as a new item, matching FR-014's plain "create or update" without inventing a separate identity key the BRD never asked for.
- **[Decision-83](#)** — a category is created the first time an import row (or manual edit) names one; there's no separate "define categories first" step blocking [decision-06](../../client-context.md#phase-1-decisions)'s bulk-import path.
- **[Decision-84](#)** — item photos are in scope after all, resolving a real drift: stage 00's decision-06 named photos, but the BRD's own FR-014 and data model (`Item{id, name, price, stockQuantity}`) never carried one forward. Confirmed with the client rather than silently assuming either side was right; photos reuse the OBJECT_STORAGE path AUTH already provisions for agent registration, not a new mechanism.
- **[Decision-85](#)** — an item is never deleted, only left at zero stock permanently, consistent with UC-002's "digitize, don't hide" model and the BRD's data model already having `OrderLine` reference `Item` by relationship — deleting an Item a past order's line item still points to would orphan that order's history.

Failure and recovery intent, in business terms (not error codes or schemas):
- **An import row fails validation** ([SS-CATALOG-002](#)): already fixed at BRD level (FR-015, AC-015) — that row is rejected and reported, the rest of the batch still succeeds.
- **A walk-in sale would take stock negative** ([SS-CATALOG-003](#)): rejected, not clamped to zero and not allowed to go negative — the same integrity principle FR-008 already applies to online checkout (an unavailable item fails honestly, it doesn't silently oversell), applied here for symmetry rather than left as a new gap.
- **ORDERS calls `reserve_stock()` for more than is available** ([SS-CATALOG-004](#)): the reservation fails and CATALOG reports the shortfall — this is [decision-24](../../business-requirements.md#brd-decisions)'s "first to confirm wins" made concrete; CATALOG never partially reserves or guesses.

## Handoff Boundaries

**To stage 40 (Experience Design, selected for CATALOG per [decision-44](../../implementation-roadmap.md#build-order)):** every screen implied by the three human-facing flows above — the storefront's category/search browsing view (now including a photo per item, per [decision-84](#)), Admin's bulk-import upload-and-summary screen, Admin's single-item edit path (including a photo field), and Admin's stock/low-stock view. Design also owns exactly how a low-stock notice and an out-of-stock state read to a shopper without making the item disappear, per UC-002's own "digitize, don't hide" framing, and how a missing photo renders (a placeholder, not a broken image).

**To stage 30d (System, required):** the exact validation rules for an import row (what makes a price or stock value invalid, beyond "not present"); the concrete low-stock threshold number ([decision-25](../../business-requirements.md#brd-decisions) fixed the model, a fixed default, not the exact figure); the precise concurrency mechanism behind `reserve_stock()` that makes "first to confirm wins" actually true under simultaneous checkouts, not just described; the exact shape of the low-stock list and import-summary data; and the mechanics of how a bulk-import row's photo reference gets from spreadsheet cell to OBJECT_STORAGE (a URL column pointing at an already-uploaded file, versus an inline upload alongside the import — this stage fixes only that a photo exists, not how it arrives).

## CATALOG Decisions

The 4 open questions this draft raised were confirmed with the client in the same round this Solution was drafted — no separate follow-up was needed.

1. **Import matches existing items by exact name within category** ([decision-82](#)) — the simplest identity rule that satisfies FR-014's "create or update" without a new field. Revisit if accidental duplicates from name variations prove frequent.
2. **Categories are created implicitly from import/edit content** ([decision-83](#)) — no separate setup step blocks decision-06's bulk-import path. Revisit if the catalog grows large enough that ungoverned category names become a navigation problem.
3. **Item photos are in scope for Phase 1** ([decision-84](#)) — the client confirmed stage 00's original intent stands; the BRD's silence on photos was an omission to close, not a deliberate cut. Photos reuse AUTH's existing OBJECT_STORAGE path. Revisit if the upload/storage or bulk-import-with-images work proves a real cost surprise.
4. **Items are never deleted, only left at zero stock** ([decision-85](#)) — avoids orphaning historical OrderLine references. Revisit if catalog clutter from discontinued items becomes a real problem.

None remain open from this Solution draft. [Oq-52](#) (import-row identity) resolved into [decision-82](#): exact name match within category. [Oq-53](#) (category creation) resolved into [decision-83](#): auto-created from import/edit content. [Oq-54](#) (item photos) resolved into [decision-84](#): in scope for Phase 1, reusing AUTH's OBJECT_STORAGE path. [Oq-55](#) (item removal) resolved into [decision-85](#): never deleted, only left at zero stock. See [CATALOG Decisions](#catalog-decisions) for the reasoning behind each.

## Approval

Approved by: Bhargav
Role:        PTL
Date:        2026-09-05
Hash:        967b3600c254…
