"""
Unit tests for the Team dataclass.
Tests cover initialization, API data conversion, and squad management functionality.
"""

from unittest.mock import Mock, patch
import pytest
from data_classes.team import Team
from data_classes.player import Player


class TestTeamInitialization:
    """Test Team dataclass initialization."""

    def test_team_with_required_fields_only(self):
        """Test creating a team with only required fields."""
        team = Team(id=1, name="Liverpool")

        assert team.id == 1
        assert team.name == "Liverpool"
        assert team.short_name is None
        assert team.tla is None
        assert team.founded is None
        assert team.club_colors is None
        assert team.venue is None
        assert team.squad == []  # Should be initialized as empty list

    def test_team_with_all_fields(self):
        """Test creating a team with all fields."""
        mock_player = Mock(spec=Player)
        squad = [mock_player]

        team = Team(
            id=1,
            name="Liverpool",
            short_name="Liverpool FC",
            tla="LIV",
            founded=1892,
            club_colors="Red / White",
            venue="Anfield",
            squad=squad
        )

        assert team.id == 1
        assert team.name == "Liverpool"
        assert team.short_name == "Liverpool FC"
        assert team.tla == "LIV"
        assert team.founded == 1892
        assert team.club_colors == "Red / White"
        assert team.venue == "Anfield"
        assert team.squad == squad

    def test_team_post_init_with_none_squad(self):
        """Test that __post_init__ initializes squad as empty list when None."""
        team = Team(id=1, name="Test Team", squad=None)
        assert team.squad == []

    def test_team_post_init_with_existing_squad(self):
        """Test that __post_init__ preserves existing squad."""
        mock_player = Mock(spec=Player)
        squad = [mock_player]
        team = Team(id=1, name="Test Team", squad=squad)
        assert team.squad == squad


class TestTeamFromApiData:
    """Test Team.from_api_data class method."""

    @patch('data_classes.team.Player')
    def test_from_api_data_complete(self, mock_player_class):
        """Test creating team from complete API data."""
        # Mock Player.from_api_data to return mock player instances
        mock_player1 = Mock(spec=Player)
        mock_player2 = Mock(spec=Player)
        mock_player_class.from_api_data.side_effect = [
            mock_player1, mock_player2]

        api_data = {
            'id': 123,
            'name': 'Manchester United',
            'shortName': 'Man United',
            'tla': 'MUN',
            'founded': 1878,
            'clubColors': 'Red / White / Black',
            'venue': 'Old Trafford',
            'squad': [
                {'id': 1, 'name': 'Player 1'},
                {'id': 2, 'name': 'Player 2'}
            ]
        }

        team = Team.from_api_data(api_data)

        assert team.id == 123
        assert team.name == 'Manchester United'
        assert team.short_name == 'Man United'
        assert team.tla == 'MUN'
        assert team.founded == 1878
        assert team.club_colors == 'Red / White / Black'
        assert team.venue == 'Old Trafford'
        assert len(team.squad) == 2
        assert team.squad == [mock_player1, mock_player2]

        # Verify Player.from_api_data was called with correct data
        assert mock_player_class.from_api_data.call_count == 2
        mock_player_class.from_api_data.assert_any_call(
            {'id': 1, 'name': 'Player 1'})
        mock_player_class.from_api_data.assert_any_call(
            {'id': 2, 'name': 'Player 2'})

    @patch('data_classes.team.Player')
    def test_from_api_data_minimal(self, mock_player_class):
        """Test creating team from minimal API data."""
        api_data = {
            'id': 456,
            'name': 'Test Team'
        }

        team = Team.from_api_data(api_data)

        assert team.id == 456
        assert team.name == 'Test Team'
        assert team.short_name is None
        assert team.tla is None
        assert team.founded is None
        assert team.club_colors is None
        assert team.venue is None
        assert team.squad == []

        # Verify Player.from_api_data was not called since no squad data
        mock_player_class.from_api_data.assert_not_called()

    @patch('data_classes.team.Player')
    def test_from_api_data_missing_id(self, mock_player_class):
        """Test creating team when ID is missing."""
        api_data = {
            'name': 'Team Without ID',
            'founded': 2000
        }

        team = Team.from_api_data(api_data)

        assert team.id == 0  # Default value
        assert team.name == 'Team Without ID'
        assert team.founded == 2000

    @patch('data_classes.team.Player')
    def test_from_api_data_missing_name(self, mock_player_class):
        """Test creating team when name is missing."""
        api_data = {
            'id': 789,
            'venue': 'Some Stadium'
        }

        team = Team.from_api_data(api_data)

        assert team.id == 789
        assert team.name == ''  # Default value
        assert team.venue == 'Some Stadium'

    @patch('data_classes.team.Player')
    def test_from_api_data_empty_squad(self, mock_player_class):
        """Test creating team with empty squad array."""
        api_data = {
            'id': 100,
            'name': 'Empty Squad Team',
            'squad': []
        }

        team = Team.from_api_data(api_data)

        assert team.id == 100
        assert team.name == 'Empty Squad Team'
        assert team.squad == []
        mock_player_class.from_api_data.assert_not_called()

    @patch('data_classes.team.Player')
    def test_from_api_data_player_creation_error(self, mock_player_class):
        """Test handling of player creation errors during team creation."""
        # Mock Player.from_api_data to raise an exception
        mock_player_class.from_api_data.side_effect = ValueError(
            "Invalid player data")

        api_data = {
            'id': 200,
            'name': 'Error Team',
            'squad': [{'id': 1, 'name': 'Invalid Player'}]
        }

        # The error should propagate up since we're not handling it in from_api_data
        with pytest.raises(ValueError, match="Invalid player data"):
            Team.from_api_data(api_data)

    @patch('data_classes.team.Player')
    def test_from_api_data_with_none_squad_data(self, mock_player_class):
        """Test creating team when squad data contains None values."""
        mock_player = Mock(spec=Player)
        mock_player_class.from_api_data.return_value = mock_player

        api_data = {
            'id': 300,
            'name': 'None Squad Team',
            'squad': None  # This should be handled gracefully
        }

        team = Team.from_api_data(api_data)

        assert team.id == 300
        assert team.name == 'None Squad Team'
        assert team.squad == []  # Should default to empty list
        mock_player_class.from_api_data.assert_not_called()


