'use client'

/**
 * Signals Table with Heatmap
 * Interactive table with edge % heatmap coloring and sorting/filtering
 */

import React, { useState, useMemo } from 'react'
import { ArrowUpDown, ArrowUp, ArrowDown, Filter, X } from 'lucide-react'
import clsx from 'clsx'

export interface BettingSignal {
  match_name: string
  league?: string
  recommended_bet: string
  model_probability: number
  implied_probability: number
  edge_percentage: number
  expected_value: number
  bookmaker_odds: number
  recommended_stake_amount: number
  recommended_stake_pct: number
  confidence_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'VERY HIGH'
  reason?: string
}

interface SignalsTableProps {
  signals: BettingSignal[]
  onPlaceBet?: (signal: BettingSignal) => void
}

type SortField = 'edge_percentage' | 'expected_value' | 'recommended_stake_amount' | 'confidence_level'
type SortDirection = 'asc' | 'desc'

export function SignalsTable({ signals, onPlaceBet }: SignalsTableProps) {
  const [sortField, setSortField] = useState<SortField>('edge_percentage')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')
  const [leagueFilter, setLeagueFilter] = useState<string>('')

  // Get unique leagues for filter
  const leagues = useMemo(() => {
    const uniqueLeagues = [...new Set(signals.map((s) => s.league).filter(Boolean))]
    return uniqueLeagues as string[]
  }, [signals])

  // Filter and sort signals
  const processedSignals = useMemo(() => {
    let filtered = [...signals]

    // Apply league filter
    if (leagueFilter) {
      filtered = filtered.filter((s) => s.league === leagueFilter)
    }

    // Sort
    filtered.sort((a, b) => {
      let aVal = a[sortField]
      let bVal = b[sortField]

      // Special handling for confidence level
      if (sortField === 'confidence_level') {
        const levelOrder = { 'LOW': 0, 'MEDIUM': 1, 'HIGH': 2, 'VERY HIGH': 3 }
        aVal = levelOrder[a.confidence_level]
        bVal = levelOrder[b.confidence_level]
      }

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal
      }

      return 0
    })

    return filtered
  }, [signals, sortField, sortDirection, leagueFilter])

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) {
      return <ArrowUpDown className="w-4 h-4 opacity-30" />
    }
    return sortDirection === 'asc' ? (
      <ArrowUp className="w-4 h-4 text-success" />
    ) : (
      <ArrowDown className="w-4 h-4 text-success" />
    )
  }

  // Get heatmap class based on edge percentage
  const getEdgeHeatmapClass = (edge: number): string => {
    if (edge >= 15) return 'edge-very-high'
    if (edge >= 10) return 'edge-high'
    if (edge >= 5) return 'edge-medium'
    return 'edge-low'
  }

  const getConfidenceBadgeClass = (level: string): string => {
    switch (level) {
      case 'VERY HIGH':
        return 'badge-success'
      case 'HIGH':
        return 'badge-success opacity-80'
      case 'MEDIUM':
        return 'badge-warning'
      default:
        return 'badge-neutral'
    }
  }

  if (signals.length === 0) {
    return (
      <div className="card p-12 text-center">
        <p className="text-text-muted">Brak sygnałów do wyświetlenia</p>
      </div>
    )
  }

  return (
    <div className="card p-6">
      {/* Header with filters */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="text-xl font-semibold text-text-primary mb-1">
            Aktywne Sygnały
          </h3>
          <p className="text-sm text-text-muted">
            Znaleziono {processedSignals.length} wartościowych zakładów
          </p>
        </div>

        {/* League Filter */}
        {leagues.length > 0 && (
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-text-muted" />
            <select
              value={leagueFilter}
              onChange={(e) => setLeagueFilter(e.target.value)}
              className="input text-sm py-1.5 px-3"
            >
              <option value="">Wszystkie ligi</option>
              {leagues.map((league) => (
                <option key={league} value={league}>
                  {league}
                </option>
              ))}
            </select>
            {leagueFilter && (
              <button
                onClick={() => setLeagueFilter('')}
                className="text-text-muted hover:text-text-primary transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        )}
      </div>

      {/* Table */}
      <div className="overflow-x-auto -mx-6 px-6">
        <table className="w-full">
          <thead>
            <tr className="border-b border-neutral-dark text-left">
              <th className="pb-3 pr-4 text-sm font-semibold text-text-secondary">
                Mecz
              </th>
              <th className="pb-3 px-4 text-sm font-semibold text-text-secondary">
                Zakład
              </th>
              <th
                className="pb-3 px-4 text-sm font-semibold text-text-secondary cursor-pointer hover:text-text-primary transition-colors"
                onClick={() => handleSort('edge_percentage')}
              >
                <div className="flex items-center gap-1">
                  Edge %
                  <SortIcon field="edge_percentage" />
                </div>
              </th>
              <th
                className="pb-3 px-4 text-sm font-semibold text-text-secondary cursor-pointer hover:text-text-primary transition-colors"
                onClick={() => handleSort('expected_value')}
              >
                <div className="flex items-center gap-1">
                  EV
                  <SortIcon field="expected_value" />
                </div>
              </th>
              <th className="pb-3 px-4 text-sm font-semibold text-text-secondary">
                Kurs
              </th>
              <th
                className="pb-3 px-4 text-sm font-semibold text-text-secondary cursor-pointer hover:text-text-primary transition-colors"
                onClick={() => handleSort('recommended_stake_amount')}
              >
                <div className="flex items-center gap-1">
                  Stake
                  <SortIcon field="recommended_stake_amount" />
                </div>
              </th>
              <th
                className="pb-3 px-4 text-sm font-semibold text-text-secondary cursor-pointer hover:text-text-primary transition-colors"
                onClick={() => handleSort('confidence_level')}
              >
                <div className="flex items-center gap-1">
                  Pewność
                  <SortIcon field="confidence_level" />
                </div>
              </th>
              <th className="pb-3 pl-4 text-sm font-semibold text-text-secondary">
                Akcja
              </th>
            </tr>
          </thead>
          <tbody>
            {processedSignals.map((signal, index) => (
              <tr
                key={index}
                className="border-b border-neutral-dark/50 hover:bg-background-hover transition-colors"
              >
                {/* Match */}
                <td className="py-4 pr-4">
                  <div>
                    <p className="text-sm font-medium text-text-primary">
                      {signal.match_name}
                    </p>
                    {signal.league && (
                      <p className="text-xs text-text-muted mt-0.5">
                        {signal.league}
                      </p>
                    )}
                  </div>
                </td>

                {/* Bet */}
                <td className="py-4 px-4">
                  <span className="badge badge-neutral">
                    {signal.recommended_bet}
                  </span>
                </td>

                {/* Edge % with Heatmap */}
                <td className="py-4 px-4">
                  <div
                    className={clsx(
                      'heatmap-cell font-mono font-semibold text-sm px-3 py-1.5 rounded-lg inline-block',
                      getEdgeHeatmapClass(signal.edge_percentage)
                    )}
                  >
                    {signal.edge_percentage.toFixed(2)}%
                  </div>
                </td>

                {/* EV */}
                <td className="py-4 px-4">
                  <span className="font-mono text-sm text-text-primary">
                    {signal.expected_value.toFixed(4)}
                  </span>
                </td>

                {/* Odds */}
                <td className="py-4 px-4">
                  <span className="font-mono text-sm font-medium text-text-primary">
                    {signal.bookmaker_odds.toFixed(2)}
                  </span>
                </td>

                {/* Stake */}
                <td className="py-4 px-4">
                  <div>
                    <p className="font-mono text-sm font-semibold text-success">
                      {signal.recommended_stake_amount.toFixed(2)} PLN
                    </p>
                    <p className="font-mono text-xs text-text-muted mt-0.5">
                      ({(signal.recommended_stake_pct * 100).toFixed(2)}%)
                    </p>
                  </div>
                </td>

                {/* Confidence */}
                <td className="py-4 px-4">
                  <span className={`badge ${getConfidenceBadgeClass(signal.confidence_level)}`}>
                    {signal.confidence_level}
                  </span>
                </td>

                {/* Action */}
                <td className="py-4 pl-4">
                  <button
                    onClick={() => onPlaceBet?.(signal)}
                    className="btn btn-primary btn-ripple text-sm px-4 py-1.5"
                  >
                    Postaw
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary */}
      <div className="mt-6 pt-6 border-t border-neutral-dark flex items-center justify-between">
        <div className="text-sm text-text-muted">
          Wyświetlono {processedSignals.length} z {signals.length} sygnałów
        </div>
        <div className="text-sm">
          <span className="text-text-muted">Całkowity stake:</span>{' '}
          <span className="font-mono font-semibold text-success ml-2">
            {processedSignals
              .reduce((sum, s) => sum + s.recommended_stake_amount, 0)
              .toFixed(2)}{' '}
            PLN
          </span>
        </div>
      </div>
    </div>
  )
}
