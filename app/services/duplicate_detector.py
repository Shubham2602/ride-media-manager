from app.db import get_connection


class DuplicateDetector:
    def is_duplicate(self, quick_fingerprint: str, size_bytes: int) -> bool:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM media_files
                WHERE quick_fingerprint = ?
                  AND size_bytes = ?
                LIMIT 1
                """,
                (quick_fingerprint, size_bytes),
            ).fetchone()

        return row is not None


duplicate_detector = DuplicateDetector()