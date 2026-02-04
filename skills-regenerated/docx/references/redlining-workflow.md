# Redlining Workflow Reference

Step-by-step reference for implementing tracked changes in Word documents.

## Batch Strategy

Group changes into batches of 3-10 related edits:

| Strategy | When to use | Example |
|----------|-------------|---------|
| By section | Document has clear sections | "Section 2 amendments" |
| By type | Changes share a category | "Date corrections" |
| By complexity | Mix of simple and complex | Simple text first, structural later |
| By proximity | Changes cluster together | "Pages 1-3 changes" |

## Location Methods

Find text in XML using these approaches (never use markdown line numbers):

- **Section/heading numbers**: "Section 3.2", "Article IV"
- **Paragraph identifiers**: Numbered paragraphs, clause numbers
- **Grep patterns**: `grep "unique surrounding text" word/document.xml`
- **Document structure**: "first paragraph after heading", "signature block"
- **Line number ranges**: `get_node(tag="w:r", line_number=range(100, 200))`

Always grep `word/document.xml` immediately before writing a script. Line numbers change after each script run.

## Verification Checklist

After applying all batches:

1. **Convert to markdown**: `pandoc --track-changes=all reviewed.docx -o verify.md`
2. **Check applied changes**:
   ```bash
   grep "replacement phrase" verify.md   # Should find it
   grep "original phrase" verify.md      # Should NOT find it (or show as deleted)
   ```
3. **Check for unintended changes**: Compare section by section
4. **Validate XML**: `doc.save()` runs automatic validation

## Validation Rules

The redlining validator checks that document text matches the original after reverting your changes:

- Never modify text inside another author's `<w:ins>` or `<w:del>` tags
- Always use nested deletions to remove another author's insertions
- Every edit must be tracked with `<w:ins>` or `<w:del>` tags
- `<w:del>` and `<w:ins>` go at paragraph level, containing complete `<w:r>` elements
- Never nest `<w:del>`/`<w:ins>` inside `<w:r>` elements

## Common Patterns

### Change a Single Word

```python
node = doc["word/document.xml"].get_node(tag="w:r", contains="within 30 days")
rpr = tags[0].toxml() if (tags := node.getElementsByTagName("w:rPr")) else ""
replacement = (
    f'<w:r w:rsidR="00XYZ789">{rpr}<w:t>within </w:t></w:r>'
    f'<w:del><w:r>{rpr}<w:delText>30</w:delText></w:r></w:del>'
    f'<w:ins><w:r>{rpr}<w:t>45</w:t></w:r></w:ins>'
    f'<w:r w:rsidR="00XYZ789">{rpr}<w:t> days</w:t></w:r>'
)
doc["word/document.xml"].replace_node(node, replacement)
```

### Add a Comment to a Change

```python
new_nodes = doc["word/document.xml"].replace_node(
    node,
    '<w:del><w:r><w:delText>old</w:delText></w:r></w:del>'
    '<w:ins><w:r><w:t>new</w:t></w:r></w:ins>'
)
doc.add_comment(start=new_nodes[0], end=new_nodes[1],
    text="Changed per requirements")
```

### Insert Image with Tracked Changes

```python
from PIL import Image
import shutil, os

media_dir = os.path.join(doc.unpacked_path, 'word/media')
os.makedirs(media_dir, exist_ok=True)
shutil.copy('image.png', os.path.join(media_dir, 'image1.png'))

img = Image.open(os.path.join(media_dir, 'image1.png'))
width_emus = int(6.5 * 914400)  # 6.5" usable width
height_emus = int(width_emus * img.size[1] / img.size[0])

rels = doc['word/_rels/document.xml.rels']
rid = rels.get_next_rid()
rels.append_to(rels.dom.documentElement,
    f'<Relationship Id="{rid}" '
    f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
    f'Target="media/image1.png"/>')
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Document fails to open | Invalid XML nesting | Check `<w:del>`/`<w:ins>` are at paragraph level, not inside `<w:r>` |
| Changes not visible | Missing trackRevisions setting | Initialize with `track_revisions=True` |
| Wrong author shown | Default author used | Pass `author="Name"` to Document constructor |
| Validation fails | Text mismatch after revert | Ensure unchanged text is preserved outside tracked change tags |
| RSID errors | Invalid format | Use 8-digit hex values (0-9, A-F only) |
