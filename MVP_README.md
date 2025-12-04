# 🎯 AlphaBet MVP - Instrukcja Użycia

## ✨ Co Nowego w MVP

Aplikacja jest teraz w pełni funkcjonalnym MVP, gdzie możesz:
- ✅ Dodawać mecze ręcznie
- ✅ Analizować value bets
- ✅ Zapisywać zakłady
- ✅ Dodawać wyniki (wygrana/przegrana)
- ✅ Śledzić wzrost kapitału
- ✅ Widzieć statystyki w czasie rzeczywistym

Wszystkie dane są zapisywane w **localStorage** przeglądarki - nic się nie traci!

---

## 🚀 Szybki Start

### 1. Uruchom Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

✅ Backend: http://localhost:8000

### 2. Uruchom Frontend

```bash
cd frontend
npm install
npm run dev
```

✅ Frontend: http://localhost:3000

---

## 📖 Workflow (Krok po Kroku)

### KROK 1: Dodaj Mecz

1. Kliknij **"Dodaj Mecz"** w prawym górnym rogu
2. Wypełnij formularz:
   - **Nazwa drużyn** (Home / Away)
   - **Średnie bramki** (strzelone / tracone)
   - **Kursy bukmacherskie** (1 / X / 2)
   - **Forma** (opcjonalnie): WWDLW
   - **xG** (opcjonalnie): Expected Goals
3. Kliknij **"Dodaj Mecz"**

✅ Mecz zostanie dodany do kolejki "Mecze do Analizy"

### KROK 2: Analizuj

1. Dodaj 1 lub więcej meczów
2. Kliknij **"Analizuj (X)"** gdzie X = liczba meczów
3. Poczekaj na analizę API

✅ System:
- Oblicza prawdopodobieństwa (model Poissona)
- Znajduje value bets (Edge > 5%)
- Oblicza optymalny stake (Kelly Criterion)
- Wyświetla rekomendacje w tabeli

### KROK 3: Postaw Zakład

1. Zobacz rekomendacje w zakładce **"Sygnały"**
2. Sprawdź:
   - **Edge %** (przewaga nad bukmacherem)
   - **EV** (Expected Value)
   - **Stake** (ile postawić)
   - **Confidence** (pewność sygnału)
3. Kliknij **"Postaw"** przy wybranym meczu

✅ Zakład zostanie zapisany w historii ze statusem **"Oczekuje"**

### KROK 4: Zapisz Wynik

1. Przejdź do zakładki **"Historia"**
2. Znajdź zakład ze statusem "Oczekuje"
3. Kliknij ikonę **ołówka** (Edit)
4. Opcjonalnie wpisz wynik meczu (np. "2:1")
5. Kliknij:
   - **Trofeum** (Trophy) = Wygrana
   - **Trend Down** = Przegrana

✅ System automatycznie:
- Przelicza profit/loss
- Aktualizuje bankroll
- Dodaje punkt do wykresu kapitału
- Aktualizuje statystyki

### KROK 5: Śledź Postępy

Dashboard pokazuje w czasie rzeczywistym:
- 💰 **Kapitał** (aktualny + ROI)
- 🎯 **Zakłady** (wygrane / przegrane)
- 📈 **Win Rate** (procent wygranych)
- 💵 **Total Profit** (całkowity zysk)

Wykres kapitału aktualizuje się po każdym zapisanym wyniku.

---

## 💡 Przykładowy Scenariusz

### Dzień 1: Dodajesz 3 mecze

```
1. Manchester City vs Arsenal
   - Home: 2.5 goli/mecz, traci 0.8
   - Away: 2.1 goli/mecz, traci 1.0
   - Kursy: 1.65 / 4.20 / 5.50

2. Real Madrid vs Barcelona
   - Home: 2.8 / 0.9
   - Away: 2.6 / 1.1
   - Kursy: 2.10 / 3.50 / 3.40

3. Liverpool vs Chelsea
   - Home: 2.4 / 0.9
   - Away: 1.9 / 1.3
   - Kursy: 1.85 / 3.80 / 4.20
```

### Analiza

System znajduje 2 value bets:
- Man City Home Win (Edge: 7.2%, Stake: 180 PLN)
- Liverpool Home Win (Edge: 5.8%, Stake: 140 PLN)

### Stawiasz zakłady

Klikasz "Postaw" na obu → Zapisane w historii

### Dzień 2: Wyniki

- Man City 3:1 Arsenal → **Wygrana** → +117 PLN
- Liverpool 1:1 Chelsea → **Przegrana** → -140 PLN

### Rezultat

- Kapitał: 10,000 → 9,977 PLN
- Total Profit: -23 PLN
- Win Rate: 50%
- Wykres: Pokazuje spadek, potem wzrost

---

## 📊 Funkcje Dashboard

### Karty Statystyk

1. **Kapitał**
   - Aktualny bankroll
   - ROI w %
   - Trend (zielony/czerwony)

2. **Zakłady**
   - Łączna liczba
   - Wygrane / Przegrane
   - Oczekujące

3. **Win Rate**
   - Procent wygranych
   - Liczba pending

4. **Total Profit**
   - Łączny zysk/strata
   - ROI w %

### Wykres Kapitału

- **Line chart** z gradientem
- **Tooltip** pokazuje:
  - Data
  - Kapitał
  - Profit/Loss
- **Glow effect** na linii
- **Auto-update** po każdym wyniku

### Tabela Sygnałów (Signals)

Kolumny:
- **Mecz** (nazwa + liga)
- **Zakład** (Home/Draw/Away)
- **Edge %** (heatmap: wyższe = jaśniejsze)
- **EV** (Expected Value)
- **Kurs**
- **Stake** (kwota + %)
- **Pewność** (LOW/MEDIUM/HIGH/VERY HIGH)

