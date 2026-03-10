from app.db import SessionLocal
from app.models.expert import Expert
from app.services.auth import hash_password

db = SessionLocal()

expert = Expert(
    full_name="Иван Петров",
    login="expert1",
    password_hash=hash_password("123456"),
    is_admin=False,
    is_active=True,
)

db.add(expert)
db.commit()

print("Expert created")