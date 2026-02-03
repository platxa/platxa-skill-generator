# Odoo Form Field Types Reference

Complete reference for form field types and their HTML generation.

## Field Type Summary

| Type | HTML Input | Validation | Use Case |
|------|-----------|------------|----------|
| `text` | `<input type="text">` | Pattern optional | Names, subjects |
| `email` | `<input type="email">` | Email format | Email addresses |
| `tel` | `<input type="tel">` | Phone pattern | Phone numbers |
| `textarea` | `<textarea>` | None | Messages, descriptions |
| `select` | `<select>` | Required option | Dropdowns |
| `radio` | `<input type="radio">` | Required group | Single choice |
| `checkbox` | `<input type="checkbox">` | None | Boolean options |
| `file` | `<input type="file">` | Accept types | Attachments |
| `date` | `<input type="date">` | Min/max dates | Date selection |
| `number` | `<input type="number">` | Min/max values | Numeric input |

## Field Configuration

### Common Properties

```python
{
    'name': 'field_name',       # Required: Field identifier
    'label': 'Field Label',     # Required: Display label
    'type': 'text',             # Required: Field type
    'required': True,           # Optional: Validation
    'placeholder': 'Hint...',   # Optional: Placeholder text
    'autofill': 'email',        # Optional: Browser autofill hint
    'help_text': 'Helper text', # Optional: Help text below field
}
```

### Type-Specific Properties

**textarea:**
```python
{'rows': 5}  # Number of visible rows
```

**select / radio:**
```python
{'options': [('value1', 'Label 1'), ('value2', 'Label 2')]}
```

**file:**
```python
{'accept': '.pdf,.doc,.docx,.jpg,.png'}  # Accepted file types
```

**date / number:**
```python
{'min': '2024-01-01', 'max': '2024-12-31'}  # Range constraints
```

**text:**
```python
{'pattern': '[A-Za-z]+'}  # Regex pattern validation
```

## Autofill Hints

Odoo's `data-fill-with` attribute supports:

| Value | Description |
|-------|-------------|
| `name` | User's full name |
| `email` | User's email address |
| `phone` | User's phone number |
| `company` | User's company name |

## CRM Field Mapping

| Form Field | CRM Lead Field | Notes |
|------------|----------------|-------|
| `contact_name` | `contact_name` | Contact person |
| `email_from` | `email_from` | Primary email |
| `phone` | `phone` | Primary phone |
| `partner_name` | `partner_name` | Company name |
| `description` | `description` | Notes/message |
| `name` | `name` | Lead title (auto-generated) |

## Validation

### Client-Side (HTML5)

- `required` attribute for mandatory fields
- `type="email"` for email format
- `pattern` attribute for regex validation
- `min`/`max` for date/number ranges

### Server-Side (Odoo)

Odoo's website form controller validates:
- Required fields
- Email format
- File size limits
- CSRF token

## Accessibility

All generated fields include:

1. **Labels** - Properly associated with `for` attribute
2. **Required indicators** - Visual `*` marker
3. **Help text** - Using `<small>` elements
4. **Form structure** - Semantic HTML5
