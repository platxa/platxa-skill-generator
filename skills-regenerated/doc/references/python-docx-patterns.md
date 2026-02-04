# python-docx API Patterns

Reference for common `python-docx` operations used in DOCX document creation and editing.

## Document Lifecycle

```python
from docx import Document

# Create new
doc = Document()
doc.save("output.docx")

# Open existing
doc = Document("input.docx")
doc.save("output.docx")
```

## Paragraphs and Runs

A paragraph contains one or more runs. Each run has uniform formatting.

```python
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Add paragraph with style
doc.add_paragraph("Text", style="Normal")
doc.add_paragraph("Heading", style="Heading 1")

# Formatted runs
para = doc.add_paragraph()
run = para.add_run("Bold text")
run.bold = True
run.font.size = Pt(12)
run.font.name = "Calibri"
run.font.color.rgb = RGBColor(0x42, 0x72, 0xC4)

# Alignment
para.alignment = WD_ALIGN_PARAGRAPH.CENTER
```

## Headings

```python
doc.add_heading("Title", level=0)      # Title style
doc.add_heading("Chapter", level=1)    # Heading 1
doc.add_heading("Section", level=2)    # Heading 2
doc.add_heading("Subsection", level=3) # Heading 3
```

## Tables

```python
from docx.shared import Cm, Pt
from docx.oxml.ns import qn

# Create table
table = doc.add_table(rows=3, cols=3, style="Table Grid")

# Access cells
cell = table.cell(row_idx, col_idx)
cell.text = "Content"

# Merge cells
table.cell(0, 0).merge(table.cell(0, 2))  # Merge first row across 3 columns

# Column widths
for row in table.rows:
    row.cells[0].width = Cm(4)
    row.cells[1].width = Cm(6)
    row.cells[2].width = Cm(3)

# Header shading
shading = cell._element.get_or_add_tcPr()
shading_elm = shading.makeelement(qn("w:shd"), {
    qn("w:val"): "clear",
    qn("w:color"): "auto",
    qn("w:fill"): "4472C4",
})
shading.append(shading_elm)
```

## Lists

```python
# Bulleted list
doc.add_paragraph("Item one", style="List Bullet")
doc.add_paragraph("Item two", style="List Bullet")

# Numbered list
doc.add_paragraph("Step one", style="List Number")
doc.add_paragraph("Step two", style="List Number")

# Nested lists (indented)
doc.add_paragraph("Sub-item", style="List Bullet 2")
doc.add_paragraph("Sub-step", style="List Number 2")
```

## Images

```python
from docx.shared import Inches

# Add image with explicit width
doc.add_picture("chart.png", width=Inches(5.0))

# Add image with both dimensions
doc.add_picture("logo.png", width=Inches(2.0), height=Inches(1.0))
```

Always specify at least `width` to prevent overflow.

## Styles

```python
# Modify default Normal style
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)

# Access heading styles
h1_style = doc.styles["Heading 1"]
h1_style.font.size = Pt(16)
h1_style.font.bold = True

# Paragraph spacing
from docx.shared import Pt
style.paragraph_format.space_before = Pt(6)
style.paragraph_format.space_after = Pt(6)
style.paragraph_format.line_spacing = 1.15
```

## Sections and Page Setup

```python
from docx.shared import Inches, Cm
from docx.enum.section import WD_ORIENT

section = doc.sections[0]

# Margins
section.top_margin = Inches(1.0)
section.bottom_margin = Inches(1.0)
section.left_margin = Inches(1.25)
section.right_margin = Inches(1.25)

# Page size (Letter: 8.5 x 11 inches, A4: 21 x 29.7 cm)
section.page_width = Cm(21.0)
section.page_height = Cm(29.7)

# Landscape
section.orientation = WD_ORIENT.LANDSCAPE
section.page_width, section.page_height = section.page_height, section.page_width
```

## Headers and Footers

```python
section = doc.sections[0]
header = section.header
header.is_linked_to_previous = False
header_para = header.paragraphs[0]
header_para.text = "Document Header"
header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

footer = section.footer
footer.is_linked_to_previous = False
footer_para = footer.paragraphs[0]
footer_para.text = "Page "
```

## Page Breaks

```python
from docx.enum.text import WD_BREAK

para = doc.add_paragraph()
run = para.add_run()
run.add_break(WD_BREAK.PAGE)
```

## Dimension Units

| Class | Unit | Example |
|-------|------|---------|
| `Inches(n)` | Inches | `Inches(1.0)` = 1 inch |
| `Cm(n)` | Centimeters | `Cm(2.54)` = 1 inch |
| `Pt(n)` | Points (1/72 inch) | `Pt(12)` = 12pt font |
| `Emu(n)` | English Metric Units | `Emu(914400)` = 1 inch |
| `Twips(n)` | Twips (1/1440 inch) | `Twips(1440)` = 1 inch |
