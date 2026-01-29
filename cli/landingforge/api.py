"""FastAPI server for LandingForge API."""

import asyncio
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from . import __version__
from .models import (
    AnalyzeRequest,
    AnalyzeResponse,
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
)
from .scraper import scrape_landing_pages
from .analyzer import analyze_designs
from .generator import generate_landing_page


# In-memory store for generated pages (for preview)
generated_pages: dict[str, str] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    yield
    # Shutdown
    generated_pages.clear()


app = FastAPI(
    title="LandingForge API",
    description="AI-powered landing page generator",
    version=__version__,
    lifespan=lifespan,
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok", version=__version__)


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_urls(request: AnalyzeRequest):
    """Analyze URLs and extract design patterns."""
    try:
        # Scrape the URLs
        scraped_contents = await scrape_landing_pages(request.urls)

        if not scraped_contents:
            raise HTTPException(
                status_code=400,
                detail="Could not scrape any of the provided URLs",
            )

        # Analyze the scraped content
        design_analysis = analyze_designs(scraped_contents)

        return AnalyzeResponse(design_analysis=design_analysis)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing URLs: {str(e)}",
        )


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_page(request: GenerateRequest):
    """Generate a landing page based on design analysis and product info."""
    try:
        # Generate the landing page
        result = generate_landing_page(
            design=request.design_analysis,
            product=request.product_info,
        )

        # Store for preview
        preview_id = str(uuid.uuid4())[:8]
        generated_pages[preview_id] = result.html

        return GenerateResponse(
            html=result.html,
            preview_id=preview_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating page: {str(e)}",
        )


@app.get("/api/preview/{preview_id}", response_class=HTMLResponse)
async def get_preview(preview_id: str):
    """Get a generated page preview by ID."""
    html = generated_pages.get(preview_id)
    if not html:
        raise HTTPException(
            status_code=404,
            detail="Preview not found",
        )
    return HTMLResponse(content=html)


# CLI runner for development
def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the FastAPI server."""
    import uvicorn

    uvicorn.run(
        "landingforge.api:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    run_server(reload=True)
