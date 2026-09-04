---
daksh:
  type: experience-design
  subtype: null
  stage: "40"
  module: AUTH
---

# AUTH Experience Design Spec

AUTH's [Solution](solution.md) and [System](system.md) specs fixed five business flows and their logical behavior; this document gives them a real frontend contract — screens, states, and interaction detail a designer or an engineer can build from without guessing. It covers all three roles equally per this stage's own scope call: End User's email+OTP signup/login, Delivery Agent's registration and status screens, and Admin's login and password recovery all get the same design discipline, not just the highest-traffic one. Fidelity is a real interactive HTML prototype, not annotated wireframes — see [Prototype Evidence](#prototype-evidence) for the live artifact. No existing brand identity exists for Mini Mart; this spec creates one from scratch, drawing on clean modern grocery/delivery apps (Blinkit, Zepto, Swiggy Instamart) for the consumer-facing energy and Stripe/Linear-style restraint for Admin's operator screens — one shared design system, not two clashing ones, per vision's [decision-13](../../vision.md#vision-decisions) (one integrated product, three role-based views).

<details>
<summary>Graph: How do primitives, design tasks, and executed screens fit together?</summary>

```items
---
id: 40-auth-design-cognition
title: AUTH Experience Design — Primitives, Tasks, Screens
default_open_depth: 1
default_color_by: kind
color_palette_source: .daksh/color-palette.json
width: 95vw
---
id: 40-auth-design-cognition
title: AUTH Experience Design — Primitives, Tasks, Screens
Users:
  - user-01 :: Admin | kind: user | summary: "Runs the mart's catalog, pricing, and stock, and oversees orders and delivery agents." | spec: [Personas and Context of Use](experience-design.md#personas-and-context-of-use) | role: "Mart Admin/Owner" | audience: client | user_type: operator | status: placeholder
  - user-02 :: Delivery Agent | kind: user | summary: "Picks up assigned orders and delivers them to end users, collecting cash on delivery." | spec: [Personas and Context of Use](experience-design.md#personas-and-context-of-use) | role: "Delivery Agent" | audience: client | user_type: practitioner | status: placeholder
  - user-03 :: End User | kind: user | summary: "Browses the catalog, places an order, and pays cash on delivery when it arrives." | spec: [Personas and Context of Use](experience-design.md#personas-and-context-of-use) | role: "Shopper/Customer" | audience: end_customer | user_type: consumer | status: placeholder
Constraints:
  - constraint-color :: Color token contract | kind: constraint | summary: "Primary/secondary/neutral/semantic color tokens every AUTH screen must use — no ad hoc hex values in any screen." | spec: [4A Primary Design Primitives](experience-design.md#4a-primary-design-primitives) | source: "Created here — no existing brand to inherit from."
  - constraint-type :: Typography contract | kind: constraint | summary: "Inter typeface, a fixed type scale, and weight rules for every screen." | spec: [4A Primary Design Primitives](experience-design.md#4a-primary-design-primitives) | source: "Created here."
  - constraint-spacing :: Spacing and layout contract | kind: constraint | summary: "A 4px-based spacing scale and responsive grid every screen lays out against." | spec: [4A Primary Design Primitives](experience-design.md#4a-primary-design-primitives) | source: "Created here."
  - constraint-a11y :: Accessibility contract | kind: constraint | summary: "Contrast, focus, keyboard, and touch-target rules with numeric targets, not \"should be accessible.\"" | spec: [4A Primary Design Primitives](experience-design.md#4a-primary-design-primitives) | source: "Created here."
Components:
  - component-btn :: Button | kind: component | summary: "The one button control every AUTH screen uses — primary, secondary, and destructive variants, all states." | spec: [4A Primary Design Primitives](experience-design.md#4a-primary-design-primitives) | boundary: "Atomic control — no page-specific button styles anywhere in AUTH."
  - component-input :: Text/email input | kind: component | summary: "The one text input control — label, helper text, error state, all states." | spec: [4A Primary Design Primitives](experience-design.md#4a-primary-design-primitives) | boundary: "Atomic control, reused by every form field across all three roles."
  - component-otp-input :: OTP segmented input | kind: component | summary: "A 6-box segmented code input, auto-advance per digit, paste support — the one distinctive control this module needs beyond generic form fields." | spec: [4A Primary Design Primitives](experience-design.md#4a-primary-design-primitives) | boundary: "Atomic control, used only by ss-auth-001's OTP entry screens."
  - ds-auth-001 :: Email entry screen | kind: component | summary: "Where End User or Delivery Agent enters their email to start signup or login." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Entry point for ss-auth-001; produces nothing but a submitted email."
  - ds-auth-002 :: OTP entry screen | kind: component | summary: "6-digit code entry, live countdown to resend, inline error on wrong code." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Follows ds-auth-001; on success, exits to whichever role's home screen."
  - ds-auth-003 :: Rate-limit-exceeded state | kind: component | summary: "Shown when the 5th OTP request in an hour is exceeded — explains why, states when they can try again." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "A state of ds-auth-001, not a separate route."
  - ds-auth-004 :: Agent registration form | kind: component | summary: "Where a prospective Delivery Agent submits name, phone, and a selfie/ID photo upload for Admin to review ([decision-65](#))." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Entry point for ss-auth-002; produces a pending_approval record."
  - ds-auth-005 :: Registration submitted confirmation | kind: component | summary: "Confirms the registration was received and explains the approval wait — sets expectations, not just a generic success toast." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Follows ds-auth-004."
  - ds-auth-006 :: Agent status screen | kind: component | summary: "One template, three states: approved (welcome, can now log in), rejected (explains outcome), deactivated (explains outcome, distinct copy from rejected per decision-55/57)." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Shown when an agent tries to log in and their status isn't a simple \"proceed\" case."
  - ds-auth-007 :: Admin login screen | kind: component | summary: "Username/password entry, deliberately plain — no OTP step, per decision-51." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Entry point for ss-auth-003."
  - ds-auth-008 :: Password reset request screen | kind: component | summary: "Admin requests a reset link to their registered recovery email." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Entry point for ss-auth-004."
  - ds-auth-009 :: Password reset confirm screen | kind: component | summary: "Reached via the emailed link — enter and confirm a new password." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Follows ds-auth-008, only reachable via a valid unused link."
  - ds-auth-010 :: Reset-link expired/used state | kind: component | summary: "Shown when the reset link is opened after use or after expiry — explains why, offers to request a new one." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "A state of ds-auth-009, not a separate route."
  - ds-auth-011 :: Session-expired prompt | kind: component | summary: "Shown app-wide (not AUTH-specific) when a 7-day session lapses mid-use — re-enter credentials without losing the page they were on." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Shared shell state, not a standalone screen."
  - ds-auth-012 :: Generic error state | kind: component | summary: "Network/server failure state shared across every AUTH screen — one visual pattern, not one per screen." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Shared state, reused by DC-AUTH-002."
  - dc-auth-001 :: StatusBadge | kind: component | summary: "A small colored label for pending_approval/approved/deactivated/rejected — used on ds-auth-006 and, later, Admin's agent list in CATALOG/ORDERS' own screens." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Secondary component — 2+ expected uses, promoted per the library-back rule."
  - dc-auth-002 :: ErrorStatePanel | kind: component | summary: "A reusable empty/error panel (icon, message, retry action) used by ds-auth-003, ds-auth-010, and ds-auth-012." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | boundary: "Secondary component — 3 expected uses."
Decisions:
  - decision-61 :: Inter as the primary typeface | kind: decision | summary: "Inter (free, Google Fonts) is the one typeface across all three role views — clean at both consumer display sizes and admin data density." | spec: [4A Primary Design Primitives](experience-design.md#4a-primary-design-primitives) | alternatives: "A paid/licensed brand font — rejected on cost grounds, consistent with every other cost-conscious choice this project has made. A second, more \"playful\" display font for End User only — rejected; would fracture the one-shared-system decision below." | reversal_trigger: "A real brand identity is commissioned later and specifies its own typeface."
  - decision-62 :: Fresh green as the primary brand color | kind: decision | summary: "A saturated green (`#059669`) is Mini Mart's primary color — grocery/freshness association, distinct enough from generic blue-SaaS without being an arbitrary choice." | spec: [4A Primary Design Primitives](experience-design.md#4a-primary-design-primitives) | alternatives: "Blue (generic, safe, but says nothing about groceries). Orange/yellow (matches Zepto/Swiggy's energy but risks looking like a direct copy rather than Mini Mart's own identity)." | reversal_trigger: "The client provides a real brand identity with a different primary color."
  - decision-63 :: One shared design system across all three role views | kind: decision | summary: "Admin and Delivery Agent screens use the same tokens, type scale, and controls as End User's — denser layout for Admin's data-heavy screens, but the same visual language, not a second brand." | spec: [4A Primary Design Primitives](experience-design.md#4a-primary-design-primitives) | alternatives: "A distinct, more \"enterprise\" visual system for Admin — rejected; contradicts vision's decision-13 (one integrated product) and doubles the design-system maintenance burden for a solo build." | reversal_trigger: "Admin's screens grow complex enough that the consumer-oriented primitives genuinely can't serve dense data tables well."
  - decision-64 :: OTP input supports paste and platform autofill | kind: decision | summary: "component-otp-input accepts a pasted 6-digit code (fills all boxes at once) and integrates with platform autofill suggestions where the OS/browser offers them, resolving oq-46." | spec: [4A Primary Design Primitives](experience-design.md#4a-primary-design-primitives) | alternatives: "Manual digit-by-digit entry only — rejected; adds friction to the single most frequent action in the app for no real benefit." | reversal_trigger: "None expected — this is additive to the existing digit-entry behavior, not a replacement."
  - decision-65 :: Agent registration collects a photo alongside name and phone | kind: decision | summary: "ds-auth-004 collects name, phone, and a selfie/ID photo upload; Admin reviews the photo manually as part of the pending_approval decision, resolving oq-47. No automated ID-verification service." | spec: [4C Design Execution](experience-design.md#4c-design-execution) | alternatives: "Name+phone only — rejected; leaves Admin nothing to judge trustworthiness by before approving someone to handle deliveries and COD cash. Full government-ID verification — rejected; overkill for a single-store MVP where Admin already approves manually." | reversal_trigger: "Agent volume grows past what manual photo review can keep up with."
  - decision-66 :: Drafted microcopy locked as final | kind: decision | summary: "The representative copy already written across ds-auth-001 through ds-auth-012 (labels, error messages, status banners) is treated as final, resolving oq-48 — no separate client copy-review pass." | spec: [Open Questions](experience-design.md#open-questions) | alternatives: "A dedicated copy-review cycle before TRD — rejected; the drafted copy already follows this project's plain-language, no-corporate-tone standard, and a separate pass would only delay stage 50a for no material gain." | reversal_trigger: "A specific screen's copy is flagged as confusing during stage 50b test authoring or later usability evaluation."
Tasks:
  - dt-auth-001 :: Design End User / Agent email+OTP screens | kind: task | summary: "ds-auth-001, ds-auth-002, ds-auth-003 — the shared signup/login mechanism both roles use." | spec: [4B Design Task Breakdown](experience-design.md#4b-design-task-breakdown) | estimate: "1 design session" | acceptance: "All 3 screen states reviewed against ss-auth-001 and sy-auth-001..004"
  - dt-auth-002 :: Design Agent registration and status screens | kind: task | summary: "ds-auth-004, ds-auth-005, ds-auth-006 — registration through to knowing where they stand." | spec: [4B Design Task Breakdown](experience-design.md#4b-design-task-breakdown) | estimate: "1 design session" | acceptance: "All 3 screens plus StatusBadge's 4 color states reviewed against ss-auth-002 and sy-auth-005..008"
  - dt-auth-003 :: Design Admin login | kind: task | summary: "ds-auth-007 — deliberately the simplest screen in this spec." | spec: [4B Design Task Breakdown](experience-design.md#4b-design-task-breakdown) | estimate: "0.5 design session" | acceptance: "Reviewed against ss-auth-003 and sy-auth-009..010"
  - dt-auth-004 :: Design Admin password recovery | kind: task | summary: "ds-auth-008, ds-auth-009, ds-auth-010 — request through to a new password, including the expired-link dead end." | spec: [4B Design Task Breakdown](experience-design.md#4b-design-task-breakdown) | estimate: "1 design session" | acceptance: "All 3 screens reviewed against ss-auth-004 and sy-auth-011..012"
  - dt-auth-005 :: Design shared session/error states | kind: task | summary: "ds-auth-011, ds-auth-012, and ErrorStatePanel — the states every other AUTH screen (and eventually CATALOG/ORDERS) can fall into." | spec: [4B Design Task Breakdown](experience-design.md#4b-design-task-breakdown) | estimate: "0.5 design session" | acceptance: "Reviewed against ss-auth-005 and sy-auth-013..014"
Flows:
  - journey-enduser-signin :: End User sign-in journey | kind: flow | summary: "Email entry through to a live session, including the rate-limit and wrong-code detours." | spec: [User Journeys](experience-design.md#user-journeys) | actor: "End User" | trigger: "Visits the storefront with no active session" | outcome: "Verified session, lands on the catalog"
  - journey-agent-onboarding :: Delivery Agent onboarding journey | kind: flow | summary: "Registration through to their first successful login as an approved agent." | spec: [User Journeys](experience-design.md#user-journeys) | actor: "Delivery Agent" | trigger: "Wants to start delivering for Mini Mart" | outcome: "Approved agent with a live session, or a clear rejected/deactivated explanation"
  - journey-admin-recovery :: Admin password recovery journey | kind: flow | summary: "Forgotten password through to a working new one, including the expired-link dead end." | spec: [User Journeys](experience-design.md#user-journeys) | actor: "Admin" | trigger: "Cannot remember their password" | outcome: "New password set and a live session, or a clear expired-link explanation with a way to retry"
Metrics:
  - metric-otp-completion :: OTP entry completion rate | kind: metric | summary: "Share of OTP entries that succeed without a wrong-code error." | spec: [Usability and Accessibility Criteria](experience-design.md#usability-and-accessibility-criteria) | baseline: "unmeasured (no prior version exists)" | target: "85%+ first-attempt success" | current: "not yet measured"
  - metric-a11y-contrast :: Text contrast ratio | kind: metric | summary: "Every text/background pairing across all AUTH screens." | spec: [Usability and Accessibility Criteria](experience-design.md#usability-and-accessibility-criteria) | baseline: "n/a — design-time target" | target: "WCAG AA, 4.5:1 minimum for body text" | current: "met in the prototype's token contract"
  - metric-signup-time :: Time to complete signup | kind: metric | summary: "Wall-clock time from ds-auth-001 to a live session for a first-time End User." | spec: [Usability and Accessibility Criteria](experience-design.md#usability-and-accessibility-criteria) | baseline: "unmeasured" | target: "under 45 seconds excluding email-delivery wait" | current: "not yet measured"
user-03 -> ds-auth-001 | relation: experiences
user-03 -> ds-auth-002 | relation: experiences
user-02 -> ds-auth-004 | relation: experiences
user-01 -> ds-auth-007 | relation: owns
user-01 -> ds-auth-006 | relation: owns
constraint-color -> component-btn | relation: governs
constraint-type -> component-input | relation: governs
constraint-a11y -> component-otp-input | relation: governs
decision-61 -> constraint-type | relation: governs
decision-62 -> constraint-color | relation: governs
decision-63 -> constraint-spacing | relation: governs
decision-64 -> component-otp-input | relation: governs
decision-65 -> ds-auth-004 | relation: governs
dt-auth-001 -> ds-auth-001 | relation: produces
dt-auth-001 -> ds-auth-002 | relation: produces
dt-auth-001 -> ds-auth-003 | relation: produces
dt-auth-002 -> ds-auth-004 | relation: produces
dt-auth-002 -> ds-auth-005 | relation: produces
dt-auth-002 -> ds-auth-006 | relation: produces
dt-auth-003 -> ds-auth-007 | relation: produces
dt-auth-004 -> ds-auth-008 | relation: produces
dt-auth-004 -> ds-auth-009 | relation: produces
dt-auth-004 -> ds-auth-010 | relation: produces
dt-auth-005 -> ds-auth-011 | relation: produces
dt-auth-005 -> ds-auth-012 | relation: produces
ds-auth-001 -> ds-auth-002 | relation: enables
ds-auth-004 -> ds-auth-005 | relation: enables
ds-auth-008 -> ds-auth-009 | relation: enables
dc-auth-001 -> ds-auth-006 | relation: governs
dc-auth-002 -> ds-auth-003 | relation: governs
dc-auth-002 -> ds-auth-010 | relation: governs
dc-auth-002 -> ds-auth-012 | relation: governs
metric-a11y-contrast -> constraint-a11y | relation: watches
```

</details>

> [!note]
> This graph carries 41 nodes across 7 groups — the closest to the 10-16 root-group ideal of any stage in this project so far, since a real design spec (primitives + tasks + screens) genuinely has more distinct structural entities than a project-wide doc. `Users` are reused from the BRD/vision by the same IDs. Screen-to-screen `enables` edges are deliberately sparse (only the 3 true linear hops) — most screens are reached via a task, not chained to each other, which is honest: this module doesn't have a long multi-screen wizard anywhere. All 3 of this spec's open questions (oq-46/47/48) resolved into decisions ([decision-64](#)–[decision-66](#)) during review, so the `OpenQuestions` group that existed in the first draft is gone — nothing unresolved remains at this stage.

## 4A Primary Design Primitives

**Primitive source of truth.** Mini Mart has no existing brand identity, design system, or component library ([client-context.md](../../client-context.md), [decision-61](#)–[decision-63](#)) — everything below is created here, not inherited. What's explicitly *not* decided yet: final logo/wordmark (out of scope for AUTH). Microcopy is decided — [decision-66](#) locks the drafted copy as final.

**Token contract** (CR-006: corrected to match the published prototype exactly — [decision-62](#)'s choice of a saturated green stands, only the precise hex values below were wrong in the first draft). Each color names its light-theme value, then its dark-theme value.

| Token | Light / Dark | Notes |
|---|---|---|
| Primary (jade) | `#12734f` / `#2fa578` | Buttons, links, focus rings, brand accents ([decision-62](#)) |
| Primary-deep (hover/active) | `#0a4f36` / `#3fc290` | |
| Primary-tint | `#e3f1ea` / `#1b2b23` | Approved-state fills, subtle highlight backgrounds |
| Background (paper) | `#faf8f4` / `#161510` | Page background — warm off-white, not stark white |
| Surface-raised | `#ffffff` / `#201f19` | Cards, the device/browser frame surface |
| Text (ink) | `#1c1b18` / `#f2efe9` | Body text |
| Text-secondary (ink-soft) | `#4a473f` / `#c9c4b8` | Helper text, placeholders |
| Border/neutral (sand) | `#8c8672` / `#948e7c` | Secondary icons, muted labels |
| Border-line | `#e4e0d5` / `#3a382f` | Input borders, dividers |
| Neutral-fill (sand-fill) | `#f0ede4` / `#211f19` | Chip/tab backgrounds |
| Warning/pending accent (gold) | `#c98a2e` / `#e0a748` | `pending_approval` StatusBadge state, submitted-confirmation icon |
| Gold-tint | `#faf0dd` / `#2b2416` | Gold accent's fill background |
| Error (brick) | `#ae4034` / `#d9695b` | Error text, borders, icons, `rejected`/`deactivated` StatusBadge states |
| Error-tint (brick-tint) | `#f7e9e7` / `#2e1c19` | Error accent's fill background |
| Shadow | `0 1px 2px rgba(28,27,24,.06), 0 8px 24px -8px rgba(28,27,24,.18)` / `0 1px 2px rgba(0,0,0,.3), 0 12px 28px -10px rgba(0,0,0,.5)` | Card elevation |
| Display typeface | Fredoka (Google Fonts) | Wordmark and large display moments only — not a second UI face; everything else stays Inter ([decision-61](#)) |
| Body/UI typeface | Inter (Google Fonts) | [decision-61](#) — free, clean at all sizes |
| Type scale | 12/14/16/20/24/32px | Caption / body / body-lg / h3 / h2 / h1 |
| Spacing scale | 4/8/12/16/24/32/48/64px | 4px base unit throughout |
| Radius | 8px (inputs/buttons), 12px (cards) | Friendly, not childish |
| Touch target | 44×44px minimum | Every tappable element, per [constraint-a11y](#) |

**Atomic controls.**

- **[component-btn](#) Button** — primary (filled, `#059669`), secondary (outlined), destructive (red, used nowhere in AUTH itself but reserved for CATALOG/ORDERS' delete actions). States: default, hover, focus (visible 2px ring), active, disabled (40% opacity, no pointer events), loading (spinner replaces label, button stays same width to avoid layout shift).
- **[component-input](#) Text/email input** — label above, helper text below (gray), error text below (red, replaces helper text). States: default, focus (primary-colored border + ring), error (red border), disabled.
- **[component-otp-input](#) OTP segmented input** — 6 individual boxes, auto-advances focus on digit entry, backspace moves focus back, pasting a full code fills all 6 at once and platform autofill suggestions are accepted where offered ([decision-64](#)). States: default, focus (current box highlighted), filled, error (all boxes flash red border briefly, then clear for retry).

**Accessibility contract** ([constraint-a11y](#)): 4.5:1 minimum contrast for body text, 3:1 for large text/icons ([metric-a11y-contrast](#)); every interactive element reachable and operable by keyboard alone; every form error is announced to screen readers via `aria-live`, not color alone; focus order follows visual reading order top-to-bottom.

**Primitive decisions:** see [decision-61](#), [decision-62](#), [decision-63](#), [decision-64](#) in the graph above for full alternatives/reversal triggers.

**Open primitive questions:** none — [decision-64](#) resolved OTP paste/autofill support during review.

## 4B Design Task Breakdown

**Grouping: flow.** AUTH's five Solution flows map close to one task each — grouping by persona would have meant three groups covering nearly the same screens as grouping by flow, since Admin and Delivery Agent are single-flow personas here; flow is the more natural checklist.

**Task inventory:** [dt-auth-001](#) through [dt-auth-005](#) — see the graph for each task's screens, estimate, and acceptance evidence. All five trace to a named `SS-AUTH-NNN` flow (Solution) and its `SY-AUTH-NNN` behaviors (System).

**Task sequencing:** [dt-auth-001](#) has no dependency and should run first — it's the highest-traffic screen and validates the token contract fastest. [dt-auth-005](#) (shared error/session states) should run early too, since [dt-auth-002](#) and [dt-auth-004](#) both reuse [dc-auth-002](#) (ErrorStatePanel) it produces — if [dt-auth-005](#) runs last, those two tasks would have to guess at the shared pattern and risk a mismatch. Recommended order: dt-auth-005 → dt-auth-001 → dt-auth-003 → dt-auth-002 → dt-auth-004. [dt-auth-003](#) (Admin login) can run any time after dt-auth-005 — it shares no screens with the others.

**State coverage:** every task's acceptance criterion in the graph names its required states explicitly (see each `ds-auth-*` node's `boundary` attribute) — happy path, error, and the specific edge states each flow actually has (rate-limit, expired-link, rejected/deactivated).

**Reuse plan:** [dc-auth-001](#) (StatusBadge) and [dc-auth-002](#) (ErrorStatePanel) are expected to be reused by CATALOG's and ORDERS' own future Experience Design Specs wherever they show a Delivery Agent's status or a generic error — flagged now so those modules' designers check here first instead of reinventing them.

**Acceptance evidence:** the live prototype (see [Prototype Evidence](#prototype-evidence)) for all screens; the usability/accessibility criteria table for the numeric targets.

**Deferred tasks:** a "sign in with Google/Apple" option was considered and explicitly deferred — no requirement anywhere asked for it, and it would add an OAuth integration this cost-conscious project hasn't budgeted for. Not blocking anything downstream.

## Personas and Context of Use

**[Admin](#) ([user-01](#))** — the mart's owner/operator, logging in from a desk or counter computer, likely once per shift rather than dozens of times a day. Context: low-frequency but high-stakes (losing access is losing the whole business) — traces to [SS-AUTH-003](solution.md#business-flow-inventory)/[SS-AUTH-004](solution.md#business-flow-inventory).

**[Delivery Agent](#) ([user-02](#))** — registers once, then logs in daily, likely on a personal phone, possibly on the move or in poor network conditions. Context: needs the registration/status screens to be unambiguous about what happens next, since there's no existing process to fall back on — traces to [SS-AUTH-002](solution.md#business-flow-inventory).

**[End User](#) ([user-03](#))** — a shopper, on a phone, in a hurry, possibly a first-time visitor with zero context for how this mart's app works. Context: this is the highest-volume, most first-impression-sensitive flow in the whole module — traces to [SS-AUTH-001](solution.md#business-flow-inventory).

## 4C Design Execution

**Screen and state inventory:** [ds-auth-001](#) through [ds-auth-012](#) — see the graph for each screen's source task, source flow, and state coverage. The prototype (see below) covers [ds-auth-001](#)–[ds-auth-009](#) fully, including all four [dc-auth-001](#) StatusBadge states on [ds-auth-006](#) via its state switcher. Not in the prototype: [ds-auth-010](#) (reset-link expired/used), [ds-auth-011](#) (session-expired), and [ds-auth-012](#) (generic error) — all three are single, mostly-static [dc-auth-002](#) ErrorStatePanel instances better demonstrated once a real page exists behind them to recover to; they're fully specified in the Screen and State Inventory graph nodes above regardless.

## Information Architecture and Navigation

AUTH's three roles are served by three role-scoped route groups within **one** Next.js deployable (CR-007) — `FRONTEND_STOREFRONT`, `FRONTEND_AGENT`, `FRONTEND_ADMIN` — [system-architecture.md](../../system-architecture.md#frontend-architecture), not three separate applications; navigation is scoped by URL path prefix, not by which separate app/domain was opened. This matters because [decision-49](solution.md#auth-decisions) lets the same email hold both an End User and a Delivery Agent identity — the path prefix, not the login form, decides which role's screens follow a successful OTP verify.

**FRONTEND_STOREFRONT (End User)** — unprefixed, the site's own root paths
- `/login` — [ds-auth-001](#) (email entry). Entry point: any unauthenticated visit.
- `/login/verify` — [ds-auth-002](#) (OTP entry). Reachable only after `/login` submits an email; back-navigation returns to `/login`, not a blank state.
- `/login/limited` — [ds-auth-003](#) (rate-limited). A state of `/login/verify`, not a distinct route the user can bookmark.
- Exit: successful verify lands on the catalog home (owned by CATALOG's own IA, out of scope here).

**FRONTEND_AGENT (Delivery Agent)** — `/agent/*` (CR-007), mirroring `FRONTEND_ADMIN`'s `/admin/*` prefix below
- `/agent/register` — [ds-auth-004](#). Entry point for anyone without an agent record yet.
- `/agent/register/submitted` — [ds-auth-005](#). Reachable only immediately after a successful `/agent/register` submit.
- `/agent/status` — [ds-auth-006](#). Where a registered agent lands if their status isn't `approved`; an `approved` agent is instead routed to `/agent/login` → `/agent/login/verify` — the same reused screens [ds-auth-001](#)/[ds-auth-002](#) serve for End User, at the agent's own path prefix, not literally End User's URL — per [decision-49](solution.md#auth-decisions).
- Exit: `approved` status plus a verified OTP lands on the agent's assigned-orders view (owned by ORDERS' own IA, out of scope here).

**FRONTEND_ADMIN (Admin)**
- `/admin/login` — [ds-auth-007](#). The only entry point; there is no admin self-registration.
- `/admin/reset` — [ds-auth-008](#), reachable from a "Forgot password" link on `/admin/login`.
- `/admin/reset/confirm?token=...` — [ds-auth-009](#), reachable only via the token-bearing link emailed after `/admin/reset` — never linked to directly from within the app.
- `/admin/reset/confirm` with an already-used or expired token renders [ds-auth-010](#) in place of the form, same route.
- Exit: successful login or reset lands on the Admin dashboard (owned by CATALOG/ORDERS' own IA, out of scope here).

**Shared, app-wide**
- [ds-auth-011](#) (session-expired) interrupts any authenticated route in any of the three apps when the 7-day session lapses ([decision-52](solution.md#auth-decisions)) — it re-prompts for credentials without discarding the page the person was on, then returns them there.
- [ds-auth-012](#) (generic error) replaces any route's content on a network/server failure, in any of the three apps.

## Mock Contracts and Data

These are frontend-facing mock contracts — stable field names and representative shapes the three frontend apps build against — not the backend's real schema or validation, which stage 50a (TRD) finalizes against [system.md](system.md)'s data models. Every field below is illustrative but traces to a named `dm-*` entity so TRD isn't guessing at intent.

| Endpoint (mock) | Request | Success response | Error/empty variants | Traces to |
|---|---|---|---|---|
| `POST /v1/auth/otp/request` | `{ "email": "shopper@example.com", "role": "end_user" }` | `202 { "cooldown_seconds": 60, "expires_in_seconds": 600 }` | `429 { "error": "rate_limited", "retry_after_seconds": 1800 }` (drives [ds-auth-003](#)) | [dm-otpcode](system.md#data-models) |
| `POST /v1/auth/otp/verify` | `{ "email": "shopper@example.com", "code": "482913", "role": "end_user" }` | `200 { "role": "end_user", "expires_at": "2026-09-11T10:00:00Z" }` + `Set-Cookie` (httpOnly, CR-004) | `401 { "error": "invalid_code" }` (inline on [ds-auth-002](#)); `410 { "error": "code_expired" }` | [dm-otpcode](system.md#data-models), [dm-session](system.md#data-models) |
| `POST /v1/auth/agent/register` | `{ "name": "Ravi Teja", "phone": "+919876543210", "email": "ravi.teja@gmail.com", "photo_url": "..." }` | `201 { "status": "pending_approval" }` | `409 { "error": "email_already_registered" }` | [dm-deliveryagent](system.md#data-models) |
| `GET /v1/auth/agent/status` | — (session-scoped) | `200 { "status": "approved" }` | `200 { "status": "rejected" }` / `200 { "status": "deactivated" }` — same shape, [dc-auth-001](#) maps color | [dm-deliveryagent](system.md#data-models), [dm-agent-status-log](system.md#data-models) |
| `POST /v1/auth/admin/login` | `{ "username": "admin", "password": "..." }` | `200 { "expires_at": "..." }` + `Set-Cookie` (httpOnly, CR-004) | `401 { "error": "invalid_credentials" }` (no distinction between wrong username vs password, to avoid enumeration) | [dm-adminaccount](system.md#data-models), [dm-session](system.md#data-models) |
| `POST /v1/auth/admin/password-reset/request` | `{ "email": "admin@minimart.app" }` | `202 {}` (always this shape, whether or not the email exists — no enumeration) | none | [dm-resettoken](system.md#data-models) |
| `POST /v1/auth/admin/password-reset/confirm` | `{ "token": "...", "new_password": "..." }` | `200 {}` + `Set-Cookie` (httpOnly, CR-004) | `410 { "error": "token_expired_or_used" }` (drives [ds-auth-010](#)) | [dm-resettoken](system.md#data-models) |

`role` note ([CR-002](change-records/CR-002.md)): the OTP request/verify payloads carry a `role` field disambiguating which identity (End User vs Delivery Agent) an email resolves to, since the same email can hold both ([decision-49](solution.md#business-states-decisions-and-recovery)). This adds no new screen or input — the value is implicit in which frontend app is calling ([Information Architecture and Navigation](#information-architecture-and-navigation)), so [ds-auth-001](#)/[ds-auth-002](#) are unchanged.

Session-delivery note ([CR-004](change-records/CR-004.md)): the three endpoints above that issue a session ([ds-auth-002](#), [ds-auth-007](#), [ds-auth-009](#)) deliver it via an `httpOnly` cookie the browser sets automatically, not a token the frontend reads from the response body and stores itself — no screen or interaction changes, since none of these screens ever needed to touch the token value directly.

Empty-state note: no AUTH screen has a true "empty list" state — every screen is single-record (one email, one OTP, one agent status, one admin account), so the empty/error variants above are the complete set; there is no pagination or collection-empty case to design for in this module.

## Widget and Interaction Contract

- **[component-btn](#) Button** — events: `onPress` (disabled while `loading`, which replaces the label with a spinner at fixed width so nothing reflows); `onFocus`/`onBlur` toggle the visible 2px ring. Keyboard: `Enter`/`Space` activate a focused button. Permission: no button in AUTH is conditionally rendered by role — each screen belongs to one role's app already, so there is no in-screen permission branching to design.
- **[component-input](#) Text/email input** — events: `onChange` (clears a prior error state on the next keystroke, per the a11y contract's "don't leave a stale error visible while the user is actively correcting it" rule), `onBlur` (triggers format validation, e.g. malformed email). Loading: none — inputs don't carry their own loading state, only the submitting button does. Keyboard/focus: standard tab order, `Enter` submits the enclosing form.
- **[component-otp-input](#) OTP segmented input** — events: `onDigitEntry` (auto-advances focus to the next box), `onBackspace` on an empty box (moves focus to the previous box and clears it), `onPaste` (fills all 6 boxes at once from a single pasted string, [decision-64](#)). Loading: all 6 boxes disable while verify is in flight. Error: all 6 boxes flash a red border on an invalid code, then clear and refocus box 1 for retry — the error is also announced via `aria-live` per [constraint-a11y](#), not conveyed by color alone.
- **[dc-auth-001](#) StatusBadge** — no interaction; a read-only label. Its 4 color states are driven entirely by the `status` field in the `GET /v1/auth/agent/status` mock response above.
- **[dc-auth-002](#) ErrorStatePanel** — events: `onRetry` (re-issues the failed request). No loading state of its own; it *is* the state shown after a request already failed.
- **Responsive rules:** [ds-auth-001](#)–[ds-auth-006](#) (End User, Delivery Agent) are designed mobile-first, single column, no desktop breakpoint — both roles' real usage is phone-only ([Personas and Context of Use](#personas-and-context-of-use)). [ds-auth-007](#)–[ds-auth-010](#) (Admin) assume a desktop/laptop browser at 1024px+ width; no mobile layout is designed for Admin in this module, consistent with the desk/counter-computer persona.
- **Permission behavior:** every AUTH screen is reachable only when unauthenticated (or, for [ds-auth-006](#)/[ds-auth-011](#), specifically mid-authentication or session-expiring) — there is no role-gating *within* AUTH's own screens to design, since role separation happens at the app level ([Information Architecture and Navigation](#information-architecture-and-navigation)).

## User Journeys

- **[journey-enduser-signin](#):** [ds-auth-001](#) → [ds-auth-002](#) → (success: lands on catalog) or → [ds-auth-003](#) (rate-limited, dead-ends with a retry time) or → inline error on [ds-auth-002](#) (wrong code, stays on screen).
- **[journey-agent-onboarding](#):** [ds-auth-004](#) → [ds-auth-005](#) → (later, once Admin decides) [ds-auth-006](#) showing `approved` (can now use [journey-enduser-signin](#)'s same email+OTP mechanism), `rejected`, or `deactivated`.
- **[journey-admin-recovery](#):** [ds-auth-008](#) → (email sent) → [ds-auth-009](#) (via emailed link) → new password set, session starts — or → [ds-auth-010](#) if the link was already used or expired, with a way back to [ds-auth-008](#).

## Prototype Evidence

A real, interactive HTML prototype covering the highest-value screen per persona plus the shared OTP mechanism: [ds-auth-001](#)/[ds-auth-002](#)/[ds-auth-003](#) (End User email+OTP, including the wrong-code and rate-limited states via an in-prototype state switcher), [ds-auth-004](#)/[ds-auth-005](#)/[ds-auth-006](#) (Agent registration through all four status states), and [ds-auth-007](#)/[ds-auth-008](#)/[ds-auth-009](#) (Admin login + recovery request + sent confirmation). It tests whether the one-shared-design-system decision ([decision-63](#)) actually reads as coherent across a consumer-energy mobile screen and an operator-plain desktop screen, and whether the OTP entry control feels fast rather than fussy.

**Prototype:** [Mini Mart AUTH Prototype](https://claude.ai/code/artifact/48f16f85-fe2b-4414-9d23-bcec69e0c3d8) — click through each role tab; the right-hand rail names the current `DS-AUTH-NNN` screen and the design decision behind it. State switchers (dashed-border controls, clearly marked "prototype only") demonstrate error/edge states that would otherwise require a real backend to trigger.

## Secondary Component Library

- **[dc-auth-001](#) StatusBadge** — pill-shaped label, color mapped to [sm-auth-agent-status](system.md#state-machines)'s four values (amber=pending_approval, green=approved, gray=deactivated, red=rejected). Source screen: [ds-auth-006](#). Expected reuse: CATALOG/ORDERS' own future admin screens showing agent status in an order-assignment list.
- **[dc-auth-002](#) ErrorStatePanel** — icon + message + retry button, used identically across [ds-auth-003](#), [ds-auth-010](#), [ds-auth-012](#). Owner: this module; sibling modules should check here before building their own error panel.

## Duplicate Component Gate

Scanned: no sibling module (`CATALOG`, `ORDERS`) has an Experience Design Spec yet — AUTH is first through this stage per the roadmap's build order, so there is nothing to duplicate against yet. This gate will need re-running once CATALOG's and ORDERS' specs exist, specifically checking their agent-status displays and error states against [dc-auth-001](#)/[dc-auth-002](#) before those modules invent their own. Flagged as a forward risk, not an open question — no action needed now.

## Usability and Accessibility Criteria

See [metric-otp-completion](#), [metric-a11y-contrast](#), [metric-signup-time](#) in the graph for the three numeric targets this spec commits to. All three are currently `assumed` targets (no prior version of this product exists to baseline against) — they become real once stage 50b's Test Specification defines how they're measured in practice.

## Evaluation Findings

None yet — this is the first pass through 4C for AUTH, and no usability testing has been run against the prototype. This section stays populated once real evaluation happens; an empty findings section at first-author time is expected, not a gap.

## Reconciliation Record

The prototype and this spec were authored together in one pass (not iterated against a separately-built prototype), so there is no drift to reconcile yet: every screen in the prototype corresponds to a `ds-auth-*` entry above with the same state coverage, and the two secondary components ([dc-auth-001](#), [dc-auth-002](#)) exist identically in both. One real diff did surface during open-question resolution: [decision-65](#) (photo upload at registration) was decided after the prototype's first pass, which had shipped [ds-auth-004](#) as text-fields-only. The prototype was updated in the same pass as this doc — [ds-auth-004](#) now includes the photo-upload field in both places, so no drift remains. This record will carry further diffs once the prototype is reviewed and revised again.

## Open Questions

None outstanding. All 3 questions this spec originally raised were resolved during review, each into a numbered decision rather than staying open:

- *Should the OTP input support paste/autofill?* Resolved yes — see [decision-64](#). [component-otp-input](#) accepts a full pasted code and platform autofill.
- *Does agent registration need photo/ID verification, not just contact details?* Resolved: name+phone+photo upload, manually reviewed by Admin — see [decision-65](#). [ds-auth-004](#) updated accordingly.
- *What's the final microcopy?* Resolved: the drafted copy across all screens is locked as final — see [decision-66](#). No separate copy-review cycle before stage 50a.

## Approval

Approved by: Bhargav
Role:        PTL
Date:        2026-09-04
Hash:        e5beb5951b19�

Approved by: Bhargav
Role:        PTL
Date:        2026-09-04
Via:         CR-002

Approved by: Bhargav
Role:        PTL
Date:        2026-09-04
Via:         CR-004

Approved by: Bhargav
Role:        PTL
Date:        2026-09-04
Via:         CR-006

Approved by: Bhargav
Role:        PTL
Date:        2026-09-04
Via:         CR-007
