# Claude Design Upload

The actual Claude Design onboarding is a **single setup form**, not a
multi-step upload sequence. This file is both the reference the skill
reads during Act ⑤ and the source for the user-facing
`upload-checklist.md` that ships with every bundle.

## Contents
- [The real setup form](#the-real-setup-form)
- [What the form ingests](#what-the-form-ingests)
- [Bundle → form-field mapping](#bundle--form-field-mapping)
- [Recommended code-folder layout](#recommended-code-folder-layout)
- [Post-setup: review and remix](#post-setup-review-and-remix)
- [Validation prompts](#validation-prompts)
- [Failure signals](#failure-signals)
- [What this skill cannot do for the user](#what-this-skill-cannot-do-for-the-user)

## The real setup form

Accessed at the Claude Design setup page under an organization's settings.
Five fields, all presented on one page:

1. **Company name and blurb** (textarea) — a sentence or short paragraph
   describing the product and/or design system
2. **Link code on GitHub** (URL) — a repository URL; alternative to field 3
3. **Link code from your computer** (folder drop) — Claude copies selected
   files; whole-folder upload is not used. The form suggests attaching a
   "frontend-focused subfolder" for large codebases
4. **Upload a .fig file** (file drop) — parsed locally in the browser,
   never uploaded
5. **Add fonts, logos and assets** (file drop) — individual brand files
6. **Any other notes?** (textarea) — free-form supplementary constraints

All fields beyond the blurb are optional. The form submits as a single
form-post, not as five separate uploads.

## What the form ingests

Claude Design extracts four output categories from whatever combination
of inputs is provided:

| Official (zh-TW) | English | Primary source among fields |
|---|---|---|
| 色彩調色板 | Color palette | code folder + assets + .fig |
| 排版 | Typography | code folder + .fig |
| 元件 | Components | code folder + .fig |
| 版面配置模式 | Layout patterns | code folder + .fig |

The blurb and notes are interpretive context. They influence extraction
but do not themselves map to categories.

### The one quote that matters most

> 包含真實範例，而不僅僅是規格。完成的登陸頁面或行銷網站比單獨的色彩
> 調色板更能向 Claude 說明您品牌的感受.

A rendered page conveys brand feel far better than a palette alone. Bundles
should ship at least two sample HTML pages inside the code folder so the
"real-example" signal is strong.

## Bundle → form-field mapping

The intake emits six bundle files. Field-by-field mapping for the user:

| Bundle file | Form field | How |
|---|---|---|
| `design.md` § 1 "Brand & Soul" first paragraph | **Company name and blurb** | User extracts the one-sentence blurb; intake can also emit a standalone `cd-upload/blurb.txt` |
| `design.tokens.yaml` + `assets/sample-landing.html` + `assets/sample-dashboard.html` | **Link code from your computer** | Package into a `cd-upload/design-system/` folder with `tokens.css`, `tokens.json`, sample HTML, and a `components.html` showcase. See § Recommended code-folder layout |
| _(nothing)_ | **Link code on GitHub** | Alternative to field 3; only if the brand's design system already lives in a git repo |
| _(nothing)_ | **Upload a .fig file** | The skill cannot produce `.fig` files (see `capability-boundaries.md`) |
| User-supplied logos, fonts, palette images | **Add fonts, logos and assets** | The skill does not generate these; user supplies if available |
| `design.md` § 2 "References" + § 3 "Positive Constraints" + § voice-and-tone, condensed | **Any other notes?** | Intake can emit a standalone `cd-upload/notes.md` with the human-pasteable content |
| `upload-checklist.md`, `terminology-map.md` | _(team-internal)_ | These are for the reviewer's audit; they do not enter Claude Design |

## Recommended code-folder layout

When emitting the `cd-upload/design-system/` folder for field 3, use this
shape. Claude Design's form tooltip recommends "frontend-focused
subfolder" for large codebases, so keep the folder small and
self-contained:

```
cd-upload/design-system/
├── README.md                explanatory — reading order + brand rules
├── tokens.css               CSS custom properties (primary token source)
├── tokens.json              W3C design-token JSON (DTCG schema)
├── components.html          every component × every state (showcase)
├── landing.html             brand-feel hero (strongest "real example")
└── journal.html             dashboard-class second surface
```

Skip anything the brand does not ship: no `components/` subfolder with
seven framework-specific files, no build config, no test suite. The folder
is a design-system specimen, not a codebase.

If the brand has specific framework conventions (React / Vue / Svelte),
include a minimal framework-native component alongside — but not a whole
component library. One representative component in the target framework
is plenty of signal.

## Post-setup: review and remix

After form submission, Claude Design analyzes and produces an initial
UI kit covering the four categories. The user reviews each category,
creates a test project, and iterates.

### Iteration

Small changes happen via the **重新混合 / Remix** button (top-right of
the design-system edit view). It opens a chat panel for incremental
token / component / pattern adjustment.

### Major revisions

For brand refreshes or new product lines, run the design-intake skill
again, emit a new version (v1.1 / v2.0), and upload as a separate
design system. Organizations can maintain multiple concurrent systems;
the "Make default" toggle selects which one new projects use.

## Validation prompts

Run three brand-specific prompts inside a Claude Design test project
before publishing. The intake should emit these tailored to the brand
in the bundle's `upload-checklist.md`. Examples by sim persona:

```
# Dusk (wellness / insomnia — dark restraint)
"為 Dusk 建立凌晨 2 點失眠用户的登陆页"
"设计显示这一周冥想记录的仪表板，列表式"
"制作关于'反治愈设计哲学'的品牌简报"

# ACIDLAB (Y2K maximalist e-commerce)
"為 ACIDLAB 建立 drop 倒计时登陆页"
"设计蹲点历史 + 命中率仪表板"
"制作 Y2K 美学宣言简报"

# VitalBoard (medical multi-tenant AAA)
"為 VitalBoard 建立 ICU 夜班登陆页，6 病人卡片"
"设计 vitals + 告警历史仪表板"
"制作多租户自定义产品简报"

# BENTO.EXE (indie pixel game companion)
"為 Midnight Bento 建立深夜便当存档登陆页"
"设计食谱进度 + 社区分享仪表板"
"制作独立游戏美术坚持简报"
```

A pass means the generated output feels correct across all three surfaces.
A fail on one or more → strengthen the relevant bundle inputs (add real-
example pages, sharpen the notes block) and re-run setup.

## Failure signals

If the Claude Design output diverges from the bundle, diagnose by
symptom:

### Palette drifts toward generic SaaS defaults
Bundle lacked signal-color specificity. Strengthen: add a real-example
landing page where the signal color is prominent but used as signal,
not decoration. Repeat the "signal-only" rule in the Notes field.

### Typography regresses to system fallback
Font family not loadable by Claude Design's preview environment. Mitigate
by spelling the family name exactly in `tokens.css`, include a complete
fallback stack, and add the font file to field 5 ("Add fonts, logos
and assets") if self-hosted.

### Components look right but feel "flat"
Material / composite extensions dropped silently (expected). Add sample
HTML that demonstrates the composite rendering so the generator can
approximate.

### Dark mode wrong or missing
The `dark-explicit` gate must pass before emitting. If the bundle
generated here, check every `color.semantic.*` has a matching
`color.dark.semantic.*`. Auto-invert was forbidden by the gate.

### Generated layout ignores per-page deltas
Expected drop-silent. Document per-page rationale in `design.md §
layouts` and apply the deltas at the implementation layer (route-level
CSS overrides). Claude Design's generation works at base-layout
granularity.

### Copy includes affirmations / emoji / exclamation points
Voice-and-tone rules are schema-silent (no surface in Claude Design's
category schema). Rely on Notes field + post-publish manual review.
Re-prompt with explicit voice rules embedded verbatim.

## What this skill cannot do for the user

The user must perform these steps manually — the skill emits the
bundle, not the upload:

- Open Claude Design and switch organization
- Drag `design-system/` into the form's drop zone
- Paste blurb and notes text
- Upload any `.fig` / logo / font files they have separately
- Submit, review the generated system, remix if needed, publish

The skill's `cd-upload/README.md` maps each file to each field so the
user doesn't have to infer.

## Schema evolution

Claude Design's schema may expand. When drop-silent items become
natively ingested, update `schema-projection.md § regression-watch` and
re-emit affected bundles.
