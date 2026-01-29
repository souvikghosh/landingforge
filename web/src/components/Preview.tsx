'use client'

import { useState, useRef, useEffect } from 'react'

interface PreviewProps {
  html: string
}

type ViewMode = 'desktop' | 'tablet' | 'mobile'

export default function Preview({ html }: PreviewProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('desktop')
  const iframeRef = useRef<HTMLIFrameElement>(null)

  const widthMap: Record<ViewMode, string> = {
    desktop: '100%',
    tablet: '768px',
    mobile: '375px',
  }

  useEffect(() => {
    // Write HTML to iframe
    if (iframeRef.current) {
      const doc = iframeRef.current.contentDocument
      if (doc) {
        doc.open()
        doc.write(html)
        doc.close()
      }
    }
  }, [html])

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-400" />
            <div className="w-3 h-3 rounded-full bg-yellow-400" />
            <div className="w-3 h-3 rounded-full bg-green-400" />
          </div>
          <span className="ml-2 text-sm text-gray-500">Preview</span>
        </div>

        {/* View mode toggle */}
        <div className="flex items-center gap-1 bg-gray-200 rounded-lg p-1">
          <ViewModeButton
            mode="desktop"
            current={viewMode}
            onClick={() => setViewMode('desktop')}
            icon={
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            }
          />
          <ViewModeButton
            mode="tablet"
            current={viewMode}
            onClick={() => setViewMode('tablet')}
            icon={
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 18h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                />
              </svg>
            }
          />
          <ViewModeButton
            mode="mobile"
            current={viewMode}
            onClick={() => setViewMode('mobile')}
            icon={
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
                />
              </svg>
            }
          />
        </div>
      </div>

      {/* Preview area */}
      <div className="bg-gray-100 p-4 flex justify-center overflow-auto" style={{ height: '70vh' }}>
        <div
          className="bg-white shadow-lg transition-all duration-300 overflow-hidden"
          style={{
            width: widthMap[viewMode],
            maxWidth: '100%',
          }}
        >
          <iframe
            ref={iframeRef}
            title="Landing Page Preview"
            className="w-full h-full border-0"
            style={{ minHeight: '800px' }}
            sandbox="allow-scripts allow-same-origin"
          />
        </div>
      </div>
    </div>
  )
}

function ViewModeButton({
  mode,
  current,
  onClick,
  icon,
}: {
  mode: ViewMode
  current: ViewMode
  onClick: () => void
  icon: React.ReactNode
}) {
  const isActive = mode === current

  return (
    <button
      onClick={onClick}
      className={`p-1.5 rounded transition ${
        isActive
          ? 'bg-white text-gray-900 shadow-sm'
          : 'text-gray-500 hover:text-gray-700'
      }`}
      title={`${mode.charAt(0).toUpperCase() + mode.slice(1)} view`}
    >
      {icon}
    </button>
  )
}
