# Act ① — Framing

Establish what the product is, who it's for, and in what moment it gets
opened. Two minutes target. No visual questions yet.

## Goal

Three things leave Act ① nailed:

1. **Product identity** — one sentence the user can say in the wild.
2. **Use moment** — concrete time, place, state-of-mind, device.
3. **Why (origin)** — what drove this to exist.

Everything downstream anchors to these three. A weak framing produces a
technically correct but soul-missing bundle.

## Opening line

Match the opening line to the mode decision (see `adaptive-dialog.md`):

### Novice
> 欢迎。我们用对话把你脑子里的"这个产品长什么样"变成一份 Claude Design
> 能直接上传的资产包。不懂设计没关系——我问你感受，你回答。先聊一聊你
> 想做什么吧。

### Guided
> 我们用 5 幕对话把品牌和视觉梳理成一个上传包。每幕我会回读一次确保我
> 没理解偏。先聊产品——它是什么、给谁、在哪个时刻被打开？

### Expert
> 5 幕对话 + 机械闸门 + schema projection。①② 可合并 3 分钟（fast-track
> 保留软维度 checklist）。产品一句话 + use moment + why，开始。

## Three core questions

Ask in order. Do not batch.

### Q1. Product identity

**Ask**:
> 一句话描述这个产品。它是个什么？

**Listen for**:
- Product category (app / tool / game / platform / …)
- Audience type implied by category
- Any positioning word ("indie", "enterprise", "cozy", "professional")

**Do not accept**:
- Lists of features ("it has X, Y, and Z")
- Marketing taglines ("reimagining the future of …")
- Long definitions

If the user gives features instead, redirect:
> Feature 先放一放。如果只能留一句话告诉陌生人这是什么，你会怎么说？

### Q2. Use moment

**Ask**:
> 谁会在什么时刻、什么地点、什么心情下打开它？

**Listen for** (record as structured `use-moment`):
- Time of day (literal — "3 a.m." is better than "night")
- Physical context (bed / desk / commute / clinic / gym)
- Device + posture (phone portrait single-hand / laptop split-screen / iPad
  on hospital cart)
- Emotional state (tired / excited / anxious / bored / focused)
- What they were doing 30 seconds before opening

**Why this matters**:
Use moment directly constrains color luminance, motion intensity, font size,
contrast tier, and interaction density. "ICU 3 a.m. night shift" produces
different tokens than "bus commute 8 a.m.".

**If the user says "all kinds of users"**:
> 你一个都描述不出来不行——我不是要你列用户画像，我要你给我**一个**具体
> 的人在**一个**具体的时刻。所有其他场景都从这一个派生。

### Q3. Why (origin)

**Ask**:
> 为什么你要做这个？不是 "market gap"，是你个人为什么非做不可。

**Listen for**:
- A specific frustration, observation, or belief the user holds
- An anti-stance (X exists but X is wrong because …)
- A population they feel unseen ("深夜失眠的人" / "独立开发者" / "凌晨 3
  点值班的护士")

**Do not accept**:
- Generic market-size answers
- "Because AI" / "because opportunity"
- Anything that could be said about a competitor

The Why becomes the first paragraph of `design.md § Brand & Soul`. It is what
prevents generation from drifting to the nearest category cliché.

## Readback before exiting

After Q1–Q3, use the three-part readback sandwich (see `adaptive-dialog.md
§readback-sandwich`):

```
我理解 X : <product identity + use moment + why in one sentence>
对应参数 Y : <2-3 downstream constraints this will drive — e.g.,
             "bg luminance ≤ 0.25 for night use", "motion duration ≥ 300ms
             for fatigued reads", "mobile portrait primary">
排除项 Z : <explicit "not this and not that" — typically the cliché of the
           category: "not Calm's sweet wellness", "not enterprise gray">
```

If the user rejects the readback, treat it as one negation. Second rejection
triggers negation-density flip (see `adaptive-dialog.md`).

## Exit conditions

Advance to Act ② only when all three fields are filled:

- `product.identity` — one sentence
- `use-moment` — time + place + device + emotional state
- `why` — specific, not generic

If the user pushes to skip framing ("can we jump to color?"):
> 这一幕的三个问题直接决定了后面色温、动效、字阶的默认值。少了这些，
> 我要么默认走中庸值（shadcn clone），要么 Act ⑤ 的样例会跑偏。三选一：
>  A. 完整 2 分钟走完
>  B. 压缩到 1 分钟（一问一答，我不回读）
>  C. 跳过，我按项目类型默认填，Act ⑤ 前你一票否决

Log the path chosen in the intake state.

## Common traps

- **Marketing-copy mode** — the user answers like they're writing a press
  release. Break it: "关掉 pitch，用人话。"
- **Feature drift** — the user keeps listing functionality. Park features to a
  separate note; Act ① is about identity, not scope.
- **Audience vagueness** — "everyone" / "general users". Force specificity.
- **Borrowed Why** — the Why sounds like it's from a VC deck. Ask a second
  time: "但你自己呢？"
- **Skipping use-moment entirely** — do not proceed. This is the single
  highest-leverage constraint and users underestimate it.
