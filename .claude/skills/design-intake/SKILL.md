---
name: design-intake
description: Use this skill whenever a user wants to build a design system, prepare
  brand assets for Claude Design onboarding, or translate brand intuition into an
  upload-ready bundle. Trigger on mentions of "design system / brand intake /
  Claude Design upload / design.md / design tokens / 设计系统 / 品牌视觉 / 调性
  梳理 / 落地页 / 仪表盘 / 配色 / 排版 / 设计资产". It runs a 5-act conversational
  intake (framing → anchors → visual tokens → components & layout → preview),
  adapts depth to novice / guided / expert users without locking soft-dimension
  capture to expert mode, mechanically verifies gates with overrides, projects
  the output against Claude Design's 4-category schema, and emits a bundle
  containing design.md, design.tokens.yaml, sample-landing.html,
  sample-dashboard.html, upload-checklist.md, and terminology-map.md.
---

# Design Intake

Turn brand intuition into a Claude-Design-ready upload bundle. Claude Design
ingests codebases, slides, PDFs, screenshots, logos, and palette files, then
extracts four categories: **色彩調色板 / 排版 / 元件 / 版面配置模式**. This skill
produces assets aligned to those four, plus a terminology map and fallback
recipes for anything the schema cannot hold.

Official onboarding flow reference: `references/claude-design-upload.md`.

---

## Runtime Rules (evaluate every turn)

These rules fire on every user turn. Keep them resident; deeper context lives
in referenced files.

### R1. Mode decision
Pick one of `novice / guided / expert` each turn. See
`references/adaptive-dialog.md` for the full decision table.

- User self-reports "not a designer" or "I don't know design" → lock out of
  `expert` even if they use jargon. Only density escalates, never assumptions.
- User self-reports hybrid ("I know hex but not tokens") → `guided` with
  terminology-sandwich auto-on.
- User writes hex / CSS / token references fluently and claims design
  background → `expert` with fast-track.

### R2. Soft-dimension checklist — mode-independent
All modes must tick the soft dimensions before exiting Act ②. Do not lock this
to `expert`. See `references/soft-dimension-checklist.md`.

Required ticks: `use-moment · why · three-adjectives · reference ·
anti-reference (3 tiers) · taboo · cultural-coordinate · differentiator ·
psychological-journey`.

### R3. Readback sandwich (three-part, not two)
Every time a user gives a metaphor or fuzzy descriptor, mirror back as:

```
我理解 X : <one-sentence paraphrase>
对应参数 Y : <concrete token or rule>
排除项 Z : <explicit "not this, not that">
```

Exclusion is mandatory. Without it, downstream generation drifts toward the
nearest cliché.

### R4. Negation-density rule
If the user rejects two candidates in a row on the same dimension, stop
proposing more candidates. Flip to a reverse-default (ask them to name what it
is *not*, then infer positives from exclusion). See
`references/adaptive-dialog.md#negation-density`.

### R5. Hard-value visibility
For `novice` and `guided` users, hide hex / px / HSL in conversation. Show
color swatches, A/B images, and metaphors. Hard values live only in the emitted
artifacts. For `expert`, show hard values inline and accept hex pastes.

### R6. Act ⑤ exit gate
Before emitting any artifact, run `scripts/gate-check.py` and paste the JSON
result. The result must be `pass` on every gate, or each non-pass must have a
structured override entry (see R7). No silent exit.

### R7. Gate override — structured only
Every override must carry `{reason, scope}` with:
- `reason` — three fields: `context-assumption`, `why-default-insufficient`,
  `upgrade-cost` (see `references/gate-overrides.md`).
- `scope` — a glob array naming exactly which tokens the override covers.
  Freeform `applies_to` / `targets` / `scope` strings are rejected.

### R8. Schema projection — three-state
Before Act ⑤, produce a schema projection report tagging every token and rule:
- ✅ `eaten` — Claude Design's 4-category schema ingests this
- ⚠️ `drop-silent` — schema ignores without warning (most common — flag loudly)
- 🔥 `drop-error` — schema would error on this shape (must fix)
- ⚡ `drop-warn` — schema partially ingests with warning
- 🔧 `fallback-recipe` — required for every drop-silent / drop-warn

Positive constraints (e.g., "≤32 colors locked to Endesga-32", "8px grid
mandatory") are a separate axis — not drop states. They live in their own
`positive_constraints:` block. See `references/schema-projection.md`.

---

## Act Navigation

| # | Act | Goal | Reference |
|---|-----|------|-----------|
| ① | Framing | product · use-moment · why | `references/act-1-framing.md` |
| ② | Anchors | 3-adjective / reference / anti-reference (3 tiers) / taboo / culture / differentiator | `references/act-2-anchors.md` |
| ③a | Color & Type | palette, contrast tiers, type scale | `references/act-3a-color-type.md` |
| ③b | Spacing & Motion | spacing, radius, motion timing functions, material | `references/act-3b-spacing-motion.md` |
| ④a | Components | triad + composite (nav-item, list-row, form-row) × 5 states | `references/act-4a-components.md` |
| ④b | Layout | per-page layout tokens, base+override | `references/act-4b-layout-tokens.md` |
| ⑤ | Preview & Confirm | gate-check, schema projection, sample render, sign-off | `references/act-5-preview-confirm.md` |

Fast-track (expert only): compress ①+② to ~3 minutes, but soft-dimension
checklist (R2) still runs completely. See `references/expert-fast-track.md`.

---

## Output Bundle

Written to repo root (or user-specified dir):

```
design.md              — brand soul + tokens narrative + positive constraints
                         + anti-reference 3-tier + terminology map + roadmap
design.tokens.yaml     — machine-readable tokens (color, type, spacing, radius,
                         motion w/ typed timing fn, material w/ composite,
                         components, per-page layout, contrast tiers)
assets/sample-landing.html     — real sample at 375×812 viewport
assets/sample-dashboard.html   — real sample at 375×812 and desktop
upload-checklist.md    — pre-flight checks + setup-form field map + post-
                         publish audit plan + gate-check JSON + overrides
terminology-map.md     — Claude Design official categories ↔ this bundle's
                         sections (mandatory, not optional)
cd-upload/             — ready-to-paste artifacts matched to Claude Design's
                         real setup form
  ├── README.md        — field-by-field mapping
  ├── blurb.txt        — paste into "Company name and blurb"
  ├── notes.md         — paste into "Any other notes?"
  └── design-system/   — drop folder into "Link code from your computer"
      ├── tokens.css           CSS custom properties
      ├── tokens.json          W3C design-token JSON
      ├── components.html      every component × every state
      ├── landing.html         brand-feel hero
      ├── journal.html         dashboard-class second surface
      └── README.md            reading order + brand rules
```

Templates live in `assets/`. See `references/claude-design-upload.md` for
the real setup form (single-page, six fields) and test prompts.

---

## Capability Boundaries

This skill cannot produce: `.aseprite` binaries, `.ase`, raster spritesheets,
WebGL shaders, Figma files, actual GIF / video. It can produce: `.gpl` palettes,
`figma-tokens.json`, `tailwind.config.js`, CSS variables, static HTML samples.

When a user pushes past the boundary, use the degradation script in
`references/capability-boundaries.md` — do not improvise.

---

## Why This Structure

- Runtime rules stay in this file because they fire every turn (R1–R8).
- Act content, gate definitions, override rules, and schema-projection mechanics
  live in `references/` because they load only when the relevant act or gate
  activates (Anthropic skill progressive disclosure).
- Templates live in `assets/` so they never enter context until written.
- Scripts live in `scripts/` so gate evaluation is mechanical, not prose-by-
  convention.
