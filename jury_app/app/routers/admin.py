from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.expert import Expert
from app.main import templates

router = APIRouter()


def get_current_user(request: Request, db: Session) -> Expert | None:
    expert_id = request.cookies.get("expert_id")
    if not expert_id:
        return None

    return db.query(Expert).filter(Expert.id == int(expert_id)).first()


@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    if not user:
        return RedirectResponse(url="/login", status_code=303)

    if not user.is_admin:
        return RedirectResponse(url="/expert", status_code=303)

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "user": user,
        },
    )