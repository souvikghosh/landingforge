"""Design pattern analyzer for extracted landing page content."""

import re
from collections import Counter

from .models import ColorPalette, Typography, LayoutPattern, DesignAnalysis
from .scraper import ScrapedContent, rgb_to_hex


class DesignAnalyzer:
    """Analyzes scraped content to extract design patterns."""

    def analyze(self, scraped_contents: list[ScrapedContent]) -> DesignAnalysis:
        """Analyze multiple scraped pages and extract unified design patterns."""
        if not scraped_contents:
            return self._default_analysis([])

        # Aggregate data from all pages
        all_colors = []
        all_fonts = []
        all_sections = []

        for content in scraped_contents:
            all_colors.extend(content.colors)
            all_fonts.extend(content.fonts)
            all_sections.extend(content.sections)

        # Extract patterns
        colors = self._analyze_colors(all_colors)
        typography = self._analyze_typography(all_fonts)
        layout = self._analyze_layout(all_sections)
        sections = self._detect_sections(all_sections)
        animations = self._detect_animations(scraped_contents)

        return DesignAnalysis(
            colors=colors,
            typography=typography,
            layout=layout,
            sections=sections,
            animations=animations,
            source_urls=[c.url for c in scraped_contents],
        )

    def _analyze_colors(self, colors: list[str]) -> ColorPalette:
        """Extract a color palette from collected colors."""
        # Convert all colors to hex
        hex_colors = []
        for color in colors:
            if color.startswith("#"):
                hex_colors.append(color.lower())
            elif color.startswith("rgb"):
                hex_color = rgb_to_hex(color)
                if hex_color:
                    hex_colors.append(hex_color.lower())

        if not hex_colors:
            return self._default_colors()

        # Count color frequencies
        color_counts = Counter(hex_colors)
        sorted_colors = [c for c, _ in color_counts.most_common(20)]

        # Categorize colors
        dark_colors = [c for c in sorted_colors if self._is_dark(c)]
        light_colors = [c for c in sorted_colors if self._is_light(c)]
        vibrant_colors = [c for c in sorted_colors if self._is_vibrant(c)]

        # Determine if dark mode based on most common background colors
        is_dark_mode = len(dark_colors) > len(light_colors)

        # Assign colors to roles
        if is_dark_mode:
            background = dark_colors[0] if dark_colors else "#0a0a0a"
            text = light_colors[0] if light_colors else "#ffffff"
        else:
            background = light_colors[0] if light_colors else "#ffffff"
            text = dark_colors[0] if dark_colors else "#1a1a1a"

        primary = vibrant_colors[0] if vibrant_colors else "#3b82f6"
        secondary = vibrant_colors[1] if len(vibrant_colors) > 1 else self._darken(primary)
        accent = vibrant_colors[2] if len(vibrant_colors) > 2 else "#f59e0b"

        return ColorPalette(
            primary=primary,
            secondary=secondary,
            accent=accent,
            background=background,
            text=text,
        )

    def _analyze_typography(self, fonts: list[str]) -> Typography:
        """Extract typography settings from collected fonts."""
        if not fonts:
            return Typography()

        # Count font frequencies
        font_counts = Counter(fonts)
        common_fonts = [f for f, _ in font_counts.most_common(3)]

        # Filter out generic fonts
        specific_fonts = [
            f for f in common_fonts if f.lower() not in ("serif", "sans-serif", "monospace")
        ]

        heading_font = specific_fonts[0] if specific_fonts else "Inter"
        body_font = specific_fonts[1] if len(specific_fonts) > 1 else heading_font

        return Typography(
            heading_font=heading_font,
            body_font=body_font,
            heading_sizes=["4rem", "2.5rem", "1.5rem"],
            body_size="1rem",
        )

    def _analyze_layout(self, sections: list[dict]) -> LayoutPattern:
        """Analyze layout patterns from section data."""
        section_classes = " ".join(s.get("classes", "") for s in sections).lower()
        section_ids = " ".join(s.get("id", "") for s in sections).lower()
        combined = section_classes + " " + section_ids

        # Detect section types
        has_hero = "hero" in combined or any(
            s.get("tag") == "header" and s.get("hasHeading") for s in sections
        )
        has_features = "feature" in combined or any(s.get("hasGrid") for s in sections)
        has_testimonials = "testimonial" in combined or "review" in combined
        has_pricing = "pricing" in combined or "price" in combined
        has_cta = "cta" in combined or "action" in combined
        has_footer = any(s.get("tag") == "footer" for s in sections)

        # Detect dark mode from background colors
        bg_colors = [s.get("backgroundColor", "") for s in sections]
        dark_bgs = sum(1 for bg in bg_colors if bg and self._is_dark(rgb_to_hex(bg) or ""))
        is_dark_mode = dark_bgs > len(bg_colors) / 2 if bg_colors else False

        return LayoutPattern(
            has_hero=has_hero,
            has_features_grid=has_features,
            has_testimonials=has_testimonials,
            has_pricing=has_pricing,
            has_cta=has_cta,
            has_footer=has_footer,
            is_dark_mode=is_dark_mode,
        )

    def _detect_sections(self, sections: list[dict]) -> list[str]:
        """Detect ordered list of section types."""
        detected = []
        section_classes = " ".join(s.get("classes", "") for s in sections).lower()

        # Check for each section type in common order
        section_types = [
            ("hero", ["hero", "header", "banner"]),
            ("features", ["feature", "benefit", "service"]),
            ("how_it_works", ["how", "step", "process"]),
            ("testimonials", ["testimonial", "review", "customer"]),
            ("pricing", ["pricing", "price", "plan"]),
            ("faq", ["faq", "question", "answer"]),
            ("cta", ["cta", "action", "signup", "subscribe"]),
            ("footer", ["footer"]),
        ]

        for section_name, keywords in section_types:
            if any(kw in section_classes for kw in keywords):
                if section_name not in detected:
                    detected.append(section_name)

        # Ensure basic sections are included
        if "hero" not in detected:
            detected.insert(0, "hero")
        if "footer" not in detected:
            detected.append("footer")

        return detected

    def _detect_animations(self, scraped_contents: list[ScrapedContent]) -> list[str]:
        """Detect CSS animation classes used."""
        animations = set()
        animation_patterns = [
            r"animate-[\w-]+",
            r"transition-[\w-]+",
            r"fade-[\w-]+",
            r"slide-[\w-]+",
            r"hover:[\w-]+",
        ]

        for content in scraped_contents:
            for style in content.styles:
                for pattern in animation_patterns:
                    matches = re.findall(pattern, style)
                    animations.update(matches)

            # Check HTML classes too
            for pattern in animation_patterns:
                matches = re.findall(pattern, content.html)
                animations.update(matches)

        return list(animations)[:10]  # Limit to 10

    def _default_analysis(self, urls: list[str]) -> DesignAnalysis:
        """Return default design analysis when no data is available."""
        return DesignAnalysis(
            colors=self._default_colors(),
            typography=Typography(),
            layout=LayoutPattern(),
            sections=["hero", "features", "cta", "footer"],
            animations=[],
            source_urls=urls,
        )

    def _default_colors(self) -> ColorPalette:
        """Return default color palette."""
        return ColorPalette(
            primary="#3b82f6",
            secondary="#1e40af",
            accent="#f59e0b",
            background="#ffffff",
            text="#1f2937",
        )

    def _is_dark(self, hex_color: str) -> bool:
        """Check if a color is dark."""
        if not hex_color or not hex_color.startswith("#"):
            return False
        try:
            hex_color = hex_color.lstrip("#")
            if len(hex_color) == 3:
                hex_color = "".join(c * 2 for c in hex_color)
            r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return luminance < 0.3
        except (ValueError, IndexError):
            return False

    def _is_light(self, hex_color: str) -> bool:
        """Check if a color is light."""
        if not hex_color or not hex_color.startswith("#"):
            return False
        try:
            hex_color = hex_color.lstrip("#")
            if len(hex_color) == 3:
                hex_color = "".join(c * 2 for c in hex_color)
            r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return luminance > 0.7
        except (ValueError, IndexError):
            return False

    def _is_vibrant(self, hex_color: str) -> bool:
        """Check if a color is vibrant (high saturation)."""
        if not hex_color or not hex_color.startswith("#"):
            return False
        try:
            hex_color = hex_color.lstrip("#")
            if len(hex_color) == 3:
                hex_color = "".join(c * 2 for c in hex_color)
            r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
            max_c = max(r, g, b)
            min_c = min(r, g, b)
            saturation = (max_c - min_c) / max_c if max_c > 0 else 0
            return saturation > 0.4 and 50 < max_c < 240
        except (ValueError, IndexError):
            return False

    def _darken(self, hex_color: str, factor: float = 0.8) -> str:
        """Darken a hex color by a factor."""
        try:
            hex_color = hex_color.lstrip("#")
            if len(hex_color) == 3:
                hex_color = "".join(c * 2 for c in hex_color)
            r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return hex_color


def analyze_designs(scraped_contents: list[ScrapedContent]) -> DesignAnalysis:
    """Convenience function to analyze scraped content."""
    analyzer = DesignAnalyzer()
    return analyzer.analyze(scraped_contents)
