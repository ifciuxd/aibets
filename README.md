# 🎯 PROPHET-70 Betting System

**Profesjonalny system analizy kuponów bukmacherskich oparty na matematyce i statystyce**

System wykorzystuje:
- 📊 **Model Rozkładu Poissona** - do obliczania prawdopodobieństw wyników
- 💰 **Kryterium Kelly'ego** - do optymalnego zarządzania kapitałem
- 🎲 **Value Betting** - identyfikacja zakładów z przewagą nad bukmacherem
- 🔒 **Fractional Kelly** - bezpieczne zarządzanie ryzykiem

---

## ⚡ Szybki Start

### 1. Instalacja

```bash
# Klonuj repozytorium
git clone <repository-url>
cd aibets

# Zainstaluj zależności
pip install -r requirements.txt
```

### 2. Uruchom Demo

```bash
python examples/demo.py
```

Demo pokazuje:
- ✅ Analizę pojedynczego meczu
- ✅ Analizę wielu meczów z pliku JSON
- ✅ Porównanie strategii stakingu (Full Kelly vs Quarter Kelly)
- ✅ Szczegółową analizę modelu Poissona

---

## 📖 Jak działa system?

### Krok 1: Model Poissona oblicza prawdopodobieństwa

System używa rozkładu Poissona do przewidywania liczby bramek:

```
P(Home Win), P(Draw), P(Away Win) = f(xG_home, xG_away)
```

**Wejście:**
- Średnia strzelonych bramek drużyn
- Średnia straconych bramek
- Expected Goals (xG) - opcjonalnie

**Wyjście:**
- Prawdopodobieństwa dla każdego wyniku (1, X, 2)
- Macierz wyników (0:0, 1:0, 1:1, itd.)

### Krok 2: Identyfikacja Value Bets

System porównuje nasze prawdopodobieństwo z kursami bukmachera:

```
Edge = P(model) - P(implied from odds)
```

**Filtry bezpieczeństwa:**
- ✅ Edge > 5% (minimalna przewaga)
- ✅ Prawdopodobieństwo w zakresie 35-75%
- ✅ Edge < 30% (eliminacja nierealistycznych przewag)

### Krok 3: Kryterium Kelly'ego

Optymalne zarządzanie kapitałem:

```
f* = (b × p - q) / b
```

gdzie:
- `f*` = procent kapitału do postawienia
- `b` = kurs - 1
- `p` = nasze prawdopodobieństwo wygranej
- `q` = 1 - p

**Bezpieczeństwo:** System używa **Quarter Kelly** (25% pełnego Kelly) i limituje stake do max 10% bankrolla.

---

## 🔧 Podstawowe Użycie

### Przykład 1: Pojedynczy Mecz

```python
from betting_system import ProphetSystem
from betting_system.data_models import Match, TeamStats

# Inicjalizacja systemu
system = ProphetSystem(
    bankroll=10000,        # Kapitał w PLN
    kelly_fraction=0.25,   # Quarter Kelly (zalecane)
    min_edge=0.05,         # Min 5% przewagi
)

# Dane meczu
match = Match(
    match_name="Manchester City vs Arsenal",
    home_team=TeamStats(
        name="Manchester City",
        goals_scored_avg=2.5,
        goals_conceded_avg=0.8
    ),
    away_team=TeamStats(
        name="Arsenal",
        goals_scored_avg=2.1,
        goals_conceded_avg=1.0
    ),
    odds_home=1.65,
    odds_draw=4.20,
    odds_away=5.50,
    home_xg=2.3,  # Opcjonalnie
    away_xg=1.1
)

# Analiza
decision = system.analyze_match(match)

print(f"Rekomendacja: {decision.recommended_bet}")
print(f"Stake: {decision.recommended_stake_amount:.2f} PLN")
print(f"Edge: {decision.edge_percentage:.2f}%")
print(f"Expected Value: {decision.expected_value:.4f}")
```

### Przykład 2: Wiele Meczów z Pliku

```python
from betting_system import ProphetSystem
from betting_system.utils import DataParser

# Wczytaj mecze z JSON
matches = DataParser.from_json_file('examples/sample_matches.json')

# Inicjalizacja
system = ProphetSystem(bankroll=10000)

# Analizuj wszystkie i zwróć ranking
results_df = system.analyze_matches(matches)

# Top 5 najlepszych zakładów
print(results_df.head(5))

# Podsumowanie portfela
summary = system.get_portfolio_summary()
print(f"Całkowity stake: {summary['total_stake_amount']:.2f} PLN")
print(f"Średnia przewaga: {summary['average_edge']:.2f}%")
```

### Przykład 3: Własne Dane (CSV)

