---
name: pdf
description: >-
  Process, generate, and fill PDF documents using Python and CLI tools. Use when
  extracting text or tables from PDFs (pypdf, pdfplumber), merging or splitting
  documents, creating new PDFs (reportlab), filling fillable form fields, or
  annotating non-fillable forms with visual bounding-box validation. Includes
  bundled scripts for form-field detection, coordinate transformation, and
  annotation placement.
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Task
metadata:
  version: "1.0.0"
  author: "platxa-skill-generator"
  tags:
    - builder
    - pdf
    - document-processing
    - forms
  provenance:
    upstream_source: "pdf"
    upstream_sha: "c0e08fdaa8ed6929110c97d1b867d101fd70218f"
    regenerated_at: "2026-02-04T15:00:00Z"
    generator_version: "1.0.0"
    intent_confidence: 0.61
---

# PDF Processing Skill

Process, generate, and fill PDF documents using Python libraries and CLI tools.

## Overview

This skill handles four categories of PDF work:

**Extraction** -- Pull text, tables, metadata, and images from existing PDFs using pdfplumber, pypdf, or CLI tools (pdftotext, pdfimages).

**Manipulation** -- Merge multiple PDFs, split a PDF into pages, rotate pages, crop regions, add watermarks, encrypt/decrypt, and optimize file size.

**Creation** -- Generate new PDFs from scratch with reportlab (Canvas for simple layouts, Platypus/SimpleDocTemplate for multi-page reports with tables and styled paragraphs).

**Form filling** -- Fill both fillable (AcroForm) and non-fillable PDFs. Fillable forms use bundled scripts that detect fields, extract metadata, and write values via pypdf. Non-fillable forms use a visual bounding-box pipeline: convert pages to images, define field coordinates in JSON, validate with overlay images, then place FreeText annotations.

**Prerequisites:**
- Python 3.8+ with `pypdf`, `pdfplumber`, `reportlab`
- For forms: `pdf2image`, `Pillow`; optional `pytesseract` for OCR
- CLI: `poppler-utils` (pdftotext, pdfimages, pdftoppm), `qpdf`

## Decision Tree

```
User request
 |- "extract text/tables/metadata from PDF"  -> extraction
 |- "merge/split/rotate/crop/watermark/encrypt"  -> manipulation
 |- "create/generate a new PDF"  -> creation
 |- "fill out a PDF form"  -> form-filling
 |- "OCR a scanned PDF"  -> extraction + OCR
```

## Workflow

### Step 1: Identify Task Category

Match the request to extraction, manipulation, creation, or form-filling. For forms, proceed to Step 5.

### Step 2: Install Dependencies

```bash
pip install pypdf pdfplumber reportlab 2>/dev/null
pip install pdf2image Pillow pytesseract 2>/dev/null
```

### Step 3: Execute Operation

#### Text Extraction (pdfplumber)

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        tables = page.extract_tables()
```

Custom table settings for complex layouts:

```python
table_settings = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "snap_tolerance": 3,
    "intersection_tolerance": 15,
}
tables = page.extract_tables(table_settings)
```

#### Merge PDFs (pypdf)

```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)
with open("merged.pdf", "wb") as f:
    writer.write(f)
```

#### Create PDF (reportlab)

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
elements = [Paragraph("Sales Report", styles['Title'])]
data = [['Product', 'Q1', 'Q2'], ['Widgets', '120', '135']]
table = Table(data)
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))
elements.append(table)
doc.build(elements)
```

#### CLI Operations (qpdf, poppler-utils)

```bash
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf
pdftotext -layout input.pdf output.txt
pdftoppm -png -r 300 document.pdf output_prefix
qpdf --password=secret --decrypt encrypted.pdf decrypted.pdf
qpdf --linearize input.pdf optimized.pdf
```

### Step 4: Validate Output

- Extracted text: non-empty, encoding correct, tables aligned
- Merged PDF: page count matches sum of inputs
- Created PDF: opens without errors, content renders correctly
- CLI output: exit code 0, output file exists and is non-empty

### Step 5: Form Filling

#### 5a: Detect Form Fields

```bash
python3 <skill-dir>/scripts/check_fillable_fields.py input.pdf
```

#### 5b Path A: Fillable Form Fields

1. Extract field metadata:
   ```bash
   python3 <skill-dir>/scripts/extract_form_field_info.py input.pdf field_info.json
   ```
   Output: `field_id`, `page`, `type` (text/checkbox/radio_group/choice), plus type-specific properties.

