"""Standalone parse/extract endpoints (useful for testing the pipeline stages)."""

from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

from app.pipeline.extract import extract_text
from app.pipeline.parse_cv import parse_cv
from app.pipeline.parse_jd import parse_jd
from app.schemas.cv import CVDoc
from app.schemas.jd import JDDoc

router = APIRouter()


class TextIn(BaseModel):
    text: str


@router.post("/parse/cv", response_model=CVDoc)
async def parse_cv_route(payload: TextIn) -> CVDoc:
    return parse_cv(payload.text)


@router.post("/parse/jd", response_model=JDDoc)
async def parse_jd_route(payload: TextIn) -> JDDoc:
    return parse_jd(payload.text)


@router.post("/extract")
async def extract_route(file: UploadFile = File(...)) -> dict:
    text, layout = extract_text(await file.read(), file.filename or "")
    return {"text": text, "layout": {k: v for k, v in layout.items() if k != "blocks"}, "blocks": layout.get("blocks", [])[:50]}
