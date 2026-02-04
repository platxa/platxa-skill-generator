# docx-js Patterns Reference

Quick reference for creating Word documents with the docx-js JavaScript library.

## Setup

```javascript
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        ImageRun, Header, Footer, AlignmentType, PageOrientation, LevelFormat,
        ExternalHyperlink, InternalHyperlink, TableOfContents, HeadingLevel,
        BorderStyle, WidthType, TabStopType, TabStopPosition, UnderlineType,
        ShadingType, VerticalAlign, SymbolRun, PageNumber, PageBreak,
        FootnoteReferenceRun, Footnote } = require('docx');

const doc = new Document({ sections: [{ children: [/* content */] }] });
Packer.toBuffer(doc).then(buf => fs.writeFileSync("doc.docx", buf));
```

## Styles and Fonts

```javascript
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } }, // 12pt
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal",
        quickFormat: true,
        run: { size: 32, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal",
        quickFormat: true,
        run: { size: 28, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 } }
    ]
  },
  sections: [{ children: [
    new Paragraph({ heading: HeadingLevel.HEADING_1,
      children: [new TextRun("Title")] })
  ] }]
});
```

Key rules:
- Override built-in styles using exact IDs: `"Heading1"`, `"Heading2"`, `"Heading3"`
- Set `outlineLevel: 0` for H1, `1` for H2 (required for TOC)
- Default font: `styles.default.document.run.font` (Arial recommended)
- Size in half-points: 24 = 12pt, 28 = 14pt, 32 = 16pt

## Text Formatting

```javascript
new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 200, after: 200 },
  children: [
    new TextRun({ text: "Bold", bold: true }),
    new TextRun({ text: "Italic", italics: true }),
    new TextRun({ text: "Colored", color: "FF0000", size: 28, font: "Arial" }),
    new TextRun({ text: "Highlighted", highlight: "yellow" }),
    new TextRun({ text: "Strike", strike: true }),
    new TextRun({ text: "2", superScript: true })
  ]
})
```

**Rule**: Never use `\n` for line breaks. Always use separate `Paragraph` elements.

## Lists

```javascript
const doc = new Document({
  numbering: { config: [
    { reference: "bullets",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    { reference: "numbers",
      levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
  ] },
  sections: [{ children: [
    new Paragraph({ numbering: { reference: "bullets", level: 0 },
      children: [new TextRun("First bullet")] }),
    new Paragraph({ numbering: { reference: "numbers", level: 0 },
      children: [new TextRun("First numbered item")] })
  ] }]
});
```

Key rules:
- Use `LevelFormat.BULLET` constant, never string `"bullet"` or unicode symbols
- Same reference = continues numbering; different reference = restarts at 1
- Use unique reference names for independent numbered sections

## Tables

```javascript
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

new Table({
  columnWidths: [4680, 4680], // DXA units (1440 = 1 inch)
  margins: { top: 100, bottom: 100, left: 180, right: 180 },
  rows: [
    new TableRow({ tableHeader: true, children: [
      new TableCell({ borders, width: { size: 4680, type: WidthType.DXA },
        shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
        children: [new Paragraph({ children: [
          new TextRun({ text: "Header", bold: true })
        ] })] })
    ] })
  ]
})
```

Key rules:
- Set BOTH `columnWidths` array and individual cell widths
- Always use `ShadingType.CLEAR` (never `SOLID`, which causes black backgrounds)
- Apply borders to cells, not the table
- Letter size usable width with 1" margins = 9360 DXA

## Images

```javascript
new Paragraph({ children: [new ImageRun({
  type: "png", // REQUIRED: png, jpg, jpeg, gif, bmp, svg
  data: fs.readFileSync("image.png"),
  transformation: { width: 200, height: 150 },
  altText: { title: "Logo", description: "Company logo", name: "Logo" }
})] })
```

## Page Setup

```javascript
sections: [{
  properties: {
    page: {
      margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      size: { orientation: PageOrientation.LANDSCAPE }
    }
  },
  headers: { default: new Header({ children: [
    new Paragraph({ alignment: AlignmentType.RIGHT,
      children: [new TextRun("Header")] })
  ] }) },
  footers: { default: new Footer({ children: [
    new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun("Page "),
        new TextRun({ children: [PageNumber.CURRENT] }),
        new TextRun(" of "),
        new TextRun({ children: [PageNumber.TOTAL_PAGES] })]
    })
  ] }) },
  children: [/* content */]
}]
```

## Page Breaks

```javascript
// Correct: PageBreak inside Paragraph
new Paragraph({ children: [new PageBreak()] })
// Also correct: pageBreakBefore
new Paragraph({ pageBreakBefore: true, children: [new TextRun("New page")] })
// WRONG: standalone PageBreak creates invalid XML
```

## Common Width Values (DXA)

| Columns | Equal widths (letter, 1" margins) |
|---------|-----------------------------------|
| 2 cols | `[4680, 4680]` |
| 3 cols | `[3120, 3120, 3120]` |
| 4 cols | `[2340, 2340, 2340, 2340]` |
