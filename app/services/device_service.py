from pathlib import Path

from app.config import settings
from app.db import db, get_connection
from app.utils.time_utils import now_iso


class DeviceService:
    def refresh_devices(self):
        sources = [
            settings.source_root,
            settings.media_mount_root, # mock/dev
            Path("/media/pi"),                # real devices
        ]

        found_devices = []

        for root in sources:
            if not root.exists():
                continue

            for entry in root.iterdir():
                if entry.is_dir():
                    found_devices.append(entry.resolve())

        with db.lock:
            with get_connection() as conn:
                conn.execute("DELETE FROM devices")

                for device_path in found_devices:
                    conn.execute(
                        """
                        INSERT INTO devices (
                            device_name,
                            mount_path,
                            status,
                            created_at,
                            updated_at
                        ) VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            device_path.name,
                            str(device_path),
                            "connected",
                            now_iso(),
                            now_iso(),
                        ),
                    )

                conn.commit()

    def list_devices(self):
        with get_connection() as conn:
            return conn.execute(
                "SELECT * FROM devices ORDER BY created_at DESC"
            ).fetchall()


device_service = DeviceService()