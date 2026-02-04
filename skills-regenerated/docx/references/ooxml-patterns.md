# OOXML Editing Patterns Reference

Reference for editing existing Word documents using the Document library (Python) and direct OOXML XML manipulation.

## Document Library Setup

```python
from scripts.document import Document, DocxXMLEditor

# Basic initialization (creates temp copy, sets up infrastructure)
doc = Document('unpacked')
# Custom author
doc = Document('unpacked', author="John Doe", initials="JD")
# Enable track revisions
doc = Document('unpacked', track_revisions=True)
# Custom RSID (auto-generated if omitted)
doc = Document('unpacked', rsid="07DC5ECB")
```

Run with PYTHONPATH set to the skill root:
```bash
PYTHONPATH=/path/to/docx-skill python your_script.py
```

## Finding Nodes

```python
# By text content
node = doc["word/document.xml"].get_node(tag="w:r", contains="target text")
# By line number (exact or range)
node = doc["word/document.xml"].get_node(tag="w:p", line_number=42)
node = doc["word/document.xml"].get_node(tag="w:p", line_number=range(100, 150))
# By attributes
node = doc["word/document.xml"].get_node(tag="w:del", attrs={"w:id": "1"})
# Combined filters (for disambiguation)
node = doc["word/document.xml"].get_node(
    tag="w:r", contains="Section", line_number=range(2400, 2500))
```

## Making Tracked Changes

### Minimal Edit Pattern

Only mark text that actually changes. Preserve original `<w:r>` elements for unchanged text.

```python
# Change "monthly" to "quarterly" in "The report is monthly"
node = doc["word/document.xml"].get_node(tag="w:r", contains="The report is monthly")
rpr = tags[0].toxml() if (tags := node.getElementsByTagName("w:rPr")) else ""
replacement = (
    f'<w:r w:rsidR="00AB12CD">{rpr}<w:t>The report is </w:t></w:r>'
    f'<w:del><w:r>{rpr}<w:delText>monthly</w:delText></w:r></w:del>'
    f'<w:ins><w:r>{rpr}<w:t>quarterly</w:t></w:r></w:ins>'
)
doc["word/document.xml"].replace_node(node, replacement)
```

### Insert New Content

```python
node = doc["word/document.xml"].get_node(tag="w:r", contains="existing text")
doc["word/document.xml"].insert_after(node, '<w:ins><w:r><w:t>new text</w:t></w:r></w:ins>')
```

### Delete Content

```python
# Delete entire run
node = doc["word/document.xml"].get_node(tag="w:r", contains="text to delete")
doc["word/document.xml"].suggest_deletion(node)

# Delete entire paragraph
para = doc["word/document.xml"].get_node(tag="w:p", contains="paragraph to delete")
doc["word/document.xml"].suggest_deletion(para)
```

### Reject Another Author's Insertion

```python
ins = doc["word/document.xml"].get_node(tag="w:ins", attrs={"w:id": "5"})
doc["word/document.xml"].revert_insertion(ins)
```

### Restore Another Author's Deletion

```python
del_elem = doc["word/document.xml"].get_node(tag="w:del", attrs={"w:id": "3"})
doc["word/document.xml"].revert_deletion(del_elem)
```

### Add New List Item

```python
target = doc["word/document.xml"].get_node(tag="w:p", contains="existing item")
pPr = tags[0].toxml() if (tags := target.getElementsByTagName("w:pPr")) else ""
new_item = f'<w:p>{pPr}<w:r><w:t>New item</w:t></w:r></w:p>'
tracked = DocxXMLEditor.suggest_paragraph(new_item)
doc["word/document.xml"].insert_after(target, tracked)
```

## Comments

```python
# Add comment spanning nodes
start = doc["word/document.xml"].get_node(tag="w:del", attrs={"w:id": "1"})
end = doc["word/document.xml"].get_node(tag="w:ins", attrs={"w:id": "2"})
doc.add_comment(start=start, end=end, text="Explanation of this change")

# Comment on a paragraph
para = doc["word/document.xml"].get_node(tag="w:p", contains="paragraph text")
doc.add_comment(start=para, end=para, text="Comment text")

# Reply to existing comment
doc.reply_to_comment(parent_comment_id=0, text="I agree with this change")
```

## Saving

```python
doc.save()                      # Validates and saves to original directory
doc.save('modified-unpacked')   # Save to different location
doc.save(validate=False)        # Skip validation (debugging only)
```

## XML Structure Reference

### Basic Paragraph
```xml
<w:p>
  <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
  <w:r><w:t>Text content</w:t></w:r>
</w:p>
```

### Element Order in `<w:pPr>`
`<w:pStyle>`, `<w:numPr>`, `<w:spacing>`, `<w:ind>`, `<w:jc>`

### Text Formatting
```xml
<w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Bold</w:t></w:r>
<w:r><w:rPr><w:i/><w:iCs/></w:rPr><w:t>Italic</w:t></w:r>
<w:r><w:rPr><w:highlight w:val="yellow"/></w:rPr><w:t>Highlighted</w:t></w:r>
```

### Tracked Change XML Patterns

**Insertion:**
```xml
<w:ins w:id="1" w:author="Claude" w:date="2025-07-30T23:05:00Z">
  <w:r w:rsidR="00792858"><w:t>inserted text</w:t></w:r>
</w:ins>
```

**Deletion:**
```xml
<w:del w:id="2" w:author="Claude" w:date="2025-07-30T23:05:00Z">
  <w:r w:rsidDel="00792858"><w:delText>deleted text</w:delText></w:r>
</w:del>
```

**Deleting Another Author's Insertion (nested structure):**
```xml
<w:ins w:author="Jane Smith" w:id="16">
  <w:del w:author="Claude" w:id="40">
    <w:r><w:delText>their text</w:delText></w:r>
  </w:del>
</w:ins>
<w:ins w:author="Claude" w:id="41">
  <w:r><w:t>replacement</w:t></w:r>
</w:ins>
```

### Whitespace and Encoding
- Add `xml:space='preserve'` to `<w:t>` elements with leading/trailing spaces
- Curly quotes: `&#8220;` and `&#8221;`; apostrophe: `&#8217;`; em-dash: `&#8212;`
- RSIDs must be 8-digit hex (0-9, A-F only)

### Key File Paths
| Path | Purpose |
|------|---------|
| `word/document.xml` | Main document body |
| `word/comments.xml` | Comments |
| `word/styles.xml` | Style definitions |
| `word/settings.xml` | Document settings |
| `word/numbering.xml` | List definitions |
| `word/media/` | Embedded images |
| `word/_rels/document.xml.rels` | Relationships |
| `[Content_Types].xml` | Content type declarations |
