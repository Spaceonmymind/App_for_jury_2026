from app.db import SessionLocal
from app.models.expert import Expert
from app.services.auth import hash_password

db = SessionLocal()

admin = Expert(
    full_name="Администратор",
    login="admin",
    password_hash=hash_password("admin123"),
    is_admin=True,
)

db.add(admin)
db.commit()

print("Admin created")
print("Admin created")