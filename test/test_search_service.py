"""
Unit tests for the SearchService class.
Tests cover team and player search functionality with fuzzy matching.
"""

import pytest
from unittest.mock import Mock

from services.search_service import SearchService
from data_classes.team import Team
from data_classes.player import Player


@pytest.fixture
def mock_players():
    """Create mock players for testing."""
    player1 = Mock(spec=Player)
    player1.name = "Mohamed Salah"
    player1.position = "Right Winger"
    player1.nationality = "Egypt"
    player1.date_of_birth = "1992-06-15"
    player1.age = 31

    player2 = Mock(spec=Player)
    player2.name = "Sadio Mané"
    player2.position = "Left Winger"
    player2.nationality = "Senegal"
    player2.date_of_birth = "1992-04-10"
    player2.age = 31

    player3 = Mock(spec=Player)
    player3.name = "Virgil van Dijk"
    player3.position = "Centre-Back"
    player3.nationality = "Netherlands"
    player3.date_of_birth = "1991-07-08"
    player3.age = 32

    player4 = Mock(spec=Player)
    player4.name = "Alisson Becker"
    player4.position = "Goalkeeper"
    player4.nationality = "Brazil"
    player4.date_of_birth = "1993-10-02"
    player4.age = 30

    player5 = Mock(spec=Player)
    player5.name = "Bruno Fernandes"
    player5.position = "Attacking Midfielder"
    player5.nationality = "Portugal"
    player5.date_of_birth = "1994-09-08"
    player5.age = 29

    return [player1, player2, player3, player4, player5]


@pytest.fixture
def mock_teams(mock_players):
    """Create mock teams with players for testing."""
    # Liverpool team
    liverpool = Mock(spec=Team)
    liverpool.id = 1
    liverpool.name = "Liverpool FC"
    liverpool.short_name = "Liverpool"
    liverpool.tla = "LIV"
    liverpool.squad = mock_players[:4]  # First 4 players

    # Manchester United team
    man_united = Mock(spec=Team)
    man_united.id = 2
    man_united.name = "Manchester United FC"
    man_united.short_name = "Man United"
    man_united.tla = "MUN"
    man_united.squad = [mock_players[4]]  # Last player

    # Arsenal team (no players for testing edge cases)
    arsenal = Mock(spec=Team)
    arsenal.id = 3
    arsenal.name = "Arsenal FC"
    arsenal.short_name = "Arsenal"
    arsenal.tla = "ARS"
    arsenal.squad = []

    return [liverpool, man_united, arsenal]


@pytest.fixture
def mock_team_data_store(mock_teams):
    """Create a mock team data store that returns teams."""
    data_store = Mock()
    data_store.get_teams.return_value = mock_teams
    return data_store


@pytest.fixture
def search_service(mock_team_data_store):
    """Create a SearchService instance with mock team data store."""
    return SearchService(mock_team_data_store)


class TestSearchServiceInitialization:
    """Test SearchService initialization."""

    def test_initialization_with_team_data_store(self, mock_team_data_store):
        """Test proper initialization with team data store."""
        service = SearchService(mock_team_data_store)
        assert service.teams_data_store == mock_team_data_store

    def test_initialization_with_empty_team_data_store(self):
        """Test initialization with team data store that returns empty teams list."""
        empty_data_store = Mock()
        empty_data_store.get_teams.return_value = []
        service = SearchService(empty_data_store)
        assert service.teams_data_store == empty_data_store
        assert service.teams_data_store.get_teams() == []


