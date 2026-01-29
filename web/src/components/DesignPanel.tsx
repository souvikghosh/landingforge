'use client'

import { DesignAnalysis } from '@/lib/api'

interface DesignPanelProps {
  analysis: DesignAnalysis
}

export default function DesignPanel({ analysis }: DesignPanelProps) {
  return (
    <div className="space-y-4">
      {/* Color Palette */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-3">Color Palette</h4>
        <div className="space-y-2">
          <ColorSwatch label="Primary" color={analysis.colors.primary} />
          <ColorSwatch label="Secondary" color={analysis.colors.secondary} />
          <ColorSwatch label="Accent" color={analysis.colors.accent} />
          <ColorSwatch label="Background" color={analysis.colors.background} />
          <ColorSwatch label="Text" color={analysis.colors.text} />
        </div>
      </div>

      {/* Typography */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-3">Typography</h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Heading Font</span>
            <span className="font-medium">{analysis.typography.heading_font}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Body Font</span>
            <span className="font-medium">{analysis.typography.body_font}</span>
          </div>
        </div>
      </div>

      {/* Layout */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-3">Layout</h4>
        <div className="flex flex-wrap gap-2">
          {analysis.layout.has_hero && <LayoutBadge label="Hero" />}
          {analysis.layout.has_features_grid && <LayoutBadge label="Features" />}
          {analysis.layout.has_testimonials && <LayoutBadge label="Testimonials" />}
          {analysis.layout.has_pricing && <LayoutBadge label="Pricing" />}
          {analysis.layout.has_cta && <LayoutBadge label="CTA" />}
          {analysis.layout.has_footer && <LayoutBadge label="Footer" />}
        </div>
        {analysis.layout.is_dark_mode && (
          <div className="mt-3 flex items-center gap-2 text-sm text-gray-600">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
            </svg>
            Dark Mode Design
          </div>
        )}
      </div>

      {/* Sections */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-3">Detected Sections</h4>
        <div className="space-y-1">
          {analysis.sections.map((section, index) => (
            <div key={section} className="flex items-center gap-2 text-sm">
              <span className="w-5 h-5 rounded-full bg-gray-100 text-gray-600 flex items-center justify-center text-xs">
                {index + 1}
              </span>
              <span className="capitalize">{section.replace('_', ' ')}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Source URLs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-3">Analyzed From</h4>
        <div className="space-y-1">
          {analysis.source_urls.map((url) => (
            <div key={url} className="text-sm text-gray-600 truncate" title={url}>
              {new URL(url).hostname}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function ColorSwatch({ label, color }: { label: string; color: string }) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div
          className="w-6 h-6 rounded border border-gray-200"
          style={{ backgroundColor: color }}
        />
        <span className="text-sm text-gray-600">{label}</span>
      </div>
      <span className="text-sm font-mono text-gray-500">{color}</span>
    </div>
  )
}

function LayoutBadge({ label }: { label: string }) {
  return (
    <span className="px-2 py-1 bg-primary-50 text-primary-700 text-xs rounded-full">
      {label}
    </span>
  )
}
