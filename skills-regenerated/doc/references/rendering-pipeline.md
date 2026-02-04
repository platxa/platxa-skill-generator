# DOCX Rendering Pipeline

Reference for converting DOCX documents to PNG pages for visual inspection.

## Pipeline Overview

```
DOCX -> LibreOffice -> PDF -> Poppler (pdftoppm) -> PNG pages
```

The bundled `scripts/render_docx.py` automates this pipeline with DPI calculation, fallback conversion paths, and page renaming.

## Bundled Script Usage

```bash
SKILL_DIR="<path-to-this-skill>"

# Basic rendering (auto-DPI)
python3 "$SKILL_DIR/scripts/render_docx.py" document.docx \
  --output_dir tmp/doc/pages

# Custom max dimensions (pixels)
python3 "$SKILL_DIR/scripts/render_docx.py" document.docx \
  --output_dir tmp/doc/pages --width 1600 --height 2000

# Override DPI (skip auto-calculation)
python3 "$SKILL_DIR/scripts/render_docx.py" document.docx \
  --output_dir tmp/doc/pages --dpi 200
```

Output files: `page-1.png`, `page-2.png`, etc. in the output directory.

## DPI Calculation

The script calculates DPI automatically from the document's page dimensions:

1. **OOXML method** (for .docx/.docm/.dotx/.dotm): Reads `word/document.xml` inside the ZIP, extracts `w:pgSz` attributes (width and height in twips, 1 twip = 1/1440 inch), computes isotropic DPI to fit within max pixel dimensions.

2. **PDF fallback**: Converts to PDF first, reads page size from PDF metadata (in points, 1 point = 1/72 inch), computes DPI similarly.

Formula: `DPI = min(max_width_px / page_width_inches, max_height_px / page_height_inches)`

## Manual Pipeline Commands

### DOCX to PDF via LibreOffice

```bash
soffice \
  -env:UserInstallation=file:///tmp/lo_profile_$$ \
  --invisible --headless --norestore \
  --convert-to pdf \
  --outdir /tmp/doc_output/ \
  input.docx
```

The `-env:UserInstallation` flag creates an isolated profile to avoid lock conflicts when running multiple conversions concurrently.

### PDF to PNG via Poppler

```bash
pdftoppm -png -r 200 /tmp/doc_output/input.pdf /tmp/doc_output/page
```

Flags:
- `-png`: Output format
- `-r 200`: DPI resolution (higher = sharper but larger files)
- Output: `page-1.png`, `page-2.png`, etc.

## Fallback Conversion Path

If direct DOCX-to-PDF fails (common with complex formatting), the script tries:

```
DOCX -> ODT (via LibreOffice) -> PDF (via LibreOffice) -> PNG
```

This two-step conversion often succeeds where direct conversion does not.

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `soffice` not found | LibreOffice not installed | `apt-get install libreoffice` or `brew install libreoffice` |
| `pdftoppm` not found | Poppler not installed | `apt-get install poppler-utils` or `brew install poppler` |
| Profile lock error | Another soffice instance running | Use unique profile path with `$$` (PID) |
| PDF conversion produces blank | Complex DOCX formatting | Try the ODT fallback path |
| Low resolution output | DPI too low | Use `--dpi 300` for print quality |
| `pdf2image` import error | Python package missing | `uv pip install pdf2image` |

## Dependencies

| Tool | Package | Purpose |
|------|---------|---------|
| `soffice` | LibreOffice | DOCX-to-PDF conversion |
| `pdftoppm` | Poppler (`poppler-utils`) | PDF-to-PNG rasterization |
| `pdf2image` | Python package | Python wrapper for pdftoppm |
| `python-docx` | Python package | OOXML page size extraction |
