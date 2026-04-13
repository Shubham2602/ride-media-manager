from typing import Optional

from pydantic import BaseModel


class MediaFileResponse(BaseModel):
    id: int
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
    quick_fingerprint: Optional[str]
    full_hash: Optional[str]
    file_status: str
    copied_at: Optional[str]
    verified_at: Optional[str]