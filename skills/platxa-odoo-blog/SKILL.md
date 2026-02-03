---
name: platxa-odoo-blog
description: Generate Odoo blog templates with post layouts, category pages, author profiles, and SEO optimization.
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
metadata:
  version: "1.0.0"
---

# Platxa Odoo Blog Generator

Generate production-ready Odoo blog templates with modern layouts, SEO optimization, and social sharing features.

## Overview

This skill creates customized Odoo blog templates that override the default blog views. Templates include:

- Blog post layouts (standard, featured, minimal)
- Blog listing pages with filtering
- Category/tag pages
- Author profile pages
- Related posts sections
- Social sharing integration
- SEO metadata

## Supported Template Types

| Type | Template | Description |
|------|----------|-------------|
| `post` | `website_blog.blog_post_complete` | Single post layout |
| `listing` | `website_blog.blog_post_short` | Post card in listings |
| `index` | `website_blog.blog` | Blog home page |
| `category` | `website_blog.blog_tag` | Category/tag page |
| `author` | Custom | Author profile page |
| `sidebar` | Custom | Blog sidebar widget |

## Workflow

### Step 1: Determine Template Style

Analyze user request to identify desired blog style:

```python
BLOG_STYLES = {
    'modern': {
        'card_style': 'shadow',
        'image_ratio': '16:9',
        'excerpt_length': 150,
        'show_author': True,
        'show_date': True,
        'show_reading_time': True,
    },
    'minimal': {
        'card_style': 'border',
        'image_ratio': '2:1',
        'excerpt_length': 100,
        'show_author': False,
        'show_date': True,
        'show_reading_time': False,
    },
    'magazine': {
        'card_style': 'overlay',
        'image_ratio': '4:3',
        'excerpt_length': 200,
        'show_author': True,
        'show_date': True,
        'show_reading_time': True,
    },
}
```

### Step 2: Generate Post Template

Create the blog post template:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="blog_post_complete" inherit_id="website_blog.blog_post_complete"
              name="Blog Post - Custom Layout" priority="99">

        <!-- Replace cover section -->
        <xpath expr="//section[hasclass('o_wblog_post_page_cover')]" position="replace">
            <section class="o_wblog_post_page_cover pt96 pb64 o_cc o_cc1">
                <div class="container">
                    <div class="row justify-content-center">
                        <div class="col-lg-8 text-center">
                            <!-- Category Badge -->
                            <t t-if="blog_post.tag_ids">
                                <div class="mb-3">
                                    <t t-foreach="blog_post.tag_ids[:1]" t-as="tag">
                                        <a t-attf-href="/blog/#{slug(blog)}/tag/#{slug(tag)}"
                                           class="badge bg-secondary text-decoration-none">
                                            <t t-esc="tag.name"/>
                                        </a>
                                    </t>
                                </div>
                            </t>

                            <!-- Title -->
                            <h1 class="display-4 text-white mb-4">
                                <t t-esc="blog_post.name"/>
                            </h1>

                            <!-- Meta Info -->
                            <div class="d-flex justify-content-center align-items-center gap-4 text-white-75">
                                <!-- Author -->
                                <div class="d-flex align-items-center">
                                    <t t-if="blog_post.author_id.image_128">
                                        <img t-att-src="image_data_uri(blog_post.author_id.image_128)"
                                             class="rounded-circle me-2"
                                             style="width: 32px; height: 32px; object-fit: cover;"
                                             t-att-alt="blog_post.author_id.name"/>
                                    </t>
                                    <span t-esc="blog_post.author_id.name"/>
                                </div>

                                <!-- Date -->
                                <div>
                                    <i class="fa fa-calendar me-1"/>
                                    <span t-field="blog_post.post_date" t-options="{'format': 'MMM d, yyyy'}"/>
                                </div>

                                <!-- Reading Time -->
                                <div>
                                    <i class="fa fa-clock-o me-1"/>
                                    <t t-set="word_count" t-value="len((blog_post.content or '').split())"/>
                                    <t t-set="reading_time" t-value="max(1, word_count // 200)"/>
                                    <span><t t-esc="reading_time"/> min read</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </xpath>

        <!-- Add featured image below cover -->
        <xpath expr="//section[hasclass('o_wblog_post_page_cover')]" position="after">
            <t t-if="blog_post.cover_properties.get('background-image')">
                <div class="container mt-n5 position-relative" style="z-index: 10;">
                    <div class="row justify-content-center">
                        <div class="col-lg-10">
                            <img t-att-src="blog_post.cover_properties.get('background-image').replace('url(', '').replace(')', '').replace(&quot;'&quot;, '')"
                                 class="img-fluid rounded shadow-lg w-100"
                                 style="max-height: 500px; object-fit: cover;"
                                 t-att-alt="blog_post.name"/>
                        </div>
                    </div>
                </div>
            </t>
        </xpath>

    </template>
