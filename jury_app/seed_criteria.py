from app.db import SessionLocal
from app.models.criterion import Criterion

db = SessionLocal()

criteria = [
    Criterion(
        name="Актуальность",
        description="Насколько проект соответствует актуальным задачам и потребностям",
        max_score=10,
        sort_order=1,
        is_active=True,
    ),
    Criterion(
        name="Проработанность решения",
        description="Насколько детально продумано предлагаемое решение",
        max_score=10,
        sort_order=2,
        is_active=True,
    ),
    Criterion(
        name="Практическая значимость",
        description="Насколько проект применим на практике",
        max_score=10,
        sort_order=3,
        is_active=True,
    ),
    Criterion(
        name="Качество презентации",
        description="Насколько понятно и убедительно представлен проект",
        max_score=10,
        sort_order=4,
        is_active=True,
    ),
]

db.add_all(criteria)
db.commit()

print("Criteria created")