# Self-Check Gates

The seven mechanical gates `scripts/gate-check.py` enforces before Act ⑤
emits the bundle. Overrides are handled per `gate-overrides.md`. Positive
constraints are orthogonal — see `schema-projection.md § positive-constraints`.

## Contents
- [Gate philosophy](#gate-philosophy)
- [Gate 1 — contrast (tiered)](#gate-1--contrast-tiered)
- [Gate 2 — neutral-scale](#gate-2--neutral-scale)
- [Gate 3 — triad-x-5state](#gate-3--triad-x-5state)
- [Gate 4 — dark-explicit](#gate-4--dark-explicit)
- [Gate 5 — token-closure](#gate-5--token-closure)
- [Gate 6 — affordance (v4.5)](#gate-6--affordance-v45)
- [Gate 7 — viewport-type (v4.5)](#gate-7--viewport-type-v45)
- [Output format](#output-format)

## Gate philosophy

Mechanical, not prose-by-convention. Every gate:

- Has a definite pass / fail / override check runnable by script
- Runs on `design.tokens.yaml` + rendered sample HTML, not on user
  conversation state
- Has a published error message mapping to a specific token path
- Is overrideable through the structured contract (except
  `token-closure` which is never overrideable — a broken reference is
  always a bug)

Gate evaluation is the Act ⑤ exit blocker. Every non-pass gate must have
an `override` entry with complete `reason` (three structured fields) and
`scope` (glob array), or the bundle does not emit.

## Gate 1 — contrast (tiered)

Tier 1 change from v4.5: contrast is layered, not single.

### Check
For every `(fg, bg)` token pair in the same contrast tier, compute WCAG
contrast ratio and compare to tier threshold:

| Tier | Body text threshold | Large text / UI threshold |
|---|---|---|
| `text` (default AA) | ≥ 4.5 | ≥ 3.0 |
| `text` (AAA override) | ≥ 7.0 | ≥ 4.5 |
| `ui` | ≥ 3.0 | ≥ 3.0 |
| `decoration` | (no check) | (no check) |

### Scope determination

Every token has an implicit tier from `color.contrast.tier.*.scope-globs`
in the tokens file. Untagged tokens default to `text` tier (strictest).

### Failure message

```
[FAIL] contrast.text: color.semantic.fg.muted (hsl 32 11% 37%)
       on color.semantic.bg.canvas (hsl 30 6% 7%) = 3.8:1
       (required ≥ 4.5:1 for body, ≥ 3.0:1 for large).
```

### Override path
Pattern C (decoration freedom) or Pattern D (AAA upgrade) in
`gate-overrides.md`.

## Gate 2 — neutral-scale

### Check
`color.neutral.*` contains at least 9 stops, sorted by luminance, with
monotonic L* progression. Adjacent stops must differ by ≥ 5% L* to ensure
perceptual differentiation.

### Rationale
Component state matrices require enough neutral stops to differentiate
`default / hover / focus / active / disabled / loading` surfaces without
reusing the same gray for two states. Fewer than 9 collapses state
differentiation.

### Failure message

```
[FAIL] neutral-scale: only 5 stops in color.neutral.*.
       State matrix for Button requires 6 perceptually-distinct grays
       (default, hover, active, disabled, loading, border).
       Hover and disabled would share gray L*=50%.
```

### Override path
Pattern A (split-layer) or Pattern B (palette-lock priority) in
`gate-overrides.md`. Each tier-override must declare `tier: <N>` and
demonstrate state matrices differentiate without the dropped stops.

## Gate 3 — triad-x-5state

### Check
For every component in `{Button, Input, Card, nav-item, list-row, form-row}`:

- Component block exists in `components.*`
- Every state in the component's declared `states:` list has a definition
  (even if it's an alias like `hover: "{component.button.active}"`)

### State sets

Base state sets defined in `components.base.*-5state` (see
`act-4a-components.md § state-inheritance`). Components declare `extends:`
or inline `states:`.

### Failure message

```
[FAIL] triad-x-5state: component.input declares extends:
       form-5state (states: default, hover, focus, disabled, error)
       but form-row.error is missing indicator field.
```

### Override path
Pattern E (mobile-only hover omission) in `gate-overrides.md`. Other
state-omissions require specific justification.

## Gate 4 — dark-explicit

### Check
If `color.dark.*` exists, every token in `color.semantic.*` has an
explicit entry under `color.dark.semantic.*`. No `auto-invert`, `auto-
darken`, or other derived-at-runtime values.

If `color.dark.*` does not exist (light-only product), this gate passes
trivially.

### Rationale
Auto-inversion produces unpredictable results across saturated accents,
breaks shadow-based elevation, and fails accessibility for critical colors.
See `act-3a-color-type.md § dark-mode`.

### Failure message

```
[FAIL] dark-explicit: color.semantic.state.warning has light value
       #C41E7A but no dark.semantic.state.warning entry.
       Declare the dark value explicitly (auto-invert may desaturate
       magenta to unusable).
```

### Override path
Rare. Only valid override: product is explicitly light-only and
`color.dark` removed entirely. No partial dark mode.

## Gate 5 — token-closure

### Check
Every `"{token.path}"` reference in `design.tokens.yaml` resolves to a
defined token. No raw hex, px, or numeric values in component definitions.

### Walk
1. Collect all token paths that are defined (LHS of assignments).
2. Find all `"{...}"` references in the file.
3. For each reference, path must be in the defined set.
4. Separately, scan `component.*.*.*` for raw values (hex / px / numbers
   that should be spacing/radius references).

### Never overrideable

A broken reference is always a bug. Either the token needs to be defined,
or the reference needs to be corrected. "Just trust it" is not a valid
state. `scripts/gate-check.py` rejects overrides on this gate.

### Failure message

```
[FAIL] token-closure: component.button.primary.default.bg references
       {color.accent.primary} but no such token is defined.
       Nearest defined: {color.semantic.accent.primary}.
```

## Gate 6 — affordance (v4.5)

### Check
For every interactive component's `default` state (Button, Input,
nav-item, list-row:interactive, form-row:editable):

- At least one of: `border` (any side), `bg` with ≥ 2% L* delta from
  parent surface, `text-decoration`, or `icon` slot filled, OR
- An explicit `label-always-visible: true` flag

### Rationale
Patricia sim surfaced that Dusk's underline-only Input risked invisibility
on Input-default. The affordance gate prevents "invisible interactive
surfaces".

### Failure message

```
[FAIL] affordance: component.input.default has no border, no bg fill
       delta from bg.canvas (both #121110), and no permanent label
       visibility. User cannot see this is an input field.
```

### Override path
Uncommon — typically fix by adding subtle fill. Override only if the
interactive element has a stronger affordance surface (e.g., surrounding
card makes it obvious). Requires Pattern-defined override with
`why-default-insufficient` naming the alternative affordance.

## Gate 7 — viewport-type (v4.5)

### Check
Render `sample-landing.html` and `sample-dashboard.html` at `layout.
primary-viewport.*` dimensions (headless measurement via a lint script,
or recorded user-visual confirmation).

- All typography scale values used in samples have computed pixel size ≥
  readability-floor for their role:
  - body ≥ 12 px at viewport
  - caption ≥ 10 px at viewport
  - button label ≥ 13 px at viewport
- If `layout.hidpi.strategy = integer-scale`, render additionally at 2×
  and 3× to verify pixel-boundary alignment

### Rationale
Dusk sim surfaced that 32 px display type read as "公告" on mobile — the
nominal size is not the perceived size. Mechanical check against
viewport-at-render ratio catches this.

### Failure message

```
[FAIL] viewport-type: typography.scale.display at 32px renders as 32px
       on 375×812 viewport. User visual feedback marked as "too small".
       Either bump scale OR change primary-viewport OR explicitly mark
       "display type for desktop only" + add a scale.mobile-display.
```

### Override path
Rare. Pattern: mobile-display scale + desktop-display scale as separate
tokens, with per-viewport usage mapping. Never override without actually
splitting.

## Output format

`scripts/gate-check.py` emits structured JSON:

```json
{
  "skill_version": "4.5",
  "bundle_timestamp": "<iso>",
  "gates": {
    "contrast":       {"status": "pass"},
    "neutral-scale":  {"status": "override", "tier": 5, "override_id": "ovr-1"},
    "triad-x-5state": {"status": "pass"},
    "dark-explicit":  {"status": "pass"},
    "token-closure":  {"status": "pass"},
    "affordance":     {"status": "pass"},
    "viewport-type":  {"status": "warn", "notes": "display bumped 32→40 after user feedback"}
  },
  "overrides": [
    {
      "id": "ovr-1",
      "gate": "neutral-scale",
      "status": "override",
      "reason": {
        "context-assumption": "...",
        "why-default-insufficient": "...",
        "upgrade-cost": "..."
      },
      "scope": ["color.neutral.*"],
      "enforce-elsewhere": true
    }
  ],
  "decision": "advance"     // or: "block"
}
```

`decision: advance` when every gate is `pass` or `override` (with complete
reason + scope) or `warn` (with recorded resolution). `decision: block`
when any gate is `fail` or an `override` lacks the structured reason.

The JSON goes verbatim into `upload-checklist.md` for the reviewer.
