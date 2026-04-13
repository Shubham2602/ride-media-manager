from datetime import datetime
from pathlib import Path

from app.config import settings
from app.schemas.device import ScanResult, ScanResultFile
from app.services.device_service import device_service
from app.utils.hashing import file_quick_fingerprint
from app.utils.media_utils import classify_source


class MediaScannerService:
    def scan_device(self, device_id: int) -> ScanResult:
        device = device_service.get_device(device_id)

        if device["status"] != "connected":
            raise ValueError("Device is not connected")

        mount_path = Path(device["mount_path"])
        files = []
        total_bytes = 0

        for file_path in mount_path.rglob("*"):
            if not file_path.is_file():
                continue

            extension = file_path.suffix.lower()
            media_type = settings.media_extensions.get(extension)
            if not media_type:
                continue

            stat = file_path.stat()
            relative_path = str(file_path.relative_to(mount_path))

            scan_file = ScanResultFile(
                source_path=str(file_path.resolve()),
                source_relative_path=relative_path,
                filename=file_path.name,
                extension=extension,
                media_type=media_type,
                size_bytes=stat.st_size,
                modified_time=datetime.utcfromtimestamp(
                    stat.st_mtime
                ).isoformat() + "Z",
                source_type=classify_source(file_path),
                quick_fingerprint=file_quick_fingerprint(file_path),
            )

            files.append(scan_file)
            total_bytes += stat.st_size

        return ScanResult(
            device_id=device_id,
            file_count=len(files),
            total_bytes=total_bytes,
            files=files,
        )


scanner_service = MediaScannerService()