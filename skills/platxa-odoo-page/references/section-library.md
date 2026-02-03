# Odoo Section Library Reference

Complete reference for all section templates and their customization.

## Section Overview

| Section | Category | Odoo Class | Description |
|---------|----------|------------|-------------|
| `hero` | Hero | `s_cover` | Full-width parallax hero |
| `hero_small` | Hero | `s_text_block` | Compact hero with breadcrumb |
| `hero_full` | Hero | `s_cover` | Full-screen landing hero |
| `story` | Content | `s_text_block` | Narrative text section |
| `values` | Content | `s_features` | Icon cards grid |
| `team_preview` | Content | `s_company_team` | Team preview cards |
| `team_intro` | Content | `s_text_block` | Team introduction |
| `team_grid` | Content | `s_company_team` | Full team grid |
| `contact_info` | Contact | `s_text_block` | Contact cards |
| `contact_form` | Contact | `s_website_form` | Odoo form integration |
| `map` | Contact | `s_google_map` | Map placeholder |
| `services_intro` | Services | `s_text_block` | Services introduction |
| `services_grid` | Services | `s_features` | Service cards grid |
| `process` | Services | `s_process` | Process steps |
| `faq_intro` | FAQ | `s_text_block` | FAQ introduction |
| `faq_accordion` | FAQ | `s_faq_collapse` | Accordion questions |
| `faq_preview` | FAQ | `s_faq_collapse` | Mini FAQ section |
| `pricing_intro` | Pricing | `s_text_block` | Pricing introduction |
| `pricing_table` | Pricing | `s_comparisons` | Pricing tiers |
| `pricing_preview` | Pricing | `s_comparisons` | Single tier preview |
| `portfolio_intro` | Portfolio | `s_text_block` | Portfolio introduction |
| `portfolio_grid` | Portfolio | `s_image_gallery` | Project cards |
| `features` | Landing | `s_features` | Feature highlights |
| `benefits` | Landing | `s_text_image` | Benefits checklist |
| `testimonials` | Landing | `s_quotes` | Customer quotes |
| `cta` | CTA | `s_call_to_action` | Primary CTA |
| `contact_cta` | CTA | `s_call_to_action` | Contact-focused CTA |

## Hero Sections

### `hero` - Standard Hero

Full-width parallax hero for main pages.

**Odoo Classes:** `s_cover`, `parallax`, `s_parallax_is_fixed`, `o_cc`, `o_cc1`

**Features:**
- Parallax background effect
- Centered content (8-column)
- Primary color overlay
- White text

**HTML Structure:**
```xml
<section class="s_cover parallax s_parallax_is_fixed pt160 pb160 o_cc o_cc1">
    <div class="container">
        <div class="row">
            <div class="col-lg-8 mx-auto text-center">
                <h1 class="display-3 text-white">Title</h1>
                <p class="lead text-white-75">Description</p>
            </div>
        </div>
    </div>
</section>
```

### `hero_small` - Compact Hero

Interior page hero with breadcrumb navigation.

**Odoo Classes:** `s_text_block`, `o_cc`, `o_cc1`

**Features:**
- Smaller padding (96px vs 160px)
- Breadcrumb navigation
- Centered layout

### `hero_full` - Full-Screen Hero

Landing page hero with dual CTAs.

**Odoo Classes:** `s_cover`, `parallax`, `s_parallax_is_fixed`, `o_cc`, `o_cc1`

**Features:**
- Full viewport height (`min-height: 100vh`)
- Dual CTA buttons (primary + outline)
- Left-aligned content (8-column)

## Content Sections

### `story` - Narrative Section

Long-form text content for company stories.

**Layout:** 10-column centered
**Elements:** H2 heading, lead paragraph, body text

### `values` - Values Grid

Icon cards showcasing company values.

**Layout:** 3-column grid (`col-lg-4`)
**Elements:** FontAwesome icon, H4 title, description

**Icons Used:**
- `fa-heart` - Integrity
- `fa-lightbulb-o` - Innovation
- `fa-users` - Collaboration

### `team_preview` / `team_grid` - Team Cards

