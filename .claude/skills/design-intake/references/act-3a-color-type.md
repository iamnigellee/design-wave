# Act ③a — Color & Typography

Translate the Act ② anchors into palette and type-scale tokens. 4–5 minutes.
Contrast tiers (text / UI / decoration) are established here. Schema
projection for any out-of-schema fields happens in Act ⑤.

## Contents
- [Palette — from feeling to hex](#palette--from-feeling-to-hex)
- [Contrast tiers](#contrast-tiers)
- [Neutral scale](#neutral-scale)
- [Semantic tokens](#semantic-tokens)
- [Dark mode](#dark-mode)
- [Typography](#typography)
- [Exit conditions](#exit-conditions)

## Palette — from feeling to hex

### Input budget
Act ②'s sheet gave you:
- Three adjectives
- Positive references (each with a reason)
- Hue-tier anti-references
- Cultural coordinate

These are the inputs. Hex values are the output.

### Opening approach

**Novice / Guided** — show swatches, never hex:
> 我听到"克制、安静、微苦"+ 反商务夜间模式 + "Sigur Rós 封面"。我先给
> 你看三个主背景候选——左 A 右 B 中 C——你告诉我哪张接近：

(render three 80×80 color blocks side by side)

**Expert** — propose hex with HSL reasoning:
> 基于"克制 + Sigur Rós + 反商务蓝灰"锚点，背景从三个方向走：
> A. `#14110F` HSL(25 11% 6%) 暖黑（红褐底）
> B. `#0F1114` HSL(220 13% 7%) 冷黑（蓝底）
> C. `#121110` HSL(30 6% 7%) 中性黑
> 你先挑方向。

### Expansion strategy

Once the base hue direction is chosen, build outward:

1. **Base background** (1 value)
2. **Surface** (1 value, 2–5% luminance shift from base)
3. **Elevated** (1 value, another shift)
4. **Ink scale** (2–3 values: primary / secondary / muted)
5. **Signal / accent** (1 value minimum, more only if the brand demands)
6. **Neutral scale** — separate section below

Expand one layer at a time. Show each before adding the next. Do not dump a
full 50-value palette in one turn.

### Signal color — ask intent first

Before picking an accent, ask:
> 这个 accent 是装饰色还是信号色？
>   - 装饰色：出现在 hero / 插画 / 背景点缀，随处可见
>   - 信号色：只在 CTA / focus / 错误 / 选中态出现，出现就意味着"请注意"

This distinction produces radically different palettes. Dusk picked
"signal, not decoration" and dropped accents entirely — downstream design.md
records this as a positive constraint: `accent-as-signal-only`.

### HSL-component form

Always record color tokens in HSL components *and* hex:

```yaml
color:
  primary:
    500:
      hex: "#6366F1"
      hsl: "243 75% 59%"   # space-separated for shadcn CSS-var form
```

The HSL-component form is what shadcn / Tailwind use for runtime theming.
Hex alone is not enough.

### Validate against anti-references

After proposing each color, mentally run:
> 这个色有没有踩到 hue-tier 反参照？

Dusk's anti-ref list included "商务蓝", "创业紫". A `#2563EB` proposal
would fail the check. Log the rejection in state, not just in conversation.

## Contrast tiers

### Why tiered (Tier 1 change from v4.5)

A single contrast rule (AA 4.5:1) breaks for any project that wants
intentional low-contrast decoration (brutalist, pixel, retro, game). A
single AAA rule breaks any project that wants palette richness in
decorative regions.

### Structure

```yaml
contrast:
  tier:
    text: AAA            # ≥ 7:1 body, ≥ 4.5:1 large
    ui: AA               # ≥ 4.5:1 body, ≥ 3:1 non-text UI
    decoration: free     # user asserts no information carried
```

### Ask

For every project, establish all three tiers explicitly:

```
Text tier (正文、数字、按钮文字、表单 label) — 默认 AA。需要升到 AAA 吗？
  升 AAA 典型场景：医疗、航空、低照度、疲劳读、读错有后果
UI tier (边框、图标、分隔线) — 默认 AA。想松到 3:1 吗？
  松 3:1 典型场景：装饰边框、非交互分隔
Decoration tier (背景图案、插画、sprite) — 默认与 UI tier 同。
  用 free 的典型场景：故意低对比的像素/复古/brutalist 背景
```

### Scope glob

Each tier maps to token globs:

```yaml
contrast:
  text:        [text.*, component.*.label, component.*.value]
  ui:          [border.*, icon.*, divider.*, component.*.state.focus.ring]
  decoration:  [background.pattern.*, component.decoration.*,
                illustration.*]
```

Any token not matched by a glob falls under the strictest tier (`text`).

### If the user asks for a custom tier

Uncommon but real (e.g., "brand-hero tier" at > AAA for hero display type).
Route through gate-override Pattern D (see `gate-overrides.md`). Do not
invent new tier names in the schema — stick to the three, and use scope globs
to differentiate hero.* vs body.*.

## Neutral scale

### Default

9 stops (50, 100, 200, 300, 400, 500, 600, 700, 800, 900). Some projects
add 950 for deep-black surfaces (Dusk did).

### When to override

If the user's palette is externally locked (palette-lock positive
constraint — see `schema-projection.md § positive-constraints`), neutral
stops cannot be expanded arbitrarily. Common overrides:

- **5-stop** (pixel / retro palettes)
- **7-stop** (restrained brand systems)
- **13-stop** (alert-severity-rich systems like VitalBoard)

Route overrides through gate-override Pattern A or B. The token file stores
the full stops the brand allows; component state matrices reference only
those stops.

### Hue-shift rule

A neutral scale is never exactly HSL(*, 0%, *). Add a 2–8% saturation shift
along the brand's hue axis to prevent the scale from feeling foreign to the
palette. Examples:

- Dusk: 30° hue (warm brown-undertone), 6–11% sat
- ACIDLAB: 80° hue (matching acid), 2% sat (barely, to avoid "dirty" mix)
- VitalBoard: 210° hue (cool clinical), 2% sat

## Semantic tokens

### Rule

Every component references semantic tokens, never palette-stop tokens
directly.

```yaml
# good
component.button.default.bg: "{color.semantic.accent.primary}"

# bad
component.button.default.bg: "{color.blue.500}"
```

This lets the palette layer evolve without rewriting components, and lets
multi-tenant theming swap semantic tokens without touching palette.

### Minimum semantic set

```yaml
color.semantic:
  bg: {canvas, surface, elevated}
  fg: {primary, secondary, muted, inverse}
  border: {subtle, strong, focus}
  accent: {primary, hover, active}
  state:
    danger: {base, bg, fg}
    warning: {base, bg, fg}
    caution: {base, bg, fg}     # if > 3 severity tiers
    success: {base, bg, fg}
    info: {base, bg, fg}
```

If the project needs > 3 severity tiers (medical / industrial control),
expand `state.*` accordingly. Record as positive constraint if the tier
count is load-bearing.

### Locked tokens

For multi-tenant systems, tag semantic tokens that tenants cannot override
with `locked: true`:

```yaml
color.semantic.state.danger:
  base: "#D11414"
  locked: true   # tenant may not override — patient-safety token
  reason: "tenant-override of safety colors would defeat redundancy coding"
```

## Dark mode

### Rule
Dark mode is a *mode*, not a color-negation. Every semantic token has an
explicit dark value; `auto-invert` is forbidden.

### Default primary

Projects whose use moment is night / low-light (Dusk, BENTO) should declare
dark as the **primary** mode and light as the derivative. Sample HTML and
tokens lead with dark values.

### Dark adjustments

Simple hue inversion breaks:
- Saturated accents (they glow at 100% luminance on dark bg — ACIDLAB drops
  acid from 56% L to 42% in dark mode)
- Shadow-based elevation (shadows disappear — use border + luminance step
  instead)
- Semantic danger / warning (red on dark reads differently; often needs
  desaturation)

Record dark values explicitly, not as formulas.

## Typography

### Fields required per scale entry

```yaml
typography.scale.h1:
  family: "<primary>, <fallback1>, <fallback2>"
  size: 32        # px
  rem: 2.0
  line-height: 1.2    # number, not "normal"
  weight: 600
  letter-spacing: "-0.02em"
  feature-settings: "'ss01'"   # optional
```

All six fields mandatory except `feature-settings`. Line-height must be a
number; `normal` is rejected by `scripts/token-lint.py` because cross-browser
`normal` is unstable.

### Families — always a stack

Never one family. Minimum: `[primary, fallback, generic]`. Example:

```
"Söhne, Inter, -apple-system, BlinkMacSystemFont, sans-serif"
```

If the primary is a webfont that might fail to load (self-hosted bitmap,
paid license), include a visually nearest fallback. BENTO's `m5x7` falls
back to `ui-monospace` because both are narrow-width stepped fonts.

### Scale size count

Default 6 stops: `display, h1, h2, body, small, micro`. Extend to 8 for
design-heavy projects (ACIDLAB's 120/72/48/32 display stack). Contract to 4
for utility projects that do not display marketing text.

### Weight constraints

Ask if the brand has a weight-count rule. Restraint brands (Dusk) use only
two weights; expressive brands (ACIDLAB) use weight as texture and go 400 /
700 / 900.

Log weight constraint as positive constraint if it's load-bearing.

### Number style

If the product displays tabular numbers (dashboards, finance, medical
vitals, game scores), record:

```yaml
typography.scale.body:
  number-style: tabular   # applied via font-feature-settings: 'tnum'
```

This is `drop-warn` in schema projection (the family lands, the feature
flag drops). Fallback recipe: apply CSS at component level for numeric
displays.

## Exit conditions

Before advancing to Act ③b, verify:

- `color.palette.*` — all stops have hex + HSL
- `color.semantic.*` — bg / fg / border / accent / states filled
- `color.dark.*` — explicit values, no auto-invert
- `contrast.tier.*` — all three tiers scoped
- `typography.scale.*` — ≥ 4 stops, all fields filled
- `typography.families` — stacks with fallbacks

Readback summary:
```
色板  : <palette description> (signal-only / with-accent)
对比  : text=AAA ui=AA decoration=free (or the specific override set)
中性  : <N> stops, <hue>° base, <sat>% sat
字体  : <primary>/<fallback>, <N> stops, weight <restriction>, <tab-nums>?

→ 这些会在 Act ③b 继续扩展到 spacing、radius、motion、material。继续？
```
