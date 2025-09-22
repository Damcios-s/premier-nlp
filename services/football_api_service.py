import requests
import json
import time
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

    def _make_request(self, endpoint: str, max_retries: int = 3) -> Dict[str, Any]:
        """Make a request to the Football API with error handling and retry logic."""
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        last_exception = None

        for attempt in range(max_retries + 1):  # +1 to include the initial attempt
            try:
                if attempt > 0:
                    # Exponential backoff: 1s, 2s, 4s for retries 1, 2, 3
                    wait_time = 2 ** (attempt - 1)
                    logger.debug(
                        f"Retrying request in {wait_time}s (attempt {attempt + 1}/{max_retries + 1})")
                    time.sleep(wait_time)

                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.warning(
                    f"API request attempt {attempt + 1} failed: {e}")

                if isinstance(e, requests.exceptions.HTTPError) and 400 <= e.response.status_code < 500:
                    logger.error(
                        f"Client error {e.response.status_code}, not retrying")
                    break

                if attempt == max_retries:
                    logger.error(f"All {max_retries + 1} attempts failed")

            except json.JSONDecodeError as e:
                last_exception = e
                logger.warning(
                    f"JSON decode error on attempt {attempt + 1}: {e}")
                if attempt == max_retries:
                    logger.error(
                        f"All {max_retries + 1} attempts failed with JSON decode errors")

        # If we get here, all retries failed
        if isinstance(last_exception, json.JSONDecodeError):
            raise FootballAPIError(
                f"Invalid JSON response from {url} after {max_retries + 1} attempts")
        else:
            raise FootballAPIError(
                f"Failed to fetch data from {url} after {max_retries + 1} attempts: {last_exception}")

    def get_teams(self, use_cache: bool = True, cache_ttl_hours: int = 24) -> List[Team]:
        """Get all teams for the competition."""
        if use_cache and self._teams_cache and self._is_cache_valid(cache_ttl_hours):
            logger.debug("Using cached teams data")
            return self._teams_cache

        logger.debug("Fetching teams data from API")
        endpoint = f"competitions/{self.config.competition_code}/teams"

        try:
            data = self._make_request(endpoint)
            teams_data = data.get("teams", [])
            teams = [Team.from_api_data(team_data) for team_data in teams_data]

            # Cache the results
            self._teams_cache = teams
            self._cache_timestamp = datetime.now()

            logger.debug(f"Successfully loaded {len(teams)} teams")
            return teams

        except FootballAPIError:
            # If API fails and we have cached data, use it
            if self._teams_cache:
                logger.warning("API failed, using stale cached data")
                return self._teams_cache
            raise
