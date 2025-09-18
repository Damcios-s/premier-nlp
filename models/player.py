from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Player:
    id: int
    name: str
    position: Optional[str] = None
    nationality: Optional[str] = None
    date_of_birth: Optional[str] = None
    age: Optional[int] = None

    @classmethod
    def from_api_data(cls, data: Dict[str, Any]) -> 'Player':
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            position=data.get('position'),
            nationality=data.get('nationality'),
            date_of_birth=data.get('dateOfBirth'),
            age=data.get('age')
        )
