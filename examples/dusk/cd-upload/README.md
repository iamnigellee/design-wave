# cd-upload/ — Claude Design form-field mapping

Everything here is organized to match the Claude Design **"Set up your
design system"** setup page exactly. Each file or folder maps to one
field on that form.

## Field map

| Form field | This bundle |
|---|---|
| **Company name and blurb** (textarea) | `blurb.txt` — paste verbatim |
| **Link code on GitHub** (URL) | _(skip — we use "from your computer" instead)_ |
| **Link code from your computer** (folder drop) | `design-system/` — drop the whole folder |
| **Upload a .fig file** | _(Dusk has no Figma file; skip)_ |
| **Add fonts, logos and assets** (file drop) | _(Dusk has no custom fonts or logo yet — skip; add if you have them)_ |
| **Any other notes?** (textarea) | `notes.md` — paste verbatim |

## What to do, step by step

1. Open [Claude Design](https://claude.ai/design) → switch to your
   organization → start design-system setup.
2. **Company name and blurb**: open `blurb.txt`, copy the whole file,
   paste into the textarea.
3. **Link code from your computer**: drag the `design-system/` folder
   into the drop zone. Per the form's note, Claude copies selected files;
   the whole folder isn't uploaded. See `design-system/README.md` for
   the suggested reading order Claude will apply.
4. Skip `.fig` and asset upload fields (Dusk has no Figma file or custom
   logo in v1.0).
5. **Any other notes?**: open `notes.md`, copy everything below the
   `---` separator, paste into the textarea. These are the rules Claude
   Design cannot infer from the code alone (brand stance, taboos,
   positive constraints, voice-and-tone).
6. Submit the form. Claude Design will analyze and produce a generated
   UI kit for review.

## After generation

Claude Design will produce an initial design-system preview including
color palette, typography, components, and layout patterns. Follow the
post-upload audit plan in [`../upload-checklist.md`](../upload-checklist.md)
to verify the five drop-silent predictions:

1. `signal-flax` usage restricted to CTA / focus / error / selected
2. No box-shadow anywhere in generated surfaces
3. Loading states show dots, not spinners
4. nav-item selected indicator is a left bar (not bottom underline)
5. Copy voice matches Dusk's declarative restraint (no affirmations,
   no exclamations)

Any drift on these five is expected data — record it and push back in
the Remix chat, or surface the drift in the design-intake skill's
`references/schema-projection.md` for future calibration.

## The rest of `examples/dusk/`

The parent `examples/dusk/` directory contains the **team-internal**
bundle artifacts:

- `design.md` — full brand narrative + all tokens + all constraints
- `design.tokens.yaml` — the intake skill's machine spec (passes
  gate-check.py and token-lint.py)
- `assets/sample-*.html` — identical content to `cd-upload/design-system/
  landing.html` and `journal.html` (this folder's copies exist so the
  upload bundle is self-contained)
- `upload-checklist.md` — the post-upload audit and validation plan
- `terminology-map.md` — Claude Design category ↔ bundle section map

Those files are for your team's review and archive. Claude Design's form
does not accept them directly — the only paths into CD are the five
form fields above.
