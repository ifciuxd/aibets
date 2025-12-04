'use client'

/**
 * Loading States Components
 * Skeleton screens and loading indicators for better UX
 */

import React from 'react'
import { Loader2 } from 'lucide-react'

// Skeleton components for different UI elements
export function SkeletonCard() {
  return (
    <div className="card p-6 space-y-4 animate-pulse">
      <div className="skeleton h-6 w-1/3 rounded" />
      <div className="skeleton h-4 w-full rounded" />
      <div className="skeleton h-4 w-5/6 rounded" />
      <div className="skeleton h-10 w-1/4 rounded-lg mt-4" />
    </div>
  )
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="card p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="skeleton h-8 w-48 rounded" />
        <div className="skeleton h-10 w-32 rounded-lg" />
      </div>

      {/* Table */}
      <div className="space-y-3">
        {/* Header Row */}
        <div className="grid grid-cols-6 gap-4 pb-3 border-b border-neutral-dark">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="skeleton h-4 rounded" />
          ))}
        </div>

        {/* Data Rows */}
        {[...Array(rows)].map((_, rowIndex) => (
          <div key={rowIndex} className="grid grid-cols-6 gap-4 py-3">
            {[...Array(6)].map((_, colIndex) => (
              <div key={colIndex} className="skeleton h-5 rounded" />
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}

export function SkeletonChart() {
  return (
    <div className="card p-6 space-y-4">
      <div className="skeleton h-6 w-1/4 rounded mb-6" />
      <div className="skeleton h-64 w-full rounded-lg" />
      <div className="flex gap-4 mt-4">
        <div className="skeleton h-4 w-20 rounded" />
        <div className="skeleton h-4 w-20 rounded" />
        <div className="skeleton h-4 w-20 rounded" />
      </div>
    </div>
  )
}

export function SkeletonStats() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="card p-6 space-y-3">
          <div className="skeleton h-4 w-1/2 rounded" />
          <div className="skeleton h-10 w-3/4 rounded" />
          <div className="skeleton h-3 w-1/3 rounded" />
        </div>
      ))}
    </div>
  )
}

// Dashboard skeleton (complete loading state)
export function SkeletonDashboard() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Stats */}
      <SkeletonStats />

      {/* Chart */}
      <SkeletonChart />

      {/* Table */}
      <SkeletonTable rows={8} />
    </div>
  )
}

// Spinning loader
export function Spinner({ size = 'md', className = '' }: { size?: 'sm' | 'md' | 'lg'; className?: string }) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  }

  return (
    <Loader2 className={`animate-spin text-success ${sizeClasses[size]} ${className}`} />
  )
}

// Button with loading state
export function LoadingButton({
  loading,
  children,
  className = '',
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { loading?: boolean }) {
  return (
    <button
      className={`btn btn-primary flex items-center gap-2 ${loading ? 'opacity-75 cursor-not-allowed' : ''} ${className}`}
      disabled={loading}
      {...props}
    >
      {loading && <Spinner size="sm" />}
      {children}
    </button>
  )
}

// Full page loader
export function PageLoader({ message = 'Ładowanie...' }: { message?: string }) {
  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="card p-8 flex flex-col items-center gap-4">
        <Spinner size="lg" />
        <p className="text-text-secondary">{message}</p>
      </div>
    </div>
  )
}

// Inline loader for sections
export function SectionLoader({ message = 'Ładowanie danych...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <Spinner size="lg" />
      <p className="text-text-secondary mt-4">{message}</p>
    </div>
  )
}

// Empty state (when no data)
export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
}: {
  icon?: React.ComponentType<{ className?: string }>
  title: string
  description?: string
  action?: React.ReactNode
}) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      {Icon && <Icon className="w-16 h-16 text-neutral-dark mb-4" />}
      <h3 className="text-xl font-semibold text-text-primary mb-2">{title}</h3>
      {description && <p className="text-text-muted max-w-md mb-6">{description}</p>}
      {action}
    </div>
  )
}

// Progress bar
export function ProgressBar({ progress, className = '' }: { progress: number; className?: string }) {
  return (
    <div className={`w-full bg-background-card rounded-full h-2 overflow-hidden ${className}`}>
      <div
        className="bg-gradient-to-r from-success-dark to-success h-full transition-all duration-300 ease-out"
        style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
      />
    </div>
  )
}

// Pulsing dot indicator
export function PulsingDot({ variant = 'success' }: { variant?: 'success' | 'warning' | 'error' }) {
  const colors = {
    success: 'bg-success',
    warning: 'bg-warning',
    error: 'bg-error',
  }

  return (
    <span className="relative flex h-3 w-3">
      <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${colors[variant]} opacity-75`} />
      <span className={`relative inline-flex rounded-full h-3 w-3 ${colors[variant]}`} />
    </span>
  )
}
