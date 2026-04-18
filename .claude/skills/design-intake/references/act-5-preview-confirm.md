# Act ⑤ — Preview & Confirm

Render samples at primary viewport, run mechanical gate-check, produce the
schema projection report, collect user edits on the rendered samples, and
get sign-off before emitting the bundle.

2–3 minutes. This is the exit gate. Nothing ships without it.

## Contents
- [Render samples](#render-samples)
- [Device-viewport validation](#device-viewport-validation)
- [Run gate-check](#run-gate-check)
- [Run token-lint for positive constraints](#run-token-lint-for-positive-constraints)
- [Produce schema-projection report](#produce-schema-projection-report)
- [User sample review loop](#user-sample-review-loop)
- [Sign-off](#sign-off)
- [Emit bundle](#emit-bundle)
- [Post-emit: record roadmap](#post-emit-record-roadmap)

## Render samples

Generate two HTML samples from the accumulated tokens:

1. **Landing** — product identity page; hero + primary CTA + one
   supporting surface. Demonstrates display typography, accent color,
   motion on the CTA.
2. **Dashboard / second surface** — information-dense page; demonstrates
   composite components, grid mode, state variety. For products that have
   no dashboard (e.g., consumer content app), substitute a list-heavy
   second surface (library / feed / archive).

### Template sources

`assets/sample-landing.html.tmpl` and `assets/sample-dashboard.html.tmpl`
contain the skeleton. Fill by substituting token values from the accumulated
`design.tokens.yaml` state.

### What must appear in landing

- `display` or `h1` typography
- Primary button in `default` and at least one other state rendered
  alongside
- Semantic `bg.canvas` + `bg.surface` visible
- If signal/accent color exists, rendered in the CTA
- If `material.composite` declared, visually applied to the hero section
- At `primary-viewport` dimensions

### What must appear in dashboard

- `h2` + `body` typography
- Card in `default` + one interactive state
- nav-item (at least two, one in `active`)
- list-row OR form-row (at least three rows)
- Grid mode correctly rendered (standard-12 / broken-12 / full-bleed-stack)
- At `primary-viewport` *and* at `desktop` (1280+) dimensions if the product
  has a desktop use-case

## Device-viewport validation

### Render at primary viewport first

Default: 375 × 812 (iPhone 13 mini class). If user declared a different
`primary-viewport` in Act ④b, render there.

### Check font-size-at-viewport

Ask the user to eye-check:
> 标题在手机上看起来对吗？不是纸面上 32px 对不对，是手机上**看着**够不
> 够、不够打眼、不刺眼。

Display typography often reads much smaller at device scale than in
tokens. Dusk's 32px `display` read as "公告" at 375px width — had to
bump to 40px.

### HiDPI validation

If `layout.hidpi` declared, also render at 2× and 3× logical scales to catch
sub-pixel rendering issues (pixel-aesthetic projects). BENTO's bitmap fonts
blurred at 3× without the transform:scale strategy.

### Record the viewport check as a gate result

```yaml
gate.viewport-type:
  status: pass             # or: warn if font-size-at-viewport feedback led
                           # to token changes
  notes: "display bumped 32→40 at 375px"
```

## Run gate-check

Execute `scripts/gate-check.py design.tokens.yaml`. It returns a JSON
report:

```json
{
  "skill_version": "<version>",
  "gates": {
    "contrast": {"status": "pass|override|fail", "details": ...},
    "neutral-scale": {"status": "...", "tier": <N>},
    "triad-x-5state": {"status": "..."},
    "dark-explicit": {"status": "..."},
    "token-closure": {"status": "..."},
    "affordance": {"status": "..."},
    "viewport-type": {"status": "..."}
  },
  "overrides": [ ... structured override entries ... ]
}
```

See `self-check-gates.md` for exact gate definitions and failure messages.

### Blocker rule

- `pass` or `override (with complete structured reason)` — advance
- `fail` — block. Return to the relevant act to fix. Do not let the user
  override a `fail` verbally; the override must be registered through the
  structured contract (see `gate-overrides.md`).

Dropping to `fail`-without-fix is the single most-common failure mode in
dogfood testing. The skill's job is to not let it happen.

## Run token-lint for positive constraints

Execute `scripts/token-lint.py design.tokens.yaml`. For every positive
constraint (`palette-lock`, `grid-N`, `motion-stepped-only`, etc.), the
linter walks every token and reports violations:

```
[FAIL] palette-lock: color.material.dither.colors[1] = "#1a1932"
       is not a palette reference. Expected one of {color.bg.base,
       color.bg.raised, color.bg.pos-warm, ...}.
```

### Lint failures block
Unlike gates, positive constraints are self-imposed — they cannot be
overridden within a run. A lint failure means either the token is wrong or
the constraint should be relaxed; decide which, fix, re-run.

## Produce schema-projection report

Run the projection from `scripts/gate-check.py --projection` (embedded in
gate-check but outputs separately). The report groups every emitted field
into the five tags (`eaten / drop-silent / drop-warn / drop-error /
fallback-recipe`). See `schema-projection.md § report-format` for the
exact template.

### Present the report to the user explicitly

Do not just drop the JSON. Narrate:

```
Schema projection report (预演 Claude Design 上传后会发生什么):

✅ <N> 字段会被吃下（color palette, typography scale, component states，
   layout base, ...）

⚠️ <N> 字段会被静默忽略（motion.steps, material.composite, per-page
   layout overrides, contrast.tier, multi-tenant overlay, ...）
   — 这些都有 fallback recipe 在 design.md 和 upload-checklist.md 里。

⚡ <N> 字段部分吃下（typography number-style：字体族会吃，tnum
   feature flag 会丢 — 已在组件实现层做 fallback）。

🔥 <N> 字段会导致上传失败（<list or "无">）。

你先看看有没有想变的。
```

### Patricia-class clarification

Patricia sim surfaced that users conflate "⚠️ 会被丢" with "会报错". Always
explicitly state: "静默忽略" — upload succeeds, field vanishes, no signal.
The fallback recipe exists because of this silence.

## User sample review loop

### Show the rendered landing + dashboard HTML

Two options:
- Inline HTML preview if the host supports
- File links the user opens separately

Ask:
> 先看这两张。气质对吗？有哪处一看就"不对"？

### Accept edits

Edit categories:

- **Token tweak** — "标题再大一点 / 再冷一点" → update token, re-render,
  re-run gate-check (contrast may change).
- **Composition tweak** — "CTA 移到下面" → sample-only change; does not
  touch tokens.
- **Missing surface** — "还想看一个空状态" → render a third sample.
- **Fundamental shift** — "整个气质不对" → return to Act ② or ③; do not
  try to fix in Act ⑤.

### Edit budget

Soft cap at 3 rounds in Act ⑤. Beyond 3, pause:
> 我们已经迭代 3 轮了。如果还没对——通常意味着前面幕的某个锚点错了。
> 要不要回 Act ② 看一下？或者锁当前版本作为 v1.0，差异记进 Roadmap？

## Sign-off

### Confirmation script

After the user approves the samples:

```
最终确认：

- Brand & Soul : <one-sentence summary>
- Palette      : <palette description + contrast tiers>
- Type         : <family + scale summary>
- Motion       : <duration range + timing-fn types>
- Material     : <single + composite summary>
- Components   : triad + 3 composites, <N> states each
- Layout       : <container mode> + <N> per-page deltas
- Gates        : <N> pass, <N> override (with reasons)
- Schema       : <N> eaten, <N> drop-silent (all with recipes)
- Constraints  : <positive constraints list>

回复"签" / "sign" / "就这样" 交付。或者告诉我哪里还要改。
```

### Version tag

On sign-off, tag the bundle with a version: `<name>-v1.0` (or follow the
user's convention). Reserved changes go into roadmap, not back into tokens.

## Emit bundle

Write all six bundle files (see `SKILL.md § output-bundle`) to the target
directory. Template sources in `assets/`.

```
design.md
design.tokens.yaml
assets/sample-landing.html
assets/sample-dashboard.html
upload-checklist.md
terminology-map.md
```

### Post-write verification

Run `scripts/gate-check.py` one more time against the emitted files (not the
in-memory state). Catches accidental template substitution errors.

## Post-emit: record roadmap

### Roadmap entries

Everything the user mentioned but isn't in v1.0 goes to `design.md §
roadmap`:

```yaml
roadmap:
  - id: v1.1-es-locale
    type: expansion
    description: "Spanish UI locale"

  - id: v1.2-rtl
    type: expansion
    description: "Arabic RTL with logical properties"

  - id: v2.0-tenant-overlay
    type: schema-upgrade
    description: "migrate extensions.multi-tenant to first-class schema
                  when Claude Design ships tenant support"

reserved-changes:
  - field: color.semantic.accent.signal
    currently: "{color.signal.flax}"
    may-change-to: "deep teal"
    trigger: "user feedback post-v1.0 launch"
    decision-deadline: "2 weeks post-launch"
```

### Why reserved-changes matters

Patricia sim ended with her saying "I might change signal color in two
weeks". Without a formal reserved-changes structure, that intent vanishes
and the next revision looks unprincipled.

### Upload handoff

Point the user to `references/claude-design-upload.md` for the official
4-step onboarding flow. The emitted `upload-checklist.md` already contains
the step-by-step, but the reference file explains *why* each step matters.

### Done

Return a terse confirmation message + the six file paths. Do not celebrate
or decorate the ending — users want the files, not confetti.
