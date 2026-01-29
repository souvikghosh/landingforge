/**
 * API client for LandingForge backend
 */

const API_BASE = '/api'

export interface ColorPalette {
  primary: string
  secondary: string
  accent: string
  background: string
  text: string
}

export interface Typography {
  heading_font: string
  body_font: string
  heading_sizes: string[]
  body_size: string
}

export interface LayoutPattern {
  has_hero: boolean
  has_features_grid: boolean
  has_testimonials: boolean
  has_pricing: boolean
  has_cta: boolean
  has_footer: boolean
  is_dark_mode: boolean
}

export interface DesignAnalysis {
  colors: ColorPalette
  typography: Typography
  layout: LayoutPattern
  sections: string[]
  animations: string[]
  source_urls: string[]
}

export interface Feature {
  title: string
  description: string
  icon?: string
}

export interface ProductInfo {
  name: string
  tagline: string
  description: string
  features: Feature[]
  cta_text: string
  cta_url: string
  logo_url?: string
}

export interface GenerateResponse {
  html: string
  preview_id?: string
}

class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message)
    this.name = 'ApiError'
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = 'An error occurred'
    try {
      const data = await response.json()
      message = data.detail || data.message || message
    } catch {
      message = response.statusText
    }
    throw new ApiError(message, response.status)
  }
  return response.json()
}

/**
 * Analyze URLs and extract design patterns
 */
export async function analyzeUrls(urls: string[]): Promise<DesignAnalysis> {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ urls }),
  })

  const data = await handleResponse<{ design_analysis: DesignAnalysis }>(response)
  return data.design_analysis
}

/**
 * Generate a landing page from design analysis and product info
 */
export async function generatePage(
  designAnalysis: DesignAnalysis,
  productInfo: ProductInfo
): Promise<GenerateResponse> {
  const response = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      design_analysis: designAnalysis,
      product_info: productInfo,
    }),
  })

  return handleResponse<GenerateResponse>(response)
}

/**
 * Check API health
 */
export async function checkHealth(): Promise<{ status: string; version: string }> {
  const response = await fetch(`${API_BASE}/health`)
  return handleResponse(response)
}
