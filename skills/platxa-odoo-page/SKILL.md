---
name: platxa-odoo-page
description: Generate complete Odoo website pages (About, Contact, Services, Team, FAQ, Pricing) with QWeb templates, SEO metadata, breadcrumbs, and proper Odoo structure.
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
metadata:
  version: "1.0.0"
---

# Platxa Odoo Page Generator

Generate complete, production-ready Odoo website pages with proper QWeb templates, SEO optimization, and modular section architecture.

## Overview

This skill creates full Odoo website pages by composing modular sections into cohesive page layouts. Each page includes:

- QWeb template with semantic HTML5 structure
- Page record for URL routing
- Menu entry for navigation
- SEO metadata (title, description, Open Graph)
- Breadcrumb navigation
- Mobile-responsive design

## Supported Page Types

| Type | Sections | Use Case |
|------|----------|----------|
| `about` | Hero, Story, Values, Team Preview, CTA | Company information |
| `contact` | Hero, Contact Info, Form, Map | Customer contact |
| `services` | Hero, Services Grid, Process, CTA | Service offerings |
| `team` | Hero, Team Grid, CTA | Team members |
| `faq` | Hero, FAQ Accordion, CTA | Common questions |
| `pricing` | Hero, Pricing Table, FAQ Preview, CTA | Pricing tiers |
| `portfolio` | Hero, Portfolio Grid, CTA | Project showcase |
| `landing` | Full Hero, Features, Testimonials, CTA | Marketing landing |

## Workflow

### Step 1: Determine Page Type

Analyze user request to identify page type and required sections:

```python
PAGE_COMPOSITIONS = {
    'about': ['hero', 'story', 'values', 'team_preview', 'cta'],
    'contact': ['hero_small', 'contact_info', 'contact_form', 'map'],
    'services': ['hero', 'services_intro', 'services_grid', 'process', 'cta'],
    'team': ['hero', 'team_intro', 'team_grid', 'cta'],
    'faq': ['hero_small', 'faq_intro', 'faq_accordion', 'contact_cta'],
    'pricing': ['hero', 'pricing_intro', 'pricing_table', 'faq_preview', 'cta'],
    'portfolio': ['hero', 'portfolio_intro', 'portfolio_grid', 'cta'],
    'landing': ['hero_full', 'features', 'benefits', 'testimonials', 'pricing_preview', 'cta'],
}
```

### Step 2: Generate QWeb Template

Create the page template using modular sections:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="page_about" name="About Us">
        <t t-call="website.layout">
            <t t-set="pageName" t-value="'about'"/>
            <div id="wrap" class="oe_structure oe_empty">

                <!-- Hero Section -->
                <section class="s_cover parallax s_parallax_is_fixed pt160 pb160 o_cc o_cc1"
                         data-scroll-background-ratio="1">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-8 mx-auto text-center">
                                <h1 class="display-3 text-white">About Us</h1>
                                <p class="lead text-white-75">
                                    Discover our story, mission, and the team behind our success.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>

                <!-- Story Section -->
                <section class="s_text_block pt64 pb64">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-10 mx-auto">
                                <h2 class="h1-fs mb-4">Our Story</h2>
                                <p class="lead">
                                    [Your company story goes here...]
                                </p>
                            </div>
                        </div>
                    </div>
                </section>

                <!-- Values Section -->
                <section class="s_features pt64 pb64 o_cc o_cc5">
                    <div class="container">
                        <h2 class="text-center mb-5">Our Values</h2>
                        <div class="row">
                            <div class="col-lg-4 text-center mb-4">
                                <div class="s_feature_box">
                                    <i class="fa fa-3x fa-heart text-primary mb-3"/>
                                    <h4>Integrity</h4>
                                    <p>We believe in honest, transparent relationships.</p>
                                </div>
                            </div>
                            <!-- More value cards... -->
                        </div>
                    </div>
                </section>

                <!-- CTA Section -->
                <section class="s_call_to_action pt64 pb64 o_cc o_cc1">
                    <div class="container text-center">
                        <h2 class="text-white mb-4">Ready to Work Together?</h2>
                        <a href="/contact" class="btn btn-lg btn-secondary">
                            Contact Us
                        </a>
                    </div>
                </section>

            </div>
        </t>
    </template>
