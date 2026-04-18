# Expert Fast-Track

Compressed Act ① + ② flow for expert-mode users: ~3 minutes total. Density
goes up, assumption depth stays the same as baseline — what changes is
**questioning style**, not **dimension coverage**. All ten soft dimensions
(see `soft-dimension-checklist.md`) must still tick before advancing.

## Contents
- [When to trigger](#when-to-trigger)
- [Three-question compression](#three-question-compression)
- [Readback as structured table](#readback-as-structured-table)
- [Post-readback soft-dimension tick check](#post-readback-soft-dimension-tick-check)
- [Skip-request handling](#skip-request-handling)
- [When to fall out of fast-track](#when-to-fall-out-of-fast-track)

## When to trigger

`expert-fast-track` activates when **all** of these hold:

- Mode decision (see `adaptive-dialog.md § mode-decision`) is `expert`
- User has volunteered ≥ 3 of the ten soft dimensions in the opening
  message (a one-paragraph self-intro that covers product, users, use-
  moment, and references counts as 4)
- User explicitly asks to compress ("让我们快一点" / "可以合并 ①②")
  OR the skill detects an opening paragraph that pre-answers ①②

If any condition fails, route to `guided` or full Act ① / ②.

## Three-question compression

Ask all three at once. Expect short answers.

### Template

```
我把 ①② 幕合并到 3 问。你可以短答，我整理：

Q1. 这个产品是什么 + 给谁 + 在什么时刻被打开？
    （一句话即可 — 不要列 feature）

Q2. 你最想让用户**反感**的参照是什么？
    （给 2-3 个，最好分别是色相级 / 质感级 / 文案级）

Q3. 如果这是个人，Ta 最**不能忍**的三件事？
    （用来抓 taboos + differentiator）
```

### Why these three

- **Q1** covers `use-moment`, `why` (implied through specificity), and
  audience anchoring in one shot.
- **Q2** forces anti-reference decomposition upfront — instead of asking
  three times (hue / material / copy), one question with structured
  expectation.
- **Q3** is the differentiator + taboo extractor. "最不能忍" captures both
  the user's stance and the lines Ta won't cross.

### What's deliberately missing

- **Three-adjectives** — inferred from Q1 + Q3 by the skill, confirmed in
  readback.
- **Positive references** — asked implicitly by "这个产品是什么样" —
  expert users volunteer them.
- **Cultural coordinate** — inferred from Q2 anti-references. User
  confirms in readback.
- **Psychological journey** — collapsed to the use-moment description
  (expert users often embed journey in their one-liner).

If the user's answers don't yield enough signal for the skill to infer these
five, fast-track fails → fall out to `guided` (see below).

## Readback as structured table

After three answers, present the inferred anchor sheet:

```
| 维度                      | 抓到的信息                                   |
|--------------------------|--------------------------------------------|
| product + use-moment     | <extracted>                                 |
| why                      | <extracted or inferred>                     |
| 三形容词                   | <inferred>, <inferred>, <inferred>          |
| 正参照                     | <extracted>                                 |
| 反参照.hue               | <extracted>                                 |
| 反参照.material          | <extracted>                                 |
| 反参照.copy              | <extracted or "<none given — ok if void>">  |
| 禁忌                       | <extracted>                                 |
| 文化坐标                   | <inferred>                                   |
| 差异化                     | <inferred>                                   |
| 心理旅程                   | <collapsed to use-moment or explicit>       |

对的继续，错的指出来。
```

### Approval mode

Expert-mode readback expects terse approval:
- `✅` / `对` / `go` / `correct` — advance
- Specific corrections — accept and re-present the affected rows
- Full rewrite of a row → treat as one rejection; two+ rejections on the
  readback trigger fall-out to `guided`

## Post-readback soft-dimension tick check

Run the tick-check even after the readback is approved:

```yaml
# all 11 dimensions must be ticked with value set
for dim in soft-dimensions:
  if dim.value is empty and dim.skipped-with-reason is not set:
    block advance; prompt specifically for this dimension
```

### Common post-readback gaps

- **copy-tier anti-reference missing** — expert users often skip this
  because it feels "non-design". Prompt: "文案层有没有什么**语气**你不
  想让 app 用？（emoji、'Great job!'、'Oops!' 这类）"
- **taboos confused with anti-references** — expert users frequently name
  preferences as taboos. Prompt: "刚才那条是禁令（出现即 bug）还是偏好
  （能避免更好）？"
- **psychological-journey collapsed too far** — if journey is just "use
  the app", probe: "用完之后用户应该留下什么感觉？推荐给谁？"

If any gap remains after one prompt-pass, the skill notes it and moves on
— do not over-extract from experts who gave enough signal elsewhere.

## Skip-request handling

Expert users sometimes ask to skip the readback entirely ("just give me the
tokens"). Negotiate:

```
我可以跳 readback，但有一条：我按当前理解填第 ③ 幕的 default，你 Act
⑤ 前必须看 sample-landing 的气质——如果气质不对，我回 Act ② 重填，整
个流程反而慢。

三选一：
  A. 10 秒 readback（只念 product + 3 adjective + differentiator 三行）
  B. 我跳 readback，Act ⑤ 前你看 sample 裁决
  C. 按完整 readback 走（~30 秒）
```

Most expert users pick A. Record the choice in state as `readback-mode:
compressed | deferred | full`.

## When to fall out of fast-track

Fast-track exits back to `guided` when:

1. **Negation density** — two rejections on the structured readback.
2. **Missing soft dimensions after one-prompt-pass** — ≥ 3 dimensions
   still untickable.
3. **User explicitly requests** — "let's slow down" / "actually let me
   think about this".
4. **Ambiguity density** — user's three answers contain > 2 terms the
   skill can't unambiguously parse.

### Fall-out script

```
切到 guided 模式——不是判断错了，而是现在多抓点信息下游会稳。我一条
一条问，每条 1 分钟。
```

Never frame fall-out as a mistake; frame as a gear change.

## Contract with gate-check

Fast-track does not change gate semantics. The five mechanical gates + the
two v4.5 additions (affordance, viewport-type) still run at Act ⑤ regardless
of how Act ①② were gathered. Over-reliance on fast-track inference without
gate enforcement is how v3 produced technically-sound bundles missing soul.

## Interaction with other references

- **`adaptive-dialog.md`** — fast-track is a shortcut through Act ①②; all
  dialog-style rules (readback sandwich, negation density, hard-value
  hiding) still apply at the appropriate moments.
- **`soft-dimension-checklist.md`** — the ten dimensions are authoritative.
  Fast-track compresses questioning, not coverage.
- **`gate-overrides.md`** — if fast-track pre-emptively declares an
  override (user's opening mentions "we need AAA contrast"), register the
  override immediately with full structured reason. Do not defer.
