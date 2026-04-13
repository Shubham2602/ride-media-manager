import sqlite3
import threading
from contextlib import contextmanager
from typing import Generator

from app.config import settings


class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.lock = threading.Lock()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection


db = Database(settings.db_path)


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    connection = db.connect()
    try:
        yield connection
    finally:
        connection.close()


def init_db() -> None:
    with db.lock:
        with get_connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS ride_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    slug TEXT NOT NULL UNIQUE,
                    ride_date TEXT NOT NULL,
                    archive_path TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_name TEXT NOT NULL,
                    mount_path TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    detected_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS import_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ride_session_id INTEGER NOT NULL,
                    device_id INTEGER NOT NULL,
                    job_status TEXT NOT NULL,
                    total_files INTEGER NOT NULL DEFAULT 0,
                    total_bytes INTEGER NOT NULL DEFAULT 0,
                    copied_files INTEGER NOT NULL DEFAULT 0,
                    copied_bytes INTEGER NOT NULL DEFAULT 0,
                    skipped_duplicates INTEGER NOT NULL DEFAULT 0,
                    failed_files INTEGER NOT NULL DEFAULT 0,
                    error_message TEXT,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    FOREIGN KEY (ride_session_id) REFERENCES ride_sessions(id),
                    FOREIGN KEY (device_id) REFERENCES devices(id)
                );

                CREATE TABLE IF NOT EXISTS media_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    import_job_id INTEGER NOT NULL,
                    source_path TEXT NOT NULL,
                    source_relative_path TEXT NOT NULL,
                    destination_path TEXT,
                    source_type TEXT NOT NULL,
                    media_type TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    extension TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    modified_time TEXT NOT NULL,
                    quick_fingerprint TEXT,
                    full_hash TEXT,
                    file_status TEXT NOT NULL,
                    copied_at TEXT,
                    verified_at TEXT,
                    FOREIGN KEY (import_job_id) REFERENCES import_jobs(id)
                );
                """
            )
            connection.commit()