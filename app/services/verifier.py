from pathlib import Path


class Verifier:
    def verify_size(self, source_path: Path, destination_path: Path) -> bool:
        if not source_path.exists() or not destination_path.exists():
            return False

        return source_path.stat().st_size == destination_path.stat().st_size


verifier = Verifier()