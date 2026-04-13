from dataclasses import dataclass
from typing import Optional


@dataclass
class Device:
    id: Optional[int]
    device_name: str
    mount_path: str
    status: str
    detected_at: str
    last_seen_at: str