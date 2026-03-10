from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.criterion import Criterion
from app.models.expert import Expert
from app.models.project import Project
from app.models.score import Score
from app.main import templates

router = APIRouter()


def get_current_expert(request: Request, db: Session) -> Expert | None:
    expert_id = request.cookies.get("expert_id")
    if not expert_id:
        return None

    return db.query(Expert).filter(Expert.id == int(expert_id)).first()


def get_active_projects(db: Session):
    return (
        db.query(Project)
        .filter(Project.is_active == True)
        .order_by(Project.sort_order.asc(), Project.id.asc())
        .all()
    )


def get_active_criteria(db: Session):
    return (
        db.query(Criterion)
        .filter(Criterion.is_active == True)
        .order_by(Criterion.sort_order.asc(), Criterion.id.asc())
        .all()
    )


def get_project_navigation(projects, project_id: int):
    current_index = next((index for index, p in enumerate(projects) if p.id == project_id), None)
    prev_project = projects[current_index - 1] if current_index is not None and current_index > 0 else None
    next_project = projects[current_index + 1] if current_index is not None and current_index < len(projects) - 1 else None
    return prev_project, next_project


def get_project_status_map(db: Session, expert_id: int, projects, criteria):
    criteria_count = len(criteria)
    status_map = {}

    for project in projects:
        score_count = (
            db.query(Score)
            .filter(
                Score.expert_id == expert_id,
                Score.project_id == project.id,
            )
            .count()
        )

        if score_count == 0:
            status_map[project.id] = {
                "code": "not_started",
                "label": "Не оценен",
            }
        elif score_count < criteria_count:
            status_map[project.id] = {
                "code": "partial",
                "label": "Заполнен частично",
            }
        else:
            status_map[project.id] = {
                "code": "completed",
                "label": "Оценен",
            }

    return status_map


def render_project_detail(
    request: Request,
    expert: Expert,
    project: Project,
    projects,
    db: Session,
    error: str | None = None,
    success: str | None = None,
):
    prev_project, next_project = get_project_navigation(projects, project.id)
    criteria = get_active_criteria(db)

    scores = (
        db.query(Score)
        .filter(Score.expert_id == expert.id, Score.project_id == project.id)
        .all()
    )

    score_map = {score.criterion_id: score.value for score in scores}
    is_project_completed = len(score_map) == len(criteria) and len(criteria) > 0

    return templates.TemplateResponse(
        "expert/project_detail.html",
        {
            "request": request,
            "expert": expert,
            "project": project,
            "prev_project": prev_project,
            "next_project": next_project,
            "criteria": criteria,
            "score_map": score_map,
            "is_project_completed": is_project_completed,
            "error": error,
            "success": success,
        },
    )


@router.get("/expert", response_class=HTMLResponse)
def expert_dashboard(request: Request, db: Session = Depends(get_db)):
    expert = get_current_expert(request, db)
    if not expert:
        return RedirectResponse(url="/login", status_code=303)

    if expert.is_admin:
        return RedirectResponse(url="/admin", status_code=303)

    projects = get_active_projects(db)
    criteria = get_active_criteria(db)
    status_map = get_project_status_map(db, expert.id, projects, criteria)

    return templates.TemplateResponse(
        "expert/dashboard.html",
        {
            "request": request,
            "expert": expert,
            "projects": projects,
            "status_map": status_map,
        },
    )


@router.get("/expert/projects/{project_id}", response_class=HTMLResponse)
def expert_project_detail(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    expert = get_current_expert(request, db)
    if not expert:
        return RedirectResponse(url="/login", status_code=303)

    if expert.is_admin:
        return RedirectResponse(url="/admin", status_code=303)

    projects = get_active_projects(db)
    project = next((p for p in projects if p.id == project_id), None)

    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    return render_project_detail(request, expert, project, projects, db)


@router.post("/expert/projects/{project_id}/score", response_class=HTMLResponse)
async def save_project_scores(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    expert = get_current_expert(request, db)
    if not expert:
        return RedirectResponse(url="/login", status_code=303)

    if expert.is_admin:
        return RedirectResponse(url="/admin", status_code=303)

    projects = get_active_projects(db)
    project = next((p for p in projects if p.id == project_id), None)

    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    criteria = get_active_criteria(db)

    form = await request.form()
    missing_fields = []

    for criterion in criteria:
        field_name = f"criterion_{criterion.id}"
        raw_value = form.get(field_name)

        if raw_value is None or raw_value == "":
            missing_fields.append(criterion.name)
            continue

        value = int(raw_value)

        if value < 0 or value > criterion.max_score:
            return render_project_detail(
                request,
                expert,
                project,
                projects,
                db,
                error=f"Критерий «{criterion.name}» заполнен некорректно.",
            )

        existing_score = (
            db.query(Score)
            .filter(
                Score.expert_id == expert.id,
                Score.project_id == project.id,
                Score.criterion_id == criterion.id,
            )
            .first()
        )

        if existing_score:
            existing_score.value = value
        else:
            new_score = Score(
                expert_id=expert.id,
                project_id=project.id,
                criterion_id=criterion.id,
                value=value,
            )
            db.add(new_score)

    if missing_fields:
        return render_project_detail(
            request,
            expert,
            project,
            projects,
            db,
            error="Не заполнены критерии: " + ", ".join(missing_fields),
        )

    db.commit()

    return render_project_detail(
        request,
        expert,
        project,
        projects,
        db,
        success="Оценки успешно сохранены.",
    )