Team member cards with optional social links.

**Layout:**
- Preview: 3 cards centered
- Grid: 4-column layout (`col-lg-3`)

**Elements:**
- Avatar placeholder (rounded circle)
- Name (H5)
- Title (small text)
- Social links (LinkedIn, Twitter, GitHub)

## Contact Sections

### `contact_info` - Contact Cards

Three-card layout for contact information.

**Cards:**
1. Address (map marker icon)
2. Phone (phone icon)
3. Email (envelope icon)

### `contact_form` - Odoo Form

Integration with Odoo's website form system.

**Form Fields:**
- Name (required)
- Email (required)
- Phone (optional)
- Subject (required)
- Message (required, textarea)

**Odoo Integration:**
```xml
<form action="/website/form/" method="post"
      class="s_website_form_form"
      data-model_name="mail.mail"
      data-success_page="/contactus-thank-you">
```

## FAQ Sections

### `faq_accordion` - Full FAQ

Bootstrap 5 accordion component.

**Structure:**
```xml
<div class="accordion" id="faqAccordion">
    <div class="accordion-item">
        <h2 class="accordion-header">
            <button class="accordion-button" data-bs-toggle="collapse">
                Question?
            </button>
        </h2>
        <div class="accordion-collapse collapse show">
            <div class="accordion-body">Answer</div>
        </div>
    </div>
</div>
```

### `faq_preview` - Mini FAQ

2-question preview with link to full FAQ page.

## Pricing Sections

### `pricing_table` - Full Pricing

Three-tier pricing comparison.

**Tiers:**
1. Starter ($19/mo) - Outline style
2. Professional ($49/mo) - Primary border, highlighted
3. Enterprise ($99/mo) - Outline style

**Features:**
- Checkmark/X icons for feature comparison
- "Most Popular" badge on middle tier
- Flexible card height (`h-100`)

### `pricing_preview` - Single Tier

Minimal pricing preview for landing pages.

## Landing Page Sections

### `features` - Feature Highlights

6 features in 2 rows of 3.

**Layout:** Horizontal (icon left, text right)
**Icons:** Primary background, white icon

### `benefits` - Benefits Checklist

Split layout with image and benefits list.

**Layout:** 2-column (image + content)
**Elements:**
- Placeholder image
- H2 heading
- Checklist with green checkmark icons

### `testimonials` - Customer Quotes

3 testimonial cards with star ratings.

**Elements:**
- 5-star rating
- Quote text
- Avatar placeholder
- Name and company

## CTA Sections

### `cta` - Primary CTA

Standard call-to-action with primary background.

**Odoo Classes:** `s_call_to_action`, `o_cc`, `o_cc1`

**Elements:**
- H2 heading (white)
- Lead text (white-75)
- Secondary button

### `contact_cta` - Support CTA

FAQ-specific CTA for unanswered questions.

**Text:** "Still Have Questions?" → Contact Support

## Color Classes Reference

| Class | Purpose |
|-------|---------|
| `o_cc o_cc1` | Primary brand color background |
| `o_cc o_cc5` | Light/neutral background |
| `text-white` | White text on dark backgrounds |
| `text-white-75` | 75% opacity white text |
| `text-primary` | Primary brand color text |
| `text-muted` | Muted/gray text |
| `bg-primary` | Primary background |
| `bg-secondary` | Secondary background |

## Spacing Classes

| Class | Padding |
|-------|---------|
| `pt64 pb64` | Standard section (64px) |
| `pt80 pb80` | Large section (80px) |
| `pt96 pb96` | Compact hero (96px) |
| `pt160 pb160` | Full hero (160px) |
| `pt200 pb200` | Full-screen hero (200px) |

## Accessibility Notes

1. **Heading Hierarchy:** Each page has one H1, sections use H2-H4
2. **ARIA Labels:** Breadcrumbs include `aria-label="breadcrumb"`
3. **Form Labels:** All form fields have associated labels
4. **Contrast:** White text on primary backgrounds meets WCAG AA
5. **Icons:** FontAwesome icons are decorative (no alt text needed)
