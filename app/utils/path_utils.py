def slugify(text: str) -> str:
    cleaned = text.strip().lower()
    return "_".join(cleaned.split())