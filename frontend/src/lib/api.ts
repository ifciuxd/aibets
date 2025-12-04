/**
 * API Client for AlphaBet Backend
 * Type-safe API calls with error handling
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface TeamStats {
  name: string
  goals_scored_avg: number
  goals_conceded_avg: number
  form?: string
}

export interface MatchInput {
  match_id?: string
  match_name: string
  date?: string
  league?: string
  home_team: TeamStats
  away_team: TeamStats
  odds_home: number
  odds_draw: number
  odds_away: number
  home_xg?: number
  away_xg?: number
}

export interface BettingDecisionResponse {
  match_name: string
  recommended_bet: string
  model_probability: number
  implied_probability: number
  edge_percentage: number
  expected_value: number
  bookmaker_odds: number
  recommended_stake_pct: number
  recommended_stake_amount: number
  confidence_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'VERY HIGH'
  reason?: string
  match_id?: string
  league?: string
  date?: string
}

export interface AnalysisResponse {
  success: boolean
  timestamp: string
  processing_time_ms: number
  total_matches_analyzed: number
  value_bets_found: number
  recommendations: BettingDecisionResponse[]
  portfolio_summary: {
    total_bets: number
    total_stake_amount: number
    percentage_of_bankroll: number
    average_odds: number
    average_edge: number
    average_expected_value: number
    confidence_distribution: Record<string, number>
  }
  settings: {
    bankroll: number
    kelly_fraction: number
    min_edge: number
    min_probability: number
    max_probability: number
  }
}

export interface ApiError {
  success: false
  error: string
  error_code: string
  timestamp: string
  details?: any
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      })

      const data = await response.json()

      if (!response.ok) {
        // Handle API errors
        if (response.status === 429) {
          throw new Error('API rate limit exceeded. Please try again later.')
        }
        throw new Error(data.error || `HTTP ${response.status}: ${response.statusText}`)
      }

      return data as T
    } catch (error) {
      if (error instanceof Error) {
        throw error
      }
      throw new Error('Unknown error occurred')
    }
  }

  async analyzeMatches(
    matches: MatchInput[],
    settings: {
      bankroll?: number
      kelly_fraction?: number
      min_edge?: number
      min_probability?: number
      max_probability?: number
    } = {}
  ): Promise<AnalysisResponse> {
    return this.request<AnalysisResponse>('/api/analyze-matches', {
      method: 'POST',
      body: JSON.stringify({
        matches,
        bankroll: settings.bankroll ?? 10000,
        kelly_fraction: settings.kelly_fraction ?? 0.25,
        min_edge: settings.min_edge ?? 0.05,
        min_probability: settings.min_probability ?? 0.35,
        max_probability: settings.max_probability ?? 0.75,
      }),
    })
  }

  async analyzeSingleMatch(
    match: MatchInput,
    bankroll: number = 10000,
    kelly_fraction: number = 0.25
  ): Promise<BettingDecisionResponse> {
    return this.request<BettingDecisionResponse>(
      `/api/analyze-single?bankroll=${bankroll}&kelly_fraction=${kelly_fraction}`,
      {
        method: 'POST',
        body: JSON.stringify(match),
      }
    )
  }

  async getPoissonAnalysis(
    home_xg: number,
    away_xg: number
  ): Promise<{
    success: boolean
    input: { home_xg: number; away_xg: number }
    probabilities: {
      home_win: number
      draw: number
      away_win: number
    }
    top_scores: Array<{ score: string; probability: number }>
    over_under_2_5: {
      over: number
      under: number
    }
  }> {
    return this.request(`/api/poisson-analysis?home_xg=${home_xg}&away_xg=${away_xg}`)
  }

  async calculateROR(
    win_probability: number,
    avg_odds: number,
    kelly_fraction: number,
    bankroll: number
  ): Promise<{
    success: boolean
    risk_of_ruin_percent: number
    risk_category: {
      level: string
      color: string
      message: string
    }
    suggested_kelly_fraction: number | null
  }> {
    return this.request('/api/calculate-ror', {
      method: 'POST',
      body: JSON.stringify({
        win_probability,
        avg_odds,
        kelly_fraction,
        bankroll,
      }),
    })
  }

  async runBacktest(
    bankroll: number,
    kelly_fraction: number,
    min_edge: number,
    num_matches: number = 50
  ): Promise<any> {
    return this.request('/api/backtest-simulation', {
      method: 'POST',
      body: JSON.stringify({
        bankroll,
        kelly_fraction,
        min_edge,
        num_matches,
      }),
    })
  }

  async healthCheck(): Promise<{
    status: string
    version: string
    timestamp: string
    uptime_seconds: number
  }> {
    return this.request('/api/health')
  }
}

export const api = new ApiClient()
