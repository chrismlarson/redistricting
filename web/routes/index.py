from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from web.db import get_session
from web.models import Evaluation
from web.templating import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index(request: Request, session: Session = Depends(get_session)):
    case_studies = session.exec(
        select(Evaluation).where(Evaluation.is_seed == True).order_by(Evaluation.created_at.desc())
    ).all()
    recent = session.exec(
        select(Evaluation).where(Evaluation.is_seed == False).order_by(Evaluation.created_at.desc()).limit(10)
    ).all()
    return templates.TemplateResponse(
        request,
        "index.html",
        {"case_studies": case_studies, "recent": recent},
    )
