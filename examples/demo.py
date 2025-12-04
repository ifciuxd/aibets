#!/usr/bin/env python3
"""
PROPHET-70 Betting System - Demo
Przykład użycia systemu analizy kuponów bukmacherskich
"""

import sys
import os

# Dodaj ścieżkę do modułu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from betting_system import ProphetSystem
from betting_system.utils import DataParser
from betting_system.data_models import Match, TeamStats


def demo_basic_usage():
    """Przykład 1: Podstawowe użycie z pojedynczym meczem"""
    print("=" * 80)
    print("PROPHET-70 BETTING SYSTEM - Demo")
    print("=" * 80)
    print()

    # Inicjalizuj system z bankrollem 10,000 PLN
    system = ProphetSystem(
        bankroll=10000,
        kelly_fraction=0.25,  # Quarter Kelly (bezpieczne)
        min_edge=0.05,  # Minimum 5% przewagi
        min_probability=0.35,  # Nie stawiaj na longshoty
        max_probability=0.75  # Nie stawiaj na faworytów z bardzo niskimi kursami
    )

    print(f"💰 Bankroll: {system.bankroll:,.2f} PLN")
    print(f"📊 Kelly Fraction: {system.kelly_fraction} (Quarter Kelly)")
    print(f"🎯 Min Edge: {system.min_edge * 100}%")
    print()

    # Przykładowy mecz
    match = Match(
        match_name="Manchester City vs Arsenal",
        home_team=TeamStats(
            name="Manchester City",
            goals_scored_avg=2.5,
            goals_conceded_avg=0.8,
            form="WWWDW"
        ),
        away_team=TeamStats(
            name="Arsenal",
            goals_scored_avg=2.1,
            goals_conceded_avg=1.0,
            form="WWDWL"
        ),
        odds_home=1.65,
        odds_draw=4.20,
        odds_away=5.50,
        home_xg=2.3,
        away_xg=1.1
    )

    print(f"⚽ Analizuję mecz: {match.match_name}")
    print(f"   🏠 Gospodarze: {match.home_team.name} (avg: {match.home_team.goals_scored_avg} goli/mecz)")
    print(f"   ✈️  Goście: {match.away_team.name} (avg: {match.away_team.goals_scored_avg} goli/mecz)")
    print(f"   📈 Kursy: {match.odds_home} / {match.odds_draw} / {match.odds_away}")
    print()

    # Analizuj
    decision = system.analyze_match(match)

    # Wyświetl wyniki
    print("=" * 80)
    print("DECYZJA SYSTEMU")
    print("=" * 80)

    if decision.recommended_bet == "NO BET":
        print("❌ NO BET")
        print(f"   Powód: {decision.reason}")
    else:
        print(f"✅ REKOMENDACJA: {decision.recommended_bet}")
        print(f"   🎲 Prawdopodobieństwo (model): {decision.model_probability * 100:.1f}%")
        print(f"   🎲 Prawdopodobieństwo (bukmacher): {decision.implied_probability * 100:.1f}%")
        print(f"   📊 Przewaga (Edge): {decision.edge_percentage:.2f}%")
        print(f"   💹 Expected Value: {decision.expected_value:.4f}")
        print(f"   💰 Kurs: {decision.bookmaker_odds}")
        print(f"   💵 Stake: {decision.recommended_stake_amount:.2f} PLN ({decision.recommended_stake_pct * 100:.2f}% bankrolla)")
        print(f"   ⭐ Pewność: {decision.confidence_level}")
        print(f"   📝 {decision.reason}")

    print()


def demo_multiple_matches():
    """Przykład 2: Analiza wielu meczów z pliku JSON"""
    print("=" * 80)
    print("ANALIZA WIELU MECZÓW")
    print("=" * 80)
    print()

    # Wczytaj dane z pliku
    json_path = os.path.join(os.path.dirname(__file__), 'sample_matches.json')
    matches = DataParser.from_json_file(json_path)

    print(f"📂 Wczytano {len(matches)} meczów z pliku: sample_matches.json")
    print()

    # Inicjalizuj system
    system = ProphetSystem(
        bankroll=10000,
        kelly_fraction=0.25,
        min_edge=0.05
    )

    # Analizuj wszystkie mecze
    results_df = system.analyze_matches(matches)

    if results_df.empty:
        print("❌ Nie znaleziono żadnych zakładów spełniających kryteria")
        return

    print(f"✅ Znaleziono {len(results_df)} wartościowych zakładów:")
    print()

    # Wyświetl top 5 zakładów
    print("TOP 5 NAJLEPSZYCH ZAKŁADÓW:")
    print("-" * 120)
    print(f"{'Rank':<5} {'Mecz':<35} {'Zakład':<12} {'Edge':<8} {'EV':<8} {'Kurs':<6} {'Stake':<10} {'Pewność':<10}")
    print("-" * 120)

    for _, row in results_df.head(5).iterrows():
        print(
            f"{int(row['rank']):<5} "
            f"{row['match_name']:<35} "
            f"{row['recommended_bet']:<12} "
            f"{row['edge_percentage']:>6.2f}% "
            f"{row['expected_value']:>7.4f} "
            f"{row['bookmaker_odds']:>6.2f} "
            f"{row['recommended_stake_amount']:>9.2f} "
            f"{row['confidence_level']:<10}"
        )

    print("-" * 120)
    print()

    # Podsumowanie portfela
    summary = system.get_portfolio_summary()
    print("=" * 80)
    print("PODSUMOWANIE PORTFELA")
    print("=" * 80)
    print(f"📊 Liczba zakładów: {summary['total_bets']}")
    print(f"💰 Całkowity stake: {summary['total_stake_amount']:,.2f} PLN ({summary['percentage_of_bankroll']:.2f}% bankrolla)")
    print(f"📈 Średni kurs: {summary['average_odds']:.2f}")
    print(f"📊 Średnia przewaga: {summary['average_edge']:.2f}%")
    print(f"💹 Średni EV: {summary['average_expected_value']:.4f}")
    print()
    print("Rozkład pewności:")
    for level, count in summary['confidence_distribution'].items():
        if count > 0:
            print(f"   {level}: {count} zakładów")
    print()


