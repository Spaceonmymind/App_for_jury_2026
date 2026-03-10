from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.expert import Expert
from app.services.auth import verify_password
from app.main import templates

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "error": None},
    )


@router.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    expert = db.query(Expert).filter(Expert.login == login).first()

    if not expert:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Пользователь не найден"},
        )

    if not verify_password(password, expert.password_hash):
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Неверный пароль"},
        )

    redirect_url = "/admin" if expert.is_admin else "/expert"

    response = RedirectResponse(url=redirect_url, status_code=303)
    response.set_cookie(
        key="expert_id",
        value=str(expert.id),
        httponly=True,
    )
    return response