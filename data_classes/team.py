from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from data_classes.player import Player


@dataclass
class Team:
    id: int
    name: str
    short_name: Optional[str] = None
    tla: Optional[str] = None  # Three Letter Abbreviation
    crest_url: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    founded: Optional[int] = None
    club_colors: Optional[str] = None
    venue: Optional[str] = None
    squad: List[Player] = None

    def __post_init__(self):
        if self.squad is None:
            self.squad = []

    @classmethod
    def from_api_data(cls, data: Dict[str, Any]) -> 'Team':
        squad_data = data.get('squad', [])
        squad = [Player.from_api_data(player_data)
                 for player_data in squad_data] if squad_data else []

        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            short_name=data.get('shortName'),
            tla=data.get('tla'),
            # crest_url=data.get('crest'),
            # address=data.get('address'),
            # website=data.get('website'),
            founded=data.get('founded'),
            club_colors=data.get('clubColors'),
            venue=data.get('venue'),
            squad=squad
        )
