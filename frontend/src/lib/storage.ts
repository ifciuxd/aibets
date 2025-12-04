/**
 * LocalStorage utilities for persisting betting data
 */

export interface BetHistory {
  id: string
  date: string
  match_name: string
  bet_type: string
  odds: number
  stake: number
  status: 'pending' | 'won' | 'lost'
  profit: number
  match_result?: string  // e.g., "2:1"
}

export interface UserSettings {
  bankroll: number
  initial_bankroll: number
  kelly_fraction: number
  min_edge: number
  min_probability: number
  max_probability: number
}

const KEYS = {
  BET_HISTORY: 'alphabet_bet_history',
  SETTINGS: 'alphabet_settings',
  CAPITAL_HISTORY: 'alphabet_capital_history',
}

// Default settings
const DEFAULT_SETTINGS: UserSettings = {
  bankroll: 10000,
  initial_bankroll: 10000,
  kelly_fraction: 0.25,
  min_edge: 0.05,
  min_probability: 0.35,
  max_probability: 0.75,
}

// Bet History
export const getBetHistory = (): BetHistory[] => {
  if (typeof window === 'undefined') return []
  const data = localStorage.getItem(KEYS.BET_HISTORY)
  return data ? JSON.parse(data) : []
}

export const saveBetHistory = (history: BetHistory[]) => {
  if (typeof window === 'undefined') return
  localStorage.setItem(KEYS.BET_HISTORY, JSON.stringify(history))
}

export const addBet = (bet: Omit<BetHistory, 'id'>) => {
  const history = getBetHistory()
  const newBet: BetHistory = {
    ...bet,
    id: `bet_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
  }
  history.push(newBet)
  saveBetHistory(history)
  return newBet
}

export const updateBetResult = (
  betId: string,
  status: 'won' | 'lost',
  match_result?: string
) => {
  const history = getBetHistory()
  const betIndex = history.findIndex((b) => b.id === betId)

  if (betIndex === -1) return null

  const bet = history[betIndex]

  // Calculate profit
  let profit = 0
  if (status === 'won') {
    profit = bet.stake * (bet.odds - 1)
  } else {
    profit = -bet.stake
  }

  history[betIndex] = {
    ...bet,
    status,
    profit,
    match_result,
  }

  saveBetHistory(history)

  // Update bankroll
  const settings = getSettings()
  settings.bankroll += profit
  saveSettings(settings)

  // Update capital history
  addCapitalHistoryPoint(settings.bankroll, profit)

  return history[betIndex]
}

export const deleteBet = (betId: string) => {
  const history = getBetHistory().filter((b) => b.id !== betId)
  saveBetHistory(history)
}

// Settings
export const getSettings = (): UserSettings => {
  if (typeof window === 'undefined') return DEFAULT_SETTINGS
  const data = localStorage.getItem(KEYS.SETTINGS)
  return data ? JSON.parse(data) : DEFAULT_SETTINGS
}

export const saveSettings = (settings: UserSettings) => {
  if (typeof window === 'undefined') return
  localStorage.setItem(KEYS.SETTINGS, JSON.stringify(settings))
}

export const resetBankroll = (newBankroll: number) => {
  const settings = getSettings()
  settings.bankroll = newBankroll
  settings.initial_bankroll = newBankroll
  saveSettings(settings)

  // Reset capital history
  const history: CapitalHistoryPoint[] = [
    {
      date: new Date().toISOString(),
      capital: newBankroll,
      profit: 0,
    },
  ]
  saveCapitalHistory(history)
}

// Capital History
export interface CapitalHistoryPoint {
  date: string
  capital: number
  profit: number
}

export const getCapitalHistory = (): CapitalHistoryPoint[] => {
  if (typeof window === 'undefined') return []
  const data = localStorage.getItem(KEYS.CAPITAL_HISTORY)

  if (!data) {
    // Initialize with current bankroll
    const settings = getSettings()
    const initial: CapitalHistoryPoint[] = [
      {
        date: new Date().toISOString(),
        capital: settings.bankroll,
        profit: 0,
      },
    ]
    saveCapitalHistory(initial)
    return initial
  }

  return JSON.parse(data)
}

export const saveCapitalHistory = (history: CapitalHistoryPoint[]) => {
  if (typeof window === 'undefined') return
  localStorage.setItem(KEYS.CAPITAL_HISTORY, JSON.stringify(history))
}

export const addCapitalHistoryPoint = (capital: number, profit: number) => {
  const history = getCapitalHistory()
  history.push({
    date: new Date().toISOString(),
    capital,
    profit,
  })

  // Keep last 100 points
  if (history.length > 100) {
    history.shift()
  }

  saveCapitalHistory(history)
}

// Stats
export const getStats = () => {
  const history = getBetHistory()
  const settings = getSettings()

  const totalBets = history.length
  const wonBets = history.filter((b) => b.status === 'won').length
  const lostBets = history.filter((b) => b.status === 'lost').length
  const pendingBets = history.filter((b) => b.status === 'pending').length

  const totalProfit = history.reduce((sum, b) => sum + b.profit, 0)
  const totalStaked = history.reduce((sum, b) => sum + b.stake, 0)

  const winRate = totalBets > 0 ? (wonBets / (wonBets + lostBets)) * 100 : 0
  const roi = totalStaked > 0 ? (totalProfit / totalStaked) * 100 : 0

  const avgOdds = totalBets > 0
    ? history.reduce((sum, b) => sum + b.odds, 0) / totalBets
    : 0

  const currentProfit = settings.bankroll - settings.initial_bankroll
  const currentRoi = (currentProfit / settings.initial_bankroll) * 100

  return {
    totalBets,
    wonBets,
    lostBets,
    pendingBets,
    winRate,
    totalProfit,
    totalStaked,
    roi,
    avgOdds,
    currentBankroll: settings.bankroll,
    initialBankroll: settings.initial_bankroll,
    currentProfit,
    currentRoi,
  }
}

// Clear all data
export const clearAllData = () => {
  if (typeof window === 'undefined') return
  localStorage.removeItem(KEYS.BET_HISTORY)
  localStorage.removeItem(KEYS.SETTINGS)
  localStorage.removeItem(KEYS.CAPITAL_HISTORY)
}
