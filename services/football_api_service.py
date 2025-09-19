import requests
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from data_classes.team import Team
from config.settings import FootballAPIConfig

logger = logging.getLogger(__name__)


class FootballAPIError(Exception):
    """Custom exception for Football API errors."""
    pass


class FootballAPIService:
    def __init__(self, config: FootballAPIConfig):
        self.config = config
        self.headers = {"X-Auth-Token": config.api_key}
        self._teams_cache: Optional[List[Team]] = None
        self._cache_timestamp: Optional[datetime] = None

    def _is_cache_valid(self, ttl_hours: int = 24) -> bool:
        """Check if the cache is still valid."""
        if not self._cache_timestamp:
            return False
        return datetime.now() - self._cache_timestamp < timedelta(hours=ttl_hours)

    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """Make a request to the Football API with error handling."""
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise FootballAPIError(f"Failed to fetch data from {url}: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise FootballAPIError(f"Invalid JSON response from {url}")

    def get_teams(self, use_cache: bool = True, cache_ttl_hours: int = 24) -> List[Team]:
        """Get all teams for the competition."""
        if use_cache and self._teams_cache and self._is_cache_valid(cache_ttl_hours):
            logger.info("Using cached teams data")
            return self._teams_cache

        logger.info("Fetching teams data from API")
        endpoint = f"competitions/{self.config.competition_code}/teams"

        try:
            data = self._make_request(endpoint)
            teams_data = data.get("teams", [])
            teams = [Team.from_api_data(team_data) for team_data in teams_data]

            # Cache the results
            self._teams_cache = teams
            self._cache_timestamp = datetime.now()

            logger.info(f"Successfully loaded {len(teams)} teams")
            return teams

        except FootballAPIError:
            # If API fails and we have cached data, use it
            if self._teams_cache:
                logger.warning("API failed, using stale cached data")
                return self._teams_cache
            raise
