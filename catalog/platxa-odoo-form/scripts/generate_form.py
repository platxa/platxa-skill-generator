#!/usr/bin/env python3
"""
Platxa Odoo Form Generator

Generates production-ready Odoo website forms with:
- QWeb form templates with Bootstrap 5 styling
- CRM lead integration
- Success page templates
- Field validation
- Multi-step wizard support
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
from xml.sax.saxutils import escape as xml_escape


# ============================================================================
# Form Type Definitions
# ============================================================================

FieldType = Literal['text', 'email', 'tel', 'textarea', 'select', 'radio', 'checkbox', 'file', 'date', 'number']

FORM_TEMPLATES: dict[str, dict[str, object]] = {
    'contact': {
        'model': 'crm.lead',
        'title': 'Contact Us',
        'success_message': 'Thank you! Your message has been received.',
        'fields': [
            {'name': 'contact_name', 'label': 'Name', 'type': 'text', 'required': True, 'autofill': 'name'},
            {'name': 'email_from', 'label': 'Email', 'type': 'email', 'required': True, 'autofill': 'email'},
            {'name': 'phone', 'label': 'Phone', 'type': 'tel', 'required': False, 'autofill': 'phone'},
            {'name': 'description', 'label': 'Message', 'type': 'textarea', 'required': True, 'rows': 5},
        ],
    },
    'quote': {
        'model': 'crm.lead',
        'title': 'Request a Quote',
        'success_message': 'Thank you! We\'ll send your quote within 24 hours.',
        'fields': [
            {'name': 'contact_name', 'label': 'Name', 'type': 'text', 'required': True, 'autofill': 'name'},
            {'name': 'email_from', 'label': 'Email', 'type': 'email', 'required': True, 'autofill': 'email'},
            {'name': 'phone', 'label': 'Phone', 'type': 'tel', 'required': False, 'autofill': 'phone'},
            {'name': 'partner_name', 'label': 'Company', 'type': 'text', 'required': False},
            {'name': 'service', 'label': 'Service', 'type': 'select', 'required': True,
             'options': [('consulting', 'Consulting'), ('development', 'Development'), ('support', 'Support')]},
            {'name': 'budget', 'label': 'Budget Range', 'type': 'radio', 'required': False,
             'options': [('small', '$1k - $5k'), ('medium', '$5k - $20k'), ('large', '$20k+')]},
            {'name': 'description', 'label': 'Project Details', 'type': 'textarea', 'required': True, 'rows': 5},
        ],
    },
    'newsletter': {
        'model': 'mailing.contact',
        'title': 'Subscribe to Newsletter',
        'success_message': 'You\'re subscribed! Check your email to confirm.',
        'fields': [
            {'name': 'name', 'label': 'Name', 'type': 'text', 'required': False},
            {'name': 'email', 'label': 'Email', 'type': 'email', 'required': True, 'autofill': 'email'},
        ],
    },
    'callback': {
        'model': 'crm.lead',
        'title': 'Request a Callback',
        'success_message': 'Thank you! We\'ll call you at your preferred time.',
        'fields': [
            {'name': 'contact_name', 'label': 'Name', 'type': 'text', 'required': True, 'autofill': 'name'},
            {'name': 'phone', 'label': 'Phone', 'type': 'tel', 'required': True, 'autofill': 'phone'},
            {'name': 'preferred_time', 'label': 'Preferred Time', 'type': 'select', 'required': False,
             'options': [('morning', 'Morning (9am-12pm)'), ('afternoon', 'Afternoon (12pm-5pm)'), ('evening', 'Evening (5pm-8pm)')]},
            {'name': 'description', 'label': 'Notes', 'type': 'textarea', 'required': False, 'rows': 3},
        ],
    },
    'feedback': {
        'model': 'mail.mail',
        'title': 'Share Your Feedback',
        'success_message': 'Thank you for your feedback!',
        'fields': [
            {'name': 'name', 'label': 'Name', 'type': 'text', 'required': False},
            {'name': 'email_from', 'label': 'Email', 'type': 'email', 'required': True, 'autofill': 'email'},
            {'name': 'rating', 'label': 'Rating', 'type': 'radio', 'required': True,
             'options': [('5', 'Excellent'), ('4', 'Good'), ('3', 'Average'), ('2', 'Poor'), ('1', 'Very Poor')]},
            {'name': 'body_html', 'label': 'Comments', 'type': 'textarea', 'required': False, 'rows': 4},
        ],
    },
}


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class FormField:
    """Configuration for a single form field."""
    name: str
    label: str
    field_type: FieldType = 'text'
    required: bool = False
    placeholder: str = ''
    autofill: str = ''
    rows: int = 4
    options: list[tuple[str, str]] = field(default_factory=list)
    pattern: str = ''
    min_value: str = ''
    max_value: str = ''
    accept: str = ''
    help_text: str = ''

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> 'FormField':
        """Create FormField from dictionary."""
        # Extract rows with proper type handling
        rows_val = data.get('rows', 4)
        rows = int(rows_val) if isinstance(rows_val, (int, float, str)) else 4

        # Extract options with proper type handling
        options_val = data.get('options', [])
        options: list[tuple[str, str]] = []
        if isinstance(options_val, list):
            for opt in options_val:
                if isinstance(opt, (list, tuple)) and len(opt) >= 2:
                    options.append((str(opt[0]), str(opt[1])))

        return cls(
            name=str(data.get('name', '')),
            label=str(data.get('label', '')),
            field_type=str(data.get('type', 'text')),  # type: ignore[arg-type]
            required=bool(data.get('required', False)),
            placeholder=str(data.get('placeholder', '')),
            autofill=str(data.get('autofill', '')),
            rows=rows,
            options=options,
            pattern=str(data.get('pattern', '')),
            min_value=str(data.get('min', '')),
            max_value=str(data.get('max', '')),
            accept=str(data.get('accept', '')),
            help_text=str(data.get('help_text', '')),
        )


@dataclass
class FormConfig:
    """Configuration for a form."""
    form_type: str
    module_name: str
    title: str = ''
    model: str = ''
    success_url: str = ''
    success_message: str = ''
    fields: list[FormField] = field(default_factory=list)
    style: str = 'card'  # card, inline, full-width
    submit_label: str = 'Submit'

    def __post_init__(self) -> None:
        """Apply defaults based on form type."""
        template = FORM_TEMPLATES.get(self.form_type, {})

        if not self.title:
            self.title = str(template.get('title', f'{self.form_type.title()} Form'))
        if not self.model:
            self.model = str(template.get('model', 'mail.mail'))
        if not self.success_message:
            self.success_message = str(template.get('success_message', 'Thank you for your submission!'))
        if not self.success_url:
            self.success_url = f'/{self.form_type}-thank-you'
        if not self.fields:
            field_dicts = template.get('fields', [])
            if isinstance(field_dicts, list):
                self.fields = [FormField.from_dict(f) for f in field_dicts if isinstance(f, dict)]

    @property
    def template_id(self) -> str:
        """Generate template ID."""
        return f'form_{self.form_type}'

    @property
    def success_template_id(self) -> str:
        """Generate success page template ID."""
        return f'form_{self.form_type}_success'

    @property
    def success_page_id(self) -> str:
        """Generate success page record ID."""
        return f'page_{self.form_type}_success'


# ============================================================================
# Field Generators
# ============================================================================

class FieldGenerator:
    """Generates HTML for form fields."""

    @staticmethod
    def text(f: FormField) -> str:
        """Generate text input field."""
        required = ' required="required"' if f.required else ''
        autofill = f' data-fill-with="{f.autofill}"' if f.autofill else ''
        placeholder = f' placeholder="{xml_escape(f.placeholder)}"' if f.placeholder else ''
        pattern = f' pattern="{f.pattern}"' if f.pattern else ''

        req_marker = ' <span class="text-danger">*</span>' if f.required else ''

        return f'''
                                            <div class="mb-3">
                                                <label class="form-label" for="{f.name}">
                                                    {xml_escape(f.label)}{req_marker}
                                                </label>
                                                <input type="text"
                                                       class="form-control"
                                                       id="{f.name}"
                                                       name="{f.name}"{required}{autofill}{placeholder}{pattern}/>
                                            </div>'''

    @staticmethod
    def email(f: FormField) -> str:
        """Generate email input field."""
        required = ' required="required"' if f.required else ''
        autofill = f' data-fill-with="{f.autofill}"' if f.autofill else ''
        placeholder = f' placeholder="{xml_escape(f.placeholder)}"' if f.placeholder else ''

        req_marker = ' <span class="text-danger">*</span>' if f.required else ''

        return f'''
                                            <div class="mb-3">
                                                <label class="form-label" for="{f.name}">
                                                    {xml_escape(f.label)}{req_marker}
                                                </label>
                                                <input type="email"
                                                       class="form-control"
                                                       id="{f.name}"
                                                       name="{f.name}"{required}{autofill}{placeholder}/>
                                            </div>'''

    @staticmethod
    def tel(f: FormField) -> str:
        """Generate phone input field."""
        required = ' required="required"' if f.required else ''
        autofill = f' data-fill-with="{f.autofill}"' if f.autofill else ''
        placeholder = f' placeholder="{xml_escape(f.placeholder)}"' if f.placeholder else ''

        req_marker = ' <span class="text-danger">*</span>' if f.required else ''

        return f'''
                                            <div class="mb-3">
                                                <label class="form-label" for="{f.name}">
                                                    {xml_escape(f.label)}{req_marker}
                                                </label>
                                                <input type="tel"
                                                       class="form-control"
                                                       id="{f.name}"
                                                       name="{f.name}"
                                                       pattern="[0-9+\\-\\s()]*"{required}{autofill}{placeholder}/>
                                            </div>'''

    @staticmethod
    def textarea(f: FormField) -> str:
        """Generate textarea field."""
        required = ' required="required"' if f.required else ''
        placeholder = f' placeholder="{xml_escape(f.placeholder)}"' if f.placeholder else ''

        req_marker = ' <span class="text-danger">*</span>' if f.required else ''

        return f'''
                                            <div class="mb-3">
                                                <label class="form-label" for="{f.name}">
                                                    {xml_escape(f.label)}{req_marker}
                                                </label>
                                                <textarea class="form-control"
                                                          id="{f.name}"
                                                          name="{f.name}"
                                                          rows="{f.rows}"{required}{placeholder}/>
                                            </div>'''

    @staticmethod
    def select(f: FormField) -> str:
        """Generate select dropdown field."""
        required = ' required="required"' if f.required else ''
        req_marker = ' <span class="text-danger">*</span>' if f.required else ''

        options_html = '\n                                                    <option value="">Select...</option>'
        for value, label in f.options:
            options_html += f'\n                                                    <option value="{xml_escape(value)}">{xml_escape(label)}</option>'

        return f'''
                                            <div class="mb-3">
                                                <label class="form-label" for="{f.name}">
                                                    {xml_escape(f.label)}{req_marker}
                                                </label>
                                                <select class="form-select"
                                                        id="{f.name}"
                                                        name="{f.name}"{required}>{options_html}
                                                </select>
                                            </div>'''

    @staticmethod
    def radio(f: FormField) -> str:
        """Generate radio button group."""
        req_marker = ' <span class="text-danger">*</span>' if f.required else ''
        required = ' required="required"' if f.required else ''

        options_html = ''
        for i, (value, label) in enumerate(f.options):
            options_html += f'''
                                                <div class="form-check form-check-inline">
                                                    <input class="form-check-input" type="radio"
                                                           name="{f.name}" id="{f.name}_{i}"
                                                           value="{xml_escape(value)}"{required}/>
                                                    <label class="form-check-label" for="{f.name}_{i}">
                                                        {xml_escape(label)}
                                                    </label>
                                                </div>'''

        return f'''
                                            <div class="mb-3">
                                                <label class="form-label d-block">
                                                    {xml_escape(f.label)}{req_marker}
                                                </label>{options_html}
                                            </div>'''

    @staticmethod
    def checkbox(f: FormField) -> str:
        """Generate checkbox field."""
        return f'''
                                            <div class="mb-3">
                                                <div class="form-check">
                                                    <input class="form-check-input" type="checkbox"
                                                           id="{f.name}" name="{f.name}" value="1"/>
                                                    <label class="form-check-label" for="{f.name}">
                                                        {xml_escape(f.label)}
                                                    </label>
                                                </div>
                                            </div>'''

    @staticmethod
    def file(f: FormField) -> str:
        """Generate file upload field."""
        required = ' required="required"' if f.required else ''
        accept = f' accept="{f.accept}"' if f.accept else ' accept=".pdf,.doc,.docx,.jpg,.png"'
        req_marker = ' <span class="text-danger">*</span>' if f.required else ''

        help_text = f.help_text or 'Max file size: 10MB'

        return f'''
                                            <div class="mb-3">
                                                <label class="form-label" for="{f.name}">
                                                    {xml_escape(f.label)}{req_marker}
                                                </label>
                                                <input type="file"
                                                       class="form-control"
                                                       id="{f.name}"
                                                       name="{f.name}"{required}{accept}/>
                                                <small class="text-muted">{xml_escape(help_text)}</small>
                                            </div>'''

    @staticmethod
    def date(f: FormField) -> str:
        """Generate date input field."""
        required = ' required="required"' if f.required else ''
        min_val = f' min="{f.min_value}"' if f.min_value else ''
        max_val = f' max="{f.max_value}"' if f.max_value else ''
        req_marker = ' <span class="text-danger">*</span>' if f.required else ''

        return f'''
                                            <div class="mb-3">
                                                <label class="form-label" for="{f.name}">
                                                    {xml_escape(f.label)}{req_marker}
                                                </label>
                                                <input type="date"
                                                       class="form-control"
                                                       id="{f.name}"
                                                       name="{f.name}"{required}{min_val}{max_val}/>
                                            </div>'''

    @staticmethod
    def number(f: FormField) -> str:
        """Generate number input field."""
        required = ' required="required"' if f.required else ''
        min_val = f' min="{f.min_value}"' if f.min_value else ''
        max_val = f' max="{f.max_value}"' if f.max_value else ''
        placeholder = f' placeholder="{xml_escape(f.placeholder)}"' if f.placeholder else ''
        req_marker = ' <span class="text-danger">*</span>' if f.required else ''

        return f'''
                                            <div class="mb-3">
                                                <label class="form-label" for="{f.name}">
                                                    {xml_escape(f.label)}{req_marker}
                                                </label>
                                                <input type="number"
                                                       class="form-control"
                                                       id="{f.name}"
                                                       name="{f.name}"{required}{min_val}{max_val}{placeholder}/>
                                            </div>'''

    def generate_field(self, f: FormField) -> str:
        """Generate HTML for a field based on its type."""
        method = getattr(self, f.field_type, None)
        if method is not None and callable(method):
            result = method(f)
            if isinstance(result, str):
                return result
            return str(result)
        return self.text(f)


# ============================================================================
# Template Generators
# ============================================================================

class FormXMLGenerator:
    """Generates Odoo form XML files."""

    def __init__(self) -> None:
        self.field_gen = FieldGenerator()

    def generate_form_template(self, config: FormConfig) -> str:
        """Generate QWeb form template."""
        fields_html = ''.join(
            self.field_gen.generate_field(f)
            for f in config.fields
        )

        if config.style == 'inline':
            return self._generate_inline_form(config, fields_html)
        elif config.style == 'full-width':
            return self._generate_fullwidth_form(config, fields_html)
        else:
            return self._generate_card_form(config, fields_html)

    def _generate_card_form(self, config: FormConfig, fields_html: str) -> str:
        """Generate card-style form."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="{config.template_id}" name="{xml_escape(config.title)}">
        <t t-call="website.layout">
            <div id="wrap" class="oe_structure">
                <section class="s_website_form pt64 pb64">
                    <div class="container">
                        <div class="row justify-content-center">
                            <div class="col-lg-8">
                                <div class="card border-0 shadow">
                                    <div class="card-body p-5">
                                        <h2 class="text-center mb-4">{xml_escape(config.title)}</h2>

                                        <form action="/website/form/"
                                              method="post"
                                              class="s_website_form_form"
                                              data-model_name="{config.model}"
                                              data-success_mode="redirect"
                                              data-success_page="{config.success_url}"
                                              enctype="multipart/form-data">

                                            <input type="hidden" name="csrf_token"
                                                   t-att-value="request.csrf_token()"/>
{fields_html}
                                            <!-- Submit Button -->
                                            <div class="text-center mt-4">
                                                <button type="submit"
                                                        class="btn btn-primary btn-lg px-5">
                                                    {xml_escape(config.submit_label)}
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
'''

    def _generate_inline_form(self, config: FormConfig, fields_html: str) -> str:
        """Generate inline-style form (e.g., newsletter)."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="{config.template_id}" name="{xml_escape(config.title)}">
        <section class="s_website_form pt32 pb32 o_cc o_cc5">
            <div class="container">
                <div class="row justify-content-center align-items-center">
                    <div class="col-lg-6 text-center text-lg-start mb-3 mb-lg-0">
                        <h4 class="mb-1">{xml_escape(config.title)}</h4>
                        <p class="text-muted mb-0">Stay updated with our latest news</p>
                    </div>
                    <div class="col-lg-6">
                        <form action="/website/form/"
                              method="post"
                              class="s_website_form_form d-flex gap-2"
                              data-model_name="{config.model}"
                              data-success_mode="redirect"
                              data-success_page="{config.success_url}">

                            <input type="hidden" name="csrf_token"
                                   t-att-value="request.csrf_token()"/>

                            <input type="email"
                                   class="form-control"
                                   name="email"
                                   placeholder="Enter your email"
                                   required="required"/>

                            <button type="submit" class="btn btn-primary px-4">
                                Subscribe
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </section>
    </template>
</odoo>
'''

    def _generate_fullwidth_form(self, config: FormConfig, fields_html: str) -> str:
        """Generate full-width form."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="{config.template_id}" name="{xml_escape(config.title)}">
        <t t-call="website.layout">
            <div id="wrap" class="oe_structure">
                <section class="s_website_form pt64 pb64">
                    <div class="container">
                        <div class="row">
                            <div class="col-12">
                                <h2 class="text-center mb-5">{xml_escape(config.title)}</h2>

                                <form action="/website/form/"
                                      method="post"
                                      class="s_website_form_form"
                                      data-model_name="{config.model}"
                                      data-success_mode="redirect"
                                      data-success_page="{config.success_url}"
                                      enctype="multipart/form-data">

                                    <input type="hidden" name="csrf_token"
                                           t-att-value="request.csrf_token()"/>

                                    <div class="row">
{fields_html}
                                    </div>

                                    <!-- Submit Button -->
                                    <div class="text-center mt-4">
                                        <button type="submit"
                                                class="btn btn-primary btn-lg px-5">
                                            {xml_escape(config.submit_label)}
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </t>
    </template>
</odoo>
'''

    def generate_success_template(self, config: FormConfig) -> str:
        """Generate success/thank-you page template."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="{config.success_template_id}" name="{xml_escape(config.title)} Success">
        <t t-call="website.layout">
            <div id="wrap" class="oe_structure">
                <section class="s_text_block pt96 pb96">
                    <div class="container text-center">
                        <div class="mb-4">
                            <i class="fa fa-check-circle fa-5x text-success"/>
                        </div>
                        <h1 class="display-4 mb-3">Thank You!</h1>
                        <p class="lead text-muted mb-4">
                            {xml_escape(config.success_message)}
                        </p>
                        <a href="/" class="btn btn-primary">Return to Home</a>
                    </div>
                </section>
            </div>
        </t>
    </template>

    <record id="{config.success_page_id}" model="website.page">
        <field name="url">{config.success_url}</field>
        <field name="name">{xml_escape(config.title)} - Thank You</field>
        <field name="website_published">True</field>
        <field name="website_indexed">False</field>
        <field name="view_id" ref="{config.success_template_id}"/>
    </record>
