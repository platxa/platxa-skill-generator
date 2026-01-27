#!/usr/bin/env python3
"""
Platxa Odoo Page Generator

Generates complete, production-ready Odoo website pages with:
- QWeb templates using semantic HTML5
- Page records for URL routing
- Menu entries for navigation
- SEO metadata (title, description, Open Graph)
- Breadcrumb navigation
- Mobile-responsive sections
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xml_escape


# ============================================================================
# Page Type Definitions
# ============================================================================

PAGE_COMPOSITIONS: dict[str, list[str]] = {
    'about': ['hero', 'story', 'values', 'team_preview', 'cta'],
    'contact': ['hero_small', 'contact_info', 'contact_form', 'map'],
    'services': ['hero', 'services_intro', 'services_grid', 'process', 'cta'],
    'team': ['hero', 'team_intro', 'team_grid', 'cta'],
    'faq': ['hero_small', 'faq_intro', 'faq_accordion', 'contact_cta'],
    'pricing': ['hero', 'pricing_intro', 'pricing_table', 'faq_preview', 'cta'],
    'portfolio': ['hero', 'portfolio_intro', 'portfolio_grid', 'cta'],
    'landing': ['hero_full', 'features', 'benefits', 'testimonials', 'pricing_preview', 'cta'],
}

PAGE_DEFAULTS: dict[str, dict[str, str]] = {
    'about': {
        'title': 'About Us',
        'description': 'Learn about our company, mission, values, and the team behind our success.',
        'menu_label': 'About',
        'sequence': '20',
    },
    'contact': {
        'title': 'Contact Us',
        'description': 'Get in touch with us. We\'d love to hear from you.',
        'menu_label': 'Contact',
        'sequence': '90',
    },
    'services': {
        'title': 'Our Services',
        'description': 'Discover our comprehensive range of services designed to meet your needs.',
        'menu_label': 'Services',
        'sequence': '30',
    },
    'team': {
        'title': 'Our Team',
        'description': 'Meet the dedicated professionals who make it all happen.',
        'menu_label': 'Team',
        'sequence': '40',
    },
    'faq': {
        'title': 'FAQ',
        'description': 'Find answers to commonly asked questions about our products and services.',
        'menu_label': 'FAQ',
        'sequence': '70',
    },
    'pricing': {
        'title': 'Pricing',
        'description': 'Simple, transparent pricing that scales with your needs.',
        'menu_label': 'Pricing',
        'sequence': '50',
    },
    'portfolio': {
        'title': 'Our Work',
        'description': 'Explore our portfolio of successful projects and case studies.',
        'menu_label': 'Portfolio',
        'sequence': '35',
    },
    'landing': {
        'title': 'Welcome',
        'description': 'Discover how we can help you achieve your goals.',
        'menu_label': 'Home',
        'sequence': '10',
    },
}


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class PageConfig:
    """Configuration for a single page."""
    page_type: str
    module_name: str
    title: str = ''
    description: str = ''
    menu_label: str = ''
    url: str = ''
    sequence: int = 10
    with_seo: bool = True
    company_name: str = 'Company Name'
    sections: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Apply defaults based on page type."""
        defaults = PAGE_DEFAULTS.get(self.page_type, {})

        if not self.title:
            self.title = defaults.get('title', self.page_type.title())
        if not self.description:
            self.description = defaults.get('description', f'{self.title} page')
        if not self.menu_label:
            self.menu_label = defaults.get('menu_label', self.title)
        if not self.url:
            self.url = f'/{self.page_type}'
        if not self.sections:
            self.sections = PAGE_COMPOSITIONS.get(self.page_type, ['hero', 'cta'])
        if self.sequence == 10:
            self.sequence = int(defaults.get('sequence', '10'))

    @property
    def template_id(self) -> str:
        """Generate template ID."""
        return f'page_{self.page_type}'

    @property
    def page_record_id(self) -> str:
        """Generate page record ID."""
        return f'page_{self.page_type}'

    @property
    def menu_record_id(self) -> str:
        """Generate menu record ID."""
        return f'menu_{self.page_type}'

    @property
    def seo_template_id(self) -> str:
        """Generate SEO template ID."""
        return f'page_{self.page_type}_seo'


# ============================================================================
# Section Templates
# ============================================================================

