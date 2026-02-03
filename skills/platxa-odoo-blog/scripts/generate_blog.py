#!/usr/bin/env python3
"""
Platxa Odoo Blog Generator

Generates production-ready Odoo blog templates with:
- Modern post layouts
- Listing card templates
- Related posts sections
- SEO optimization
- Social sharing integration
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

# ============================================================================
# Blog Style Definitions
# ============================================================================

BlogStyle = Literal["modern", "minimal", "magazine"]

BLOG_STYLES: dict[str, dict[str, object]] = {
    "modern": {
        "card_style": "shadow",
        "image_ratio": "16x9",
        "excerpt_length": 150,
        "show_author": True,
        "show_author_image": True,
        "show_date": True,
        "show_reading_time": True,
        "show_category": True,
    },
    "minimal": {
        "card_style": "border",
        "image_ratio": "21x9",
        "excerpt_length": 100,
        "show_author": True,
        "show_author_image": False,
        "show_date": True,
        "show_reading_time": False,
        "show_category": True,
    },
    "magazine": {
        "card_style": "overlay",
        "image_ratio": "4x3",
        "excerpt_length": 200,
        "show_author": True,
        "show_author_image": True,
        "show_date": True,
        "show_reading_time": True,
        "show_category": True,
    },
}


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class BlogConfig:
    """Configuration for blog templates."""

    style: BlogStyle
    module_name: str
    card_style: str = "shadow"
    image_ratio: str = "16x9"
    excerpt_length: int = 150
    show_author: bool = True
    show_author_image: bool = True
    show_date: bool = True
    show_reading_time: bool = True
    show_category: bool = True
    with_related_posts: bool = True
    with_social_sharing: bool = True
    with_sidebar: bool = False
    posts_per_page: int = 6

    def __post_init__(self) -> None:
        """Apply style defaults."""
        style_config = BLOG_STYLES.get(self.style, BLOG_STYLES["modern"])

        if self.card_style == "shadow":
            self.card_style = str(style_config.get("card_style", "shadow"))
        if self.image_ratio == "16x9":
            self.image_ratio = str(style_config.get("image_ratio", "16x9"))
        if self.excerpt_length == 150:
            excerpt = style_config.get("excerpt_length", 150)
            self.excerpt_length = int(excerpt) if isinstance(excerpt, (int, float, str)) else 150


# ============================================================================
# Template Generators
# ============================================================================


class BlogTemplateGenerator:
    """Generates Odoo blog template XML files."""

    def generate_post_template(self, config: BlogConfig) -> str:
        """Generate blog post detail template."""
        reading_time_section = ""
        if config.show_reading_time:
            reading_time_section = """
                                <!-- Reading Time -->
                                <div>
                                    <i class="fa fa-clock-o me-1"/>
                                    <t t-set="word_count" t-value="len((blog_post.content or '').split())"/>
                                    <t t-set="reading_time" t-value="max(1, word_count // 200)"/>
                                    <span><t t-esc="reading_time"/> min read</span>
                                </div>"""

        author_image = ""
        if config.show_author_image:
            author_image = """
                                    <t t-if="blog_post.author_id.image_128">
                                        <img t-att-src="image_data_uri(blog_post.author_id.image_128)"
                                             class="rounded-circle me-2"
                                             style="width: 32px; height: 32px; object-fit: cover;"
                                             t-att-alt="blog_post.author_id.name"/>
                                    </t>"""

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="blog_post_complete" inherit_id="website_blog.blog_post_complete"
              name="Blog Post - {config.style.title()} Layout" priority="99">

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
                                        <a t-attf-href="/blog/#{{slug(blog)}}/tag/#{{slug(tag)}}"
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
                            <div class="d-flex justify-content-center align-items-center flex-wrap gap-4 text-white-75">
                                <!-- Author -->
                                <div class="d-flex align-items-center">{author_image}
                                    <span t-esc="blog_post.author_id.name"/>
                                </div>

                                <!-- Date -->
                                <div>
                                    <i class="fa fa-calendar me-1"/>
                                    <span t-field="blog_post.post_date" t-options="{{'format': 'MMM d, yyyy'}}"/>
                                </div>
{reading_time_section}
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
                                 t-att-alt="blog_post.name"
                                 loading="lazy"/>
                        </div>
                    </div>
                </div>
            </t>
        </xpath>

    </template>
</odoo>
"""

    def generate_card_template(self, config: BlogConfig) -> str:
        """Generate blog post card template for listings."""
        card_class = "shadow-sm" if config.card_style == "shadow" else "border"

        author_section = ""
        if config.show_author:
            author_image = ""
            if config.show_author_image:
                author_image = """
                        <t t-if="post.author_id.image_128">
                            <img t-att-src="image_data_uri(post.author_id.image_128)"
                                 class="rounded-circle me-2"
                                 style="width: 28px; height: 28px; object-fit: cover;"
                                 t-att-alt="post.author_id.name"/>
                        </t>"""

            author_section = f"""
                    <!-- Meta -->
                    <div class="d-flex align-items-center mt-auto pt-3 border-top">{author_image}
                        <div class="small">
                            <div class="fw-medium" t-esc="post.author_id.name"/>
                            <div class="text-muted" t-field="post.post_date"
                                 t-options="{{'format': 'MMM d, yyyy'}}"/>
                        </div>
                    </div>"""

        category_section = ""
        if config.show_category:
            category_section = """
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
                    </t>"""

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="blog_post_short" inherit_id="website_blog.blog_post_short"
              name="Blog Post Card - {config.style.title()}" priority="99">

        <xpath expr="//article" position="replace">
            <article class="card h-100 border-0 {card_class} o_wblog_post">
                <!-- Featured Image -->
                <t t-if="post.cover_properties.get('background-image')">
                    <a t-attf-href="/blog/#{{slug(blog)}}/#{{slug(post)}}" class="card-img-top-wrapper">
                        <div class="ratio ratio-{config.image_ratio}">
                            <img t-att-src="post.cover_properties.get('background-image').replace('url(', '').replace(')', '').replace(&quot;'&quot;, '')"
                                 class="card-img-top"
                                 style="object-fit: cover;"
                                 t-att-alt="post.name"
                                 loading="lazy"/>
                        </div>
                    </a>
                </t>

                <div class="card-body d-flex flex-column">
{category_section}
                    <!-- Title -->
                    <h3 class="card-title h5">
                        <a t-attf-href="/blog/#{{slug(blog)}}/#{{slug(post)}}"
                           class="text-decoration-none text-dark">
                            <t t-esc="post.name"/>
                        </a>
                    </h3>

                    <!-- Excerpt -->
                    <p class="card-text text-muted flex-grow-1">
                        <t t-if="post.subtitle" t-esc="post.subtitle"/>
                        <t t-elif="post.teaser">
                            <t t-if="len(post.teaser or '') > {config.excerpt_length}">
                                <t t-esc="post.teaser[:{config.excerpt_length}]"/>...
                            </t>
                            <t t-else="" t-esc="post.teaser"/>
                        </t>
                    </p>
{author_section}
                </div>
            </article>
        </xpath>

    </template>