</odoo>
'''


# ============================================================================
# File Operations
# ============================================================================

def validate_output_path(output_path: Path, base_dir: Path) -> bool:
    """Validate output path is within allowed directory."""
    try:
        resolved_output = output_path.resolve()
        resolved_base = base_dir.resolve()
        return str(resolved_output).startswith(str(resolved_base))
    except (OSError, ValueError):
        return False


def generate_form(config: FormConfig, output_dir: Path) -> dict[str, Path]:
    """Generate all files for a form."""
    cwd = Path.cwd()
    if not validate_output_path(output_dir, cwd):
        raise ValueError(f'Output directory must be within {cwd}')

    generator = FormXMLGenerator()
    files_created: dict[str, Path] = {}

    views_dir = output_dir / 'views' / 'forms'
    views_dir.mkdir(parents=True, exist_ok=True)

    # Generate form template
    form_file = views_dir / f'form_{config.form_type}.xml'
    form_file.write_text(generator.generate_form_template(config))
    files_created['form_template'] = form_file

    # Generate success page
    success_file = views_dir / f'form_{config.form_type}_success.xml'
    success_file.write_text(generator.generate_success_template(config))
    files_created['success_template'] = success_file

    return files_created


# ============================================================================
# CLI Interface
# ============================================================================

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate Odoo website forms with CRM integration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s --type contact --module theme_company
  %(prog)s --type quote --module theme_company --title "Get a Quote"
  %(prog)s --type newsletter --module theme_company --style inline
        ''',
    )

    parser.add_argument(
        '--type',
        choices=list(FORM_TEMPLATES.keys()),
        help='Form type to generate',
    )
    parser.add_argument(
        '--module',
        help='Odoo module name (e.g., theme_company)',
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('.'),
        help='Output directory (default: current directory)',
    )
    parser.add_argument(
        '--title',
        help='Custom form title',
    )
    parser.add_argument(
        '--style',
        choices=['card', 'inline', 'full-width'],
        default='card',
        help='Form layout style (default: card)',
    )
    parser.add_argument(
        '--submit-label',
        default='Submit',
        help='Submit button label (default: Submit)',
    )
    parser.add_argument(
        '--list-types',
        action='store_true',
        help='List available form types and exit',
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON',
    )

    args = parser.parse_args()

    # List types
    if args.list_types:
        print('Available form types:')
        for form_type, template in FORM_TEMPLATES.items():
            title = template.get('title', form_type.title())
            model = template.get('model', 'mail.mail')
            fields_data = template.get('fields', [])
            field_count = len(fields_data) if isinstance(fields_data, list) else 0
            print(f'  {form_type}: {title}')
            print(f'    Model: {model}, Fields: {field_count}')
        return 0

    # Validate arguments
    if not args.type:
        parser.error('--type is required')
    if not args.module:
        parser.error('--module is required when generating forms')

    config = FormConfig(
        form_type=args.type,
        module_name=args.module,
        title=args.title or '',
        style=args.style,
        submit_label=args.submit_label,
    )

    try:
        files = generate_form(config, args.output)
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        return 1

    # Output results
    if args.json:
        json_results = {k: str(v) for k, v in files.items()}
        print(json.dumps(json_results, indent=2))
    else:
        print(f'\nGenerated {args.type} form in {args.output}')
        for file_type, path in files.items():
            print(f'  {file_type}: {path}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
