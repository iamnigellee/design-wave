# Any other notes?

Paste the content below into the "Any other notes?" textarea on the
design-system setup page. These rules are the ones Claude Design cannot
infer from code alone — they are constraints on what the generated
system must *not* become.

---

## Brand stance

Dusk is a meditation app for insomniacs that deliberately refuses wellness
tropes. The brand's core move is honesty: it doesn't promise relief at
2 a.m. — it sits with the user. Treat any generated output that sounds
encouraging, warm, or solution-oriented as a drift from brand. The brand
adjectives are: **restrained · quiet · faintly bitter**.

## Use moment (drives every visual default)

One concrete user: 30-something urban professional, in bed, lights off,
iPhone portrait, single-hand, 2:30 a.m., physically exhausted but mentally
wired. This moment determines:

- dark is the primary mode (not a light/dark toggle — dark is canonical)
- motion duration floors at 200ms and prefers 400–600ms (nothing snappy)
- reduced-motion strategy is `remove`, not `reduce`
- display type at 40px on 375-wide viewport (32px read as "announcement")

## Positive constraints (must hold across all generated output)

1. **accent-as-signal-only.** The one accent color (`signal-flax #A89680`)
   appears only in primary CTAs, focus rings, error borders, and selected
   indicators. It must never appear in decoration, hero typography,
   illustration, body text, or background patterns. Decorative use of flax
   is the single most detectable drift.

2. **weights-restricted.** Typography weights are drawn only from {400, 500}.
   Weights 600, 700, and 900 are forbidden. Bold type speaks too loudly at
   2 a.m.

3. **material-policy: matte only.** No gloss, chrome, liquid, noise, or
   textural overlays. Surfaces are flat matte. Elevation is communicated
   by 1px border + 2–5% luminance step between surfaces — never by shadow.

## Taboos (absolute — violations are bugs)

- **No box-shadow anywhere.** Any component that renders with an elevation
  shadow is broken, regardless of how subtle.
- **No spinner on loading states.** Show three dots `···` instead. The
  spinner's circular animation is too busy for the use moment.
- **No affirmations.** "Great job", "You got this", "Well done", or any
  post-session encouragement is a taboo copy violation.

## Anti-references (three tiers)

### Color / hue

Forbidden: Calm-class pastel gradient greens, Headspace sunrise orange,
startup purple (`#7C3AED` family), "business navy" night-mode.

### Material / shape / texture

Forbidden: elevation shadows, gradient chrome, subtle sheen, glassmorphism,
radius > 4px, emoji illustrations.

### Copy / voice / tone

Forbidden: exclamation points in UI labels, emoji in UI, "Untitled"
placeholders, treatment phrases ("breathe in", "relax", "let it go",
"release"), any affirmation pattern.

## Voice & tone (for generated copy)

- Second person, present tense, declarative. Short sentences.
- No exclamation points. No emoji. No apology ("Sorry about that!").
- Specific time references: "3:14 a.m.", never "late at night".
- Neutral verbs: start / stop / return / leave. Never "begin your
  journey".
- Sessions end in silence. No post-session summary. Maybe a timestamp.

Sample microcopy, always acceptable:

- `Session` (not `Start Session`)
- `End` (not `Finish`, not `Done`)
- `Sign out` (not `See you tomorrow!`)
- `3:14 a.m.` (not `Now`)

## Semantic counter-intuitions

In Dusk's token map, `bg.surface` is *darker* than `bg.canvas`
(neutral-950 vs neutral-900). Cards recede into the night, not out of it.
This inverts the usual "surface is lighter than canvas" convention and
is load-bearing — do not normalize.

## What Claude Design cannot generate (leave to humans)

- **Meditation content** (session audio, voice scripts) — out of scope.
- **Timestamp microcopy** in UI — needs minute precision ("2:34 a.m."),
  not relative ("a moment ago"). Human writers enforce.
- **Reserved palette change.** The accent `signal-flax #A89680` may
  mutate to "deep cold teal" within 14 days of launch if user testing
  reveals flax reads too warm. If so, the system re-uploads as v1.1.

## On shadows, one more time

The temptation to add a subtle shadow is the most common drift in generated
dashboards and cards. Before accepting any generated component, check the
computed styles for `box-shadow` — if any value other than `none` appears,
reject and re-prompt with "no box-shadow anywhere; elevation via border
only".