</odoo>
"""

    def generate_related_posts(self, config: BlogConfig) -> str:
        """Generate related posts section template."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="blog_post_related" name="Related Posts Section">
        <section class="s_blog_related pt64 pb64 o_cc o_cc5">
            <div class="container">
                <h2 class="text-center mb-5">Related Articles</h2>
                <div class="row">
                    <t t-foreach="related_posts[:3]" t-as="rpost">
                        <div class="col-lg-4 mb-4">
                            <article class="card h-100 border-0 shadow-sm">
                                <t t-if="rpost.cover_properties.get('background-image')">
                                    <a t-attf-href="/blog/#{{slug(blog)}}/#{{slug(rpost)}}">
                                        <div class="ratio ratio-{config.image_ratio}">
                                            <img t-att-src="rpost.cover_properties.get('background-image').replace('url(', '').replace(')', '').replace(&quot;'&quot;, '')"
                                                 class="card-img-top"
                                                 style="object-fit: cover;"
                                                 t-att-alt="rpost.name"
                                                 loading="lazy"/>
                                        </div>
                                    </a>
                                </t>
                                <div class="card-body">
                                    <h4 class="card-title h6">
                                        <a t-attf-href="/blog/#{{slug(blog)}}/#{{slug(rpost)}}"
                                           class="text-decoration-none text-dark">
                                            <t t-esc="rpost.name"/>
                                        </a>
                                    </h4>
                                    <small class="text-muted" t-field="rpost.post_date"
                                           t-options="{{'format': 'MMM d, yyyy'}}"/>
                                </div>
                            </article>
                        </div>
                    </t>
                </div>
            </div>
        </section>
    </template>
