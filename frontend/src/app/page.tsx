'use client'

/**
 * AlphaBet Dashboard - MVP Version
 * Real data from localStorage, manual match entry, bet tracking
 */

import React, { useState, useEffect } from 'react'
import { CapitalChart } from '@/components/charts/CapitalChart'
import { SignalsTable, BettingSignal } from '@/components/tables/SignalsTable'
import { BetHistoryTable } from '@/components/history/BetHistoryTable'
import { AddMatchForm } from '@/components/forms/AddMatchForm'
import { SkeletonDashboard } from '@/components/ui/LoadingStates'
import { toast } from '@/components/ui/Toast'
import { api, AnalysisResponse, MatchInput, BettingDecisionResponse } from '@/lib/api'
import {
  getSettings,
  saveSettings,
  getBetHistory,
  addBet,
  updateBetResult,
  deleteBet,
  getCapitalHistory,
  getStats,
  resetBankroll,
  BetHistory,
} from '@/lib/storage'
import {
  TrendingUp,
  DollarSign,
  Target,
  Award,
  RefreshCw,
  Settings,
  Plus,
  History,
  BarChart3,
} from 'lucide-react'

export default function Dashboard() {
  const [loading, setLoading] = useState(false)
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null)
  const [settings, setSettingsState] = useState(getSettings())
  const [betHistory, setBetHistory] = useState<BetHistory[]>([])
  const [capitalHistory, setCapitalHistory] = useState(getCapitalHistory())
  const [stats, setStats] = useState(getStats())

  // UI State
  const [showAddMatch, setShowAddMatch] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [currentTab, setCurrentTab] = useState<'signals' | 'history'>('signals')

  // Pending matches to analyze
  const [pendingMatches, setPendingMatches] = useState<MatchInput[]>([])

  useEffect(() => {
    // Load data from localStorage
    setBetHistory(getBetHistory())
    setCapitalHistory(getCapitalHistory())
    setStats(getStats())
  }, [])

  const refreshData = () => {
    setBetHistory(getBetHistory())
    setCapitalHistory(getCapitalHistory())
    setStats(getStats())
    setSettingsState(getSettings())
  }

  const handleAddMatch = (match: MatchInput) => {
    setPendingMatches([...pendingMatches, match])
    setShowAddMatch(false)
    toast.success('Mecz dodany!', `${match.match_name} został dodany do analizy`)
  }

  const handleAnalyzeMatches = async () => {
    if (pendingMatches.length === 0) {
      toast.warning('Brak meczów', 'Dodaj mecze do analizy')
      return
    }

    setLoading(true)
    try {
      const result = await api.analyzeMatches(pendingMatches, settings)
      setAnalysis(result)

      if (result.value_bets_found > 0) {
        toast.success(
          `Znaleziono ${result.value_bets_found} wartościowych zakładów!`,
          `Łączny stake: ${result.portfolio_summary.total_stake_amount.toFixed(2)} PLN`
        )
      } else {
        toast.info('Brak value bets', 'Spróbuj dostosować ustawienia lub dodać inne mecze')
      }
    } catch (error) {
      toast.error(
        'Błąd analizy',
        error instanceof Error ? error.message : 'Nieznany błąd'
      )
    } finally {
      setLoading(false)
    }
  }

  const handlePlaceBet = (signal: BettingSignal) => {
    // Add bet to history
    addBet({
      date: new Date().toISOString(),
      match_name: signal.match_name,
      bet_type: signal.recommended_bet,
      odds: signal.bookmaker_odds,
      stake: signal.recommended_stake_amount,
      status: 'pending',
      profit: 0,
    })

    // Remove from pending matches
    setPendingMatches(
      pendingMatches.filter((m) => m.match_name !== signal.match_name)
    )

    // Clear analysis if all bets placed
    if (analysis && analysis.recommendations.length === 1) {
      setAnalysis(null)
    } else if (analysis) {
      setAnalysis({
        ...analysis,
        recommendations: analysis.recommendations.filter(
          (r) => r.match_name !== signal.match_name
        ),
        value_bets_found: analysis.value_bets_found - 1,
      })
    }

    refreshData()
    toast.success('Zakład dodany!', `${signal.match_name}: ${signal.recommended_bet}`)
  }

  const handleUpdateBetResult = (
    betId: string,
    status: 'won' | 'lost',
    matchResult?: string
  ) => {
    updateBetResult(betId, status, matchResult)
    refreshData()

    const bet = betHistory.find((b) => b.id === betId)
    if (bet) {
      if (status === 'won') {
        toast.success(
          'Wygrana! 🎉',
          `+${(bet.stake * (bet.odds - 1)).toFixed(2)} PLN`
        )
      } else {
        toast.error('Przegrana', `-${bet.stake.toFixed(2)} PLN`)
      }
    }
  }

  const handleDeleteBet = (betId: string) => {
    deleteBet(betId)
    refreshData()
    toast.info('Zakład usunięty')
  }

  const handleRemovePendingMatch = (matchName: string) => {
    setPendingMatches(pendingMatches.filter((m) => m.match_name !== matchName))
    toast.info('Mecz usunięty z listy')
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-background p-4 md:p-8">
        <div className="max-w-7xl mx-auto">
          <SkeletonDashboard />
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-neutral-dark bg-background-card">
        <div className="max-w-7xl mx-auto px-4 md:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gradient-success mb-1">
                AlphaBet MVP
              </h1>
              <p className="text-text-muted">
                Professional Betting Analysis Platform
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowAddMatch(true)}
                className="btn btn-primary flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Dodaj Mecz
              </button>
              {pendingMatches.length > 0 && (
                <button
                  onClick={handleAnalyzeMatches}
                  className="btn btn-primary flex items-center gap-2 animate-pulse"
                >
                  <BarChart3 className="w-4 h-4" />
                  Analizuj ({pendingMatches.length})
                </button>
              )}
              <button
                onClick={refreshData}
                className="btn btn-secondary flex items-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Odśwież
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 md:px-8 py-8 space-y-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            icon={DollarSign}
            label="Kapitał"
            value={`${stats.currentBankroll.toLocaleString('pl-PL', {
              minimumFractionDigits: 2,
            })} PLN`}
            trend={`${stats.currentRoi >= 0 ? '+' : ''}${stats.currentRoi.toFixed(2)}%`}
            trendUp={stats.currentRoi >= 0}
          />
          <StatCard
            icon={Target}
            label="Zakłady"
            value={stats.totalBets}
            subtitle={`${stats.wonBets} wygranych / ${stats.lostBets} przegranych`}
          />
          <StatCard
            icon={TrendingUp}
            label="Win Rate"
            value={`${stats.winRate.toFixed(1)}%`}
            subtitle={`${stats.pendingBets} oczekujących`}
          />
          <StatCard
            icon={Award}
            label="Total Profit"
            value={`${stats.totalProfit >= 0 ? '+' : ''}${stats.totalProfit.toFixed(
              2
            )} PLN`}
            trend={`ROI: ${stats.roi.toFixed(1)}%`}
            trendUp={stats.totalProfit >= 0}
          />
        </div>

        {/* Capital Chart */}
        <CapitalChart
          data={capitalHistory.map((h) => ({
            date: h.date,
            capital: h.capital,
            profit: h.profit,
          }))}
          initialCapital={settings.initial_bankroll}
        />

        {/* Pending Matches */}
        {pendingMatches.length > 0 && (
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-text-primary">
                Mecze do Analizy ({pendingMatches.length})
              </h3>
              <button
                onClick={handleAnalyzeMatches}
                className="btn btn-primary btn-sm"
              >
                Analizuj Wszystkie
              </button>
            </div>
            <div className="space-y-2">
              {pendingMatches.map((match, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 rounded bg-background-hover"
                >
                  <div>
                    <p className="text-text-primary font-medium">
                      {match.match_name}
                    </p>
                    <p className="text-xs text-text-muted">
                      Kursy: {match.odds_home} / {match.odds_draw} /{' '}
                      {match.odds_away}
                    </p>
                  </div>
                  <button
                    onClick={() => handleRemovePendingMatch(match.match_name)}
                    className="text-error hover:text-error-light"
                  >
                    Usuń
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-4 border-b border-neutral-dark">
          <button
            onClick={() => setCurrentTab('signals')}
            className={`pb-3 px-4 border-b-2 transition-colors ${
              currentTab === 'signals'
                ? 'border-success text-success'
                : 'border-transparent text-text-muted hover:text-text-primary'
            }`}
          >
            Sygnały
          </button>
          <button
            onClick={() => setCurrentTab('history')}
            className={`pb-3 px-4 border-b-2 transition-colors flex items-center gap-2 ${
              currentTab === 'history'
                ? 'border-success text-success'
                : 'border-transparent text-text-muted hover:text-text-primary'
            }`}
          >
            <History className="w-4 h-4" />
            Historia ({betHistory.length})
          </button>
        </div>

        {/* Content */}
        {currentTab === 'signals' ? (
          analysis && analysis.recommendations.length > 0 ? (
            <SignalsTable
              signals={analysis.recommendations}
              onPlaceBet={handlePlaceBet}
            />
          ) : (
            <div className="card p-12 text-center">
              <Target className="w-16 h-16 text-neutral-dark mx-auto mb-4" />
              <p className="text-text-muted text-lg mb-2">
                Brak sygnałów do wyświetlenia
              </p>
              <p className="text-text-muted text-sm mb-6">
                Dodaj mecze i kliknij "Analizuj" aby znaleźć value bets
              </p>
              <button
                onClick={() => setShowAddMatch(true)}
                className="btn btn-primary mx-auto"
              >
                <Plus className="w-4 h-4 inline mr-2" />
                Dodaj Pierwszy Mecz
              </button>
            </div>
          )
        ) : (
          <BetHistoryTable
            bets={betHistory}
            onUpdateResult={handleUpdateBetResult}
            onDelete={handleDeleteBet}
          />
        )}

        {/* Footer */}
        <footer className="text-center text-text-muted text-sm py-6">
          <p>AlphaBet Platform MVP v1.0.0</p>
          <p className="mt-1">
            Pamiętaj: Stawiaj odpowiedzialnie. Hazard może uzależniać.
          </p>
        </footer>
      </div>

      {/* Modals */}
      {showAddMatch && (
        <AddMatchForm
          onSubmit={handleAddMatch}
          onCancel={() => setShowAddMatch(false)}
        />
      )}
    </main>
  )
}

// Stat Card Component
function StatCard({
  icon: Icon,
  label,
  value,
  subtitle,
  trend,
  trendUp,
}: {
  icon: React.ComponentType<{ className?: string }>
  label: string
  value: string | number
  subtitle?: string
  trend?: string
  trendUp?: boolean
}) {
  return (
    <div className="card p-6 hover-lift">
      <div className="flex items-center justify-between mb-3">
        <div className="p-2 rounded-lg bg-success/10">
          <Icon className="w-5 h-5 text-success" />
        </div>
        {trend && (
          <span
            className={`text-xs font-medium font-mono ${
              trendUp ? 'text-success' : 'text-error'
            }`}
          >
            {trend}
          </span>
        )}
      </div>
      <p className="text-text-muted text-sm mb-1">{label}</p>
      <p className="text-2xl font-bold font-mono text-text-primary">{value}</p>
      {subtitle && <p className="text-text-muted text-xs mt-1">{subtitle}</p>}
    </div>
  )
}
