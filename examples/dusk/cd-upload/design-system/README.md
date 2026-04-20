# Dusk Design System

Drop this folder into Claude Design's **"Link code from your computer"**
field on the setup page. Claude will select and copy files from here;
the whole folder does not transfer, per the form's guidance.

## Contents

```
design-system/
├── tokens.css         CSS custom properties — primary source of truth
├── tokens.json        Design-token JSON (W3C DTCG schema) — machine-readable
├── components.html    All six components × all states (exhaustive showcase)
├── landing.html       Hero page — brand-feel signal (strongest input)
├── journal.html       Dashboard-class second surface
└── README.md          this file
```

## Reading order (for Claude Design's ingestion)

1. **`landing.html`** — brand feel, use-moment emotional anchor.
2. **`journal.html`** — information-dense second surface; nav-item with
   left-bar indicator, card hover without shadow, form-row.
3. **`components.html`** — exhaustive state matrix. Every component in
   every state, with in-file state-labels.
4. **`tokens.css`** — authoritative token names and values. CSS custom
   properties with `--neutral-*`, `--bg-*`, `--fg-*`, `--signal-flax`,
   type scale, spacing, motion, focus-ring.
5. **`tokens.json`** — same tokens in W3C design-token format; mirrors
   tokens.css.

## Brand rules embedded in this folder (non-obvious ones)

- **Dark is primary**, not a variant. No light-mode variant is included.
- **`--signal-flax` (#A89680) appears only in CTA / focus / error /
  selected indicator.** Decoration use is forbidden.
- **No box-shadow anywhere.** Elevation is communicated by 1px border +
  2–5% luminance step between `--bg-canvas` (#121110), `--bg-surface`
  (#0A0908 — darker), and `--bg-elevated` (#1C1A16 — lighter). Cards
  recede into the night.
- **Typography weights are 400 and 500 only.** Bolder weights (600 / 700
  / 900) are forbidden.
- **Loading state shows three dots `···`, never a spinner.** See
  `.btn-loading` in components.html.
- **Radius caps at 4px.** Larger values forbidden.
- **Material is matte only.** No gloss / chrome / liquid / noise.
- **nav-item selected indicator is a 2px LEFT bar** — not the more common
  bottom underline.

## Font loading note

The design uses `Söhne` as the primary family with `Inter` as fallback
and system sans as final. Neither is self-hosted here; the stack expects
the host browser to have either Söhne or Inter installed, or fall back
to the system default. The choice is sans-serif with a neutral voice —
any similar family renders acceptably.

## Not in this folder

- **No logos.** Dusk has not finalized a logo for v1.0 (Roadmap item).
  If you have a logo SVG, add it to the "Add fonts, logos and assets"
  field on the setup page.
- **No images / illustrations.** The brand forbids illustrations.
- **No Figma file.** The design was born in code. If a team member
  produces a `.fig` later, upload via the "Upload a .fig file" field.