class TestTeamDataclassFeatures:
    """Test dataclass-specific features."""

    def test_team_equality(self):
        """Test that two teams with same data are equal."""
        team1 = Team(id=1, name="Test Team")
        team2 = Team(id=1, name="Test Team")

        assert team1 == team2

    def test_team_inequality(self):
        """Test that teams with different data are not equal."""
        team1 = Team(id=1, name="Team One")
        team2 = Team(id=2, name="Team Two")

        assert team1 != team2

    def test_team_inequality_different_squad(self):
        """Test that teams with different squads are not equal."""
        mock_player1 = Mock(spec=Player)
        mock_player2 = Mock(spec=Player)

        team1 = Team(id=1, name="Team", squad=[mock_player1])
        team2 = Team(id=1, name="Team", squad=[mock_player2])

        assert team1 != team2

    def test_team_string_representation(self):
        """Test the string representation of a team."""
        mock_player = Mock(spec=Player)
        team = Team(
            id=123,
            name="Test Team",
            short_name="Test",
            tla="TST",
            founded=1900,
            club_colors="Blue / White",
            venue="Test Stadium",
            squad=[mock_player]
        )

        repr_str = repr(team)
        assert "Team" in repr_str
        assert "123" in repr_str
        assert "Test Team" in repr_str
        assert "Test" in repr_str
        assert "TST" in repr_str
        assert "1900" in repr_str
        assert "Blue / White" in repr_str
        assert "Test Stadium" in repr_str

    def test_team_with_large_squad(self):
        """Test team with a large squad."""
        mock_players = [Mock(spec=Player) for _ in range(25)]
        team = Team(id=1, name="Large Squad Team", squad=mock_players)

        assert len(team.squad) == 25
        assert all(isinstance(player, Mock) for player in team.squad)


class TestTeamEdgeCases:
    """Test edge cases and error conditions."""

    def test_team_with_zero_id(self):
        """Test team with zero ID."""
        team = Team(id=0, name="Zero ID Team")
        assert team.id == 0

    def test_team_with_negative_id(self):
        """Test team with negative ID."""
        team = Team(id=-1, name="Negative ID Team")
        assert team.id == -1

    def test_team_with_empty_name(self):
        """Test team with empty name."""
        team = Team(id=1, name="")
        assert team.name == ""

    def test_team_with_special_characters_in_name(self):
        """Test team with special characters in name."""
        team = Team(id=1, name="Team with Special Chars áéíóú & Co.")
        assert team.name == "Team with Special Chars áéíóú & Co."

    def test_team_founded_edge_cases(self):
        """Test team with various founded year values."""
        # Very old team
        old_team = Team(id=1, name="Old Team", founded=1800)
        assert old_team.founded == 1800

        # Future founded date
        future_team = Team(id=2, name="Future Team", founded=3000)
        assert future_team.founded == 3000

        # Zero founded date
        zero_team = Team(id=3, name="Zero Team", founded=0)
        assert zero_team.founded == 0
