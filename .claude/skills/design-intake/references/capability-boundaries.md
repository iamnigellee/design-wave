# Capability Boundaries

Claude-the-intake-skill has real limits. This file is the single source of
truth for what the skill **cannot produce** and the structured degradation
responses for each boundary. When a user pushes past a boundary, run the
script — do not improvise.

## Contents
- [The principle](#the-principle)
- [Capability matrix](#capability-matrix)
- [Degradation scripts](#degradation-scripts)
- [Recording boundaries in the bundle](#recording-boundaries-in-the-bundle)
- [Adding new boundaries](#adding-new-boundaries)

## The principle

Never pretend to have a capability the skill lacks. Two failure modes:

1. **False acceptance** — skill says yes, produces something close-but-wrong
   or stalls. User loses trust and time.
2. **Cold refusal** — skill says "no" without offering a path forward. User
   leaves with nothing.

The degradation script threads these: acknowledge the limit, explain what's
possible, propose an alternate artifact the skill CAN produce, route the
rest to the post-upload manual step.

ACIDLAB sim ("can you spec the liquid chrome effect?") and BENTO sim ("can
you produce .aseprite?") validated this approach — honest boundary + path
forward earned both users' trust.

## Capability matrix

### What the skill CAN produce

| Artifact | Format | Quality |
|---|---|---|
| Design tokens | `design.tokens.yaml` | full |
| Design prose | `design.md` | full |
| Sample HTML (static) | `sample-*.html` with inline CSS or `<style>` | demonstration quality |
| Palette file (text) | `.gpl` (GIMP), `.json`, CSS variables, Tailwind config | full |
| Terminology map | `terminology-map.md` | full |
| Upload checklist | `upload-checklist.md` with JSON blocks | full |
| SVG (simple) | inline svg, path strings, rect/circle/line | simple shapes only |

### What the skill CANNOT produce

| Artifact | Reason | Degradation |
|---|---|---|
| `.aseprite` | binary format; requires Aseprite application | propose `.gpl` + import guide |
| `.ase` (Adobe swatch exchange) | binary format | propose `.json` + instructions |
| Raster spritesheets (PNG) | requires pixel manipulation runtime | propose `.gpl` + external tool recommendation |
| WebGL / shader source (.glsl) | shader programming skill exceeds intake scope | CSS `conic-gradient` fallback |
| Framer Motion / Lottie animations | runtime artifacts, not tokens | CSS keyframes for simple cases |
| Figma files (.fig) | proprietary binary | `figma-tokens.json` for tokens-plugin import |
| Videos / GIFs | media generation exceeds scope | static sample HTML + motion timing-fn spec |
| Actual photography / illustration | content, not system | describe in `design.md § imagery` for downstream designers |
| Typography design (new glyphs) | font design exceeds scope | recommend vendor + list required weights |
| Icon set design | icon design exceeds scope | recommend icon font / library + usage rules |
| Functioning React / Vue / Svelte components | code generation varies by framework | provide token mapping + CSS, leave component authoring to implementer |

## Degradation scripts

Run the script verbatim when a user requests a boundary-crossing artifact.

### Script A — Binary design-tool file requested

Triggered by: `.aseprite`, `.ase`, `.sketch`, `.fig`, any binary design format.

```
我做不到直接产出 <format>——它是 <原因：binary / proprietary / requires
a running <app>>. 但有一条最稳的路径：

我给你：
  ✅ <textual substitute>（包含全部颜色信息）
  ✅ 一份"如何导入 <app>"的逐步指引（我会写在 upload-checklist.md 里）

你拿到后：
  1. <step 1 in the target app>
  2. <step 2>
  3. <outcome>

全程不会丢信息，除了 <specific metadata the text format can't carry, if any>。
接受这条路径吗？
```

Example (BENTO `.aseprite` request):

```
我做不到直接产出 .aseprite —— 它是 Aseprite 的 binary 格式。但我给你
.gpl（GIMP palette，纯文本）：

→ 你拿到 .gpl 后：
  1. 打开 Aseprite
  2. Palette 面板 → More Options → Load palette
  3. 选 .gpl 文件
  4. palette 全部颜色一键导入，顺序保持

全程不会丢信息。接受吗？
```

### Script B — Shader / runtime-animation requested

Triggered by: liquid metal, smoke, fire, particle systems, parallax, physics-based motion.

```
这个效果 (<name>) 需要 <WebGL / shader / JS runtime>，不是 token 能
描述的东西。Skill 的能力在这里。

我能做到的降级路径：

1. 在 tokens 里写一个 <CSS fallback> —— 效果大约是真实的 <percentage>%
2. 在 design.md 的 § out-of-schema 段写明："真实的 <effect name> 需要
   <tool / technique>，建议从 <vendor / open-source source> 获取
   .<format>，在 <framework> 层挂载，不纳入 token 系统"
3. 上传后手动接入，在 upload-checklist.md 里标红

这样 Claude Design 生成的页面不会完全丢掉这个效果的意图——会有 fallback
视觉，配套文档告诉团队怎么补齐真实效果。

接受吗？
```

### Script C — Content (photography, illustration, copy) requested

Triggered by: "can you write the landing page copy?", "can you design the
hero illustration?"

```
Skill 做设计**系统**，不产内容。landing page 的 hero copy 或者插画是内
容层，要另外找 copywriter / illustrator 做。

但 Skill 可以：
  ✅ 在 design.md 的 § imagery / § voice-and-tone 里写清楚：文案应该是什
     么语气（你在 Act ② 抓的 copy-tier 反参照现在起作用）、插画应该什么
     风格、禁用什么
  ✅ 在 sample HTML 里用占位符 + 位置 + 尺寸约束，让后续内容直接套进去

content brief 要做吗？
```

### Script D — Scope creep into implementation

Triggered by: "can you build the React component for me?", "generate the
Tailwind config for my whole app".

```
我做 design system 的**定义**，不做具体 framework 的**实现**。原因：
  - 定义是跨 framework 的（React / Vue / Svelte 都能吃同一份 token）
  - 实现每个 framework 细节不同，我给不全，还会误导

我能给你：
  ✅ tailwind.config.js（token → utility 映射）
  ✅ CSS variables 全量文件
  ✅ 组件规格（每个 component 的 anatomy / state / variant 完整定义）
  ✅ 一份"如何在 React / Vue / Svelte 里消费 tokens"的通用 pattern 指引

剩下的 framework-specific 组件开发留给实现侧。这个分工对吗？
```

## Recording boundaries in the bundle

When a boundary is hit and a degradation accepted, record it:

### In `design.tokens.yaml`

Under the affected token or section:

```yaml
material.liquid:
  capability-boundary:
    cannot-produce: "shader source .glsl"
    fallback-applied: "conic-gradient"
    fallback-quality: "~30% of real effect"
    external-resource: "shader-gradient.com"
```

### In `design.md`

Under `§ capability-boundaries`:

```markdown
## Capability Boundaries

The following were requested but cannot be produced by the intake. Each has
a degradation path applied:

- **Liquid chrome effect** — fallback: conic-gradient approximation. Real
  effect requires WebGL shader, see `shader-gradient.com`.
- **.aseprite palette file** — fallback: `.gpl` text palette + import
  guide. Quality: equivalent (no information loss).
```

### In `upload-checklist.md`

Red-flagged as post-upload manual action:

```markdown
### Post-Upload Manual Actions

🔴 Liquid chrome — after Claude Design publishes, integrate shader source
   at hero component level. See `design.md § capability-boundaries`.
```

## Adding new boundaries

When a novel capability gap is encountered during an intake:

1. During the intake, run the generic degradation script template
   (acknowledge limit + propose fallback + route post-upload).
2. After the intake completes, add the new case to the capability matrix
   above with its degradation script.
3. Include one or two example user phrasings that trigger the boundary —
   this helps future intakes recognize the pattern faster.

Do not add hypothetical boundaries — only real ones encountered in real
intakes. A thick speculative list rots; a focused empirical list stays
useful.
