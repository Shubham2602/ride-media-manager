from typing import List

from pydantic import BaseModel


class DeviceResponse(BaseModel):
    id: int
    device_name: str
    mount_path: str
    status: str
    detected_at: str
    last_seen_at: str


class ScanResultFile(BaseModel):
    source_path: str
    source_relative_path: str
    filename: str
    extension: str
    media_type: str
    size_bytes: int
    modified_time: str
    source_type: str
    quick_fingerprint: str


class ScanResult(BaseModel):
    device_id: int
    file_count: int
    total_bytes: int
    files: List[ScanResultFile]