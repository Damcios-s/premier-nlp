"""
Unit tests for the FootballAPIService class.
Tests cover API requests, caching, error handling, and team data retrieval functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import requests
import json

from services.football_api_service import FootballAPIService, FootballAPIError
from data_classes.team import Team
from config.settings import FootballAPIConfig


@pytest.fixture
def mock_config():
    """Create a mock FootballAPIConfig for testing."""
    config = Mock(spec=FootballAPIConfig)
    config.api_key = "test_api_key"
    config.base_url = "https://api.football-data.org/v4"
    config.competition_code = "PL"
    return config


@pytest.fixture
def api_service(mock_config):
    """Create a FootballAPIService instance with mocked config."""
    return FootballAPIService(mock_config)


@pytest.fixture
def sample_teams_api_response():
    """Sample API response for teams endpoint."""
    return {
        "teams": [
            {
                "id": 1,
                "name": "Liverpool FC",
                "shortName": "Liverpool",
                "tla": "LIV",
                "founded": 1892,
                "clubColors": "Red / White",
                "venue": "Anfield",
                "squad": []
            },
            {
                "id": 2,
                "name": "Manchester United FC",
                "shortName": "Man United",
                "tla": "MUN",
                "founded": 1878,
                "clubColors": "Red / Yellow / Black",
                "venue": "Old Trafford",
                "squad": []
            }
        ]
    }


@pytest.fixture
def sample_team_api_response():
    """Sample API response for single team endpoint."""
    return {
        "id": 1,
        "name": "Liverpool FC",
        "shortName": "Liverpool",
        "tla": "LIV",
        "founded": 1892,
        "clubColors": "Red / White",
        "venue": "Anfield",
        "squad": [
            {"id": 101, "name": "Player 1", "position": "Goalkeeper"},
            {"id": 102, "name": "Player 2", "position": "Defender"}
        ]
    }


class TestFootballAPIServiceInitialization:
    """Test FootballAPIService initialization."""

    def test_initialization_with_config(self, mock_config):
        """Test proper initialization with config."""
        service = FootballAPIService(mock_config)

        assert service.config == mock_config
        assert service.headers == {"X-Auth-Token": "test_api_key"}
        assert service._teams_cache is None
        assert service._cache_timestamp is None

    def test_headers_created_correctly(self, mock_config):
        """Test that headers are created with the API key."""
        service = FootballAPIService(mock_config)
        expected_headers = {"X-Auth-Token": "test_api_key"}
        assert service.headers == expected_headers


class TestCacheManagement:
    """Test cache management functionality."""

    def test_is_cache_valid_no_timestamp(self, api_service):
        """Test cache validity when no timestamp exists."""
        assert not api_service._is_cache_valid()

    def test_is_cache_valid_recent_timestamp(self, api_service):
        """Test cache validity with recent timestamp."""
        api_service._cache_timestamp = datetime.now() - timedelta(hours=1)
        assert api_service._is_cache_valid(ttl_hours=24)

    def test_is_cache_valid_expired_timestamp(self, api_service):
        """Test cache validity with expired timestamp."""
        api_service._cache_timestamp = datetime.now() - timedelta(hours=25)
        assert not api_service._is_cache_valid(ttl_hours=24)

    def test_is_cache_valid_custom_ttl(self, api_service):
        """Test cache validity with custom TTL."""
        api_service._cache_timestamp = datetime.now() - timedelta(hours=2)
        assert not api_service._is_cache_valid(ttl_hours=1)
        assert api_service._is_cache_valid(ttl_hours=3)


class TestMakeRequest:
    """Test the _make_request private method."""

    @patch('services.football_api_service.requests.get')
    def test_make_request_success(self, mock_get, api_service):
        """Test successful API request."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = api_service._make_request("test-endpoint")

        assert result == {"data": "test"}
        expected_url = "https://api.football-data.org/v4/test-endpoint"
        mock_get.assert_called_once_with(
            expected_url,
            headers={"X-Auth-Token": "test_api_key"},
            timeout=10
        )

    @patch('services.football_api_service.requests.get')
    def test_make_request_with_leading_slash(self, mock_get, api_service):
        """Test API request with leading slash in endpoint."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api_service._make_request("/test-endpoint")

        expected_url = "https://api.football-data.org/v4/test-endpoint"
        mock_get.assert_called_once_with(
            expected_url,
            headers={"X-Auth-Token": "test_api_key"},
            timeout=10
        )

    @patch('services.football_api_service.requests.get')
    def test_make_request_handles_trailing_slash_in_base_url(self, mock_get, mock_config):
        """Test API request handling of trailing slash in base URL."""
        mock_config.base_url = "https://api.football-data.org/v4/"
        service = FootballAPIService(mock_config)

        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service._make_request("test-endpoint")

        expected_url = "https://api.football-data.org/v4/test-endpoint"
        mock_get.assert_called_once_with(
            expected_url,
            headers={"X-Auth-Token": "test_api_key"},
            timeout=10
        )

    @patch('services.football_api_service.requests.get')
    def test_make_request_http_error(self, mock_get, api_service):
        """Test API request with HTTP error."""
        mock_get.side_effect = requests.exceptions.HTTPError("404 Not Found")

        with pytest.raises(FootballAPIError, match="Failed to fetch data.*404 Not Found"):
            api_service._make_request("test-endpoint")

    @patch('services.football_api_service.requests.get')
    def test_make_request_connection_error(self, mock_get, api_service):
        """Test API request with connection error."""
        mock_get.side_effect = requests.exceptions.ConnectionError(
            "Connection failed")

        with pytest.raises(FootballAPIError, match="Failed to fetch data.*Connection failed"):
            api_service._make_request("test-endpoint")

    @patch('services.football_api_service.requests.get')
    def test_make_request_timeout_error(self, mock_get, api_service):
        """Test API request with timeout error."""
        mock_get.side_effect = requests.exceptions.Timeout("Timeout occurred")

        with pytest.raises(FootballAPIError, match="Failed to fetch data.*Timeout occurred"):
            api_service._make_request("test-endpoint")

    @patch('services.football_api_service.requests.get')
    def test_make_request_json_decode_error(self, mock_get, api_service):
        """Test API request with JSON decode error."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError(
            "Invalid JSON", "", 0)
        mock_get.return_value = mock_response

        with pytest.raises(FootballAPIError, match="Invalid JSON response"):
            api_service._make_request("test-endpoint")


