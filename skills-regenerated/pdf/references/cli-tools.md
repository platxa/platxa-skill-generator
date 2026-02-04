# PDF CLI Tools Reference

## poppler-utils

Suite of CLI tools for PDF manipulation. Install: `apt-get install poppler-utils` (Linux) or `brew install poppler` (macOS).

### pdftotext -- Extract Text

```bash
# Basic extraction
pdftotext input.pdf output.txt

# Preserve column layout
pdftotext -layout input.pdf output.txt

# Extract specific page range (1-based)
pdftotext -f 1 -l 5 input.pdf output.txt

# Extract with bounding box coordinates (XML output)
pdftotext -bbox-layout input.pdf output.xml
```

### pdftoppm -- Convert Pages to Images

```bash
# PNG at 300 DPI
pdftoppm -png -r 300 document.pdf output_prefix
# Creates output_prefix-1.png, output_prefix-2.png, etc.

# Specific page range at high resolution
pdftoppm -png -r 600 -f 1 -l 3 document.pdf high_res

# JPEG with quality setting
pdftoppm -jpeg -jpegopt quality=85 -r 200 document.pdf jpeg_output
```

### pdfimages -- Extract Embedded Images

```bash
# Extract as JPEG
pdfimages -j document.pdf output_prefix
# Creates output_prefix-000.jpg, output_prefix-001.jpg, etc.

# Extract in original format
pdfimages -all document.pdf images/img

# List image info without extracting
pdfimages -list document.pdf

# Include page numbers in output names
pdfimages -j -p document.pdf page_images
```

### pdfinfo -- Document Metadata

```bash
pdfinfo document.pdf
# Output: Title, Author, Subject, Pages, File size, PDF version, etc.
```

## qpdf

Structural PDF transformation tool. Install: `apt-get install qpdf` (Linux) or `brew install qpdf` (macOS).

### Merge

```bash
# Merge entire files
qpdf --empty --pages file1.pdf file2.pdf file3.pdf -- merged.pdf

# Merge specific pages from multiple files
qpdf --empty --pages doc1.pdf 1-3 doc2.pdf 5-7 doc3.pdf 2,4 -- combined.pdf
```

### Split

```bash
# Extract page range
qpdf input.pdf --pages . 1-5 -- first_five.pdf

# Split into individual pages
qpdf --split-pages input.pdf output_%02d.pdf

# Split into groups of N pages
qpdf --split-pages=3 input.pdf group_%02d.pdf

# Complex page selection (1, 3-5, 8, 10 to end)
qpdf input.pdf --pages . 1,3-5,8,10-z -- selected.pdf
```

### Rotate

```bash
# Rotate page 1 by 90 degrees clockwise
qpdf input.pdf output.pdf --rotate=+90:1

# Rotate all pages 180 degrees
qpdf input.pdf output.pdf --rotate=180

# Rotate pages 3-5 by 270 degrees
qpdf input.pdf output.pdf --rotate=+270:3-5
```

### Encryption and Decryption

```bash
# Encrypt with 256-bit AES, restrict print and modify
qpdf --encrypt user_pass owner_pass 256 \
  --print=none --modify=none -- input.pdf encrypted.pdf

# Check encryption status
qpdf --show-encryption encrypted.pdf

# Decrypt (requires correct password)
qpdf --password=secret --decrypt encrypted.pdf decrypted.pdf
```

### Optimization and Repair

```bash
# Linearize for web streaming (fast first-page load)
qpdf --linearize input.pdf optimized.pdf

# Remove unused objects and compress
qpdf --optimize-level=all input.pdf compressed.pdf

# Check PDF structure for errors
qpdf --check input.pdf

# Attempt repair of corrupted PDF
qpdf --replace-input corrupted.pdf

# Show detailed PDF structure
qpdf --show-all-pages input.pdf > structure.txt
```

## pdftk (if available)

Alternative PDF toolkit. Install: `apt-get install pdftk-java`.

```bash
# Merge
pdftk file1.pdf file2.pdf cat output merged.pdf

# Split into individual pages
pdftk input.pdf burst

# Rotate page 1 east (90 degrees clockwise)
pdftk input.pdf rotate 1east output rotated.pdf

# Extract pages 1-3
pdftk input.pdf cat 1-3 output extracted.pdf
```

## Tool Selection

| Task | Best CLI Tool | Key Flag |
|------|--------------|----------|
| Extract text | pdftotext | `-layout` for columns |
| Page images | pdftoppm | `-r 300` for DPI |
| Extract images | pdfimages | `-all` for original format |
| Merge | qpdf | `--pages` for selective |
| Split | qpdf | `--split-pages` |
| Rotate | qpdf | `--rotate=+90:1` |
| Encrypt | qpdf | `--encrypt u o 256` |
| Decrypt | qpdf | `--password=X --decrypt` |
| Optimize | qpdf | `--linearize` |
| Repair | qpdf | `--check` then `--replace-input` |
