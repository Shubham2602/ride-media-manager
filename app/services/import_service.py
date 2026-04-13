import shutil
from pathlib import Path

from app.config import settings
from app.db import db, get_connection
from app.services.device_service import device_service
from app.services.duplicate_detector import duplicate_detector
from app.services.media_scanner import scanner_service
from app.services.ride_service import ride_service
from app.services.verifier import verifier
from app.utils.file_utils import ensure_dir
from app.utils.time_utils import now_iso


class ImportService:
    def create_import_job(self, ride_session_id: int, device_id: int):
        ride = ride_service.get_ride(ride_session_id)
        device = device_service.get_device(device_id)

        if device["status"] != "connected":
            raise ValueError("Device is not connected")

        current_time = now_iso()

        with db.lock:
            with get_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO import_jobs (
                        ride_session_id,
                        device_id,
                        job_status,
                        started_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (ride["id"], device["id"], "pending", current_time),
                )
                connection.commit()

                job_id = connection.execute(
                    "SELECT last_insert_rowid()"
                ).fetchone()[0]

                row = connection.execute(
                    "SELECT * FROM import_jobs WHERE id = ?",
                    (job_id,),
                ).fetchone()

        return row

    def get_job(self, job_id: int):
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM import_jobs WHERE id = ?",
                (job_id,),
            ).fetchone()

        if not row:
            raise ValueError("Import job not found")

        return row

    def list_job_files(self, job_id: int):
        with get_connection() as connection:
            return connection.execute(
                """
                SELECT *
                FROM media_files
                WHERE import_job_id = ?
                ORDER BY id ASC
                """,
                (job_id,),
            ).fetchall()

    def start_import(self, job_id: int):
        job = self.get_job(job_id)
        ride = ride_service.get_ride(job["ride_session_id"])
        device = device_service.get_device(job["device_id"])
        scan_result = scanner_service.scan_device(device["id"])

        archive_root = Path(ride["archive_path"])

        with db.lock:
            with get_connection() as connection:
                connection.execute(
                    """
                    UPDATE import_jobs
                    SET job_status = ?, total_files = ?, total_bytes = ?
                    WHERE id = ?
                    """,
                    (
                        "importing",
                        scan_result.file_count,
                        scan_result.total_bytes,
                        job_id,
                    ),
                )
                connection.commit()

        copied_files = 0
        copied_bytes = 0
        skipped_duplicates = 0
        failed_files = 0

        for file_info in scan_result.files:
            source_path = Path(file_info.source_path)
            destination_dir = archive_root / "imports" / file_info.source_type / "raw"
            ensure_dir(destination_dir)

            destination_path = destination_dir / file_info.filename
            temp_destination_path = destination_path.with_suffix(
                destination_path.suffix + settings.temp_extension
            )

            with db.lock:
                with get_connection() as connection:
                    is_duplicate = duplicate_detector.is_duplicate(
                        quick_fingerprint=file_info.quick_fingerprint,
                        size_bytes=file_info.size_bytes,
                    )

                    if is_duplicate:
                        connection.execute(
                            """
                            INSERT INTO media_files (
                                import_job_id,
                                source_path,
                                source_relative_path,
                                destination_path,
                                source_type,
                                media_type,
                                filename,
                                extension,
                                size_bytes,
                                modified_time,
                                quick_fingerprint,
                                file_status
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                job_id,
                                file_info.source_path,
                                file_info.source_relative_path,
                                str(destination_path),
                                file_info.source_type,
                                file_info.media_type,
                                file_info.filename,
                                file_info.extension,
                                file_info.size_bytes,
                                file_info.modified_time,
                                file_info.quick_fingerprint,
                                "skipped_duplicate",
                            ),
                        )

                        skipped_duplicates += 1

                        connection.execute(
                            """
                            UPDATE import_jobs
                            SET skipped_duplicates = ?
                            WHERE id = ?
                            """,
                            (skipped_duplicates, job_id),
                        )
                        connection.commit()
                        continue

                    connection.execute(
                        """
                        INSERT INTO media_files (
                            import_job_id,
                            source_path,
                            source_relative_path,
                            destination_path,
                            source_type,
                            media_type,
                            filename,
                            extension,
                            size_bytes,
                            modified_time,
                            quick_fingerprint,
                            file_status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            job_id,
                            file_info.source_path,
                            file_info.source_relative_path,
                            str(destination_path),
                            file_info.source_type,
                            file_info.media_type,
                            file_info.filename,
                            file_info.extension,
                            file_info.size_bytes,
                            file_info.modified_time,
                            file_info.quick_fingerprint,
                            "queued",
                        ),
                    )
                    connection.commit()

                    media_file_id = connection.execute(
                        "SELECT last_insert_rowid()"
                    ).fetchone()[0]

            try:
                shutil.copy2(source_path, temp_destination_path)

                if not verifier.verify_size(source_path, temp_destination_path):
                    raise IOError("Copied file size mismatch")

                temp_destination_path.replace(destination_path)

                copied_files += 1
                copied_bytes += file_info.size_bytes

                with db.lock:
                    with get_connection() as connection:
                        connection.execute(
                            """
                            UPDATE media_files
                            SET file_status = ?, copied_at = ?, verified_at = ?
                            WHERE id = ?
                            """,
                            ("verified", now_iso(), now_iso(), media_file_id),
                        )
                        connection.execute(
                            """
                            UPDATE import_jobs
                            SET copied_files = ?, copied_bytes = ?
                            WHERE id = ?
                            """,
                            (copied_files, copied_bytes, job_id),
                        )
                        connection.commit()

            except Exception as exc:
                failed_files += 1

                if temp_destination_path.exists():
                    temp_destination_path.unlink(missing_ok=True)

                with db.lock:
                    with get_connection() as connection:
                        connection.execute(
                            """
                            UPDATE media_files
                            SET file_status = ?
                            WHERE id = ?
                            """,
                            ("failed", media_file_id),
                        )
                        connection.execute(
                            """
                            UPDATE import_jobs
                            SET failed_files = ?, error_message = ?
                            WHERE id = ?
                            """,
                            (failed_files, str(exc), job_id),
                        )
                        connection.commit()

        final_status = "completed" if failed_files == 0 else "partial"

        with db.lock:
            with get_connection() as connection:
                connection.execute(
                    """
                    UPDATE import_jobs
                    SET job_status = ?, completed_at = ?
                    WHERE id = ?
                    """,
                    (final_status, now_iso(), job_id),
                )
                connection.commit()

        return self.get_job(job_id)


import_service = ImportService()