from app.db import SessionLocal
from app.models.project import Project

db = SessionLocal()

projects = [
    Project(
        title="Project AI",
        author_full_name="Иван Иванов",
        organization="Финансовый университет",
        description="Описание проекта 1",
        additional_info="Доп. информация 1",
        card_image="img/projects/test1.jpg",
        sort_order=1,
        is_active=True,
    ),
    Project(
        title="FinTrack",
        author_full_name="Мария Петрова",
        organization="МГУ",
        description="Описание проекта 2",
        additional_info="Доп. информация 2",
        card_image="img/projects/test1.jpg",
        sort_order=2,
        is_active=True,
    ),
    Project(
        title="Smart Budget",
        author_full_name="Алексей Смирнов",
        organization="ВШЭ",
        description="Описание проекта 3",
        additional_info="Доп. информация 3",
        card_image="img/projects/test1.jpg",
        sort_order=3,
        is_active=True,
    ),
]

db.add_all(projects)
db.commit()

print("Projects created")