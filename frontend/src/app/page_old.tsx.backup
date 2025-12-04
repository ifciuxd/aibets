'use client'

/**
 * AlphaBet Dashboard - Main Page
 * Professional betting analysis interface with real-time updates
 */

import React, { useState, useEffect } from 'react'
import { CapitalChart } from '@/components/charts/CapitalChart'
import { SignalsTable, BettingSignal } from '@/components/tables/SignalsTable'
import { SkeletonDashboard, SkeletonStats } from '@/components/ui/LoadingStates'
import { toast } from '@/components/ui/Toast'
import { api, AnalysisResponse, MatchInput } from '@/lib/api'
import { TrendingUp, DollarSign, Target, Award, RefreshCw, Settings } from 'lucide-react'

// Sample data for demo
const SAMPLE_MATCHES: MatchInput[] = [
  {
    match_name: "Manchester City vs Arsenal",
    league: "Premier League",
    home_team: {
      name: "Manchester City",
      goals_scored_avg: 2.5,
      goals_conceded_avg: 0.8,
      form: "WWWDW"
    },
    away_team: {
      name: "Arsenal",
      goals_scored_avg: 2.1,
      goals_conceded_avg: 1.0,
      form: "WWDWL"
    },
    odds_home: 1.65,
    odds_draw: 4.20,
    odds_away: 5.50,
    home_xg: 2.3,
    away_xg: 1.1
  },
  {
    match_name: "Real Madrid vs Barcelona",
    league: "La Liga",
    home_team: {
      name: "Real Madrid",
      goals_scored_avg: 2.8,
      goals_conceded_avg: 0.9,
      form: "WWWWW"
    },
    away_team: {
      name: "Barcelona",
      goals_scored_avg: 2.6,
      goals_conceded_avg: 1.1,
      form: "WDWWW"
    },
    odds_home: 2.10,
    odds_draw: 3.50,
    odds_away: 3.40,
    home_xg: 2.4,
    away_xg: 1.8
  },
  // Add more matches...
]

export default function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null)
  const [settings, setSettings] = useState({
    bankroll: 10000,
    kelly_fraction: 0.25,
    min_edge: 0.05,
  })

  useEffect(() => {
    loadAnalysis()
  }, [])

  const loadAnalysis = async () => {
    setLoading(true)
    try {
      const result = await api.analyzeMatches(SAMPLE_MATCHES, settings)
      setAnalysis(result)

      if (result.value_bets_found > 0) {
        toast.success(
          `Znaleziono ${result.value_bets_found} wartościowych zakładów!`,
          `Całkowity stake: ${result.portfolio_summary.total_stake_amount.toFixed(2)} PLN`
        )
      } else {
        toast.info('Brak value bets', 'Spróbuj dostosować ustawienia')
      }
    } catch (error) {
      toast.error(
        'Błąd połączenia z API',
        error instanceof Error ? error.message : 'Nieznany błąd'
      )
    } finally {
      setLoading(false)
    }
  }

  const handlePlaceBet = (signal: BettingSignal) => {
    toast.success(
      'Zakład dodany!',
      `${signal.match_name}: ${signal.recommended_bet} @ ${signal.bookmaker_odds}`
    )
  }

  // Sample capital history data
  const capitalHistory = [
    { date: '2024-12-01', capital: 10000, profit: 0 },
    { date: '2024-12-02', capital: 10250, profit: 250 },
    { date: '2024-12-03', capital: 10180, profit: -70 },
    { date: '2024-12-04', capital: 10580, profit: 400 },
  ]

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
                AlphaBet
              </h1>
              <p className="text-text-muted">Professional Betting Analysis Platform</p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={loadAnalysis}
                className="btn btn-secondary flex items-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Odśwież
              </button>
              <button className="btn btn-primary flex items-center gap-2">
                <Settings className="w-4 h-4" />
                Ustawienia
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 md:px-8 py-8 space-y-8">
        {/* Stats Cards */}
        {analysis && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              icon={DollarSign}
              label="Kapitał"
              value={`${settings.bankroll.toLocaleString('pl-PL')} PLN`}
              trend="+5.8%"
              trendUp
            />
            <StatCard
              icon={Target}
              label="Value Bets"
              value={analysis.value_bets_found}
              subtitle={`z ${analysis.total_matches_analyzed} meczów`}
            />
            <StatCard
              icon={TrendingUp}
              label="Średni Edge"
              value={`${analysis.portfolio_summary.average_edge.toFixed(2)}%`}
              trend="Wysoki"
              trendUp
            />
            <StatCard
              icon={Award}
              label="Expected Value"
              value={analysis.portfolio_summary.average_expected_value.toFixed(4)}
              subtitle="Średni EV"
            />
          </div>
        )}

        {/* Capital Chart */}
        <CapitalChart data={capitalHistory} initialCapital={settings.bankroll} />

        {/* Signals Table */}
        {analysis && (
          <SignalsTable
            signals={analysis.recommendations}
            onPlaceBet={handlePlaceBet}
          />
        )}

        {/* Portfolio Summary */}
        {analysis && analysis.value_bets_found > 0 && (
          <div className="card p-6">
            <h3 className="text-xl font-semibold text-text-primary mb-4">
              Podsumowanie Portfela
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-text-muted text-sm mb-1">Całkowity Stake</p>
                <p className="font-mono text-2xl font-bold text-success">
                  {analysis.portfolio_summary.total_stake_amount.toFixed(2)} PLN
                </p>
                <p className="text-text-muted text-sm mt-1">
                  {analysis.portfolio_summary.percentage_of_bankroll.toFixed(2)}% bankrolla
                </p>
              </div>
              <div>
                <p className="text-text-muted text-sm mb-1">Średni Kurs</p>
                <p className="font-mono text-2xl font-bold text-text-primary">
                  {analysis.portfolio_summary.average_odds.toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-text-muted text-sm mb-1">Rozkład Pewności</p>
                <div className="flex flex-wrap gap-2 mt-2">
                  {Object.entries(analysis.portfolio_summary.confidence_distribution).map(
                    ([level, count]) =>
                      count > 0 && (
                        <span
                          key={level}
                          className={`badge ${
                            level === 'VERY HIGH' || level === 'HIGH'
                              ? 'badge-success'
                              : level === 'MEDIUM'
                              ? 'badge-warning'
                              : 'badge-neutral'
                          }`}
                        >
                          {level}: {count}
                        </span>
                      )
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="text-center text-text-muted text-sm py-6">
          <p>AlphaBet Platform v1.0.0 - Powered by PROPHET-70</p>
          <p className="mt-1">
            Pamiętaj: Stawiaj odpowiedzialnie. Hazard może uzależniać.
          </p>
        </footer>
      </div>
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
            className={`text-xs font-medium ${
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
