# Gate Overrides

The five self-check gates (defined in `self-check-gates.md`) are not binary
pass/fail. Each has a third state: `override` with structured justification.
This file defines the override contract.

## Contents
- [Why overrides exist](#why-overrides-exist)
- [Override contract](#override-contract)
- [Soft-compliance library](#soft-compliance-library)
- [Forbidden override patterns](#forbidden-override-patterns)
- [Rendered override entries](#rendered-override-entries)

---

## Why overrides exist

Two failure modes without overrides:

1. **Gates fire blindly** — a cozy pixel game with a 5-color-palette lock
   cannot satisfy "9 neutral grays" and should not. Forcing the gate breaks
   the brand.
2. **Gates become advisory** — if users learn gates can be ignored freely,
   mechanical verification is worthless and we're back to prose-by-convention.

The override state threads this needle: the gate still fires, the system still
records the deviation, but the user must defend it in writing. The defense
goes into `upload-checklist.md` where reviewers and future-self can audit it.

---

## Override contract

Every override entry must have exactly these fields:

```yaml
gate: <string>                  # gate id, e.g., "contrast", "neutral-scale"
status: override                # literal
reason:
  context-assumption: <string>  # what's true in this project that the default
                                # assumed otherwise
  why-default-insufficient: <string>
                                # concrete way the default would break the work
  upgrade-cost: <string>        # what the override costs (risk, complexity,
                                # reviewer burden)
scope:                          # glob array; which tokens the override covers
  - "<pattern>"
  - "<pattern>"
enforce-elsewhere: <bool>       # does the default still hold outside scope?
                                # default true — overrides should be surgical
```

### The three reason fields

Freeform "reason" strings degrade to "client requirement" or "design
decision" within a week. The three-field format forces the writer to name:

- **context-assumption** — *what's different here*. E.g., "ICU night shift at
  3 a.m. with 12-hour fatigue, not office lighting"; "palette locked to
  Endesga-32 by brand identity, not a Tailwind default".
- **why-default-insufficient** — *how the default would break it*. E.g., "AA
  4.5:1 assumes office light + non-fatigued reader; this failure mode produces
  misread vitals"; "9 neutral grays would dilute the 32-color lock below 30%
  palette fidelity".
- **upgrade-cost** — *what we pay for the override*. E.g., "AAA 7:1 reduces
  accent color options in error states"; "5-gray scale means disabled state
  and loading state share a gray with only 8% luminance delta — operator must
  also rely on text differentiation".

All three fields are mandatory. Empty → override is rejected by
`scripts/gate-check.py`.

### Scope as glob array

```yaml
# good — surgical
scope:
  - "color.neutral.*"

# good — multiple patterns
scope:
  - "component.decoration.*"
  - "background.pattern.*"

# rejected — freeform string
scope: "decorative elements"

# rejected — wildcard without defense
scope:
  - "*"
# (a whole-system override needs its own gate, not a scope wildcard)
```

`enforce-elsewhere: true` (default) means gates still fire on tokens outside
the scope globs. Setting `false` requires a second override entry explaining
why the default is wrong system-wide, not just in scope.

---

## Soft-compliance library

Reusable override patterns that have defended themselves across projects.
When a user's case matches, pre-fill the reason fields from here rather than
from scratch.

### Pattern A: Split-layer neutral gray

**Matches**: user wants a collapsed semantic layer (3 grays) but the gate
needs ≥ 9 for state matrices to hold.

```yaml
gate: neutral-scale
status: override
reason:
  context-assumption: "brand doctrine keeps the visible palette collapsed"
  why-default-insufficient: "a flat collapse breaks state differentiation in
    Button × 5 states and Card × 3 states"
  upgrade-cost: "internal token file grows; semantic-layer consumers do not
    see the underlying 9 — but tooling must map correctly"
scope:
  - "color.semantic.*"
enforce-elsewhere: true
# companion file spec: neutral-base.yaml has 9 stops, semantic layer references
# 3 of them; state matrices reference base not semantic.
```

### Pattern B: Palette-lock priority

**Matches**: user has an external palette source (Endesga-32, PICO-8, custom
brand palette file) and refuses arbitrary hue expansion.

```yaml
gate: neutral-scale
status: override
reason:
  context-assumption: "palette is locked to <source> with <N> total colors;
    expanding beyond the source violates brand identity"
  why-default-insufficient: "9 neutral stops would require interpolating
    between palette entries, producing off-palette hex values"
  upgrade-cost: "state matrices must tolerate fewer stops (see tier: 5 or 7);
    disabled/loading must differentiate via opacity or pattern, not hue"
scope:
  - "color.neutral.*"
enforce-elsewhere: true
```

### Pattern C: Decorative-tier contrast freedom

**Matches**: user wants decorative sprite / pattern layers to have low
contrast intentionally (depth, texture) while keeping text at AAA.

```yaml
gate: contrast
status: override
reason:
  context-assumption: "decorative sprites do not carry information; they
    create spatial depth by receding into background luminance"
  why-default-insufficient: "enforcing 4.5:1 on decoration forces every
    background sprite to foreground-grade contrast, destroying layered depth"
  upgrade-cost: "accessibility audits must be primed that contrast enforcement
    is tiered — text: AAA, UI: AA, decoration: free"
scope:
  - "component.decoration.*"
  - "background.pattern.*"
enforce-elsewhere: true
# companion: contrast.tier in tokens file defines AAA for text.*, AA for ui.*,
# free for decoration.*
```

### Pattern D: AAA upgrade for safety-critical reads

**Matches**: user explicitly needs > AA contrast (medical, aviation, industrial
control, accessibility-first products).

```yaml
gate: contrast
status: override
reason:
  context-assumption: "reads happen under fatigue / low-light / consequence-
    of-misread, not office conditions"
  why-default-insufficient: "AA's 4.5:1 margin of safety was calibrated for
    office lighting and non-fatigued readers; both assumptions fail here"
  upgrade-cost: "accent palette shrinks — some brand accents at 4.5:1 fail
    AAA; brand team must concede accent purity in body text, retain it in
    hero/display type"
scope:
  - "text.*"
  - "component.form-row.*"
  - "component.critical.*"
enforce-elsewhere: false   # non-text can stay at 3:1 for icon/shape contrast
```

### Pattern E: Mobile-only hover omission

**Matches**: mobile-primary app, hover state has no physical trigger.

```yaml
gate: triad-x-5state
status: override
reason:
  context-assumption: "primary surface is mobile; touch has no hover"
  why-default-insufficient: "defining hover would either duplicate default or
    mislead implementers into shipping desktop-only fallback"
  upgrade-cost: "when a desktop breakpoint is added later, hover must be
    designed then, not assumed"
scope:
  - "component.*.state.hover"
enforce-elsewhere: true
```

Add new patterns here when a novel defense is accepted. Each pattern should
have been used successfully in at least one real intake before being added.

---

## Forbidden override patterns

Reject these at `scripts/gate-check.py` level, not by conversation.

### F1. Freeform reason string
```yaml
reason: "client requirement"   # rejected
reason: "audit said so"        # rejected
```
Must be the three-field structure.

### F2. Scope wildcard without companion
```yaml
scope:
  - "*"
# rejected unless a second, more specific override justifies the global
# scope as a deliberate system-wide decision.
```

### F3. Override stacking
An override on gate A cannot be used to justify an override on gate B. Each
override defends itself. If gates conflict (e.g., contrast AAA forces
palette expansion that breaks palette-lock), that conflict is itself a new
design decision needing a merged override with merged reasons, not two
separately-justified ones.

### F4. Override on `token-closure`
`token-closure` (every component reference resolves to a defined token) is
not overridable. A broken closure is always a bug. If tokens do not exist,
add them; do not excuse their absence.

---

## Rendered override entries

`scripts/gate-check.py` emits override entries into the upload checklist in
this shape:

```markdown
## Gate Overrides

### contrast → override (scope: text.*, component.critical.*)

**Context assumption.** Reads happen under fatigue and low-light, not office.

**Why AA insufficient.** Misread vitals have consequence-of-misread risk;
AA's margin assumes non-critical reads.

**Upgrade cost.** Brand accents that barely cleared AA fail AAA in body type
and must be re-scoped to display type only.

**Default still enforced outside scope.** No (non-text remains at 3:1).

---
```

This format goes verbatim into `upload-checklist.md` for the reviewer.
