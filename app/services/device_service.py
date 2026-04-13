from app.config import settings
from app.db import db, get_connection
from app.utils.time_utils import now_iso


class DeviceService:
    def refresh_devices(self) -> None:
        current_time = now_iso()
        available_paths = [path for path in settings.source_root.iterdir() if path.is_dir()]

        with db.lock:
            with get_connection() as connection:
                existing_rows = connection.execute(
                    "SELECT * FROM devices"
                ).fetchall()

                existing_by_mount = {
                    row["mount_path"]: row for row in existing_rows
                }

                seen_mount_paths = set()

                for path in available_paths:
                    mount_path = str(path.resolve())
                    device_name = path.name
                    seen_mount_paths.add(mount_path)

                    existing = existing_by_mount.get(mount_path)
                    if existing:
                        connection.execute(
                            """
                            UPDATE devices
                            SET status = ?, last_seen_at = ?
                            WHERE id = ?
                            """,
                            ("connected", current_time, existing["id"]),
                        )
                    else:
                        connection.execute(
                            """
                            INSERT INTO devices (
                                device_name,
                                mount_path,
                                status,
                                detected_at,
                                last_seen_at
                            ) VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                device_name,
                                mount_path,
                                "connected",
                                current_time,
                                current_time,
                            ),
                        )

                for row in existing_rows:
                    if row["mount_path"] not in seen_mount_paths:
                        connection.execute(
                            """
                            UPDATE devices
                            SET status = ?
                            WHERE id = ?
                            """,
                            ("disconnected", row["id"]),
                        )

                connection.commit()

    def list_devices(self):
        self.refresh_devices()
        with get_connection() as connection:
            return connection.execute(
                "SELECT * FROM devices ORDER BY last_seen_at DESC"
            ).fetchall()

    def get_device(self, device_id: int):
        self.refresh_devices()
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM devices WHERE id = ?",
                (device_id,),
            ).fetchone()

        if not row:
            raise ValueError("Device not found")

        return row


device_service = DeviceService()