from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db import Base, engine
from app.models import Criterion, Expert, Project, Score


app = FastAPI(title="Jury App")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


from app.routers.auth import router as auth_router
from app.routers.expert import router as expert_router
from app.routers.admin import router as admin_router

app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(expert_router)



@app.get("/")
def root():
    return {"message": "Jury App is running"}