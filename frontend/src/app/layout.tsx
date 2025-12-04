import type { Metadata } from 'next'
import { Inter, Roboto_Mono } from 'next/font/google'
import './globals.css'
import { ToastProvider } from '@/components/ui/Toast'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const robotoMono = Roboto_Mono({ subsets: ['latin'], variable: '--font-roboto-mono' })

export const metadata: Metadata = {
  title: 'AlphaBet - Professional Betting Analysis Platform',
  description: 'Advanced betting analysis powered by PROPHET-70 system',
  keywords: 'betting, sports analysis, value betting, kelly criterion, poisson model',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pl" className={`${inter.variable} ${robotoMono.variable}`}>
      <body className="antialiased">
        {children}
        <ToastProvider />
      </body>
    </html>
  )
}
