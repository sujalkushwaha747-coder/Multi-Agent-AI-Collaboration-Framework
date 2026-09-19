from app.schemas.common import TaskCategory


ACADEMIC_TERMS = {
    "literature",
    "research",
    "paper",
    "review",
    "summarize",
    "summarise",
    "concept",
    "academic",
    "citation",
    "theory",
}

TECHNICAL_TERMS = {
    "architecture",
    "api",
    "database",
    "debug",
    "srs",
    "software",
    "system",
    "design",
    "code",
    "deployment",
}


def classify_task(prompt: str, manual_category: TaskCategory | None = None) -> TaskCategory:
    if manual_category in {"academic", "technical", "general"}:
        return manual_category
    words = set(prompt.lower().split())
    academic_score = len(words & ACADEMIC_TERMS)
    technical_score = len(words & TECHNICAL_TERMS)
    if academic_score > technical_score:
        return "academic"
    if technical_score > academic_score:
        return "technical"
    return "general"

