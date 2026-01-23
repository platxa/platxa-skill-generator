---
name: platxa-odoo-form
description: Generate Odoo website forms with CRM lead integration, field validation, conditional logic, and multi-step wizards.
version: 1.0.0
allowed-tools: Read, Write, Glob, Grep
---

# Platxa Odoo Form Generator

Generate production-ready Odoo website forms with CRM integration, field validation, and advanced form features.

## Overview

This skill creates Odoo website forms that integrate seamlessly with Odoo's CRM and other modules. Forms include:

- QWeb form templates with Bootstrap 5 styling
- Server-side validation with Python controllers
- CRM lead creation on submission
- Email notifications
- Success/error page handling
- Optional multi-step wizard layouts

## Supported Form Types

| Type | Model | Use Case |
|------|-------|----------|
| `contact` | `crm.lead` | General contact/inquiry form |
| `quote` | `crm.lead` | Quote/estimate request |
| `newsletter` | `mailing.contact` | Email newsletter signup |
| `callback` | `crm.lead` | Request callback form |
| `support` | `helpdesk.ticket` | Support ticket submission |
| `feedback` | `survey.user_input` | Customer feedback |
| `appointment` | `calendar.event` | Appointment booking |
| `custom` | Custom model | Any custom form |

## Workflow

### Step 1: Determine Form Type and Fields

Analyze user request to identify form type and required fields:

```python
FORM_TEMPLATES = {
    'contact': {
        'model': 'crm.lead',
        'fields': ['name', 'email', 'phone', 'company', 'subject', 'message'],
        'required': ['name', 'email', 'message'],
    },
    'quote': {
        'model': 'crm.lead',
        'fields': ['name', 'email', 'phone', 'company', 'service', 'budget', 'timeline', 'message'],
        'required': ['name', 'email', 'service'],
    },
    'newsletter': {
        'model': 'mailing.contact',
        'fields': ['name', 'email'],
        'required': ['email'],
    },
    'callback': {
        'model': 'crm.lead',
        'fields': ['name', 'phone', 'preferred_time', 'message'],
        'required': ['name', 'phone'],
    },
}
```

### Step 2: Generate Form Template

Create the QWeb form template:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="form_contact" name="Contact Form">
        <t t-call="website.layout">
            <div id="wrap" class="oe_structure">
                <section class="s_website_form pt64 pb64">
                    <div class="container">
                        <div class="row justify-content-center">
                            <div class="col-lg-8">
                                <div class="card border-0 shadow">
                                    <div class="card-body p-5">
                                        <h2 class="text-center mb-4">Contact Us</h2>

                                        <form action="/website/form/"
                                              method="post"
                                              class="s_website_form_form"
                                              data-model_name="crm.lead"
                                              data-success_mode="redirect"
                                              data-success_page="/contact-thank-you"
                                              enctype="multipart/form-data">

                                            <input type="hidden" name="csrf_token"
                                                   t-att-value="request.csrf_token()"/>

                                            <!-- Name Field -->
                                            <div class="mb-3">
                                                <label class="form-label" for="contact_name">
                                                    Name <span class="text-danger">*</span>
                                                </label>
                                                <input type="text"
                                                       class="form-control"
                                                       id="contact_name"
                                                       name="contact_name"
                                                       required="required"
                                                       data-fill-with="name"/>
                                            </div>

                                            <!-- Email Field -->
                                            <div class="mb-3">
                                                <label class="form-label" for="email_from">
                                                    Email <span class="text-danger">*</span>
                                                </label>
                                                <input type="email"
                                                       class="form-control"
                                                       id="email_from"
                                                       name="email_from"
                                                       required="required"
                                                       data-fill-with="email"/>
                                            </div>

                                            <!-- Phone Field -->
                                            <div class="mb-3">
                                                <label class="form-label" for="phone">Phone</label>
                                                <input type="tel"
                                                       class="form-control"
                                                       id="phone"
                                                       name="phone"
                                                       data-fill-with="phone"/>
                                            </div>

                                            <!-- Message Field -->
                                            <div class="mb-4">
                                                <label class="form-label" for="description">
                                                    Message <span class="text-danger">*</span>
                                                </label>
                                                <textarea class="form-control"
                                                          id="description"
                                                          name="description"
                                                          rows="5"
                                                          required="required"/>
                                            </div>

                                            <!-- Submit Button -->
                                            <div class="text-center">
                                                <button type="submit"
                                                        class="btn btn-primary btn-lg px-5">
                                                    Send Message
                                                </button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </t>
    </template>
