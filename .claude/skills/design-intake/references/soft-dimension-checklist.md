# Soft-Dimension Checklist

The soft dimensions captured in Act ① + ② are what separate a Claude-
Design-ready bundle from a technical-looking-but-soulless one. v4.5 unlocks
this checklist from expert mode — every mode (`novice / guided / expert`)
runs it to completion.

## Contents
- [Why this is not expert-only](#why-this-is-not-expert-only)
- [The ten required dimensions](#the-ten-required-dimensions)
- [Tick format](#tick-format)
- [Mode-specific gathering style](#mode-specific-gathering-style)
- [When to declare a dimension "skipped-with-reason"](#when-to-declare-a-dimension-skipped-with-reason)

## Why this is not expert-only

Patricia sim (v4) surfaced that the soft-dimension checklist was locked to
expert fast-track, skipping it in guided / novice because "they'll naturally
cover it in narrative". They don't. Narrative covers half; half stays
implicit.

Explicit ticking forces every dimension to land somewhere in the artifact:

- Skipped dimension → `drop-silent` risk — the omission is invisible to
  the user, but Claude Design generation drifts to the category cliché on
  that axis.
- Narratively-covered dimension → the dimension exists in `design.md` prose
  but not in a checkable form. Downstream reviewers cannot verify.
- Ticked dimension → explicit field in `design.md` state with a source
  (act, turn, user's exact wording).

Every mode runs all ten. What changes is the **gathering style**, not the
coverage.

## The ten required dimensions

Tick all before exiting Act ②. If a dimension cannot be filled, mark
`skipped-with-reason` (see below) — do not silently advance.

| # | Dimension | Source act | Captured as |
|---|---|---|---|
| 1 | **use-moment** | ① | time + place + device + emotional state |
| 2 | **why / origin** | ① | one-paragraph origin that names a specific population / frustration / belief |
| 3 | **three-adjectives** | ② | three emotional-directional adjectives |
| 4 | **positive-references** | ② | 2-5 named artifacts (not brands — specific artifacts) |
| 5 | **anti-reference.hue** | ② | at least 1 hue-tier prohibition (empty set explicit, not silent) |
| 6 | **anti-reference.material** | ② | at least 1 material-tier prohibition |
| 7 | **anti-reference.copy** | ② | at least 1 copy-tier prohibition |
| 8 | **taboos** | ② | absolute prohibitions with violation-consequence |
| 9 | **cultural-coordinate** | ② | one or a mix of aesthetic lineage names |
| 10 | **differentiator** | ② | one-line "only we ___" statement |
| 11 | **psychological-journey** | ② | 3–5 stages, each with a feeling |

(Eleven dimensions; numbered 1–11 for addressability. "Ten required" refers
to the ten that always land; journey sometimes collapses to 2–3 stages for
simple products.)

## Tick format

Recorded in the intake state under `soft-dimensions`:

```yaml
soft-dimensions:
  use-moment:
    value: "ICU 3 a.m. night shift, 12-hour fatigue, reading 6 patients'
            vitals on a wall-mounted screen"
    ticked: true
    source: "act-1, turn 2"
    user-verbatim: "凌晨 3 点 / 夜班 12h / 一眼 6 病人 / 3 秒决策"

  why:
    value: "护士疲劳态 + 低照度 + 医疗后果 = 认知负荷必须最小化"
    ticked: true
    source: "act-1, turn 4"

  three-adjectives:
    value: ["专注", "冷静", "零情绪化"]
    ticked: true
    source: "act-2, turn 1"

  positive-references:
    value:
      - {name: "Bloomberg Terminal", reason: "交易员专注"}
      - {name: "航空 PFD", reason: "任务关键"}
    ticked: true

  anti-reference:
    hue:
      value: ["Epic/Cerner 办公蓝 #3B5998 类"]
      ticked: true
    material:
      value: ["Windows 98 凸起按钮", "iOS Health 温暖圆润"]
      ticked: true
    copy:
      value: ["Notion/Linear 'Great job!' 愉悦口吻"]
      ticked: true

  taboos:
    value:
      - "critical 告警闪烁（护士疲劳态禁）"
      - "任意 shadow"
    ticked: true

  cultural-coordinate:
    value: "ops-room × aviation cockpit"
    ticked: true

  differentiator:
    value: "其他医疗仪表盘降低信息密度让新手可用；我们提高密度让老手
            一眼看完"
    ticked: true

  psychological-journey:
    value:
      - {stage: "开班", feeling: "平静"}
      - {stage: "发现异常", feeling: "3 秒内锁定是谁"}
      - {stage: "dispatch 医生", feeling: "动作连贯没有 UI 卡顿"}
    ticked: true
```

Any dimension with `ticked: false` blocks exit from Act ②.

## Mode-specific gathering style

The style differs; the coverage does not.

### Expert (fast-track)

Three compressed questions surface all eleven dimensions at once. Expect
the user to volunteer most dimensions unprompted. See
`expert-fast-track.md § three-question compression`.

Tick by extraction from the user's opening paragraph. Confirm once via
a structured summary table; user corrects or assents.

### Guided

One question per dimension, 20–40 seconds each. Readback sandwich for the
ambiguous ones (three-adjectives, psychological-journey). Total time ~4–5
minutes for Act ②.

### Novice

One question per dimension, but each question uses reference pairs and A/B
options rather than open-ended prompts. Example:

Instead of "what's your brand's cultural coordinate?", ask:
> "如果要找一个美学参照——这两个里哪个近？
>   A. 北欧极简（冷静、留白、木色）
>   B. Y2K 电子（亮色、变形、躁动）"

Then follow up to nuance.

Total time ~6–8 minutes for Act ②. Novice users may need 2–3 passes on
some dimensions; that's expected. Don't rush — novice mode's whole value
is getting the soft dimensions right even if the user wouldn't have
articulated them alone.

## When to declare a dimension "skipped-with-reason"

Rare. Only when a dimension genuinely doesn't apply:

```yaml
soft-dimensions:
  anti-reference.copy:
    value: []
    ticked: false
    skipped-with-reason: "product is a non-text utility (PDF splitter);
                          no voice / tone layer"
```

### Valid skips

- Non-text utility products (no copy tier)
- Internal-only tools (psychological-journey may collapse to 2 stages:
  find, use)
- Replacement-for-existing-product retheming (use-moment may inherit from
  existing product, explicitly noted)

### Invalid skips (reject — ask again)

- "The user doesn't know" on differentiator — press harder; or pin a
  default.
- "Doesn't feel important" on taboos — the absence is itself information;
  tick as empty set with reason "no brand-level prohibitions at this
  stage".
- Skipping three-adjectives — never acceptable; every product has a feel,
  even if generic.

## Interaction with schema projection

Not every soft dimension maps to a schema field:

| Dimension | Schema target | Drop status |
|---|---|---|
| use-moment | `design.md § brand-soul` + drives viewport / motion defaults | drop-silent (narrative) |
| why | `design.md § brand-soul` | drop-silent (narrative) |
| three-adjectives | `design.md § brand-soul` | drop-silent (narrative) |
| positive-references | `design.md § references` | drop-silent (narrative) |
| anti-reference.hue | `design.md § anti-references` + token-lint if specific hex named | partial — hex drops, prose stays |
| anti-reference.material | `design.md § anti-references` + taboo → enforceable | mixed |
| anti-reference.copy | `design.md § voice-and-tone` only | drop-silent (schema has no voice surface) |
| taboos | enforceable — token-lint + `design.md § taboos` | mixed |
| cultural-coordinate | `design.md § brand-soul` | drop-silent |
| differentiator | `design.md § brand-soul` | drop-silent |
| psychological-journey | `design.md § brand-soul` + drives visual weight decisions in Act ③④ | drop-silent |

The drop-silent tags are expected and acceptable. Act ⑤'s schema projection
report makes the drops visible so reviewers know what lives in prose vs
in enforceable tokens.
