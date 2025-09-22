from services.football_api_service import FootballAPIService
from config.settings import load_config

config = load_config()
api_service = FootballAPIService(config.football_api)


def list_positions() -> str:
    """List all available player positions."""

    teams = api_service.get_teams()
    positions = set()
    for team in teams:
        for player in team.squad:
            if player.position:
                positions.add(player.position)

    if not positions:
        return "No player positions found."

    sorted_positions = sorted(positions)
    return sorted_positions


if __name__ == "__main__":
    positions = list_positions()
    print("Available Player Positions:")
    print(positions)
