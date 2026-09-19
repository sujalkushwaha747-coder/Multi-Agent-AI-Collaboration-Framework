from sqlalchemy.orm import Session

from app.models.benchmark import BenchmarkPrompt

SEED_BENCHMARKS = [
    (
        "academic",
        "Explain the concept of Retrieval-Augmented Generation and its advantages.",
    ),
    (
        "academic",
        "Write a concise literature review on Large Language Models.",
    ),
    (
        "academic",
        "Compare supervised learning and unsupervised learning.",
    ),
    (
        "technical",
        "Design a high-level architecture for an online library management system.",
    ),
    (
        "technical",
        "Create an SRS outline for an online examination system.",
    ),
    (
        "technical",
        "Explain how to design a REST API for a student management system.",
    ),
]


def seed_benchmarks(db: Session) -> int:
    inserted = 0
    for category, prompt in SEED_BENCHMARKS:
        exists = (
            db.query(BenchmarkPrompt)
            .filter(BenchmarkPrompt.prompt == prompt)
            .one_or_none()
        )
        if exists:
            continue
        db.add(BenchmarkPrompt(category=category, prompt=prompt, source="seed"))
        inserted += 1
    db.commit()
    return inserted

