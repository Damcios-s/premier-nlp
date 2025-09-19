from datetime import date
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
            age=cls.calculate_age(data.get('dateOfBirth'))
        )

    @staticmethod
    def calculate_age(date_of_birth: Optional[str]) -> Optional[int]:
        if not date_of_birth:
            return None

        try:
            birth_date = date.fromisoformat(date_of_birth)
            today = date.today()
            age = today.year - birth_date.year - \
                ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age if age >= 0 else None

        except ValueError:
            return None
