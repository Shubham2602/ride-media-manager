from pathlib import Path


class SourceClassifierService:
    def classify(self, path: Path) -> str:
        lowered = str(path).lower()

        if "dji" in lowered:
            return "dji_action"
        if "drone" in lowered:
            return "dji_drone"
        if "gopro" in lowered:
            return "gopro"
        if "iphone" in lowered or "android" in lowered or "phone" in lowered:
            return "phone"

        return "generic_sd"


source_classifier_service = SourceClassifierService()