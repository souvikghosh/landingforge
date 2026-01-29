'use client'

import { useState } from 'react'
import UrlInput from '@/components/UrlInput'
import ProductForm from '@/components/ProductForm'
import DesignPanel from '@/components/DesignPanel'
import Preview from '@/components/Preview'
import ExportButton from '@/components/ExportButton'
import { analyzeUrls, generatePage, DesignAnalysis, ProductInfo } from '@/lib/api'

type Step = 'urls' | 'product' | 'preview'

export default function Home() {
  const [step, setStep] = useState<Step>('urls')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [designAnalysis, setDesignAnalysis] = useState<DesignAnalysis | null>(null)
  const [productInfo, setProductInfo] = useState<ProductInfo | null>(null)
  const [generatedHtml, setGeneratedHtml] = useState<string | null>(null)

  const handleAnalyzeUrls = async (urls: string[]) => {
    setLoading(true)
    setError(null)
    try {
      const analysis = await analyzeUrls(urls)
      setDesignAnalysis(analysis)
      setStep('product')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze URLs')
    } finally {
      setLoading(false)
    }
  }

  const handleGeneratePage = async (product: ProductInfo) => {
    if (!designAnalysis) return

    setLoading(true)
    setError(null)
    setProductInfo(product)
    try {
      const result = await generatePage(designAnalysis, product)
      setGeneratedHtml(result.html)
      setStep('preview')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate page')
    } finally {
      setLoading(false)
    }
  }

  const handleBack = () => {
    if (step === 'product') {
      setStep('urls')
    } else if (step === 'preview') {
      setStep('product')
    }
  }

  const handleStartOver = () => {
    setStep('urls')
    setDesignAnalysis(null)
    setProductInfo(null)
    setGeneratedHtml(null)
    setError(null)
  }

  return (
    <main className="min-h-screen">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">LandingForge</h1>
                <p className="text-sm text-gray-500">AI Landing Page Generator</p>
              </div>
            </div>

            {/* Step indicator */}
            <div className="flex items-center gap-2">
              <StepIndicator step={1} current={step === 'urls'} completed={step !== 'urls'} label="Analyze" />
              <div className="w-8 h-px bg-gray-300" />
              <StepIndicator step={2} current={step === 'product'} completed={step === 'preview'} label="Details" />
              <div className="w-8 h-px bg-gray-300" />
              <StepIndicator step={3} current={step === 'preview'} completed={false} label="Preview" />
            </div>
          </div>
        </div>
      </header>

      {/* Error banner */}
      {error && (
        <div className="bg-red-50 border-b border-red-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
            <div className="flex items-center gap-2 text-red-800">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              <span>{error}</span>
              <button
                onClick={() => setError(null)}
                className="ml-auto text-red-600 hover:text-red-800"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {step === 'urls' && (
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                Get Inspired by Beautiful Sites
              </h2>
              <p className="text-gray-600">
                Enter 1-5 landing page URLs you admire. We&apos;ll analyze their design patterns
                and help you create something similar.
              </p>
            </div>
            <UrlInput onSubmit={handleAnalyzeUrls} loading={loading} />
          </div>
        )}

        {step === 'product' && designAnalysis && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <div className="flex items-center gap-4 mb-6">
                <button
                  onClick={handleBack}
                  className="text-gray-600 hover:text-gray-900 flex items-center gap-1"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Back
                </button>
                <h2 className="text-2xl font-bold text-gray-900">
                  Tell Us About Your Product
                </h2>
              </div>
              <ProductForm onSubmit={handleGeneratePage} loading={loading} />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Extracted Design
              </h3>
              <DesignPanel analysis={designAnalysis} />
            </div>
          </div>
        )}

        {step === 'preview' && generatedHtml && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <button
                  onClick={handleBack}
                  className="text-gray-600 hover:text-gray-900 flex items-center gap-1"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Back
                </button>
                <h2 className="text-2xl font-bold text-gray-900">
                  Your Generated Landing Page
                </h2>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={handleStartOver}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Start Over
                </button>
                <ExportButton html={generatedHtml} filename={productInfo?.name || 'landing-page'} />
              </div>
            </div>
            <Preview html={generatedHtml} />
          </div>
        )}
      </div>
    </main>
  )
}

function StepIndicator({
  step,
  current,
  completed,
  label,
}: {
  step: number
  current: boolean
  completed: boolean
  label: string
}) {
  return (
    <div className="flex items-center gap-2">
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
          current
            ? 'bg-primary-600 text-white'
            : completed
            ? 'bg-green-500 text-white'
            : 'bg-gray-200 text-gray-600'
        }`}
      >
        {completed ? (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clipRule="evenodd"
            />
          </svg>
        ) : (
          step
        )}
      </div>
      <span className={`text-sm ${current ? 'text-gray-900 font-medium' : 'text-gray-500'}`}>
        {label}
      </span>
    </div>
  )
}
