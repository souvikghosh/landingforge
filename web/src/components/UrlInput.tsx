'use client'

import { useState } from 'react'

interface UrlInputProps {
  onSubmit: (urls: string[]) => void
  loading: boolean
}

export default function UrlInput({ onSubmit, loading }: UrlInputProps) {
  const [urls, setUrls] = useState<string[]>([''])

  const addUrl = () => {
    if (urls.length < 5) {
      setUrls([...urls, ''])
    }
  }

  const removeUrl = (index: number) => {
    if (urls.length > 1) {
      setUrls(urls.filter((_, i) => i !== index))
    }
  }

  const updateUrl = (index: number, value: string) => {
    const newUrls = [...urls]
    newUrls[index] = value
    setUrls(newUrls)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const validUrls = urls.filter((url) => url.trim() !== '')
    if (validUrls.length > 0) {
      // Normalize URLs
      const normalizedUrls = validUrls.map((url) => {
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
          return `https://${url}`
        }
        return url
      })
      onSubmit(normalizedUrls)
    }
  }

  const hasValidUrls = urls.some((url) => url.trim() !== '')

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Landing Page URLs
        </label>

        <div className="space-y-3">
          {urls.map((url, index) => (
            <div key={index} className="flex items-center gap-2">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={url}
                  onChange={(e) => updateUrl(index, e.target.value)}
                  placeholder="e.g., linear.app or https://vercel.com"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                  disabled={loading}
                />
              </div>
              {urls.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeUrl(index)}
                  className="p-2 text-gray-400 hover:text-red-500 transition"
                  disabled={loading}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              )}
            </div>
          ))}
        </div>

        {urls.length < 5 && (
          <button
            type="button"
            onClick={addUrl}
            className="mt-3 text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
            disabled={loading}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add another URL
          </button>
        )}

        <p className="mt-3 text-sm text-gray-500">
          Add up to 5 URLs. We&apos;ll extract colors, fonts, and layout patterns from these sites.
        </p>
      </div>

      {/* Example sites */}
      <div className="bg-gray-50 rounded-lg p-4">
        <p className="text-sm text-gray-600 mb-2">Try these examples:</p>
        <div className="flex flex-wrap gap-2">
          {['linear.app', 'vercel.com', 'stripe.com', 'notion.so', 'figma.com'].map((site) => (
            <button
              key={site}
              type="button"
              onClick={() => {
                const emptyIndex = urls.findIndex((u) => u.trim() === '')
                if (emptyIndex !== -1) {
                  updateUrl(emptyIndex, site)
                } else if (urls.length < 5) {
                  setUrls([...urls, site])
                }
              }}
              className="px-3 py-1 text-sm bg-white border border-gray-200 rounded-full hover:border-primary-300 hover:text-primary-600 transition"
              disabled={loading}
            >
              {site}
            </button>
          ))}
        </div>
      </div>

      <button
        type="submit"
        disabled={!hasValidUrls || loading}
        className="w-full py-3 px-4 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <div className="spinner" />
            Analyzing...
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            Analyze Design Patterns
          </>
        )}
      </button>
    </form>
  )
}
