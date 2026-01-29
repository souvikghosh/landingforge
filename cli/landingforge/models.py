"""Pydantic models for LandingForge data structures."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ColorPalette(BaseModel):
    """Extracted color palette from analyzed sites."""

    primary: str = Field(description="Primary brand color (hex)")
    secondary: str = Field(description="Secondary color (hex)")
    accent: str = Field(description="Accent/highlight color (hex)")
    background: str = Field(description="Background color (hex)")
    text: str = Field(description="Main text color (hex)")


class Typography(BaseModel):
    """Typography settings extracted from analyzed sites."""

    heading_font: str = Field(default="Inter", description="Font family for headings")
    body_font: str = Field(default="Inter", description="Font family for body text")
    heading_sizes: list[str] = Field(
        default=["4rem", "2.5rem", "1.5rem"], description="Heading sizes (h1, h2, h3)"
    )
    body_size: str = Field(default="1rem", description="Body text size")


class LayoutPattern(BaseModel):
    """Layout pattern information."""

    has_hero: bool = Field(default=True, description="Has hero section")
    has_features_grid: bool = Field(default=True, description="Has features grid")
    has_testimonials: bool = Field(default=False, description="Has testimonials section")
    has_pricing: bool = Field(default=False, description="Has pricing section")
    has_cta: bool = Field(default=True, description="Has call-to-action section")
    has_footer: bool = Field(default=True, description="Has footer")
    is_dark_mode: bool = Field(default=False, description="Uses dark mode design")


class DesignAnalysis(BaseModel):
    """Complete design analysis from scraped URLs."""

    colors: ColorPalette
    typography: Typography
    layout: LayoutPattern
    sections: list[str] = Field(
        default_factory=lambda: ["hero", "features", "cta", "footer"],
        description="Ordered list of detected sections",
    )
    animations: list[str] = Field(
        default_factory=list, description="CSS animation classes detected"
    )
    source_urls: list[str] = Field(description="Original URLs analyzed")


class Feature(BaseModel):
    """A product feature with title and description."""

    title: str = Field(description="Feature name/title")
    description: str = Field(description="Feature description")
    icon: Optional[str] = Field(default=None, description="Optional icon name or emoji")


class ProductInfo(BaseModel):
    """User-provided product information for landing page generation."""

    name: str = Field(description="Product/company name")
    tagline: str = Field(description="Hero headline/tagline")
    description: str = Field(description="What the product does")
    features: list[Feature] = Field(
        default_factory=list, description="List of product features"
    )
    cta_text: str = Field(default="Get Started", description="Call-to-action button text")
    cta_url: str = Field(default="#", description="CTA link URL")
    logo_url: Optional[str] = Field(default=None, description="Logo image URL")


class GeneratedPage(BaseModel):
    """A generated landing page with all associated data."""

    html: str = Field(description="Complete HTML with Tailwind CDN")
    design_analysis: DesignAnalysis
    product_info: ProductInfo
    created_at: datetime = Field(default_factory=datetime.now)


# API Request/Response Models


class AnalyzeRequest(BaseModel):
    """Request body for /api/analyze endpoint."""

    urls: list[str] = Field(min_length=1, max_length=5, description="URLs to analyze")


class AnalyzeResponse(BaseModel):
    """Response body for /api/analyze endpoint."""

    design_analysis: DesignAnalysis


class GenerateRequest(BaseModel):
    """Request body for /api/generate endpoint."""

    design_analysis: DesignAnalysis
    product_info: ProductInfo


class GenerateResponse(BaseModel):
    """Response body for /api/generate endpoint."""

    html: str
    preview_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Response body for /api/health endpoint."""

    status: str = "ok"
    version: str
