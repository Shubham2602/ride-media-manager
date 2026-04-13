from datetime import datetime

from app.config import settings
from app.db import db, get_connection
from app.utils.file_utils import ensure_dir
from app.utils.path_utils import slugify
from app.utils.time_utils import now_iso


class RideService:
    def create_ride(self, name: str):
        current_time = now_iso()
        ride_date = datetime.utcnow().date().isoformat()
        base_slug = slugify(name)
        slug = base_slug

        with db.lock:
            with get_connection() as connection:
                index = 2
                while connection.execute(
                    "SELECT 1 FROM ride_sessions WHERE slug = ?",
                    (slug,),
                ).fetchone():
                    slug = f"{base_slug}_{index}"
                    index += 1

                archive_path = (
                    settings.archive_root / str(datetime.utcnow().year) / slug
                ).resolve()
                ensure_dir(archive_path)

                connection.execute(
                    """
                    INSERT INTO ride_sessions (
                        name,
                        slug,
                        ride_date,
                        archive_path,
                        status,
                        created_at,
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        slug,
                        ride_date,
                        str(archive_path),
                        "active",
                        current_time,
                        current_time,
                    ),
                )
                connection.commit()

                ride_id = connection.execute(
                    "SELECT last_insert_rowid()"
                ).fetchone()[0]

                row = connection.execute(
                    "SELECT * FROM ride_sessions WHERE id = ?",
                    (ride_id,),
                ).fetchone()

        return row

    def list_rides(self):
        with get_connection() as connection:
            return connection.execute(
                "SELECT * FROM ride_sessions ORDER BY created_at DESC"
            ).fetchall()

    def get_ride(self, ride_id: int):
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM ride_sessions WHERE id = ?",
                (ride_id,),
            ).fetchone()

        if not row:
            raise ValueError("Ride session not found")

        return row


ride_service = RideService()