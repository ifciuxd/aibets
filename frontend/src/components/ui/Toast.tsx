'use client'

/**
 * Toast Notification System
 * Professional toast notifications with success/error/warning variants
 */

import { Toaster, toast as hotToast } from 'react-hot-toast'
import { CheckCircle2, AlertCircle, XCircle, Info, X } from 'lucide-react'

export function ToastProvider() {
  return (
    <Toaster
      position="top-right"
      toastOptions={{
        duration: 4000,
        style: {
          background: 'var(--bg-elevated)',
          color: 'var(--text-primary)',
          border: '1px solid var(--clr-neutral-dark)',
          padding: '16px',
          borderRadius: '12px',
          boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)',
          maxWidth: '500px',
        },
        success: {
          icon: <CheckCircle2 className="w-5 h-5" />,
          style: {
            border: '1px solid var(--clr-success)',
          },
        },
        error: {
          icon: <XCircle className="w-5 h-5" />,
          style: {
            border: '1px solid var(--clr-error)',
          },
        },
      }}
    />
  )
}

// Custom toast helpers
export const toast = {
  success: (message: string, description?: string) => {
    return hotToast.custom(
      (t) => (
        <div className={`${t.visible ? 'animate-slide-down' : 'animate-slide-up'}
                        bg-background-elevated border border-success/30 rounded-lg p-4
                        shadow-neon-sm max-w-md flex items-start gap-3`}>
          <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-success">{message}</p>
            {description && (
              <p className="text-sm text-text-secondary mt-1">{description}</p>
            )}
          </div>
          <button
            onClick={() => hotToast.dismiss(t.id)}
            className="text-text-muted hover:text-text-primary transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ),
      { duration: 4000 }
    )
  },

  error: (message: string, description?: string) => {
    return hotToast.custom(
      (t) => (
        <div className={`${t.visible ? 'animate-slide-down' : 'animate-slide-up'}
                        bg-background-elevated border border-error/30 rounded-lg p-4
                        shadow-lg max-w-md flex items-start gap-3`}>
          <XCircle className="w-5 h-5 text-error flex-shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-error">{message}</p>
            {description && (
              <p className="text-sm text-text-secondary mt-1">{description}</p>
            )}
          </div>
          <button
            onClick={() => hotToast.dismiss(t.id)}
            className="text-text-muted hover:text-text-primary transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ),
      { duration: 5000 }
    )
  },

  warning: (message: string, description?: string) => {
    return hotToast.custom(
      (t) => (
        <div className={`${t.visible ? 'animate-slide-down' : 'animate-slide-up'}
                        bg-background-elevated border border-warning/30 rounded-lg p-4
                        shadow-lg max-w-md flex items-start gap-3`}>
          <AlertCircle className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-warning">{message}</p>
            {description && (
              <p className="text-sm text-text-secondary mt-1">{description}</p>
            )}
          </div>
          <button
            onClick={() => hotToast.dismiss(t.id)}
            className="text-text-muted hover:text-text-primary transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ),
      { duration: 4500 }
    )
  },

  info: (message: string, description?: string) => {
    return hotToast.custom(
      (t) => (
        <div className={`${t.visible ? 'animate-slide-down' : 'animate-slide-up'}
                        bg-background-elevated border border-neutral/30 rounded-lg p-4
                        shadow-lg max-w-md flex items-start gap-3`}>
          <Info className="w-5 h-5 text-neutral-light flex-shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-text-primary">{message}</p>
            {description && (
              <p className="text-sm text-text-secondary mt-1">{description}</p>
            )}
          </div>
          <button
            onClick={() => hotToast.dismiss(t.id)}
            className="text-text-muted hover:text-text-primary transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ),
      { duration: 3500 }
    )
  },

  // Special: API Rate Limit Error with countdown
  apiRateLimit: (retryAfter: number = 60) => {
    return hotToast.custom(
      (t) => (
        <div className={`${t.visible ? 'animate-slide-down' : 'animate-slide-up'}
                        bg-background-elevated border border-error/30 rounded-lg p-4
                        shadow-lg max-w-md flex items-start gap-3`}>
          <AlertCircle className="w-5 h-5 text-error flex-shrink-0 mt-0.5 animate-pulse" />
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-error">Przekroczono limit zapytań API</p>
            <p className="text-sm text-text-secondary mt-1">
              Błąd 429: Spróbuj ponownie za {retryAfter} sekund
            </p>
            <div className="mt-2 w-full bg-background-card rounded-full h-1.5">
              <div
                className="bg-error h-1.5 rounded-full transition-all duration-1000"
                style={{ width: '100%' }}
              />
            </div>
          </div>
          <button
            onClick={() => hotToast.dismiss(t.id)}
            className="text-text-muted hover:text-text-primary transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ),
      { duration: retryAfter * 1000 }
    )
  },

  // Loading toast
  loading: (message: string) => {
    return hotToast.loading(message, {
      style: {
        background: 'var(--bg-elevated)',
        color: 'var(--text-primary)',
        border: '1px solid var(--clr-neutral-dark)',
      },
    })
  },

  // Promise-based toast (for async operations)
  promise: <T,>(
    promise: Promise<T>,
    messages: {
      loading: string
      success: string
      error: string
    }
  ) => {
    return hotToast.promise(
      promise,
      {
        loading: messages.loading,
        success: messages.success,
        error: messages.error,
      },
      {
        style: {
          background: 'var(--bg-elevated)',
          color: 'var(--text-primary)',
          border: '1px solid var(--clr-neutral-dark)',
        },
      }
    )
  },
}
