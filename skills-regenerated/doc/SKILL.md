---
name: doc
description: >-
  Use when the task involves reading, creating, or editing .docx documents with
  professional formatting; leverages python-docx for structured authoring
  (headings, styles, tables, lists, images) and the bundled
  scripts/render_docx.py for visual review via LibreOffice-to-PNG conversion;
  handles dependency installation, rendering pipelines, and quality validation.
allowed-tools:
  - Bash
  - Read
  - Write
  - AskUserQuestion
metadata:
  version: "1.0.0"
  author: "platxa-skill-generator"
  tags:
    - guide
    - docx
    - document-processing
    - python-docx
  provenance:
    upstream_source: "doc"
    upstream_sha: "c0e08fdaa8ed6929110c97d1b867d101fd70218f"
    regenerated_at: "2026-02-04T16:00:00Z"
    generator_version: "1.0.0"
    intent_confidence: 0.58
---

# DOCX Document Skill

Read, create, and edit `.docx` documents with professional formatting and visual verification.

## Overview

This skill handles Word document operations end-to-end: reading existing `.docx` files, creating new documents with structured formatting, editing content while preserving layout, and verifying visual quality through a rendering pipeline that converts DOCX to PNG pages.

**Core capabilities:**
- Create `.docx` files with headings, styles, tables, lists, and images via `python-docx`
- Edit existing documents while preserving formatting, styles, and section properties
- Render documents to PNG pages via LibreOffice and Poppler for visual inspection
- Validate layout quality (typography, spacing, alignment, table integrity)

**When to use:**
- Read or review DOCX content where layout matters (tables, diagrams, pagination)
- Create or edit DOCX files with professional formatting
- Validate visual layout before delivery

## Dependencies

Install with `uv` (preferred) or `pip`:

```bash
uv pip install python-docx pdf2image
```

System tools for rendering (LibreOffice + Poppler):

```bash
# Ubuntu/Debian
sudo apt-get install -y libreoffice poppler-utils
# macOS
brew install libreoffice poppler
```

If system tools cannot be installed, `python-docx` still works for document creation and editing; only the rendering pipeline requires LibreOffice and Poppler.

## Workflow

### Step 1: Assess Environment

```bash
python3 -c "import docx; print('python-docx:', docx.__version__)" 2>/dev/null || echo "MISSING"
command -v soffice >/dev/null 2>&1 && echo "LibreOffice: OK" || echo "MISSING: LibreOffice"
command -v pdftoppm >/dev/null 2>&1 && echo "Poppler: OK" || echo "MISSING: Poppler"
```

### Step 2: Gather Requirements

Ask the user for objective, mode (create/edit/review), input file path, output path (default: `output/doc/<name>.docx`), and style requirements.

### Step 3: Execute Document Operation

**Create a document:**

```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)
doc.add_heading("Title", level=0)
table = doc.add_table(rows=3, cols=3, style="Table Grid")
table.cell(0, 0).text = "Header 1"
doc.add_picture("image.png", width=Inches(4.0))
doc.save("output/doc/result.docx")
```

**Read a document:**

```python
from docx import Document
doc = Document("input.docx")
for para in doc.paragraphs:
    print(f"[{para.style.name}] {para.text}")
for table in doc.tables:
    for row in table.rows:
        print([cell.text for cell in row.cells])
```

**Edit a document:**

```python
from docx import Document
doc = Document("input.docx")
for para in doc.paragraphs:
    if "old text" in para.text:
        for run in para.runs:
            run.text = run.text.replace("old text", "new text")
doc.save("output/doc/edited.docx")
```

### Step 4: Render and Inspect

```bash
SKILL_DIR="<path-to-this-skill>"
python3 "$SKILL_DIR/scripts/render_docx.py" output/doc/result.docx \
  --output_dir tmp/doc/pages --width 1600 --height 2000
```

Manual rendering without the bundled script:

```bash
soffice -env:UserInstallation=file:///tmp/lo_profile_$$ \
  --headless --convert-to pdf --outdir tmp/doc/ output/doc/result.docx
pdftoppm -png tmp/doc/result.pdf tmp/doc/result
```

Inspect each page for: clipped text, broken tables, encoding issues, spacing, image overflow.

### Step 5: Iterate and Deliver

Fix formatting issues, re-render, re-inspect. Save final `.docx`, report path, clean up `tmp/doc/`.

