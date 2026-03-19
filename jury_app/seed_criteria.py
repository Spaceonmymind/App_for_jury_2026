from app.db import SessionLocal
from app.models.criterion import Criterion

db = SessionLocal()

criteria = [
    Criterion(
        name="Инновационность / оригинальность",
        description="Оценивается уникальность предложенного сервиса, его отличительность от существующих аналогов, а также способность принципиально по-новому решать выявленную проблему и удовлетворять потребности пользователей.",
        max_score=10,
        sort_order=1,
        is_active=True,
    ),
    Criterion(
        name="Реализуемость",
        description="Оценивается возможность сделать предложенный сервис реальным, включая предлагаемые рабочие процессы, технические аспекты внедрения и финансовую модель.",
        max_score=10,
        sort_order=2,
        is_active=True,
    ),
    Criterion(
        name="Выступление, презентация, аргументация",
        description="Оценивается способность четко и убедительно представить свою идею, включая структуру доклада, визуальные материалы, а также умение аргументированно отвечать на вопросы.",
        max_score=10,
        sort_order=3,
        is_active=True,
    ),
]

db.query(Criterion).delete()
db.add_all(criteria)
db.commit()

print("Criteria created")