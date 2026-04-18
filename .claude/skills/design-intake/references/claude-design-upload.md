# Claude Design Upload

Official 4-step onboarding flow for pushing the emitted bundle into Claude
Design. This file is both the reference the skill reads during Act ⑤ and
the template for the user-facing `upload-checklist.md` that ships with
every bundle.

Source: Anthropic support article — *"在 Claude Design 中設定您的設計系統"*.

## Contents
- [What Claude Design ingests](#what-claude-design-ingests)
- [Prerequisites](#prerequisites)
- [The 4-step flow](#the-4-step-flow)
- [Validation prompts](#validation-prompts)
- [Upload-checklist template](#upload-checklist-template)
- [Post-upload remix](#post-upload-remix)
- [Failure signals](#failure-signals)

## What Claude Design ingests

Claude Design accepts these source types as **assets**:

- **Codebase** (GitHub link or zip) — React components, CSS, Tailwind
  config, tokens files
- **Slide deck** — PowerPoint, Google Slides, Keynote, PDF presentation
- **PDF / documents** — brand guide, style guide, marketing collateral
- **Screenshots / mockups** — existing product screens, Figma exports
- **Individual brand assets** — logos, palette files, type specimens

It extracts and produces four output categories:

| Official (zh-TW) | English | Covers |
|---|---|---|
| 色彩調色板 | Color palette | primary / secondary / accent, semantic, dark pair |
| 排版 | Typography | font families, size, weight, line-height |
| 元件 | Components | Button, Card, nav, common UI patterns |
| 版面配置模式 | Layout patterns | spacing, grid, breakpoints, page structure |

Anything outside these four is ignored silently (see
`schema-projection.md § drop-silent`).

### The one quote that matters most

> 包含真實範例，而不僅僅是規格。完成的登陸頁面或行銷網站比單獨的色彩
> 調色板更能向 Claude 說明您品牌的感受。

A rendered landing page conveys brand feel far better than a color palette
alone. The bundle ships with `sample-landing.html` and `sample-dashboard.
html` specifically to supply these "real examples".

## Prerequisites

- Claude Pro / Max / Team / Enterprise subscription (Claude Design is
  research preview, Enterprise must opt in)
- Organization admin has granted design-system setup permission
- At least one source asset ready to upload (the bundle provides this)

## The 4-step flow

### Step 1 — Create or switch to your organization

1. Open Claude Design
2. In the project selector (bottom-left), click the current organization
   name
3. Select your organization or create a new one
4. You are redirected to onboarding. Complete it.

### Step 2 — Upload brand + product assets

Upload the emitted bundle. Recommended order, strongest signal first:

1. `sample-landing.html` + `sample-dashboard.html` — real-example pages
   (strongest signal per official guidance)
2. `design.md` — narrative + tokens + positive constraints
3. `design.tokens.yaml` — machine spec
4. `logo/` (if provided separately) + `palette.png` (visual palette card)
5. `type-specimen.png` (if provided)

Claude will analyze and extract a reusable design system. Providing
multiple sources gives Claude richer signal.

### Step 3 — Review the generated system

Claude produces a UI kit typically containing:
- Color palette (primary / secondary / accent extracted from assets)
- Typography (family, size, weight)
- Components (buttons, cards, nav, UI patterns)
- Layout patterns (spacing, grid, page structure)

Validate against brand expectation by creating a test project. Use the
three official test prompts:

```
為 <your product> 建立登陸頁面
設計顯示 <relevant metric> 的儀表板
製作關於 <your team's usual topic> 的簡報
```

If the output matches the brand, proceed. If not, iterate (Step 2 —
upload additional or different assets).

### Step 4 — Publish for your team

Once the quality is acceptable:
1. Toggle the "已發佈" (Published) switch to ON
2. From this point, any project created from the Claude Design homepage
   within your organization uses this design system (instead of the
   default Claude Platform Design System)

## Validation prompts

Per the bundle's brand:

```
# Dusk (wellness / insomnia)
"為 Dusk 建立凌晨 2 點失眠用户的落地页"
"设计显示今晚冥想时长和睡眠质量的仪表板"
"制作关于'反治愈设计'的简报"

# ACIDLAB (drop-style e-commerce)
"為 ACIDLAB 建立 drop 倒计时落地页，显示明天 23:59 EST 的 drop"
"设计显示用户蹲点历史和 drop 命中率的仪表板"
"制作关于 Y2K drop 美学宣言的简报"

# VitalBoard (medical monitor)
"為 VitalBoard 建立 ICU 护士站夜班落地页，6 个病人卡片"
"设计显示患者 vitals + 告警历史的仪表板"
"制作关于多租户医院自定义的产品简报"

# BENTO.EXE (pixel game companion)
"為 Midnight Bento 建立深夜便当存档落地页"
"设计显示食谱进度 + 社区分享的仪表板"
"制作关于独立游戏美术坚持的简报"
```

If the generated output on these prompts feels correct, the brand
signal reached Claude Design intact. If it feels wrong, specific aspects
(palette drift, typography regression, component style mismatch) indicate
which part of the bundle needs strengthening — usually by adding more
real-example pages.

## Upload-checklist template

The template in `assets/upload-checklist.md.tmpl` renders to something like:

```markdown
# <Brand> → Claude Design Upload Checklist

## Before upload
- [ ] Run scripts/gate-check.py → all gates pass or have structured override
- [ ] Run scripts/token-lint.py → all positive constraints satisfied
- [ ] Review schema-projection report for drop-silent items and recipes
- [ ] Rendered samples look right at primary viewport

## Step 1 — organization
- [ ] Open Claude Design
- [ ] Switch to organization <name>

## Step 2 — upload (strongest signal first)
- [ ] Upload assets/sample-landing.html
- [ ] Upload assets/sample-dashboard.html
- [ ] Upload design.md
- [ ] Upload design.tokens.yaml
- [ ] Upload logo + palette.png + type-specimen.png (if available)

## Step 3 — validate
- [ ] Test prompt 1: <bespoke to brand>
- [ ] Test prompt 2: <bespoke to brand>
- [ ] Test prompt 3: <bespoke to brand>
- [ ] Output matches brand expectation on all three

## Step 4 — publish
- [ ] Toggle 已發佈 / Published to ON
- [ ] Notify team that <brand> design system is live

## Gate-check JSON (copied verbatim from scripts/gate-check.py output)
<json block>

## Schema-projection report
<report>

## Overrides registered
<list>

## Positive constraints
<list>

## Post-upload manual actions
<red-flagged items>
```

## Post-upload remix

After publishing, design-system refinement happens via the "重新混合"
(Remix) button in the top-right of the design-system edit view. This
opens a chat panel on the left where the user collaborates with Claude to
adjust. Use this for small iterative changes.

For major revisions (brand refresh, new product line), run the intake
skill again, emit a new bundle versioned (e.g., `v2.0`), and upload as a
second design system alongside the first. The organization settings
screen lets multiple systems coexist — teams can "Make default" to
select.

## Failure signals

If the Claude Design output diverges from the bundle, diagnose by symptom:

### Palette drifts toward generic SaaS blue
- Bundle lacked signal-color specificity. Strengthen by adding a real-
  example landing page with the signal color prominent.
- Check: is the accent color in design.tokens.yaml actually appearing in
  `component.button.primary.default.bg`? If not, the link is broken.

### Typography regresses to system fallback
- Font family not loadable by Claude Design's preview environment. Provide
  family name spelled exactly + add `font-display: swap` guidance in
  design.md.
- For self-hosted fonts, include the font file URL in the upload note.

### Components look right but feel "flat"
- Material / composite extensions dropped silently. Expected if no CSS
  fallback was documented. Add sample HTML demonstrating composite
  rendering so Claude Design's generator can approximate.

### Dark mode wrong or missing
- dark-explicit gate must pass. Check: for every `color.semantic.*`, is
  there a matching `color.dark.semantic.*`? If auto-invert was relied on,
  fix and re-upload.

### Generated layout ignores per-page deltas
- Expected drop-silent. Confirm `design.md § layouts` describes per-page
  rationale, and at implementation level the engineer applies base +
  delta. This is never fully automated.

## Schema evolution

Claude Design's schema may expand. When it does, drop-silent items may
become `eaten`. See `schema-projection.md § regression-watch` for how to
update the projection tags and migrate prior bundles.
