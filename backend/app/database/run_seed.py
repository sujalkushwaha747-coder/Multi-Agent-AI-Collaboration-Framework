from app.database.seed import seed_benchmarks
from app.database.session import SessionLocal


def main() -> None:
    db = SessionLocal()
    try:
        count = seed_benchmarks(db)
        print(f"Seeded {count} benchmark prompts.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

