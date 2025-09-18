from typing import List, Optional, Tuple
from difflib import SequenceMatcher
from models.team import Team
from models.player import Player


class SearchService:
    def __init__(self, teams: List[Team]):
        self.teams = teams

    def _calculate_similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings."""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def find_team(self, team_name: str, threshold: float = 0.6) -> Optional[Team]:
        """Find a team by name with fuzzy matching."""
        best_match = None
        best_score = 0

        for team in self.teams:
            # Check full name
            score = self._calculate_similarity(team_name, team.name)
            if score > best_score and score >= threshold:
                best_match = team
                best_score = score

            # Check short name if available
            if team.short_name:
                score = self._calculate_similarity(team_name, team.short_name)
                if score > best_score and score >= threshold:
                    best_match = team
                    best_score = score

            # Check TLA if available
            if team.tla:
                score = self._calculate_similarity(team_name, team.tla)
                if score > best_score and score >= threshold:
                    best_match = team
                    best_score = score

        return best_match

    def find_player(self, player_name: str, threshold: float = 0.7) -> Optional[Tuple[Player, Team]]:
        """Find a player by name with fuzzy matching."""
        best_match = None
        best_team = None
        best_score = 0

        for team in self.teams:
            for player in team.squad:
                score = self._calculate_similarity(player_name, player.name)
                if score > best_score and score >= threshold:
                    best_match = player
                    best_team = team
                    best_score = score

        return (best_match, best_team) if best_match else None

    def find_players_by_team_and_position(self, team_name: str, position: str) -> List[Player]:
        """Find all players by position."""
        results = []
        team = self.find_team(team_name)
        if team is None:
            return []

        for player in team.squad:
            if player.position and position.lower() in player.position.lower():
                results.append(player)
        return results