```python
from betting_system.utils import DataParser

# Wczytaj z CSV
matches = DataParser.from_csv('my_matches.csv')

# Format CSV (wymagane kolumny):
# match_name, home_team, away_team, home_goals_avg, home_conceded_avg,
# away_goals_avg, away_conceded_avg, odds_home, odds_draw, odds_away
```

---

## 📊 Struktura Projektu

```
aibets/
├── betting_system/          # Główny moduł
│   ├── __init__.py
│   ├── prophet_system.py    # Główna logika systemu
│   ├── poisson_model.py     # Model Poissona
│   ├── kelly_criterion.py   # Kryterium Kelly'ego
│   ├── data_models.py       # Modele danych (Pydantic)
│   └── utils.py             # Narzędzia pomocnicze
│
├── examples/                # Przykłady użycia
│   ├── demo.py              # Demonstracja wszystkich funkcji
│   └── sample_matches.json  # Przykładowe dane
│
├── tests/                   # Testy jednostkowe
│
├── data/                    # Dane (gitignored)
│   ├── raw/                 # Surowe dane
│   └── processed/           # Przetworzone dane
│
├── config/                  # Konfiguracja
│   └── api_keys.json        # Klucze API (gitignored)
│
├── requirements.txt         # Zależności
├── .gitignore
└── README.md               # Ta dokumentacja
```

---

## 🔌 Integracja z API (Zaawansowane)

System może pobierać dane z prawdziwych API:

### Wspierane API:
- 🔵 **API-Football** - https://www.api-football.com/
- 🟢 **The Odds API** - https://the-odds-api.com/
- 🟡 **Football-Data.org** - https://www.football-data.org/

### Konfiguracja:

1. Zarejestruj się i uzyskaj API key
2. Utwórz `config/api_keys.json`:

```json
{
  "api_football": "your-api-key-here",
  "odds_api": "your-api-key-here"
}
```

3. Użyj DataFetcher:

```python
from betting_system.utils import DataFetcher

fetcher = DataFetcher(
    api_key="your-key",
    api_source="api-football"
)

# Pobierz mecze z Premier League (ID: 39)
matches = fetcher.fetch_matches(league_id=39, date="2025-12-06")
```

⚠️ **Uwaga:** Darmowe plany API mają limity requestów (zazwyczaj 100/dzień).

---

## 📈 Strategie i Parametry

### Konfiguracja Systemu

```python
ProphetSystem(
    bankroll=10000,           # Twój kapitał
    kelly_fraction=0.25,      # 0.25 = Quarter Kelly (zalecane)
                              # 0.5 = Half Kelly (agresywniejsze)
                              # 1.0 = Full Kelly (bardzo agresywne, NIE zalecane)

    min_edge=0.05,            # Min 5% przewagi (wyższe = mniej zakładów, ale bezpieczniej)
    min_probability=0.35,     # Unikaj longshotów (zbyt niskie prawdopodobieństwo)
    max_probability=0.75,     # Unikaj faworytów z bardzo niskimi kursami
    league_avg_goals=2.7      # Średnia bramek w lidze (2.7 dla top 5 lig)
)
```

### Zalecenia dla Różnych Profili Ryzyka

| Profil | Kelly Fraction | Min Edge | Min Prob | Typ |
|--------|---------------|----------|----------|-----|
| **Konserwatywny** | 0.10-0.20 | 8-10% | 40% | Bezpieczny, niskie zyski |
| **Zbalansowany** ⭐ | 0.25 | 5% | 35% | Zalecany start |
| **Agresywny** | 0.30-0.40 | 3-5% | 30% | Wyższe ryzyko |
| **Bardzo Agresywny** ⚠️ | 0.50+ | 2-3% | 25% | Tylko dla doświadczonych |

---

## 🧪 Testowanie Strategii

### Symulacja Monte Carlo

```python
from betting_system.kelly_criterion import KellyCriterion

kelly = KellyCriterion(fraction=0.25)

# Symuluj 100 zakładów
result = kelly.simulate_kelly_growth(
    initial_bankroll=10000,
    win_rate=0.55,        # 55% wygranych
    avg_odds=2.0,         # Średni kurs 2.0
    num_bets=100,
    use_kelly=True        # True = Kelly, False = Flat 2%
)

print(f"ROI: {result['roi']}%")
print(f"Final: {result['final_bankroll']} PLN")
```

---

## ⚠️ Ważne Zastrzeżenia

### 🔴 Ryzyko i Odpowiedzialność

1. **To nie jest gwarancja zysku** - System matematyczny nie może przewidzieć przypadków (kontuzje, czerwone kartki, itp.)
2. **Bukmacher zawsze ma marżę** - Zazwyczaj 5-10% na każdy mecz
3. **Zakłady to hazard** - Nie stawiaj więcej niż możesz stracić
4. **Model ma ograniczenia**:
   - Nie uwzględnia kontekstu (motywacja, pogoda, zmęczenie)
   - Zakłada niezależność bramek (uproszczenie)
   - Wymaga dokładnych danych wejściowych

