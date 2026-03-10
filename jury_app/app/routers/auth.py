from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.expert import Expert
from app.services.auth import verify_password
from app.main import templates

router = APIRouter()


def get_current_user(request: Request, db: Session) -> Expert | None:
    expert_id = request.cookies.get("expert_id")
    if not expert_id:
        return None

    return db.query(Expert).filter(Expert.id == int(expert_id)).first()


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


@router.post("/logout")
def logout(
    request: Request,
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)

    if not user:
        return RedirectResponse(url="/login", status_code=303)

    if not verify_password(password, user.password_hash):
        redirect_url = "/admin?logout_error=1" if user.is_admin else "/expert?logout_error=1"
        return RedirectResponse(url=redirect_url, status_code=303)

    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("expert_id")
    return response