class TestCalculateSimilarity:
    """Test the _calculate_similarity private method."""

    def test_calculate_similarity_identical_strings(self, search_service):
        """Test similarity calculation with identical strings."""
        similarity = search_service._calculate_similarity(
            "Liverpool", "Liverpool")
        assert similarity == 1.0

    def test_calculate_similarity_case_insensitive(self, search_service):
        """Test similarity calculation is case insensitive."""
        similarity = search_service._calculate_similarity(
            "LIVERPOOL", "liverpool")
        assert similarity == 1.0

    def test_calculate_similarity_different_strings(self, search_service):
        """Test similarity calculation with different strings."""
        similarity = search_service._calculate_similarity(
            "Liverpool", "Arsenal")
        assert 0.0 <= similarity < 1.0

    def test_calculate_similarity_partial_match(self, search_service):
        """Test similarity calculation with partial matches."""
        similarity = search_service._calculate_similarity("Liver", "Liverpool")
        assert 0.5 < similarity < 1.0

    def test_calculate_similarity_empty_strings(self, search_service):
        """Test similarity calculation with empty strings."""
        similarity = search_service._calculate_similarity("", "")
        assert similarity == 1.0

        similarity = search_service._calculate_similarity("Liverpool", "")
        assert similarity == 0.0

    def test_calculate_similarity_whitespace_handling(self, search_service):
        """Test similarity calculation with whitespace."""
        similarity1 = search_service._calculate_similarity(
            "Liverpool FC", "Liverpool")
        similarity2 = search_service._calculate_similarity(
            "Liverpool", "Liverpool FC")
        assert similarity1 == similarity2
        assert 0.5 < similarity1 < 1.0


class TestFindTeam:
    """Test the find_team method."""

    def test_find_team_exact_match(self, search_service):
        """Test finding team with exact name match."""
        team = search_service.find_team("Liverpool FC")
        assert team is not None
        assert team.name == "Liverpool FC"

    def test_find_team_case_insensitive(self, search_service):
        """Test finding team with case insensitive search."""
        team = search_service.find_team("liverpool fc")
        assert team is not None
        assert team.name == "Liverpool FC"

    def test_find_team_partial_match(self, search_service):
        """Test finding team with partial name match."""
        team = search_service.find_team("Liverpool")
        assert team is not None
        assert team.name == "Liverpool FC"

    def test_find_team_short_name_match(self, search_service):
        """Test finding team by short name."""
        team = search_service.find_team("Liverpool")
        assert team is not None
        assert team.short_name == "Liverpool"

    def test_find_team_tla_match(self, search_service):
        """Test finding team by TLA (Three Letter Abbreviation)."""
        team = search_service.find_team("LIV")
        assert team is not None
        assert team.tla == "LIV"

    def test_find_team_no_match_below_threshold(self, search_service):
        """Test no match when similarity is below threshold."""
        team = search_service.find_team("Barcelona", threshold=0.8)
        assert team is None

    def test_find_team_custom_threshold(self, search_service):
        """Test finding team with custom threshold."""
        # This should find a match with lower threshold
        team = search_service.find_team("Liver", threshold=0.3)
        assert team is not None

        # This should not find a match with higher threshold
        team = search_service.find_team("Liver", threshold=0.9)
        assert team is None

    def test_find_team_best_match_selection(self, search_service):
        """Test that the best match is selected among multiple candidates."""
        # "Man" should match "Man United" better than other teams
        team = search_service.find_team("Man United")
        assert team is not None
        assert team.name == "Manchester United FC"

    def test_find_team_with_none_optional_fields(self):
        """Test finding team when optional fields are None."""
        # Create a team with None short_name and tla
        team_with_none_fields = Mock(spec=Team)
        team_with_none_fields.name = "Test Team"
        team_with_none_fields.short_name = None
        team_with_none_fields.tla = None

        # Create mock data store
        mock_data_store = Mock()
        mock_data_store.get_teams.return_value = [team_with_none_fields]

        service = SearchService(mock_data_store)
        result = service.find_team("Test Team")
        assert result is not None

    def test_find_team_empty_search_string(self, search_service):
        """Test finding team with empty search string."""
        team = search_service.find_team("")
        assert team is None

    def test_find_team_from_empty_teams_list(self):
        """Test finding team when teams list is empty."""
        empty_data_store = Mock()
        empty_data_store.get_teams.return_value = []
        service = SearchService(empty_data_store)
        team = service.find_team("Any Team")
        assert team is None


