"""
Unit tests for the FootballTools class.
Tests cover all tool methods and LangChain tool integration functionality.
"""

import pytest
import json
from unittest.mock import Mock

import langchain
from tools.football_tools import FootballTools
from services.search_service import SearchService
from data_classes.team import Team
from data_classes.player import Player


@pytest.fixture
def mock_search_service():
    """Create a mock SearchService."""
    service = Mock(spec=SearchService)
    return service


@pytest.fixture
def mock_player():
    """Create a mock Player."""
    player = Mock(spec=Player)
    player.name = "Mohamed Salah"
    player.position = "Right Winger"
    player.nationality = "Egypt"
    player.date_of_birth = "1992-06-15"
    player.age = 31
    return player


@pytest.fixture
def mock_team():
    """Create a mock Team."""
    team = Mock(spec=Team)
    team.name = "Liverpool FC"
    team.short_name = "Liverpool"
    team.tla = "LIV"
    team.founded = 1892
    team.club_colors = "Red / White"
    team.venue = "Anfield"
    return team


@pytest.fixture
def football_tools(mock_search_service):
    """Create a FootballTools instance with mocked dependencies."""
    return FootballTools(mock_search_service)


class TestGetPlayerInfo:
    """Test the get_player_info method."""

    def test_get_player_info_success(self, football_tools, mock_player, mock_team):
        """Test successful player info retrieval."""
        football_tools.search_service.find_player.return_value = (
            mock_player, mock_team)

        result = football_tools.get_player_info("Mohamed Salah")

        # Parse JSON result to verify structure
        result_data = json.loads(result)
        assert result_data["Name"] == "Mohamed Salah"
        assert result_data["Team"] == "Liverpool FC"
        assert result_data["Position"] == "Right Winger"
        assert result_data["Date of Birth"] == "1992-06-15"
        assert result_data["Age"] == 31
        assert result_data["Nationality"] == "Egypt"

        football_tools.search_service.find_player.assert_called_once_with(
            "Mohamed Salah")

    def test_get_player_info_player_not_found(self, football_tools):
        """Test player info when player is not found."""
        football_tools.search_service.find_player.return_value = None

        result = football_tools.get_player_info("Unknown Player")

        assert result == "No player found matching 'Unknown Player'."
        football_tools.search_service.find_player.assert_called_once_with(
            "Unknown Player")

    def test_get_player_info_search_service_error(self, football_tools):
        """Test player info when search service raises an error."""
        football_tools.search_service.find_player.side_effect = Exception(
            "Search error")

        result = football_tools.get_player_info("Mohamed Salah")

        assert result == "An error occurred while retrieving player information."

    def test_get_player_info_with_no_team(self, football_tools, mock_player):
        """Test player info when player has no associated team."""
        football_tools.search_service.find_player.return_value = (
            mock_player, None)

        result = football_tools.get_player_info("Mohamed Salah")

        result_data = json.loads(result)
        assert result_data["Team"] == "N/A"
        assert result_data["Name"] == "Mohamed Salah"

    def test_get_player_info_with_none_values(self, football_tools, mock_team):
        """Test player info with None values in player data."""
        player_with_nones = Mock(spec=Player)
        player_with_nones.name = "Test Player"
        player_with_nones.position = None
        player_with_nones.nationality = None
        player_with_nones.date_of_birth = None
        player_with_nones.age = None

        football_tools.search_service.find_player.return_value = (
            player_with_nones, mock_team)

        result = football_tools.get_player_info("Test Player")

        result_data = json.loads(result)
        assert result_data["Name"] == "Test Player"
        assert result_data["Position"] is None
        assert result_data["Nationality"] is None
        assert result_data["Date of Birth"] is None
        assert result_data["Age"] is None