class SectionGenerator:
    """Generates QWeb section templates."""

    @staticmethod
    def hero(config: PageConfig) -> str:
        """Full-width hero with parallax background."""
        return f'''
                <!-- Hero Section -->
                <section class="s_cover parallax s_parallax_is_fixed pt160 pb160 o_cc o_cc1"
                         data-scroll-background-ratio="1">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-8 mx-auto text-center">
                                <h1 class="display-3 text-white">{xml_escape(config.title)}</h1>
                                <p class="lead text-white-75">
                                    {xml_escape(config.description)}
                                </p>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def hero_small(config: PageConfig) -> str:
        """Compact hero for interior pages with breadcrumb."""
        return f'''
                <!-- Hero Section (Compact) -->
                <section class="s_text_block pt96 pb96 o_cc o_cc1">
                    <div class="container text-center">
                        <h1 class="display-4 text-white">{xml_escape(config.title)}</h1>
                        <p class="lead text-white-75">{xml_escape(config.description)}</p>
                        <!-- Breadcrumb -->
                        <nav aria-label="breadcrumb" class="mt-4">
                            <ol class="breadcrumb justify-content-center mb-0">
                                <li class="breadcrumb-item"><a href="/" class="text-white-50">Home</a></li>
                                <li class="breadcrumb-item active text-white" aria-current="page">{xml_escape(config.menu_label)}</li>
                            </ol>
                        </nav>
                    </div>
                </section>'''

    @staticmethod
    def hero_full(config: PageConfig) -> str:
        """Full-screen hero for landing pages."""
        return f'''
                <!-- Full Hero Section -->
                <section class="s_cover parallax s_parallax_is_fixed o_cc o_cc1"
                         data-scroll-background-ratio="1"
                         style="min-height: 100vh;">
                    <div class="container h-100 d-flex align-items-center">
                        <div class="row">
                            <div class="col-lg-8">
                                <h1 class="display-2 text-white mb-4">{xml_escape(config.title)}</h1>
                                <p class="lead text-white-75 mb-5">
                                    {xml_escape(config.description)}
                                </p>
                                <div class="s_btn">
                                    <a href="/contact" class="btn btn-lg btn-secondary me-2">Get Started</a>
                                    <a href="/about" class="btn btn-lg btn-outline-light">Learn More</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def story(config: PageConfig) -> str:
        """Company story section."""
        return '''
                <!-- Our Story Section -->
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
                                    customer-centric services. Today, we continue to push boundaries and
                                    deliver excellence in everything we do.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def values(config: PageConfig) -> str:
        """Core values section with icons."""
        return '''
                <!-- Our Values Section -->
                <section class="s_features pt64 pb64 o_cc o_cc5">
                    <div class="container">
                        <h2 class="text-center mb-5">Our Values</h2>
                        <div class="row">
                            <div class="col-lg-4 text-center mb-4">
                                <div class="s_feature_box p-4">
                                    <i class="fa fa-3x fa-heart text-primary mb-3"/>
                                    <h4>Integrity</h4>
                                    <p class="text-muted">We believe in honest, transparent relationships with our clients and partners.</p>
                                </div>
                            </div>
                            <div class="col-lg-4 text-center mb-4">
                                <div class="s_feature_box p-4">
                                    <i class="fa fa-3x fa-lightbulb-o text-primary mb-3"/>
                                    <h4>Innovation</h4>
                                    <p class="text-muted">We constantly seek new ways to solve problems and improve our services.</p>
                                </div>
                            </div>
                            <div class="col-lg-4 text-center mb-4">
                                <div class="s_feature_box p-4">
                                    <i class="fa fa-3x fa-users text-primary mb-3"/>
                                    <h4>Collaboration</h4>
                                    <p class="text-muted">We work together with our clients to achieve shared success.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def team_preview(config: PageConfig) -> str:
        """Preview of team members with link to full team page."""
        return '''
                <!-- Team Preview Section -->
                <section class="s_company_team pt64 pb64">
                    <div class="container">
                        <h2 class="text-center mb-5">Meet Our Leadership</h2>
                        <div class="row justify-content-center">
                            <div class="col-lg-3 col-md-6 mb-4">
                                <div class="card border-0 text-center shadow-sm">
                                    <div class="card-body py-4">
                                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                                             style="width: 100px; height: 100px; font-size: 2rem;">
                                            <i class="fa fa-user"/>
                                        </div>
                                        <h5 class="card-title mb-1">Jane Doe</h5>
                                        <p class="text-muted small">CEO &amp; Founder</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-3 col-md-6 mb-4">
                                <div class="card border-0 text-center shadow-sm">
                                    <div class="card-body py-4">
                                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                                             style="width: 100px; height: 100px; font-size: 2rem;">
                                            <i class="fa fa-user"/>
                                        </div>
                                        <h5 class="card-title mb-1">John Smith</h5>
                                        <p class="text-muted small">CTO</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-3 col-md-6 mb-4">
                                <div class="card border-0 text-center shadow-sm">
                                    <div class="card-body py-4">
                                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                                             style="width: 100px; height: 100px; font-size: 2rem;">
                                            <i class="fa fa-user"/>
                                        </div>
                                        <h5 class="card-title mb-1">Alice Johnson</h5>
                                        <p class="text-muted small">COO</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="text-center mt-4">
                            <a href="/team" class="btn btn-outline-primary">View Full Team</a>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def team_intro(config: PageConfig) -> str:
        """Team page introduction."""
        return '''
                <!-- Team Introduction -->
                <section class="s_text_block pt64 pb32">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-8 mx-auto text-center">
                                <p class="lead text-muted">
                                    Our success is built on the talent, dedication, and passion of our team members.
                                    Get to know the people who make it all happen.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def team_grid(config: PageConfig) -> str:
        """Full team member grid."""
        return '''
                <!-- Team Grid -->
                <section class="s_company_team pb64">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-3 col-md-6 mb-4">
                                <div class="card border-0 text-center h-100">
                                    <div class="card-body">
                                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                                             style="width: 120px; height: 120px; font-size: 2.5rem;">
                                            <i class="fa fa-user"/>
                                        </div>
                                        <h5 class="card-title mb-1">Jane Doe</h5>
                                        <p class="text-primary small mb-2">CEO &amp; Founder</p>
                                        <p class="text-muted small">Visionary leader with 20+ years of industry experience.</p>
                                        <div class="social-links mt-3">
                                            <a href="#" class="text-muted me-2"><i class="fa fa-linkedin"/></a>
                                            <a href="#" class="text-muted"><i class="fa fa-twitter"/></a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-3 col-md-6 mb-4">
                                <div class="card border-0 text-center h-100">
                                    <div class="card-body">
                                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                                             style="width: 120px; height: 120px; font-size: 2.5rem;">
                                            <i class="fa fa-user"/>
                                        </div>
                                        <h5 class="card-title mb-1">John Smith</h5>
                                        <p class="text-primary small mb-2">CTO</p>
                                        <p class="text-muted small">Tech innovator driving our engineering excellence.</p>
                                        <div class="social-links mt-3">
                                            <a href="#" class="text-muted me-2"><i class="fa fa-linkedin"/></a>
                                            <a href="#" class="text-muted"><i class="fa fa-github"/></a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-3 col-md-6 mb-4">
                                <div class="card border-0 text-center h-100">
                                    <div class="card-body">
                                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                                             style="width: 120px; height: 120px; font-size: 2.5rem;">
                                            <i class="fa fa-user"/>
                                        </div>
                                        <h5 class="card-title mb-1">Alice Johnson</h5>
                                        <p class="text-primary small mb-2">COO</p>
                                        <p class="text-muted small">Operations expert ensuring seamless delivery.</p>
                                        <div class="social-links mt-3">
                                            <a href="#" class="text-muted me-2"><i class="fa fa-linkedin"/></a>
                                            <a href="#" class="text-muted"><i class="fa fa-twitter"/></a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-3 col-md-6 mb-4">
                                <div class="card border-0 text-center h-100">
                                    <div class="card-body">
                                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                                             style="width: 120px; height: 120px; font-size: 2.5rem;">
                                            <i class="fa fa-user"/>
                                        </div>
                                        <h5 class="card-title mb-1">Bob Williams</h5>
                                        <p class="text-primary small mb-2">Head of Design</p>
                                        <p class="text-muted small">Creative director crafting beautiful experiences.</p>
                                        <div class="social-links mt-3">
                                            <a href="#" class="text-muted me-2"><i class="fa fa-linkedin"/></a>
                                            <a href="#" class="text-muted"><i class="fa fa-dribbble"/></a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def contact_info(config: PageConfig) -> str:
        """Contact information cards."""
        return '''
                <!-- Contact Information -->
                <section class="s_text_block pt64 pb32">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-4 mb-4">
                                <div class="card border-0 shadow-sm h-100">
                                    <div class="card-body text-center p-4">
                                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                                             style="width: 60px; height: 60px;">
                                            <i class="fa fa-map-marker fa-lg"/>
                                        </div>
                                        <h5>Visit Us</h5>
                                        <p class="text-muted mb-0">
                                            123 Business Street<br/>
                                            Suite 100<br/>
                                            City, State 12345
                                        </p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 mb-4">
                                <div class="card border-0 shadow-sm h-100">
                                    <div class="card-body text-center p-4">
                                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                                             style="width: 60px; height: 60px;">
                                            <i class="fa fa-phone fa-lg"/>
                                        </div>
                                        <h5>Call Us</h5>
                                        <p class="text-muted mb-0">
                                            <a href="tel:+1234567890" class="text-decoration-none">+1 (234) 567-890</a><br/>
                                            Mon-Fri: 9am - 6pm
                                        </p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 mb-4">
                                <div class="card border-0 shadow-sm h-100">
                                    <div class="card-body text-center p-4">
                                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                                             style="width: 60px; height: 60px;">
                                            <i class="fa fa-envelope fa-lg"/>
                                        </div>
                                        <h5>Email Us</h5>
                                        <p class="text-muted mb-0">
                                            <a href="mailto:info@company.com" class="text-decoration-none">info@company.com</a><br/>
                                            <a href="mailto:support@company.com" class="text-decoration-none">support@company.com</a>
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def contact_form(config: PageConfig) -> str:
        """Contact form section."""
        return '''
                <!-- Contact Form -->
                <section class="s_website_form pt32 pb64">
                    <div class="container">
                        <div class="row justify-content-center">
                            <div class="col-lg-8">
                                <div class="card border-0 shadow">
                                    <div class="card-body p-5">
                                        <h3 class="text-center mb-4">Send Us a Message</h3>
                                        <form action="/website/form/" method="post" class="s_website_form_form"
                                              data-model_name="mail.mail" data-success_page="/contactus-thank-you">
                                            <div class="row">
                                                <div class="col-md-6 mb-3">
                                                    <label class="form-label" for="contact_name">Name *</label>
                                                    <input type="text" class="form-control" id="contact_name"
                                                           name="name" required="required"/>
                                                </div>
                                                <div class="col-md-6 mb-3">
                                                    <label class="form-label" for="contact_email">Email *</label>
                                                    <input type="email" class="form-control" id="contact_email"
                                                           name="email_from" required="required"/>
                                                </div>
                                            </div>
                                            <div class="mb-3">
                                                <label class="form-label" for="contact_phone">Phone</label>
                                                <input type="tel" class="form-control" id="contact_phone" name="phone"/>
                                            </div>
                                            <div class="mb-3">
                                                <label class="form-label" for="contact_subject">Subject *</label>
                                                <input type="text" class="form-control" id="contact_subject"
                                                       name="subject" required="required"/>
                                            </div>
                                            <div class="mb-4">
                                                <label class="form-label" for="contact_message">Message *</label>
                                                <textarea class="form-control" id="contact_message" name="body_html"
                                                          rows="5" required="required"/>
                                            </div>
                                            <div class="text-center">
                                                <button type="submit" class="btn btn-primary btn-lg px-5">
                                                    Send Message
                                                </button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def map(config: PageConfig) -> str:
        """Map placeholder section."""
        return '''
                <!-- Map Section -->
                <section class="s_google_map">
                    <div class="container-fluid px-0">
                        <div class="ratio ratio-21x9" style="max-height: 400px;">
                            <div class="bg-secondary d-flex align-items-center justify-content-center">
                                <div class="text-center text-white">
                                    <i class="fa fa-map-marker fa-3x mb-3"/>
                                    <p class="mb-0">Map integration available through Odoo Website Builder</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def services_intro(config: PageConfig) -> str:
        """Services introduction."""
        return '''
                <!-- Services Introduction -->
                <section class="s_text_block pt64 pb32">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-8 mx-auto text-center">
                                <p class="lead text-muted">
                                    We offer a comprehensive range of services designed to help your business
                                    thrive in today's competitive landscape.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def services_grid(config: PageConfig) -> str:
        """Services grid with cards."""
        return '''
                <!-- Services Grid -->
                <section class="s_features pb64">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-4 mb-4">
                                <div class="card h-100 border-0 shadow-sm">
                                    <div class="card-body p-4">
                                        <div class="feature-icon bg-primary bg-gradient text-white rounded mb-3"
                                             style="width: 56px; height: 56px; display: flex; align-items: center; justify-content: center;">
                                            <i class="fa fa-cogs fa-lg"/>
                                        </div>
                                        <h4>Consulting</h4>
                                        <p class="text-muted">Strategic guidance to optimize your operations and achieve your business goals.</p>
                                        <a href="#" class="btn btn-outline-primary btn-sm">Learn More</a>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 mb-4">
                                <div class="card h-100 border-0 shadow-sm">
                                    <div class="card-body p-4">
                                        <div class="feature-icon bg-primary bg-gradient text-white rounded mb-3"
                                             style="width: 56px; height: 56px; display: flex; align-items: center; justify-content: center;">
                                            <i class="fa fa-code fa-lg"/>
                                        </div>
                                        <h4>Development</h4>
                                        <p class="text-muted">Custom software solutions built with cutting-edge technology and best practices.</p>
                                        <a href="#" class="btn btn-outline-primary btn-sm">Learn More</a>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 mb-4">
                                <div class="card h-100 border-0 shadow-sm">
                                    <div class="card-body p-4">
                                        <div class="feature-icon bg-primary bg-gradient text-white rounded mb-3"
                                             style="width: 56px; height: 56px; display: flex; align-items: center; justify-content: center;">
                                            <i class="fa fa-rocket fa-lg"/>
                                        </div>
                                        <h4>Growth</h4>
                                        <p class="text-muted">Scalable solutions that grow with your business and adapt to changing needs.</p>
                                        <a href="#" class="btn btn-outline-primary btn-sm">Learn More</a>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 mb-4">
                                <div class="card h-100 border-0 shadow-sm">
                                    <div class="card-body p-4">
                                        <div class="feature-icon bg-primary bg-gradient text-white rounded mb-3"
                                             style="width: 56px; height: 56px; display: flex; align-items: center; justify-content: center;">
                                            <i class="fa fa-shield fa-lg"/>
                                        </div>
                                        <h4>Security</h4>
                                        <p class="text-muted">Comprehensive security solutions to protect your data and infrastructure.</p>
                                        <a href="#" class="btn btn-outline-primary btn-sm">Learn More</a>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 mb-4">
                                <div class="card h-100 border-0 shadow-sm">
                                    <div class="card-body p-4">
                                        <div class="feature-icon bg-primary bg-gradient text-white rounded mb-3"
                                             style="width: 56px; height: 56px; display: flex; align-items: center; justify-content: center;">
                                            <i class="fa fa-cloud fa-lg"/>
                                        </div>
                                        <h4>Cloud</h4>
                                        <p class="text-muted">Modern cloud infrastructure and migration services for maximum efficiency.</p>
                                        <a href="#" class="btn btn-outline-primary btn-sm">Learn More</a>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 mb-4">
                                <div class="card h-100 border-0 shadow-sm">
                                    <div class="card-body p-4">
                                        <div class="feature-icon bg-primary bg-gradient text-white rounded mb-3"
                                             style="width: 56px; height: 56px; display: flex; align-items: center; justify-content: center;">
                                            <i class="fa fa-headphones fa-lg"/>
                                        </div>
                                        <h4>Support</h4>
                                        <p class="text-muted">24/7 dedicated support to keep your systems running smoothly.</p>
                                        <a href="#" class="btn btn-outline-primary btn-sm">Learn More</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def process(config: PageConfig) -> str:
        """Process/workflow section."""
        return '''
                <!-- Our Process -->
                <section class="s_process pt64 pb64 o_cc o_cc5">
                    <div class="container">
                        <h2 class="text-center mb-5">Our Process</h2>
                        <div class="row">
                            <div class="col-lg-3 text-center mb-4">
                                <div class="process-step">
                                    <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                                         style="width: 80px; height: 80px; font-size: 1.5rem; font-weight: bold;">1</div>
                                    <h5>Discovery</h5>
                                    <p class="text-muted small">We learn about your business, goals, and challenges.</p>
                                </div>
                            </div>
                            <div class="col-lg-3 text-center mb-4">
                                <div class="process-step">
                                    <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                                         style="width: 80px; height: 80px; font-size: 1.5rem; font-weight: bold;">2</div>
                                    <h5>Strategy</h5>
                                    <p class="text-muted small">We develop a customized plan tailored to your needs.</p>
                                </div>
                            </div>
                            <div class="col-lg-3 text-center mb-4">
                                <div class="process-step">
                                    <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                                         style="width: 80px; height: 80px; font-size: 1.5rem; font-weight: bold;">3</div>
                                    <h5>Execution</h5>
                                    <p class="text-muted small">We implement solutions with precision and care.</p>
                                </div>
                            </div>
                            <div class="col-lg-3 text-center mb-4">
                                <div class="process-step">
                                    <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center mx-auto mb-3"
                                         style="width: 80px; height: 80px; font-size: 1.5rem; font-weight: bold;">4</div>
                                    <h5>Support</h5>
                                    <p class="text-muted small">We provide ongoing support and optimization.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def faq_intro(config: PageConfig) -> str:
        """FAQ introduction."""
        return '''
                <!-- FAQ Introduction -->
                <section class="s_text_block pt64 pb32">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-8 mx-auto text-center">
                                <p class="lead text-muted">
                                    Find answers to the most commonly asked questions about our products and services.
                                    Can't find what you're looking for? Contact us directly.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def faq_accordion(config: PageConfig) -> str:
        """FAQ accordion section."""
        return '''
                <!-- FAQ Accordion -->
                <section class="s_faq_collapse pb64">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-8 mx-auto">
                                <div class="accordion" id="faqAccordion">
                                    <div class="accordion-item">
                                        <h2 class="accordion-header" id="faq1">
                                            <button class="accordion-button" type="button"
                                                    data-bs-toggle="collapse" data-bs-target="#collapse1"
                                                    aria-expanded="true" aria-controls="collapse1">
                                                What services do you offer?
                                            </button>
                                        </h2>
                                        <div id="collapse1" class="accordion-collapse collapse show"
                                             aria-labelledby="faq1" data-bs-parent="#faqAccordion">
                                            <div class="accordion-body">
                                                We offer a comprehensive range of services including consulting, development,
                                                cloud solutions, security, and ongoing support. Each service is tailored to
                                                meet your specific business needs.
                                            </div>
                                        </div>
                                    </div>
                                    <div class="accordion-item">
                                        <h2 class="accordion-header" id="faq2">
                                            <button class="accordion-button collapsed" type="button"
                                                    data-bs-toggle="collapse" data-bs-target="#collapse2"
                                                    aria-expanded="false" aria-controls="collapse2">
                                                How long does a typical project take?
                                            </button>
                                        </h2>
                                        <div id="collapse2" class="accordion-collapse collapse"
                                             aria-labelledby="faq2" data-bs-parent="#faqAccordion">
                                            <div class="accordion-body">
                                                Project timelines vary based on scope and complexity. Small projects may take
                                                a few weeks, while larger implementations can span several months. We'll provide
                                                a detailed timeline during our initial consultation.
                                            </div>
                                        </div>
                                    </div>
                                    <div class="accordion-item">
                                        <h2 class="accordion-header" id="faq3">
                                            <button class="accordion-button collapsed" type="button"
                                                    data-bs-toggle="collapse" data-bs-target="#collapse3"
                                                    aria-expanded="false" aria-controls="collapse3">
                                                Do you offer ongoing support?
                                            </button>
                                        </h2>
                                        <div id="collapse3" class="accordion-collapse collapse"
                                             aria-labelledby="faq3" data-bs-parent="#faqAccordion">
                                            <div class="accordion-body">
                                                Yes! We offer various support packages to ensure your systems continue running
                                                smoothly. From basic maintenance to 24/7 dedicated support, we have options
                                                to fit every need.
                                            </div>
                                        </div>
                                    </div>
                                    <div class="accordion-item">
                                        <h2 class="accordion-header" id="faq4">
                                            <button class="accordion-button collapsed" type="button"
                                                    data-bs-toggle="collapse" data-bs-target="#collapse4"
                                                    aria-expanded="false" aria-controls="collapse4">
                                                How do I get started?
                                            </button>
                                        </h2>
                                        <div id="collapse4" class="accordion-collapse collapse"
                                             aria-labelledby="faq4" data-bs-parent="#faqAccordion">
                                            <div class="accordion-body">
                                                Getting started is easy! Simply contact us through our contact form or give us
                                                a call. We'll schedule a free consultation to discuss your needs and how we
                                                can help.
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def faq_preview(config: PageConfig) -> str:
        """FAQ preview for pricing page."""
        return '''
                <!-- FAQ Preview -->
                <section class="s_faq_collapse pt64 pb64 o_cc o_cc5">
                    <div class="container">
                        <h2 class="text-center mb-5">Common Questions</h2>
                        <div class="row">
                            <div class="col-lg-8 mx-auto">
                                <div class="accordion" id="pricingFaq">
                                    <div class="accordion-item">
                                        <h2 class="accordion-header">
                                            <button class="accordion-button" type="button"
                                                    data-bs-toggle="collapse" data-bs-target="#pFaq1">
                                                Can I change plans later?
                                            </button>
                                        </h2>
                                        <div id="pFaq1" class="accordion-collapse collapse show" data-bs-parent="#pricingFaq">
                                            <div class="accordion-body">
                                                Yes! You can upgrade or downgrade your plan at any time. Changes take effect
                                                at the start of your next billing cycle.
                                            </div>
                                        </div>
                                    </div>
                                    <div class="accordion-item">
                                        <h2 class="accordion-header">
                                            <button class="accordion-button collapsed" type="button"
                                                    data-bs-toggle="collapse" data-bs-target="#pFaq2">
                                                Is there a free trial?
                                            </button>
                                        </h2>
                                        <div id="pFaq2" class="accordion-collapse collapse" data-bs-parent="#pricingFaq">
                                            <div class="accordion-body">
                                                We offer a 14-day free trial on all plans. No credit card required to start.
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="text-center mt-4">
                                    <a href="/faq" class="btn btn-outline-primary">View All FAQs</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def pricing_intro(config: PageConfig) -> str:
        """Pricing introduction."""
        return '''
                <!-- Pricing Introduction -->
                <section class="s_text_block pt64 pb32">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-8 mx-auto text-center">
                                <p class="lead text-muted">
                                    Choose the plan that best fits your needs. All plans include our core features
                                    with no hidden fees.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def pricing_table(config: PageConfig) -> str:
        """Pricing table section."""
        return '''
                <!-- Pricing Table -->
                <section class="s_comparisons pb64">
                    <div class="container">
                        <div class="row justify-content-center">
                            <div class="col-lg-4 col-md-6 mb-4">
                                <div class="card h-100 text-center">
                                    <div class="card-header py-3 bg-light">
                                        <h4 class="my-0 fw-normal">Starter</h4>
                                    </div>
                                    <div class="card-body d-flex flex-column">
                                        <h1 class="card-title pricing-card-title mb-4">
                                            $19<small class="text-muted fw-light">/mo</small>
                                        </h1>
                                        <ul class="list-unstyled mt-3 mb-4 flex-grow-1">
                                            <li class="mb-2"><i class="fa fa-check text-success me-2"/>5 users included</li>
                                            <li class="mb-2"><i class="fa fa-check text-success me-2"/>10 GB storage</li>
                                            <li class="mb-2"><i class="fa fa-check text-success me-2"/>Email support</li>
                                            <li class="mb-2 text-muted"><i class="fa fa-times text-muted me-2"/>Phone support</li>
                                            <li class="mb-2 text-muted"><i class="fa fa-times text-muted me-2"/>Priority access</li>
                                        </ul>
                                        <a href="/contact" class="btn btn-lg btn-outline-primary w-100">Get Started</a>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 col-md-6 mb-4">
                                <div class="card h-100 text-center border-primary">
                                    <div class="card-header py-3 bg-primary text-white">
                                        <h4 class="my-0 fw-normal">Professional</h4>
                                        <span class="badge bg-light text-primary">Most Popular</span>
                                    </div>
                                    <div class="card-body d-flex flex-column">
                                        <h1 class="card-title pricing-card-title mb-4">
                                            $49<small class="text-muted fw-light">/mo</small>
                                        </h1>
                                        <ul class="list-unstyled mt-3 mb-4 flex-grow-1">
                                            <li class="mb-2"><i class="fa fa-check text-success me-2"/>25 users included</li>
                                            <li class="mb-2"><i class="fa fa-check text-success me-2"/>50 GB storage</li>
                                            <li class="mb-2"><i class="fa fa-check text-success me-2"/>Priority email support</li>
                                            <li class="mb-2"><i class="fa fa-check text-success me-2"/>Phone support</li>
                                            <li class="mb-2 text-muted"><i class="fa fa-times text-muted me-2"/>Priority access</li>
                                        </ul>
                                        <a href="/contact" class="btn btn-lg btn-primary w-100">Get Started</a>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 col-md-6 mb-4">
                                <div class="card h-100 text-center">
                                    <div class="card-header py-3 bg-light">
                                        <h4 class="my-0 fw-normal">Enterprise</h4>
                                    </div>
                                    <div class="card-body d-flex flex-column">
                                        <h1 class="card-title pricing-card-title mb-4">
                                            $99<small class="text-muted fw-light">/mo</small>
                                        </h1>
                                        <ul class="list-unstyled mt-3 mb-4 flex-grow-1">
                                            <li class="mb-2"><i class="fa fa-check text-success me-2"/>Unlimited users</li>
                                            <li class="mb-2"><i class="fa fa-check text-success me-2"/>200 GB storage</li>
                                            <li class="mb-2"><i class="fa fa-check text-success me-2"/>24/7 support</li>
                                            <li class="mb-2"><i class="fa fa-check text-success me-2"/>Dedicated account manager</li>
                                            <li class="mb-2"><i class="fa fa-check text-success me-2"/>Priority access</li>
                                        </ul>
                                        <a href="/contact" class="btn btn-lg btn-outline-primary w-100">Contact Sales</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def pricing_preview(config: PageConfig) -> str:
        """Pricing preview for landing pages."""
        return '''
                <!-- Pricing Preview -->
                <section class="s_comparisons pt64 pb64">
                    <div class="container">
                        <h2 class="text-center mb-2">Simple Pricing</h2>
                        <p class="text-center text-muted mb-5">No hidden fees. Cancel anytime.</p>
                        <div class="row justify-content-center">
                            <div class="col-lg-4 col-md-6 mb-4">
                                <div class="card h-100 text-center border-primary">
                                    <div class="card-header py-3 bg-primary text-white">
                                        <h4 class="my-0">Starting at</h4>
                                    </div>
                                    <div class="card-body">
                                        <h1 class="card-title pricing-card-title">
                                            $19<small class="text-muted">/mo</small>
                                        </h1>
                                        <p class="text-muted">Everything you need to get started</p>
                                        <a href="/pricing" class="btn btn-primary">View All Plans</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def portfolio_intro(config: PageConfig) -> str:
        """Portfolio introduction."""
        return '''
                <!-- Portfolio Introduction -->
                <section class="s_text_block pt64 pb32">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-8 mx-auto text-center">
                                <p class="lead text-muted">
                                    Explore our portfolio of successful projects. Each represents our commitment
                                    to quality and innovation.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def portfolio_grid(config: PageConfig) -> str:
        """Portfolio project grid."""
        return '''
                <!-- Portfolio Grid -->
                <section class="s_image_gallery pb64">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-4 col-md-6 mb-4">
                                <div class="card border-0 shadow-sm h-100">
                                    <div class="card-img-top bg-secondary d-flex align-items-center justify-content-center"
                                         style="height: 200px;">
                                        <i class="fa fa-image fa-3x text-white"/>
                                    </div>
                                    <div class="card-body">
                                        <span class="badge bg-primary mb-2">Web Design</span>
                                        <h5 class="card-title">E-Commerce Platform</h5>
                                        <p class="card-text text-muted small">Complete redesign of online shopping experience.</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 col-md-6 mb-4">
                                <div class="card border-0 shadow-sm h-100">
                                    <div class="card-img-top bg-secondary d-flex align-items-center justify-content-center"
                                         style="height: 200px;">
                                        <i class="fa fa-image fa-3x text-white"/>
                                    </div>
                                    <div class="card-body">
                                        <span class="badge bg-primary mb-2">Mobile App</span>
                                        <h5 class="card-title">Fitness Tracker</h5>
                                        <p class="card-text text-muted small">Cross-platform health and fitness application.</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 col-md-6 mb-4">
                                <div class="card border-0 shadow-sm h-100">
                                    <div class="card-img-top bg-secondary d-flex align-items-center justify-content-center"
                                         style="height: 200px;">
                                        <i class="fa fa-image fa-3x text-white"/>
                                    </div>
                                    <div class="card-body">
                                        <span class="badge bg-primary mb-2">Branding</span>
                                        <h5 class="card-title">Startup Identity</h5>
                                        <p class="card-text text-muted small">Complete brand identity for tech startup.</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 col-md-6 mb-4">
                                <div class="card border-0 shadow-sm h-100">
                                    <div class="card-img-top bg-secondary d-flex align-items-center justify-content-center"
                                         style="height: 200px;">
                                        <i class="fa fa-image fa-3x text-white"/>
                                    </div>
                                    <div class="card-body">
                                        <span class="badge bg-primary mb-2">Enterprise</span>
                                        <h5 class="card-title">CRM System</h5>
                                        <p class="card-text text-muted small">Custom CRM solution for sales team.</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 col-md-6 mb-4">
                                <div class="card border-0 shadow-sm h-100">
                                    <div class="card-img-top bg-secondary d-flex align-items-center justify-content-center"
                                         style="height: 200px;">
                                        <i class="fa fa-image fa-3x text-white"/>
                                    </div>
                                    <div class="card-body">
                                        <span class="badge bg-primary mb-2">Cloud</span>
                                        <h5 class="card-title">Infrastructure Migration</h5>
                                        <p class="card-text text-muted small">Legacy system cloud migration project.</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 col-md-6 mb-4">
                                <div class="card border-0 shadow-sm h-100">
                                    <div class="card-img-top bg-secondary d-flex align-items-center justify-content-center"
                                         style="height: 200px;">
                                        <i class="fa fa-image fa-3x text-white"/>
                                    </div>
                                    <div class="card-body">
                                        <span class="badge bg-primary mb-2">Security</span>
                                        <h5 class="card-title">Security Audit</h5>
                                        <p class="card-text text-muted small">Comprehensive security assessment and remediation.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def features(config: PageConfig) -> str:
        """Features section for landing pages."""
        return '''
                <!-- Features Section -->
                <section class="s_features pt80 pb80">
                    <div class="container">
                        <h2 class="text-center mb-2">Why Choose Us</h2>
                        <p class="text-center text-muted mb-5">Everything you need to succeed</p>
                        <div class="row">
                            <div class="col-lg-4 mb-4">
                                <div class="d-flex">
                                    <div class="flex-shrink-0">
                                        <div class="bg-primary text-white rounded p-3">
                                            <i class="fa fa-bolt fa-lg"/>
                                        </div>
                                    </div>
                                    <div class="flex-grow-1 ms-3">
                                        <h5>Lightning Fast</h5>
                                        <p class="text-muted">Optimized performance ensures your site loads in milliseconds.</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 mb-4">
                                <div class="d-flex">
                                    <div class="flex-shrink-0">
                                        <div class="bg-primary text-white rounded p-3">
                                            <i class="fa fa-lock fa-lg"/>
                                        </div>
                                    </div>
                                    <div class="flex-grow-1 ms-3">
                                        <h5>Secure by Default</h5>
                                        <p class="text-muted">Enterprise-grade security protects your data 24/7.</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 mb-4">
                                <div class="d-flex">
                                    <div class="flex-shrink-0">
                                        <div class="bg-primary text-white rounded p-3">
                                            <i class="fa fa-expand fa-lg"/>
                                        </div>
                                    </div>
                                    <div class="flex-grow-1 ms-3">
                                        <h5>Scalable</h5>
                                        <p class="text-muted">Grows with your business from startup to enterprise.</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 mb-4">
                                <div class="d-flex">
                                    <div class="flex-shrink-0">
                                        <div class="bg-primary text-white rounded p-3">
                                            <i class="fa fa-mobile fa-lg"/>
                                        </div>
                                    </div>
                                    <div class="flex-grow-1 ms-3">
                                        <h5>Mobile First</h5>
                                        <p class="text-muted">Responsive design ensures perfect experience on any device.</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 mb-4">
                                <div class="d-flex">
                                    <div class="flex-shrink-0">
                                        <div class="bg-primary text-white rounded p-3">
                                            <i class="fa fa-cogs fa-lg"/>
                                        </div>
                                    </div>
                                    <div class="flex-grow-1 ms-3">
                                        <h5>Easy Integration</h5>
                                        <p class="text-muted">Connects seamlessly with your existing tools and workflows.</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 mb-4">
                                <div class="d-flex">
                                    <div class="flex-shrink-0">
                                        <div class="bg-primary text-white rounded p-3">
                                            <i class="fa fa-life-ring fa-lg"/>
                                        </div>
                                    </div>
                                    <div class="flex-grow-1 ms-3">
                                        <h5>24/7 Support</h5>
                                        <p class="text-muted">Our team is always here to help you succeed.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def benefits(config: PageConfig) -> str:
        """Benefits section for landing pages."""
        return '''
                <!-- Benefits Section -->
                <section class="s_text_image pt80 pb80 o_cc o_cc5">
                    <div class="container">
                        <div class="row align-items-center">
                            <div class="col-lg-6 mb-4 mb-lg-0">
                                <div class="bg-secondary rounded d-flex align-items-center justify-content-center"
                                     style="height: 400px;">
                                    <i class="fa fa-image fa-5x text-white"/>
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <h2 class="mb-4">Transform Your Business</h2>
                                <div class="mb-4">
                                    <div class="d-flex mb-3">
                                        <i class="fa fa-check-circle text-success fa-lg me-3 mt-1"/>
                                        <div>
                                            <h6 class="mb-1">Increase Productivity</h6>
                                            <p class="text-muted mb-0">Automate repetitive tasks and focus on what matters.</p>
                                        </div>
                                    </div>
                                    <div class="d-flex mb-3">
                                        <i class="fa fa-check-circle text-success fa-lg me-3 mt-1"/>
                                        <div>
                                            <h6 class="mb-1">Reduce Costs</h6>
                                            <p class="text-muted mb-0">Eliminate inefficiencies and optimize operations.</p>
                                        </div>
                                    </div>
                                    <div class="d-flex mb-3">
                                        <i class="fa fa-check-circle text-success fa-lg me-3 mt-1"/>
                                        <div>
                                            <h6 class="mb-1">Improve Customer Experience</h6>
                                            <p class="text-muted mb-0">Deliver exceptional service at every touchpoint.</p>
                                        </div>
                                    </div>
                                </div>
                                <a href="/contact" class="btn btn-primary">Start Today</a>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def testimonials(config: PageConfig) -> str:
        """Testimonials section."""
        return '''
                <!-- Testimonials Section -->
                <section class="s_quotes pt80 pb80">
                    <div class="container">
                        <h2 class="text-center mb-5">What Our Clients Say</h2>
                        <div class="row">
                            <div class="col-lg-4 mb-4">
                                <div class="card border-0 shadow-sm h-100">
                                    <div class="card-body p-4">
                                        <div class="d-flex mb-3">
                                            <i class="fa fa-star text-warning"/>
                                            <i class="fa fa-star text-warning"/>
                                            <i class="fa fa-star text-warning"/>
                                            <i class="fa fa-star text-warning"/>
                                            <i class="fa fa-star text-warning"/>
                                        </div>
                                        <p class="mb-4">"Working with this team has transformed our business. The results exceeded our expectations."</p>
                                        <div class="d-flex align-items-center">
                                            <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center me-3"
                                                 style="width: 50px; height: 50px;">
                                                <i class="fa fa-user"/>
                                            </div>
                                            <div>
                                                <h6 class="mb-0">Sarah Johnson</h6>
                                                <small class="text-muted">CEO, TechCorp</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 mb-4">
                                <div class="card border-0 shadow-sm h-100">
                                    <div class="card-body p-4">
                                        <div class="d-flex mb-3">
                                            <i class="fa fa-star text-warning"/>
                                            <i class="fa fa-star text-warning"/>
                                            <i class="fa fa-star text-warning"/>
                                            <i class="fa fa-star text-warning"/>
                                            <i class="fa fa-star text-warning"/>
                                        </div>
                                        <p class="mb-4">"The support team is incredible. They're always available and go above and beyond to help."</p>
                                        <div class="d-flex align-items-center">
                                            <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center me-3"
                                                 style="width: 50px; height: 50px;">
                                                <i class="fa fa-user"/>
                                            </div>
                                            <div>
                                                <h6 class="mb-0">Michael Chen</h6>
                                                <small class="text-muted">CTO, StartupXYZ</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4 mb-4">
                                <div class="card border-0 shadow-sm h-100">
                                    <div class="card-body p-4">
                                        <div class="d-flex mb-3">
                                            <i class="fa fa-star text-warning"/>
                                            <i class="fa fa-star text-warning"/>
                                            <i class="fa fa-star text-warning"/>
                                            <i class="fa fa-star text-warning"/>
                                            <i class="fa fa-star text-warning"/>
                                        </div>
                                        <p class="mb-4">"We've seen a 40% increase in efficiency since implementing their solutions. Highly recommend!"</p>
                                        <div class="d-flex align-items-center">
                                            <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center me-3"
                                                 style="width: 50px; height: 50px;">
                                                <i class="fa fa-user"/>
                                            </div>
                                            <div>
                                                <h6 class="mb-0">Emily Davis</h6>
                                                <small class="text-muted">Director, RetailCo</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>'''

    @staticmethod
    def cta(config: PageConfig) -> str:
        """Primary call-to-action section."""
        return '''
                <!-- Call to Action -->
                <section class="s_call_to_action pt80 pb80 o_cc o_cc1">
                    <div class="container text-center">
                        <h2 class="text-white mb-3">Ready to Get Started?</h2>
                        <p class="lead text-white-75 mb-4">
                            Join thousands of satisfied customers and transform your business today.
                        </p>
                        <a href="/contact" class="btn btn-lg btn-secondary">Contact Us</a>
                    </div>
                </section>'''

    @staticmethod
    def contact_cta(config: PageConfig) -> str:
        """Contact-focused CTA for FAQ page."""
        return '''
                <!-- Contact CTA -->
                <section class="s_call_to_action pt64 pb64 o_cc o_cc1">
                    <div class="container text-center">
                        <h2 class="text-white mb-3">Still Have Questions?</h2>
                        <p class="lead text-white-75 mb-4">
                            Our team is here to help. Reach out and we'll get back to you promptly.
                        </p>
                        <a href="/contact" class="btn btn-lg btn-secondary">Contact Support</a>
                    </div>
                </section>'''

    def generate_section(self, section_name: str, config: PageConfig) -> str:
        """Generate a section by name."""
        method = getattr(self, section_name, None)
        if method is not None and callable(method):
            result = method(config)
            if isinstance(result, str):
                return result
            return str(result)
        return f'\n                <!-- Section "{section_name}" not found -->'


# ============================================================================
# XML Generators
# ============================================================================

class PageXMLGenerator:
    """Generates Odoo page XML files."""

    def __init__(self) -> None:
        self.section_gen = SectionGenerator()

    def generate_template(self, config: PageConfig) -> str:
        """Generate QWeb page template."""
        sections = '\n'.join(
            self.section_gen.generate_section(section, config)
            for section in config.sections
        )

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="{config.template_id}" name="{xml_escape(config.title)}">
        <t t-call="website.layout">
            <t t-set="pageName" t-value="'{config.page_type}'"/>
            <div id="wrap" class="oe_structure oe_empty">
{sections}
            </div>
        </t>
    </template>
</odoo>
'''

    def generate_page_record(self, config: PageConfig) -> str:
        """Generate website.page record XML."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data noupdate="0">
        <!-- {config.title} Page -->
        <record id="{config.page_record_id}" model="website.page">
            <field name="url">{config.url}</field>
            <field name="name">{xml_escape(config.title)}</field>
            <field name="website_published">True</field>
            <field name="website_indexed">True</field>
            <field name="view_id" ref="{config.template_id}"/>
        </record>
    </data>
</odoo>
'''

    def generate_menu_record(self, config: PageConfig) -> str:
        """Generate website.menu record XML."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data noupdate="0">
        <record id="{config.menu_record_id}" model="website.menu">
            <field name="name">{xml_escape(config.menu_label)}</field>
            <field name="url">{config.url}</field>
            <field name="page_id" ref="{config.page_record_id}"/>
            <field name="parent_id" ref="website.main_menu"/>
            <field name="sequence">{config.sequence}</field>
        </record>
    </data>
