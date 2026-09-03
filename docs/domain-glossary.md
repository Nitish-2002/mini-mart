# Domain Glossary

Client-vocabulary terms for Mini Mart — entity names, status values, and business-process terms used across every Daksh doc from this point on. This is separate from [`docs/glossary.md`](glossary.md), which holds Daksh's own process terms (stage, manifest, approval, and so on). Status terms here are the highest-risk entries: once a status value appears in an approved BRD, every downstream TRD, System spec, and Task **must** reuse it verbatim rather than inventing a synonym — this file is the source of truth for that vocabulary, not any individual downstream doc.

---

## Order

### Order status
The canonical five-value lifecycle for an order: `placed` (checked out, stock reserved, within or past the cancellation window), `assigned` (admin has assigned a delivery agent), `out_for_delivery` (agent has picked up and is en route), `delivered` (agent confirmed COD collection), `cancelled` (terminal — see cancellation reason). First fixed in [`business-requirements.md`](business-requirements.md#domain-vocabulary) (decision-26). No other status values are valid; a new one requires a formal change record, not a silent addition downstream.

### Cancellation reason
A sub-field on a `cancelled` order recording why: `customer_requested` (cancelled within the 5-minute pre-dispatch window, [UC-004](business-requirements.md#uc-004-end-user-cancels-an-order-before-dispatch)), `cod_refused` (customer declined to pay at the door, [UC-010](business-requirements.md#uc-010-delivery-agent-fulfills-an-order)), or `stale_timeout` (order never confirmed/picked up within the system timeout, [UC-011](business-requirements.md#uc-011-system-releases-stock-for-stale-orders)).

### Stale order
An order in `placed` or `assigned` status that has not progressed within a timeout window (exact value set at stage 30d System spec). Triggers automatic stock release and `cancelled` (reason: `stale_timeout`) — see [UC-011](business-requirements.md#uc-011-system-releases-stock-for-stale-orders).

---

## Stock

### Stock status
A display-only, derived label — not a stored field — computed from an item's stock quantity against the low-stock threshold: `in_stock`, `low_stock`, or `out_of_stock`. See [UC-002](business-requirements.md#uc-002-end-user-browses-and-searches-the-catalog) and [UC-007](business-requirements.md#uc-007-admin-manages-stock).

### Walk-in sale
An in-person purchase made at Mini Mart's physical store, recorded by Admin, that deducts from the same stock pool as online orders — there is no separate stock count per channel. First established in [`client-context.md`](client-context.md#phase-1-decisions) (decision-05).

### Service area
The fixed delivery radius around the store within which checkout is permitted; an address outside it is rejected at checkout ([UC-003](business-requirements.md#uc-003-end-user-places-an-order)). First established in [`client-context.md`](client-context.md#phase-1-decisions) (decision-01).

---

## Delivery Agent

### Delivery Agent status
The lifecycle of an agent's account: `pending_approval` (self-registered, awaiting admin review) → `approved` (can receive order assignments) → `deactivated` (admin cuts off a previously-approved agent — quit, unreliable, etc.; can no longer receive new assignments), or `pending_approval` → `rejected` (admin declined the registration — never approved). `deactivated` and `rejected` are not interchangeable: `deactivated` is reachable only from `approved`, `rejected` only from `pending_approval`. See [UC-009](business-requirements.md#uc-009-delivery-agent-registers-and-gets-approved) and CR-001 (`docs/implementation/AUTH/change-records/CR-001.md`).

---

## Payment

### COD (Cash on Delivery)
The only payment method in Phase 1 — the delivery agent collects cash from the End User at the point of delivery and confirms collection in-app before the order is marked `delivered`. First established in [`client-context.md`](client-context.md#phase-1-decisions) (decision-09).
