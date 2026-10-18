"""Course catalog + recommendation endpoints (P3)."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.data_loader import load_courses
from app.pipeline.recommend import recommend_courses
from app.schemas.report import CourseRec, GapItem

router = APIRouter()


class RecommendCoursesRequest(BaseModel):
    gaps: list[GapItem] = Field(default_factory=list)
    language: str = "en"
    limit: int = Field(default=8, ge=1, le=20)


class RecommendCoursesResponse(BaseModel):
    courses: list[CourseRec]


@router.get("/courses")
async def list_courses() -> dict:
    return {"courses": load_courses()}


@router.post("/recommend-courses", response_model=RecommendCoursesResponse)
async def recommend(payload: RecommendCoursesRequest) -> RecommendCoursesResponse:
    courses = recommend_courses(payload.gaps, language=payload.language, limit=payload.limit)
    return RecommendCoursesResponse(courses=courses)
