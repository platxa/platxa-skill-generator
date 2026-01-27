#!/usr/bin/env python3
"""
Platxa Preview Server

Real-time preview service for Odoo themes with:
- FastAPI REST endpoints
- WebSocket live reload
- CSS variable injection from tokens
- Section template rendering
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xml_escape

# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class PreviewSession:
    """A preview session with tokens and pages."""

    session_id: str
    tokens: dict[str, Any] = field(default_factory=dict)
    pages: dict[str, dict[str, Any]] = field(default_factory=dict)
    websockets: list[Any] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self) -> None:
        """Update last activity time."""
        self.last_activity = datetime.now(timezone.utc)

    def is_expired(self, timeout_seconds: int = 1800) -> bool:
        """Check if session has expired."""
        return datetime.now(timezone.utc) - self.last_activity > timedelta(seconds=timeout_seconds)

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Broadcast message to all connected WebSockets."""
        for ws in self.websockets[:]:
            try:
                await ws.send_json(message)
            except Exception:
                if ws in self.websockets:
                    self.websockets.remove(ws)


# ============================================================================
# Template Renderer
# ============================================================================


class PreviewRenderer:
    """Renders preview HTML from tokens and page configurations."""

    def __init__(self) -> None:
        self.section_renderers: dict[str, Callable[..., str]] = {
            "hero": self._render_hero,
            "hero_small": self._render_hero_small,
            "hero_full": self._render_hero_full,
            "story": self._render_story,
            "values": self._render_values,
            "cta": self._render_cta,
            "features": self._render_features,
            "contact_info": self._render_contact_info,
            "contact_form": self._render_contact_form,
            "team_grid": self._render_team_grid,
            "faq_accordion": self._render_faq_accordion,
            "pricing_table": self._render_pricing_table,
        }

    def render_page(self, session: PreviewSession, page_type: str) -> str:
        """Render a complete page preview."""
        page_config = session.pages.get(page_type, self._default_page(page_type))
        sections_html = self._render_sections(page_config, session.tokens)
        css = self._generate_css(session.tokens)

        return self._wrap_layout(
            content=sections_html,
            css=css,
            title=page_config.get("title", page_type.title()),
            session_id=session.session_id,
        )

    def _render_sections(self, page_config: dict[str, Any], tokens: dict[str, Any]) -> str:
        """Render all sections for a page."""
        sections = page_config.get("sections", ["hero", "cta"])
        html_parts: list[str] = []

        for section in sections:
            section_type = section if isinstance(section, str) else section.get("type", "hero")
            section_data = {} if isinstance(section, str) else section

            renderer = self.section_renderers.get(section_type)
            if renderer:
                html_parts.append(renderer(section_data, tokens, page_config))
            else:
                html_parts.append(f'<!-- Section "{section_type}" not implemented -->')

        return "\n".join(html_parts)

    def _default_page(self, page_type: str) -> dict[str, Any]:
        """Get default page configuration."""
        defaults: dict[str, dict[str, Any]] = {
            "about": {"title": "About Us", "sections": ["hero", "story", "values", "cta"]},
            "contact": {
                "title": "Contact Us",
                "sections": ["hero_small", "contact_info", "contact_form"],
            },
            "services": {"title": "Our Services", "sections": ["hero", "features", "cta"]},
            "team": {"title": "Our Team", "sections": ["hero", "team_grid", "cta"]},
            "faq": {"title": "FAQ", "sections": ["hero_small", "faq_accordion", "cta"]},
            "pricing": {"title": "Pricing", "sections": ["hero", "pricing_table", "cta"]},
            "landing": {"title": "Welcome", "sections": ["hero_full", "features", "cta"]},
        }
        return defaults.get(page_type, {"title": page_type.title(), "sections": ["hero", "cta"]})

    def _generate_css(self, tokens: dict[str, Any]) -> str:
        """Generate CSS from design tokens."""
        colors = tokens.get("colors", {})

        primary = colors.get("primary", {}).get("hex", "#8B35A8")
        accent = colors.get("accent", {}).get("hex", "#2ECCC4")
        dark = colors.get("neutral", {}).get("dark", {}).get("hex", "#1C1C21")
        light = colors.get("neutral", {}).get("light", {}).get("hex", "#F0F0F0")
        bg = colors.get("neutral", {}).get("background", {}).get("hex", "#FAFAFA")

        typography = tokens.get("typography", {})
        font_sans = typography.get("families", {}).get("sans", "'Inter', sans-serif")

        return f"""
:root {{
    --o-color-1: {primary};
    --o-color-2: {accent};
    --o-color-3: {dark};
    --o-color-4: {light};
    --o-color-5: {bg};
}}

body {{
    font-family: {font_sans};
    background-color: var(--o-color-5);
    color: var(--o-color-3);
}}

.o_cc.o_cc1 {{ background-color: var(--o-color-1); color: white; }}
.o_cc.o_cc2 {{ background-color: var(--o-color-2); }}
.o_cc.o_cc3 {{ background-color: var(--o-color-3); color: white; }}
.o_cc.o_cc4 {{ background-color: var(--o-color-4); }}
.o_cc.o_cc5 {{ background-color: var(--o-color-5); }}

.text-primary {{ color: var(--o-color-1) !important; }}
.text-white-75 {{ color: rgba(255,255,255,0.75) !important; }}

.bg-primary {{ background-color: var(--o-color-1) !important; }}

.btn-primary {{
    background-color: var(--o-color-1);
    border-color: var(--o-color-1);
}}
.btn-primary:hover {{
    background-color: color-mix(in srgb, var(--o-color-1) 85%, black);
    border-color: color-mix(in srgb, var(--o-color-1) 85%, black);
}}

.btn-secondary {{
    background-color: var(--o-color-2);
    border-color: var(--o-color-2);
    color: var(--o-color-3);
}}

.btn-outline-primary {{
    color: var(--o-color-1);
    border-color: var(--o-color-1);
}}
.btn-outline-primary:hover {{
    background-color: var(--o-color-1);
    color: white;
}}

.badge.bg-primary {{ background-color: var(--o-color-1) !important; }}

.card {{ border-radius: 0.5rem; }}
.shadow-sm {{ box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075) !important; }}

section {{ overflow: hidden; }}
.pt64 {{ padding-top: 4rem !important; }}
.pb64 {{ padding-bottom: 4rem !important; }}
.pt80 {{ padding-top: 5rem !important; }}
.pb80 {{ padding-bottom: 5rem !important; }}
.pt96 {{ padding-top: 6rem !important; }}
.pb96 {{ padding-bottom: 6rem !important; }}
.pt160 {{ padding-top: 10rem !important; }}
.pb160 {{ padding-bottom: 10rem !important; }}
"""

    def _wrap_layout(self, content: str, css: str, title: str, session_id: str) -> str:
        """Wrap content in HTML layout."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{xml_escape(title)} - Preview</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet">
    <style>{css}</style>
</head>
<body>
    <div id="wrap">
        {content}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Live reload WebSocket
        (function() {{
            const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
            const ws = new WebSocket(protocol + '//' + location.host + '/ws/{session_id}');

            ws.onmessage = function(event) {{
                const data = JSON.parse(event.data);
                if (data.type === 'reload') {{
                    location.reload();
                }} else if (data.type === 'css_update') {{
                    const style = document.querySelector('style');
                    if (style) style.textContent = data.css;
                }}
            }};

            ws.onclose = function() {{
                console.log('Preview connection closed. Reconnecting...');
                setTimeout(() => location.reload(), 2000);
            }};
        }})();
    </script>
</body>
</html>"""

    # Section Renderers

    def _render_hero(
        self, section: dict[str, Any], tokens: dict[str, Any], page: dict[str, Any]
    ) -> str:
        title = section.get("title", page.get("title", "Welcome"))
        subtitle = section.get("subtitle", page.get("description", "Discover what we offer"))
        return f"""
<section class="s_cover pt160 pb160 o_cc o_cc1">
    <div class="container">
        <div class="row">
            <div class="col-lg-8 mx-auto text-center">
                <h1 class="display-3 text-white mb-4">{xml_escape(str(title))}</h1>
                <p class="lead text-white-75">{xml_escape(str(subtitle))}</p>
            </div>
        </div>
    </div>
</section>"""

    def _render_hero_small(
        self, section: dict[str, Any], tokens: dict[str, Any], page: dict[str, Any]
    ) -> str:
        title = section.get("title", page.get("title", "Page Title"))
        return f"""
<section class="s_text_block pt96 pb96 o_cc o_cc1">
    <div class="container text-center">
        <h1 class="display-4 text-white">{xml_escape(str(title))}</h1>
        <nav aria-label="breadcrumb" class="mt-4">
            <ol class="breadcrumb justify-content-center mb-0">
                <li class="breadcrumb-item"><a href="#" class="text-white-50">Home</a></li>
                <li class="breadcrumb-item active text-white">{xml_escape(str(title))}</li>
            </ol>
        </nav>
    </div>
</section>"""

    def _render_hero_full(
        self, section: dict[str, Any], tokens: dict[str, Any], page: dict[str, Any]
    ) -> str:
        title = section.get("title", page.get("title", "Welcome"))
        subtitle = section.get("subtitle", "Your journey starts here")
        return f"""
<section class="s_cover o_cc o_cc1" style="min-height: 100vh;">
    <div class="container h-100 d-flex align-items-center">
        <div class="row">
            <div class="col-lg-8">
                <h1 class="display-2 text-white mb-4">{xml_escape(str(title))}</h1>
                <p class="lead text-white-75 mb-5">{xml_escape(str(subtitle))}</p>
                <div>
                    <a href="#" class="btn btn-lg btn-secondary me-2">Get Started</a>
                    <a href="#" class="btn btn-lg btn-outline-light">Learn More</a>
                </div>
            </div>
        </div>
    </div>
</section>"""

    def _render_story(
        self, section: dict[str, Any], tokens: dict[str, Any], page: dict[str, Any]
    ) -> str:
        return """
<section class="s_text_block pt64 pb64">
    <div class="container">
        <div class="row">
            <div class="col-lg-10 mx-auto">
                <h2 class="h1-fs mb-4">Our Story</h2>
                <p class="lead text-muted mb-4">
                    Founded with a vision to transform the industry, we've grown from a small
                    team of passionate individuals to a leading provider of innovative solutions.
                </p>
                <p>
                    Our journey began when we recognized a gap in the market for truly
                    customer-centric services. Today, we continue to push boundaries.
                </p>
            </div>
        </div>
    </div>
</section>"""

    def _render_values(
        self, section: dict[str, Any], tokens: dict[str, Any], page: dict[str, Any]
    ) -> str:
        return """
<section class="s_features pt64 pb64 o_cc o_cc5">
    <div class="container">
        <h2 class="text-center mb-5">Our Values</h2>
        <div class="row">
            <div class="col-lg-4 text-center mb-4">
                <div class="p-4">
                    <i class="fa fa-3x fa-heart text-primary mb-3"></i>
                    <h4>Integrity</h4>
                    <p class="text-muted">We believe in honest, transparent relationships.</p>
                </div>
            </div>
            <div class="col-lg-4 text-center mb-4">
                <div class="p-4">
                    <i class="fa fa-3x fa-lightbulb-o text-primary mb-3"></i>
                    <h4>Innovation</h4>
                    <p class="text-muted">We constantly seek new ways to solve problems.</p>
                </div>
            </div>
            <div class="col-lg-4 text-center mb-4">
                <div class="p-4">
                    <i class="fa fa-3x fa-users text-primary mb-3"></i>
                    <h4>Collaboration</h4>
                    <p class="text-muted">We work together to achieve shared success.</p>
                </div>
            </div>
        </div>
    </div>
</section>"""

    def _render_features(
        self, section: dict[str, Any], tokens: dict[str, Any], page: dict[str, Any]
    ) -> str:
        return """
<section class="s_features pt80 pb80">
    <div class="container">
        <h2 class="text-center mb-2">Why Choose Us</h2>
        <p class="text-center text-muted mb-5">Everything you need to succeed</p>
        <div class="row">
            <div class="col-lg-4 mb-4">
                <div class="d-flex">
                    <div class="flex-shrink-0">
                        <div class="bg-primary text-white rounded p-3">
                            <i class="fa fa-bolt fa-lg"></i>
                        </div>
                    </div>
                    <div class="flex-grow-1 ms-3">
                        <h5>Lightning Fast</h5>
                        <p class="text-muted">Optimized for maximum performance.</p>
                    </div>
                </div>
            </div>
            <div class="col-lg-4 mb-4">
                <div class="d-flex">
                    <div class="flex-shrink-0">
                        <div class="bg-primary text-white rounded p-3">
                            <i class="fa fa-lock fa-lg"></i>
                        </div>
                    </div>
                    <div class="flex-grow-1 ms-3">
                        <h5>Secure</h5>
                        <p class="text-muted">Enterprise-grade security built-in.</p>
                    </div>
                </div>
            </div>
            <div class="col-lg-4 mb-4">
                <div class="d-flex">
                    <div class="flex-shrink-0">
                        <div class="bg-primary text-white rounded p-3">
                            <i class="fa fa-expand fa-lg"></i>
                        </div>
                    </div>
                    <div class="flex-grow-1 ms-3">
                        <h5>Scalable</h5>
                        <p class="text-muted">Grows with your business needs.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>"""

    def _render_cta(
        self, section: dict[str, Any], tokens: dict[str, Any], page: dict[str, Any]
    ) -> str:
        return """
<section class="s_call_to_action pt80 pb80 o_cc o_cc1">
    <div class="container text-center">
        <h2 class="text-white mb-3">Ready to Get Started?</h2>
        <p class="lead text-white-75 mb-4">Join thousands of satisfied customers today.</p>
        <a href="#" class="btn btn-lg btn-secondary">Contact Us</a>
    </div>
</section>"""

    def _render_contact_info(
        self, section: dict[str, Any], tokens: dict[str, Any], page: dict[str, Any]
    ) -> str:
        return """
<section class="s_text_block pt64 pb32">
    <div class="container">
        <div class="row">
            <div class="col-lg-4 mb-4">
                <div class="card border-0 shadow-sm h-100">
                    <div class="card-body text-center p-4">
                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                             style="width: 60px; height: 60px;">
                            <i class="fa fa-map-marker fa-lg"></i>
                        </div>
                        <h5>Visit Us</h5>
                        <p class="text-muted mb-0">123 Business Street<br/>City, State 12345</p>
                    </div>
                </div>
            </div>
            <div class="col-lg-4 mb-4">
                <div class="card border-0 shadow-sm h-100">
                    <div class="card-body text-center p-4">
                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                             style="width: 60px; height: 60px;">
                            <i class="fa fa-phone fa-lg"></i>
                        </div>
                        <h5>Call Us</h5>
                        <p class="text-muted mb-0">+1 (234) 567-890<br/>Mon-Fri: 9am - 6pm</p>
                    </div>
                </div>
            </div>
            <div class="col-lg-4 mb-4">
                <div class="card border-0 shadow-sm h-100">
                    <div class="card-body text-center p-4">
                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                             style="width: 60px; height: 60px;">
                            <i class="fa fa-envelope fa-lg"></i>
                        </div>
                        <h5>Email Us</h5>
                        <p class="text-muted mb-0">info@company.com<br/>support@company.com</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>"""

    def _render_contact_form(
        self, section: dict[str, Any], tokens: dict[str, Any], page: dict[str, Any]
    ) -> str:
        return """
<section class="s_website_form pt32 pb64">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card border-0 shadow">
                    <div class="card-body p-5">
                        <h3 class="text-center mb-4">Send Us a Message</h3>
                        <form>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Name *</label>
                                    <input type="text" class="form-control" placeholder="Your name">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Email *</label>
                                    <input type="email" class="form-control" placeholder="your@email.com">
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Subject</label>
                                <input type="text" class="form-control" placeholder="How can we help?">
                            </div>
                            <div class="mb-4">
                                <label class="form-label">Message *</label>
                                <textarea class="form-control" rows="5" placeholder="Your message..."></textarea>
                            </div>
                            <div class="text-center">
                                <button type="button" class="btn btn-primary btn-lg px-5">Send Message</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>"""

    def _render_team_grid(
        self, section: dict[str, Any], tokens: dict[str, Any], page: dict[str, Any]
    ) -> str:
        return """
<section class="s_company_team pt64 pb64">
    <div class="container">
        <div class="row">
            <div class="col-lg-3 col-md-6 mb-4">
                <div class="card border-0 text-center h-100 shadow-sm">
                    <div class="card-body py-4">
                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                             style="width: 100px; height: 100px; font-size: 2rem;">
                            <i class="fa fa-user"></i>
                        </div>
                        <h5 class="card-title mb-1">Jane Doe</h5>
                        <p class="text-primary small mb-2">CEO &amp; Founder</p>
                        <p class="text-muted small">Visionary leader with 20+ years experience.</p>
                    </div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-4">
                <div class="card border-0 text-center h-100 shadow-sm">
                    <div class="card-body py-4">
                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                             style="width: 100px; height: 100px; font-size: 2rem;">
                            <i class="fa fa-user"></i>
                        </div>
                        <h5 class="card-title mb-1">John Smith</h5>
                        <p class="text-primary small mb-2">CTO</p>
                        <p class="text-muted small">Tech innovator driving engineering.</p>
                    </div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-4">
                <div class="card border-0 text-center h-100 shadow-sm">
                    <div class="card-body py-4">
                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                             style="width: 100px; height: 100px; font-size: 2rem;">
                            <i class="fa fa-user"></i>
                        </div>
                        <h5 class="card-title mb-1">Alice Johnson</h5>
                        <p class="text-primary small mb-2">COO</p>
                        <p class="text-muted small">Operations expert ensuring delivery.</p>
                    </div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-4">
                <div class="card border-0 text-center h-100 shadow-sm">
                    <div class="card-body py-4">
                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                             style="width: 100px; height: 100px; font-size: 2rem;">
                            <i class="fa fa-user"></i>
                        </div>
                        <h5 class="card-title mb-1">Bob Williams</h5>
                        <p class="text-primary small mb-2">Head of Design</p>
                        <p class="text-muted small">Creative director crafting experiences.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>"""

    def _render_faq_accordion(
        self, section: dict[str, Any], tokens: dict[str, Any], page: dict[str, Any]
    ) -> str:
        return """
<section class="s_faq_collapse pt64 pb64">
    <div class="container">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="accordion" id="faqAccordion">
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#faq1">
                                What services do you offer?
                            </button>
                        </h2>
                        <div id="faq1" class="accordion-collapse collapse show" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                We offer consulting, development, and support services.
                            </div>
                        </div>
                    </div>
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq2">
                                How long does a project take?
                            </button>
                        </h2>
                        <div id="faq2" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                Timelines vary based on scope. Small projects take weeks, larger ones months.
                            </div>
                        </div>
                    </div>
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq3">
                                Do you offer support?
                            </button>
                        </h2>
                        <div id="faq3" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                Yes! We offer various support packages from basic to 24/7 dedicated.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>"""

    def _render_pricing_table(
        self, section: dict[str, Any], tokens: dict[str, Any], page: dict[str, Any]
    ) -> str:
        return """
<section class="s_comparisons pt64 pb64">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="card h-100 text-center">
                    <div class="card-header py-3 bg-light">
                        <h4 class="my-0">Starter</h4>
                    </div>
                    <div class="card-body d-flex flex-column">
                        <h1 class="card-title mb-4">$19<small class="text-muted">/mo</small></h1>
                        <ul class="list-unstyled mb-4 flex-grow-1">
                            <li class="mb-2"><i class="fa fa-check text-success me-2"></i>5 users</li>
                            <li class="mb-2"><i class="fa fa-check text-success me-2"></i>10 GB storage</li>
                            <li class="mb-2"><i class="fa fa-check text-success me-2"></i>Email support</li>
                        </ul>
                        <a href="#" class="btn btn-outline-primary w-100">Get Started</a>
                    </div>
                </div>
            </div>
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="card h-100 text-center border-primary">
                    <div class="card-header py-3 bg-primary text-white">
                        <h4 class="my-0">Professional</h4>
                    </div>
                    <div class="card-body d-flex flex-column">
                        <h1 class="card-title mb-4">$49<small class="text-muted">/mo</small></h1>
                        <ul class="list-unstyled mb-4 flex-grow-1">
                            <li class="mb-2"><i class="fa fa-check text-success me-2"></i>25 users</li>
                            <li class="mb-2"><i class="fa fa-check text-success me-2"></i>50 GB storage</li>
                            <li class="mb-2"><i class="fa fa-check text-success me-2"></i>Priority support</li>
                        </ul>
                        <a href="#" class="btn btn-primary w-100">Get Started</a>
                    </div>
                </div>
            </div>
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="card h-100 text-center">
                    <div class="card-header py-3 bg-light">
                        <h4 class="my-0">Enterprise</h4>
                    </div>
                    <div class="card-body d-flex flex-column">
                        <h1 class="card-title mb-4">$99<small class="text-muted">/mo</small></h1>
                        <ul class="list-unstyled mb-4 flex-grow-1">
                            <li class="mb-2"><i class="fa fa-check text-success me-2"></i>Unlimited users</li>
                            <li class="mb-2"><i class="fa fa-check text-success me-2"></i>200 GB storage</li>
                            <li class="mb-2"><i class="fa fa-check text-success me-2"></i>24/7 support</li>
                        </ul>
                        <a href="#" class="btn btn-outline-primary w-100">Contact Sales</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>"""


