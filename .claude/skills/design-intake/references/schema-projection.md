# Schema Projection

Before Act ⑤ emits artifacts, the skill produces a schema projection report
telling the user which parts of the bundle Claude Design will actually ingest
and which parts it will silently drop, error on, or partially accept. Every
drop must have a fallback recipe.

Positive constraints — rules the user supplies beyond Claude Design's schema,
like "≤32 colors locked to Endesga-32" — live on their own axis and are not
drop states.

## Contents
- [What Claude Design ingests](#what-claude-design-ingests)
- [The five projection tags](#the-five-projection-tags)
- [Positive constraints — separate axis](#positive-constraints--separate-axis)
- [Fallback-recipe catalog](#fallback-recipe-catalog)
- [Report format](#report-format)
- [Regression watch](#regression-watch)

---

## What Claude Design ingests

Per the official onboarding docs (`claude-design-upload.md`), the ingestion
engine extracts exactly four categories and discards the rest:

| Official | Covers | Commonly drops |
|---|---|---|
| 色彩調色板 | palette stops, semantic names, dark pairs | HSL-component form, per-tenant overrides, texture/material modifiers |
| 排版 | font families, sizes, weights, line-heights | tabular-nums, feature-settings, bitmap-font fallback strategies, language-specific variants |
| 元件 | Button / Input / Card and common variants | nav-item custom indicators, form-row separator styles, composite components, multi-slot anatomy |
| 版面配置模式 | grid, spacing rhythm, breakpoints | per-page layout namespaces, `logical` properties (inline-start), broken-grid / rotated-layout overrides |

Anything outside these four either drops silently, drops with a warning, or
passes through only if its shape happens to match an enum value. The
projection report classifies every output field into one of the five tags
below.

---

## The five projection tags

### ✅ `eaten`
The field matches Claude Design's expected schema shape and values.
Post-upload, the design system panel will show this field correctly.

### ⚠️ `drop-silent`
The field is syntactically valid (not an error), but Claude Design does not
have a slot for it. It disappears from the generated design system without
warning. Most dangerous tag because users assume silence means acceptance.

**Examples**: custom `material.composite`, `contrast.tier` layers,
`extensions.multi-tenant`, `motion.timing.fn.type=steps`, `typography.
number-style=tabular`, per-page `layout.page.*` namespaces, anti-reference
tier level "copy", `brand.soul.adjectives.negative-axis`.

### 🔥 `drop-error`
The field's shape would cause the ingestion pipeline to reject the artifact.
Must be rewritten before upload.

**Examples**: malformed YAML, circular token references, a hex value that
isn't 6 or 8 hex chars, a font-family with no fallback at all, a color token
pointing to a non-existent referent.

### ⚡ `drop-warn`
The field partially ingests — the primary value lands, but attached metadata
drops. Upload will complete but the generated system is incomplete.

**Examples**: color tokens with extra metadata fields beyond hex/hsl, type
scale entries with letter-spacing but no line-height, component variants with
states the schema does not enumerate.

### 🔧 `fallback-recipe`
Every `drop-silent` and `drop-warn` must be paired with a fallback recipe
stating one of:

1. *Translate to positive constraint* — e.g., "禁用 shadow" (negative) becomes
   `shadow: none` on every component state token (positive, ingestible).
2. *Preserve in `design.md` prose* — the field lives in the human-readable
   doc; team enforces it manually.
3. *External asset* — the field becomes a separate file (e.g.,
   `tenant-overlay.example.yaml`) uploaded alongside the main bundle.
4. *Post-upload manual step* — a checklist item in `upload-checklist.md`
   telling the team what to do after Claude Design generates.

Recipe must be concrete, not aspirational. "Document for later" is not a
recipe.

### Three-state drop clarity

Users conflate "dropped" with "rejected" (see Patricia sim, Act ⑤). The
three drop tags are deliberately distinct:

- `drop-silent` — upload succeeds, field vanishes, no signal
- `drop-warn` — upload succeeds, field partially lands, warning in logs
- `drop-error` — upload fails; must fix

When narrating to the user, always state which drop tag applies, never just
"dropped".

---

## Positive constraints — separate axis

Positive constraints are rules *the user adds* to restrict the design space,
not rules the schema imposes. They are orthogonal to projection tags.

### Examples
- "≤32 colors locked to Endesga-32"
- "8px grid, integer multiples only"
- "global radius = 0 except CTA = 24px"
- "weights used: only 400 and 500 (no 700)"
- "tenant-override allowed only on brand.primary and brand.logo"

### Why separate

If positive constraints use the same projection tags, the semantics collapse:
"Endesga-32 lock" is neither "eaten" (schema doesn't enforce it) nor
"drop-silent" (it's a rule for the team, not a field Claude Design would
ingest). It is a *policy*, not a *value*.

### Storage
Positive constraints live in `design.tokens.yaml` under a top-level
`positive_constraints` block and in `design.md` as a dedicated section. The
upload checklist contains a paragraph enforcing them manually.

### Shape

```yaml
positive_constraints:
  - id: palette-lock
    rule: "all color tokens must be a subset of Endesga-32"
    source: "https://lospec.com/palette-list/endesga-32"
    scope: ["color.*"]
    enforcement: "scripts/token-lint.py --positive palette-lock"

  - id: grid-8
    rule: "all spacing, component dimensions, and positions are integer
           multiples of 8px"
    scope: ["spacing.*", "layout.*", "component.*.size", "component.*.pos"]
    enforcement: "scripts/token-lint.py --positive grid-8"

  - id: tenant-overlay-whitelist
    rule: "tenants may only override brand.primary and brand.logo; semantic
           colors are locked"
    scope: ["brand.primary", "brand.logo"]
    enforcement: "manual review; see design.md §multi-tenant"
```

`scripts/token-lint.py` runs every positive constraint's `enforcement` and
fails the bundle if any lint fails. Unlike gate overrides, positive constraints
are not overrideable within a single run — changing them means the user
rewrites the rule.

---

## Fallback-recipe catalog

Common drops and their canonical recipes. Use these before inventing new ones.

### material.composite (multi-layer surfaces)

- **Drop tag**: `drop-silent`
- **Why**: Claude Design ingests single-material surfaces; layered stacks
  (noise + scanline + dither) have no schema slot.
- **Recipe**:
  1. Keep `material.composite` block in `design.tokens.yaml` for the team.
  2. In `design.md`, write a "Material Composition" section describing each
     layer with render order and concrete CSS/SVG snippets.
  3. In `upload-checklist.md`, mark composite surfaces as "component-layer
     reassembly required post-upload".

### motion.timing.fn = steps(n, jump-*)

- **Drop tag**: `drop-silent` (schema enum excludes `steps`)
- **Recipe**:
  1. Store as string in the tokens file.
  2. Add positive constraint: "motion uses stepped timing only; bezier and
     ease-* are forbidden".
  3. In `design.md`, state the aesthetic reason (pixel / retro / game) so
     downstream generation doesn't "correct" to a bezier.

### contrast.tier (layered contrast enforcement)

- **Drop tag**: `drop-silent`
- **Recipe**:
  1. Gate override on `contrast` with scope restricted to
     `component.decoration.*`.
  2. `design.md` section naming text / UI / decoration tiers with concrete
     ratios per tier.
  3. Token file: group tokens by `contrast.tier` annotation.

### multi-tenant theming

- **Drop tag**: `drop-silent`
- **Recipe**:
  1. Emit `tenant-overlay.example.yaml` as a separate file (not part of main
     `design.tokens.yaml`).
  2. `design.md` section listing `overridable` vs `locked` tokens, with the
     safety rationale for each lock.
  3. `upload-checklist.md` step: "after Claude Design publishes, verify that
     tenant-specific forks do not touch `locked` tokens".

### per-page layout namespaces

- **Drop tag**: `drop-silent`
- **Recipe**:
  1. Single `layout.base` block that Claude Design ingests.
  2. `layout.page.<name>` overrides as deltas against base.
  3. `design.md` describes per-page density rationale; implementation layer
     applies overrides at route boundaries.

### anti-reference tier "copy"

- **Drop tag**: `drop-silent` (schema has no voice/tone surface)
- **Recipe**:
  1. Move copy-tier anti-references into a `voice-and-tone` section in
     `design.md`.
  2. Treat as documentation for human writers, not a design-generation input.

### HiDPI / devicePixelRatio strategies

- **Drop tag**: `drop-silent` (not in v4.5 schema)
- **Recipe**:
  1. Store in `design.tokens.yaml` under `hidpi:` block.
  2. `design.md` describes integer-scale strategy + `image-rendering:
     pixelated` + `font-smoothing: none` for pixel-aesthetic projects.
  3. Sample HTML demonstrates the CSS transforms.

### typography.number-style = tabular

- **Drop tag**: `drop-warn` (font-family lands, feature flag drops)
- **Recipe**:
  1. Keep `number-style: tabular` in tokens.
  2. `design.md` states: "vital signs / financial / tabular reads require
     `font-feature-settings: 'tnum'` applied at component level".
  3. Components for numeric displays reference this CSS in their implementation
     spec.

---

## Report format

Every bundle includes a `schema_projection_report` block in
`upload-checklist.md`:

```markdown
## Schema Projection Report

Generated <timestamp> by design-intake skill v<version>.

### Eaten ✅ (<N> fields)
Claude Design will ingest these correctly.

- color.primary.* (palette, HSL, dark pair)
- typography.body / heading / caption (family, size, weight, line-height)
- component.button / input / card × states
- layout.base (spacing, radius, breakpoints)
- material.noise / chrome / liquid / matte / gloss (single-layer)

### Silent Drops ⚠️ (<N> fields) — requires fallback recipes

| Field | Recipe |
|---|---|
| material.composite | preserve in design.md §material; component-layer reassembly post-upload |
| motion.timing.fn=steps | positive constraint + design.md aesthetic rationale |
| contrast.tier | gate override + design.md §contrast-tiers |
| layout.page.* | base+delta pattern; per-page overrides applied at route level |

### Warn Drops ⚡ (<N> fields)
Partial ingest; attached metadata lost.

| Field | What drops | Recipe |
|---|---|---|
| typography.*.number-style | 'tabular' feature flag | apply at component level as font-feature-settings |

### Error Drops 🔥 (<N> fields)
Must fix before upload.

<none>  (or list blocking issues)

### Positive Constraints (separate axis, <N> rules)

| id | rule | enforcement |
|---|---|---|
| palette-lock | all colors subset of Endesga-32 | token-lint.py --positive palette-lock |
| grid-8 | all sizes multiples of 8px | token-lint.py --positive grid-8 |
```

This report is generated by `scripts/gate-check.py` from annotations in
`design.tokens.yaml`. The skill does not hand-write it — the script does.

---

## Regression watch

Claude Design's schema may expand over time (motion.steps, material composite,
tenant overlays are all plausible future additions). Fallback recipes that
are no longer needed because the schema now ingests natively should be marked
as **deprecated**, not deleted, so older bundles remain reproducible.

When Claude Design announces a schema change, update the drop tags in this
file and add a migration note in `design.md` roadmap.