class TestFindPlayer:
    """Test the find_player method."""

    def test_find_player_exact_match(self, search_service):
        """Test finding player with exact name match."""
        result = search_service.find_player("Mohamed Salah")
        assert result is not None
        player, team = result
        assert player.name == "Mohamed Salah"
        assert team.name == "Liverpool FC"

    def test_find_player_case_insensitive(self, search_service):
        """Test finding player with case insensitive search."""
        result = search_service.find_player("mohamed salah")
        assert result is not None
        player, team = result
        assert player.name == "Mohamed Salah"

    def test_find_player_partial_match(self, search_service):
        """Test finding player with partial name match."""
        result = search_service.find_player("Mohamed")
        assert result is not None
        player, team = result
        assert player.name == "Mohamed Salah"

    def test_find_player_no_match_below_threshold(self, search_service):
        """Test no match when similarity is below threshold."""
        result = search_service.find_player("Messi", threshold=0.8)
        assert result is None

    def test_find_player_custom_threshold(self, search_service):
        """Test finding player with custom threshold."""
        # This should find a match with lower threshold
        result = search_service.find_player("Virgil", threshold=0.3)
        assert result is not None

        # This should not find a match with higher threshold
        result = search_service.find_player("Virgil", threshold=0.9)
        assert result is None

    def test_find_player_best_match_selection(self, search_service):
        """Test that the best match is selected among multiple candidates."""
        result = search_service.find_player("Bruno Fernandes")
        assert result is not None
        player, team = result
        assert player.name == "Bruno Fernandes"
        assert team.name == "Manchester United FC"

    def test_find_player_from_different_teams(self, search_service):
        """Test finding players from different teams."""
        # Liverpool player
        result1 = search_service.find_player("Mohamed Salah")
        assert result1 is not None
        _, team1 = result1
        assert team1.name == "Liverpool FC"

        # Manchester United player
        result2 = search_service.find_player("Bruno Fernandes")
        assert result2 is not None
        _, team2 = result2
        assert team2.name == "Manchester United FC"

    def test_find_player_empty_search_string(self, search_service):
        """Test finding player with empty search string."""
        result = search_service.find_player("")
        assert result is None

    def test_find_player_from_team_with_empty_squad(self, search_service):
        """Test finding player from team with empty squad."""
        result = search_service.find_player("Non Existent Player")
        assert result is None

    def test_find_player_from_empty_teams_list(self):
        """Test finding player when teams list is empty."""
        empty_data_store = Mock()
        empty_data_store.get_teams.return_value = []
        service = SearchService(empty_data_store)
        result = service.find_player("Any Player")
        assert result is None