# ============================================================================
# Session Manager
# ============================================================================


class SessionManager:
    """Manages preview sessions."""

    def __init__(self, max_sessions: int = 100, timeout_seconds: int = 1800):
        self.sessions: dict[str, PreviewSession] = {}
        self.max_sessions = max_sessions
        self.timeout_seconds = timeout_seconds

    def create_session(self, tokens: dict[str, Any] | None = None) -> PreviewSession:
        """Create a new preview session."""
        self._cleanup_expired()

        if len(self.sessions) >= self.max_sessions:
            raise RuntimeError("Maximum session limit reached")

        session_id = str(uuid.uuid4())[:8]
        session = PreviewSession(
            session_id=session_id,
            tokens=tokens or {},
        )
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> PreviewSession | None:
        """Get a session by ID."""
        session = self.sessions.get(session_id)
        if session and not session.is_expired(self.timeout_seconds):
            session.touch()
            return session
        return None

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def _cleanup_expired(self) -> None:
        """Remove expired sessions."""
        expired = [
            sid
            for sid, session in self.sessions.items()
            if session.is_expired(self.timeout_seconds)
        ]
        for sid in expired:
            del self.sessions[sid]


# ============================================================================
# Static HTML Generator (No FastAPI required)
# ============================================================================


def generate_static_preview(
    tokens_path: Path | None,
    output_dir: Path,
    page_types: list[str] | None = None,
) -> dict[str, Path]:
    """Generate static HTML preview files."""
    tokens: dict[str, Any] = {}
    if tokens_path and tokens_path.exists():
        tokens = json.loads(tokens_path.read_text())

    if page_types is None:
        page_types = ["about", "contact", "services", "team", "faq", "pricing", "landing"]

    output_dir.mkdir(parents=True, exist_ok=True)

    session = PreviewSession(session_id="static", tokens=tokens)
    renderer = PreviewRenderer()
    files_created: dict[str, Path] = {}

    for page_type in page_types:
        html = renderer.render_page(session, page_type)
        output_file = output_dir / f"{page_type}.html"
        output_file.write_text(html)
        files_created[page_type] = output_file

    return files_created


