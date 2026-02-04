# HTML to PowerPoint Guide

Convert HTML slides to PowerPoint with accurate positioning using `html2pptx.js`.

## HTML Slide Dimensions

- **16:9** (default): `width: 720pt; height: 405pt`
- **4:3**: `width: 720pt; height: 540pt`
- **16:10**: `width: 720pt; height: 450pt`

## Supported Elements

| Element | Purpose |
|---------|---------|
| `<p>`, `<h1>`-`<h6>` | Text with styling |
| `<ul>`, `<ol>` | Lists (never use manual bullets) |
| `<b>`, `<i>`, `<u>` | Inline formatting |
| `<span>` | Inline styles (bold, italic, underline, color) |
| `<br>` | Line breaks |
| `<div>` with bg/border | Shapes |
| `<img>` | Images |
| `class="placeholder"` | Reserved chart/table area (returns `{id, x, y, w, h}`) |

## Critical Rules

1. **All text MUST be in `<p>`, `<h1>`-`<h6>`, `<ul>`, or `<ol>` tags** -- text in bare `<div>` or `<span>` is silently dropped
2. **Never use manual bullet symbols** (`*`, `-`, etc.) -- use `<ul>`/`<ol>`
3. **Only web-safe fonts**: Arial, Helvetica, Times New Roman, Georgia, Courier New, Verdana, Tahoma, Trebuchet MS, Impact
4. **Never use CSS gradients** -- rasterize SVG to PNG with Sharp first
5. **Backgrounds/borders/shadows only on `<div>`** -- not on text elements
6. Use `display: flex` on body to prevent margin collapse issues
7. Use hex colors with `#` prefix in CSS

## Rasterizing Icons and Gradients

Always create PNG assets before referencing in HTML:

```javascript
// Icons: rasterize react-icons SVG to PNG
const sharp = require('sharp');
const React = require('react');
const ReactDOMServer = require('react-dom/server');
const { FaHome } = require('react-icons/fa');

const svg = ReactDOMServer.renderToStaticMarkup(
  React.createElement(FaHome, { color: '#4472c4', size: '256' })
);
await sharp(Buffer.from(svg)).png().toFile('icon.png');

// Gradients: SVG to PNG background
const gradientSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="563">
  <defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" style="stop-color:#COLOR1"/>
    <stop offset="100%" style="stop-color:#COLOR2"/>
  </linearGradient></defs>
  <rect width="100%" height="100%" fill="url(#g)"/>
</svg>`;
await sharp(Buffer.from(gradientSvg)).png().toFile('gradient-bg.png');
```

## API Reference

```javascript
const { slide, placeholders } = await html2pptx(htmlFile, pres, options);
```

- `htmlFile`: Path to HTML file
- `pres`: PptxGenJS instance with layout set
- `options.tmpDir`: Temp directory (default: `/tmp`)
- `options.slide`: Existing slide to reuse
- Returns: `{ slide, placeholders: [{ id, x, y, w, h }] }`

## PptxGenJS Charts

**Colors: NEVER use `#` prefix** -- causes file corruption. Use `"FF0000"` not `"#FF0000"`.

```javascript
// Bar chart
slide.addChart(pptx.charts.BAR, [{
  name: "Sales", labels: ["Q1","Q2","Q3","Q4"], values: [45,55,62,71]
}], { ...placeholders[0], barDir: 'col', chartColors: ["4472C4"] });

// Pie chart (single series, no axis labels)
slide.addChart(pptx.charts.PIE, [{
  name: "Share", labels: ["A","B","C"], values: [35,45,20]
}], { showPercent: true, chartColors: ["4472C4","ED7D31","A5A5A5"] });

// Line chart
slide.addChart(pptx.charts.LINE, [{
  name: "Temp", labels: ["Jan","Feb","Mar"], values: [32,35,42]
}], { lineSize: 4, showCatAxisTitle: true, catAxisTitle: 'Month' });
```

## PptxGenJS Tables

```javascript
slide.addTable([
  [{ text: "Header", options: { fill: {color:"4472C4"}, color:"FFFFFF", bold:true }}],
  ["Row 1"], ["Row 2"]
], { x:1, y:1.5, w:8, border: {pt:1, color:"999999"} });
```

## Validation

The library auto-validates: dimension mismatches, content overflow, unsupported gradients, and text element styling errors. All errors reported together.