</odoo>
```

### Step 3: Generate Listing Card Template

Create the blog post card for listings:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="blog_post_short" inherit_id="website_blog.blog_post_short"
              name="Blog Post Card - Custom" priority="99">

        <xpath expr="//article" position="replace">
            <article class="card h-100 border-0 shadow-sm o_wblog_post">
                <!-- Featured Image -->
                <t t-if="post.cover_properties.get('background-image')">
                    <a t-attf-href="/blog/#{slug(blog)}/#{slug(post)}" class="card-img-top-wrapper">
                        <div class="ratio ratio-16x9">
                            <img t-att-src="post.cover_properties.get('background-image').replace('url(', '').replace(')', '').replace(&quot;'&quot;, '')"
                                 class="card-img-top"
                                 style="object-fit: cover;"
                                 t-att-alt="post.name"
                                 loading="lazy"/>
                        </div>
                    </a>
                </t>

                <div class="card-body d-flex flex-column">
                    <!-- Category -->
                    <t t-if="post.tag_ids">
                        <div class="mb-2">
                            <t t-foreach="post.tag_ids[:1]" t-as="tag">
                                <a t-attf-href="/blog/#{slug(blog)}/tag/#{slug(tag)}"
                                   class="badge bg-primary text-decoration-none">
                                    <t t-esc="tag.name"/>
                                </a>
                            </t>
                        </div>
                    </t>

                    <!-- Title -->
                    <h3 class="card-title h5">
                        <a t-attf-href="/blog/#{slug(blog)}/#{slug(post)}"
                           class="text-decoration-none text-dark">
                            <t t-esc="post.name"/>
                        </a>
                    </h3>

                    <!-- Excerpt -->
                    <p class="card-text text-muted flex-grow-1">
                        <t t-esc="post.subtitle or post.teaser[:150] + '...' if post.teaser and len(post.teaser) > 150 else post.teaser"/>
                    </p>

                    <!-- Meta -->
                    <div class="d-flex align-items-center mt-auto pt-3 border-top">
                        <t t-if="post.author_id.image_128">
                            <img t-att-src="image_data_uri(post.author_id.image_128)"
                                 class="rounded-circle me-2"
                                 style="width: 28px; height: 28px; object-fit: cover;"
                                 t-att-alt="post.author_id.name"/>
                        </t>
                        <div class="small">
                            <div class="fw-medium" t-esc="post.author_id.name"/>
                            <div class="text-muted" t-field="post.post_date"
                                 t-options="{'format': 'MMM d, yyyy'}"/>
                        </div>
                    </div>
                </div>
            </article>
        </xpath>

    </template>
</odoo>
```

