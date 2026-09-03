# Glossary

Terms used across Daksh documents. When a term appears in any stage output, it means what's defined here — not what a cold reader might guess. Every term is a `###` heading so other documents can link directly to it: `[stage](glossary#stage)`, `[manifest](glossary#manifest)`, etc. Module-stage docs use `../../glossary#term`.

---

## Pipeline Structure

### Stage
A named phase of the Daksh pipeline. Each stage has one input (the previous stage's output), one output document, and an approval gate before the next stage can proceed. Stages 00–50c and 90 are [document stages](#document-stage); stage 50d is an [execution session](#execution-session).

### Document stage
Any stage that produces a document as its artifact (`onboard`, `vision`, `brd`, `solution`, `system`, `roadmap`, `design`, `trd`, `tasks`, `handbook`). Contrast with [execution session](#execution-session).

### Execution session
Stage 50d (`/daksh impl`). Produces code, a PR, and optionally a [change record](#change-record) — not a document. One task per session.

### Separate gate
Daksh v0.6 gives every stage its own document and approval. `stages_merged`
must be empty. Stage 40 Experience Design Spec is optional; all other module
stages are required.

### Weight class
Project classification — `small`, `medium`, or `large` — determined at init
from timeline and module count. It controls approval count, open-question policy,
and tend frequency; it never changes the document hierarchy.

### Module
A major feature area with its own Solution, System, optional Experience Design Spec, TRD,
Test Specification, Tasks, and Implementation.

### Experience Design Spec
The optional stage 40 frontend implementation contract. It owns information
architecture, navigation, screens, widgets, interaction behavior, mock API
payloads, mock data, edge states, prototype evidence, and shared component
decisions for one module.

---

## Manifest

### Manifest
The machine-readable pipeline state file at `docs/.daksh/manifest.json`. Every `/daksh` invocation reads it. Tracks [stage](#stage) status, approvals, [doc hashes](#doc-hash), [team roster](#roster), modules, [traceability](#traceability-chain), and [cross-module contracts](#cross-module-contract). Created by `/daksh init`; if it doesn't exist, no stage will run.

### Doc hash
SHA-256 digest of an output file, computed at the time the file is written or approved. Stored in the [manifest](#manifest). If the file changes after approval, the hash no longer matches — this is a [stale approval](#stale-approval).

### Stale approval
An approval whose [doc hash](#doc-hash) no longer matches the current file on disk. Detected by `/daksh tend`. Means someone approved a version that no longer exists.

### Stage status
The lifecycle state of a [stage](#stage) in the [manifest](#manifest): `not_started` → `in_progress` → `pending_approval` → `approved` (or `revision_needed`).

### Roster
The `team_roster` array in the [manifest](#manifest). Only people on the roster can approve [gates](#gate). The PTL manages the roster. Added at init; members can be added later via manifest edit + `/daksh tend`.

---

## Gates and Approvals

### Gate
The approval count check at the start of each [stage](#stage). Reads the prior stage's approval count from the [manifest](#manifest): 0 approvals = [hard stop](#hard-stop), fewer than required = warning, met = proceed. The gate is what makes stages sequential by contract, not just by convention.

### Approval
A recorded sign-off in the [manifest](#manifest): approver name, role, date, and the [doc hash](#doc-hash) at approval time. Required before the next stage can proceed. [Small weight class](#weight-class) requires 1; medium and large require 2.

### Approval gate
The block at the bottom of every stage output document where approvers fill in their name, role, and date. Reading this block is how the next stage counts approvals.

### Hard stop
A [gate](#gate) outcome where the system refuses to proceed. Triggered when 0 approvals are found on the prior stage. Cannot be overridden by "proceed anyway" — requires actual sign-off.

---

## Traceability

### Traceability chain
The lineage from business need to evidence:
[UC](#uc) → [FR](#fr) → [SS](#ss) → [SY](#sy) → TRD requirement →
[Test](#test) → [TASK](#task) → evidence.

### UC
Use Case. Top-level user need. Identified as `UC-001`, `UC-002`, etc. Defined in the BRD (`/daksh brd`). Every [functional requirement](#fr) must reference a UC.

### FR
Functional Requirement. A specific, testable product behavior that implements part of a [UC](#uc). Identified as `FR-001`, `FR-002`, etc. Defined in the BRD. Every [user story](#us) must reference an FR.

### NFR
Non-Functional Requirement. A constraint on how the system behaves — performance, security, reliability, maintainability. Not traced to a [UC](#uc), but must be satisfied by TRD design choices.

### SS
Solution behavior for one module. Identified as `SS-[MODULE]-NNN`; traces to a
[UC](#uc) or [FR](#fr). Defined in stage 30c.

### SY
System behavior for one module, stated so pass/fail is testable. Identified as
`SY-[MODULE]-NNN`; traces to a module `SS`. Defined in stage 30d.

### Test
A stable proof case in the module Test Specification. Identified as
`TEST-[MODULE]-NNN`; maps Solution, System, or testable TRD requirements to
setup, data, steps, and an observable expected result.

### TASK
A unit of implementation or test work for one engineer in one sprint.
Identified as `TASK-[MODULE]-001`; preserves the Test IDs it implements.

### Orphan
A traceability ID with a missing required link, including a requirement without
a Test or a Test without a Task.

---

## Implementation

### Decision budget
A per-[TASK](#task) field specifying exactly what the engineer can decide independently vs. what must be escalated to TL or PTL. Prevents both under-delivery (waiting for permission on trivial choices) and over-delivery (making architectural decisions unilaterally). Mandatory on every task.

### Change record
A structured document raised via `/daksh change [MODULE]` when implementation reality diverges from the spec. Written to `docs/implementation/[MODULE]/change-records/CR-NNN.md`. Contains what was specified, what reality showed, impact, proposed resolution, and a change summary listing every doc mutation. The change command patches affected planning docs, marks them `pending_approval`, creates a change task, and registers the CR in `manifest.change_records`. The engineer cannot proceed past the divergence until `/daksh approve CR-NNN` resolves the change set. A project with zero change records either had perfect foresight or never looked hard enough.

### Change record tier
The highest document a change touches: `tasks`, `test`, `trd`, `design`,
`system`, `solution`, `roadmap`, or `brd`.

### Definition of Done
The five conditions that must all be true before a task is marked Done: acceptance criteria confirmed, mapped Tests passing, frontend artifacts reconciled, handbook patched, and Jira/PR state updated.

### Test Specification
The separate stage 50b document that defines Test cases, coverage, setup, data,
expected results, and requirement mappings for one module.

### Cross-module contract
A formal interface agreement between two modules — who produces what, who consumes it, and what the shape is. Defined in `/daksh roadmap`, tracked in `manifest.contracts`. Changes must be approved by the PTL and may trigger downstream revision.

### Contract version
Semver attached to a cross-module contract or Interface. TRDs must reference both name and version so shape drift is visible.

### Compatibility
The change class for a contract version: `breaking`, `additive`, or `patch`.

### State machine
Closed lifecycle for an entity: states, initial state, terminal states, transitions, guards, and invariants.

### Evidence tier
Confidence label on infrastructure sizing or SLO values: `assumed`, `estimated`, or `measured`.

---

## Document Quality

### Doc-narrator
The writing skill that Daksh stages invoke before generating output. Enforces prose-before-diagrams, context seeds, open questions sections, narrative structure, and glossary linking. An output written without doc-narrator patterns is harder to read cold.

### Vyasa conventions
Formatting and structure rules from the `vyasa` skill: callout syntax, heading hierarchy, sidebar ordering via `.vyasa`, Mermaid diagram rules, and content structure. All Daksh outputs must follow Vyasa conventions to render correctly in the Vyasa doc viewer.

### Context seed
The opening paragraph of a stage document — 3–5 sentences that orient a cold reader: what this document is, why it exists, who it's for, and why now. Every stage output starts with one. The heading is chosen to fit the document, not prescribed.

### Leap-of-faith assumption
An unvalidated belief that the product depends on. If wrong, the product fails — not degrades. Mandatory section in the vision document. Unvalidated assumptions dressed as decisions are kindling.

---

## Commands

### init
`/daksh init` — the pipeline bootstrapper. Creates the [manifest](#manifest), determines [weight class](#weight-class), scaffolds directories including `docs/glossary.md`. Must run before any stage.

### tend
`/daksh tend` — health audit. Hashes all output files and compares to [manifest](#manifest), checks for [orphan](#orphan) traceability IDs, flags [stale approvals](#stale-approval), identifies missing artifacts. Run frequency depends on weight class.

### change
`/daksh change [MODULE]` — change intake and re-planning command. Creates a [change record](#change-record), patches affected planning docs, marks them `pending_approval`, creates a change task, and registers the CR in the [manifest](#manifest). Does not execute — execution happens later via `/daksh impl`. The only sanctioned way to create change records; hand-written CRs bypass governance.

### preflight
`/daksh preflight` — pre-stage validation. Checks that required skills are available, [gate](#gate) conditions are met, no documents are `pending_approval` from open [change records](#change-record), and context budget is within limits before a stage runs.

---

## Cognition Graph

### User
A graph entity kind: a persona who experiences the system or is responsible for its work. Carries `role`, `audience` (`delivery` / `client` / `end_customer`), and `status` (`validated` if interviewed, `placeholder` if assumed but not yet confirmed with a real person). First entered the ontology at stage 00 onboarding, where every named persona becomes a `User` node; carries the same ID forward into every later stage doc that references it.