</odoo>
```

### Step 3: Create Page Record

Register the page with Odoo's website module:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data noupdate="0">
        <!-- About Page -->
        <record id="page_about" model="website.page">
            <field name="url">/about</field>
            <field name="name">About Us</field>
            <field name="website_published">True</field>
            <field name="website_indexed">True</field>
            <field name="view_id" ref="page_about"/>
        </record>
    </data>
</odoo>
```

### Step 4: Add Menu Entry

Create navigation menu item:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data noupdate="0">
        <record id="menu_about" model="website.menu">
            <field name="name">About</field>
            <field name="url">/about</field>
            <field name="page_id" ref="page_about"/>
            <field name="parent_id" ref="website.main_menu"/>
            <field name="sequence">20</field>
        </record>
    </data>
</odoo>
```

### Step 5: Generate SEO Metadata

Add SEO optimization through template inheritance:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="page_about_seo" inherit_id="website.layout"
              name="About Page SEO" active="True"
              customize_show="False" primary="False">
        <xpath expr="//head/title" position="replace">
            <title>About Us | Company Name</title>
        </xpath>
        <xpath expr="//head" position="inside">
            <meta name="description"
                  content="Learn about our company's story, mission, values, and the dedicated team working to serve you."/>
            <meta name="keywords"
                  content="about us, company, team, mission, values"/>

            <!-- Open Graph -->
            <meta property="og:title" content="About Us | Company Name"/>
            <meta property="og:description"
                  content="Discover our story and meet the team behind our success."/>
            <meta property="og:type" content="website"/>
            <meta property="og:url" content="/about"/>
        </xpath>
    </template>
</odoo>
```

## Section Library

### Hero Sections

**Full Hero (Landing Pages)**
```xml
<section class="s_cover parallax s_parallax_is_fixed pt200 pb200 o_cc o_cc1"
         data-scroll-background-ratio="1"
         style="background-image: url('/web/image/...');">
    <div class="container">
        <div class="row">
            <div class="col-lg-8">
                <h1 class="display-2 text-white mb-4">Headline Here</h1>
                <p class="lead text-white-75 mb-5">
                    Supporting text that explains your value proposition.
                </p>
                <div class="s_btn">
                    <a href="#" class="btn btn-lg btn-secondary me-2">Primary CTA</a>
                    <a href="#" class="btn btn-lg btn-outline-light">Secondary CTA</a>
                </div>
            </div>
        </div>
    </div>
</section>
```

**Small Hero (Interior Pages)**
```xml
<section class="s_text_block pt96 pb96 o_cc o_cc1">
    <div class="container text-center">
        <h1 class="display-4">Page Title</h1>
        <p class="lead text-muted">Brief page description</p>
        <!-- Breadcrumb -->
        <nav aria-label="breadcrumb" class="mt-4">
            <ol class="breadcrumb justify-content-center">
                <li class="breadcrumb-item"><a href="/">Home</a></li>
                <li class="breadcrumb-item active" aria-current="page">Current</li>
            </ol>
        </nav>
    </div>
</section>
```

### Content Sections

**Feature Cards**
```xml
<section class="s_features pt64 pb64">
    <div class="container">
        <div class="row">
            <t t-foreach="[1, 2, 3]" t-as="item">
                <div class="col-lg-4 mb-4">
                    <div class="card h-100 border-0 shadow-sm">
                        <div class="card-body text-center p-4">
                            <div class="feature-icon bg-primary bg-gradient text-white
                                        rounded-circle mb-3 mx-auto"
                                 style="width: 64px; height: 64px; line-height: 64px;">
                                <i class="fa fa-star"/>
                            </div>
                            <h4>Feature Title</h4>
                            <p class="text-muted">Feature description goes here.</p>
                        </div>
                    </div>
                </div>
            </t>
        </div>
    </div>
</section>
```

