# Act ② — Anchors

Translate the brand's soul into coordinates the visual layer can anchor to:
three adjectives, positive references, anti-references (three tiers), cultural
coordinate, taboos, differentiator, and the psychological journey.

3–4 minutes target. Still no hex values. This is where the "soft dimensions"
that Act ③ will translate into tokens get captured — and where the bundle's
personality either survives or dies.

## Contents
- [What Act ② captures](#what-act--captures)
- [Three-adjective extraction](#three-adjective-extraction)
- [References — positive](#references--positive)
- [Anti-references — three tiers](#anti-references--three-tiers)
- [Taboos](#taboos)
- [Cultural coordinate](#cultural-coordinate)
- [Differentiator](#differentiator)
- [Psychological journey](#psychological-journey)
- [Readback and exit](#readback-and-exit)

## What Act ② captures

These ten fields must all be filled before exiting. The soft-dimension
checklist (see `soft-dimension-checklist.md`) runs in every mode — expert
fast-track does not skip these, only compresses the questioning.

```
three-adjectives: [<str>, <str>, <str>]
positive-references: [<product/film/place/era>, ...]   # 2-5 items
anti-references:
  hue:      [...]   # color-level things to avoid
  material: [...]   # texture / shape / finish things to avoid
  copy:     [...]   # voice / tone / word things to avoid
taboos: [...]       # hard prohibitions, stronger than anti-reference
cultural-coordinate: <str>   # aesthetic lineage (Swiss modern / Y2K rave /
                             # Nordic minimal / Showa-retro / etc.)
differentiator: <str>        # "only we ___"
why-psychological-journey:
  - stage: <str>, feeling: <str>
  - ...
```

## Three-adjective extraction

### Ask

> 用三个形容词描述这个产品应该让用户感觉到什么。

### Rules for accepting adjectives

- **Specific over generic** — "restrained" not "clean"; "stubborn" not "unique".
- **Emotional over descriptive** — "quiet" not "dark"; "acidic" not "green".
- **Directional over neutral** — "warm" is directional; "balanced" is a dodge.

### Reject / push back on

- Any of: *modern, clean, simple, elegant, minimal, beautiful, friendly*.
  These are default-tokens of the design cliché. Ask for the flavor inside
  them:
  > "干净" 有很多种——苹果那种克制的贵，无印良品那种温柔的空，还是
  > 瑞士设计那种数学的冷？

- Three adjectives that all live in the same axis (e.g., "warm, cozy, soft").
  Ask for at least one off-axis word to prevent flat brand expression.

### Test against exclusion
After the three are named, ask the inverse:
> 那么——如果有人描述你的产品是 <opposite of adjective 1>，你会觉得"错
> 得离谱"吗？

This confirms the adjective actually means something to them. If they shrug,
the adjective is decorative, not functional.

## References — positive

### Ask

> 列 2-5 个参照——可以是产品、电影、音乐专辑、一家店、一个时代。
> 它们让你觉得"ACIDLAB 该有那个感觉"。

### Press for specificity

"像 Apple" is useless. Ask:
> Apple 什么时期？iPhone 4 的玻璃金属，还是 Apple Music 的彩色渐变，还是
> HIG 的系统灰？

Write down the specific artifact, not the brand.

### Record with a one-line reason

```
- "Sigur Rós 'Takk' 专辑封面" → 冷、极简、留白、自然质感
- "Playdate 掌机界面" → 2-bit 色深、硬边像素、有限调色板
- "90 年代日本便利店 POS 机" → 橙底黑字、LCD 等宽、小票虚线分隔
```

Each reference should contribute a different axis. Five references all
pointing to "Scandinavian minimal" give the skill only one coordinate.

## Anti-references — three tiers

### Why tier

A flat anti-reference list treats "don't look like iOS" and "don't use iOS's
tone of voice" as the same rule. They're not. Downstream schema can enforce
hue-level prohibitions (no SF Blue) and material-level (no glass-morphism),
but copy-tier anti-references live in documentation only (see
`schema-projection.md § fallback-recipe-catalog`).

### The three tiers

| Tier | What's forbidden | Example |
|---|---|---|
| **hue** | color / palette / gradient choices | no gradient purple, no SF Blue #007AFF, no acid-house neon |
| **material** | texture / shape / finish / motion | no glass-morphism, no elevation shadows, no >4px radius, no bouncy spring motion |
| **copy** | voice / tone / word / punctuation | no "Great job!", no emoji, no "you got this", no Untitled placeholders |

### Ask per tier

```
色相禁区：有没有哪种颜色一看就让你觉得"不是我们"？
质感禁区：形状、圆角、阴影、动效——哪种一出现就是背叛？
文案禁区：哪种说话方式你不想让用户在这个 app 里看到？
```

If a user gives one anti-reference that spans tiers (e.g., "Notion"),
decompose it:
> Notion 你反三件事里哪个？是浅灰无边框（质感）、Inter 12px（typography）
> 还是 "Untitled" 空态（文案）？

Multi-tier anti-references get one entry per tier.

### Downstream handling
- `hue` + `material` → enforceable in `design.tokens.yaml` and gate-check
- `copy` → enforceable only in `design.md § voice-and-tone`; schema projection
  will mark as `drop-silent` with a `fallback-recipe` pointing back to the
  voice-and-tone doc

## Taboos

### What makes taboos different from anti-references

Anti-references describe the *region* you don't want to be in. Taboos are
absolute prohibitions with consequence-of-violation.

- Anti-reference: "not Material Design shadows"
- Taboo: "shadow never appears anywhere in this product"

### Ask

> 有没有什么——出现一次就 "这是 bug，修"？不是风格偏好，是禁令。

### Record

```
taboos:
  - "shadow anywhere (elevation communicated by 1px border + luminance shift)"
  - "any animation on critical alerts (fatigue risk in ICU)"
  - "purple in any form (no tenant override allowed to introduce purple)"
```

Taboos translate into gate-check or token-lint rules — they are enforceable.

## Cultural coordinate

### Ask

> 如果要给这个产品找一个文化坐标——哪个美学流派、哪个时代、哪个地区的
> 设计语言——它站在哪里？

### Why

Cultural coordinate anchors references that don't otherwise share vocabulary.
"Playdate + Unpacking + 便利店 POS" makes sense when the coordinate is
"cozy pixel retro". Without it, those three references look random.

### Accept one or a mix

```
cultural-coordinate: "Nordic minimal × East Asian wabi-sabi × cyber late-
  night" (Dusk)
cultural-coordinate: "Y2K rave flyer × 2001 MTV bumper × Dimes Square"
  (ACIDLAB)
```

A mix is fine if the user can articulate the intersection. "Modern" alone is
a default — push for an adjacent coordinate that anchors it.

## Differentiator

### Ask

> 同品类里，只有你们才 ___。填空一句话。

### Listen for

- A stance other competitors would struggle to take
- An opinion, not a feature
- Something that implies a visual consequence

### Example

- Dusk: "other meditation apps lower your anxiety with 'it'll be ok' —
  we sit in it with you."
- ACIDLAB: "other drop apps lower anxiety so you buy — we amplify FOMO
  because that's the point."

### Push back on

- "We're better at X" — better is relative to what, measured how?
- Anything that sounds like a roadmap bullet

## Psychological journey

### Ask

> 想象用户从第一次见到这个品牌到推荐给朋友。列 3-5 个阶段，每个阶段他
> 应该感觉到什么。

### Record

```
psychological-journey:
  - stage: "首次打开"
    feeling: "这 app 不是给我妈的"
  - stage: "用了 5 分钟"
    feeling: "它没想让我买东西，这很反常"
  - stage: "drop 倒计时"
    feeling: "拇指在屏幕上悬着出汗"
  - stage: "付款后"
    feeling: "自己很酷"
```

### Why

Downstream: the journey informs where to invest visual weight. If stage 3 is
the emotional peak, the countdown screen deserves the most dramatic typography
+ motion; login / settings can default.

## Readback and exit

Before advancing to Act ③, run a full anchor-sheet readback. Unlike Act ①'s
three-part sandwich, Act ② gets a structured summary:

```
三形容词 : <a>, <b>, <c>
正参照   : <1-3 most-load-bearing>
反参照   : hue=<>, material=<>, copy=<>
禁忌     : <1-3>
文化坐标 : <coord>
差异化   : <one line>
心理旅程 : <stage 1 → stage N, one phrase each>

→ 这些会变成第三幕色温、字阶、动效、第四幕元件状态的 default 出发点。
  有想修改的吗？
```

If the user accepts without changes, lock the anchor sheet and advance.

If the user makes one change, update and re-show. If two+ changes, pause
and ask whether the underlying adjectives / references are off — often
multiple small corrections mean one of the three adjectives is wrong.

## Common traps

- **Adjective drift into features** — user says "fast, scalable, reliable".
  Those are product qualities, not visual qualities. Ask for how the user
  should *feel*, not what the product *does*.
- **Reference monoculture** — all references from one category. Push for
  cross-domain references (one product + one film + one place).
- **Anti-reference without tier** — "not generic SaaS" — unusable without
  decomposition.
- **Fake differentiator** — "our UX is better" — rejected.
- **Journey without emotional arc** — if every stage feels the same, the
  user hasn't thought through stakes; press on stage 3.
