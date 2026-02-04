# Office Open XML Reference for PowerPoint

Read this entire document before editing any PPTX file directly.

## Schema Rules

- **Element order in `<p:txBody>`**: `<a:bodyPr>`, `<a:lstStyle>`, `<a:p>`
- **Whitespace**: Add `xml:space='preserve'` to `<a:t>` with leading/trailing spaces
- **Unicode**: Escape characters: `"` becomes `&#8220;`
- **Dirty attribute**: Add `dirty="0"` to `<a:rPr>` and `<a:endParaRPr>`
- **Images**: Add to `ppt/media/`, reference in slide XML, update relationships

## Slide Structure

```xml
<p:sld>
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>...</p:nvGrpSpPr>
      <p:grpSpPr>...</p:grpSpPr>
      <!-- Shapes go here -->
    </p:spTree>
  </p:cSld>
</p:sld>
```

## Text Formatting

```xml
<!-- Bold --><a:rPr b="1"/>
<!-- Italic --><a:rPr i="1"/>
<!-- Underline --><a:rPr u="sng"/>
<!-- Font/size/color -->
<a:rPr lang="en-US" sz="2400" b="1" dirty="0">
  <a:solidFill><a:srgbClr val="FF0000"/></a:solidFill>
</a:rPr>
```

## Lists

```xml
<!-- Bullet -->
<a:p><a:pPr lvl="0"><a:buChar char="&#x2022;"/></a:pPr>
  <a:r><a:t>Bullet point</a:t></a:r></a:p>

<!-- Numbered -->
<a:p><a:pPr lvl="0"><a:buAutoNum type="arabicPeriod"/></a:pPr>
  <a:r><a:t>Item one</a:t></a:r></a:p>
```

## Shapes and Images

Shapes use `<a:prstGeom prst="rect|roundRect|ellipse">`. Images use `<p:pic>` with `<a:blip r:embed="rId2"/>`. Position via `<a:xfrm>` with `<a:off>` and `<a:ext>` in EMU units.

## File Updates Required

When adding slides or content, update:
1. `[Content_Types].xml` -- declare all slides, media types
2. `ppt/_rels/presentation.xml.rels` -- slide relationships
3. `ppt/presentation.xml` -- slide ID list (`<p:sldIdLst>`)
4. `ppt/slides/_rels/slideN.xml.rels` -- per-slide resources
5. `docProps/app.xml` -- slide count and statistics

## Slide Operations

**Add**: Create slide XML, update Content_Types, presentation rels, presentation.xml sldIdLst, and app.xml.

**Duplicate**: Copy slide XML with new name, update all IDs to be unique, remove/update notes slide references.

**Reorder**: Change order of `<p:sldId>` elements in `<p:sldIdLst>`. Keep IDs unchanged.

**Delete**: Remove from presentation.xml, rels, Content_Types. Delete slide file and its rels. Clean unused media.

## Validation Checklist

Before packing:
- Clean unused resources (media, fonts, notes)
- Fix Content_Types.xml for ALL slides/layouts/themes
- Remove broken references in `_rels` files
- Fix font embed references if not using embedded fonts
- Watch for duplicate notes slide references after duplication
