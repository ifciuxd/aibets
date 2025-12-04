'use client'

/**
 * Capital Growth Chart
 * Advanced chart with gradient line, custom tooltips, and animations
 */

import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts'
import { format } from 'date-fns'
import { pl } from 'date-fns/locale'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface CapitalDataPoint {
  date: string
  capital: number
  profit?: number
}

interface CapitalChartProps {
  data: CapitalDataPoint[]
  initialCapital?: number
}

export function CapitalChart({ data, initialCapital = 10000 }: CapitalChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="card p-6">
        <p className="text-text-muted text-center">Brak danych do wyświetlenia</p>
      </div>
    )
  }

  const currentCapital = data[data.length - 1]?.capital || initialCapital
  const capitalChange = currentCapital - initialCapital
  const capitalChangePercent = ((capitalChange / initialCapital) * 100).toFixed(2)
  const isPositive = capitalChange >= 0

  return (
    <div className="card p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-semibold text-text-primary mb-1">
            Wzrost Kapitału
          </h3>
          <div className="flex items-center gap-3">
            <span className="font-mono text-3xl font-bold text-gradient-success">
              {currentCapital.toLocaleString('pl-PL', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })} PLN
            </span>
            <div
              className={`flex items-center gap-1 px-2 py-1 rounded-full text-sm font-medium ${
                isPositive
                  ? 'bg-success/20 text-success'
                  : 'bg-error/20 text-error'
              }`}
            >
              {isPositive ? (
                <TrendingUp className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )}
              <span className="font-mono">
                {isPositive ? '+' : ''}
                {capitalChangePercent}%
              </span>
            </div>
          </div>
        </div>

        <div className="text-right">
          <p className="text-text-muted text-sm">Kapitał początkowy</p>
          <p className="font-mono text-lg text-text-secondary">
            {initialCapital.toLocaleString('pl-PL')} PLN
          </p>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={350}>
        <AreaChart
          data={data}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <defs>
            {/* Gradient for the area */}
            <linearGradient id="capitalGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--clr-success)" stopOpacity={0.3} />
              <stop offset="100%" stopColor="var(--clr-success-dark)" stopOpacity={0} />
            </linearGradient>

            {/* Gradient for the line */}
            <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="var(--clr-success-dark)" />
              <stop offset="100%" stopColor="var(--clr-success-light)" />
            </linearGradient>
          </defs>

          <CartesianGrid
            strokeDasharray="3 3"
            stroke="var(--clr-neutral-dark)"
            opacity={0.1}
          />

          <XAxis
            dataKey="date"
            stroke="var(--text-muted)"
            tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
            tickFormatter={(value) => {
              try {
                return format(new Date(value), 'dd MMM', { locale: pl })
              } catch {
                return value
              }
            }}
          />

          <YAxis
            stroke="var(--text-muted)"
            tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
            tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
            domain={['dataMin - 500', 'dataMax + 500']}
          />

          <Tooltip content={<CustomTooltip />} />

          {/* Area fill */}
          <Area
            type="monotone"
            dataKey="capital"
            stroke="none"
            fill="url(#capitalGradient)"
          />

          {/* Line with gradient and glow */}
          <Line
            type="monotone"
            dataKey="capital"
            stroke="url(#lineGradient)"
            strokeWidth={3}
            dot={false}
            activeDot={{
              r: 6,
              fill: 'var(--clr-success-light)',
              stroke: 'var(--bg-dark)',
              strokeWidth: 2,
            }}
            filter="drop-shadow(0 0 8px var(--clr-success))"
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-success shadow-neon-sm" />
          <span className="text-text-secondary">Kapitał</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-0.5 bg-gradient-to-r from-success-dark to-success-light" />
          <span className="text-text-secondary">Trend</span>
        </div>
      </div>
    </div>
  )
}

// Custom Tooltip Component
function CustomTooltip({ active, payload }: any) {
  if (!active || !payload || !payload.length) {
    return null
  }

  const data = payload[0].payload as CapitalDataPoint

  return (
    <div className="chart-tooltip">
      <p className="text-xs text-text-muted mb-2">
        {format(new Date(data.date), 'dd MMMM yyyy', { locale: pl })}
      </p>
      <div className="space-y-1">
        <div className="flex items-center justify-between gap-4">
          <span className="text-sm text-text-secondary">Kapitał:</span>
          <span className="font-mono text-sm font-semibold text-success">
            {data.capital.toLocaleString('pl-PL', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })} PLN
          </span>
        </div>
        {data.profit !== undefined && (
          <div className="flex items-center justify-between gap-4">
            <span className="text-sm text-text-secondary">Zysk:</span>
            <span
              className={`font-mono text-sm font-semibold ${
                data.profit >= 0 ? 'text-success' : 'text-error'
              }`}
            >
              {data.profit >= 0 ? '+' : ''}
              {data.profit.toLocaleString('pl-PL', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })} PLN
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
