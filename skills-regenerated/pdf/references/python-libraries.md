# Python PDF Libraries Reference

## pypdf (BSD License)

Core library for reading, merging, splitting, rotating, and encrypting PDFs. Pure Python with no external dependencies.

### Reading and Text Extraction

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Text from single page
text = reader.pages[0].extract_text()

# Metadata
meta = reader.metadata
# meta.title, meta.author, meta.subject, meta.creator
```

### Page Manipulation

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

# Rotate page 90 degrees clockwise
page = reader.pages[0]
page.rotate(90)
writer.add_page(page)

# Crop page (points: left, bottom, right, top)
page.mediabox.left = 50
page.mediabox.bottom = 50
page.mediabox.right = 550
page.mediabox.top = 750

# Add watermark
watermark_page = PdfReader("watermark.pdf").pages[0]
for page in reader.pages:
    page.merge_page(watermark_page)
    writer.add_page(page)

with open("output.pdf", "wb") as f:
    writer.write(f)
```

### Encryption and Decryption

```python
# Encrypt
writer.encrypt("user_password", "owner_password")

# Decrypt
reader = PdfReader("encrypted.pdf")
if reader.is_encrypted:
    reader.decrypt("password")
```

## pdfplumber (MIT License)

Best library for extracting text with layout preservation and tables from digital PDFs. Built on pdfminer.six.

### Text Extraction

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]

    # Full page text
    text = page.extract_text()

    # Text within bounding box (left, top, right, bottom)
    region_text = page.within_bbox((100, 100, 400, 200)).extract_text()

    # Character-level data
    for char in page.chars[:10]:
        print(f"'{char['text']}' at x:{char['x0']:.1f} y:{char['y0']:.1f}")
```

### Table Extraction

```python
import pdfplumber
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]

    # Default extraction
    tables = page.extract_tables()

    # Custom settings for complex layouts
    table_settings = {
        "vertical_strategy": "lines",     # or "text", "explicit"
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,              # pixel snap for line detection
        "intersection_tolerance": 15,     # intersection detection tolerance
    }
    tables = page.extract_tables(table_settings)

    # Convert to DataFrame
    for table in tables:
        if table:
            df = pd.DataFrame(table[1:], columns=table[0])

    # Debug: save page image with detected lines
    img = page.to_image(resolution=150)
    img.save("debug_layout.png")
```

## reportlab (BSD License)

PDF creation library with two APIs: Canvas (low-level drawing) and Platypus (high-level document layout).

### Canvas API (Simple PDFs)

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("output.pdf", pagesize=letter)
width, height = letter

c.drawString(100, height - 100, "Title Text")
c.line(100, height - 110, 500, height - 110)
c.save()
```

### Platypus API (Complex Documents)

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.platypus import Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
elements = []

# Title and body
elements.append(Paragraph("Report Title", styles['Title']))
elements.append(Spacer(1, 12))
elements.append(Paragraph("Body text content here.", styles['Normal']))

# Table with styling
data = [
    ['Product', 'Q1', 'Q2', 'Q3', 'Q4'],
    ['Widgets', '120', '135', '142', '158'],
]
table = Table(data)
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 14),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))
elements.append(table)
elements.append(PageBreak())

doc.build(elements)
```

## pypdfium2 (Apache/BSD License)

Python binding for PDFium (Chromium PDF engine). Fast rendering and text extraction.

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("document.pdf")

# Render page to image
page = pdf[0]
bitmap = page.render(scale=2.0, rotation=0)
img = bitmap.to_pil()
img.save("page_1.png", "PNG")

# Text extraction
for i, page in enumerate(pdf):
    text = page.get_text()
    print(f"Page {i+1}: {len(text)} chars")
```

## OCR Pipeline (pytesseract + pdf2image)

For scanned PDFs where text extraction returns empty results.

```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path('scanned.pdf', dpi=200)
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"
```

Requires: `pip install pytesseract pdf2image` plus system Tesseract and poppler-utils.

## Library Selection Matrix

| Need | Use | Why |
|------|-----|-----|
| Read/merge/split/encrypt | pypdf | Pure Python, lightweight |
| Extract text with layout | pdfplumber | Best layout preservation |
| Extract tables | pdfplumber | Built-in table detection |
| Create new PDFs | reportlab | Rich formatting support |
| Render pages to images | pypdfium2 | Fast, Chromium-grade rendering |
| OCR scanned PDFs | pytesseract + pdf2image | Tesseract integration |