# ============================================================================
# CLI
# ============================================================================


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Platxa Preview Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --static --output ./preview --tokens tokens.json
  %(prog)s --host 0.0.0.0 --port 8080  (requires fastapi)
        """,
    )

    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to listen on (default: 8080)",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Enable development mode with auto-reload",
    )
    parser.add_argument(
        "--tokens",
        type=Path,
        help="Path to tokens JSON file",
    )
    parser.add_argument(
        "--static",
        action="store_true",
        help="Generate static HTML files instead of running server",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("./preview"),
        help="Output directory for static files (default: ./preview)",
    )
    parser.add_argument(
        "--pages",
        help="Comma-separated list of page types to generate",
    )

    args = parser.parse_args()

    # Static generation mode (no FastAPI required)
    if args.static:
        page_types = args.pages.split(",") if args.pages else None
        files = generate_static_preview(args.tokens, args.output, page_types)
        print(f"Generated {len(files)} preview files in {args.output}")
        for page_type, path in files.items():
            print(f"  {page_type}: {path}")
        return 0

    # Server mode (requires FastAPI)
    try:
        import uvicorn
        from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import HTMLResponse
    except ImportError:
        print("Error: FastAPI not installed.", file=sys.stderr)
        print("Install with: pip install fastapi uvicorn", file=sys.stderr)
        print("Or use --static mode to generate static HTML files.", file=sys.stderr)
        return 1

    # Create FastAPI app
    app = FastAPI(
        title="Platxa Preview Service",
        description="Real-time preview for Odoo themes",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    session_manager = SessionManager()
    renderer = PreviewRenderer()

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "healthy"}

    @app.post("/api/sessions")
    async def create_session(tokens: dict[str, Any] | None = None) -> dict[str, str]:
        try:
            session = session_manager.create_session(tokens)
            return {"session_id": session.session_id}
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e)) from e

    @app.get("/api/sessions/{session_id}")
    async def get_session(session_id: str) -> dict[str, Any]:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return {
            "session_id": session.session_id,
            "created_at": session.created_at.isoformat(),
            "pages": list(session.pages.keys()),
        }

    @app.delete("/api/sessions/{session_id}")
    async def delete_session(session_id: str) -> dict[str, str]:
        if session_manager.delete_session(session_id):
            return {"status": "deleted"}
        raise HTTPException(status_code=404, detail="Session not found")

    @app.put("/api/sessions/{session_id}/tokens")
    async def update_tokens(session_id: str, tokens: dict[str, Any]) -> dict[str, str]:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        session.tokens = tokens
        await session.broadcast({"type": "reload"})
        return {"status": "updated"}

    @app.get("/preview/{session_id}/{page_type}")
    async def preview_page(session_id: str, page_type: str) -> HTMLResponse:
        session = session_manager.get_session(session_id)
        if not session:
            session = session_manager.create_session()
            session.session_id = session_id
            session_manager.sessions[session_id] = session

        html = renderer.render_page(session, page_type)
        return HTMLResponse(html)

    @app.websocket("/ws/{session_id}")
    async def websocket_endpoint(websocket: WebSocket, session_id: str) -> None:
        await websocket.accept()

        session = session_manager.get_session(session_id)
        if not session:
            await websocket.close(code=4004)
            return

        session.websockets.append(websocket)

        try:
            while True:
                data = await websocket.receive_json()
                session.touch()

                if data.get("type") == "token_update":
                    session.tokens = data.get("tokens", {})
                    await session.broadcast({"type": "reload"})
                elif data.get("type") == "page_update":
                    page_id = data.get("page_id")
                    if page_id:
                        session.pages[page_id] = data.get("content", {})
                        await session.broadcast({"type": "reload"})

        except WebSocketDisconnect:
            pass
        finally:
            if websocket in session.websockets:
                session.websockets.remove(websocket)

    print(f"Starting Platxa Preview Server on http://{args.host}:{args.port}")
    print(f"Preview URL: http://localhost:{args.port}/preview/demo/about")

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.dev,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
