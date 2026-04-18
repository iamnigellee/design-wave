# Adaptive Dialog

How to keep the intake conversation responsive to who the user actually is,
without locking soft-dimension capture to expert mode or bullying novices with
hex codes.

## Contents
- [Mode decision](#mode-decision)
- [Terminology sandwich](#terminology-sandwich)
- [Negation density](#negation-density)
- [Readback sandwich (three-part)](#readback-sandwich)
- [Hard-value visibility](#hard-value-visibility)
- [Stall breakers](#stall-breakers)
- [Skip / compress requests](#skip--compress-requests)

---

## Mode decision

Evaluate every turn, not just at start. Users reveal capability over time.

### Signals → mode

| Signal | Mode |
|---|---|
| Self-reports "not a designer" / "I don't know design" | `novice` (locked out of `expert` even if jargon appears) |
| Hybrid self-report: "I know hex but not tokens" / "I do game art but not UI" | `guided` + terminology-sandwich auto-on |
| Uses ≥ 2 jargon terms AND claims design background | `expert` |
| Pastes Figma links / hex strings / CSS in opening | `expert` candidate — confirm with one clarifier |
| Says "都行" / "都可以" / "你决定" | `novice` regardless of prior signals |
| Asks "what does X mean" mid-conversation | Drop one level, add sandwich for that turn |

### The anti-upgrade rule
Do not escalate novice → expert on jargon alone. Jargon leaks from marketing
copy, podcasts, or LLM drafting. Only escalate when jargon pairs with a fluent
operational claim ("I use Tailwind daily", "I ship React components").

### Density vs assumption
Mode controls two dimensions independently:
- **Assumption depth** — how much the skill assumes the user knows
- **Information density** — how many options / questions per turn

A mixed user (jargon-literate but untrained) gets `guided` assumption depth
with `expert` density. Patricia-class users need exactly this — novice density
feels patronizing, expert assumption feels unsafe.

---

## Terminology sandwich

Triggered automatically in `guided` mode. Every non-trivial term's first
appearance uses this format:

```
<term> (in plain words: <one-sentence paraphrase>)
```

Example: "semantic token (in plain words: a name like `fg.primary` that points
to a real color, so you change the pointer once and every component follows)".

Do not repeat the plain-words gloss after first use in the same act.

---

## Negation density

### Rule
Two rejections of candidates on the same dimension → stop proposing more
candidates. Flip to exclusion-inference.

### Why
Users who reject twice usually cannot name what they want — they know what
they don't want. Continuing to propose burns trust. Flip the question.

### Flip pattern

```
You've ruled out A and B. Instead of me guessing a third, tell me:
— What's the worst possible version of this (on this dimension)?
— What would make you close the app / hate the brand?
I'll infer the positive from the negation set.
```

### Threshold
Applies per dimension, per act. Rejections across different dimensions (color,
type, spacing) count separately. Reset the counter at act boundaries.

---

## Readback sandwich

Always three parts:

```
我理解 X : <paraphrase of what they said>
对应参数 Y : <concrete token, rule, or range>
排除项 Z : <explicit "not this, and not that">
```

### Why three, not two
A two-part readback ("I heard X, so I'll do Y") locks the positive but leaves
the negative implicit. Downstream generation fills implicit negatives with the
nearest cliché. The exclusion line forces explicit negation into the artifact.

### Exclusion sourcing
Pull Z from:
1. The user's current anti-reference list (highest priority)
2. The cliché nearest to Y in the same design space (e.g., if Y is "#B5FF1F
   acid green", Z includes "not Spotify green, not Fiverr green")
3. A paired opposite that the user's three adjectives exclude

### When to skip readback
- Expert mode on pure parameter questions ("radius should be 0") — acknowledge
  and move on.
- Short functional clarifications ("which page?") — no sandwich needed.

---

## Hard-value visibility

### Novice
- Never paste hex codes in conversation.
- Show 80×80 swatches, side-by-side comparisons, or A/B labeled images.
- Describe color as metaphor + temperature + saturation level (e.g., "cool
  off-black with a touch of warm undertone").
- Hex values land only in `design.tokens.yaml`.

### Guided
- Show swatches by default.
- Reveal hex on demand ("what's that in hex?" → yes).
- Use plain-English tokens in dialog ("primary", "background-canvas") instead
  of file-path references.

### Expert
- Hex, rem, HSL, cubic-bezier expressions inline are fine.
- Users may paste their own tokens; parse and confirm structure.

---

## Stall breakers

When the user gives silence, "都行", "不知道", or an off-topic detour:

### Three tools, in order

1. **Reference pair** — "Is it more like A or more like B?" where A and B are
   well-known products in their space. Ground abstraction.
2. **A/B binary** — show two images or swatch pairs. No third option.
3. **Default pin** — "I'll pin `<concrete default>` for now, we can revisit.
   Move on?"

### Pinning rules
When pinning a default, log it in the act's state as `pinned: true`. Pinned
items bypass gates only if the user explicitly confirms before Act ⑤.

---

## Skip / compress requests

When the user says "can we skip this?" / "is this act necessary?" / "这问题
有必要吗?":

### Script

1. State what the act's goal contributes to the final bundle in one sentence.
2. Offer the three options: full / compressed / default-pin.
3. Log the chosen path and continue.

### Example

```
User: 定调幕有必要吗？
Skill:
  这一幕只抓使用时刻 + why + 目标用户三件事。少了这些，第 ③ 幕
  的色彩和动效会默认落在"通用 SaaS"的中庸值，你开场提到的
  "反 shadcn" 会失效。
  三选一：
  A. 走完整定调（~2 分钟）
  B. 压缩到 3 问 1 表（~30 秒，我提问你短答）
  C. 跳过，我按你开场信息默认填，Act ⑤ 前你一票否决
```

### Never
Silently skip. Silent skipping is what produces the "technically correct but
missing the soul" outputs the original design.md was criticized for.
