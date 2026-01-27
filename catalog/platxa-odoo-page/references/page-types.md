# Odoo Page Types Reference

Complete reference for all supported page types and their configurations.

## Page Type Summary

| Type | Title | URL | Sections | Use Case |
|------|-------|-----|----------|----------|
| `about` | About Us | /about | 5 | Company information |
| `contact` | Contact Us | /contact | 4 | Customer contact |
| `services` | Our Services | /services | 5 | Service offerings |
| `team` | Our Team | /team | 4 | Team members |
| `faq` | FAQ | /faq | 4 | Common questions |
| `pricing` | Pricing | /pricing | 5 | Pricing tiers |
| `portfolio` | Our Work | /portfolio | 4 | Project showcase |
| `landing` | Welcome | / | 6 | Marketing landing |

## Detailed Page Configurations

### About Page (`about`)

**Purpose:** Company information, mission, values, and team overview.

**Default Configuration:**
```python
{
    'title': 'About Us',
    'description': 'Learn about our company, mission, values, and the team behind our success.',
    'menu_label': 'About',
    'sequence': 20,
    'url': '/about'
}
```

**Sections:**
1. `hero` - Full-width parallax hero with title and description
2. `story` - Company story narrative
3. `values` - Core values with icons (3 columns)
4. `team_preview` - Leadership preview with link to full team page
5. `cta` - Call-to-action for contact

### Contact Page (`contact`)

**Purpose:** Customer contact information and inquiry form.

**Default Configuration:**
```python
{
    'title': 'Contact Us',
    'description': "Get in touch with us. We'd love to hear from you.",
    'menu_label': 'Contact',
    'sequence': 90,
    'url': '/contact'
}
```

**Sections:**
1. `hero_small` - Compact hero with breadcrumb
2. `contact_info` - Address, phone, email cards
3. `contact_form` - Odoo website form with CRM integration
4. `map` - Map placeholder section

### Services Page (`services`)

**Purpose:** Service offerings and process overview.

**Default Configuration:**
```python
{
    'title': 'Our Services',
    'description': 'Discover our comprehensive range of services designed to meet your needs.',
    'menu_label': 'Services',
    'sequence': 30,
    'url': '/services'
}
```

**Sections:**
1. `hero` - Full-width hero
2. `services_intro` - Introduction paragraph
3. `services_grid` - 6-card service grid with icons
4. `process` - 4-step process visualization
5. `cta` - Call-to-action

### Team Page (`team`)

**Purpose:** Full team member showcase.

**Default Configuration:**
```python
{
    'title': 'Our Team',
    'description': 'Meet the dedicated professionals who make it all happen.',
    'menu_label': 'Team',
    'sequence': 40,
    'url': '/team'
}
```

**Sections:**
1. `hero` - Full-width hero
2. `team_intro` - Introduction paragraph
3. `team_grid` - 4-column team member cards with social links
4. `cta` - Call-to-action

### FAQ Page (`faq`)

**Purpose:** Frequently asked questions with accordion interface.

**Default Configuration:**
```python
{
    'title': 'FAQ',
    'description': 'Find answers to commonly asked questions about our products and services.',
    'menu_label': 'FAQ',
    'sequence': 70,
    'url': '/faq'
}
```

**Sections:**
1. `hero_small` - Compact hero with breadcrumb
2. `faq_intro` - Introduction paragraph
3. `faq_accordion` - Bootstrap accordion with 4 sample questions
4. `contact_cta` - Contact-focused CTA for unanswered questions

### Pricing Page (`pricing`)

**Purpose:** Pricing tiers and common pricing questions.

**Default Configuration:**
```python
{
    'title': 'Pricing',
    'description': 'Simple, transparent pricing that scales with your needs.',
    'menu_label': 'Pricing',
    'sequence': 50,
    'url': '/pricing'
}
```

**Sections:**
1. `hero` - Full-width hero
2. `pricing_intro` - Introduction paragraph
3. `pricing_table` - 3-tier pricing cards (Starter, Professional, Enterprise)
4. `faq_preview` - 2-question FAQ preview with link to full FAQ
5. `cta` - Call-to-action

### Portfolio Page (`portfolio`)

**Purpose:** Project showcase and case studies.

**Default Configuration:**
```python
{
    'title': 'Our Work',
    'description': 'Explore our portfolio of successful projects and case studies.',
    'menu_label': 'Portfolio',
    'sequence': 35,
    'url': '/portfolio'
}
```

**Sections:**
1. `hero` - Full-width hero
2. `portfolio_intro` - Introduction paragraph
3. `portfolio_grid` - 6-card project grid with category badges
4. `cta` - Call-to-action

### Landing Page (`landing`)

**Purpose:** Marketing landing page with full conversion funnel.

**Default Configuration:**
```python
{
    'title': 'Welcome',
    'description': 'Discover how we can help you achieve your goals.',
    'menu_label': 'Home',
    'sequence': 10,
    'url': '/'
}
```

**Sections:**
1. `hero_full` - Full-screen hero with dual CTAs
2. `features` - 6 feature highlights with icons
3. `benefits` - Image + benefits checklist
4. `testimonials` - 3 customer testimonials with ratings
5. `pricing_preview` - Single pricing card preview
6. `cta` - Call-to-action

## Menu Sequence Guidelines

| Range | Purpose |
|-------|---------|
| 10-19 | Home/Landing |
| 20-29 | About |
| 30-39 | Services, Portfolio |
| 40-49 | Team |
| 50-59 | Pricing |
| 60-79 | FAQ, Resources |
| 80-99 | Contact |

## Customization

### Override Default Title

```bash
python generate_page.py --type about --module theme_company \
    --title "Our Company Story"
```

### Custom Description

```bash
python generate_page.py --type about --module theme_company \
    --description "Learn about Acme Corp's 20-year journey"
```

### Custom Company Name (SEO)

```bash
python generate_page.py --type about --module theme_company \
    --company "Acme Corporation"
```

This generates SEO title: "About Us | Acme Corporation"
