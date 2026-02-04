# Prompting Best Practices

Best practices for writing effective image generation prompts with `gpt-image-1.5`.

## Prompt Structure

Use a consistent order: scene/background -> subject -> key details -> constraints -> output intent.

Include the intended use (ad, UI mock, infographic) to set the model's mode and polish level. For complex requests, use short labeled lines instead of a long paragraph.

## Specificity

- Name materials, textures, and visual medium (photo, watercolor, 3D render)
- For photorealism, include camera/composition language (lens, framing, lighting)
- Add targeted quality cues only when needed (film grain, macro detail)
- Avoid generic buzzwords ("8K", "ultra HD", "award-winning")

## Avoiding Tacky Outputs

Do not use vibe-only terms ("epic", "cinematic", "trending", "artstation") unless the user explicitly wants that look.

Specify restraint instead:
- "minimal", "editorial", "premium", "subtle"
- "natural color grading", "soft contrast"
- "no harsh bloom", "no oversharpening"

Add a short negative line when needed:
```
Avoid: stock-photo vibe; cheesy lens flare; oversaturated neon; excessive bokeh; clutter
```

## Composition and Layout

- Specify framing and viewpoint (close-up, wide, top-down)
- Specify placement ("logo top-right", "subject center-left")
- Call out negative space if room is needed for UI or text overlays

## Constraints and Invariants

- State what must NOT change: "keep background unchanged"
- For edits: "change only X; keep Y unchanged"
- Repeat invariants on every iteration to reduce drift

## Text in Images

- Put literal text in quotes or ALL CAPS
- Specify typography: font style, size, color, placement
- Spell uncommon words letter-by-letter if accuracy matters
- Require verbatim rendering, no extra characters

## Multi-Image Inputs

- Reference inputs by index and role: "Image 1: product, Image 2: style"
- Describe how to combine them: "apply Image 2's style to Image 1"
- For compositing, specify what moves where and what stays unchanged

## Iteration Strategy

- Start with a clean base prompt, then make small single-change edits
- Re-specify critical constraints when iterating
- For edits, repeat invariants every time

## Quality vs Latency

- Fast iteration: `quality=low`
- Text-heavy or detail-critical: `quality=high`
- Strict edits (identity/layout lock): `input_fidelity=high`

## Use-Case Tips

### Generate

| Use Case | Key Tips |
|----------|---------|
| photorealistic-natural | Photography language; real texture (pores, fabric wear); avoid staging |
| product-mockup | Clean silhouette; label clarity; verbatim text rendering |
| ui-mockup | Real product look; layout/hierarchy focus; avoid concept-art language |
| infographic-diagram | Define layout flow; label parts explicitly; `quality=high` |
| logo-brand | Simple, scalable; strong silhouette; balanced negative space |
| illustration-story | Concrete actions per panel; restate character traits for continuity |
| stylized-concept | Name finish (matte, ink, clay); add "Avoid" line for tacky effects |
| historical-scene | State location/date; constrain clothing, props, environment to era |

### Edit

| Use Case | Key Tips |
|----------|---------|
| text-localization | Change only text; preserve layout and typography |
| identity-preserve | Lock face/body/pose; `input_fidelity=high` if likeness drifts |
| precise-object-edit | Specify exactly what to remove/replace; preserve surrounding texture |
| lighting-weather | Change only environmental conditions; keep geometry unchanged |
| background-extraction | Transparent bg; crisp silhouette; no halos; preserve labels |
| style-transfer | Specify style cues to keep; add "no extra elements" |
| compositing | Match lighting/perspective/scale; keep background unchanged |
| sketch-to-render | Preserve layout/proportions; add materials and lighting; no new elements |

## Where to Find Recipes

For copy-paste prompt specs, see `references/sample-prompts.md`. This file focuses on principles and patterns.
