from langchain.agents import Tool
from typing import List
from services.football_api_service import FootballAPIService
from services.search_service import SearchService
import json
import logging

logger = logging.getLogger(__name__)


class FootballTools:
    def __init__(self, search_service: SearchService):
        self.search_service = search_service

    def get_player_info(self, player_name: str) -> str:
        try:
            result = self.search_service.find_player(player_name)
            if not result:
                return f"No player found matching '{player_name}'."

            player, team = result
            player_info = {
                "Name": player.name,
                "Team": team.name if team else "N/A",
                "Position": player.position,
                "Date of Birth": player.date_of_birth,
                "Age": player.age,
                "Nationality": player.nationality
            }

            return json.dumps(player_info, indent=2)

        except Exception as e:
            logger.error(f"Error retrieving player info: {e}")
            return "An error occurred while retrieving player information."

    def get_team_info(self, team_name: str) -> str:
        try:
            team = self.search_service.find_team(team_name)
            if not team:
                return f"No team found matching '{team_name}'"

            team_info = {
                "Name": team.name,
                "Short Name": team.short_name,
                "TLA": team.tla,
                "Founded": team.founded,
                "Club Colors": team.club_colors,
                "Venue": team.venue,
                "Squad": [{
                    "Name": player.name,
                    "Position": player.position,
                    "Date of Birth": player.date_of_birth,
                    "Age": player.age,
                    "Nationality": player.nationality
                } for player in team.squad]
            }

            return json.dumps(team_info, indent=2)

        except Exception as e:
            logger.error(f"Error retrieving team info: {e}")
            return "An error occured while retrieving team information."

    def find_players_by_team_and_position(self, query: str) -> str:
        """Find players by team and position. Query should be in format: 'team_name, position' or 'team_name - position'."""

        try:
            # Parse the query to extract team name and position
            if ',' in query:
                parts = [part.strip() for part in query.split(',', 1)]
            elif ' - ' in query:
                parts = [part.strip() for part in query.split(' - ', 1)]
            else:
                return "Please provide both team name and position in format: 'team_name, position' (e.g., 'Liverpool, Midfielder')"

            if len(parts) != 2:
                return "Please provide both team name and position in format: 'team_name, position' (e.g., 'Liverpool, Midfielder')"

            team_name, position = parts

            results = self.search_service.find_players_by_team_and_position(
                team_name, position)
            if not results:
                return f"No players found for team '{team_name}' in position '{position}'."

            players_info = []
            for player in results:
                players_info.append({
                    "Name": player.name,
                    "Nationality": player.nationality,
                    "Date of Birth": player.date_of_birth,
                    "Age": player.age
                })

            response = {
                "team": team_name,
                "position": position,
                "count": len(results),
                "players": players_info
            }

            return json.dumps(response, indent=2)

        except Exception as e:
            logger.error(f"Error finding players by team and position: {e}")
            return f"An error occurred while searching for players by team and position."

    def get_tools(self) -> List[Tool]:
        """Get the list of LangChain tools."""
        return [
            Tool(
                name="Player_Info",
                func=self.get_player_info,
                description="Get detailed information about a specific Premier League player by name. Use this when asked about a specific player."
            ),
            Tool(
                name="Team_Info",
                func=self.get_team_info,
                description="Get detailed information about a specific Premier League team including stadium, founding year, colors, etc. Use this when asked about a specific team."
            ),
            Tool(
                name="Players_By_Team_And_Position",
                func=self.find_players_by_team_and_position,
                description="Find all players who play in a specific position for a given team. Input should be formatted as 'team_name, position' (e.g., 'Liverpool, Midfielder' or 'Arsenal, Goalkeeper'). Available positions include: 'Goalkeeper', 'Defender', 'Midfielder', 'Forward'. Use this when asked about players in a certain position on a team."
            )
        ]
