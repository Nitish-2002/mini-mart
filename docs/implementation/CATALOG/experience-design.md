---
daksh:
  type: experience-design
  subtype: null
  stage: "40"
  module: CATALOG
---

# CATALOG Experience Design Spec

CATALOG's [Solution](solution.md) and [System](system.md) specs fixed four business flows and their logical behavior; this document gives them a real frontend contract — screens, states, and interaction detail an engineer can build from without guessing. It covers both of CATALOG's roles: End User's browsing/search storefront, and Admin's bulk-import, single-item edit, and stock-management screens. Fidelity is a real interactive HTML prototype, matching [AUTH's own precedent](../AUTH/experience-design.md#prototype-evidence) — see [Prototype Evidence](#prototype-evidence) for the live artifact. Mini Mart already has a design system from AUTH's own spec ([decision-61](../AUTH/experience-design.md#4a-primary-design-primitives)–[decision-63](../AUTH/experience-design.md#4a-primary-design-primitives)); this spec inherits it wholesale rather than starting over, per vision's [decision-13](../../vision.md#vision-decisions) (one integrated product, not a fresh brand per module).

<details>
<summary>Graph: How do primitives, design tasks, and executed screens fit together?</summary>

```items
---
id: 40-catalog-design-cognition
title: CATALOG Experience Design — Primitives, Tasks, Screens
default_open_depth: 1
default_color_by: kind
color_palette_source: .daksh/color-palette.json
width: 95vw
---
id: 40-catalog-design-cognition
title: CATALOG Experience Design — Primitives, Tasks, Screens
Users:
  - user-01 :: Admin | kind: user | summary: "Runs the mart's catalog, pricing, and stock." | spec: [Personas and Context of Use](experience-design.md#personas-and-context-of-use) | role: "Mart Admin/Owner" | audience: client | user_type: operator | status: placeholder
  - user-03 :: End User | kind: user | summary: "Browses the catalog and places an order." | spec: [Personas and Context of Use](experience-design.md#personas-and-context-of-use) | role: "Shopper/Customer" | audience: end_customer | user_type: consumer | status: placeholder
Constraints:
  - constraint-catalog-image :: Item photo display contract | kind: constraint | summary: "Fixed aspect ratio, lazy-loaded, and a generic placeholder icon when an item has no photo (decision-84, solution.md, made photos optional) — never a broken image." | spec: [4A Primary Design Primitives](experience-design.md#4a-primary-design-primitives) | source: "Created here — AUTH never displayed a photo, only uploaded one."
Components:
  - component-catalog-image :: Item photo display | kind: component | summary: "Fixed-aspect-ratio image slot with a lazy-loaded photo or a placeholder icon." | spec: [4A Primary Design Primitives](experience-design.md#4a-primary-design-primitives) | boundary: "Atomic control — display only, no upload behavior (that's component-catalog-fileupload and the single-item edit form's own upload field)."
  - component-catalog-stepper :: Quantity stepper | kind: component | summary: "A +/- numeric control for entering a walk-in sale quantity, bounded at 1 and at current available stock." | spec: [4A Primary Design Primitives](experience-design.md#4a-primary-design-primitives) | boundary: "Atomic control, used only by ds-catalog-008 (walk-in sale)."
  - component-catalog-chip :: Category chip | kind: component | summary: "A tappable, selectable pill for one category — visually distinct from AUTH's read-only StatusBadge pill, since this one is interactive." | spec: [4A Primary Design Primitives](experience-design.md#4a-primary-design-primitives) | boundary: "Atomic control, used by ds-catalog-001's category navigation."
  - component-catalog-table :: Data table | kind: component | summary: "The one tabular-data control CATALOG needs — sortable columns, row-level actions — for Admin's stock list and import summary. AUTH never needed this; every AUTH screen was single-record." | spec: [4A Primary Design Primitives](experience-design.md#4a-primary-design-primitives) | boundary: "Atomic control, reused by ds-catalog-005 and ds-catalog-007; flagged for ORDERS' own future order-list screens."
  - component-catalog-fileupload :: File upload control | kind: component | summary: "A drag-or-browse CSV/spreadsheet picker with a filename confirmation before submit — distinct from AUTH's single-photo upload (one file, a different purpose, a different accepted-format set)." | spec: [4A Primary Design Primitives](experience-design.md#4a-primary-design-primitives) | boundary: "Atomic control, used only by ds-catalog-004 (bulk import)."
  - ds-catalog-001 :: Storefront browsing and search | kind: component | summary: "Category chips, a search box, and an item grid showing every item's photo, name, price, and live stock status — all items across every category by default (decision-94)." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Entry point for ss-catalog-001; becomes the real \"/\" storefront home (decision-93), closing AUTH's own placeholder redirect there."
  - ds-catalog-002 :: Out-of-stock item state | kind: component | summary: "An item card with add-to-cart disabled and an explicit \"out of stock\" label — the item stays visible, never disappears, per UC-002's own \"digitize, don't hide\" model." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "A state of ds-catalog-001's item card, not a separate route."
  - ds-catalog-003 :: Low-stock notice state | kind: component | summary: "An item card showing a subtle low-stock notice alongside a still-enabled add-to-cart — distinct from out-of-stock, per BRD's 3-value stock-status vocabulary." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "A state of ds-catalog-001's item card, not a separate route."
  - ds-catalog-004 :: Bulk import upload screen | kind: component | summary: "Admin picks a catalog file and submits it for import." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Entry point for ss-catalog-002's bulk path; produces an import attempt."
  - ds-catalog-005 :: Import summary screen | kind: component | summary: "Per-row results — succeeded rows, and every failed row with its specific reason, per FR-015." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Follows ds-catalog-004."
  - ds-catalog-006 :: Single-item edit screen | kind: component | summary: "Edit one item's name, price, category, stock, or photo directly, without a full re-import." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "The lighter path ss-catalog-002 (solution.md) mentions alongside bulk import; also the only place a photo gets a real file upload (decision-88, system.md)."
  - ds-catalog-007 :: Stock management dashboard | kind: component | summary: "Every item's current stock, with items at or below the 5-unit threshold (decision-87, system.md) flagged without Admin searching for them." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Entry point for ss-catalog-003's stock-check side; also the entry point to ds-catalog-008."
  - ds-catalog-008 :: Walk-in sale recording screen | kind: component | summary: "Admin picks an item and a quantity to record an in-person sale against the same stock pool online orders draw from." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Reached from ds-catalog-007; produces an updated stock quantity or a rejected attempt (SY-CATALOG-010, system.md)."
  - dc-catalog-001 :: ItemCard | kind: component | summary: "Photo, name, price, and stock-status badge in one reusable card — the single unit ds-catalog-001's grid repeats, and what ds-catalog-002/003 are states of." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Secondary component — repeated dozens of times per screen, the definition of a shared pattern."
  - dc-catalog-002 :: StockStatusBadge | kind: component | summary: "A small colored label for in_stock/low_stock/out_of_stock — the same pill-badge pattern as AUTH's StatusBadge (dc-auth-001), but a genuinely different component: the value domain doesn't overlap, so it isn't literally the same badge with new colors." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Secondary component — used on dc-catalog-001 and ds-catalog-007's table rows."
Decisions:
  - decision-90 :: CATALOG inherits AUTH's design system wholesale, adding only catalog-specific primitives | kind: decision | summary: "Color, typography, spacing, and the accessibility contract are unchanged from AUTH's 4A ([decision-61](../AUTH/experience-design.md#4a-primary-design-primitives)–[decision-63](../AUTH/experience-design.md#4a-primary-design-primitives)) — this spec adds only what CATALOG genuinely needs that AUTH never did: photo display, a quantity stepper, category chips, a data table, and a file-upload control." | spec: [4A Primary Design Primitives](experience-design.md#4a-primary-design-primitives) | alternatives: "A denser, more \"retail\" visual system distinct from AUTH's — rejected on the same grounds decision-63 already rejected a separate Admin system: one integrated product, not a second brand two modules in." | reversal_trigger: "CATALOG's data-heavy Admin screens prove genuinely underserved by primitives designed around AUTH's mostly single-record forms — matching decision-63's own reversal trigger."
  - decision-91 :: No separate item-detail page — the item card is the complete product view | kind: decision | summary: "Browsing never navigates to a dedicated per-item page; every item's photo, name, price, and stock status is fully shown and actionable on the grid card itself (dc-catalog-001), matching the reference apps AUTH's own spec already cited (Blinkit, Zepto)." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | alternatives: "A dedicated item-detail route with a larger photo and a description field — nothing in the BRD's data model or FR-004–006 asks for a longer item description, and a detail page adds a navigation hop for no stated benefit at this catalog's scale." | reversal_trigger: "The catalog grows items with real per-item detail worth showing (multiple photos, a description field) that the BRD never anticipated."
  - decision-92 :: Category navigation is a horizontal chip bar, not a sidebar or dropdown | kind: decision | summary: "Categories render as tappable chips across the top of ds-catalog-001, matching mobile-first grocery-app convention (the same reference apps decision-91 cites) rather than a desktop-oriented sidebar." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | alternatives: "A sidebar category list — more scannable at a glance for a large catalog, but this project's catalog is small enough (single store) that a sidebar's screen-real-estate cost isn't earned, and it reads as a desktop pattern on a mobile-first screen." | reversal_trigger: "The category count grows past what a horizontal scroll can comfortably hold (a dozen or more)."
  - decision-93 :: The browsing screen becomes the real \"/\" storefront home | kind: decision | summary: "ds-catalog-001 is what AUTH's app/page.tsx redirect to /login was always a placeholder for — closing a gap AUTH's own implementation explicitly flagged (\"CATALOG's own storefront home isn't built yet\")." | spec: [Information Architecture and Navigation](experience-design.md#information-architecture-and-navigation) | alternatives: "None considered — this is simply naming what the BRD's UC-002 already implied as the site's own root; there was never a real alternative to CATALOG owning \"/\"." | reversal_trigger: "None expected."
  - decision-94 :: The browsing screen shows all items across every category by default | kind: decision | summary: "ds-catalog-001 renders every item unfiltered on first load — category chips and search narrow what's already showing, rather than requiring a choice before anything renders. Confirmed with the client." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | alternatives: "An empty state until a category or search term is chosen — simpler initial query, but adds a step before a first-time visitor sees anything, for a single-store catalog small enough that showing everything isn't overwhelming." | reversal_trigger: "The catalog grows large enough that an unfiltered grid becomes genuinely overwhelming on a phone screen."
OpenQuestions:
  - oq-58 :: What does the browsing screen show before any category or search is chosen? | kind: openquestion | summary: "Neither the BRD nor CATALOG's Solution/System specs said what the default, unfiltered view shows. — resolved, see decision-94." | spec: [CATALOG Decisions](experience-design.md#open-questions)
Tasks:
  - dt-catalog-001 :: Design storefront browsing and search | kind: task | summary: "ds-catalog-001, 002, 003 — the shared grid and its two stock-status states." | spec: [4B Design Task Breakdown](experience-design.md#4b-design-task-breakdown) | estimate: "1 design session" | acceptance: "All 3 states reviewed against ss-catalog-001 and sy-catalog-001..003"
  - dt-catalog-002 :: Design bulk import flow | kind: task | summary: "ds-catalog-004, 005 — upload through to a per-row result." | spec: [4B Design Task Breakdown](experience-design.md#4b-design-task-breakdown) | estimate: "1 design session" | acceptance: "Both screens reviewed against ss-catalog-002 and sy-catalog-004..007"
  - dt-catalog-003 :: Design single-item edit | kind: task | summary: "ds-catalog-006 — the lighter path alongside bulk import, including the one real photo-upload interaction in this module." | spec: [4B Design Task Breakdown](experience-design.md#4b-design-task-breakdown) | estimate: "0.5 design session" | acceptance: "Reviewed against ss-catalog-002 and sy-catalog-005..008"
  - dt-catalog-004 :: Design stock management and walk-in sale | kind: task | summary: "ds-catalog-007, 008 — the low-stock dashboard and recording a walk-in sale." | spec: [4B Design Task Breakdown](experience-design.md#4b-design-task-breakdown) | estimate: "1 design session" | acceptance: "Both screens reviewed against ss-catalog-003 and sy-catalog-009..011"
Flows:
  - journey-shopper-browse :: Shopper browsing journey | kind: flow | summary: "Opening the storefront through to adding an item to cart." | spec: [User Journeys](experience-design.md#user-journeys) | actor: "End User" | trigger: "Visits the storefront" | outcome: "Item added to cart (exits to ORDERS' own cart, out of scope) or sees it's unavailable without it disappearing"
  - journey-admin-import :: Admin bulk-import journey | kind: flow | summary: "Uploading a catalog file through to a per-row result, with an optional single-item correction after." | spec: [User Journeys](experience-design.md#user-journeys) | actor: "Admin" | trigger: "Admin has a new or updated catalog file" | outcome: "Catalog reflects the file's items, prices, categories, and photos; every failed row is individually explained"
  - journey-admin-stock :: Admin stock-management journey | kind: flow | summary: "Checking current stock through to recording a walk-in sale." | spec: [User Journeys](experience-design.md#user-journeys) | actor: "Admin" | trigger: "A walk-in sale happens, or Admin checks stock levels" | outcome: "Stock count stays accurate; low-stock items are flagged without a manual search"
Metrics:
  - metric-catalog-search-speed :: Search/filter response time | kind: metric | summary: "Wall-clock time from a keystroke or chip tap to updated results on ds-catalog-001." | spec: [Usability and Accessibility Criteria](experience-design.md#usability-and-accessibility-criteria) | baseline: "unmeasured (no prior version exists)" | target: "under 1 second, consistent with system-architecture.md's ~2s page-load budget" | current: "not yet measured"
  - metric-catalog-import-clarity :: Import-error self-resolution rate | kind: metric | summary: "Share of failed import rows Admin corrects and successfully re-imports without asking for help, based on the per-row reason shown on ds-catalog-005." | spec: [Usability and Accessibility Criteria](experience-design.md#usability-and-accessibility-criteria) | baseline: "unmeasured" | target: "80%+ of failed rows corrected on the first retry" | current: "not yet measured"
user-03 -> ds-catalog-001 | relation: experiences
user-01 -> ds-catalog-004 | relation: owns
user-01 -> ds-catalog-006 | relation: owns
user-01 -> ds-catalog-007 | relation: owns
constraint-catalog-image -> component-catalog-image | relation: governs
decision-90 -> component-catalog-image | relation: governs
decision-90 -> component-catalog-table | relation: governs
decision-91 -> dc-catalog-001 | relation: governs
decision-92 -> component-catalog-chip | relation: governs
decision-93 -> ds-catalog-001 | relation: governs
decision-94 -> ds-catalog-001 | relation: governs
decision-94 -> oq-58 | relation: decides
dt-catalog-001 -> ds-catalog-001 | relation: produces
dt-catalog-001 -> ds-catalog-002 | relation: produces
dt-catalog-001 -> ds-catalog-003 | relation: produces
dt-catalog-002 -> ds-catalog-004 | relation: produces
dt-catalog-002 -> ds-catalog-005 | relation: produces
dt-catalog-003 -> ds-catalog-006 | relation: produces
dt-catalog-004 -> ds-catalog-007 | relation: produces
dt-catalog-004 -> ds-catalog-008 | relation: produces
ds-catalog-004 -> ds-catalog-005 | relation: enables
ds-catalog-007 -> ds-catalog-008 | relation: enables
dc-catalog-001 -> ds-catalog-001 | relation: governs
dc-catalog-002 -> ds-catalog-007 | relation: governs
metric-catalog-search-speed -> ds-catalog-001 | relation: watches
metric-catalog-import-clarity -> ds-catalog-005 | relation: watches
```

</details>

> [!note]
> This graph carries 33 nodes across 8 groups — thinner than AUTH's own 41-node/7-group design graph, since CATALOG has fewer screens (8 vs 12) and reuses AUTH's color/type/a11y constraints by reference rather than re-declaring them. `Users` are reused from BRD/solution.md by the same IDs; `Delivery Agent` never appears — CATALOG has no agent-facing surface. Only one new `Constraint` node exists ([constraint-catalog-image](#)) — color, type, spacing, and accessibility are governed by AUTH's own [constraint-color](../AUTH/experience-design.md#4a-primary-design-primitives)/[constraint-type](../AUTH/experience-design.md#4a-primary-design-primitives)/[constraint-spacing](../AUTH/experience-design.md#4a-primary-design-primitives)/[constraint-a11y](../AUTH/experience-design.md#4a-primary-design-primitives), referenced in prose rather than redrawn as duplicate nodes in this module's own graph. The one open question this draft raised was confirmed with the client in the same round; see [Open Questions](#open-questions).

## 4A Primary Design Primitives

**Primitive source of truth.** CATALOG inherits AUTH's entire token contract, typography, spacing scale, and accessibility rules unchanged ([decision-90](#)) — see [AUTH's own 4A section](../AUTH/experience-design.md#4a-primary-design-primitives) for the full color/type/spacing table; it is not repeated here to avoid two copies of the same law drifting apart. What's created here is only what CATALOG genuinely needs beyond AUTH's mostly single-record, form-driven screens: photo display, a quantity stepper, category chips, a data table, and a file-upload control.

**Token contract:** unchanged from AUTH — jade primary, gold/sand/brick semantic accents, Inter body type, Fredoka display type, the 4px spacing scale, 8px/12px radii, 44×44px touch targets. No new tokens.

**Atomic controls (new for CATALOG):**

- **[component-catalog-image](#) Item photo display** — a fixed-aspect-ratio (1:1) slot; lazy-loads the photo when present, renders a generic gray placeholder icon when absent ([constraint-catalog-image](#)) — an item with no photo is never a broken image.
- **[component-catalog-stepper](#) Quantity stepper** — `−` / number / `+`, bounded at a minimum of 1 and a maximum of the item's current available stock (a walk-in sale can't be recorded past what's actually there, per [SY-CATALOG-010](system.md#testable-behaviors)).
- **[component-catalog-chip](#) Category chip** — a tappable pill, visually distinct from AUTH's StatusBadge in one respect: it has a selected/unselected state, since it's interactive, not read-only.
- **[component-catalog-table](#) Data table** — sortable columns, row-level actions (edit, record sale); the first tabular control this project has needed, since every AUTH screen was single-record.
- **[component-catalog-fileupload](#) File upload control** — drag-or-browse, one file, shows the chosen filename before submit; accepts CSV/spreadsheet formats only, distinct from AUTH's single-photo upload on [ds-auth-004](../AUTH/experience-design.md#4c-design-execution).

**Accessibility contract:** unchanged from AUTH's [constraint-a11y](../AUTH/experience-design.md#4a-primary-design-primitives) — 4.5:1 minimum contrast, full keyboard operability, `aria-live` error announcement, top-to-bottom focus order. Extended here: [component-catalog-image](#)'s placeholder icon carries `alt` text naming the item, never a bare decorative image with no text alternative; [component-catalog-table](#)'s sortable column headers are keyboard-operable (`Enter`/`Space` toggles sort), not mouse-only.

**Primitive decisions:** see [decision-90](#) in the graph above for the inherit-vs-create call.

**Open primitive questions:** none.

## 4B Design Task Breakdown

**Grouping: flow.** CATALOG's four Solution flows map close to one task each, the same reasoning [AUTH's own 4B](../AUTH/experience-design.md#4b-design-task-breakdown) used — Admin is a multi-flow persona here (import, edit, stock), so grouping by persona would have produced one oversized "Admin" group instead of the more reviewable per-flow breakdown below.

**Task inventory:** [dt-catalog-001](#) through [dt-catalog-004](#) — see the graph for each task's screens, estimate, and acceptance evidence. All four trace to a named `SS-CATALOG-NNN` flow (Solution) and its `SY-CATALOG-NNN` behaviors (System).

**Task sequencing:** [dt-catalog-001](#) (browsing) has no dependency and should run first — it's the highest-traffic screen and the one every End User sees. [dt-catalog-002](#) (import) should run before [dt-catalog-003](#) (single-item edit), since both share the same underlying item-edit fields and running import first surfaces the shared field set once rather than twice. [dt-catalog-004](#) (stock management) can run any time after [dt-catalog-001](#), since [dc-catalog-002](#) (StockStatusBadge) it reuses is already defined there.

**State coverage:** every task's acceptance criterion in the graph names its required states explicitly (see each `ds-catalog-*` node's `boundary` attribute) — happy path, and the specific edge states each flow actually has (out-of-stock, low-stock, per-row import failure, a walk-in sale that would oversell).

**Reuse plan:** [dc-auth-002](../AUTH/experience-design.md#4c-design-execution) (ErrorStatePanel) is reused directly for CATALOG's own generic network/server error state — no new error panel is built here. [dc-catalog-001](#) (ItemCard) and [dc-catalog-002](#) (StockStatusBadge) are new to this module but flagged for ORDERS' own future screens that might show item/stock information in a cart or order-line context.

**Acceptance evidence:** the live prototype (see [Prototype Evidence](#prototype-evidence)) for all screens; the usability/accessibility criteria table for the two numeric targets.

**Deferred tasks:** a dedicated item-detail page was considered and explicitly deferred — [decision-91](#) covers the reasoning. A "recently viewed" or "recommended items" section was also considered and deferred — no requirement anywhere asked for it, and personalization of that kind is out of Phase 1's scope.

## Personas and Context of Use

**[Admin](#) ([user-01](#))** — the same mart owner/operator as AUTH's own persona, here doing a heavier-weight, less-frequent task: uploading a catalog file or checking stock, likely from the same desk/counter computer. Context: import and stock screens need to be scannable and forgiving of a messy source file, since a rejected row is a real interruption to a task Admin is trying to finish quickly — traces to [SS-CATALOG-002](solution.md#business-flow-inventory)/[SS-CATALOG-003](solution.md#business-flow-inventory).

**[End User](#) ([user-03](#))** — the same shopper as AUTH's own persona, here doing the single highest-frequency thing anyone does in this product: looking at what's for sale. Context: phone-first, often mid-errand, wants to see what's available and its price at a glance without a slow page or an extra tap to a detail view — traces to [SS-CATALOG-001](solution.md#business-flow-inventory).

## 4C Design Execution

**Screen and state inventory:** [ds-catalog-001](#) through [ds-catalog-008](#) — see the graph for each screen's source task, source flow, and state coverage. The prototype (see below) covers all 8, including [ds-catalog-001](#)'s three item-card states ([dc-catalog-001](#) at `in_stock`, [ds-catalog-003](#) at `low_stock`, [ds-catalog-002](#) at `out_of_stock`) via an in-prototype state switcher, the same technique [AUTH's own prototype](../AUTH/experience-design.md#prototype-evidence) used for its four agent-status states.

## Information Architecture and Navigation

CATALOG's two roles are served by the same two route groups AUTH already established within the **one** Next.js deployable (CR-002, CR-007, [system-architecture.md](../../system-architecture.md#frontend-architecture)) — `FRONTEND_STOREFRONT` (unprefixed) for End User, `FRONTEND_ADMIN` (`/admin/*`) for Admin. No new route group — CATALOG adds screens to groups AUTH already scaffolded.

**FRONTEND_STOREFRONT (End User)** — unprefixed, the site's own root paths
- `/` — [ds-catalog-001](#) (browsing and search), all items shown by default ([decision-94](#)). This **replaces** AUTH's own placeholder redirect from `/` to `/login` ([decision-93](#)) — browsing needs no session, matching [SS-CATALOG-001](solution.md#module-responsibilities-boundaries-and-dependencies)'s own "no session at all" framing.
- Exit: adding an item to cart hands off to ORDERS' own cart/checkout IA, out of scope here. A shopper who isn't signed in can still browse and add to cart; AUTH's own `/login` remains reachable from wherever ORDERS' cart flow requires an account.

**FRONTEND_ADMIN (Admin)** — `/admin/*`, session-gated per AUTH's authorization contract
- `/admin/catalog/import` — [ds-catalog-004](#) (bulk import upload). Entry point for the bulk path.
- `/admin/catalog/import/summary` — [ds-catalog-005](#). Reachable only immediately after a submitted import; not bookmarkable as a standalone destination since a summary is tied to one specific import attempt.
- `/admin/catalog/[itemId]/edit` — [ds-catalog-006](#) (single-item edit). Reachable from a link/action on [ds-catalog-007](#)'s stock table, or directly if Admin already knows the item.
- `/admin/stock` — [ds-catalog-007](#) (stock dashboard, low-stock flagged).
- `/admin/stock/walk-in-sale` — [ds-catalog-008](#). Reachable from `/admin/stock`, not a standalone entry point — recording a sale always starts from seeing current stock first.

**Shared, app-wide (already fixed by AUTH, unchanged here):** [ds-auth-011](../AUTH/experience-design.md#4c-design-execution) (session-expired) interrupts any authenticated CATALOG route the same way it interrupts AUTH's own; [ds-auth-012](../AUTH/experience-design.md#4c-design-execution) (generic error) replaces any CATALOG route's content on a network/server failure. Neither is redrawn here — CATALOG reuses both directly.

## Mock Contracts and Data

These are frontend-facing mock contracts — stable field names and representative shapes the frontend builds against — not the backend's real schema or validation, which stage 50a (TRD) finalizes against [system.md](system.md)'s data models. Every field below traces to a named `dm-catalog-*` entity so TRD isn't guessing at intent.

| Endpoint (mock) | Request | Success response | Error/empty variants | Traces to |
|---|---|---|---|---|
| `GET /v1/catalog/items` | `?category=snacks&q=chips` (both optional — omitted means all items, per decision-94) | `200 [{ "id": "...", "name": "Lay's Chips 50g", "price": 20, "category": "Snacks", "photo_url": "...", "stock_status": "in_stock" }, ...]` | `200 []` (no matches — not an error, per AUTH's own empty-vs-error distinction) | [dm-catalog-item](system.md#logical-data-ownership-and-invariants), [dm-catalog-category](system.md#logical-data-ownership-and-invariants) |
| `POST /v1/catalog/import` | multipart file upload | `202 { "succeeded": 42, "failed": [{ "row": 7, "reason": "price must be a positive number" }] }` (drives [ds-catalog-005](#)) | none — every row either succeeds or is reported, per [SY-CATALOG-004](system.md#testable-behaviors) | [dm-catalog-item](system.md#logical-data-ownership-and-invariants) |
| `PATCH /v1/catalog/items/{id}` | `{ "name": "...", "price": 22, "category": "Snacks", "stock_quantity": 40, "photo": <file> }` (any subset) | `200 { ...updated item }` | `400 { "error": "invalid_field", "field": "price" }` | [dm-catalog-item](system.md#logical-data-ownership-and-invariants) |
| `POST /v1/catalog/walk-in-sale` | `{ "item_id": "...", "quantity": 3 }` | `200 { "item_id": "...", "stock_quantity": 37 }` | `409 { "error": "insufficient_stock" }` (drives an inline error on [ds-catalog-008](#), per [SY-CATALOG-010](system.md#testable-behaviors)) | [dm-catalog-item](system.md#logical-data-ownership-and-invariants) |
| `GET /v1/catalog/stock` | — (admin-session-scoped) | `200 [{ "id": "...", "name": "...", "stock_quantity": 3, "low_stock": true }, ...]` | `200 []` (an empty catalog — not an error) | [dm-catalog-item](system.md#logical-data-ownership-and-invariants) |

Empty-state note: [ds-catalog-001](#)'s "no items match" (a search/category filter with zero results) and [ds-catalog-007](#)'s "no items in catalog yet" are both true empty states, not errors — rendered as a plain message, never [dc-auth-002](../AUTH/experience-design.md#4c-design-execution) ErrorStatePanel, matching AUTH's own established distinction between "nothing matched" and "something broke."

## Widget and Interaction Contract

- **[component-catalog-image](#)** — no interaction; a display-only slot. Loading: a neutral-fill placeholder shows while the real photo loads, replaced without layout shift once it arrives (same fixed-aspect-ratio box throughout).
- **[component-catalog-stepper](#)** — events: `onIncrement`/`onDecrement` (disabled at the 1-unit floor and the current-stock ceiling), direct numeric entry also accepted and clamped to the same bounds on blur. Keyboard: arrow up/down adjust the value when the control has focus, matching native `<input type=number>` expectations.
- **[component-catalog-chip](#)** — events: `onSelect` (toggles that category's filter, updates the grid per [metric-catalog-search-speed](#)'s target). Keyboard: `Tab` reaches each chip in visual left-to-right order, `Enter`/`Space` toggles selection. Permission: no role-gating — chips are storefront-only, Admin never sees them.
- **[component-catalog-table](#)** — events: `onSort` (per column, ascending/descending toggle), `onRowAction` (edit or record-sale, depending on which table it's rendered in). Loading: a skeleton-row state while data fetches. Empty: a plain "no items" row, not an error panel.
- **[component-catalog-fileupload](#)** — events: `onFileSelect` (shows the chosen filename, enables submit), `onSubmit` (disables the control and shows a progress state while the import runs — this can take longer than the sub-2-second page-load budget for a large file, so it gets its own visible progress state rather than a spinner with no context). Error: an unreadable file (wrong format) is rejected before submit, with a specific message — never silently ignored.
- **[dc-catalog-001](#) ItemCard** — events: `onAddToCart` (disabled entirely in the [ds-catalog-002](#) out-of-stock state, enabled with a low-stock notice in the [ds-catalog-003](#) state). No loading state of its own — the grid's own loading state (skeleton cards) covers it.
- **[dc-catalog-002](#) StockStatusBadge** — no interaction; a read-only label, driven by the `stock_status` field in the mock responses above, exactly like AUTH's own StatusBadge is driven by its own status field.
- **Responsive rules:** [ds-catalog-001](#)–[ds-catalog-003](#) (End User) are mobile-first, matching AUTH's own End User screens — a single-column card list on phone width, a multi-column grid at wider viewports (unlike AUTH, which had no grid at all). [ds-catalog-004](#)–[ds-catalog-008](#) (Admin) assume a desktop/laptop browser at 1024px+, matching AUTH's own Admin screens — no mobile layout designed for Admin in this module either.
- **Permission behavior:** [ds-catalog-001](#)–[ds-catalog-003](#) require no session at all. [ds-catalog-004](#)–[ds-catalog-008](#) all require an Admin session — an unauthenticated visit to any `/admin/*` route redirects to [ds-auth-007](../AUTH/experience-design.md#4c-design-execution) (Admin login), the same authorization contract AUTH's own [SY-AUTH-013](../AUTH/system.md#testable-behaviors) already fixed.

## User Journeys

- **[journey-shopper-browse](#):** [ds-catalog-001](#) → (item in stock: add to cart, exits to ORDERS) or → [ds-catalog-003](#) (low stock, can still add to cart) or → [ds-catalog-002](#) (out of stock, add-to-cart disabled, item stays visible).
- **[journey-admin-import](#):** [ds-catalog-004](#) → [ds-catalog-005](#) (per-row summary) → optionally [ds-catalog-006](#) to correct one item the import couldn't (e.g. a row that failed validation and needs a manual fix instead of a re-import).
- **[journey-admin-stock](#):** [ds-catalog-007](#) → [ds-catalog-008](#) (record a walk-in sale) → back to [ds-catalog-007](#) with the updated count, or an inline rejection if the sale would oversell.

## Prototype Evidence

A real, interactive HTML prototype covering all three journeys: [ds-catalog-001](#) (browsing, with a state switcher demonstrating [dc-catalog-001](#)'s in-stock/low-stock/out-of-stock states), [ds-catalog-004](#)/[ds-catalog-005](#) (bulk import through to a per-row summary with a mix of success and failure), and [ds-catalog-007](#)/[ds-catalog-008](#) (stock dashboard through to recording a walk-in sale). It tests whether [decision-90](#)'s inherited design system reads as coherent on genuinely new surfaces AUTH never needed (a photo grid, a data table) and whether [decision-91](#)'s no-detail-page call feels complete rather than cut short.

**Prototype:** [Mini Mart Catalog Prototype](https://claude.ai/code/artifact/6b5bd539-65c6-4a10-8f5f-a53a64d35a98) — a rail on the left switches between the three journeys; each names the current `DS-CATALOG-NNN` screen and the decision behind it, the same technique [AUTH's own prototype](../AUTH/experience-design.md#prototype-evidence) uses. On the storefront tab, clicking any item's stock badge cycles it through in-stock → low-stock → out-of-stock (clearly marked "prototype only"), demonstrating [dc-catalog-001](#)'s three states without a real backend. The stock tab's walk-in sale form demonstrates [SY-CATALOG-010](system.md#testable-behaviors)'s oversell rejection live.

## Secondary Component Library

- **[dc-catalog-001](#) ItemCard** — photo, name, price, [dc-catalog-002](#) StockStatusBadge, add-to-cart button. Source screen: [ds-catalog-001](#). Expected reuse: none currently anticipated outside this module — ORDERS' own cart screen shows line items in its own format (quantity, subtotal), not this card.
- **[dc-catalog-002](#) StockStatusBadge** — pill-shaped label, color mapped to the 3-value stock-status vocabulary (green=in_stock, gold=low_stock, brick=out_of_stock — reusing AUTH's own semantic color tokens, [decision-90](#)). Source screen: [ds-catalog-001](#). Expected reuse: [ds-catalog-007](#)'s stock table, and potentially ORDERS' own future order-line display if it ever needs to show an item's current stock status.

## Duplicate Component Gate

Scanned against AUTH's own Experience Design Spec (the only sibling module with one so far, per the roadmap's build order): [dc-catalog-002](#) StockStatusBadge follows the identical visual *pattern* as [dc-auth-001](../AUTH/experience-design.md#4c-design-execution) StatusBadge (a colored pill, one label per value) but is not a literal duplicate — the two badges' value domains don't overlap (`in_stock`/`low_stock`/`out_of_stock` vs `pending_approval`/`approved`/`deactivated`/`rejected`), so they stay two components sharing one pattern, not one component with two call sites. [dc-auth-002](../AUTH/experience-design.md#4c-design-execution) ErrorStatePanel is reused directly, not duplicated — see [Widget and Interaction Contract](#widget-and-interaction-contract)'s empty-state note. No other duplicate candidates found. This gate will need re-running once ORDERS' own Experience Design Spec exists, specifically checking any item/stock display it needs against [dc-catalog-001](#)/[dc-catalog-002](#) before it invents its own.

## Usability and Accessibility Criteria

See [metric-catalog-search-speed](#) and [metric-catalog-import-clarity](#) in the graph for the two numeric targets this spec commits to, both currently `assumed` (no prior version of this product exists to baseline against) — they become real once stage 50b's Test Specification defines how they're measured. Accessibility reuses AUTH's own [metric-a11y-contrast](../AUTH/experience-design.md#usability-and-accessibility-criteria) target (WCAG AA, 4.5:1) unchanged — not re-declared as a duplicate metric node in this module's own graph.

## Evaluation Findings

None yet — this is the first pass through 4C for CATALOG, and no usability testing has been run against the prototype. This section stays populated once real evaluation happens; an empty findings section at first-author time is expected, not a gap.

## Reconciliation Record

The prototype and this spec were authored together in one pass, so there is no drift to reconcile: every screen in the prototype corresponds to a `ds-catalog-*` entry above with the same state coverage, and both secondary components ([dc-catalog-001](#), [dc-catalog-002](#)) exist identically in both. One detail the prototype makes concrete that the spec only described in prose: [component-catalog-image](#)'s no-photo placeholder ([constraint-catalog-image](#)) is demonstrated on one grid item (Tomato 1kg) deliberately given no photo, alongside the eleven items that do have one — confirming the placeholder reads as "no photo yet," not as a broken image, exactly as [constraint-catalog-image](#) requires. No Solution or System patch is needed — this is a prototype detail, not a behavior change.

## Open Questions

None outstanding. The one question this spec raised was resolved during the same drafting round:

- *What does the browsing screen show before any category or search is chosen?* Resolved: all items across every category, confirmed with the client — see [decision-94](#).

## Approval

Approved by: Bhargav
Role:        PTL
Date:        2026-09-05
Hash:        d5d9712c3508…