Funkcje:
- Sortowanie (kliknij nagłówek)
- Filtrowanie po lidze
- Hover effects

### Tabela Historia (History)

Kolumny:
- **Data** (dzień + godzina)
- **Mecz** (+ wynik jeśli podany)
- **Typ** (badge kolorowy)
- **Kurs** (monospace)
- **Stake**
- **Status** (pending/won/lost)
- **Profit/Loss** (zielony/czerwony)

Akcje:
- **Edit** (ołówek) - zapisz wynik
- **Delete** (kosz) - usuń zakład

---

## 🔧 Zaawansowane Funkcje

### localStorage Keys

Dane są zapisywane w przeglądarce pod kluczami:
- `alphabet_bet_history` - Historia zakładów
- `alphabet_settings` - Ustawienia użytkownika
- `alphabet_capital_history` - Historia kapitału

Możesz je sprawdzić w DevTools → Application → Local Storage

### Reset Danych

Jeśli chcesz zacząć od nowa, otwórz Console (F12) i wpisz:

```javascript
localStorage.clear()
location.reload()
```

Albo zmodyfikuj `storage.ts` i dodaj funkcję reset w UI.

### Ustawienia (Settings)

Domyślne:
- Bankroll: 10,000 PLN
- Kelly Fraction: 0.25 (Quarter Kelly)
- Min Edge: 5%
- Min Probability: 35%
- Max Probability: 75%

Można je zmienić edytując w `storage.ts` lub dodając UI do ustawień.

---

## 🎨 UI/UX Features

### Toast Notifications

Komunikaty pojawiają się w prawym górnym rogu:
- ✅ **Sukces** (zielony): "Zakład dodany!"
- ❌ **Błąd** (czerwony): "Błąd API"
- ⚠️ **Warning** (pomarańczowy): "Brak meczów"
- ℹ️ **Info** (niebieski): "Zakład usunięty"

### Loading States

- **Skeleton screens** podczas ładowania
- **Spinner** na przyciskach
- **Animacja** na "Analizuj" (pulsowanie)

### Micro-interactions

- Hover effects na kartach
- Ripple effect na przyciskach
- Smooth animations (fade-in, slide)
- Heatmap na Edge %

---

## 🔌 Integracja z API (Przyszłość)

Obecnie mecze dodaje się ręcznie. W przyszłości można dodać:

### API-Football Integration

```typescript
// W AddMatchForm.tsx można dodać:
const fetchFromAPI = async (fixtureId: number) => {
  const response = await fetch(`https://api-football.com/v3/fixtures/${fixtureId}`)
  const data = await response.json()
  // Auto-fill form with API data
}
```

### Auto-Update Results

```typescript
// Można dodać cron job który sprawdza wyniki:
const checkResults = async () => {
  const pending = getBetHistory().filter(b => b.status === 'pending')
  for (const bet of pending) {
    const result = await fetchResult(bet.match_id)
    if (result.finished) {
      updateBetResult(bet.id, result.won ? 'won' : 'lost', result.score)
    }
  }
}
```

---

## 🐛 Troubleshooting

### Problem: Nie widzę danych po odświeżeniu

**Rozwiązanie**: localStorage może być zablokowany w trybie incognito. Użyj normalnej przeglądarki.

### Problem: Backend nie działa

**Rozwiązanie**: Sprawdź czy port 8000 jest wolny:
```bash
lsof -i :8000
kill -9 <PID>
uvicorn main:app --reload
```

### Problem: Frontend nie łączy się z backendem

**Rozwiązanie**: Sprawdź CORS i API_URL:
```bash
# W frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Problem: Statystyki się nie aktualizują

**Rozwiązanie**: Kliknij "Odśwież" w prawym górnym rogu lub F5.

---

## 📈 Roadmap (Co Dalej?)

### Faza 1: MVP ✅ (DONE)
- ✅ Manual match entry
- ✅ localStorage persistence
- ✅ Bet tracking
- ✅ Result recording
- ✅ Capital tracking

### Faza 2: Enhancements (TODO)
- ⬜ Settings panel (edit Kelly, min edge, etc.)
- ⬜ Export data (CSV/JSON)
- ⬜ Import historical data
- ⬜ Confidence Score display
- ⬜ Risk of Ruin calculator UI

### Faza 3: API Integration (TODO)
- ⬜ API-Football connector
- ⬜ Auto-fetch matches
- ⬜ Auto-update results
- ⬜ Live odds tracking

### Faza 4: Advanced (TODO)
- ⬜ Backtesting simulator UI
- ⬜ Strategy comparison
- ⬜ Machine learning predictions
- ⬜ Mobile app (React Native)

---

## 🎉 Podsumowanie

AlphaBet MVP jest teraz w pełni funkcjonalną aplikacją do:
- ✅ Analizowania meczów
- ✅ Znajdowania value bets
- ✅ Śledzenia zakładów
- ✅ Monitorowania kapitału
- ✅ Obliczania statystyk

**Workflow jest prosty**:
1. Dodaj mecze
2. Analizuj
3. Postaw zakłady
4. Zapisz wyniki
5. Śledź wzrost kapitału

**Wszystko działa offline** - dane w localStorage!

---

## 📚 Dodatkowe Zasoby

- **README.md** - Oryginalny system PROPHET-70
- **FRONTEND_DOCUMENTATION.md** - Dokumentacja UI/UX
- **QUICKSTART.md** - 5-minutowy setup
- **IMPROVEMENTS_SUMMARY.md** - Changelog

---

**Enjoy responsible betting with math! 🎲📊**

*AlphaBet MVP - Where Analysis Meets Reality* ✨
