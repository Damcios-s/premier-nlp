"""
Unit tests for the Player dataclass.
Tests cover initialization, API data conversion, and age calculation functionality.
"""

from datetime import date
from unittest.mock import patch
from data_classes.player import Player


class TestPlayerInitialization:
    """Test Player dataclass initialization."""

    def test_player_with_required_fields_only(self):
        """Test creating a player with only required fields."""
        player = Player(id=1, name="Harry Kane")

        assert player.id == 1
        assert player.name == "Harry Kane"
        assert player.position is None
        assert player.nationality is None
        assert player.date_of_birth is None
        assert player.age is None

    def test_player_with_all_fields(self):
        """Test creating a player with all fields."""
        player = Player(
            id=1,
            name="Harry Kane",
            position="Forward",
            nationality="England",
            date_of_birth="1993-07-28",
            age=30
        )

        assert player.id == 1
        assert player.name == "Harry Kane"
        assert player.position == "Forward"
        assert player.nationality == "England"
        assert player.date_of_birth == "1993-07-28"
        assert player.age == 30


class TestPlayerFromApiData:
    """Test Player.from_api_data class method."""

    def test_from_api_data_complete(self):
        """Test creating player from complete API data."""
        api_data = {
            'id': 123,
            'name': 'Mohamed Salah',
            'position': 'Right Winger',
            'nationality': 'Egypt',
            'dateOfBirth': '1992-06-15'
        }

        with patch.object(Player, 'calculate_age', return_value=31) as mock_age:
            player = Player.from_api_data(api_data)

            assert player.id == 123
            assert player.name == 'Mohamed Salah'
            assert player.position == 'Right Winger'
            assert player.nationality == 'Egypt'
            assert player.date_of_birth == '1992-06-15'
            assert player.age == 31
            mock_age.assert_called_once_with('1992-06-15')

    def test_from_api_data_minimal(self):
        """Test creating player from minimal API data."""
        api_data = {
            'id': 456,
            'name': 'Unknown Player'
        }

        with patch.object(Player, 'calculate_age', return_value=None) as mock_age:
            player = Player.from_api_data(api_data)

            assert player.id == 456
            assert player.name == 'Unknown Player'
            assert player.position is None
            assert player.nationality is None
            assert player.date_of_birth is None
            assert player.age is None
            mock_age.assert_called_once_with(None)

    def test_from_api_data_missing_id(self):
        """Test creating player when ID is missing."""
        api_data = {
            'name': 'Player Without ID',
            'dateOfBirth': '1995-01-01'
        }

        with patch.object(Player, 'calculate_age', return_value=28) as mock_age:
            player = Player.from_api_data(api_data)

            assert player.id == 0  # Default value
            assert player.name == 'Player Without ID'
            assert player.date_of_birth == '1995-01-01'
            assert player.age == 28
            mock_age.assert_called_once_with('1995-01-01')

    def test_from_api_data_missing_name(self):
        """Test creating player when name is missing."""
        api_data = {
            'id': 789,
            'position': 'Goalkeeper',
            'dateOfBirth': '1990-12-25'
        }

        with patch.object(Player, 'calculate_age', return_value=32) as mock_age:
            player = Player.from_api_data(api_data)

            assert player.id == 789
            assert player.name == ''  # Default value
            assert player.position == 'Goalkeeper'
            assert player.date_of_birth == '1990-12-25'
            assert player.age == 32
            mock_age.assert_called_once_with('1990-12-25')


class TestCalculateAge:
    """Test Player.calculate_age static method."""

    def test_calculate_age_valid_date(self):
        """Test age calculation with a valid date."""
        # Test with a known date to ensure predictable results
        with patch('data_classes.player.date') as mock_date:
            mock_date.today.return_value = date(2025, 9, 19)
            mock_date.fromisoformat.return_value = date(1993, 7, 28)

            age = Player.calculate_age('1993-07-28')

            assert age == 32
            mock_date.fromisoformat.assert_called_once_with('1993-07-28')

    def test_calculate_age_birthday_not_passed(self):
        """Test age calculation when birthday hasn't occurred this year."""
        with patch('data_classes.player.date') as mock_date:
            mock_date.today.return_value = date(2025, 6, 15)  # Before birthday
            mock_date.fromisoformat.return_value = date(1993, 7, 28)

            age = Player.calculate_age('1993-07-28')

            assert age == 31  # One year less because birthday hasn't passed

    def test_calculate_age_birthday_today(self):
        """Test age calculation when today is the birthday."""
        with patch('data_classes.player.date') as mock_date:
            mock_date.today.return_value = date(2025, 7, 28)  # Exact birthday
            mock_date.fromisoformat.return_value = date(1993, 7, 28)

            age = Player.calculate_age('1993-07-28')

            assert age == 32

    def test_calculate_age_none_input(self):
        """Test age calculation with None input."""
        age = Player.calculate_age(None)
        assert age is None

    def test_calculate_age_empty_string(self):
        """Test age calculation with empty string."""
        age = Player.calculate_age('')
        assert age is None

    def test_calculate_age_invalid_format(self):
        """Test age calculation with invalid date format."""
        age = Player.calculate_age('invalid-date')
        assert age is None

    def test_calculate_age_invalid_date_values(self):
        """Test age calculation with invalid date values."""
        # Test various invalid date formats that might cause ValueError
        invalid_dates = [
            '2023-13-01',  # Invalid month
            '2023-01-32',  # Invalid day
            '2023/01/01',  # Wrong format
            '01-01-2023',  # Wrong order
            'not-a-date',
        ]

        for invalid_date in invalid_dates:
            age = Player.calculate_age(invalid_date)
            assert age is None, f"Expected None for invalid date: {invalid_date}"

    def test_calculate_age_future_date(self):
        """Test age calculation with a future birth date."""
        with patch('data_classes.player.date') as mock_date:
            mock_date.today.return_value = date(2025, 9, 19)
            mock_date.fromisoformat.return_value = date(
                2026, 1, 1)  # Future date

            age = Player.calculate_age('2026-01-01')

            assert age is None  # Should return None for negative age

    def test_calculate_age_edge_cases(self):
        """Test age calculation edge cases."""
        # Test leap year scenarios
        with patch('data_classes.player.date') as mock_date:
            mock_date.today.return_value = date(2024, 2, 29)  # Leap year
            mock_date.fromisoformat.return_value = date(
                2000, 2, 29)  # Born on leap day

            age = Player.calculate_age('2000-02-29')

            assert age == 24


class TestPlayerDataclassFeatures:
    """Test dataclass-specific features."""

    def test_player_equality(self):
        """Test that two players with same data are equal."""
        player1 = Player(id=1, name="Test Player")
        player2 = Player(id=1, name="Test Player")

        assert player1 == player2

    def test_player_inequality(self):
        """Test that players with different data are not equal."""
        player1 = Player(id=1, name="Player One")
        player2 = Player(id=2, name="Player Two")

        assert player1 != player2

    def test_player_string_representation(self):
        """Test the string representation of a player."""
        player = Player(
            id=123,
            name="Test Player",
            position="Forward",
            nationality="England",
            date_of_birth="1990-01-01",
            age=35
        )

        repr_str = repr(player)
        assert "Player" in repr_str
        assert "123" in repr_str
        assert "Test Player" in repr_str
        assert "Forward" in repr_str
        assert "England" in repr_str