</odoo>
```

### Step 3: Create Success Page

Generate thank-you/success page:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="form_contact_success" name="Contact Form Success">
        <t t-call="website.layout">
            <div id="wrap" class="oe_structure">
                <section class="s_text_block pt96 pb96">
                    <div class="container text-center">
                        <div class="mb-4">
                            <i class="fa fa-check-circle fa-5x text-success"/>
                        </div>
                        <h1 class="display-4 mb-3">Thank You!</h1>
                        <p class="lead text-muted mb-4">
                            Your message has been received. We'll get back to you shortly.
                        </p>
                        <a href="/" class="btn btn-primary">Return to Home</a>
                    </div>
                </section>
            </div>
        </t>
    </template>

    <record id="page_contact_success" model="website.page">
        <field name="url">/contact-thank-you</field>
        <field name="name">Contact Success</field>
        <field name="website_published">True</field>
        <field name="website_indexed">False</field>
        <field name="view_id" ref="form_contact_success"/>
    </record>
</odoo>
```

### Step 4: Configure Form Action (Optional Controller)

For advanced validation or custom logic, create a controller:

```python
from odoo import http
from odoo.http import request


class WebsiteFormController(http.Controller):

    @http.route('/website/form/contact', type='http', auth='public',
                methods=['POST'], website=True, csrf=True)
    def contact_form_submit(self, **kwargs):
        """Handle contact form submission with custom validation."""
        # Validate required fields
        errors = []
        if not kwargs.get('contact_name'):
            errors.append('Name is required')
        if not kwargs.get('email_from'):
            errors.append('Email is required')
        elif not self._validate_email(kwargs['email_from']):
            errors.append('Invalid email format')
        if not kwargs.get('description'):
            errors.append('Message is required')

        if errors:
            return request.render('theme_name.form_contact', {
                'errors': errors,
                'form_data': kwargs,
            })

        # Create CRM lead
        lead_vals = {
            'name': f"Website Contact: {kwargs.get('contact_name')}",
            'contact_name': kwargs.get('contact_name'),
            'email_from': kwargs.get('email_from'),
            'phone': kwargs.get('phone'),
            'description': kwargs.get('description'),
            'type': 'lead',
            'source_id': request.env.ref('utm.utm_source_website').id,
        }

        lead = request.env['crm.lead'].sudo().create(lead_vals)

        # Send notification email (optional)
        template = request.env.ref('theme_name.email_template_contact_form')
        if template:
            template.sudo().send_mail(lead.id)

        return request.redirect('/contact-thank-you')

    def _validate_email(self, email):
        """Basic email validation."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
```

## Field Types

### Text Input

```xml
<div class="mb-3">
    <label class="form-label" for="field_name">Label</label>
    <input type="text" class="form-control" id="field_name" name="field_name"/>
</div>
```

### Email Input

```xml
<div class="mb-3">
    <label class="form-label" for="email_from">Email *</label>
    <input type="email" class="form-control" id="email_from" name="email_from"
           required="required" data-fill-with="email"/>
</div>
```

### Phone Input

```xml
<div class="mb-3">
    <label class="form-label" for="phone">Phone</label>
    <input type="tel" class="form-control" id="phone" name="phone"
           pattern="[0-9+\-\s()]*" data-fill-with="phone"/>
</div>
```

### Textarea

```xml
<div class="mb-3">
    <label class="form-label" for="description">Message</label>
    <textarea class="form-control" id="description" name="description" rows="5"/>
</div>
```

### Select Dropdown

```xml
<div class="mb-3">
    <label class="form-label" for="service">Service *</label>
    <select class="form-select" id="service" name="service" required="required">
        <option value="">Select a service...</option>
        <option value="consulting">Consulting</option>
        <option value="development">Development</option>
        <option value="support">Support</option>
    </select>
</div>
```

### Radio Buttons

```xml
<div class="mb-3">
    <label class="form-label d-block">Budget Range</label>
    <div class="form-check form-check-inline">
        <input class="form-check-input" type="radio" name="budget" id="budget1" value="small"/>
        <label class="form-check-label" for="budget1">$1k - $5k</label>
    </div>
    <div class="form-check form-check-inline">
        <input class="form-check-input" type="radio" name="budget" id="budget2" value="medium"/>
        <label class="form-check-label" for="budget2">$5k - $20k</label>
    </div>
    <div class="form-check form-check-inline">
        <input class="form-check-input" type="radio" name="budget" id="budget3" value="large"/>
        <label class="form-check-label" for="budget3">$20k+</label>
    </div>
</div>
```

