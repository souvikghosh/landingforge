"""URL scraper using Playwright for extracting landing page content."""

import asyncio
import re
from dataclasses import dataclass

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, Browser


@dataclass
class ScrapedContent:
    """Content extracted from a URL."""

    url: str
    html: str
    text_content: str
    styles: list[str]
    fonts: list[str]
    colors: list[str]
    sections: list[dict]
    meta: dict


class Scraper:
    """Playwright-based scraper for landing pages."""

    def __init__(self):
        self._browser: Browser | None = None
        self._playwright = None

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def scrape_url(self, url: str) -> ScrapedContent:
        """Scrape a single URL and extract design-relevant content."""
        if not self._browser:
            raise RuntimeError("Scraper must be used as async context manager")

        # Use a real browser user agent
        context = await self._browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            # Use "load" instead of "networkidle" for faster loading
            await page.goto(url, wait_until="load", timeout=45000)
            await page.wait_for_timeout(2000)  # Wait for JS rendering

            # Get full HTML
            html = await page.content()

            # Extract computed styles for key elements
            styles = await self._extract_styles(page)

            # Extract fonts
            fonts = await self._extract_fonts(page)

            # Extract colors
            colors = await self._extract_colors(page)

            # Extract sections
            sections = await self._extract_sections(page)

            # Extract meta info
            meta = await self._extract_meta(page)

            # Get text content
            text_content = await page.inner_text("body")

            return ScrapedContent(
                url=url,
                html=html,
                text_content=text_content,
                styles=styles,
                fonts=fonts,
                colors=colors,
                sections=sections,
                meta=meta,
            )
        finally:
            await page.close()
            await context.close()

    async def _extract_styles(self, page: Page) -> list[str]:
        """Extract inline and linked stylesheets."""
        styles = []

        # Get inline styles
        inline_styles = await page.evaluate("""
            () => {
                const styles = [];
                document.querySelectorAll('style').forEach(s => {
                    styles.push(s.textContent);
                });
                return styles;
            }
        """)
        styles.extend(inline_styles)

        return styles

    async def _extract_fonts(self, page: Page) -> list[str]:
        """Extract font families used on the page."""
        fonts = await page.evaluate("""
            () => {
                const fonts = new Set();
                const elements = document.querySelectorAll('h1, h2, h3, h4, p, a, button, span');
                elements.forEach(el => {
                    const computed = window.getComputedStyle(el);
                    const fontFamily = computed.fontFamily;
                    if (fontFamily) {
                        // Extract first font from family
                        const firstFont = fontFamily.split(',')[0].trim().replace(/['"]/g, '');
                        fonts.add(firstFont);
                    }
                });
                return Array.from(fonts);
            }
        """)
        return fonts

    async def _extract_colors(self, page: Page) -> list[str]:
        """Extract colors used on the page."""
        colors = await page.evaluate("""
            () => {
                const colors = new Set();
                const elements = document.querySelectorAll('*');

                elements.forEach(el => {
                    const computed = window.getComputedStyle(el);

                    // Get background color
                    const bg = computed.backgroundColor;
                    if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
                        colors.add(bg);
                    }

                    // Get text color
                    const color = computed.color;
                    if (color) {
                        colors.add(color);
                    }

                    // Get border color
                    const border = computed.borderColor;
                    if (border && border !== 'rgba(0, 0, 0, 0)') {
                        colors.add(border);
                    }
                });

                return Array.from(colors).slice(0, 50); // Limit to 50 colors
            }
        """)
        return colors

    async def _extract_sections(self, page: Page) -> list[dict]:
        """Extract main sections from the page."""
        sections = await page.evaluate("""
            () => {
                const sections = [];
                const sectionElements = document.querySelectorAll('section, header, footer, main, [class*="hero"], [class*="feature"], [class*="pricing"], [class*="testimonial"], [class*="cta"]');

                sectionElements.forEach((el, index) => {
                    const rect = el.getBoundingClientRect();
                    const computed = window.getComputedStyle(el);

                    sections.push({
                        tag: el.tagName.toLowerCase(),
                        classes: el.className,
                        id: el.id,
                        backgroundColor: computed.backgroundColor,
                        height: rect.height,
                        order: index,
                        hasHeading: el.querySelector('h1, h2, h3') !== null,
                        hasButton: el.querySelector('button, a[class*="btn"], a[class*="button"]') !== null,
                        hasGrid: el.querySelector('[class*="grid"]') !== null || computed.display === 'grid',
                    });
                });

                return sections;
            }
        """)
        return sections

    async def _extract_meta(self, page: Page) -> dict:
        """Extract meta information from the page."""
        meta = await page.evaluate("""
            () => {
                const getMeta = (name) => {
                    const el = document.querySelector(`meta[name="${name}"], meta[property="${name}"]`);
                    return el ? el.getAttribute('content') : null;
                };

                return {
                    title: document.title,
                    description: getMeta('description') || getMeta('og:description'),
                    ogImage: getMeta('og:image'),
                    themeColor: getMeta('theme-color'),
                };
            }
        """)
        return meta

    async def scrape_urls(self, urls: list[str]) -> list[ScrapedContent]:
        """Scrape multiple URLs concurrently."""
        tasks = [self.scrape_url(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)


def rgb_to_hex(rgb_string: str) -> str | None:
    """Convert RGB/RGBA string to hex color."""
    match = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", rgb_string)
    if match:
        r, g, b = map(int, match.groups())
        return f"#{r:02x}{g:02x}{b:02x}"
    return None


async def scrape_landing_pages(urls: list[str]) -> list[ScrapedContent]:
    """Convenience function to scrape multiple landing pages."""
    async with Scraper() as scraper:
        results = await scraper.scrape_urls(urls)
        # Filter out exceptions
        return [r for r in results if isinstance(r, ScrapedContent)]
