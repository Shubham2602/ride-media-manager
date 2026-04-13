from dataclasses import dataclass
from typing import Optional


@dataclass
class MediaFile:
    id: Optional[int]
    import_job_id: int
    source_path: str
    source_relative_path: str
    destination_path: Optional[str]
    source_type: str
    media_type: str
    filename: str
    extension: str
    size_bytes: int
    modified_time: str
    quick_fingerprint: Optional[str] = None
    full_hash: Optional[str] = None
    file_status: str = "queued"
    copied_at: Optional[str] = None
    verified_at: Optional[str] = None