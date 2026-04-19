# Dusk · Terminology Map

Mandatory bundle artifact per design-intake skill v4.5. Translates Claude
Design's official ingestion vocabulary to this bundle's internal section
names and file paths, so team members uploading can reconcile the two
without guesswork.

Source reference: *"在 Claude Design 中設定您的設計系統"* (Anthropic
Support, zh-TW).

## 1. Category map (headline)

Claude Design extracts exactly four categories from uploaded assets.
Everything else is silently ignored or partially ingested.

| Claude Design (zh-TW) | English | `design.md §` | `design.tokens.yaml §` |
|---|---|---|---|
| 色彩調色板 | Color palette | § 4.1 Color · § 5 Semantic Tokens | `color.*` |
| 排版 | Typography | § 4.3 Typography | `typography.families` · `typography.scale.*` |
| 元件 | Components | § 6 Components | `components.*` |
| 版面配置模式 | Layout patterns | § 4.4 Spacing & Layout | `spacing` · `layout.*` |

## 2. Sub-field map

Finer-grained vocabulary bridges.

### 色彩調色板 (Color palette)

| Claude Design term | Dusk bundle |
|---|---|
| primary color | `color.semantic.fg.primary` → `color.neutral.50` (the brand uses text-on-canvas rather than a traditional brand color) |
| secondary color | Does not apply. Dusk has one signal color (`signal.flax`), not a secondary. |
| accent color | `color.semantic.accent.primary` → `color.signal.flax` |
| background | `color.semantic.bg.canvas` → `color.neutral.900` |
| surface | `color.semantic.bg.surface` → `color.neutral.950` (note: *darker* than canvas — cards recede into night) |
| elevated surface | `color.semantic.bg.elevated` → `color.neutral.800` |
| text color | `color.semantic.fg.{primary,secondary,muted}` |
| border color | `color.semantic.border.{subtle,strong}` |
| dark mode | `color.dark.semantic.*` — explicit; identical to non-dark (Dusk is dark-primary) |
| danger / warning / success | `color.semantic.state.*.base` |

### 排版 (Typography)

| Claude Design term | Dusk bundle |
|---|---|
| font family | `typography.families.primary = "Söhne, Inter, -apple-system, …"` |
| display / heading sizes | `typography.scale.{display,h1,h2}` (40 / 28 / 18 px) |
| body / small / caption | `typography.scale.{body,small,micro}` (16 / 14 / 12 px) |
| weight | `typography.scale.*.weight` — **only 400 and 500** (positive constraint) |
| line-height | `typography.scale.*.line-height` (number, not `normal`) |
| letter-spacing / tracking | `typography.scale.*.letter-spacing` |
| tabular numbers | Applied at sample-HTML level via `font-variant-numeric: tabular-nums`; no token surface in schema. |

### 元件 (Components)

| Claude Design term | Dusk bundle |
|---|---|
| Button primary | `components.button.variants.primary` — default / hover / focus / active / disabled / loading |
| Button secondary | `components.button.variants.secondary` — bordered, transparent bg |
| Input / text field | `components.input` — form-5state (default / hover / focus / disabled / error) |
| Card | `components.card` — interactive-5state |
| navigation item | `components.nav-item` — **left-side 2px bar indicator** (drop-silent) |
| list row | `components.list-row` — 44px min-height, line separator |
| form row | `components.form-row` — label + value, line separator |
| variant | `components.*.variants.<name>` (Button only in this bundle) |
| state | `components.*.<state>` or `components.*.variants.<variant>.<state>` |
| loading state | `components.button.variants.primary.loading.content: dots` — **dots subtype drops silent** |

### 版面配置模式 (Layout patterns)

| Claude Design term | Dusk bundle |
|---|---|
| grid | `layout.base.grid.mode = standard-12` with `columns: 12, gap: 24` |
| spacing rhythm | `spacing: [0, 4, 8, 12, 16, 24, 32, 48, 64, 96]` (explicit array) |
| breakpoints | `layout.breakpoints.{sm,md,lg,xl,2xl}` — Tailwind defaults |
| container | `layout.base.container.mode = fixed-max`, `max-width: 640` |
| page structure | `layout.page.{home,session,journal}` — **per-page deltas drop silent** |
| primary viewport | `layout.primary-viewport.width: 375, height: 812, posture: portrait-single-hand` |