</odoo>
'''

    def generate_seo_template(self, config: PageConfig) -> str:
        """Generate SEO metadata template."""
        full_title = f'{config.title} | {config.company_name}'

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="{config.seo_template_id}" inherit_id="website.layout"
              name="{xml_escape(config.title)} SEO" active="True"
              customize_show="False" primary="False">
        <xpath expr="//head/title" position="replace">
            <t t-if="pageName == '{config.page_type}'">
                <title>{xml_escape(full_title)}</title>
            </t>
            <t t-else="">
                <title t-esc="website.name"/>
            </t>
        </xpath>
        <xpath expr="//head" position="inside">
            <t t-if="pageName == '{config.page_type}'">
                <!-- Meta Description -->
                <meta name="description" content="{xml_escape(config.description)}"/>

                <!-- Open Graph -->
                <meta property="og:title" content="{xml_escape(full_title)}"/>
                <meta property="og:description" content="{xml_escape(config.description)}"/>
                <meta property="og:type" content="website"/>
                <meta property="og:url" t-attf-content="{{{{ website.domain }}}}{config.url}"/>

                <!-- Twitter Card -->
                <meta name="twitter:card" content="summary"/>
                <meta name="twitter:title" content="{xml_escape(full_title)}"/>
                <meta name="twitter:description" content="{xml_escape(config.description)}"/>
            </t>
        </xpath>
    </template>
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


def generate_page(config: PageConfig, output_dir: Path, with_seo: bool = True) -> dict[str, Path]:
    """Generate all files for a page."""
    # Validate output directory
    cwd = Path.cwd()
    if not validate_output_path(output_dir, cwd):
        raise ValueError(f'Output directory must be within {cwd}')

    generator = PageXMLGenerator()
    files_created: dict[str, Path] = {}

    # Create directories
    views_dir = output_dir / 'views' / 'pages'
    data_dir = output_dir / 'data'

    views_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    # Generate template
    template_file = views_dir / f'page_{config.page_type}.xml'
    template_file.write_text(generator.generate_template(config))
    files_created['template'] = template_file

    # Generate page record
    page_file = data_dir / f'page_{config.page_type}.xml'
    page_file.write_text(generator.generate_page_record(config))
    files_created['page_record'] = page_file

    # Generate menu record
    menu_file = data_dir / f'menu_{config.page_type}.xml'
    menu_file.write_text(generator.generate_menu_record(config))
    files_created['menu_record'] = menu_file

    # Generate SEO template
    if with_seo:
        seo_file = views_dir / f'page_{config.page_type}_seo.xml'
        seo_file.write_text(generator.generate_seo_template(config))
        files_created['seo_template'] = seo_file

    return files_created


def generate_multiple_pages(
    page_types: list[str],
    module_name: str,
    output_dir: Path,
    with_seo: bool = True,
    company_name: str = 'Company Name'
) -> dict[str, dict[str, Path]]:
    """Generate multiple pages."""
    results: dict[str, dict[str, Path]] = {}

    for page_type in page_types:
        if page_type not in PAGE_COMPOSITIONS:
            print(f'Warning: Unknown page type "{page_type}", skipping')
            continue

        config = PageConfig(
            page_type=page_type,
            module_name=module_name,
            company_name=company_name,
        )

        try:
            files = generate_page(config, output_dir, with_seo)
            results[page_type] = files
            print(f'Generated {page_type} page: {len(files)} files')
        except Exception as e:
            print(f'Error generating {page_type} page: {e}')

    return results


# ============================================================================
# CLI Interface
# ============================================================================

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate Odoo website pages with QWeb templates',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s --type about --module theme_company
  %(prog)s --pages about,contact,services --module theme_company --with-seo
  %(prog)s --type landing --module theme_company --title "Welcome" --company "Acme Corp"
        ''',
    )

    parser.add_argument(
        '--type',
        choices=list(PAGE_COMPOSITIONS.keys()),
        help='Single page type to generate',
    )
    parser.add_argument(
        '--pages',
        help='Comma-separated list of page types to generate',
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
        help='Custom page title (for single page)',
    )
    parser.add_argument(
        '--description',
        help='Custom page description (for single page)',
    )
    parser.add_argument(
        '--company',
        default='Company Name',
        help='Company name for SEO metadata',
    )
    parser.add_argument(
        '--with-seo',
        action='store_true',
        default=True,
        help='Generate SEO metadata templates (default: True)',
    )
    parser.add_argument(
        '--no-seo',
        action='store_true',
        help='Skip SEO metadata generation',
    )
    parser.add_argument(
        '--list-types',
        action='store_true',
        help='List available page types and exit',
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON',
    )

    args = parser.parse_args()

    # List types
    if args.list_types:
        print('Available page types:')
        for page_type, sections in PAGE_COMPOSITIONS.items():
            defaults = PAGE_DEFAULTS.get(page_type, {})
            print(f'  {page_type}: {defaults.get("title", page_type.title())}')
            print(f'    Sections: {", ".join(sections)}')
        return 0

    # Validate arguments
    if not args.type and not args.pages:
        parser.error('Either --type or --pages is required')

    if not args.module:
        parser.error('--module is required when generating pages')

    with_seo = not args.no_seo

    # Generate pages
    if args.pages:
        page_types = [p.strip() for p in args.pages.split(',')]
        results = generate_multiple_pages(
            page_types,
            args.module,
            args.output,
            with_seo,
            args.company,
        )
    else:
        config = PageConfig(
            page_type=args.type,
            module_name=args.module,
            title=args.title or '',
            description=args.description or '',
            company_name=args.company,
        )
        try:
            files = generate_page(config, args.output, with_seo)
            results = {args.type: files}
        except Exception as e:
            print(f'Error: {e}', file=sys.stderr)
            return 1

    # Output results
    if args.json:
        json_results = {
            page_type: {k: str(v) for k, v in files.items()}
            for page_type, files in results.items()
        }
        print(json.dumps(json_results, indent=2))
    else:
        print(f'\nGenerated {len(results)} page(s) in {args.output}')
        for page_type, files in results.items():
            print(f'\n{page_type}:')
            for file_type, path in files.items():
                print(f'  {file_type}: {path}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
