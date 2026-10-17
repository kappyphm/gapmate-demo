"""GapMate Analysis API — stateless CV/JD analysis pipeline."""

from fastapi import FastAPI

from app.api.routes import analyze, ats, courses, taxonomy
from app.core.config import settings

app = FastAPI(title=settings.app_name, version=settings.pipeline_version)


@app.get("/health", tags=["meta"])
async def health() -> dict:
    return {"status": "ok", "service": "analysis-api", "version": settings.pipeline_version}


app.include_router(analyze.router, prefix="/v1", tags=["analyze"])
app.include_router(ats.router, prefix="/v1", tags=["ats"])
app.include_router(courses.router, prefix="/v1", tags=["courses"])
app.include_router(taxonomy.router, prefix="/v1", tags=["taxonomy"])
