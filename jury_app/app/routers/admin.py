from collections import defaultdict

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


def get_current_user(request: Request, db: Session) -> Expert | None:
    expert_id = request.cookies.get("expert_id")
    if not expert_id:
        return None

    return db.query(Expert).filter(Expert.id == int(expert_id)).first()


def require_admin(request: Request, db: Session) -> Expert | RedirectResponse:
    user = get_current_user(request, db)

    if not user:
        return RedirectResponse(url="/login", status_code=303)

    if not user.is_admin:
        return RedirectResponse(url="/expert", status_code=303)

    return user


@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    user = require_admin(request, db)
    if not isinstance(user, Expert):
        return user

    projects = (
        db.query(Project)
        .filter(Project.is_active == True)
        .order_by(Project.sort_order.asc(), Project.id.asc())
        .all()
    )

    scores = db.query(Score).all()

    project_scores_map = defaultdict(list)
    project_experts_map = defaultdict(set)

    for score in scores:
        project_scores_map[score.project_id].append(score.value)
        project_experts_map[score.project_id].add(score.expert_id)

    results = []

    for project in projects:
        values = project_scores_map.get(project.id, [])
        experts_count = len(project_experts_map.get(project.id, set()))
        total_score = sum(values)
        average_score = round(total_score / len(values), 2) if values else 0

        results.append(
            {
                "project_id": project.id,
                "title": project.title,
                "author_full_name": project.author_full_name,
                "organization": project.organization,
                "experts_count": experts_count,
                "total_score": total_score,
                "average_score": average_score,
            }
        )

    results.sort(
        key=lambda item: (item["average_score"], item["total_score"]),
        reverse=True,
    )

    for index, item in enumerate(results, start=1):
        item["rank"] = index

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "user": user,
            "results": results,
        },
    )


@router.get("/admin/projects/{project_id}", response_class=HTMLResponse)
def admin_project_detail(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    user = require_admin(request, db)
    if not isinstance(user, Expert):
        return user

    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.is_active == True)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    criteria = (
        db.query(Criterion)
        .filter(Criterion.is_active == True)
        .order_by(Criterion.sort_order.asc(), Criterion.id.asc())
        .all()
    )

    experts = (
        db.query(Expert)
        .filter(Expert.is_admin == False, Expert.is_active == True)
        .order_by(Expert.full_name.asc())
        .all()
    )

    scores = (
        db.query(Score)
        .filter(Score.project_id == project.id)
        .all()
    )

    score_map = {}
    expert_totals = defaultdict(int)
    expert_filled_count = defaultdict(int)

    for score in scores:
        score_map[(score.expert_id, score.criterion_id)] = score.value
        expert_totals[score.expert_id] += score.value
        expert_filled_count[score.expert_id] += 1

    expert_rows = []
    criteria_count = len(criteria)

    for expert in experts:
        row_scores = []
        for criterion in criteria:
            row_scores.append(
                {
                    "criterion_id": criterion.id,
                    "value": score_map.get((expert.id, criterion.id)),
                }
            )

        is_complete = expert_filled_count[expert.id] == criteria_count and criteria_count > 0

        expert_rows.append(
            {
                "expert": expert,
                "scores": row_scores,
                "total_score": expert_totals[expert.id],
                "is_complete": is_complete,
            }
        )

    project_total = sum(expert_totals.values())
    completed_experts_count = sum(1 for row in expert_rows if row["is_complete"])
    average_total_per_expert = round(project_total / completed_experts_count, 2) if completed_experts_count else 0

    return templates.TemplateResponse(
        "admin/project_detail.html",
        {
            "request": request,
            "user": user,
            "project": project,
            "criteria": criteria,
            "expert_rows": expert_rows,
            "project_total": project_total,
            "completed_experts_count": completed_experts_count,
            "average_total_per_expert": average_total_per_expert,
        },
    )