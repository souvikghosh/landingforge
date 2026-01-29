"""AI-powered HTML landing page generator using Claude."""

import os
from anthropic import Anthropic

from .models import DesignAnalysis, ProductInfo, GeneratedPage


SYSTEM_PROMPT = """You are an expert web developer specializing in creating beautiful,
modern landing pages using Tailwind CSS. You create clean, semantic HTML that is
responsive and accessible.

Your task is to generate a complete, standalone HTML landing page that:
1. Uses only Tailwind CSS via CDN (no custom CSS)
2. Is fully responsive (mobile-first design)
3. Follows the design patterns and color scheme provided
4. Includes smooth scroll behavior and hover effects
5. Uses semantic HTML5 elements
6. Is production-ready and beautiful

Always output ONLY the complete HTML document, starting with <!DOCTYPE html> and
ending with </html>. Do not include any explanations or markdown code fences."""


def build_generation_prompt(design: DesignAnalysis, product: ProductInfo) -> str:
    """Build the prompt for landing page generation."""
    sections_list = ", ".join(design.sections)
    features_text = "\n".join(
        f"- {f.title}: {f.description}" for f in product.features
    ) if product.features else "No specific features provided"

    prompt = f"""Generate a stunning landing page with the following specifications:

## Design System

### Colors
- Primary: {design.colors.primary}
- Secondary: {design.colors.secondary}
- Accent: {design.colors.accent}
- Background: {design.colors.background}
- Text: {design.colors.text}

### Typography
- Heading Font: {design.typography.heading_font}
- Body Font: {design.typography.body_font}
- Use Google Fonts link in the head if fonts are not system fonts

### Layout
- Dark Mode: {"Yes" if design.layout.is_dark_mode else "No"}
- Sections to include: {sections_list}

## Product Information

### Basic Info
- Name: {product.name}
- Tagline: {product.tagline}
- Description: {product.description}

### Features
{features_text}

### Call to Action
- Button Text: {product.cta_text}
- Button Link: {product.cta_url}

{"### Logo" if product.logo_url else ""}
{"Logo URL: " + product.logo_url if product.logo_url else ""}

## Requirements

1. Start with <!DOCTYPE html> and include proper meta tags
2. Include Tailwind CSS via CDN: <script src="https://cdn.tailwindcss.com"></script>
3. Add a Tailwind config script to extend colors with the custom palette
4. Create each section from the layout specification
5. Make the hero section impactful with the tagline and CTA
6. Use a features grid with icons (use emoji or simple SVG icons)
7. Include a footer with copyright
8. Add subtle hover effects on interactive elements
9. Ensure the page is fully responsive
10. Use the exact colors provided in the design system

Generate the complete HTML now:"""

    return prompt


class LandingPageGenerator:
    """Generates landing pages using Claude AI."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable."
            )
        self.client = Anthropic(api_key=self.api_key)

    def generate(self, design: DesignAnalysis, product: ProductInfo) -> GeneratedPage:
        """Generate a landing page based on design analysis and product info."""
        prompt = build_generation_prompt(design, product)

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        html = message.content[0].text

        # Clean up the HTML if it has markdown code fences
        if html.startswith("```"):
            lines = html.split("\n")
            # Remove first line (```html or ```)
            lines = lines[1:]
            # Remove last line if it's ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            html = "\n".join(lines)

        # Ensure it starts with DOCTYPE
        if not html.strip().startswith("<!DOCTYPE"):
            html = "<!DOCTYPE html>\n" + html

        return GeneratedPage(
            html=html,
            design_analysis=design,
            product_info=product,
        )


def generate_landing_page(
    design: DesignAnalysis, product: ProductInfo, api_key: str | None = None
) -> GeneratedPage:
    """Convenience function to generate a landing page."""
    generator = LandingPageGenerator(api_key=api_key)
    return generator.generate(design, product)
