from pathlib import Path
from typing import Dict

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Ride Media Manager"
    app_version: str = "0.1.0"
    debug: bool = True

    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = base_dir / "data"
    db_dir: Path = data_dir / "db"
    db_path: Path = db_dir / "ride_media_manager.db"

    archive_root: Path = data_dir / "ride_archive"

    # Mock/dev devices
    source_root: Path = data_dir / "connected_devices"

    # Real mounted USB / SD / camera devices on Raspberry Pi
    media_mount_root: Path = Path("/media/pi")

    temp_dir: Path = data_dir / "temp"
    log_dir: Path = data_dir / "logs"

    temp_extension: str = ".part"

    media_extensions: Dict[str, str] = {
        ".mp4": "video",
        ".mov": "video",
        ".mkv": "video",
        ".avi": "video",
        ".jpg": "image",
        ".jpeg": "image",
        ".png": "image",
        ".dng": "image",
        ".wav": "audio",
        ".m4a": "audio",
    }

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.archive_root.mkdir(parents=True, exist_ok=True)
        self.source_root.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()