class TestGetTeamInfo:
    """Test the get_team_info method."""

    def test_get_team_info_success(self, football_tools, mock_team, mock_player):
        """Test successful team info retrieval."""
        mock_team.squad = [mock_player]
        football_tools.search_service.find_team.return_value = mock_team

        result = football_tools.get_team_info("Liverpool FC")

        # Parse JSON result to verify structure
        result_data = json.loads(result)
        assert result_data["Name"] == "Liverpool FC"
        assert result_data["Short Name"] == "Liverpool"
        assert result_data["TLA"] == "LIV"
        assert result_data["Founded"] == 1892
        assert result_data["Club Colors"] == "Red / White"
        assert result_data["Venue"] == "Anfield"
        assert len(result_data["Squad"]) == 1

        squad_player = result_data["Squad"][0]
        assert squad_player["Name"] == "Mohamed Salah"
        assert squad_player["Position"] == "Right Winger"
        assert squad_player["Nationality"] == "Egypt"

        football_tools.search_service.find_team.assert_called_once_with(
            "Liverpool FC")

    def test_get_team_info_team_not_found(self, football_tools):
        """Test team info when team is not found."""
        football_tools.search_service.find_team.return_value = None

        result = football_tools.get_team_info("Unknown Team")

        assert result == "No team found matching 'Unknown Team'"
        football_tools.search_service.find_team.assert_called_once_with(
            "Unknown Team")

    def test_get_team_info_search_service_error(self, football_tools):
        """Test team info when search service raises an error."""
        football_tools.search_service.find_team.side_effect = Exception(
            "Search error")

        result = football_tools.get_team_info("Liverpool FC")

        assert result == "An error occured while retrieving team information."

    def test_get_team_info_empty_squad(self, football_tools, mock_team):
        """Test team info with empty squad."""
        mock_team.squad = []
        football_tools.search_service.find_team.return_value = mock_team

        result = football_tools.get_team_info("Liverpool FC")

        result_data = json.loads(result)
        assert result_data["Squad"] == []

    def test_get_team_info_with_none_values(self, football_tools):
        """Test team info with None values in team data."""
        team_with_nones = Mock(spec=Team)
        team_with_nones.name = "Test Team"
        team_with_nones.short_name = None
        team_with_nones.tla = None
        team_with_nones.founded = None
        team_with_nones.club_colors = None
        team_with_nones.venue = None
        team_with_nones.squad = []

        football_tools.search_service.find_team.return_value = team_with_nones

        result = football_tools.get_team_info("Test Team")

        result_data = json.loads(result)
        assert result_data["Name"] == "Test Team"
        assert result_data["Short Name"] is None
        assert result_data["TLA"] is None
        assert result_data["Founded"] is None
        assert result_data["Club Colors"] is None
        assert result_data["Venue"] is None


