from typing import Optional

from pydantic import BaseModel


class ImportCreateRequest(BaseModel):
    ride_session_id: int
    device_id: int


class ImportJobResponse(BaseModel):
    id: int
    ride_session_id: int
    device_id: int
    job_status: str
    total_files: int
    total_bytes: int
    copied_files: int
    copied_bytes: int
    skipped_duplicates: int
    failed_files: int
    error_message: Optional[str]
    started_at: str
    completed_at: Optional[str]