### Checkbox

```xml
<div class="mb-3">
    <div class="form-check">
        <input class="form-check-input" type="checkbox" id="newsletter" name="newsletter" value="1"/>
        <label class="form-check-label" for="newsletter">
            Subscribe to our newsletter
        </label>
    </div>
</div>
```

### File Upload

```xml
<div class="mb-3">
    <label class="form-label" for="attachment">Attachment</label>
    <input type="file" class="form-control" id="attachment" name="attachment"
           accept=".pdf,.doc,.docx,.jpg,.png"/>
    <small class="text-muted">Max file size: 10MB. Allowed: PDF, DOC, JPG, PNG</small>
</div>
```

### Date Picker

```xml
<div class="mb-3">
    <label class="form-label" for="preferred_date">Preferred Date</label>
    <input type="date" class="form-control" id="preferred_date" name="preferred_date"
           min="today"/>
</div>
```

## Multi-Step Forms

### Wizard Template

```xml
<form class="s_website_form_form multi-step-form" data-model_name="crm.lead">
    <!-- Step 1: Personal Info -->
    <div class="form-step" data-step="1">
        <h4 class="mb-4">Step 1: Your Information</h4>
        <!-- Fields -->
        <div class="d-flex justify-content-end">
            <button type="button" class="btn btn-primary btn-next">Next</button>
        </div>
    </div>

    <!-- Step 2: Project Details -->
    <div class="form-step d-none" data-step="2">
        <h4 class="mb-4">Step 2: Project Details</h4>
        <!-- Fields -->
        <div class="d-flex justify-content-between">
            <button type="button" class="btn btn-secondary btn-prev">Back</button>
            <button type="button" class="btn btn-primary btn-next">Next</button>
        </div>
    </div>

    <!-- Step 3: Confirmation -->
    <div class="form-step d-none" data-step="3">
        <h4 class="mb-4">Step 3: Confirm &amp; Submit</h4>
        <!-- Summary -->
        <div class="d-flex justify-content-between">
            <button type="button" class="btn btn-secondary btn-prev">Back</button>
            <button type="submit" class="btn btn-primary">Submit</button>
        </div>
    </div>

    <!-- Progress Indicator -->
    <div class="progress mt-4" style="height: 4px;">
        <div class="progress-bar" role="progressbar" style="width: 33%;"/>
    </div>
</form>
```

## CRM Field Mapping

| Form Field | CRM Lead Field | Description |
|------------|----------------|-------------|
| `contact_name` | `contact_name` | Contact person name |
| `email_from` | `email_from` | Email address |
| `phone` | `phone` | Phone number |
| `company` | `partner_name` | Company name |
| `description` | `description` | Message/notes |
| `subject` | `name` | Lead name/subject |
| `source` | `source_id` | UTM source |

## Usage Examples

### Generate Contact Form

```bash
python scripts/generate_form.py \
    --type contact \
    --module theme_company \
    --title "Get In Touch"
```

### Generate Quote Request Form

```bash
python scripts/generate_form.py \
    --type quote \
    --module theme_company \
    --fields name,email,phone,company,service,budget,timeline,message \
    --required name,email,service
```

### Generate Newsletter Signup

```bash
python scripts/generate_form.py \
    --type newsletter \
    --module theme_company \
    --style inline \
    --title "Stay Updated"
```

## Integration

### With platxa-odoo-page

Forms can be embedded in generated pages:

```python
# In page generation
1. Generate page with contact_form section
2. Section references form template
3. Form auto-integrates with page layout
```

### With platxa-odoo-theme

Forms inherit theme styling:

```scss
// Forms use theme's primary_variables.scss
.s_website_form .btn-primary {
    background-color: $o-color-1;
}
```

## Best Practices

1. **Validation** - Always validate server-side, client-side is optional enhancement
2. **CSRF Protection** - Include `csrf_token` in all forms
3. **Spam Prevention** - Consider honeypot fields or reCAPTCHA integration
4. **Accessibility** - Use proper labels, required indicators, error messages
5. **Mobile** - Ensure forms work well on mobile devices
6. **Performance** - Lazy load file upload components
