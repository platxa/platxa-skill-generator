# Sample Prompts

Copy-paste prompt recipes organized by use case. Keep user-provided requirements; do not invent new creative elements. For prompting principles, see `references/prompting-guide.md`.

## Generate

### photorealistic-natural
```
Use case: photorealistic-natural
Primary request: candid photo of an elderly sailor on a fishing boat adjusting a net
Scene/background: coastal water with soft haze
Subject: weathered skin with wrinkles and sun texture; calm dog on deck
Style/medium: photorealistic candid photo
Composition/framing: medium close-up, eye-level, 50mm lens
Lighting/mood: soft coastal daylight, shallow depth of field, subtle film grain
Materials/textures: real skin texture, worn fabric, salt-worn wood
Constraints: natural color balance; no retouching; no watermark
Avoid: studio polish; staged look
Quality: high
```

### product-mockup
```
Use case: product-mockup
Primary request: premium product photo of a matte black shampoo bottle
Scene/background: clean studio gradient from light gray to white
Subject: single bottle centered with subtle reflection
Style/medium: premium product photography
Composition/framing: centered, three-quarter angle, generous padding
Lighting/mood: softbox lighting, clean highlights
Constraints: no logos or trademarks; no watermark
Quality: high
```

### ui-mockup
```
Use case: ui-mockup
Primary request: mobile app UI for a farmers market with vendors and specials
Scene/background: clean white background
Subject: header, vendor list, "Today's specials" section, location and hours
Style/medium: realistic product UI
Composition/framing: iPhone frame, balanced spacing
Constraints: practical layout, clear typography, no watermark
```

### infographic-diagram
```
Use case: infographic-diagram
Primary request: infographic of an automatic coffee machine flow
Scene/background: clean, light neutral background
Subject: bean hopper -> grinder -> brew group -> boiler -> water tank -> drip tray
Style/medium: clean vector-like infographic with callouts and arrows
Composition/framing: vertical poster, top-to-bottom flow
Text (verbatim): "Bean Hopper", "Grinder", "Brew Group", "Boiler", "Water Tank", "Drip Tray"
Constraints: clear labels, strong contrast, no watermark
Quality: high
```

### logo-brand
```
Use case: logo-brand
Primary request: logo for "Field & Flour", a local bakery
Style/medium: vector logo mark; flat colors; minimal
Composition/framing: centered on plain background with padding
Constraints: strong silhouette; balanced negative space; no gradients; no watermark
```

### stylized-concept
```
Use case: stylized-concept
Primary request: cavernous hangar interior with support beams and drifting fog
Scene/background: industrial hangar, deep scale, light haze
Subject: compact shuttle, parked center-left, bay door open
Style/medium: cinematic concept art, industrial realism
Composition/framing: wide-angle, low-angle
Lighting/mood: volumetric light rays through fog
Constraints: no logos; no watermark
```

## Asset Type Templates

### Website hero
```
Use case: <slug>
Asset type: landing page hero
Primary request: <description>
Style/medium: <photo/illustration>
Composition/framing: wide; negative space on <side> for headline
Lighting/mood: <lighting>
Constraints: no text; no logos; no watermark
```

### Game environment
```
Use case: stylized-concept
Asset type: game environment concept art
Primary request: <biome/scene>
Scene/background: <location + set dressing>
Style/medium: cinematic concept art
Composition/framing: <wide/establishing>; <camera angle>
Lighting/mood: <time of day>; volumetric
Constraints: no logos; no watermark
```

### Logo
```
Use case: logo-brand
Asset type: logo concept
Primary request: <brand idea>
Style/medium: vector logo mark; flat colors; minimal
Composition/framing: centered; clear silhouette; generous margin
Color palette: <1-2 colors>
Text (verbatim): "<exact name>" (if needed)
Constraints: no gradients; no mockups; no 3D; no watermark
```

## Edit

### background-extraction
```
Use case: background-extraction
Input images: Image 1: product photo
Primary request: extract the product on a transparent background
Output: transparent background (RGBA PNG)
Constraints: crisp silhouette, no halos; preserve label text; no restyling
```

### precise-object-edit
```
Use case: precise-object-edit
Input images: Image 1: room photo
Primary request: replace ONLY the white chairs with wooden chairs
Constraints: preserve camera angle, lighting, shadows; keep everything else unchanged
```

### compositing
```
Use case: compositing
Input images: Image 1: base scene; Image 2: subject to insert
Primary request: place subject from Image 2 next to person in Image 1
Constraints: match lighting, perspective, scale; keep background unchanged
Input fidelity: high
```

### style-transfer
```
Use case: style-transfer
Input images: Image 1: style reference
Primary request: apply Image 1's visual style to a man on a motorcycle
Constraints: preserve palette, texture, brushwork; no extra elements; white background
```

### sketch-to-render
```
Use case: sketch-to-render
Input images: Image 1: drawing
Primary request: turn the drawing into a photorealistic image
Constraints: preserve layout, proportions, perspective; realistic materials; no new elements
Quality: high
```
