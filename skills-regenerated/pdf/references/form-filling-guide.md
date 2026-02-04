# PDF Form Filling Guide

## Overview

PDF forms come in two types that require different filling strategies:

1. **Fillable (AcroForm)** -- The PDF contains native form field definitions with field IDs, types, and validation rules. These can be filled programmatically by setting field values.

2. **Non-fillable** -- The form is a flat visual layout (scanned or designed without form fields). Filling requires identifying field positions visually and placing text annotations at the correct coordinates.

## Fillable Form Workflow

### Step 1: Detect Fillable Fields

```bash
python3 scripts/check_fillable_fields.py document.pdf
```

Output: "This PDF has fillable form fields" or "This PDF does not have fillable form fields".

### Step 2: Extract Field Metadata

```bash
python3 scripts/extract_form_field_info.py document.pdf field_info.json
```

### Field Types and Properties

**Text fields:**
```json
{
  "field_id": "full_name",
  "page": 1,
  "type": "text",
  "rect": [72, 680, 300, 700]
}
```

**Checkboxes:**
```json
{
  "field_id": "agree_terms",
  "page": 1,
  "type": "checkbox",
  "checked_value": "/Yes",
  "unchecked_value": "/Off"
}
```
Set to `checked_value` to check, `unchecked_value` to uncheck.

**Radio groups:**
```json
{
  "field_id": "filing_status",
  "page": 1,
  "type": "radio_group",
  "radio_options": [
    {"value": "/Single", "rect": [72, 500, 85, 513]},
    {"value": "/Married", "rect": [72, 480, 85, 493]}
  ]
}
```
Set to one of the `radio_options[].value` values.

**Choice (dropdown/list):**
```json
{
  "field_id": "state",
  "page": 1,
  "type": "choice",
  "choice_options": [
    {"value": "CA", "text": "California"},
    {"value": "NY", "text": "New York"}
  ]
}
```
Set to one of the `choice_options[].value` values.

### Step 3: Create Field Values

```json
[
  {"field_id": "full_name", "page": 1, "value": "Jane Smith"},
  {"field_id": "agree_terms", "page": 1, "value": "/Yes"},
  {"field_id": "filing_status", "page": 1, "value": "/Single"},
  {"field_id": "state", "page": 2, "value": "CA"}
]
```

### Step 4: Fill

```bash
python3 scripts/fill_fillable_fields.py document.pdf field_values.json output.pdf
```

The script validates field IDs and values before writing. Error messages indicate mismatches.

## Non-Fillable Form Workflow

### Step 1: Convert to Images

```bash
python3 scripts/convert_pdf_to_images.py document.pdf ./page_images/
```

Creates `page_1.png`, `page_2.png`, etc. at 200 DPI (max 1000px dimension).

### Step 2: Identify Fields

Examine each page image and identify form fields. For each field, determine:
- **Label bounding box**: The text label area (e.g., "Name:")
- **Entry bounding box**: The blank area where data goes

Bounding boxes use image pixel coordinates: `[left, top, right, bottom]`.

### Common Form Patterns

**Label inside box:**
```
+------------------------+
| Name:                  |
+------------------------+
```
Entry area: right of "Name:" to box edge.

**Label before line:**
```
Email: _______________________
```
Entry area: above the line, full width.

**Label under line:**
```
_________________________
Name
```
Entry area: above the line, full width. Common for signatures.

**Checkboxes:**
```
Are you a US citizen? Yes []  No []
```
Entry area: the small square only, not the text label. Use "X" as entry text.

### Step 3: Create fields.json

```json
{
  "pages": [
    {"page_number": 1, "image_width": 850, "image_height": 1100}
  ],
  "form_fields": [
    {
      "page_number": 1,
      "description": "First name input area",
      "field_label": "First Name",
      "label_bounding_box": [30, 125, 110, 142],
      "entry_bounding_box": [115, 125, 300, 142],
      "entry_text": {
        "text": "Jane",
        "font_size": 14,
        "font_color": "000000"
      }
    }
  ]
}
```

Key rules:
- Label and entry bounding boxes MUST NOT overlap
- Entry boxes must be tall enough to contain text (min ~15px for 14pt font)
- `image_width` and `image_height` must match actual image dimensions exactly

### Step 4: Validate

Generate validation overlay:
```bash
python3 scripts/create_validation_image.py 1 fields.json page_images/page_1.png validation.png
```

Run automated check:
```bash
python3 scripts/check_bounding_boxes.py fields.json
```

### Step 5: Visual Inspection

In the validation image:
- **Red rectangles** = entry areas (must be on blank space only)
- **Blue rectangles** = labels (must cover label text)

If any rectangles are misplaced, update fields.json and regenerate.

### Step 6: Apply Annotations

```bash
python3 scripts/fill_pdf_form_with_annotations.py document.pdf fields.json output.pdf
```

The script transforms image pixel coordinates to PDF coordinates (origin at bottom-left, y increases upward) and places FreeText annotations.