class TestFindPlayersByTeamAndPosition:
    """Test the find_players_by_team_and_position method."""

    def test_find_players_by_team_and_position_comma_separator(self, football_tools, mock_player):
        """Test finding players with comma separator."""
        football_tools.search_service.find_players_by_team_and_position.return_value = [
            mock_player]

        result = football_tools.find_players_by_team_and_position(
            "Liverpool, Winger")

        result_data = json.loads(result)
        assert result_data["team"] == "Liverpool"
        assert result_data["position"] == "Winger"
        assert result_data["count"] == 1
        assert len(result_data["players"]) == 1

        player_data = result_data["players"][0]
        assert player_data["Name"] == "Mohamed Salah"
        assert player_data["Nationality"] == "Egypt"

        football_tools.search_service.find_players_by_team_and_position.assert_called_once_with(
            "Liverpool", "Winger")

    def test_find_players_by_team_and_position_dash_separator(self, football_tools, mock_player):
        """Test finding players with dash separator."""
        football_tools.search_service.find_players_by_team_and_position.return_value = [
            mock_player]

        result = football_tools.find_players_by_team_and_position(
            "Liverpool - Winger")

        result_data = json.loads(result)
        assert result_data["team"] == "Liverpool"
        assert result_data["position"] == "Winger"

        football_tools.search_service.find_players_by_team_and_position.assert_called_once_with(
            "Liverpool", "Winger")

    def test_find_players_by_team_and_position_invalid_format_no_separator(self, football_tools):
        """Test finding players with invalid format (no separator)."""
        result = football_tools.find_players_by_team_and_position(
            "Liverpool Winger")

        expected_message = "Please provide both team name and position in format: 'team_name, position' (e.g., 'Liverpool, Midfielder')"
        assert result == expected_message

    def test_find_players_by_team_and_position_no_players_found(self, football_tools):
        """Test finding players when no players match criteria."""
        football_tools.search_service.find_players_by_team_and_position.return_value = []

        result = football_tools.find_players_by_team_and_position(
            "Arsenal, Striker")

        assert result == "No players found for team 'Arsenal' in position 'Striker'."
        football_tools.search_service.find_players_by_team_and_position.assert_called_once_with(
            "Arsenal", "Striker")

    def test_find_players_by_team_and_position_search_service_error(self, football_tools):
        """Test finding players when search service raises an error."""
        football_tools.search_service.find_players_by_team_and_position.side_effect = Exception(
            "Search error")

        result = football_tools.find_players_by_team_and_position(
            "Liverpool, Winger")

        assert result == "An error occurred while searching for players by team and position."

    def test_find_players_by_team_and_position_multiple_players(self, football_tools):
        """Test finding multiple players matching criteria."""
        player1 = Mock(spec=Player)
        player1.name = "Player 1"
        player1.nationality = "Country 1"
        player1.date_of_birth = "1990-01-01"
        player1.age = 33

        player2 = Mock(spec=Player)
        player2.name = "Player 2"
        player2.nationality = "Country 2"
        player2.date_of_birth = "1995-01-01"
        player2.age = 28

        football_tools.search_service.find_players_by_team_and_position.return_value = [
            player1, player2]

        result = football_tools.find_players_by_team_and_position(
            "Liverpool, Midfielder")

        result_data = json.loads(result)
        assert result_data["count"] == 2
        assert len(result_data["players"]) == 2

        player_names = [p["Name"] for p in result_data["players"]]
        assert "Player 1" in player_names
        assert "Player 2" in player_names

    def test_find_players_by_team_and_position_with_whitespace(self, football_tools, mock_player):
        """Test finding players with extra whitespace in query."""
        football_tools.search_service.find_players_by_team_and_position.return_value = [
            mock_player]

        result = football_tools.find_players_by_team_and_position(
            "  Liverpool  ,  Winger  ")

        result_data = json.loads(result)
        assert result_data["team"] == "Liverpool"  # Should be trimmed
        assert result_data["position"] == "Winger"  # Should be trimmed

        football_tools.search_service.find_players_by_team_and_position.assert_called_once_with(
            "Liverpool", "Winger")


class TestGetTools:
    """Test the get_tools method that returns LangChain tools."""

    def test_get_tools_returns_correct_number(self, football_tools):
        """Test that get_tools returns the expected number of tools."""
        tools = football_tools.get_tools()
        assert len(tools) == 3

    def test_get_tools_returns_langchain_tool_objects(self, football_tools):
        """Test that get_tools returns proper LangChain Tool objects."""
        from langchain.agents import Tool

        tools = football_tools.get_tools()

        for tool in tools:
            assert isinstance(tool, Tool)
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'func')
            assert hasattr(tool, 'description')

    def test_get_tools_has_correct_tool_names(self, football_tools):
        """Test that get_tools returns tools with expected names."""
        tools = football_tools.get_tools()
        tool_names = [tool.name for tool in tools]

        expected_names = ["Player_Info", "Team_Info",
                          "Players_By_Team_And_Position"]
        assert set(tool_names) == set(expected_names)

    def test_get_tools_functions_callable(self, football_tools):
        """Test that all tool functions are callable."""
        tools = football_tools.get_tools()

        for tool in tools:
            assert callable(tool.func)

    def test_get_tools_descriptions_not_empty(self, football_tools):
        """Test that all tools have non-empty descriptions."""
        tools = football_tools.get_tools()

        for tool in tools:
            assert tool.description
            assert len(tool.description.strip()) > 0

    def test_tool_functions_match_methods(self, football_tools):
        """Test that tool functions match the corresponding methods."""
        tools = football_tools.get_tools()
        tool_dict = {tool.name: tool.func for tool in tools}

        assert tool_dict["Player_Info"] == football_tools.get_player_info
        assert tool_dict["Team_Info"] == football_tools.get_team_info
        assert tool_dict["Players_By_Team_And_Position"] == football_tools.find_players_by_team_and_position


