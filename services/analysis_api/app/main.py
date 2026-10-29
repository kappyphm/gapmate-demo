"""GapMate Analysis API — stateless CV/JD analysis pipeline."""

import logging

from fastapi import FastAPI

from app.api.routes import analyze, ats, courses, parse, taxonomy
from app.core.config import settings

# App loggers (per-request analysis + LLM usage lines, warnings) must reach
# the container log; without this only uvicorn's own access logs show.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(title=settings.app_name, version=settings.pipeline_version)


@app.get("/health", tags=["meta"])
async def health() -> dict:
    return {"status": "ok", "service": "analysis-api", "version": settings.pipeline_version}


app.include_router(analyze.router, prefix="/v1", tags=["analyze"])
app.include_router(parse.router, prefix="/v1", tags=["parse"])
app.include_router(ats.router, prefix="/v1", tags=["ats"])
app.include_router(courses.router, prefix="/v1", tags=["courses"])
app.include_router(taxonomy.router, prefix="/v1", tags=["taxonomy"])
