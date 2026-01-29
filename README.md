# LandingForge

AI-powered landing page generator that analyzes beautiful websites and creates custom landing pages inspired by their design patterns.

## Features

- **URL Scraping** - Extract design patterns from 1-5 landing pages
- **Design Analysis** - Identify colors, fonts, layout patterns, and sections
- **AI Generation** - Generate landing page HTML using Claude
- **Live Preview** - Preview in responsive desktop, tablet, and mobile views
- **Export** - Download as standalone HTML with Tailwind CDN

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        LandingForge                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐      ┌──────────────────────────────────┐ │
│  │   Python CLI     │      │        Next.js Web UI            │ │
│  │                  │      │                                  │ │
│  │  • Scrape sites  │ JSON │  • Input URLs & product info     │ │
│  │  • Extract design│─────▶│  • Real-time preview             │ │
│  │  • Analyze with  │      │  • Customize sections            │ │
│  │    AI            │      │  • Export HTML                   │ │
│  │  • Generate HTML │      │                                  │ │
│  └──────────────────┘      └──────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| CLI Backend | Python 3.11+, Playwright, BeautifulSoup |
| AI | Claude API (Anthropic) |
| Web UI | Next.js 14, React 18, Tailwind CSS |
| Communication | REST API (FastAPI) |
| Output | Standalone HTML + Tailwind CDN |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Anthropic API key

### 1. Set up the Python CLI/API

```bash
cd cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Install Playwright browsers
playwright install chromium

# Set your Anthropic API key
export ANTHROPIC_API_KEY=your-api-key
```

### 2. Set up the Web UI

```bash
cd web

# Install dependencies
npm install
```

### 3. Run the application

In one terminal, start the API server:
```bash
cd cli
source venv/bin/activate
landingforge serve
```

In another terminal, start the web UI:
```bash
cd web
npm run dev
```

Open http://localhost:3000 in your browser.

## CLI Usage

### Analyze landing pages

```bash
# Analyze one or more URLs (max 5)
landingforge analyze linear.app vercel.com

# Save analysis to JSON
landingforge analyze linear.app -o analysis.json
```

### Generate a landing page

```bash
# Generate with default styling
landingforge generate \
  --name "TaskFlow" \
  --tagline "Project management that just works" \
  --feature "Real-time sync:Changes appear instantly" \
  --feature "Keyboard first:Navigate with shortcuts"

# Generate using analyzed design patterns
landingforge generate \
  --analysis analysis.json \
  --name "TaskFlow" \
  --tagline "Project management that just works" \
  --output my-landing-page.html

# Generate with dark mode
landingforge generate \
  --name "TaskFlow" \
  --tagline "Project management that just works" \
  --dark
```

### Start API server

```bash
# Start with default settings (0.0.0.0:8000)
landingforge serve

# Custom host and port
landingforge serve --host 127.0.0.1 --port 9000

# Development mode with auto-reload
landingforge serve --reload
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/analyze` | Analyze URLs, return design patterns |
| POST | `/api/generate` | Generate landing page HTML |
| GET | `/api/preview/{id}` | Get generated page preview |

### POST /api/analyze

```json
// Request
{ "urls": ["https://linear.app", "https://vercel.com"] }

// Response
{
  "design_analysis": {
    "colors": {
      "primary": "#5E6AD2",
      "secondary": "#2D2D2D",
      "accent": "#F5A623",
      "background": "#000000",
      "text": "#FFFFFF"
    },
    "typography": {
      "heading_font": "Inter",
      "body_font": "Inter"
    },
    "sections": ["hero", "features", "cta", "footer"]
  }
}
```

### POST /api/generate

```json
// Request
{
  "design_analysis": { ... },
  "product_info": {
    "name": "TaskFlow",
    "tagline": "Project management that just works",
    "description": "Simple, fast task management",
    "features": [
      {"title": "Real-time sync", "description": "Changes appear instantly"}
    ],
    "cta_text": "Start for free",
    "cta_url": "https://taskflow.app/signup"
  }
}

// Response
{
  "html": "<!DOCTYPE html>...",
  "preview_id": "abc123"
}
```

## Project Structure

```
landingforge/
├── cli/                          # Python CLI & API backend
│   ├── landingforge/
│   │   ├── __init__.py
│   │   ├── cli.py               # CLI entry point
│   │   ├── scraper.py           # Playwright scraping
│   │   ├── analyzer.py          # Design pattern analysis
│   │   ├── generator.py         # AI-powered HTML generation
│   │   ├── api.py               # FastAPI server
│   │   └── models.py            # Pydantic models
│   └── pyproject.toml
│
├── web/                          # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Main page
│   │   │   └── layout.tsx       # Root layout
│   │   ├── components/
│   │   │   ├── UrlInput.tsx     # URL input form
│   │   │   ├── ProductForm.tsx  # Product info form
│   │   │   ├── Preview.tsx      # Live HTML preview
│   │   │   ├── DesignPanel.tsx  # Design analysis display
│   │   │   └── ExportButton.tsx # Download button
│   │   └── lib/
│   │       └── api.ts           # API client
│   └── package.json
│
└── README.md
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Yes |

## License

MIT
