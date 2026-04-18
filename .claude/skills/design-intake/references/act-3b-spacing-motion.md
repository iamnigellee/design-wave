# Act ③b — Spacing, Radius, Motion, Material

Second half of the visual-token translation. Spacing rhythm, radius scale,
motion (with typed timing functions — Tier 1 change), border / shadow, and
material layers (noise / chrome / liquid / matte / gloss / pixel / scanline /
dither / composite).

3–4 minutes.

## Contents
- [Spacing scale](#spacing-scale)
- [Radius](#radius)
- [Border](#border)
- [Shadow / elevation](#shadow--elevation)
- [Motion — typed timing functions](#motion--typed-timing-functions)
- [Material — single and composite](#material--single-and-composite)
- [Focus ring](#focus-ring)
- [Z-index](#z-index)
- [Exit conditions](#exit-conditions)

## Spacing scale

### Rule — explicit array, never a formula

```yaml
# good
spacing: [0, 2, 4, 8, 12, 16, 24, 32, 48, 64, 96]

# rejected
spacing: "multiples of 8"
```

Formulas invite invention (AI fills 7, 15, 31). The explicit array is the
only thing `scripts/token-lint.py` can check against.

### Defaults by density

- **Low-density** (chat / reader apps) — `[0, 4, 8, 16, 24, 32, 48, 64]`
- **Default** — `[0, 2, 4, 8, 12, 16, 24, 32, 48, 64, 96]`
- **High-density** (dashboards, data grids) — `[0, 2, 4, 8, 12, 16, 20, 24,
   32, 40, 48, 64]`
- **Grid-locked** (pixel / retro) — `[0, 8, 16, 24, 32, 40, 48, 56, 64]`
  (positive constraint: multiples of 8 enforced)

### Ask

> 默认值 <array>。你的产品有没有硬网格约束（像素/8px倍数/4px倍数）？

If yes, record as positive constraint `grid-<N>` (see
`schema-projection.md §positive-constraints`).

## Radius

### Rule — global default + named exceptions

```yaml
radius:
  default: 4        # applied to all components unless overridden
  sharp: 0
  sm: 2
  md: 4
  lg: 8
  xl: 16
  full: 9999        # pill
  # explicit per-component exceptions
  cta: 24           # e.g., ACIDLAB: global 0 but CTA 24
```

### Single-point disruption

Some brands use one radius as a visual weapon (global 0, one component 24px).
Record this as an explicit named exception rather than proliferating the
scale.

### Restraint brands

Dusk-class brands cap at 2px or 4px. Record as constraint:
> radius-cap: 4 (larger values forbidden)

Downstream: `scripts/token-lint.py` rejects any radius > cap unless a named
exception is registered.

## Border

```yaml
border:
  width:
    hairline: 1
    base: 2
    thick: 4
  style: solid    # or: dashed, dotted — record positive constraint if
                  # alternatives are brand-load-bearing
  default-color: "{color.semantic.border.subtle}"
```

Dashed / dotted borders are drop-warn under Claude Design's schema (style
drops; width/color land). Recipe: document voice in `design.md § borders`
and apply at component level.

## Shadow / elevation

### Three common approaches

1. **Full shadow scale** (default) — 6 tokens `sm / base / md / lg / xl / 2xl`
   with explicit CSS values.
2. **No shadow** (Dusk, BENTO, VitalBoard) — elevation communicated by 1px
   border + 2-5% luminance step between surfaces. Record as:
   ```yaml
   shadow:
     policy: forbidden
     rationale: "elevation via border + luminance step, not blur"
   ```
   This is a taboo (see `act-2-anchors.md § taboos`).
3. **Chrome / glow / inset** (ACIDLAB) — non-standard shadow as texture.
   Record in `material.shadow.*` per token (below).

### Dark-mode shadow rewrite

Box-shadows on dark backgrounds barely render. For dark-primary brands:
- Either forbid shadow entirely and use border + luminance step
- Or define `shadow.dark.*` explicitly as `inset` or heavy-blur variants
- Never `auto`

## Motion — typed timing functions

### Tier 1 change (v4.5)

The `timing.fn` field is typed, not a string. The type distinguishes:

```yaml
motion:
  duration:
    instant: 0
    fast: 120
    base: 200
    slow: 400
    dramatic: 800
  timing-fn:
    standard:
      type: bezier
      value: "cubic-bezier(0.32, 0.72, 0.24, 1)"
    step-in:
      type: steps
      count: 4
      jump: end          # one of: start | end | both | none
    spring-subtle:
      type: spring
      stiffness: 180
      damping: 24
  usage:
    enter: {duration: base, fn: standard}
    exit: {duration: fast, fn: standard}
    hover: {duration: fast, fn: standard}
    state-change: {duration: base, fn: standard}
```

### Why typed

Claude Design's motion schema only enumerates `bezier` easings. `steps()` and
spring physics are `drop-silent` under projection.

Typed timing-fn lets:
- `scripts/token-lint.py` validate that `type: steps` carries `count` and
  `jump`, not arbitrary params
- `schema-projection.md` report know exactly which timing-fn values drop
- Fallback recipes be type-specific (steps → string-encoded easing;
  spring → CSS custom-property with JS interpolation or framework-motion
  config)

### Aesthetic defaults

- **Restrained** (Dusk) — one `bezier` easing only, duration slow.
- **Expressive** (ACIDLAB) — `bezier` + a `spring` for hero, dramatic
  duration for intro animations.
- **Retro / pixel** (BENTO) — `steps` only, all others forbidden as a
  positive constraint `motion-stepped-only`.
- **Safety-critical** (VitalBoard) — `duration.max: 200ms`, `reduced-motion:
  respected`, no animation on critical alerts (taboo from Act ②).

### Reduced motion

Always define:

```yaml
motion:
  reduced-motion:
    strategy: reduce   # or: remove
    duration-override: 0
```

`reduce` keeps easing but flattens duration; `remove` strips transitions
entirely. Medical / vestibular-sensitivity projects usually pick `remove`.

## Material — single and composite

### Single-layer (v4 baseline)

```yaml
material:
  noise: {opacity: 0.02, baseFrequency: 0.9, octaves: 2}
  chrome: {type: conic, colors: [...], rotation: 8s}
  liquid: {type: shader-fallback, fallback: conic-gradient}
  matte: {render: flat}
  gloss: {render: subtle-sheen}
  pixel: {grid: 8, aa: false, render: pixelated}
  scanline: {interval: 2, opacity: 0.08}
  dither: {pattern: bayer-4x4, density: 0.15}
```

### Composite — Tier 1 change (v4.5)

Multi-layer stacks get first-class schema:

```yaml
material:
  composite:
    bg-textured:
      layers:
        - type: solid
          color: "{color.bg.base}"
        - type: dither
          pattern: bayer-4x4
          density: 0.15
          colors: ["{color.bg.base}", "{color.bg.raised}"]
        - type: scanline
          interval: 2
          opacity: 0.08
          color: "#000"
      render-order: "0 → 1 → 2"
```

Every composite is `drop-silent` under projection. Recipe: preserve in
tokens; `design.md § material` describes layer intent and CSS assembly;
sample HTML demonstrates rendering. Mark in `upload-checklist.md` as
"post-upload component-layer assembly required".

### Material palette-lock binding

If the project has a palette-lock positive constraint (e.g., Endesga-32),
material layers must reference palette tokens, not raw hex:

```yaml
# good
dither: {colors: ["{color.bg.base}", "{color.bg.raised}"]}

# rejected by token-lint (breaks palette-lock)
dither: {colors: ["#1a1932", "#262b44"]}
```

## Focus ring

Single most-forgotten token. Always explicit:

```yaml
focus-ring:
  width: 2
  style: solid
  color: "{color.semantic.accent.primary}"
  offset: 2
  outer-glow:
    color: "{color.semantic.accent.primary}"
    alpha: 0.3
    blur: 4
```

For safety-critical projects, offset + width must be enforceable as gate
check (focus not discoverable by color alone → must have offset).

For brutalist / pixel projects, focus ring often uses a non-standard color
(chrome silver for ACIDLAB; single pixel row for BENTO). Record the choice
explicitly.

## Z-index

```yaml
z-index:
  base: 0
  dropdown: 10
  sticky: 20
  overlay: 30
  modal: 40
  toast: 50
  tooltip: 60
```

Never use arbitrary large values (`9999`). Token-lint rejects them.

## Exit conditions

Before advancing to Act ④:

- `spacing` — explicit array
- `radius` — default + named set; exceptions registered
- `border` — width + style + default-color
- `shadow` — scale OR explicit "forbidden" policy with rationale
- `motion.duration.*` + `motion.timing-fn.*` (typed) + `motion.usage.*`
- `motion.reduced-motion.*`
- `material.*` — single-layer entries; `composite.*` when needed
- `focus-ring` — all five fields
- `z-index` — named layers, no arbitrary values
- positive constraints accumulated this act (grid, motion-stepped, radius-
  cap, palette-material-binding) logged to `positive_constraints` block

Readback:
```
节奏 : spacing=<array>, radius=<default>/<cap>, shadow=<policy>
动效 : duration.<fast>-<dramatic>, fn.type=<bezier|steps|spring>, reduced=<>
质感 : <single layers used>, composite=<stacks if any>
Focus: <ring spec>
约束 : positive=[<list>]

→ 进入 Act ④ 元件矩阵。继续？
```
