import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'LandingForge - AI Landing Page Generator',
  description: 'Generate beautiful landing pages inspired by sites you admire',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen">{children}</body>
    </html>
  )
}
