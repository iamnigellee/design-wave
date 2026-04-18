# Act ④b — Layout Tokens

Define the base layout (grid, breakpoints, container) plus per-page overrides.
Tier 1 change (v4.5): per-page layout uses a **base + delta** pattern, not
independent namespaces, to avoid the namespace-explosion Patricia flagged
(20+ pages × full layout = 20 disconnected configs).

1–2 minutes.

## Contents
- [Base layout](#base-layout)
- [Breakpoints](#breakpoints)
- [Container](#container)
- [Grid mode](#grid-mode)
- [Per-page overrides](#per-page-overrides)
- [Logical properties for RTL](#logical-properties-for-rtl)
- [Exit conditions](#exit-conditions)

## Base layout

One base applies to all pages by default. Per-page overrides declare deltas
only.

```yaml
layout:
  base:
    container:
      max-width: 1280
      padding-x: {mobile: 16, tablet: 24, desktop: 32}
    grid:
      columns: 12
      gap: 24
      row-gap: 24
    density: default              # default | dense | sparse
    logical: false                # true → use inline-start/block-end
```

## Breakpoints

```yaml
layout.breakpoints:
  sm: 640
  md: 768
  lg: 1024
  xl: 1280
  2xl: 1536
```

Values explicit in px. Never "mobile-first responsive" as a description.
Variable names track Tailwind defaults; overriding the names is fine if the
brand uses different scales, but record as positive constraint so downstream
code knows.

### Primary viewport

Record which viewport defines the product:

```yaml
layout.primary-viewport:
  width: 375       # iPhone SE / 13 mini class
  height: 812
  device-pixel-ratio: 2      # for pixel-perfect aesthetics; see HiDPI below
  posture: portrait-single-hand   # one of: portrait / landscape / split /
                                   # portrait-single-hand / hospital-cart
```

Downstream: Act ⑤ samples render at this viewport first. For products with
truly desktop-first usage (dashboards consumed at 1920+), declare it and
adjust samples accordingly.

### HiDPI

For pixel-aesthetic or bitmap-font projects (BENTO), declare explicit
integer-scale strategy:

```yaml
layout.hidpi:
  strategy: integer-scale          # integer-scale | browser-default | snap-to-grid
  base-unit: 8
  scale@2x: 2
  scale@3x: 3
  image-rendering: pixelated
  font-smoothing: none
```

This block is `drop-silent` under schema projection. Fallback recipe: CSS
custom-properties + media queries that force integer scaling, documented in
sample HTML.

## Container

### Options
- **Fluid** — no max-width; content fills viewport
- **Fixed-max** — clamped at `container.max-width`
- **Full-bleed** — per section, 100vw with internal padding only

```yaml
layout.container:
  mode: fixed-max             # fluid | fixed-max | full-bleed-per-section
  max-width: 1280
  padding-x: {...}
```

Record the choice explicitly. "Mobile responsive" is not a choice — it's
three independent choices (what are the breakpoints, what's the container
mode, what's the grid).

## Grid mode

### Default
Standard 12-column responsive grid, equal gutters.

### Alternatives
- **Broken grid** — cells intentionally overflow or misalign (ACIDLAB's
  Dashboard). Requires `overflow: visible` + negative margins permitted.
- **Full-bleed stack** — single-column vertical, 100vw sections (ACIDLAB's
  Landing).
- **Diagonal / rotated** — section-level rotation transforms (rare).

```yaml
layout.grid:
  mode: standard-12             # standard-12 | broken-12 | full-bleed-stack |
                                # diagonal-N-degrees
  overflow-allowed: false
  negative-margin-allowed: false
```

Non-standard grids drop under schema projection; fallback is CSS spec in
`design.md § layout` and sample HTML demonstration.

## Per-page overrides

### Base + delta pattern

Base layout applies everywhere. Named pages declare deltas only:

```yaml
layout.page:
  landing:
    grid.mode: full-bleed-stack          # override from base
    container.mode: full-bleed-per-section
    rationale: "hero impact over information density"
  dashboard:
    grid.mode: broken-12                  # override
    grid.overflow-allowed: true
    density: dense
    rationale: "multi-surface data density; broken grid adds rhythm"
  patient-detail:
    density: default
    grid.columns: 8                       # narrower for focus
    rationale: "single-patient deep read; avoid distraction"
  settings:
    container.max-width: 800
    density: sparse
    rationale: "configuration, not consumption"
```

### Why base + delta, not independent namespaces

Patricia sim exposed that a 20-page product would produce 20 disconnected
full-layout configs. Deltas compress duplication and make it obvious which
pages deviate from base.

### When deltas conflict

If two pages need to override the same field with different values
(dashboard wants `dense`, settings wants `sparse`), the per-page delta wins.
If three+ pages need identical deltas against base, consider whether the
base itself should change — five dashboards all overriding to `dense`
probably means the product's default density should be `dense`.

### Auto-promotion rule

When `scripts/token-lint.py` detects ≥ 3 pages with identical delta, it
reports:
> Suggestion: delta `density: dense` repeats on 3+ pages. Consider
> promoting to `layout.base.density`.

## Logical properties for RTL

### When to enable

Enable `layout.base.logical: true` when the product ships in RTL locales
(Arabic, Hebrew, Persian, Urdu).

### Effect

All spacing / padding / margin tokens in layout contexts use CSS logical
properties:

- `padding-left` → `padding-inline-start`
- `margin-right` → `margin-inline-end`
- `border-top` → `border-block-start`

### Schema projection

`drop-silent`. Claude Design's schema currently uses directional properties.
Fallback recipe: record in `design.md § internationalization`; apply at
component implementation level via CSS logical properties, tokens store
the unit value only.

### Number direction override

Even in RTL, numbers stay LTR:

```yaml
layout.rtl:
  number-direction: ltr   # "140/90 mmHg" reads left-to-right in any locale
```

## Exit conditions

Before advancing to Act ⑤:

- `layout.base.*` all fields declared
- `layout.breakpoints` explicit px
- `layout.primary-viewport` declared (width + posture minimum)
- `layout.hidpi` if pixel aesthetic (BENTO-class)
- `layout.container.mode` named
- `layout.grid.mode` named
- `layout.page.*` deltas for ≥ 2 pages (typically landing + one internal)
- `layout.base.logical` + `layout.rtl` if multi-locale

Readback:
```
Base     : container=<mode>, max=<>, grid=<columns>×<gap>, density=<>
Viewport : primary=<w>×<h> @<dpr>x, posture=<>
HiDPI    : <strategy> (if applicable)
Pages    : <N> page deltas registered
RTL      : logical=<yes|no>

→ Act ⑤ 预览 + 共识 + 闸门。继续？
```
