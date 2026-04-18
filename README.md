# design-wave

A Claude Code skill that turns brand intuition into a Claude-Design-ready
upload bundle through a 5-act conversational intake.

The skill lives at [`.claude/skills/design-intake/`](./.claude/skills/design-intake/).
Source of truth: [`.claude/skills/design-intake/SKILL.md`](./.claude/skills/design-intake/SKILL.md).

## What it does

[Claude Design](https://support.claude.com/en/articles/14604416-get-started-with-claude-design)
extracts a design system from uploaded assets (codebase, slides, PDFs,
screenshots, palette files) and re-exposes it as four categories:
**色彩調色板 / 排版 / 元件 / 版面配置模式**. Quality of generated output
depends entirely on the quality of those uploaded assets.

`design-intake` is the upstream step. Through five conversational acts —
framing, anchors, visual tokens, components & layout, preview & confirm —
it captures both:

- **Soft dimensions** (brand soul, why, use moment, three adjectives,
  references and three-tier anti-references, taboos, cultural coordinate,
  differentiator, psychological journey)
- **Hard tokens** (palette, contrast tiers, typography, spacing, radius,
  motion with typed timing functions, material extensions including
  composite layering, components × five states, per-page layout deltas)

It then mechanically verifies seven gates, projects the output against
Claude Design's schema, and emits a six-file bundle: `design.md`,
`design.tokens.yaml`, `sample-landing.html`, `sample-dashboard.html`,
`upload-checklist.md`, `terminology-map.md`.

## Quick start

In a Claude Code session inside any repo where this skill is installed:

```
> 我想给我的产品做一份设计系统，准备上传给 Claude Design
```

The skill auto-triggers on phrases like *设计系统 / 品牌视觉 / Claude
Design upload / design.md / 调性梳理 / 落地页 / 配色 / 排版*. It detects
expert vs guided vs novice mode, runs the appropriate 5-act flow, and
writes the bundle to your repo root.

## What makes this skill different

Three design decisions came out of dogfooding against four extreme
personas (a non-technical wellness founder, a Y2K-maximalist designer,
a healthcare PM with WCAG-AAA needs, an indie pixel-game studio):

1. **Soft dimensions are mode-independent.** Every mode — including
   expert fast-track — runs the full 10-dimension soft checklist. Earlier
   versions locked it to expert mode; novice and guided users dropped
   the brand soul silently. Now they can't.
2. **Gate overrides are structured.** Each override carries a 3-field
   reason (context-assumption / why-default-insufficient / upgrade-cost)
   and a glob-scope. Freeform "client requirement" reasons are rejected
   by `scripts/gate-check.py`.
3. **Schema projection is explicit.** Before any artifact ships, the
   skill tags every emitted field as `eaten / drop-silent / drop-warn /
   drop-error / fallback-recipe`. Users learn upfront what Claude Design
   will silently ignore — and every silent-drop must have a concrete
   fallback recipe before the bundle emits.

## Structure

```
.claude/skills/design-intake/
├── SKILL.md                      navigation + 8 runtime rules
├── references/                   per-act + per-topic guidance (loaded on demand)
│   ├── act-1-framing.md
│   ├── act-2-anchors.md
│   ├── act-3a-color-type.md
│   ├── act-3b-spacing-motion.md
│   ├── act-4a-components.md
│   ├── act-4b-layout-tokens.md
│   ├── act-5-preview-confirm.md
│   ├── adaptive-dialog.md
│   ├── soft-dimension-checklist.md
│   ├── expert-fast-track.md
│   ├── self-check-gates.md
│   ├── gate-overrides.md
│   ├── schema-projection.md
│   ├── material-extensions.md
│   ├── capability-boundaries.md
│   └── claude-design-upload.md
├── scripts/                      mechanical enforcement
│   ├── gate-check.py             7 gates + structured-override validation
│   └── token-lint.py             positive-constraint enforcement
└── assets/                       output bundle templates
    ├── design.md.tmpl
    ├── design.tokens.yaml.tmpl
    ├── sample-landing.html.tmpl
    ├── sample-dashboard.html.tmpl
    ├── upload-checklist.md.tmpl
    ├── terminology-map.md.tmpl
    └── mood-prompts.md           stall-breaking reference (not in bundle)
```

The structure follows the [Anthropic Agent Skills](https://github.com/anthropics/skills)
progressive-disclosure convention: SKILL.md stays small (~160 lines, well
under the 500-line ceiling); references load only when their act or topic
becomes relevant; assets and scripts never enter context until the skill
needs to write or run them.

## Verifying the scripts

Both scripts run on Python 3.10+ with PyYAML. From the repo root:

```bash
python3 .claude/skills/design-intake/scripts/gate-check.py path/to/design.tokens.yaml
python3 .claude/skills/design-intake/scripts/token-lint.py path/to/design.tokens.yaml
```

Exit code `0` = `pass` or complete `override`. Non-zero = blocking
failures. JSON output is designed to be pasted verbatim into the
emitted `upload-checklist.md`.

## Versioning

Current skill version: **v4.5**.

Major decisions and their dogfood-test rationale are recorded in commit
messages:
- `fc07fa6` — Phase 1: SKILL.md + 3 core runtime references
- `ab999f7` — Phase 2: 7 act + 6 support references
- `71213f2` — Phase 3: scripts + 7 asset templates

For roadmap items deferred from v4.5 (multi-tenant theming as first-class
schema, color-blind redundancy channels, RTL logical properties, HiDPI
scale strategies, genre-aware gate weighting, capability-boundary
artifact-format matrix, etc.), see the v5-tier discussion in the commit
history of this branch.

## License

The skill is provided for educational and operational use within
projects authorized to integrate with Claude Design. Adapt freely; if
you ship improvements, consider opening a PR back to this branch so
the dogfood corpus grows.
