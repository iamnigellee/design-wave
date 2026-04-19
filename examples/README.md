# examples/

Real, validated bundles produced by the `design-intake` skill. Each
subdirectory is a complete Claude Design upload set. Use them as:

- **Reference bundles** — what the skill actually emits for a given persona
- **Schema-projection calibration tests** — upload to Claude Design and
  verify the skill's drop-silent / drop-warn predictions against real
  ingestion behavior
- **Worked examples** — for teams onboarding to the skill and wanting a
  concrete shape before running their own intake

## Index

| Bundle | Brand type | Primary aesthetic stress-test |
|---|---|---|
| [`dusk/`](./dusk/) | Meditation app for insomniacs | Restrained dark; signal-only accent; negative rules (no shadow, no spinner, no warmth); voice-and-tone drop-silent |

_(More personas available from the sim corpus: ACIDLAB [Y2K maximalist
e-commerce], VitalBoard [medical multi-tenant AAA], BENTO.EXE [indie pixel
game]. Fully-built bundles for those are roadmap items — ask the skill's
maintainer if needed.)_

## Anatomy of a bundle

Every bundle contains exactly six files:

```
<bundle>/
├── design.md                  brand soul + tokens narrative + positive
│                              constraints + anti-references + voice-and-
│                              tone + roadmap
├── design.tokens.yaml         machine spec; passes gate-check.py and
│                              token-lint.py
├── assets/
│   ├── sample-landing.html    brand-feel hero page (strongest upload signal)
│   └── sample-dashboard.html  component + layout exerciser
├── upload-checklist.md        4-step Claude Design flow + gate-check JSON +
│                              schema-projection report + post-upload audits
└── terminology-map.md         Claude Design categories ↔ bundle sections
```

## Validating a bundle locally

From the repo root:

```bash
python3 .claude/skills/design-intake/scripts/gate-check.py examples/<bundle>/design.tokens.yaml
python3 .claude/skills/design-intake/scripts/token-lint.py examples/<bundle>/design.tokens.yaml
```

Expect `decision: advance` on gate-check and `decision: pass` on token-lint
for all committed bundles. Any new bundle added here must pass both before
merge.

Sample pages render in any modern browser with no dependencies:

```bash
open examples/<bundle>/assets/sample-landing.html
open examples/<bundle>/assets/sample-dashboard.html
```

## Using a bundle for Claude Design upload

1. Follow the bundle's own `upload-checklist.md` step-by-step.
2. After Step 4 (publish), perform the post-upload audits listed in the
   checklist — these are the schema-projection verifications.
3. Record any drift in the organization's internal tracker so future
   bundles can tighten their fallback recipes.

## Calibration feedback loop

The drop-silent claims in each bundle's `upload-checklist.md § schema-
projection-report` are predictions. If actual Claude Design ingestion
behavior differs, the claims need updating. Feedback flow:

1. Upload the bundle.
2. Generate pages via the three brand-specific test prompts.
3. Note each drop-silent claim where the generated output *did* carry the
   intent (i.e., the field did not actually drop silent) or where an
   eaten claim drifted.
4. Open an issue (or edit `.claude/skills/design-intake/references/
   schema-projection.md`) with the delta — category-of-field + observed
   behavior + evidence snippet.

The skill's drop-silent catalog is based on current Claude Design behavior;
it will evolve as the schema expands. See `references/schema-projection.md
§ regression-watch`.

## Why the first bundle is Dusk

Dusk was chosen as the first example because its schema coverage is the
simplest (no material composites, no per-tenant overlay, no pixel
rendering) **while** its brand rules are sharp enough to surface a
meaningful number of drop-silent items:

1. `accent-as-signal-only` — meta-rule across tokens
2. `shadow.policy: forbidden` — negative rule
3. `button.loading.content: dots` — state-subtype
4. `nav-item.selected-indicator: left bar` — non-default shape + position
5. Voice & Tone — entire schema-less category

An upload test on Dusk tells us how well the simple cases are projected
before attempting maximalist or pixel bundles with ten times more extensions.