2. Convert to images: `python3 <skill-dir>/scripts/convert_pdf_to_images.py input.pdf ./page_images/`

3. Analyze images to map field IDs to their visual purpose.

4. Create `field_values.json`:
   ```json
   [
     {"field_id": "last_name", "page": 1, "value": "Simpson"},
     {"field_id": "citizen_yes", "page": 1, "value": "/On"}
   ]
   ```
   For checkboxes use `checked_value`. For radio groups use `radio_options[].value`.

5. Fill: `python3 <skill-dir>/scripts/fill_fillable_fields.py input.pdf field_values.json output.pdf`

#### 5c Path B: Non-Fillable Forms (Annotation-Based)

1. Convert: `python3 <skill-dir>/scripts/convert_pdf_to_images.py input.pdf ./page_images/`

2. Determine two non-overlapping bounding boxes per field (label + entry). Coords: `[left, top, right, bottom]` in image pixels.

3. Create `fields.json`:
   ```json
   {
     "pages": [{"page_number": 1, "image_width": 850, "image_height": 1100}],
     "form_fields": [{
       "page_number": 1, "description": "Last name field",
       "field_label": "Last Name",
       "label_bounding_box": [30, 125, 95, 142],
       "entry_bounding_box": [100, 125, 280, 142],
       "entry_text": {"text": "Simpson", "font_size": 14}
     }]
   }
   ```

4. Validate:
   ```bash
   python3 <skill-dir>/scripts/create_validation_image.py 1 fields.json page_images/page_1.png val.png
   python3 <skill-dir>/scripts/check_bounding_boxes.py fields.json
   ```
   Red = entry areas, blue = labels. Fix intersections, re-check until clean.

5. Inspect: red boxes on blank areas only, blue boxes on label text.

6. Apply: `python3 <skill-dir>/scripts/fill_pdf_form_with_annotations.py input.pdf fields.json output.pdf`

## Tool Selection Guide

| Task | Best Tool | Notes |
|------|-----------|-------|
| Extract text (digital) | pdfplumber | Preserves layout, handles tables |
| Extract text (scanned) | pytesseract + pdf2image | OCR, requires Tesseract |
| Extract tables | pdfplumber + pandas | `pd.DataFrame(table[1:], columns=table[0])` |
| Merge/split/rotate | pypdf | Pure Python, no external deps |
| Create new PDF | reportlab | Canvas (simple) or Platypus (complex) |
| CLI merge/split | qpdf | `--pages` for selective extraction |
| CLI text extraction | pdftotext | `-layout` preserves columns |
| Render to images | pdftoppm or pypdfium2 | `-r 300` for 300 DPI |
| Password ops | pypdf or qpdf | `writer.encrypt()` / `qpdf --encrypt` |
| Fill fillable forms | bundled scripts | See Step 5b |
| Fill non-fillable forms | bundled scripts | See Step 5c |

## Examples

### Example 1: Extract Tables to Excel

```
User: Extract all tables from quarterly-report.pdf to an Excel spreadsheet
Assistant: Extract tables with pdfplumber, convert to DataFrames, write to Excel.
Result: extracted_tables.xlsx with 12 tables across 3 sheets.
```

### Example 2: Fill a Tax Form

```
User: Fill out form W-4 in w4.pdf
Assistant: Check fillable fields, extract metadata, create field_values.json, fill.
Output: w4_filled.pdf
```

## Output Checklist

- [ ] Output file exists and is non-empty
- [ ] PDF opens without corruption errors
- [ ] Page count matches expectations
- [ ] Text encoding correct
- [ ] Form fields contain correct values
- [ ] Annotations at correct positions

## Troubleshooting

| Problem | Solution |
|---------|----------|
| ModuleNotFoundError: pypdf | `pip install pypdf` (not PyPDF2) |
| Garbled text | Try pdfplumber; if scanned use OCR |
| Tables misaligned | Increase pdfplumber `snap_tolerance` |
| qpdf not found | `apt-get install qpdf` |
| Field IDs not matching | Re-run extract_form_field_info.py |
| Bounding boxes overlap | Run check_bounding_boxes.py, fix coords |
| Wrong annotation position | Verify image dims in fields.json |

## Reference Map

- **references/python-libraries.md**: pypdf, pdfplumber, reportlab API patterns
- **references/form-filling-guide.md**: Fillable and non-fillable form workflows
- **references/cli-tools.md**: qpdf, poppler-utils commands and recipes
