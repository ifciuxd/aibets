"""
Moduły pomocnicze - narzędzia do pobierania danych i integracji z API
"""

import json
import requests
from typing import List, Dict, Optional
from datetime import datetime
from .data_models import Match, TeamStats


class DataFetcher:
    """
    Wrapper do pobierania danych z różnych źródeł

    Obsługiwane API:
    - API-Football (https://www.api-football.com/)
    - The Odds API (https://the-odds-api.com/)
    - Football-Data.org (https://www.football-data.org/)
    """

    def __init__(self, api_key: Optional[str] = None, api_source: str = "api-football"):
        """
        Args:
            api_key: Klucz API (opcjonalny dla demo)
            api_source: Źródło danych ("api-football", "odds-api", "football-data")
        """
        self.api_key = api_key
        self.api_source = api_source
        self.base_urls = {
            "api-football": "https://v3.football.api-sports.io",
            "odds-api": "https://api.the-odds-api.com/v4",
            "football-data": "https://api.football-data.org/v4"
        }

    def fetch_matches(self, league_id: int, date: str = None) -> List[Dict]:
        """
        Pobiera listę meczów z API (demonstracja - wymaga prawdziwego API key)

        Args:
            league_id: ID ligi (np. 39 = Premier League)
            date: Data w formacie YYYY-MM-DD

        Returns:
            List[Dict]: Lista meczów
        """
        if not self.api_key:
            raise ValueError("API key jest wymagany. Zarejestruj się na API-Football")

        # To jest przykład - potrzebujesz prawdziwego API key
        headers = {
            "x-apisports-key": self.api_key
        }

        params = {
            "league": league_id,
            "season": datetime.now().year
        }

        if date:
            params["date"] = date

        try:
            response = requests.get(
                f"{self.base_urls[self.api_source]}/fixtures",
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("response", [])
        except Exception as e:
            print(f"Błąd pobierania danych: {e}")
            return []

    def fetch_odds(self, fixture_id: int) -> Dict:
        """
        Pobiera kursy dla meczu

        Args:
            fixture_id: ID meczu

        Returns:
            Dict: Kursy bukmacherskie
        """
        if not self.api_key:
            raise ValueError("API key jest wymagany")

        headers = {"x-apisports-key": self.api_key}

        try:
            response = requests.get(
                f"{self.base_urls[self.api_source]}/odds",
                headers=headers,
                params={"fixture": fixture_id},
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("response", {})
        except Exception as e:
            print(f"Błąd pobierania kursów: {e}")
            return {}


class DataParser:
    """Konwerter danych z różnych formatów do obiektów Match"""

    @staticmethod
    def from_json_file(file_path: str) -> List[Match]:
        """
        Wczytuje mecze z pliku JSON

        Args:
            file_path: Ścieżka do pliku JSON

        Returns:
            List[Match]: Lista obiektów Match
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        matches = []
        for item in data:
            match = Match(
                match_id=item.get("match_id"),
                match_name=item["match_name"],
                date=datetime.fromisoformat(item["date"]) if "date" in item else None,
                league=item.get("league"),
                home_team=TeamStats(**item["home_team"]),
                away_team=TeamStats(**item["away_team"]),
                odds_home=item["odds_home"],
                odds_draw=item["odds_draw"],
                odds_away=item["odds_away"],
                home_xg=item.get("home_xg"),
                away_xg=item.get("away_xg")
            )
            matches.append(match)

        return matches

    @staticmethod
    def from_csv(file_path: str) -> List[Match]:
        """
        Wczytuje mecze z pliku CSV

        Args:
            file_path: Ścieżka do pliku CSV

        Returns:
            List[Match]: Lista obiektów Match
        """
        import pandas as pd

        df = pd.read_csv(file_path)

        matches = []
        for _, row in df.iterrows():
            match = Match(
                match_name=row["match_name"],
                home_team=TeamStats(
                    name=row["home_team"],
                    goals_scored_avg=row["home_goals_avg"],
                    goals_conceded_avg=row["home_conceded_avg"]
                ),
                away_team=TeamStats(
                    name=row["away_team"],
                    goals_scored_avg=row["away_goals_avg"],
                    goals_conceded_avg=row["away_conceded_avg"]
                ),
                odds_home=row["odds_home"],
                odds_draw=row["odds_draw"],
                odds_away=row["odds_away"],
                home_xg=row.get("home_xg"),
                away_xg=row.get("away_xg")
            )
            matches.append(match)

        return matches

    @staticmethod
    def to_csv(matches: List[Match], output_path: str):
        """Eksportuje mecze do CSV"""
        import pandas as pd

        data = []
        for match in matches:
            data.append({
                "match_name": match.match_name,
                "home_team": match.home_team.name,
                "away_team": match.away_team.name,
                "home_goals_avg": match.home_team.goals_scored_avg,
                "home_conceded_avg": match.home_team.goals_conceded_avg,
                "away_goals_avg": match.away_team.goals_scored_avg,
                "away_conceded_avg": match.away_team.goals_conceded_avg,
                "odds_home": match.odds_home,
                "odds_draw": match.odds_draw,
                "odds_away": match.odds_away,
                "home_xg": match.home_xg,
                "away_xg": match.away_xg
            })

        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)


def calculate_team_form_score(form: str) -> float:
    """
    Oblicza score formy drużyny z ostatnich meczów

    Args:
        form: String typu "WWDLW" (W=Win, D=Draw, L=Loss)

    Returns:
        float: Score od 0 do 3 (3 = doskonała forma)
    """
    if not form:
        return 1.5  # Neutral

    points = {"W": 3, "D": 1, "L": 0}
    total = sum(points.get(result, 0) for result in form)
    return total / len(form)


def implied_probability_from_odds(odds: float) -> float:
    """
    Konwertuje kurs na prawdopodobieństwo implikowane

    Args:
        odds: Kurs bukmachera (np. 2.5)

    Returns:
        float: Prawdopodobieństwo (0-1)
    """
    return 1 / odds


def calculate_bookmaker_margin(odds_home: float, odds_draw: float, odds_away: float) -> float:
    """
    Oblicza marżę bukmachera (overround)

    Args:
        odds_home, odds_draw, odds_away: Kursy na wszystkie wyniki

    Returns:
        float: Marża w % (np. 5.5 = 5.5% marży)
    """
    implied_probs_sum = (1/odds_home) + (1/odds_draw) + (1/odds_away)
    margin = (implied_probs_sum - 1) * 100
    return round(margin, 2)


def fair_odds_from_probability(probability: float, remove_margin: bool = False, margin: float = 0.05) -> float:
    """
    Konwertuje prawdopodobieństwo na 'fair odds'

    Args:
        probability: Prawdopodobieństwo (0-1)
        remove_margin: Czy usunąć marżę bukmachera
        margin: Marża do usunięcia (domyślnie 5%)

    Returns:
        float: Kurs
    """
    if remove_margin:
        adjusted_prob = probability * (1 + margin)
    else:
        adjusted_prob = probability

    return 1 / adjusted_prob