### 🟢 Dobre Praktyki

✅ **DO:**
- Zaczynaj od małego bankrolla (testuj strategię)
- Używaj Quarter Kelly (0.25) lub mniejszego
- Prowadź dokładną historię zakładów
- Aktualizuj dane regularnie
- Stawiaj tylko gdy masz >5% edge
- Traktuj jako długoterminową inwestycję

❌ **NIE:**
- Nie używaj Full Kelly (zbyt agresywne)
- Nie stawiaj na emocjach
- Nie gonisz strat
- Nie stawiaj pieniędzy, których potrzebujesz
- Nie ignoruj czerwonych flag (nierealistyczne edge >20%)

---

## 📚 Wiedza Teoretyczna

### Dlaczego Poisson?

Rozkład Poissona doskonale modeluje rzadkie, niezależne wydarzenia (jak bramki w piłce):

```
P(X = k) = (λ^k × e^(-λ)) / k!
```

gdzie `λ` (lambda) to oczekiwana liczba bramek.

**Zalety:**
- Sprawdza się empirycznie (badania akademickie)
- Prosta implementacja
- Dobre wyniki dla top lig

**Wady:**
- Nie uwzględnia korelacji (np. "otwarcie się meczu" po 1. bramce)
- Gorsze wyniki dla bardzo defensywnych zespołów

### Dlaczego Kelly Criterion?

Matematycznie optymalna strategia maksymalizująca wzrost logarytmiczny kapitału.

**Zalety:**
- Maksymalizuje długoterminowy wzrost
- Automatycznie skaluje stake z bankrollem
- Minimalizuje ryzyko ruiny

**Wady:**
- Full Kelly jest bardzo agresywny (duże wahania)
- Wymaga dokładnego prawdopodobieństwa (błąd = overbet)

**Rozwiązanie:** Fractional Kelly (25-50% pełnego Kelly)

---

## 🛠️ Development

### Uruchom Testy

```bash
pytest tests/ -v
```

### Zainstaluj w trybie deweloperskim

```bash
pip install -e .
```

### Dodaj nowe funkcje

System jest modularny - łatwo dodać:
- Nowe modele (np. Dixon-Coles zamiast Poissona)
- Nowe źródła danych
- Zaawansowane filtry
- Machine Learning

---

## 📖 Materiały Edukacyjne

### Artykuły Naukowe:
- Dixon & Coles (1997) - "Modelling Association Football Scores"
- Kelly (1956) - "A New Interpretation of Information Rate"
- Thorp (1969) - "Optimal Gambling Systems"

### Książki:
- "Trading and Exchanges" - Larry Harris
- "Fortune's Formula" - William Poundstone
- "The Kelly Capital Growth Investment Criterion" - MacLean, Thorp, Ziemba

### Online:
- https://www.pinnacle.com/en/betting-articles/betting-strategy
- https://www.football-data.co.uk/blog/

---

## 🤝 Contributing

Pull requesty mile widziane! Jeśli masz pomysły na:
- Nowe modele statystyczne
- Lepsze źródła danych
- Optymalizacje algorytmów

Otwórz issue lub wyślij PR.

---

## 📄 Licencja

MIT License - używaj na własną odpowiedzialność.

---

## 💬 FAQ

**Q: Czy to naprawdę działa?**
A: System ma solidne fundamenty matematyczne, ale nie gwarantuje zysków. Długoterminowy sukces zależy od jakości danych i dyscypliny.

**Q: Ile mogę zarobić?**
A: Realistyczne oczekiwania: 5-15% ROI rocznie (jeśli masz dobre dane i dyscyplinę). To mniej niż myślisz, ale stabilne.

**Q: Potrzebuję API?**
A: Nie na start - możesz używać własnych danych (CSV/JSON). API przydatne do automatyzacji.

**Q: Czy mogę użyć tego profesjonalnie?**
A: Tak, ale pamiętaj o limitach kont bukmacherskich (za dobre wyniki mogą zablokować konto).

**Q: Działa dla innych sportów?**
A: Model Poissona działa najlepiej dla piłki nożnej. Dla koszykówki/tenisa potrzeba innych modeli.

---

## 📞 Kontakt

Masz pytania? Otwórz issue na GitHubie.

**Powodzenia i stawiaj odpowiedzialnie! 🍀**

---

*Disclaimer: Ten projekt ma charakter edukacyjny. Autor nie ponosi odpowiedzialności za straty finansowe. Hazard może uzależniać - graj odpowiedzialnie.*
