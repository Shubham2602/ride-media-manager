from dataclasses import dataclass
from typing import Optional


@dataclass
class ImportJob:
    id: Optional[int]
    ride_session_id: int
    device_id: int
    job_status: str
    total_files: int = 0
    total_bytes: int = 0
    copied_files: int = 0
    copied_bytes: int = 0
    skipped_duplicates: int = 0
    failed_files: int = 0
    error_message: Optional[str] = None
    started_at: str = ""
    completed_at: Optional[str] = None