</odoo>
"""

    def generate_social_sharing(self, config: BlogConfig) -> str:
        """Generate social sharing buttons template."""
        return """<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="blog_post_social_sharing" name="Blog Post Social Sharing">
        <div class="s_blog_social_sharing d-flex gap-2 my-4">
            <!-- Twitter/X -->
            <a t-attf-href="https://twitter.com/intent/tweet?text=#{blog_post.name}&amp;url=#{request.httprequest.url}"
               target="_blank" rel="noopener"
               class="btn btn-outline-secondary btn-sm">
                <i class="fa fa-twitter"/> Share
            </a>

            <!-- LinkedIn -->
            <a t-attf-href="https://www.linkedin.com/sharing/share-offsite/?url=#{request.httprequest.url}"
               target="_blank" rel="noopener"
               class="btn btn-outline-secondary btn-sm">
                <i class="fa fa-linkedin"/> Share
            </a>

            <!-- Facebook -->
            <a t-attf-href="https://www.facebook.com/sharer/sharer.php?u=#{request.httprequest.url}"
               target="_blank" rel="noopener"
               class="btn btn-outline-secondary btn-sm">
                <i class="fa fa-facebook"/> Share
            </a>

            <!-- Copy Link -->
            <button type="button" class="btn btn-outline-secondary btn-sm"
                    onclick="navigator.clipboard.writeText(window.location.href); this.innerHTML='<i class=\\'fa fa-check\\'></i> Copied!';">
                <i class="fa fa-link"/> Copy Link
            </button>
        </div>
    </template>
</odoo>
"""

    def generate_seo_template(self, config: BlogConfig) -> str:
        """Generate SEO enhancement template."""
        return """<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="blog_post_seo" inherit_id="website_blog.blog_post_complete"
              name="Blog Post SEO Enhancements" priority="98">

        <xpath expr="//t[@t-call='website.layout']" position="inside">
            <t t-set="additional_title" t-value="blog_post.name"/>
        </xpath>

        <xpath expr="//head" position="inside">
            <!-- Open Graph Article -->
            <meta property="og:type" content="article"/>
            <meta property="article:published_time" t-att-content="blog_post.post_date"/>
            <meta property="article:modified_time" t-att-content="blog_post.write_date"/>
            <meta property="article:author" t-att-content="blog_post.author_id.name"/>
            <t t-foreach="blog_post.tag_ids" t-as="tag">
                <meta property="article:tag" t-att-content="tag.name"/>
            </t>

            <!-- Twitter Card -->
            <meta name="twitter:card" content="summary_large_image"/>
            <meta name="twitter:title" t-att-content="blog_post.name"/>
            <meta name="twitter:description" t-att-content="blog_post.subtitle or blog_post.teaser[:200] if blog_post.teaser else ''"/>
        </xpath>

    </template>
</odoo>
"""

    def generate_sidebar(self, config: BlogConfig) -> str:
        """Generate blog sidebar template."""
        return """<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="blog_sidebar" name="Blog Sidebar">
        <aside class="blog-sidebar">
            <!-- Search -->
            <div class="card border-0 shadow-sm mb-4">
                <div class="card-body">
                    <h5 class="card-title">Search</h5>
                    <form action="/blog" method="get">
                        <div class="input-group">
                            <input type="text" name="search" class="form-control"
                                   placeholder="Search articles..."/>
                            <button type="submit" class="btn btn-primary">
                                <i class="fa fa-search"/>
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <!-- Categories -->
            <div class="card border-0 shadow-sm mb-4">
                <div class="card-body">
                    <h5 class="card-title">Categories</h5>
                    <ul class="list-unstyled mb-0">
                        <t t-foreach="tags" t-as="tag">
                            <li class="mb-2">
                                <a t-attf-href="/blog/#{slug(blog)}/tag/#{slug(tag)}"
                                   class="text-decoration-none d-flex justify-content-between">
                                    <span t-esc="tag.name"/>
                                    <span class="badge bg-secondary rounded-pill"
                                          t-esc="tag.post_count"/>
                                </a>
                            </li>
                        </t>
                    </ul>
                </div>
            </div>

            <!-- Recent Posts -->
            <div class="card border-0 shadow-sm">
                <div class="card-body">
                    <h5 class="card-title">Recent Posts</h5>
                    <t t-foreach="recent_posts[:5]" t-as="rpost">
                        <div class="d-flex mb-3">
                            <t t-if="rpost.cover_properties.get('background-image')">
                                <img t-att-src="rpost.cover_properties.get('background-image').replace('url(', '').replace(')', '').replace(&quot;'&quot;, '')"
                                     class="rounded me-3"
                                     style="width: 60px; height: 60px; object-fit: cover;"
                                     t-att-alt="rpost.name"/>
                            </t>
                            <div>
                                <a t-attf-href="/blog/#{slug(blog)}/#{slug(rpost)}"
                                   class="text-decoration-none small fw-medium">
                                    <t t-esc="rpost.name"/>
                                </a>
                                <div class="text-muted small" t-field="rpost.post_date"
                                     t-options="{'format': 'MMM d'}"/>
                            </div>
                        </div>
                    </t>
                </div>
            </div>
        </aside>
    </template>
