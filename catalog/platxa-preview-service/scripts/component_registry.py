#!/usr/bin/env python3
"""
Platxa Component Registry

Registry for browsable Odoo website components with:
- Component definitions with variants and options
- Category-based organization
- Search functionality
- Sample content generation
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ComponentVariant:
    """A variant of a component (e.g., 2-column vs 3-column)."""

    id: str
    name: str
    defaults: dict[str, Any] = field(default_factory=dict)


@dataclass
class ComponentOption:
    """A customizable option for a component."""

    id: str
    name: str
    type: str  # boolean, select, number, text, color
    default: Any
    options: list[str] | None = None  # For select type
    min_value: int | None = None  # For number type
    max_value: int | None = None  # For number type


@dataclass
class ComponentDefinition:
    """Definition of a reusable component."""

    id: str
    category: str
    name: str
    description: str
    template: str
    thumbnail: str = ""
    variants: list[ComponentVariant] = field(default_factory=list)
    options: list[ComponentOption] = field(default_factory=list)
    tokens_used: list[str] = field(default_factory=list)
    qweb_template: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "category": self.category,
            "name": self.name,
            "description": self.description,
            "template": self.template,
            "thumbnail": self.thumbnail,
            "variants": [
                {"id": v.id, "name": v.name, "defaults": v.defaults}
                for v in self.variants
            ],
            "options": [
                {
                    "id": o.id,
                    "name": o.name,
                    "type": o.type,
                    "default": o.default,
                    "options": o.options,
                    "min": o.min_value,
                    "max": o.max_value,
                }
                for o in self.options
            ],
            "tokens_used": self.tokens_used,
            "qweb_template": self.qweb_template,
        }


class ComponentRegistry:
    """Registry of all available components."""

    def __init__(self, data_path: Path | None = None):
        self._components: dict[str, ComponentDefinition] = {}
        self._categories: dict[str, list[str]] = {}
        self._load_builtin_components()
        if data_path and data_path.exists():
            self._load_from_file(data_path)

    def register(self, component: ComponentDefinition) -> None:
        """Register a component."""
        key = f"{component.category}/{component.id}"
        self._components[key] = component
        if component.category not in self._categories:
            self._categories[component.category] = []
        if component.id not in self._categories[component.category]:
            self._categories[component.category].append(component.id)

    def get_component(
        self, category: str, component_id: str
    ) -> ComponentDefinition | None:
        """Get a component by category and ID."""
        key = f"{category}/{component_id}"
        return self._components.get(key)

    def list_categories(self) -> list[str]:
        """List all categories."""
        return list(self._categories.keys())

    def list_by_category(self, category: str) -> list[ComponentDefinition]:
        """List all components in a category."""
        component_ids = self._categories.get(category, [])
        result: list[ComponentDefinition] = []
        for cid in component_ids:
            comp = self._components.get(f"{category}/{cid}")
            if comp is not None:
                result.append(comp)
        return result

    def list_all(self) -> list[ComponentDefinition]:
        """List all components."""
        return list(self._components.values())

    def search(self, query: str) -> list[ComponentDefinition]:
        """Search components by name or description."""
        query_lower = query.lower()
        return [
            c
            for c in self._components.values()
            if query_lower in c.name.lower() or query_lower in c.description.lower()
        ]

    def _load_from_file(self, path: Path) -> None:
        """Load components from a JSON file."""
        data = json.loads(path.read_text())
        for comp_data in data.get("components", []):
            component = self._parse_component(comp_data)
            self.register(component)

    def _parse_component(self, data: dict[str, Any]) -> ComponentDefinition:
        """Parse a component from dictionary data."""
        variants = []
        for v in data.get("variants", []):
            variants.append(
                ComponentVariant(
                    id=str(v.get("id", "")),
                    name=str(v.get("name", "")),
                    defaults=v.get("defaults", {}),
                )
            )

        options = []
        for o in data.get("options", []):
            options.append(
                ComponentOption(
                    id=str(o.get("id", "")),
                    name=str(o.get("name", "")),
                    type=str(o.get("type", "text")),
                    default=o.get("default"),
                    options=o.get("options"),
                    min_value=o.get("min"),
                    max_value=o.get("max"),
                )
            )

        return ComponentDefinition(
            id=str(data.get("id", "")),
            category=str(data.get("category", "")),
            name=str(data.get("name", "")),
            description=str(data.get("description", "")),
            template=str(data.get("template", "")),
            thumbnail=str(data.get("thumbnail", "")),
            variants=variants,
            options=options,
            tokens_used=data.get("tokens_used", []),
            qweb_template=str(data.get("qweb_template", "")),
        )

    def _load_builtin_components(self) -> None:
        """Load built-in component definitions."""
        builtin = [
            # Hero sections
            ComponentDefinition(
                id="hero_banner",
                category="hero",
                name="Hero Banner",
                description="Full-width hero section with background image and CTA",
                template="hero/hero_banner",
                qweb_template="s_cover",
                variants=[
                    ComponentVariant("image", "Image Background", {"bg_type": "image"}),
                    ComponentVariant(
                        "gradient", "Gradient Background", {"bg_type": "gradient"}
                    ),
                    ComponentVariant("video", "Video Background", {"bg_type": "video"}),
                ],
                options=[
                    ComponentOption(
                        "alignment",
                        "Text Alignment",
                        "select",
                        "center",
                        ["left", "center", "right"],
                    ),
                    ComponentOption(
                        "overlay", "Dark Overlay", "boolean", True
                    ),
                    ComponentOption(
                        "height", "Height", "select", "full", ["full", "large", "medium"]
                    ),
                ],
                tokens_used=["primary", "background"],
            ),
            ComponentDefinition(
                id="hero_split",
                category="hero",
                name="Hero Split",
                description="Side-by-side hero with image and text",
                template="hero/hero_split",
                qweb_template="s_image_text",
                variants=[
                    ComponentVariant(
                        "image_right", "Image Right", {"image_position": "right"}
                    ),
                    ComponentVariant(
                        "image_left", "Image Left", {"image_position": "left"}
                    ),
                ],
                options=[
                    ComponentOption(
                        "image_ratio",
                        "Image Ratio",
                        "select",
                        "1:1",
                        ["1:1", "4:3", "16:9"],
                    ),
                ],
                tokens_used=["primary", "accent"],
            ),
            # Features sections
            ComponentDefinition(
                id="features_grid",
                category="features",
                name="Features Grid",
                description="Display features in a responsive grid layout",
                template="features/features_grid",
                qweb_template="s_features_grid",
                variants=[
                    ComponentVariant("2col", "2 Columns", {"columns": 2}),
                    ComponentVariant("3col", "3 Columns", {"columns": 3}),
                    ComponentVariant("4col", "4 Columns", {"columns": 4}),
                ],
                options=[
                    ComponentOption("show_icons", "Show Icons", "boolean", True),
                    ComponentOption(
                        "icon_style",
                        "Icon Style",
                        "select",
                        "circle",
                        ["circle", "square", "none"],
                    ),
                    ComponentOption(
                        "card_style",
                        "Card Style",
                        "select",
                        "shadow",
                        ["shadow", "border", "flat"],
                    ),
                ],
                tokens_used=["primary", "accent", "background"],
            ),
            ComponentDefinition(
                id="features_list",
                category="features",
                name="Features List",
                description="Vertical list of features with icons",
                template="features/features_list",
                qweb_template="s_features",
                variants=[
                    ComponentVariant("icons", "With Icons", {"show_icons": True}),
                    ComponentVariant("checkmarks", "Checkmarks", {"icon": "check"}),
                ],
                options=[
                    ComponentOption(
                        "icon_color", "Icon Color", "select", "primary", ["primary", "accent"]
                    ),
                ],
                tokens_used=["primary"],
            ),
            # Content sections
            ComponentDefinition(
                id="text_block",
                category="content",
                name="Text Block",
                description="Simple text content section",
                template="content/text_block",
                qweb_template="s_text_block",
                variants=[
                    ComponentVariant("centered", "Centered", {"align": "center"}),
                    ComponentVariant("left", "Left Aligned", {"align": "left"}),
                ],
                options=[
                    ComponentOption(
                        "width", "Content Width", "select", "narrow", ["narrow", "medium", "wide"]
                    ),
                ],
                tokens_used=["background"],
            ),
            ComponentDefinition(
                id="text_image",
                category="content",
                name="Text with Image",
                description="Text content alongside an image",
                template="content/text_image",
                qweb_template="s_text_image",
                variants=[
                    ComponentVariant("image_right", "Image Right", {"image_position": "right"}),
                    ComponentVariant("image_left", "Image Left", {"image_position": "left"}),
                ],
                options=[
                    ComponentOption(
                        "image_size",
                        "Image Size",
                        "select",
                        "half",
                        ["third", "half", "two-thirds"],
                    ),
                ],
                tokens_used=["primary", "background"],
            ),
            # Testimonials
            ComponentDefinition(
                id="testimonials_cards",
                category="testimonials",
                name="Testimonial Cards",
                description="Display testimonials in card format",
                template="testimonials/testimonials_cards",
                qweb_template="s_references",
                variants=[
                    ComponentVariant("1col", "Single Column", {"columns": 1}),
                    ComponentVariant("2col", "2 Columns", {"columns": 2}),
                    ComponentVariant("3col", "3 Columns", {"columns": 3}),
                ],
                options=[
                    ComponentOption("show_photo", "Show Photos", "boolean", True),
                    ComponentOption("show_rating", "Show Rating", "boolean", False),
                ],
                tokens_used=["primary", "background"],
            ),
            # CTA sections
            ComponentDefinition(
                id="cta_banner",
                category="cta",
                name="CTA Banner",
                description="Full-width call-to-action section",
                template="cta/cta_banner",
                qweb_template="s_call_to_action",
                variants=[
                    ComponentVariant("simple", "Simple", {"style": "simple"}),
                    ComponentVariant("with_image", "With Image", {"style": "image"}),
                ],
                options=[
                    ComponentOption(
                        "bg_color",
                        "Background",
                        "select",
                        "primary",
                        ["primary", "accent", "dark"],
                    ),
                ],
                tokens_used=["primary", "accent"],
            ),
            # Team sections
            ComponentDefinition(
                id="team_grid",
                category="team",
                name="Team Grid",
                description="Display team members in a grid",
                template="team/team_grid",
                qweb_template="s_company_team",
                variants=[
                    ComponentVariant("2col", "2 Columns", {"columns": 2}),
                    ComponentVariant("3col", "3 Columns", {"columns": 3}),
                    ComponentVariant("4col", "4 Columns", {"columns": 4}),
                ],
                options=[
                    ComponentOption("show_social", "Show Social Links", "boolean", True),
                    ComponentOption("show_role", "Show Role", "boolean", True),
                ],
                tokens_used=["primary", "background"],
            ),
            # Pricing sections
            ComponentDefinition(
                id="pricing_cards",
                category="pricing",
                name="Pricing Cards",
                description="Pricing comparison cards",
                template="pricing/pricing_cards",
                qweb_template="s_comparisons",
                variants=[
                    ComponentVariant("2plans", "2 Plans", {"plans": 2}),
                    ComponentVariant("3plans", "3 Plans", {"plans": 3}),
                    ComponentVariant("4plans", "4 Plans", {"plans": 4}),
                ],
                options=[
                    ComponentOption("highlight", "Highlight Popular", "boolean", True),
                    ComponentOption("show_features", "Show Features", "boolean", True),
                ],
                tokens_used=["primary", "accent", "background"],
            ),
            # FAQ sections
            ComponentDefinition(
                id="faq_accordion",
                category="faq",
                name="FAQ Accordion",
                description="Collapsible FAQ section",
                template="faq/faq_accordion",
                qweb_template="s_faq_collapse",
                variants=[
                    ComponentVariant("single", "Single Open", {"multi_open": False}),
                    ComponentVariant("multi", "Multi Open", {"multi_open": True}),
                ],
                options=[
                    ComponentOption("show_icons", "Show Icons", "boolean", True),
                ],
                tokens_used=["primary", "background"],
            ),
            # Contact sections
            ComponentDefinition(
                id="contact_form",
                category="contact",
                name="Contact Form",
                description="Contact form section",
                template="contact/contact_form",
                qweb_template="s_website_form",
                variants=[
                    ComponentVariant("simple", "Simple", {"fields": "basic"}),
                    ComponentVariant("detailed", "Detailed", {"fields": "extended"}),
                ],
                options=[
                    ComponentOption("show_map", "Show Map", "boolean", False),
                    ComponentOption("show_info", "Show Contact Info", "boolean", True),
                ],
                tokens_used=["primary", "background"],
            ),
            # Footer sections
            ComponentDefinition(
                id="footer_columns",
                category="footer",
                name="Footer Columns",
                description="Multi-column footer",
                template="footer/footer_columns",
                qweb_template="website.footer_custom",
                variants=[
                    ComponentVariant("3col", "3 Columns", {"columns": 3}),
                    ComponentVariant("4col", "4 Columns", {"columns": 4}),
                    ComponentVariant("5col", "5 Columns", {"columns": 5}),
                ],
                options=[
                    ComponentOption("show_social", "Show Social Icons", "boolean", True),
                    ComponentOption("show_newsletter", "Newsletter Signup", "boolean", False),
                ],
                tokens_used=["primary", "background"],
            ),
        ]

        for component in builtin:
            self.register(component)


# Sample content for previews
SAMPLE_CONTENT: dict[str, dict[str, Any]] = {
    "hero": {
        "title": "Transform Your Business Today",
        "subtitle": "Innovative solutions for modern challenges",
        "cta_primary": "Get Started",
        "cta_secondary": "Learn More",
        "image": "/static/samples/hero-image.jpg",
    },
    "features": {
        "title": "Why Choose Us",
        "subtitle": "Features that set us apart",
        "items": [
            {
                "icon": "fa-rocket",
                "title": "Fast Delivery",
                "description": "Quick turnaround times for all projects",
            },
            {
                "icon": "fa-shield",
                "title": "Secure",
                "description": "Enterprise-grade security standards",
            },
            {
                "icon": "fa-chart-line",
                "title": "Analytics",
                "description": "Real-time insights and reporting",
            },
            {
                "icon": "fa-headset",
                "title": "Support",
                "description": "24/7 dedicated customer support",
            },
        ],
    },
    "content": {
        "title": "About Our Company",
        "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.",
        "image": "/static/samples/content-image.jpg",
    },
    "testimonials": {
        "title": "What Our Clients Say",
        "items": [
            {
                "name": "Sarah Johnson",
                "role": "CEO, TechCorp",
                "quote": "Exceptional service and outstanding results. Highly recommended!",
                "avatar": "/static/samples/avatar-1.jpg",
                "rating": 5,
            },
            {
                "name": "Michael Chen",
                "role": "CTO, StartupXYZ",
                "quote": "They transformed our online presence completely.",
                "avatar": "/static/samples/avatar-2.jpg",
                "rating": 5,
            },
            {
                "name": "Emily Rodriguez",
                "role": "Director, GlobalCo",
                "quote": "Professional team with excellent communication.",
                "avatar": "/static/samples/avatar-3.jpg",
                "rating": 5,
            },
        ],
    },
    "cta": {
        "title": "Ready to Get Started?",
        "subtitle": "Join thousands of satisfied customers",
        "cta_text": "Start Free Trial",
        "secondary_text": "Contact Sales",
    },
    "team": {
        "title": "Meet Our Team",
        "subtitle": "The people behind our success",
        "members": [
            {
                "name": "John Smith",
                "role": "CEO",
                "image": "/static/samples/team-1.jpg",
                "linkedin": "#",
                "twitter": "#",
            },
            {
                "name": "Jane Doe",
                "role": "CTO",
                "image": "/static/samples/team-2.jpg",
                "linkedin": "#",
                "twitter": "#",
            },
            {
                "name": "Bob Wilson",
                "role": "Design Lead",
                "image": "/static/samples/team-3.jpg",
                "linkedin": "#",
                "twitter": "#",
            },
        ],
    },
    "pricing": {
        "title": "Simple Pricing",
        "subtitle": "Choose the plan that works for you",
        "plans": [
            {
                "name": "Starter",
                "price": 29,
                "period": "month",
                "features": ["5 Users", "10GB Storage", "Email Support"],
                "cta": "Start Free",
                "popular": False,
            },
            {
                "name": "Professional",
                "price": 79,
                "period": "month",
                "features": ["25 Users", "100GB Storage", "Priority Support", "API Access"],
                "cta": "Get Started",
                "popular": True,
            },
            {
                "name": "Enterprise",
                "price": 199,
                "period": "month",
                "features": [
                    "Unlimited Users",
                    "1TB Storage",
                    "24/7 Support",
                    "Custom Integration",
                ],
                "cta": "Contact Sales",
                "popular": False,
            },
        ],
    },
    "faq": {
        "title": "Frequently Asked Questions",
        "items": [
            {
                "question": "How do I get started?",
                "answer": "Simply sign up for a free account and follow our onboarding guide.",
            },
            {
                "question": "What payment methods do you accept?",
                "answer": "We accept all major credit cards, PayPal, and bank transfers.",
            },
            {
                "question": "Can I cancel anytime?",
                "answer": "Yes, you can cancel your subscription at any time with no penalties.",
            },
            {
                "question": "Do you offer refunds?",
                "answer": "We offer a 30-day money-back guarantee on all plans.",
            },
        ],
    },
    "contact": {
        "title": "Get in Touch",
        "subtitle": "We'd love to hear from you",
        "email": "hello@example.com",
        "phone": "+1 (555) 123-4567",
        "address": "123 Business Street, City, ST 12345",
    },
    "footer": {
        "company_name": "Company Name",
        "tagline": "Building better solutions",
        "columns": [
            {
                "title": "Product",
                "links": [
                    {"text": "Features", "url": "#"},
                    {"text": "Pricing", "url": "#"},
                    {"text": "API", "url": "#"},
                ],
            },
            {
                "title": "Company",
                "links": [
                    {"text": "About", "url": "#"},
                    {"text": "Blog", "url": "#"},
                    {"text": "Careers", "url": "#"},
                ],
            },
            {
                "title": "Support",
                "links": [
                    {"text": "Help Center", "url": "#"},
                    {"text": "Contact", "url": "#"},
                    {"text": "Status", "url": "#"},
                ],
            },
        ],
        "social": [
            {"platform": "twitter", "url": "#"},
            {"platform": "linkedin", "url": "#"},
            {"platform": "github", "url": "#"},
        ],
    },
}


def get_sample_content(category: str) -> dict[str, Any]:
    """Get sample content for a category."""
    return SAMPLE_CONTENT.get(category, {})


if __name__ == "__main__":
    # Demo: List all components
    registry = ComponentRegistry()
    print("Component Library")
    print("=" * 50)
    for category in registry.list_categories():
        print(f"\n{category.upper()}")
        print("-" * 30)
        for comp in registry.list_by_category(category):
            variants = ", ".join(v.id for v in comp.variants)
            print(f"  {comp.id}: {comp.name}")
            print(f"    Variants: {variants}")
