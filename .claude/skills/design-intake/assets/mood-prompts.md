# Mood Prompts

Static reference used by `act-2-anchors.md` when users stall on abstract
brand-feel questions. Not emitted in the bundle. The skill reads this file
only when a stall is detected or when the user explicitly asks for options.

## Contents
- [20 emotion-word cards](#20-emotion-word-cards)
- [Reference-pair decks by axis](#reference-pair-decks-by-axis)
- [Use-moment archetype prompts](#use-moment-archetype-prompts)
- [Cultural-coordinate starters](#cultural-coordinate-starters)
- [Anti-reference priming](#anti-reference-priming)

## 20 emotion-word cards

When a user can't produce three adjectives, offer four cards of five each
and ask them to pick three across the grid. Never offer all 20 at once —
decision fatigue kills the exercise.

### Card A — temperature
`冷静 · 克制 · 温润 · 锋利 · 柔和`

### Card B — stance
`固执 · 轻盈 · 诚恳 · 狡黠 · 庄重`

### Card C — texture
`粗粝 · 细腻 · 干净 · 凌乱 · 手工`

### Card D — intent
`招摇 · 隐匿 · 陪伴 · 挑衅 · 记录`

Pairing rule: if three picks all come from one card, the skill should nudge
for one off-axis word to prevent single-axis brand expression.

## Reference-pair decks by axis

Used when a user's stated "I want it clean" needs disambiguation. Offer
A vs B. The user picks; the skill infers a whole cluster.

### Axis — calm vs alert
- A: Calm / Headspace (aerated, warm, soft)
- B: Linear / Stripe Dashboard (clinical, cool, compressed)

### Axis — artful vs operational
- A: Are.na / Readymag (editorial, curated, asymmetric)
- B: Notion / Airtable (grid, functional, neutral)

### Axis — restrained vs expressive
- A: Apple.com (quiet, typography-led, whitespace)
- B: MSCHF / Tonal (typographic shouting, aggressive crops)

### Axis — cozy vs cold
- A: Stardew Valley UI (warm palette, rounded bitmap)
- B: Playdate system (monochrome, hard pixel, sparse)

### Axis — retro vs contemporary
- A: 90s Japanese POS (orange + black, LCD, dashed)
- B: Arc browser (frosted, pastel, playful)

### Axis — editorial vs utility
- A: The New York Times (magazine-grid, serif, dateline)
- B: Google Material (card-grid, sans, FAB)

## Use-moment archetype prompts

When a user struggles to specify a use moment, offer five archetypes. The
user can pick closest + modify, or say none fit.

1. **Night-table** — bed, dark room, tired, one-handed, phone portrait
2. **Commute** — public transit, interrupted, thumb-only, short sessions
3. **Desk-work** — office light, laptop, split attention, longer sessions
4. **Workshop / studio** — workspace, two screens, focus mode, makers' tools
5. **On-call / dispatch** — under duress, wall-mount or iPad, glance-read,
   consequence-of-misread

Downstream: each archetype pre-fills defaults for viewport, motion duration
range, contrast floor, and information density. Users often start from
an archetype and adjust one dimension.

## Cultural-coordinate starters

Offer when "cultural coordinate" returns "I don't know what you mean by that".

- **Swiss modernism** — grid, sans, asymmetric balance, typography-as-content
- **Japanese MA / 間** — negative space as subject, vertical composition,
  soft materials
- **Y2K rave** — acid colors, distorted serif, chrome, early-internet flyer
- **Nordic minimal** — muted naturals, unembellished typography, wood/stone
- **Brutalist web** — raw defaults, system UI, pixel-perfect offsets
- **Showa retro** — 60s–80s Japanese commercial, warm neons, LCD typefaces
- **Corporate Memphis** — flat vector people, primary shapes, startup
  illustration cliché (typically invoked as anti-reference)
- **Dimes Square / downtown NYC** — off-black, serif revival, deliberately
  amateur

Users may combine. ACIDLAB's "Y2K rave × 2001 MTV × Dimes Square" is a
legitimate combined coordinate.

## Anti-reference priming

When users give positive references but can't name anti-references, prime
with the common traps:

### Category clichés (ask: are any of these what you'd *dread* being seen as?)

- **Meditation / wellness** — dread cliché: pastel gradients, serif quotes,
  emoji buttons
- **Enterprise SaaS** — dread cliché: generic blue + white, stock
  illustrations, "Great job!" empty states
- **Fintech** — dread cliché: teal/navy, "your money, simplified", big
  numbers with arrows
- **Dev tools** — dread cliché: monospace body text, gradient accents,
  "Open source" badge, CLI mockup
- **Crypto** — dread cliché: neon purple, geometric abstractions, chrome
- **Medical** — dread cliché: Windows 98 gray-blue, serif "professional",
  stock doctor photos
- **Game companion app** — dread cliché: achievement badges, leaderboard
  first screen, Discord-inspired blurple
- **Media** — dread cliché: Inter-everywhere, card-grid-homepage, dark-
  mode-as-afterthought

Offer 2–3 relevant clichés; let the user reject, accept, or add.

### Tier reminders

After the user lists anti-references, prompt to decompose into three tiers
if any single entry spans multiple levels:

- "Did you mean Notion's *color palette*, its *visual texture*, or its
  *voice*?"
- "iOS the color system, the material finish, or the copy style?"

## When not to use this file

- The user already gave enough references / anti-references unprompted.
  Stop priming — it adds noise.
- The user is in expert-fast-track mode and giving direct parameter
  answers. Priming breaks the compressed flow.
- The skill has already cycled three prompts on the same dimension
  without convergence. At that point, pin a default and move on
  (`adaptive-dialog.md § stall-breakers § default-pin`).