### Step 4: Generate Related Posts Section

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="blog_post_related" name="Related Posts Section">
        <section class="s_blog_related pt64 pb64 o_cc o_cc5">
            <div class="container">
                <h2 class="text-center mb-5">Related Articles</h2>
                <div class="row">
                    <t t-foreach="related_posts[:3]" t-as="post">
                        <div class="col-lg-4 mb-4">
                            <article class="card h-100 border-0 shadow-sm">
                                <t t-if="post.cover_properties.get('background-image')">
                                    <a t-attf-href="/blog/#{slug(blog)}/#{slug(post)}">
                                        <div class="ratio ratio-16x9">
                                            <img t-att-src="post.cover_properties.get('background-image').replace('url(', '').replace(')', '').replace(&quot;'&quot;, '')"
                                                 class="card-img-top"
                                                 style="object-fit: cover;"
                                                 t-att-alt="post.name"/>
                                        </div>
                                    </a>
                                </t>
                                <div class="card-body">
                                    <h4 class="card-title h6">
                                        <a t-attf-href="/blog/#{slug(blog)}/#{slug(post)}"
                                           class="text-decoration-none text-dark">
                                            <t t-esc="post.name"/>
                                        </a>
                                    </h4>
                                    <small class="text-muted" t-field="post.post_date"
                                           t-options="{'format': 'MMM d, yyyy'}"/>
                                </div>
                            </article>
                        </div>
                    </t>
                </div>
            </div>
        </section>
    </template>
</odoo>
```

### Step 5: Generate SEO Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="blog_post_seo" inherit_id="website_blog.blog_post_complete"
              name="Blog Post SEO" priority="98">

        <xpath expr="//head" position="inside">
            <!-- Article Schema -->
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "BlogPosting",
                "headline": "<t t-esc="blog_post.name"/>",
                "description": "<t t-esc="blog_post.subtitle or blog_post.teaser[:160] if blog_post.teaser else ''"/>",
                "author": {
                    "@type": "Person",
                    "name": "<t t-esc="blog_post.author_id.name"/>"
                },
                "datePublished": "<t t-esc="blog_post.post_date"/>",
                "dateModified": "<t t-esc="blog_post.write_date"/>"
            }
            </script>

            <!-- Open Graph -->
            <meta property="og:type" content="article"/>
            <meta property="article:published_time" t-att-content="blog_post.post_date"/>
            <meta property="article:author" t-att-content="blog_post.author_id.name"/>
            <t t-foreach="blog_post.tag_ids" t-as="tag">
                <meta property="article:tag" t-att-content="tag.name"/>
            </t>

            <!-- Twitter Card -->
            <meta name="twitter:card" content="summary_large_image"/>
        </xpath>

    </template>
</odoo>
```

## Usage Examples

### Generate Modern Blog Templates

```bash
python scripts/generate_blog.py \
    --style modern \
    --module theme_company \
    --with-related-posts \
    --with-social-sharing
```

### Generate Minimal Blog Templates

```bash
python scripts/generate_blog.py \
    --style minimal \
    --module theme_company \
    --no-author-images
```

### Generate Magazine-Style Blog

```bash
python scripts/generate_blog.py \
    --style magazine \
    --module theme_company \
    --with-sidebar \
    --posts-per-page 9
```

## Integration

### With platxa-odoo-theme

Blog templates inherit theme colors:

```scss
// Blog cards use theme variables
.o_wblog_post .card {
    border-color: $o-color-4;
}

.o_wblog_post .badge {
    background-color: $o-color-1;
}
```

### With platxa-odoo-page

Blog can be embedded in generated pages:

```xml
<section class="s_blog_posts">
    <t t-call="website_blog.latest_posts">
        <t t-set="posts_limit" t-value="3"/>
    </t>
</section>
```

## Best Practices

1. **Image Optimization** - Use `loading="lazy"` for blog images
2. **SEO** - Include structured data (JSON-LD) for articles
3. **Accessibility** - Proper heading hierarchy, alt text
4. **Performance** - Limit posts per page, paginate
5. **Mobile** - Responsive card layouts
6. **Social** - Open Graph and Twitter Card meta tags
