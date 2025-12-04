'use client'

/**
 * Form to add a new match for analysis
 */

import React, { useState } from 'react'
import { X, Plus } from 'lucide-react'
import { MatchInput } from '@/lib/api'

interface AddMatchFormProps {
  onSubmit: (match: MatchInput) => void
  onCancel: () => void
}

export function AddMatchForm({ onSubmit, onCancel }: AddMatchFormProps) {
  const [formData, setFormData] = useState<MatchInput>({
    match_name: '',
    league: '',
    home_team: {
      name: '',
      goals_scored_avg: 0,
      goals_conceded_avg: 0,
      form: '',
    },
    away_team: {
      name: '',
      goals_scored_avg: 0,
      goals_conceded_avg: 0,
      form: '',
    },
    odds_home: 2.0,
    odds_draw: 3.5,
    odds_away: 3.0,
    home_xg: undefined,
    away_xg: undefined,
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Auto-generate match name if empty
    const matchName =
      formData.match_name ||
      `${formData.home_team.name} vs ${formData.away_team.name}`

    onSubmit({
      ...formData,
      match_name: matchName,
    })
  }

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="card p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-text-primary">Dodaj Mecz</h2>
          <button
            onClick={onCancel}
            className="text-text-muted hover:text-text-primary transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Match Info */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-text-primary">
              Informacje o Meczu
            </h3>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-text-secondary mb-1">
                  Liga (opcjonalnie)
                </label>
                <input
                  type="text"
                  className="input w-full"
                  placeholder="Premier League"
                  value={formData.league}
                  onChange={(e) =>
                    setFormData({ ...formData, league: e.target.value })
                  }
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-1">
                  Nazwa Meczu (auto)
                </label>
                <input
                  type="text"
                  className="input w-full"
                  placeholder="Auto-generowane"
                  value={formData.match_name}
                  onChange={(e) =>
                    setFormData({ ...formData, match_name: e.target.value })
                  }
                />
              </div>
            </div>
          </div>

          {/* Home Team */}
          <div className="space-y-4 border-t border-neutral-dark pt-4">
            <h3 className="text-lg font-semibold text-success">
              Gospodarze (Home)
            </h3>

            <div>
              <label className="block text-sm text-text-secondary mb-1">
                Nazwa Drużyny *
              </label>
              <input
                type="text"
                className="input w-full"
                placeholder="Manchester City"
                value={formData.home_team.name}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    home_team: { ...formData.home_team, name: e.target.value },
                  })
                }
                required
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm text-text-secondary mb-1">
                  Śr. Bramek Strzela *
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="10"
                  className="input w-full font-mono"
                  value={formData.home_team.goals_scored_avg || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      home_team: {
                        ...formData.home_team,
                        goals_scored_avg: parseFloat(e.target.value) || 0,
                      },
                    })
                  }
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-1">
                  Śr. Bramek Traci *
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="10"
                  className="input w-full font-mono"
                  value={formData.home_team.goals_conceded_avg || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      home_team: {
                        ...formData.home_team,
                        goals_conceded_avg: parseFloat(e.target.value) || 0,
                      },
                    })
                  }
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-1">
                  Forma (WWDLW)
                </label>
                <input
                  type="text"
                  className="input w-full font-mono"
                  placeholder="WWDWL"
                  maxLength={10}
                  value={formData.home_team.form}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      home_team: {
                        ...formData.home_team,
                        form: e.target.value.toUpperCase(),
                      },
                    })
                  }
                />
              </div>
            </div>
          </div>

          {/* Away Team */}
          <div className="space-y-4 border-t border-neutral-dark pt-4">
            <h3 className="text-lg font-semibold text-warning">
              Goście (Away)
            </h3>

            <div>
              <label className="block text-sm text-text-secondary mb-1">
                Nazwa Drużyny *
              </label>
              <input
                type="text"
                className="input w-full"
                placeholder="Arsenal"
                value={formData.away_team.name}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    away_team: { ...formData.away_team, name: e.target.value },
                  })
                }
                required
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm text-text-secondary mb-1">
                  Śr. Bramek Strzela *
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="10"
                  className="input w-full font-mono"
                  value={formData.away_team.goals_scored_avg || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      away_team: {
                        ...formData.away_team,
                        goals_scored_avg: parseFloat(e.target.value) || 0,
                      },
                    })
                  }
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-1">
                  Śr. Bramek Traci *
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="10"
                  className="input w-full font-mono"
                  value={formData.away_team.goals_conceded_avg || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      away_team: {
                        ...formData.away_team,
                        goals_conceded_avg: parseFloat(e.target.value) || 0,
                      },
                    })
                  }
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-1">
                  Forma (WWDLW)
                </label>
                <input
                  type="text"
                  className="input w-full font-mono"
                  placeholder="WDWDL"
                  maxLength={10}
                  value={formData.away_team.form}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      away_team: {
                        ...formData.away_team,
                        form: e.target.value.toUpperCase(),
                      },
                    })
                  }
                />
              </div>
            </div>
          </div>

          {/* Odds */}
          <div className="space-y-4 border-t border-neutral-dark pt-4">
            <h3 className="text-lg font-semibold text-text-primary">
              Kursy Bukmacherskie
            </h3>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm text-text-secondary mb-1">
                  1 (Home Win) *
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="1.01"
                  max="100"
                  className="input w-full font-mono text-lg"
                  value={formData.odds_home || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      odds_home: parseFloat(e.target.value) || 2.0,
                    })
                  }
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-1">
                  X (Draw) *
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="1.01"
                  max="100"
                  className="input w-full font-mono text-lg"
                  value={formData.odds_draw || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      odds_draw: parseFloat(e.target.value) || 3.5,
                    })
                  }
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-1">
                  2 (Away Win) *
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="1.01"
                  max="100"
                  className="input w-full font-mono text-lg"
                  value={formData.odds_away || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      odds_away: parseFloat(e.target.value) || 3.0,
                    })
                  }
                  required
                />
              </div>
            </div>
          </div>

          {/* Expected Goals (Optional) */}
          <div className="space-y-4 border-t border-neutral-dark pt-4">
            <h3 className="text-lg font-semibold text-text-primary">
              Expected Goals (opcjonalnie)
            </h3>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-text-secondary mb-1">
                  xG Gospodarzy
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="6"
                  className="input w-full font-mono"
                  placeholder="2.3"
                  value={formData.home_xg || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      home_xg: e.target.value ? parseFloat(e.target.value) : undefined,
                    })
                  }
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-1">
                  xG Gości
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="6"
                  className="input w-full font-mono"
                  placeholder="1.1"
                  value={formData.away_xg || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      away_xg: e.target.value ? parseFloat(e.target.value) : undefined,
                    })
                  }
                />
              </div>
            </div>

            <p className="text-xs text-text-muted">
              Jeśli nie podasz xG, system użyje średnich bramek do obliczeń
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-4 pt-4">
            <button
              type="button"
              onClick={onCancel}
              className="btn btn-secondary flex-1"
            >
              Anuluj
            </button>
            <button type="submit" className="btn btn-primary flex-1 flex items-center justify-center gap-2">
              <Plus className="w-4 h-4" />
              Dodaj Mecz
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
