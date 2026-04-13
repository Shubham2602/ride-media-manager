from pathlib import Path

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
    source_root: Path = data_dir / "connected_devices"
    temp_dir: Path = data_dir / "temp"
    log_dir: Path = data_dir / "logs"

    temp_extension: str = ".part"

    media_extensions: dict = {
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