class TestFindPlayersByTeamAndPosition:
    """Test the find_players_by_team_and_position method."""

    def test_find_players_by_team_and_position_exact_match(self, search_service):
        """Test finding players with exact team and position match."""
        players = search_service.find_players_by_team_and_position(
            "Liverpool FC", "Goalkeeper")
        assert len(players) == 1
        assert players[0].name == "Alisson Becker"
        assert players[0].position == "Goalkeeper"

    def test_find_players_by_team_and_position_partial_position_match(self, search_service):
        """Test finding players with partial position match."""
        players = search_service.find_players_by_team_and_position(
            "Liverpool FC", "Winger")
        assert len(players) == 2  # Mohamed Salah and Sadio Mané
        player_names = [p.name for p in players]
        assert "Mohamed Salah" in player_names
        assert "Sadio Mané" in player_names

    def test_find_players_by_team_and_position_case_insensitive_position(self, search_service):
        """Test finding players with case insensitive position search."""
        players = search_service.find_players_by_team_and_position(
            "Liverpool FC", "goalkeeper")
        assert len(players) == 1
        assert players[0].name == "Alisson Becker"

    def test_find_players_by_team_and_position_fuzzy_team_match(self, search_service):
        """Test finding players with fuzzy team name match."""
        players = search_service.find_players_by_team_and_position(
            "Liverpool", "Goalkeeper")
        assert len(players) == 1
        assert players[0].name == "Alisson Becker"

    def test_find_players_by_team_and_position_no_team_match(self, search_service):
        """Test finding players when team is not found."""
        players = search_service.find_players_by_team_and_position(
            "Barcelona", "Forward")
        assert players == []

    def test_find_players_by_team_and_position_no_position_match(self, search_service):
        """Test finding players when position doesn't match."""
        players = search_service.find_players_by_team_and_position(
            "Liverpool FC", "Striker")
        assert players == []

    def test_find_players_by_team_and_position_empty_squad(self, search_service):
        """Test finding players from team with empty squad."""
        players = search_service.find_players_by_team_and_position(
            "Arsenal FC", "Forward")
        assert players == []

    def test_find_players_by_team_and_position_multiple_matches(self, search_service):
        """Test finding multiple players matching criteria."""
        players = search_service.find_players_by_team_and_position(
            "Liverpool FC", "Winger")
        assert len(players) >= 2  # Should find both wingers

    def test_find_players_by_team_and_position_player_with_none_position(self, search_service, mock_teams):
        """Test finding players when some players have None position."""
        # Add a player with None position
        player_no_position = Mock(spec=Player)
        player_no_position.name = "No Position Player"
        player_no_position.position = None

        # Add to Liverpool's squad (first team in mock_teams)
        mock_teams[0].squad.append(player_no_position)

        # Update the data store to return the modified teams
        search_service.teams_data_store.get_teams.return_value = mock_teams

        players = search_service.find_players_by_team_and_position(
            "Liverpool FC", "Any Position")

        # Should not include the player with None position
        player_names = [p.name for p in players]
        assert "No Position Player" not in player_names

    def test_find_players_by_team_and_position_complex_position_names(self, search_service):
        """Test finding players with complex position names."""
        # Test with "Midfielder" which should match "Attacking Midfielder"
        players = search_service.find_players_by_team_and_position(
            "Manchester United FC", "Midfielder")
        assert len(players) == 1
        assert players[0].name == "Bruno Fernandes"
        assert "Midfielder" in players[0].position


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""

    def test_search_service_with_teams_having_duplicate_names(self):
        """Test search service with teams having duplicate names."""
        team1 = Mock(spec=Team)
        team1.name = "Duplicate Team"
        team1.short_name = "Duplicate1"
        team1.tla = "DT1"
        team1.squad = []

        team2 = Mock(spec=Team)
        team2.name = "Duplicate Team"
        team2.short_name = "Duplicate2"
        team2.tla = "DT2"
        team2.squad = []

        # Create mock data store
        mock_data_store = Mock()
        mock_data_store.get_teams.return_value = [team1, team2]
        service = SearchService(mock_data_store)

        # Should return one of the teams (implementation returns the first best match)
        result = service.find_team("Duplicate Team")
        assert result is not None
        assert result.name == "Duplicate Team"

    def test_search_service_with_players_having_duplicate_names(self):
        """Test search service with players having duplicate names."""
        player1 = Mock(spec=Player)
        player1.name = "Duplicate Player"

        player2 = Mock(spec=Player)
        player2.name = "Duplicate Player"

        team = Mock(spec=Team)
        team.name = "Test Team"
        team.short_name = "Test"
        team.tla = "TST"
        team.squad = [player1, player2]

        # Create mock data store
        mock_data_store = Mock()
        mock_data_store.get_teams.return_value = [team]
        service = SearchService(mock_data_store)

        result = service.find_player("Duplicate Player")
        assert result is not None
        player, found_team = result
        assert player.name == "Duplicate Player"
        assert found_team.name == "Test Team"

    def test_special_characters_in_names(self):
        """Test handling of special characters in team and player names."""
        # Create team with special characters
        special_team = Mock(spec=Team)
        special_team.name = "Team with Spéçial Chäractérs & Co."
        special_team.short_name = "Spéçial"
        special_team.tla = "SPC"
        special_team.squad = []

        # Create mock data store
        mock_data_store = Mock()
        mock_data_store.get_teams.return_value = [special_team]
        service = SearchService(mock_data_store)

        result = service.find_team("Spéçial")
        # Should handle special characters gracefully (may or may not match depending on similarity algorithm)
        assert result.name == "Team with Spéçial Chäractérs & Co."

    def test_very_long_names(self, search_service):
        """Test handling of very long team and player names."""
        long_name = "A" * 1000  # Very long name

        result = search_service.find_team(long_name)
        assert result is None  # Should not crash

        result = search_service.find_player(long_name)
        assert result is None  # Should not crash

    def test_unicode_names(self):
        """Test handling of Unicode characters in names."""
        unicode_team = Mock(spec=Team)
        unicode_team.name = "FC København 🇩🇰"
        unicode_team.short_name = "København"
        unicode_team.tla = "FCK"
        unicode_team.squad = []

        # Create mock data store
        mock_data_store = Mock()
        mock_data_store.get_teams.return_value = [unicode_team]
        service = SearchService(mock_data_store)

        # Should handle Unicode characters without crashing
        result = service.find_team("København")
        assert result.name == "FC København 🇩🇰"