## File Conventions

| Path | Purpose |
|------|---------|
| `tmp/doc/` | Intermediate files (PDFs, PNGs); delete when done |
| `output/doc/` | Final document artifacts |

## Best Practices

**Do:**
- Set explicit fonts, sizes, and spacing via `doc.styles`
- Use `Inches()`, `Pt()`, `Cm()`, `Emu()` for dimensions
- Set column widths explicitly with `cell.width = Cm(N)`
- Re-render after every structural change
- Use ASCII hyphens only; avoid U+2011, U+2013, U+2014

**Do not:**
- Leave formatting to Word defaults (they vary across systems)
- Mix direct formatting with style-based formatting
- Insert images without specifying width
- Skip visual verification before delivery

## Common Patterns

### Table with Header Shading

```python
from docx import Document
from docx.shared import Pt, Cm
from docx.oxml.ns import qn

doc = Document()
table = doc.add_table(rows=4, cols=3, style="Table Grid")
for i, header in enumerate(["Name", "Role", "Status"]):
    cell = table.cell(0, i)
    cell.text = header
    run = cell.paragraphs[0].runs[0]
    run.bold = True
    run.font.size = Pt(10)
    shading = cell._element.get_or_add_tcPr()
    shading_elm = shading.makeelement(qn("w:shd"), {
        qn("w:val"): "clear", qn("w:color"): "auto", qn("w:fill"): "4472C4"})
    shading.append(shading_elm)
for row in table.rows:
    row.cells[0].width = Cm(5)
    row.cells[1].width = Cm(5)
    row.cells[2].width = Cm(3)
```

### Page Setup

```python
from docx import Document
from docx.shared import Inches
from docx.enum.section import WD_ORIENT

doc = Document()
section = doc.sections[0]
section.top_margin = Inches(1.0)
section.bottom_margin = Inches(1.0)
section.left_margin = Inches(1.25)
section.right_margin = Inches(1.25)
section.orientation = WD_ORIENT.LANDSCAPE
section.page_width, section.page_height = section.page_height, section.page_width
```

## Examples

### Example 1: Create a report

> **Prompt**: Create a quarterly sales report with summary table
>
> **Steps**: Set up Calibri 11pt, add title heading, create a 5-row table with Q1-Q4 revenue columns, add chart placeholder, render to PNG, save to `output/doc/quarterly-report.docx`

### Example 2: Edit an existing document

> **Prompt**: Update the header in proposal.docx to say "2026 Budget Proposal"
>
> **Steps**: Load with `python-docx`, find heading paragraph, replace text preserving formatting, re-render, save to `output/doc/proposal.docx`

### Example 3: Visual review

> **Prompt**: Check if the tables in report.docx are aligned properly
>
> **Steps**: Run `render_docx.py`, inspect each PNG page for alignment, report findings on column widths and border consistency, suggest fixes

## Output Checklist

Before delivering a document, verify:

- [ ] Document opens without errors in Word or LibreOffice
- [ ] Fonts render consistently (no fallback to default serif)
- [ ] Tables have aligned columns with no text overflow
- [ ] Images are properly sized within page margins
- [ ] Page margins and orientation match requirements
- [ ] Headings follow consistent hierarchy (H1, H2, H3)
- [ ] No encoding artifacts (mojibake, replacement characters)
- [ ] Temporary files cleaned up from `tmp/doc/`

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: docx` | Run `uv pip install python-docx` (package name differs from import) |
| `soffice` not found | Install LibreOffice: `apt-get install libreoffice` or `brew install libreoffice` |
| `pdftoppm` not found | Install Poppler: `apt-get install poppler-utils` or `brew install poppler` |
| LibreOffice profile lock | Use unique profile: `-env:UserInstallation=file:///tmp/lo_profile_$$` |
| PDF conversion fails | Try DOCX to ODT to PDF fallback (bundled script handles this) |
| Table columns misaligned | Set explicit widths: `cell.width = Cm(N)` |
| Image overflows page | Specify width: `doc.add_picture(path, width=Inches(N))` |
| Unicode dash rendering | Replace U+2011, U+2013, U+2014 with ASCII hyphen 0x2D |

## Reference Map

- **`references/python-docx-patterns.md`**: API patterns for paragraphs, tables, styles, images, sections
- **`references/rendering-pipeline.md`**: DOCX-to-PNG conversion, DPI calculation, troubleshooting