class TestGetTeams:
    """Test the get_teams method."""

    @patch.object(FootballAPIService, '_make_request')
    @patch('data_classes.team.Team.from_api_data')
    def test_get_teams_success_no_cache(self, mock_team_from_api, mock_make_request,
                                        api_service, sample_teams_api_response):
        """Test successful teams retrieval without cache."""
        # Setup mocks
        mock_make_request.return_value = sample_teams_api_response
        mock_team1 = Mock(spec=Team)
        mock_team2 = Mock(spec=Team)
        mock_team_from_api.side_effect = [mock_team1, mock_team2]

        result = api_service.get_teams(use_cache=False)

        assert result == [mock_team1, mock_team2]
        mock_make_request.assert_called_once_with("competitions/PL/teams")
        assert mock_team_from_api.call_count == 2

        # Verify cache was updated
        assert api_service._teams_cache == [mock_team1, mock_team2]
        assert api_service._cache_timestamp is not None

    @patch('data_classes.team.Team.from_api_data')
    def test_get_teams_uses_valid_cache(self, mock_team_from_api, api_service):
        """Test that valid cache is used instead of making API call."""
        # Setup cache
        mock_team = Mock(spec=Team)
        api_service._teams_cache = [mock_team]
        api_service._cache_timestamp = datetime.now() - timedelta(hours=1)

        result = api_service.get_teams(use_cache=True, cache_ttl_hours=24)

        assert result == [mock_team]
        mock_team_from_api.assert_not_called()

    @patch.object(FootballAPIService, '_make_request')
    @patch('data_classes.team.Team.from_api_data')
    def test_get_teams_expired_cache(self, mock_team_from_api, mock_make_request,
                                     api_service, sample_teams_api_response):
        """Test that expired cache triggers API call."""
        # Setup expired cache
        old_mock_team = Mock(spec=Team)
        api_service._teams_cache = [old_mock_team]
        api_service._cache_timestamp = datetime.now() - timedelta(hours=25)

        # Setup new API response
        mock_make_request.return_value = sample_teams_api_response
        new_mock_team = Mock(spec=Team)
        mock_team_from_api.return_value = new_mock_team

        result = api_service.get_teams(cache_ttl_hours=24)

        mock_make_request.assert_called_once()
        assert result != [old_mock_team]

    @patch.object(FootballAPIService, '_make_request')
    def test_get_teams_api_error_with_cache_fallback(self, mock_make_request, api_service):
        """Test fallback to stale cache when API fails."""
        # Setup stale cache
        mock_team = Mock(spec=Team)
        api_service._teams_cache = [mock_team]
        api_service._cache_timestamp = datetime.now() - timedelta(hours=25)

        # Setup API to fail
        mock_make_request.side_effect = FootballAPIError("API failed")

        result = api_service.get_teams()

        assert result == [mock_team]

    @patch.object(FootballAPIService, '_make_request')
    def test_get_teams_api_error_no_cache(self, mock_make_request, api_service):
        """Test error propagation when API fails and no cache exists."""
        mock_make_request.side_effect = FootballAPIError("API failed")

        with pytest.raises(FootballAPIError, match="API failed"):
            api_service.get_teams()

    @patch.object(FootballAPIService, '_make_request')
    @patch('data_classes.team.Team.from_api_data')
    def test_get_teams_empty_teams_response(self, mock_team_from_api, mock_make_request, api_service):
        """Test handling of empty teams response."""
        mock_make_request.return_value = {"teams": []}

        result = api_service.get_teams()

        assert result == []
        mock_team_from_api.assert_not_called()

    @patch.object(FootballAPIService, '_make_request')
    @patch('data_classes.team.Team.from_api_data')
    def test_get_teams_missing_teams_key(self, mock_team_from_api, mock_make_request, api_service):
        """Test handling of response missing teams key."""
        mock_make_request.return_value = {"other_data": "value"}

        result = api_service.get_teams()

        assert result == []
        mock_team_from_api.assert_not_called()


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases."""

    def test_service_state_after_multiple_operations(self, api_service, sample_teams_api_response):
        """Test service state consistency after multiple operations."""
        with patch.object(api_service, '_make_request') as mock_request:
            with patch('data_classes.team.Team.from_api_data') as mock_team_from_api:
                mock_request.return_value = sample_teams_api_response
                mock_team = Mock(spec=Team)
                mock_team_from_api.return_value = mock_team

                # First call should make request and cache
                result1 = api_service.get_teams()
                assert len(result1) == 2
                assert api_service._teams_cache is not None
                assert api_service._cache_timestamp is not None

                # Second call should use cache
                result2 = api_service.get_teams()
                assert result2 == result1
                assert mock_request.call_count == 1  # Should only be called once

    @patch.object(FootballAPIService, '_make_request')
    @patch('data_classes.team.Team.from_api_data')
    def test_concurrent_cache_behavior(self, mock_team_from_api, mock_make_request, api_service):
        """Test cache behavior under concurrent-like conditions."""
        mock_make_request.return_value = {"teams": [{"id": 1, "name": "Test"}]}
        mock_team = Mock(spec=Team)
        mock_team_from_api.return_value = mock_team

        # Simulate rapid successive calls
        results = []
        for _ in range(5):
            results.append(api_service.get_teams())

        # Should use cache after first call
        assert all(result == results[0] for result in results)
        assert mock_make_request.call_count == 1

    def test_service_with_different_config_values(self, mock_config):
        """Test service with various config values."""
        # Test with different competition codes
        mock_config.competition_code = "PD"  # La Liga
        service = FootballAPIService(mock_config)

        with patch.object(service, '_make_request') as mock_request:
            mock_request.return_value = {"teams": []}
            service.get_teams(use_cache=False)
            mock_request.assert_called_once_with("competitions/PD/teams")