def demo_kelly_comparison():
    """Przykład 3: Porównanie różnych strategii stakingu"""
    print("=" * 80)
    print("PORÓWNANIE STRATEGII STAKINGU")
    print("=" * 80)
    print()

    from betting_system.kelly_criterion import KellyCriterion

    # Przykładowy zakład
    true_probability = 0.58  # 58% szans na wygraną
    odds = 1.95  # Kurs bukmachera
    bankroll = 10000

    print(f"Scenariusz: Prawdopodobieństwo = {true_probability*100:.0f}%, Kurs = {odds}")
    print()

    strategies = {
        "Full Kelly": 1.0,
        "Half Kelly": 0.5,
        "Quarter Kelly (zalecane)": 0.25,
        "Flat 2%": None
    }

    for name, fraction in strategies.items():
        if fraction:
            kelly = KellyCriterion(fraction=fraction)
            result = kelly.calculate_stake(true_probability, odds, bankroll)
            print(f"{name}:")
            print(f"   Stake: {result['stake_amount']:.2f} PLN ({result['kelly_percentage']*100:.2f}%)")
            print(f"   Edge: {result['edge_percentage']:.2f}%")
            print(f"   EV: {result['expected_value']:.4f}")
        else:
            print(f"{name}:")
            print(f"   Stake: {bankroll * 0.02:.2f} PLN (2.00%)")
            print(f"   (Stała kwota niezależnie od value)")
        print()


def demo_poisson_analysis():
    """Przykład 4: Szczegółowa analiza Poissona"""
    print("=" * 80)
    print("ANALIZA MODELU POISSONA")
    print("=" * 80)
    print()

    from betting_system.poisson_model import PoissonFootballModel

    model = PoissonFootballModel(max_goals=6)

    # Przykład: Real Madrid vs Barcelona
    home_xg = 2.4
    away_xg = 1.8

    print(f"Mecz: Real Madrid vs Barcelona")
    print(f"Expected Goals (xG): {home_xg} vs {away_xg}")
    print()

    # Oblicz prawdopodobieństwa
    p_home, p_draw, p_away = model.calculate_from_expected_goals(home_xg, away_xg)

    print("Prawdopodobieństwa wyników:")
    print(f"   🏠 Wygrana gospodarzy: {p_home*100:.2f}%")
    print(f"   🤝 Remis: {p_draw*100:.2f}%")
    print(f"   ✈️  Wygrana gości: {p_away*100:.2f}%")
    print()

    # Najczęstsze wyniki
    scores = model.get_score_probabilities(home_xg, away_xg, top_n=8)
    print("8 najbardziej prawdopodobnych wyników:")
    for i, (score, prob) in enumerate(scores.items(), 1):
        print(f"   {i}. {score[0]}:{score[1]} - {prob*100:.2f}%")
    print()

    # Over/Under
    p_over, p_under = model.calculate_over_under_probability(home_xg, away_xg, threshold=2.5)
    print("Over/Under 2.5:")
    print(f"   Over 2.5: {p_over*100:.2f}%")
    print(f"   Under 2.5: {p_under*100:.2f}%")
    print()


if __name__ == "__main__":
    # Uruchom wszystkie demo
    demo_basic_usage()
    print("\n" * 2)
    demo_multiple_matches()
    print("\n" * 2)
    demo_kelly_comparison()
    print("\n" * 2)
    demo_poisson_analysis()

    print("=" * 80)
    print("KONIEC DEMONSTRACJI")
    print("=" * 80)
    print()
    print("📚 Więcej informacji w README.md")
    print("🔧 Aby używać z prawdziwymi danymi, skonfiguruj API w config/api_keys.json")
    print()
