# Material Extensions

Schema for material tokens beyond basic fill color: noise, chrome, liquid,
matte, gloss, pixel, scanline, dither, and composite multi-layer stacks.
All material entries must reference palette tokens (not raw hex) to avoid
breaking palette-lock positive constraints.

## Contents
- [Why material is separate](#why-material-is-separate)
- [Single-layer types](#single-layer-types)
- [Composite layering (Tier 1 v4.5)](#composite-layering-tier-1-v45)
- [Schema-projection for materials](#schema-projection-for-materials)
- [Fallback recipes](#fallback-recipes)
- [Material × palette-lock binding](#material--palette-lock-binding)

## Why material is separate

Claude Design's color palette schema captures flat fills. Anything beyond
flat — gradients, noise overlays, scanlines, dithering, liquid metal —
needs extra fields. The `material.*` block is where those live.

Every material field is `drop-silent` under schema projection by default.
Fallback recipes (below) make the intent survive the drop.

## Single-layer types

### noise
Subtle texture, typically via SVG `feTurbulence`:

```yaml
material.noise:
  opacity: 0.02
  base-frequency: 0.9
  octaves: 2
  blend-mode: overlay
  applied-to: ["{color.bg.*}"]    # surfaces that get the overlay
```

Rendered as inline `<svg>` with filter + a `::before` pseudo-element.

### chrome
Metallic / mirrored surfaces. Typically conic-gradient approximation:

```yaml
material.chrome:
  type: conic-gradient
  colors:
    - "{color.chrome.100}"
    - "{color.chrome.400}"
    - "{color.chrome.700}"
    - "{color.chrome.100}"
  rotation-cycle: 8000ms
  animated: true
```

For a truly liquid-metal effect, see `liquid` (WebGL fallback).

### liquid
Shader-based liquid metal. CSS cannot render natively:

```yaml
material.liquid:
  type: shader-fallback
  shader-source: "external .glsl or framework config"
  fallback:
    type: conic-gradient
    colors: ["{color.chrome.100}", "{color.chrome.700}"]
    animation: "rotate 8s linear infinite"
  capability-boundary: true          # mark for capability-boundaries.md
```

The skill cannot produce shader source. Record the fallback and declare
capability boundary.

### matte
Explicit "no sheen" declaration. Useful as positive constraint when
brand forbids all material finish:

```yaml
material.matte:
  render: flat
  forbids: [gloss, chrome, liquid, noise]
```

### gloss
Subtle sheen / highlight:

```yaml
material.gloss:
  highlight-color: "{color.white.alpha-10}"
  highlight-position: "top"
  blur: 12
  forbidden-in-dark: true          # gloss rarely works on dark; record
```

### pixel (v4 addition)
Pixel-perfect rendering:

```yaml
material.pixel:
  grid: 8                   # px
  anti-aliasing: false
  render: pixelated         # CSS image-rendering
  sub-pixel: forbidden
```

### scanline (v4 addition)
Horizontal dark lines for CRT / retro aesthetic:

```yaml
material.scanline:
  interval: 2               # px between lines
  opacity: 0.08
  color: "#000"
  direction: horizontal     # horizontal | vertical
```

### dither (v4 addition)
Bayer dithering replaces smooth gradients:

```yaml
material.dither:
  pattern: bayer-4x4        # bayer-2x2 | bayer-4x4 | bayer-8x8 | floyd-steinberg
  density: 0.15
  colors:
    - "{color.bg.base}"
    - "{color.bg.raised}"
```

## Composite layering (Tier 1 v4.5)

Multi-layer material stacks are first-class. BENTO's hero background
(base + dither + scanline + sprite) looks like this:

```yaml
material.composite:
  bg-textured:
    layers:
      - index: 0
        type: solid
        color: "{color.bg.base}"
      - index: 1
        type: dither
        pattern: bayer-4x4
        density: 0.15
        colors:
          - "{color.bg.base}"
          - "{color.bg.raised}"
        blend-mode: normal
      - index: 2
        type: scanline
        interval: 2
        opacity: 0.08
        color: "#000"
        blend-mode: multiply
      - index: 3
        type: pixel-sprite
        asset: "assets/sprites/bento-hero.svg"
        grid: 8
        anti-aliasing: false
    render-order: "0 → 1 → 2 → 3"
    applied-to: ["{layout.page.landing.hero}"]
```

### Composite rules

- `layers[]` array; each layer has unique `index` that defines z-order
- `render-order` string documents stacking for readers
- Each layer's colors reference palette tokens
- `blend-mode` is explicit (CSS mix-blend-mode or manual layer stacking)
- `applied-to` is a glob array of regions the composite paints

### Why schema this instead of free YAML

Patricia sim and KAI sim both show users inventing `material.stack[]`,
`material.layers[]`, `material.composed`, `material.group[]` — all the
same concept under different keys. Without standardization, bundles from
different intakes aren't comparable, and `scripts/token-lint.py` cannot
validate layer integrity.

## Schema-projection for materials

| Material | Projection tag | Notes |
|---|---|---|
| `noise` (single) | `eaten` (as metadata; effective rendering requires SVG filter at component level) | recipe: SVG filter |
| `chrome` (single, conic-gradient) | `eaten` (gradient lands as-is) | — |
| `liquid` | `drop-silent` (shader-based) | fallback to conic-gradient recipe |
| `matte` (declaration) | `drop-silent` (prose, not value) | record as positive constraint `material-policy: matte-only` |
| `gloss` | `drop-silent` (as concept; gradient lands if translated to conic) | recipe: document + translate to gradient token |
| `pixel` | `drop-silent` | recipe: CSS `image-rendering: pixelated` documented in design.md |
| `scanline` | `drop-silent` | recipe: CSS `repeating-linear-gradient` documented |
| `dither` | `drop-silent` | recipe: SVG filter or CSS dither pattern |
| `composite` (any) | `drop-silent` | recipe: preserve in tokens, document layer assembly in design.md + sample HTML |

The projection report enumerates each declared material and tags
accordingly. See `schema-projection.md § report-format`.

## Fallback recipes

Every drop-silent material must have a concrete fallback recipe in one of
four forms (see `schema-projection.md § the-five-projection-tags`):

### Recipe 1 — CSS translation

Examples:
- scanline → `background: repeating-linear-gradient(0deg, transparent
  0 1px, rgba(0,0,0,0.08) 1px 2px);`
- dither → SVG `<feTurbulence baseFrequency="0.9">` filter + opacity
- pixel → `image-rendering: pixelated; -webkit-font-smoothing: none;`

Recipe lives in:
- `design.tokens.yaml material.*.css-recipe` (embedded string)
- `design.md § material` (human-readable explanation)
- Sample HTML (demonstrates rendered output)

### Recipe 2 — External asset reference

- liquid → reference to `.glsl` or framework-motion config
- chrome (with true metal highlight) → reference to image asset

```yaml
material.liquid:
  external-asset:
    path: "assets/shaders/liquid-chrome.glsl"
    integration: "shader-gradient.com or equivalent"
    capability-boundary: true
```

### Recipe 3 — Post-upload manual step

When Claude Design drops the material entirely and no CSS fallback is
viable:

```yaml
material.composite.bg-textured:
  post-upload-manual:
    step: "after Claude Design publishes, reassemble at component-layer
           by applying the layer stack via CSS pseudo-elements"
    instruction-file: "upload-checklist.md § post-upload-manual"
```

### Recipe 4 — Downgrade to positive constraint

For material declarations that are really taboos in disguise:

```yaml
material.matte:
  downgrade-to-positive-constraint:
    id: "material-policy-matte-only"
    rule: "no gloss / chrome / liquid / noise anywhere"
    scope: ["material.*"]
    enforcement: "token-lint.py --positive material-policy-matte-only"
```

## Material × palette-lock binding

If the project has a palette-lock positive constraint (e.g., Endesga-32),
every material layer's color fields must reference palette tokens, never
raw hex.

### Enforcement

```yaml
# good — dither references palette tokens
material.dither:
  colors:
    - "{color.bg.base}"
    - "{color.bg.raised}"

# rejected by scripts/token-lint.py
material.dither:
  colors:
    - "#1a1932"
    - "#262b44"
```

Even if `#1a1932` is the exact hex of `color.bg.base`, the raw form breaks
palette-lock enforcement — a later palette update would not propagate.

### Lint rule

`scripts/token-lint.py --positive palette-lock` walks all `material.*.
color*` fields and fails on any raw hex. The check is mandatory when a
palette-lock constraint is declared.

## When to declare material

Not every project needs `material.*`. Dusk has `shadow.policy: forbidden`
and `material: {}` — perfectly valid. Patricia's VitalBoard has
`material.matte.render: flat` as a positive declaration against texture.

Declare material only when:
- The brand positively specifies a finish (noise, gloss, chrome, pixel,
  scanline, dither)
- The brand explicitly forbids finish as a policy (record as matte +
  positive constraint)
- A specific region has a multi-layer composite need

Skipping material entirely is the default; it's not a gate failure.
