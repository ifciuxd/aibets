'use client'

/**
 * Bet History Table - shows all placed bets with results
 */

import React, { useState } from 'react'
import { Check, X, Edit2, Trash2, Trophy, TrendingDown } from 'lucide-react'
import { BetHistory } from '@/lib/storage'
import { format } from 'date-fns'
import { pl } from 'date-fns/locale'

interface BetHistoryTableProps {
  bets: BetHistory[]
  onUpdateResult: (betId: string, status: 'won' | 'lost', matchResult?: string) => void
  onDelete: (betId: string) => void
}

export function BetHistoryTable({ bets, onUpdateResult, onDelete }: BetHistoryTableProps) {
  const [editingBet, setEditingBet] = useState<string | null>(null)
  const [matchResult, setMatchResult] = useState('')

  if (bets.length === 0) {
    return (
      <div className="card p-12 text-center">
        <Trophy className="w-16 h-16 text-neutral-dark mx-auto mb-4" />
        <p className="text-text-muted text-lg">Brak historii zakładów</p>
        <p className="text-text-muted text-sm mt-2">
          Dodaj mecze i zacznij analizować zakłady
        </p>
      </div>
    )
  }

  const handleSaveResult = (betId: string, won: boolean) => {
    onUpdateResult(betId, won ? 'won' : 'lost', matchResult || undefined)
    setEditingBet(null)
    setMatchResult('')
  }

  const sortedBets = [...bets].sort((a, b) =>
    new Date(b.date).getTime() - new Date(a.date).getTime()
  )

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-text-primary">
          Historia Zakładów
        </h3>
        <div className="text-sm text-text-muted">
          Łącznie: {bets.length} zakładów
        </div>
      </div>

      <div className="overflow-x-auto -mx-6 px-6">
        <table className="w-full">
          <thead>
            <tr className="border-b border-neutral-dark text-left">
              <th className="pb-3 pr-4 text-sm font-semibold text-text-secondary">
                Data
              </th>
              <th className="pb-3 px-4 text-sm font-semibold text-text-secondary">
                Mecz
              </th>
              <th className="pb-3 px-4 text-sm font-semibold text-text-secondary">
                Typ
              </th>
              <th className="pb-3 px-4 text-sm font-semibold text-text-secondary">
                Kurs
              </th>
              <th className="pb-3 px-4 text-sm font-semibold text-text-secondary">
                Stake
              </th>
              <th className="pb-3 px-4 text-sm font-semibold text-text-secondary">
                Status
              </th>
              <th className="pb-3 px-4 text-sm font-semibold text-text-secondary">
                Profit/Loss
              </th>
              <th className="pb-3 pl-4 text-sm font-semibold text-text-secondary">
                Akcje
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedBets.map((bet) => (
              <tr
                key={bet.id}
                className="border-b border-neutral-dark/50 hover:bg-background-hover transition-colors"
              >
                {/* Date */}
                <td className="py-4 pr-4">
                  <div className="text-sm text-text-primary">
                    {format(new Date(bet.date), 'dd MMM', { locale: pl })}
                  </div>
                  <div className="text-xs text-text-muted">
                    {format(new Date(bet.date), 'HH:mm')}
                  </div>
                </td>

                {/* Match */}
                <td className="py-4 px-4">
                  <div className="text-sm text-text-primary">
                    {bet.match_name}
                  </div>
                  {bet.match_result && (
                    <div className="text-xs text-text-muted mt-0.5">
                      Wynik: {bet.match_result}
                    </div>
                  )}
                </td>

                {/* Bet Type */}
                <td className="py-4 px-4">
                  <span
                    className={`badge ${
                      bet.bet_type === 'Home Win'
                        ? 'badge-success'
                        : bet.bet_type === 'Draw'
                        ? 'badge-neutral'
                        : 'badge-warning'
                    }`}
                  >
                    {bet.bet_type}
                  </span>
                </td>

                {/* Odds */}
                <td className="py-4 px-4">
                  <span className="font-mono text-sm text-text-primary font-medium">
                    {bet.odds.toFixed(2)}
                  </span>
                </td>

                {/* Stake */}
                <td className="py-4 px-4">
                  <span className="font-mono text-sm text-text-primary">
                    {bet.stake.toFixed(2)} PLN
                  </span>
                </td>

                {/* Status */}
                <td className="py-4 px-4">
                  {editingBet === bet.id ? (
                    <div className="flex gap-2">
                      <input
                        type="text"
                        placeholder="2:1"
                        className="input text-xs py-1 px-2 w-16"
                        value={matchResult}
                        onChange={(e) => setMatchResult(e.target.value)}
                      />
                    </div>
                  ) : (
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${
                        bet.status === 'won'
                          ? 'bg-success/20 text-success'
                          : bet.status === 'lost'
                          ? 'bg-error/20 text-error'
                          : 'bg-neutral/20 text-neutral'
                      }`}
                    >
                      {bet.status === 'won' && <Check className="w-3 h-3" />}
                      {bet.status === 'lost' && <X className="w-3 h-3" />}
                      {bet.status === 'pending' && 'Oczekuje'}
                      {bet.status === 'won' && 'Wygrana'}
                      {bet.status === 'lost' && 'Przegrana'}
                    </span>
                  )}
                </td>

                {/* Profit/Loss */}
                <td className="py-4 px-4">
                  <span
                    className={`font-mono text-sm font-semibold ${
                      bet.profit > 0
                        ? 'text-success'
                        : bet.profit < 0
                        ? 'text-error'
                        : 'text-text-muted'
                    }`}
                  >
                    {bet.profit > 0 && '+'}
                    {bet.profit.toFixed(2)} PLN
                  </span>
                </td>

                {/* Actions */}
                <td className="py-4 pl-4">
                  {bet.status === 'pending' && (
                    <>
                      {editingBet === bet.id ? (
                        <div className="flex gap-1">
                          <button
                            onClick={() => handleSaveResult(bet.id, true)}
                            className="p-1.5 rounded bg-success/20 hover:bg-success/30 text-success transition-colors"
                            title="Wygrana"
                          >
                            <Trophy className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleSaveResult(bet.id, false)}
                            className="p-1.5 rounded bg-error/20 hover:bg-error/30 text-error transition-colors"
                            title="Przegrana"
                          >
                            <TrendingDown className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => {
                              setEditingBet(null)
                              setMatchResult('')
                            }}
                            className="p-1.5 rounded bg-neutral/20 hover:bg-neutral/30 text-neutral transition-colors"
                            title="Anuluj"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ) : (
                        <div className="flex gap-1">
                          <button
                            onClick={() => setEditingBet(bet.id)}
                            className="p-1.5 rounded hover:bg-background-hover text-text-muted hover:text-text-primary transition-colors"
                            title="Zapisz wynik"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => {
                              if (confirm('Czy na pewno usunąć ten zakład?')) {
                                onDelete(bet.id)
                              }
                            }}
                            className="p-1.5 rounded hover:bg-error/20 text-text-muted hover:text-error transition-colors"
                            title="Usuń"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      )}
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary */}
      <div className="mt-6 pt-6 border-t border-neutral-dark grid grid-cols-3 gap-6">
        <div>
          <p className="text-xs text-text-muted mb-1">Oczekujące</p>
          <p className="text-2xl font-mono font-bold text-neutral">
            {bets.filter((b) => b.status === 'pending').length}
          </p>
        </div>
        <div>
          <p className="text-xs text-text-muted mb-1">Wygrane</p>
          <p className="text-2xl font-mono font-bold text-success">
            {bets.filter((b) => b.status === 'won').length}
          </p>
        </div>
        <div>
          <p className="text-xs text-text-muted mb-1">Przegrane</p>
          <p className="text-2xl font-mono font-bold text-error">
            {bets.filter((b) => b.status === 'lost').length}
          </p>
        </div>
      </div>
    </div>
  )
}
