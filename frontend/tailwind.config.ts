import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Dark Mode Theme - AlphaBet Design System
        background: {
          DEFAULT: 'var(--bg-dark)',
          card: 'var(--bg-card)',
          hover: 'var(--bg-hover)',
        },
        success: {
          DEFAULT: 'var(--clr-success)',
          dark: 'var(--clr-success-dark)',
          light: 'var(--clr-success-light)',
        },
        warning: {
          DEFAULT: 'var(--clr-warning)',
          dark: 'var(--clr-warning-dark)',
          light: 'var(--clr-warning-light)',
        },
        error: {
          DEFAULT: 'var(--clr-error)',
          dark: 'var(--clr-error-dark)',
          light: 'var(--clr-error-light)',
        },
        neutral: {
          DEFAULT: 'var(--clr-neutral)',
          light: 'var(--clr-neutral-light)',
          dark: 'var(--clr-neutral-dark)',
        },
        text: {
          primary: 'var(--text-primary)',
          secondary: 'var(--text-secondary)',
          muted: 'var(--text-muted)',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Roboto Mono', 'Space Mono', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'fade-in': 'fadeIn 0.2s ease-in',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
      boxShadow: {
        'neon-sm': '0 0 10px var(--clr-success)',
        'neon-md': '0 0 20px var(--clr-success)',
        'neon-lg': '0 0 30px var(--clr-success)',
      },
    },
  },
  plugins: [],
}

export default config
