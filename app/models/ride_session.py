from dataclasses import dataclass
from typing import Optional


@dataclass
class RideSession:
    id: Optional[int]
    name: str
    slug: str
    ride_date: str
    archive_path: str
    status: str
    created_at: str
    updated_at: str