## 3. Out-of-schema surface (drop-silent)

Eight bundle fields do not map to any of the four Claude Design categories.
Each has a fallback recipe — see `upload-checklist.md §
schema-projection-report` for full treatment.

| Bundle field | Drop tag | Fallback recipe |
|---|---|---|
| `positive_constraints[accent-as-signal-only]` | drop-silent | Manual-review rule documented in `design.md § 3`; post-upload audit prompt in checklist |
| `shadow.policy: forbidden` | drop-silent | Every component state explicitly writes `box-shadow: none`; sample HTML demonstrates absence |
| `components.button.*.loading.content: dots` | drop-silent | Sample HTML shows `···` rendering; `design.md § 6 Do & Don't` documents |
| `components.nav-item.selected-indicator: bar + left` | drop-silent | `sample-dashboard.html` renders explicitly; top post-upload audit item |
| `material.matte.rationale` | drop-silent | `render: flat` lands; rationale in `design.md § 4.7` |
| `layout.page.*` per-page deltas | drop-silent | Implementation layer applies deltas at route boundary; `design.md § 4.4` describes intent |
| `§ 10 Voice & Tone` (entire section) | drop-silent | Schema has no voice surface; human writers enforce per § 10; recurring post-upload audit item |
| `color.contrast.tier.*.scope-globs` | drop-warn | Pair-level contrast math lands; scope-glob routing does not |

## 4. Positive-constraint surface

Three self-imposed rules. Not overrideable within this run; separate axis
from drop-silent/eaten tags.

| id | rule | enforcement |
|---|---|---|
| `accent-as-signal-only` | signal-flax only in CTA / focus / error / selected | manual review (rule is semantic, not value-level) |
| `weights-restricted` | typography weights ∈ {400, 500} | `scripts/token-lint.py` |
| `material-policy` | no gloss / chrome / liquid / noise | `scripts/token-lint.py` |

## 5. Override surface

None. Dusk's gates all passed without structured exceptions. The neutral-
scale warn on 950/900/800 is informational, not an override — see
`upload-checklist.md § why-neutral-scale-warns-not-fails`.

## 6. What Claude Design cannot produce from this bundle

Even after a clean upload, Claude Design does not generate these surfaces
— they remain manual responsibilities:

- **Voice-and-tone copy.** `design.md § 10` documents the voice; human
  writers enforce. Generated outputs require post-publish copy review.
- **Timestamp convention.** Dusk uses minute-precision timestamps
  ("2:34 a.m.") as a tonal element; this is not a typographic token and
  doesn't carry through Claude Design's ingestion. Manual convention.
- **Meditation content / voice recordings / actual session audio.** Not a
  design-system concern; out of scope by definition.

## 7. Glossary

Terms in the bundle that may confuse cross-role readers.

- **Signal color** — a color that appears only when the UI needs user
  attention. In Dusk, `signal.flax` is the only non-neutral color and
  appears in CTAs, focus rings, errors, and the selected indicator.
  Decoration use is forbidden by the `accent-as-signal-only` positive
  constraint.
- **Semantic token** — a named token like `color.semantic.fg.primary` that
  points to a palette stop. Components reference semantic tokens so the
  palette can change without touching component definitions.
- **Positive constraint** — a user-asserted rule that restricts the design
  space beyond Claude Design's schema defaults (e.g., "weights only 400 /
  500"). Enforced by `scripts/token-lint.py`. Cannot be overridden within
  a run.
- **Drop-silent** — a field the upload accepts without error but does not
  ingest. The field vanishes from Claude Design's generated system.
- **Matte (material policy)** — in this bundle, a positive declaration
  that no other material finish is permitted — not a sheen level, but an
  enforced absence.
- **Readback sandwich** — the skill's three-part confirmation format
  (understanding / parameter / exclusion) used throughout intake.
  Preserved here only as footnote: all readbacks happened during
  generation and are captured in the bundle's token values.

---

*Generated by design-intake skill v4.5 · Bundle Dusk v1.0.0.
For operational details: `upload-checklist.md`. For narrative: `design.md`.
For machine spec: `design.tokens.yaml`. For brand-feel signals:
`assets/sample-*.html`.*