class TestIntegrationScenarios:
    """Test integration scenarios and complex use cases."""

    def test_full_workflow_player_search(self, mock_search_service):
        """Test full workflow of initializing tools and searching for a player."""
        # Create tools instance with mock search service
        tools = FootballTools(mock_search_service)

        # Setup player search result
        mock_player = Mock(spec=Player)
        mock_player.name = "Test Player"
        mock_player.position = "Forward"
        mock_player.nationality = "England"
        mock_player.date_of_birth = "1990-01-01"
        mock_player.age = 33

        mock_team = Mock(spec=Team)
        mock_team.name = "Test Team"

        mock_search_service.find_player.return_value = (mock_player, mock_team)

        # Test the workflow
        result = tools.get_player_info("Test Player")

        # Verify the search service was called correctly
        mock_search_service.find_player.assert_called_once_with("Test Player")

        result_data = json.loads(result)
        assert result_data["Name"] == "Test Player"

    def test_error_propagation_through_layers(self, mock_search_service):
        """Test that errors propagate correctly through the layers."""
        # Setup search service to fail
        mock_search_service.find_player.side_effect = Exception(
            "Search Failed")

        # Create tools instance
        tools = FootballTools(mock_search_service)

        # Method calls should return appropriate error messages
        result = tools.get_player_info("Any Player")
        assert result == "An error occurred while retrieving player information."

    def test_json_serialization_with_complex_data(self, football_tools):
        """Test JSON serialization with complex nested data structures."""
        # Create complex mock data
        mock_players = []
        for i in range(3):
            player = Mock(spec=Player)
            player.name = f"Player {i}"
            player.position = f"Position {i}"
            player.nationality = f"Country {i}"
            player.date_of_birth = f"199{i}-01-01"
            player.age = 30 + i
            mock_players.append(player)

        mock_team = Mock(spec=Team)
        mock_team.name = "Complex Team"
        mock_team.short_name = "Complex"
        mock_team.tla = "CPX"
        mock_team.founded = 1900
        mock_team.club_colors = "Blue / White / Red"
        mock_team.venue = "Complex Stadium"
        mock_team.squad = mock_players

        football_tools.search_service.find_team.return_value = mock_team

        result = football_tools.get_team_info("Complex Team")

        # Should successfully parse as JSON
        result_data = json.loads(result)
        assert result_data["Name"] == "Complex Team"
        assert len(result_data["Squad"]) == 3
        assert all("Name" in player for player in result_data["Squad"])

    def test_memory_efficiency_with_large_datasets(self, football_tools):
        """Test memory efficiency with large numbers of players/teams."""
        # Create a large number of mock players
        large_player_list = []
        for i in range(100):
            player = Mock(spec=Player)
            player.name = f"Player {i}"
            # Rotate through 10 countries
            player.nationality = f"Country {i % 10}"
            player.date_of_birth = "1990-01-01"
            player.age = 33
            large_player_list.append(player)

        football_tools.search_service.find_players_by_team_and_position.return_value = large_player_list

        result = football_tools.find_players_by_team_and_position(
            "Big Team, Midfielder")

        # Should handle large datasets without issues
        result_data = json.loads(result)
        assert result_data["count"] == 100
        assert len(result_data["players"]) == 100

        # Verify all players are properly serialized
        player_names = [p["Name"] for p in result_data["players"]]
        assert len(set(player_names)) == 100  # All unique names
