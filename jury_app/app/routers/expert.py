from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.expert import Expert
from app.models.project import Project
from app.main import templates

router = APIRouter()


def get_current_expert(request: Request, db: Session) -> Expert | None:
    expert_id = request.cookies.get("expert_id")
    if not expert_id:
        return None

    return db.query(Expert).filter(Expert.id == int(expert_id)).first()


@router.get("/expert", response_class=HTMLResponse)
def expert_dashboard(request: Request, db: Session = Depends(get_db)):
    expert = get_current_expert(request, db)
    if not expert:
        return RedirectResponse(url="/login", status_code=303)

    projects = (
        db.query(Project)
        .filter(Project.is_active == True)
        .order_by(Project.sort_order.asc(), Project.id.asc())
        .all()
    )

    return templates.TemplateResponse(
        "expert/dashboard.html",
        {
            "request": request,
            "expert": expert,
            "projects": projects,
        },
    )