</odoo>
"""


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


def generate_blog_templates(config: BlogConfig, output_dir: Path) -> dict[str, Path]:
    """Generate all blog template files."""
    cwd = Path.cwd()
    if not validate_output_path(output_dir, cwd):
        raise ValueError(f"Output directory must be within {cwd}")

    generator = BlogTemplateGenerator()
    files_created: dict[str, Path] = {}

    views_dir = output_dir / "views" / "blog"
    views_dir.mkdir(parents=True, exist_ok=True)

    # Generate post template
    post_file = views_dir / "blog_post.xml"
    post_file.write_text(generator.generate_post_template(config))
    files_created["post_template"] = post_file

    # Generate card template
    card_file = views_dir / "blog_card.xml"
    card_file.write_text(generator.generate_card_template(config))
    files_created["card_template"] = card_file

    # Generate SEO template
    seo_file = views_dir / "blog_seo.xml"
    seo_file.write_text(generator.generate_seo_template(config))
    files_created["seo_template"] = seo_file

    # Optional: Related posts
    if config.with_related_posts:
        related_file = views_dir / "blog_related.xml"
        related_file.write_text(generator.generate_related_posts(config))
        files_created["related_posts"] = related_file

    # Optional: Social sharing
    if config.with_social_sharing:
        social_file = views_dir / "blog_social.xml"
        social_file.write_text(generator.generate_social_sharing(config))
        files_created["social_sharing"] = social_file

    # Optional: Sidebar
    if config.with_sidebar:
        sidebar_file = views_dir / "blog_sidebar.xml"
        sidebar_file.write_text(generator.generate_sidebar(config))
        files_created["sidebar"] = sidebar_file

    return files_created


# ============================================================================
# CLI Interface
# ============================================================================


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Odoo blog templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --style modern --module theme_company
  %(prog)s --style minimal --module theme_company --no-author-images
  %(prog)s --style magazine --module theme_company --with-sidebar
        """,
    )

    parser.add_argument(
        "--style",
        choices=list(BLOG_STYLES.keys()),
        default="modern",
        help="Blog template style (default: modern)",
    )
    parser.add_argument(
        "--module",
        help="Odoo module name (e.g., theme_company)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("."),
        help="Output directory (default: current directory)",
    )
    parser.add_argument(
        "--with-related-posts",
        action="store_true",
        default=True,
        help="Include related posts section (default: True)",
    )
    parser.add_argument(
        "--no-related-posts",
        action="store_true",
        help="Exclude related posts section",
    )
    parser.add_argument(
        "--with-social-sharing",
        action="store_true",
        default=True,
        help="Include social sharing buttons (default: True)",
    )
    parser.add_argument(
        "--no-social-sharing",
        action="store_true",
        help="Exclude social sharing buttons",
    )
    parser.add_argument(
        "--with-sidebar",
        action="store_true",
        help="Include blog sidebar template",
    )
    parser.add_argument(
        "--no-author-images",
        action="store_true",
        help="Hide author profile images",
    )
    parser.add_argument(
        "--list-styles",
        action="store_true",
        help="List available blog styles and exit",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    # List styles
    if args.list_styles:
        print("Available blog styles:")
        for style, style_config in BLOG_STYLES.items():
            print(f"  {style}:")
            print(f"    Card style: {style_config.get('card_style')}")
            print(f"    Image ratio: {style_config.get('image_ratio')}")
            print(f"    Reading time: {style_config.get('show_reading_time')}")
        return 0

    # Validate arguments
    if not args.module:
        parser.error("--module is required when generating templates")

    config = BlogConfig(
        style=args.style,
        module_name=args.module,
        with_related_posts=not args.no_related_posts,
        with_social_sharing=not args.no_social_sharing,
        with_sidebar=args.with_sidebar,
        show_author_image=not args.no_author_images,
    )

    try:
        files = generate_blog_templates(config, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Output results
    if args.json:
        json_results = {k: str(v) for k, v in files.items()}
        print(json.dumps(json_results, indent=2))
    else:
        print(f"\nGenerated {args.style} blog templates in {args.output}")
        for file_type, path in files.items():
            print(f"  {file_type}: {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