**Team Grid**
```xml
<section class="s_company_team pt64 pb64">
    <div class="container">
        <div class="row">
            <div class="col-lg-3 col-md-6 mb-4">
                <div class="card border-0 text-center">
                    <img src="/web/image/..." class="card-img-top rounded-circle mx-auto mt-4"
                         style="width: 150px; height: 150px; object-fit: cover;"
                         alt="Team Member"/>
                    <div class="card-body">
                        <h5 class="card-title mb-1">John Doe</h5>
                        <p class="text-muted small mb-2">CEO &amp; Founder</p>
                        <div class="social-links">
                            <a href="#" class="text-muted me-2"><i class="fa fa-linkedin"/></a>
                            <a href="#" class="text-muted"><i class="fa fa-twitter"/></a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
```

**FAQ Accordion**
```xml
<section class="s_faq_collapse pt64 pb64">
    <div class="container">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="accordion" id="faqAccordion">
                    <div class="accordion-item">
                        <h2 class="accordion-header" id="faq1">
                            <button class="accordion-button" type="button"
                                    data-bs-toggle="collapse" data-bs-target="#collapse1">
                                Question 1?
                            </button>
                        </h2>
                        <div id="collapse1" class="accordion-collapse collapse show"
                             data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                Answer to question 1 goes here.
                            </div>
                        </div>
                    </div>
                    <!-- More FAQ items... -->
                </div>
            </div>
        </div>
    </div>
</section>
```

**Pricing Table**
```xml
<section class="s_comparisons pt64 pb64">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="card h-100 text-center">
                    <div class="card-header py-3">
                        <h4 class="my-0">Basic</h4>
                    </div>
                    <div class="card-body">
                        <h1 class="card-title pricing-card-title">
                            $19<small class="text-muted">/mo</small>
                        </h1>
                        <ul class="list-unstyled mt-3 mb-4">
                            <li>10 users included</li>
                            <li>2 GB of storage</li>
                            <li>Email support</li>
                        </ul>
                        <a href="#" class="btn btn-lg btn-outline-primary">Get Started</a>
                    </div>
                </div>
            </div>
            <!-- More pricing tiers... -->
        </div>
    </div>
</section>
```

### Call-to-Action Sections

**Primary CTA**
```xml
<section class="s_call_to_action pt80 pb80 o_cc o_cc1">
    <div class="container text-center">
        <h2 class="text-white mb-3">Ready to Get Started?</h2>
        <p class="lead text-white-75 mb-4">
            Join thousands of satisfied customers today.
        </p>
        <a href="/contact" class="btn btn-lg btn-secondary">Contact Us</a>
    </div>
</section>
```

## Usage Examples

### Generate About Page

```bash
python scripts/generate_page.py \
  --type about \
  --module theme_company \
  --title "About Our Company" \
  --description "Learn about our mission and team"
```

**Output:**
```
views/pages/page_about.xml
data/pages.xml (updated)
data/menus.xml (updated)
```

### Generate Multiple Pages

```bash
python scripts/generate_page.py \
  --pages about,contact,services,team \
  --module theme_company \
  --with-seo
```

### Generate Landing Page

```bash
python scripts/generate_page.py \
  --type landing \
  --module theme_company \
  --title "Welcome to Company" \
  --hero-style full \
  --sections hero,features,testimonials,pricing,cta
```

## Integration

### With platxa-odoo-theme

Pages are automatically added to generated themes:

```python
# In theme generation workflow
1. Generate base theme structure
2. Call platxa-odoo-page for each required page
3. Update manifest with page XML files
```

### With platxa-token-sync

Pages use theme color variables:

```scss
// Pages inherit from theme's primary_variables.scss
.s_cover.o_cc1 {
    background-color: $o-color-1;  // From token sync
}
```

### With platxa-odoo-validator

Validate generated pages:

```bash
python validate_module.py theme_company/ --check-pages
```

## Best Practices

1. **Semantic HTML5** - Use proper heading hierarchy (h1 → h2 → h3)
2. **Accessibility** - Include alt text, ARIA labels, proper contrast
3. **Mobile-First** - Design for mobile, enhance for desktop
4. **Performance** - Lazy load images, minimize DOM depth
5. **SEO** - Unique titles/descriptions per page, proper meta tags
6. **Odoo Conventions** - Use `o_cc` classes for color customizer support
