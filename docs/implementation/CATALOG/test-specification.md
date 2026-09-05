---
daksh:
  type: test-specification
  subtype: null
  stage: "50b"
  module: CATALOG
---

# CATALOG Test Specification

CATALOG's [Solution](solution.md), [System](system.md), and [TRD](trd.md) promised four business flows, fourteen testable behaviors, and ten technical requirements; this document is the evidence plan proving each one — every `SS-CATALOG-NNN`, `SY-CATALOG-NNN`, and `TRD-CATALOG-NNN`, plus every `DS-CATALOG-NNN` screen from [experience-design.md](experience-design.md), maps to at least one stable `TEST-CATALOG-NNN` case below. Coverage spans the same five layers AUTH's own Test Specification established: unit (pure functions, no DB), integration (real Postgres, faked S3), interface/contract (HTTP-level schema conformance), end-to-end (full journeys through a real app instance), and frontend/accessibility (per-screen, against [experience-design.md](experience-design.md#usability-and-accessibility-criteria)'s own numeric targets). Test IDs are stable identifiers; a revision changes a case's body, never its identity.

<details>
<summary>Graph: What evidence proves each promised behavior?</summary>

```items
---
id: 50b-catalog-test-cognition
title: CATALOG Test Specification — Evidence and Proof
default_open_depth: 1
default_color_by: kind
color_palette_source: .daksh/color-palette.json
width: 95vw
---
id: 50b-catalog-test-cognition
title: CATALOG Test Specification — Evidence and Proof
Flows:
  - ss-catalog-001 :: Catalog browsing and search | kind: flow | summary: "Reused from solution.md — covered by this stage's browsing/search test area." | spec: [Traceability](test-specification.md#traceability) | actor: "End User" | trigger: "Shopper opens the storefront or searches" | outcome: "Shopper finds an item and can add it to cart, or sees it's out of stock without it disappearing"
  - ss-catalog-002 :: Catalog maintenance via bulk import | kind: flow | summary: "Reused from solution.md — covered by this stage's import/edit test area." | spec: [Traceability](test-specification.md#traceability) | actor: "Admin" | trigger: "Admin uploads a catalog file, or edits one item directly" | outcome: "Catalog reflects current items, prices, categories, and photos; a per-row import summary reports success/failure"
  - ss-catalog-003 :: Stock management across two sales channels | kind: flow | summary: "Reused from solution.md — covered by this stage's stock-management test area." | spec: [Traceability](test-specification.md#traceability) | actor: "Admin" | trigger: "A walk-in sale happens, or admin checks stock levels" | outcome: "Stock count stays accurate across both channels; items at or below the threshold are flagged"
  - ss-catalog-004 :: Stock reservation and release for order fulfillment | kind: flow | summary: "Reused from solution.md — covered by this stage's reservation-contract test area, the cross-cutting mechanism ORDERS depends on." | spec: [Traceability](test-specification.md#traceability) | actor: "System (invisible to the end user)" | trigger: "ORDERS attempts a checkout, a cancellation, or a stale-order timeout fires" | outcome: "Stock is reserved, found insufficient, or released back to the pool"
Interfaces:
  - interface-catalog-browse :: Catalog browsing & search interface | kind: interface | summary: "Reused from system.md/trd.md — contract-tested by TEST-CATALOG-014." | spec: [Interface and Contract Tests](test-specification.md#interface-and-contract-tests) | shape: "[trd.md API Contracts](trd.md#api-contracts)" | version: "v1" | compatibility: additive
  - interface-catalog-manage :: Catalog & stock management interface | kind: interface | summary: "Reused from system.md/trd.md — contract-tested by TEST-CATALOG-015/016/017/018." | spec: [Interface and Contract Tests](test-specification.md#interface-and-contract-tests) | shape: "[trd.md API Contracts](trd.md#api-contracts)" | version: "v1" | compatibility: additive
Invariants:
  - inv-catalog-nonnegative-stock :: catalog_items.stock_quantity is never negative | kind: invariant | summary: "Reused from trd.md — proved by TEST-CATALOG-008 and TEST-CATALOG-011." | spec: [Integration Tests](test-specification.md#integration-tests) | violation_signal: "Any row with stock_quantity < 0, or a successful write that would produce one."
  - inv-catalog-reservation-consistency :: An active reservation's quantity was actually deducted from its item | kind: invariant | summary: "Reused from trd.md — proved by TEST-CATALOG-010 and watched by TEST-CATALOG-025's concurrency case." | spec: [Integration Tests](test-specification.md#integration-tests) | violation_signal: "An active reservation row with no matching stock deduction, or vice versa."
Risks:
  - risk-catalog-s3-outage :: OBJECT_STORAGE (S3) outage blocks photo upload, not the rest of CATALOG | kind: risk | summary: "Reused from trd.md — watched by TEST-CATALOG-026." | spec: [Edge, Failure, Security, Performance, and Recovery Tests](test-specification.md#edge-failure-security-performance-and-recovery-tests) | likelihood: "unknown — unvalidated" | impact: "low — narrowly scoped to the photo field" | mitigation: "A failed photo upload fails only that row/edit, with a specific reason." | phase: runtime
Metrics:
  - metric-catalog-search-speed :: Search/filter response time | kind: metric | summary: "Reused from experience-design.md — proved by TEST-CATALOG-027." | spec: [Edge, Failure, Security, Performance, and Recovery Tests](test-specification.md#edge-failure-security-performance-and-recovery-tests) | baseline: "unmeasured" | target: "under 1 second" | current: "not yet measured"
  - metric-catalog-import-clarity :: Import-error self-resolution rate | kind: metric | summary: "Reused from experience-design.md — a post-launch field measurement, not something this test spec proves directly; TEST-CATALOG-015's per-row reason clarity is the closest proxy this stage can test." | spec: [Interface and Contract Tests](test-specification.md#interface-and-contract-tests) | baseline: "unmeasured" | target: "80%+ of failed rows corrected on the first retry" | current: "not yet measured"
Tests:
  - test-catalog-browse :: Browsing and search test suite | kind: test | summary: "Bundles TEST-CATALOG-001, 014, 019, 022, 027 — stock-status derivation, contract conformance, the full e2e shopper journey, frontend/a11y, and search-speed." | spec: [Unit Tests](test-specification.md#unit-tests) | trigger: "Runs on every push/PR via pipeline-01 (CI)"
  - test-catalog-import :: Bulk import and single-item edit test suite | kind: test | summary: "Bundles TEST-CATALOG-002 through 006, 013, 015, 016, 020, 023, 026 — validation, match-or-create, race-safe category creation, both photo paths, contract conformance, e2e admin journey, frontend/a11y, S3-outage recovery." | spec: [Integration Tests](test-specification.md#integration-tests) | trigger: "Runs on every push/PR via pipeline-01 (CI)"
  - test-catalog-stock :: Stock management test suite | kind: test | summary: "Bundles TEST-CATALOG-007 through 009, 017, 018, 021, 024 — walk-in sale, oversell rejection, low-stock flagging, contract conformance, e2e admin journey, frontend/a11y." | spec: [Integration Tests](test-specification.md#integration-tests) | trigger: "Runs on every push/PR via pipeline-01 (CI)"
  - test-catalog-reservation :: Stock reservation contract test suite | kind: test | summary: "Bundles TEST-CATALOG-010 through 012, 025 — reserve/release/availability and the concurrent-race proof that makes decision-95's atomicity claim more than a description." | spec: [Integration Tests](test-specification.md#integration-tests) | trigger: "Runs on every push/PR via pipeline-01 (CI)"
test-catalog-browse -> ss-catalog-001 | relation: proves
test-catalog-browse -> interface-catalog-browse | relation: proves
test-catalog-browse -> metric-catalog-search-speed | relation: proves
test-catalog-import -> ss-catalog-002 | relation: proves
test-catalog-import -> interface-catalog-manage | relation: proves
test-catalog-import -> risk-catalog-s3-outage | relation: watches
test-catalog-import -> metric-catalog-import-clarity | relation: watches
test-catalog-stock -> ss-catalog-003 | relation: proves
test-catalog-stock -> inv-catalog-nonnegative-stock | relation: proves
test-catalog-reservation -> ss-catalog-004 | relation: proves
test-catalog-reservation -> inv-catalog-reservation-consistency | relation: proves
```

</details>

> [!note]
> This graph carries 18 nodes across 6 groups — thin relative to the 30-60 ideal, and worth explaining rather than padding: `Flows` and `Interfaces` are pure reuse by ID from `solution.md`/`system.md`/`trd.md` — this stage proves what earlier stages promised, it does not invent new promises. Per the same graph-vs-schema boundary AUTH's own Test Specification established, the 4 `Tests` nodes are representative suites, not all 28 `TEST-CATALOG-NNN` case IDs individually — the full 1:1 case-level detail lives in the tables below, which every `Tests` node's `spec:` link points into. `SY-CATALOG-NNN` and `TRD-CATALOG-NNN` requirements are not re-promoted as graph nodes either, matching AUTH's own precedent — they exist as table rows and inline tags upstream, not `items`-fence entries, so re-inventing them here would duplicate the [Traceability](#traceability) table, not deepen it.

## Scope, Risks, and Test Environments

This spec designs the evidence plan for all four `SS-CATALOG-NNN` flows, all fourteen `SY-CATALOG-NNN` behaviors, all ten `TRD-CATALOG-NNN` technical requirements, and all eight `DS-CATALOG-NNN` screens — nothing in AUTH or ORDERS, no implementation code (stage 50d), no new business decisions (a gap found here flows back through `/daksh change CATALOG`). One budget this spec deliberately does **not** re-test: the sub-100ms authorization-overhead target every [interface-catalog-manage](#) write depends on is the identical `get_current_user()`/`require_role()` code path AUTH's own [TEST-AUTH-040](../AUTH/test-specification.md#edge-failure-security-performance-and-recovery-tests) already proves — re-measuring the same function here would duplicate evidence, not add any.

**Test environments**, per [system-architecture.md's Deployment Architecture](../../system-architecture.md#deployment-architecture): unit and integration tests run against [env-01](../../system-architecture.md#deployment-architecture) `LOCAL` (Docker Compose Postgres) inside [pipeline-01](../../system-architecture.md#deployment-architecture) `CI` on every push/PR; end-to-end tests run against [env-02](../../system-architecture.md#deployment-architecture) `PREVIEW` once `oq-27` (hosting) resolves — until then, `TEST-CATALOG-019` through `TEST-CATALOG-021` are designed but run against a locally-hosted equivalent instead, the same caveat AUTH's own e2e tests already carry (flagged in [Open Questions](#open-questions)).

**Boundaries — real, fake, or contract-tested, and why:**
- **DATABASE (Postgres): real**, not mocked, in every unit/integration/contract/e2e test — a disposable per-test-run schema created fresh from the [5a](trd.md#5a-persistence-constraints) DDL. CATALOG's correctness rests on real constraint behavior (the `(name, category_id)` unique index, the nonnegative-stock CHECK, the atomic conditional UPDATE) that a mock would trivially "pass" without proving anything.
- **OBJECT_STORAGE (AWS S3): fake** everywhere — a local double recording every PUT call and returning a deterministic URL, never a real bucket. Unlike AUTH's OTP-latency test, there is no metric here requiring proof of real-object retrievability or delivery timing, so no equivalent "one real-S3 test" exception exists.
- **AUTH's authorization dependency (`get_current_user()`/`require_role()`): real**, exercised directly against every [interface-catalog-manage](#) write — the same in-process contract, not faked, since CATALOG's own tests need to prove the dependency is actually wired in, not assume it.
- **The in-process reservation contract (`reserve_stock()`/`release_stock()`/`get_availability()`): real**, called directly as CATALOG's own functions in [Integration Tests](#integration-tests) — these tests exercise CATALOG's side of the contract, not a simulated ORDERS caller; ORDERS' own future Test Specification is what proves it calls the contract correctly from its side.
- **ORDERS: not applicable** — CATALOG has no dependency on ORDERS ([system-architecture.md](../../system-architecture.md#module-decomposition): "CATALOG never calls out to ORDERS"), so no test here calls into it.

**Risks this spec is aware of and does not try to eliminate:** [risk-catalog-s3-outage](#) (watched, not eliminated — see `TEST-CATALOG-026`).

## Traceability

Every requirement below maps to at least one Test ID; a requirement with no row is a gap that blocks this stage's approval, per [stages/50b-test-specification/CONTEXT.md](.)'s own rule.

| Requirement | Test ID(s) |
|---|---|
| [SS-CATALOG-001](solution.md#business-flow-inventory) | TEST-CATALOG-001, 014, 019, 022, 027 |
| [SS-CATALOG-002](solution.md#business-flow-inventory) | TEST-CATALOG-002, 003, 004, 005, 006, 013, 015, 016, 020, 023, 026 |
| [SS-CATALOG-003](solution.md#business-flow-inventory) | TEST-CATALOG-007, 008, 009, 017, 018, 021, 024 |
| [SS-CATALOG-004](solution.md#business-flow-inventory) | TEST-CATALOG-010, 011, 012, 013, 025 |
| [SY-CATALOG-001](system.md#testable-behaviors) | TEST-CATALOG-014 |
| [SY-CATALOG-002](system.md#testable-behaviors) | TEST-CATALOG-014, 027 |
| [SY-CATALOG-003](system.md#testable-behaviors) | TEST-CATALOG-001, 009 |
| [SY-CATALOG-004](system.md#testable-behaviors) | TEST-CATALOG-002, 015 |
| [SY-CATALOG-005](system.md#testable-behaviors) | TEST-CATALOG-004, 005 |
| [SY-CATALOG-006](system.md#testable-behaviors) | TEST-CATALOG-004, 006 |
| [SY-CATALOG-007](system.md#testable-behaviors) | TEST-CATALOG-003, 013, 026 |
| [SY-CATALOG-008](system.md#testable-behaviors) | TEST-CATALOG-016 |
| [SY-CATALOG-009](system.md#testable-behaviors) | TEST-CATALOG-007 |
| [SY-CATALOG-010](system.md#testable-behaviors) | TEST-CATALOG-008, 017 |
| [SY-CATALOG-011](system.md#testable-behaviors) | TEST-CATALOG-009, 018 |
| [SY-CATALOG-012](system.md#testable-behaviors) | TEST-CATALOG-010, 011, 025 |
| [SY-CATALOG-013](system.md#testable-behaviors) | TEST-CATALOG-012 |
| [SY-CATALOG-014](system.md#testable-behaviors) | TEST-CATALOG-013 |
| TRD-CATALOG-001 ([trd.md](trd.md#data-model)) | TEST-CATALOG-008, 011 |
| TRD-CATALOG-002 ([trd.md](trd.md#data-model)) | TEST-CATALOG-004, 005 |
| TRD-CATALOG-003 ([trd.md](trd.md#data-model)) | TEST-CATALOG-009 |
| TRD-CATALOG-004 ([trd.md](trd.md#5a-persistence-constraints)) | TEST-CATALOG-006 |
| TRD-CATALOG-005 ([trd.md](trd.md#5b-state-machines)) | TEST-CATALOG-010, 025 |
| TRD-CATALOG-006 ([trd.md](trd.md#api-contracts)) | TEST-CATALOG-008, 017 |
| TRD-CATALOG-007 ([trd.md](trd.md#api-contracts)) | TEST-CATALOG-015 |
| TRD-CATALOG-008 ([trd.md](trd.md#security-design)) | TEST-CATALOG-003, 026 |
| TRD-CATALOG-009 ([trd.md](trd.md#security-design)) | TEST-CATALOG-014 |
| TRD-CATALOG-010 ([trd.md](trd.md#6a-idempotency-and-failure-contracts)) | TEST-CATALOG-004, 005 |
| [DS-CATALOG-001](experience-design.md#4c-design-execution)–[003](experience-design.md#4c-design-execution) | TEST-CATALOG-022 |
| [DS-CATALOG-004](experience-design.md#4c-design-execution)–[006](experience-design.md#4c-design-execution) | TEST-CATALOG-023 |
| [DS-CATALOG-007](experience-design.md#4c-design-execution)–[008](experience-design.md#4c-design-execution) | TEST-CATALOG-024 |

## Unit Tests

Pure functions, no database, no network — fastest tier, run first in `pipeline-01`.

| ID | Preconditions | Data | Steps | Expected Result | Layer | Owner | Automation |
|---|---|---|---|---|---|---|---|
| TEST-CATALOG-001 | None | `stock_quantity` values of 0, 5, 6, and 40 | Run the stock-status derivation function against each | 0 → `out_of_stock`; 5 → `low_stock` (at the threshold, decision-87); 6 → `in_stock`; 40 → `in_stock` | Unit | PTL | Automated — pytest |
| TEST-CATALOG-002 | None | Rows with an empty name, a zero/negative price, a negative stock value, and a fully valid row | Run the import-row validator against each | The valid row passes; each invalid row is rejected with a specific, distinct reason naming the failing field | Unit | PTL | Automated — pytest |
| TEST-CATALOG-003 | None | A JPEG under 5MB, a PNG under 5MB, a PDF, and a JPEG over 5MB | Run the photo validator against each | Both image files pass; the PDF and the oversized JPEG are each rejected with a specific reason (wrong type / too large) | Unit | PTL | Automated — pytest |

## Integration Tests

Real Postgres (disposable per-run schema), faked `OBJECT_STORAGE`, real service-layer functions.

| ID | Preconditions | Data | Steps | Expected Result | Layer | Owner | Automation |
|---|---|---|---|---|---|---|---|
| TEST-CATALOG-004 | Empty catalog | An import row naming a category that doesn't exist yet | Import the row | The category is created; the item is created, referencing it | Integration | PTL | Automated — pytest + test DB |
| TEST-CATALOG-005 | An item already exists with a given name+category | A re-imported row with the same name+category but a different price | Import the row | The existing item's price updates in place; no second item is created ([decision-82](solution.md#business-states-decisions-and-recovery)) | Integration | PTL | Automated — pytest + test DB |
| TEST-CATALOG-006 | No category with a given name exists | Two import rows, in two concurrent import calls, both naming the same new category | Run both concurrently | Exactly one `catalog_categories` row is created for that name; both items reference the same category row, not two different ones ([decision-97](trd.md#5a-persistence-constraints)) | Integration | PTL | Automated — pytest + test DB |
| TEST-CATALOG-007 | An item with `stock_quantity = 40` | A walk-in sale of quantity 5 | Record the sale | `stock_quantity` becomes 35 | Integration | PTL | Automated — pytest + test DB |
| TEST-CATALOG-008 | An item with `stock_quantity = 3` | A walk-in sale of quantity 5 | Attempt to record the sale | Rejected `409 insufficient_stock`; `stock_quantity` remains 3, unchanged ([inv-catalog-nonnegative-stock](#)) | Integration | PTL | Automated — pytest + test DB |
| TEST-CATALOG-009 | Items at `stock_quantity` 0, 5, and 40 | — | Fetch the low-stock list | The 0 and 5 items both appear (5 is the threshold, inclusive per decision-87); the 40 item does not; the 0-quantity item is still present in the general catalog listing too, never hidden ([decision-85](solution.md#business-states-decisions-and-recovery)) | Integration | PTL | Automated — pytest + test DB |
| TEST-CATALOG-010 | An item with `stock_quantity = 10` | `reserve_stock(item_id, 4, "ref-1")` | Call it | Returns `True`; `stock_quantity` becomes 6; one `catalog_reservations` row exists with `status='active'`, `quantity=4` ([inv-catalog-reservation-consistency](#)) | Integration | PTL | Automated — pytest + test DB |
| TEST-CATALOG-011 | An item with `stock_quantity = 2` | `reserve_stock(item_id, 5, "ref-2")` | Call it | Returns `False`; `stock_quantity` remains 2, unchanged; no `catalog_reservations` row is created ([inv-catalog-nonnegative-stock](#)) | Integration | PTL | Automated — pytest + test DB |
| TEST-CATALOG-012 | Two active reservations under the same reference, against two different items | `release_stock("ref-3")` | Call it | Both items' `stock_quantity` are restored by their reserved amounts; both reservation rows become `status='released'` | Integration | PTL | Automated — pytest + test DB |
| TEST-CATALOG-013 | An item with `stock_quantity = 12`, one active reservation of 3 against it | `get_availability(item_id)` | Call it twice in a row | Both calls return 9; `stock_quantity` and the reservation row are unchanged by either call (read-only) | Integration | PTL | Automated — pytest + test DB |

## Interface and Contract Tests

Real HTTP calls to a running test instance of the FastAPI app; real Postgres; faked `OBJECT_STORAGE`. Validates the literal request/response shapes in [trd.md's API Contracts](trd.md#api-contracts) against [experience-design.md's Mock Contracts](experience-design.md#mock-contracts-and-data) — the frontend and backend are never allowed to silently drift apart.

| ID | Preconditions | Data | Steps | Expected Result | Layer | Owner | Automation |
|---|---|---|---|---|---|---|---|
| TEST-CATALOG-014 | Running test app, a seeded catalog across 2 categories | No params; a category filter; a search keyword; a keyword matching nothing | `GET /v1/catalog/items` for each case, with no session | All items returned when no params given (decision-94); category filter narrows correctly; search narrows correctly; the no-match case returns `200 []`, not an error | Contract | PTL | Automated — schemathesis/pytest against the OpenAPI-shaped contract |
| TEST-CATALOG-015 | Running test app, admin and non-admin sessions available | A file with 5 valid rows and 1 invalid row | `POST /v1/catalog/import` as admin, then as a non-admin session, then with no session | Admin call returns `202 {succeeded: 5, failed: [{row, reason}]}` exactly shaped; non-admin `403`; no session `401` | Contract | PTL | Automated |
| TEST-CATALOG-016 | Running test app, an existing item, admin session | A valid field update; an invalid price; a nonexistent item id | `PATCH /v1/catalog/items/{id}` for each case | Valid update returns `200` with the updated item; invalid price returns `400 invalid_field`; nonexistent id returns `404` | Contract | PTL | Automated |
| TEST-CATALOG-017 | Running test app, an item with known stock, admin session | A sale within stock, a sale exceeding stock | `POST /v1/catalog/walk-in-sale` for each case | Response matches the documented `200`/`409` schema exactly | Contract | PTL | Automated |
| TEST-CATALOG-018 | Running test app, an empty catalog, then a seeded one, admin session | — | `GET /v1/catalog/stock` before and after seeding | Empty catalog returns `200 []`; seeded catalog returns every item with a correct `low_stock` boolean per item | Contract | PTL | Automated |

## End-to-End Tests

Full journeys through a real (or PREVIEW-equivalent) app instance — see [Scope](#scope-risks-and-test-environments) for the current environment caveat.

| ID | Preconditions | Data | Steps | Expected Result | Layer | Owner | Automation |
|---|---|---|---|---|---|---|---|
| TEST-CATALOG-019 | Fresh browser session, a seeded catalog with an in-stock, a low-stock, and an out-of-stock item | — | Follow [journey-shopper-browse](experience-design.md#user-journeys): [ds-catalog-001](experience-design.md#4c-design-execution), search, filter by category, add an in-stock item to cart | Item added; the low-stock item shows its notice but is still addable; the out-of-stock item's add-to-cart is disabled and the item remains visible | E2E | PTL | Automated — Playwright |
| TEST-CATALOG-020 | Fresh browser session (admin), a catalog file with a mix of valid and invalid rows | — | Follow [journey-admin-import](experience-design.md#user-journeys): [ds-catalog-004](experience-design.md#4c-design-execution) → [ds-catalog-005](experience-design.md#4c-design-execution) → correct one failed row via [ds-catalog-006](experience-design.md#4c-design-execution) | Import summary shows the correct success/failure split; the corrected item saves successfully afterward | E2E | PTL | Automated — Playwright |
| TEST-CATALOG-021 | Fresh browser session (admin), an item near the low-stock threshold | A walk-in sale quantity that would oversell | Follow [journey-admin-stock](experience-design.md#user-journeys): [ds-catalog-007](experience-design.md#4c-design-execution) → [ds-catalog-008](experience-design.md#4c-design-execution), attempt the oversized sale, then a valid one | Oversized attempt shows an inline rejection, stock unchanged; the valid sale updates the dashboard's count on return | E2E | PTL | Automated — Playwright |

## Frontend and Accessibility Tests

Per [experience-design.md's Usability and Accessibility Criteria](experience-design.md#usability-and-accessibility-criteria) — every `DS-CATALOG-NNN` screen gets at least one entry here.

| ID | Preconditions | Data | Steps | Expected Result | Layer | Owner | Automation |
|---|---|---|---|---|---|---|---|
| TEST-CATALOG-022 | Prototype-equivalent build of [ds-catalog-001](experience-design.md#4c-design-execution)–[003](experience-design.md#4c-design-execution) rendered | An in-stock, low-stock, and out-of-stock item | Complete a search and an add-to-cart using only keyboard (Tab/Enter) | Flow completes without a mouse; all 3 [dc-catalog-002](experience-design.md#4c-design-execution) StockStatusBadge states render with the correct color/label; axe-core reports zero violations at `metric-a11y-contrast`'s 4.5:1 threshold | Frontend/A11y | PTL | Automated — Playwright + axe-core |
| TEST-CATALOG-023 | Build of [ds-catalog-004](experience-design.md#4c-design-execution)–[006](experience-design.md#4c-design-execution) rendered | An import file, a single item to edit | Complete a bulk import and a single-item edit (including the photo upload field) using only keyboard | Both flows complete without a mouse; [component-catalog-fileupload](experience-design.md#4a-primary-design-primitives) and [component-catalog-table](experience-design.md#4a-primary-design-primitives)'s sortable headers are keyboard-operable; axe-core zero violations | Frontend/A11y | PTL | Automated — Playwright + axe-core |
| TEST-CATALOG-024 | Build of [ds-catalog-007](experience-design.md#4c-design-execution)–[008](experience-design.md#4c-design-execution) rendered | A seeded stock list, a walk-in sale | Sort the stock table by a column, then record a sale using only keyboard, including [component-catalog-stepper](experience-design.md#4a-primary-design-primitives) | Flow completes without a mouse; the stepper's arrow-key adjustment works; axe-core zero violations | Frontend/A11y | PTL | Automated — Playwright + axe-core |

## Edge, Failure, Security, Performance, and Recovery Tests

| ID | Preconditions | Data | Steps | Expected Result | Layer | Owner | Automation |
|---|---|---|---|---|---|---|---|
| TEST-CATALOG-025 | An item with `stock_quantity = 1` | 10 concurrent `reserve_stock(item_id, 1, reference)` calls, each a distinct reference | Fire all 10 simultaneously | Exactly one call returns `True`; the other 9 return `False`; final `stock_quantity` is 0, never negative ([decision-95](trd.md#business-rules-and-validation), [inv-catalog-nonnegative-stock](#)) | Concurrency | PTL | Automated — pytest, concurrent asyncio tasks against the real test DB |
| TEST-CATALOG-026 | Faked `OBJECT_STORAGE` configured to raise on PUT | An import row with a photo URL, and a single-item edit with a photo file | Attempt both while the double fails | The import row is reported as failed with a specific photo-related reason (not silently imported without its photo); the edit request fails with the same kind of specific reason ([risk-catalog-s3-outage](#), [trd.md 6a](trd.md#6a-idempotency-and-failure-contracts)) | Recovery | PTL | Automated — pytest |
| TEST-CATALOG-027 | A seeded catalog of realistic size (dozens of items) | A category filter, a search keyword | Measure wall-clock time from request to response for each | Both under 1 second ([metric-catalog-search-speed](#)) | Performance | PTL | Automated — pytest, measured against `LOCAL`; revisit against `PREVIEW` once `oq-27` resolves |

## Setup, Fixtures, Factories, Seeds, Mocks, and Cleanup

- **Database:** a fresh Postgres schema per test run, migrated via Alembic from the [5a](trd.md#5a-persistence-constraints) DDL — never a shared, persistent test database, matching AUTH's own discipline.
- **Factories:** one factory per entity (`CatalogCategoryFactory`, `CatalogItemFactory`, `CatalogReservationFactory`) producing valid rows with sensible defaults, overridable per test.
- **OBJECT_STORAGE double:** a recording fake implementing the same `put`/`get`-shaped interface a real S3 client would, returning a deterministic URL and capturing call arguments for assertion; used by every test except none — no real-S3 test exists in this spec (see [Scope](#scope-risks-and-test-environments)).
- **Admin session:** reused directly from AUTH's own test seeding/login helpers — no separate Admin-account fixture is built here.
- **Cleanup:** the per-run schema is dropped after the run; no manual cleanup step exists or is needed.

## Coverage Targets and Evidence Location

- 100% of `SS-CATALOG-NNN`, `SY-CATALOG-NNN`, `TRD-CATALOG-NNN`, and `DS-CATALOG-NNN` requirements have at least one mapped Test ID — see [Traceability](#traceability); this is a gate, not an aspiration.
- `app/catalog` line coverage target: 90%+, matching AUTH's own bar, enforced in [pipeline-01](../../system-architecture.md#deployment-architecture) `CI` once implementation exists (stage 50d) — a target recorded here for the implementer to build against, not yet measured.
- Evidence location: CI test reports and coverage artifacts attach to each `pipeline-01` run in GitHub Actions — no separate test-evidence store exists at this scale, same as AUTH.

## Open Questions

None outstanding for the test design itself. One execution-timing note, not a design gap:

- `TEST-CATALOG-019` through `TEST-CATALOG-021` need a real `PREVIEW` deployment to run as designed; until `oq-27` (hosting, system-architecture.md) resolves, they run against a locally-hosted equivalent instead — the test design doesn't change, only where it executes, the identical caveat AUTH's own e2e tests already carry.

## Approval

Approved by: Bhargav
Role:        PTL
Date:        2026-09-05
Hash:        3c086e5c539b…
