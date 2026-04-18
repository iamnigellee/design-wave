# Act ④a — Components

Define Button / Input / Card × five states (default / hover / focus /
active-or-selected / disabled, plus loading on triggerable components), and
the three composite components mandatory in v4.5: nav-item / list-row /
form-row.

3–4 minutes.

## Contents
- [The triad + three composites](#the-triad--three-composites)
- [State matrix rules](#state-matrix-rules)
- [State inheritance](#state-inheritance)
- [Button](#button)
- [Input](#input)
- [Card](#card)
- [nav-item](#nav-item)
- [list-row](#list-row)
- [form-row](#form-row)
- [Mobile-primary hover rule](#mobile-primary-hover-rule)
- [Exit conditions](#exit-conditions)

## The triad + three composites

Six components are mandatory before exiting Act ④:

| | why mandatory |
|---|---|
| Button | most-generated element; if tokens drift here, they drift everywhere |
| Input | user-text-entry surface; focus / error states define form UX |
| Card | elevation unit; defines how surfaces stack |
| nav-item | every product has navigation; indicator style is brand-defining |
| list-row | dashboards / data / settings screens lean on this |
| form-row | high-frequency entry surface (Patricia: nurses enter vitals 30×/shift) |

Additional components (dialog, toast, table, select, checkbox, etc.) are
optional per project — record in `design.md § optional-components` when the
user names them, but don't gate-block on their absence.

## State matrix rules

### Every component × every state references tokens, never raw values

```yaml
# good
component.button.default:
  bg: "{color.semantic.accent.primary}"
  fg: "{color.semantic.bg.canvas}"

# rejected (token-closure gate fails)
component.button.default:
  bg: "#6366F1"
```

### State names — fixed vocabulary

```
default, hover, focus, active (or selected for nav-item),
disabled, loading (triggerable only)
```

Do not invent names (`focus-ring`, `pressed`, `checked`). Use the core
vocabulary plus slot names (`.ring`, `.overlay`).

### What each state must declare

At minimum: `bg, fg`. Where relevant: `border, ring, shadow, opacity,
transform, cursor`. Omit fields that don't change from `default`.

```yaml
component.button:
  default: {bg, fg, radius, padding, weight}
  hover: {bg}                                # delta-only
  focus: {ring}                              # delta-only
  active: {bg, transform}
  disabled: {bg, fg, opacity, cursor}
  loading: {fg: transparent, spinner-token}
```

### Delta-only style

Record only the fields that change vs `default`. Reduces noise and makes
review trivially easy. `scripts/gate-check.py` expands deltas when verifying
state-completeness.

## State inheritance

When multiple components share a state pattern, declare a shared base:

```yaml
component:
  base:
    interactive-5state:
      states: [default, hover, focus, active, disabled]
    form-5state:
      states: [default, hover, focus, disabled, error]
    nav-selected:
      states: [default, active, disabled]

  button:
    extends: interactive-5state
    default: {...}
    hover: {...}
    ...
```

`extends` means the component declares all named states. Missing states fail
the triad-x-5state gate.

This lets projects extend the pattern (ACIDLAB adds `loading` to `Button`
but not `Input`; BENTO omits `hover` from mobile primaries — route via mobile-
primary rule below).

## Button

### Variants

Minimum two: `primary, secondary`. Add `ghost, destructive, link` as needed.

```yaml
component.button:
  extends: interactive-5state
  base:
    radius: "{radius.md}"
    padding: "{spacing.3} {spacing.5}"
    font: "{typography.scale.body}"
    weight: 500
  variants:
    primary:
      default: {bg: "{color.accent.primary}", fg: "{color.accent.primary-fg}"}
      hover:   {bg: "{color.accent.hover}"}
      focus:   {ring: "{focus-ring}"}
      active:  {bg: "{color.accent.active}", transform: "scale(0.98)"}
      disabled:{opacity: 0.4, cursor: not-allowed}
      loading: {fg: transparent, spinner: "{color.accent.primary-fg}"}
    secondary:
      ...
    destructive:
      ...
```

### Loading content — ask explicitly

Dusk forbade spinners ("太忙"), using three dots instead. Record choice:

```yaml
component.button.loading:
  content: dots      # or: spinner | bar | none
  rationale: "..."   # when non-default
```

## Input

### Variants

`text, textarea, number, password` at minimum. Underlying token set is shared;
variants differ in input-type attribute, not styling.

### Affordance gate (v4.5 addition)

`default` state must have at least one of:
- border (any side)
- background fill ≥ 2% luminance delta from parent surface
- label-inside or placeholder permanently visible

Pure text-in-surface with no border and no fill will fail the affordance
gate. Dusk had to add a 1% fill to satisfy Patricia-class users who worried
the input wouldn't be visible.

### Error state

Input gains `error` instead of (or alongside) `disabled`:

```yaml
component.input.error:
  border-bottom: "{color.state.danger.base}"
  hint-color: "{color.state.danger.fg}"
  indicator: dot-right   # or: banner-below | outline
```

## Card

```yaml
component.card:
  base:
    bg: "{color.semantic.bg.surface}"
    padding: "{spacing.6}"
    radius: "{radius.lg}"
    border: "1px solid {color.semantic.border.subtle}"
  variants:
    default: {}
    interactive:
      extends: interactive-5state
      hover: {border-color: "{color.semantic.border.strong}"}
      focus: {ring: "{focus-ring}"}
    raised:
      shadow: "{shadow.md}"                   # if shadow policy allows
```

`raised` variant only when `shadow.policy ≠ forbidden`. Otherwise omit —
gate-check will fail if `raised` is declared but shadow is forbidden.

## nav-item

```yaml
component.nav-item:
  base:
    icon:
      type: svg                # one of: svg | icon-font | pixel-sprite
      size: 20
    label:
      font: "{typography.scale.small}"
    gap-icon-label: "{spacing.3}"
    padding: "{spacing.2} {spacing.3}"
  states:
    default: {fg: "{color.semantic.fg.muted}"}
    hover:   {fg: "{color.semantic.fg.primary}"}
    focus:   {ring: "{focus-ring}"}
    active:  {fg: "{color.semantic.accent.primary}"}
    disabled:{opacity: 0.4}
  selected-indicator:
    style: bar               # bar | underline | pill | dot | border-left
    thickness: 2
    color: "{color.semantic.accent.primary}"
    position: bottom         # bottom | top | left | right
```

### icon.type options
- `svg` — default. Schema-safe.
- `icon-font` — requires font family registered in `typography`.
- `pixel-sprite` — `drop-silent`. Recipe: svg with `shape-rendering:
  crispEdges` + disabled anti-alias. Record material binding to palette lock
  if relevant.

### indicator.style options
All ingest to some degree, but `border-left` is unusual for mobile bottom
navs — the skill warns if selected.

### gap specifics
Patricia sim surfaced that nav-item's `gap-icon-label` is commonly
under-specified. Always declare explicit spacing token, not "small".

## list-row

```yaml
component.list-row:
  base:
    padding: "{spacing.3} {spacing.4}"
    min-height: "{spacing.11}"
    separator:
      style: line              # line | dashed | none
      color: "{color.semantic.border.subtle}"
      placement: bottom
  layout:
    leading: {type: icon|avatar|none, size, gap-to-title}
    title: {font, weight, color}
    subtitle: {font, weight, color}
    trailing: {type: chevron|meta|action|none, gap-from-title}
  states:
    default: {}
    hover: {bg: "{color.semantic.bg.elevated}"}
    focus: {ring}
    selected: {bg: "{color.semantic.accent.bg-subtle}"}
    disabled: {opacity: 0.4}
```

### Separator style

`dashed` drops under schema projection (border style drops). Fallback
recipe: document voice in `design.md § list-row` and apply at component
implementation level.

## form-row

```yaml
component.form-row:
  base:
    padding: "{spacing.2} 0"
    gap-label-value: "auto"           # justify-between layout
    separator:
      style: line                     # line | dashed | none
      color: "{color.semantic.border.subtle}"
      placement: bottom
  layout:
    label: {font, color, align: left}
    value:
      font
      color
      align: right
      number-style: tabular?           # if tabular declared in typography
  variants:
    readonly: {}
    editable: {} # merges with component.input
    error: {hint-color, indicator}
```

form-row is the highest-leverage composite for data-entry products. If the
user's use-moment involves structured input, spend extra time here.

## Mobile-primary hover rule

For mobile-primary products (majority of intakes), `hover` is a
conceptually weak state. Two acceptable strategies:

### Strategy A — omit hover entirely
Route via gate-override Pattern E (see `gate-overrides.md`):

```yaml
component.button:
  extends: interactive-5state
  omit-states: [hover]
```

### Strategy B — mirror hover to active
Keep hover defined but identical to active. Documents the intent that hover
doesn't carry information on touch:

```yaml
component.button:
  hover: "{component.button.active}"   # deliberate alias
```

Both are valid; Strategy A is cleaner for strictly-mobile products.

## Exit conditions

- All six components (triad + composites) defined
- Each extends a state-set base or declares states explicitly
- Every state field references tokens, not raw values (token-closure)
- Affordance gate passes for Input
- If hover omitted, override registered with scope
- If `indicator`, `separator`, `icon.type` uses non-default values, schema-
  projection tags noted

Readback:
```
Button   : <N> variants, <state-set>, loading=<dots|spinner|bar>
Input    : <N> variants, affordance via <border|fill|label>, error=<style>
Card     : <N> variants, raised=<yes|no per shadow policy>
Nav-item : indicator=<style>/<position>/<color>, icon.type=<>
List-row : leading=<>, trailing=<>, separator=<>
Form-row : number-style=<>, separator=<>, error=<>

→ Act ④b layout tokens. 继续？
```
