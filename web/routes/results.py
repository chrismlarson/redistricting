import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlmodel import Session, select

from web.db import get_session
from web.models import Evaluation
from web.templating import templates

router = APIRouter()


def _get_or_404(session: Session, slug: str) -> Evaluation:
    ev = session.exec(select(Evaluation).where(Evaluation.slug == slug)).first()
    if ev is None:
        raise HTTPException(status_code=404, detail=f"No evaluation found at slug '{slug}'")
    return ev


@router.get("/r/{slug}.json")
def result_json(slug: str, session: Session = Depends(get_session)):
    ev = _get_or_404(session, slug)
    return JSONResponse(content=json.loads(ev.report_json))


@router.get("/r/{slug}", response_class=HTMLResponse)
def result_page(slug: str, request: Request, session: Session = Depends(get_session)):
    ev = _get_or_404(session, slug)
    report = json.loads(ev.report_json)
    return templates.TemplateResponse(
        request,
        "results.html",
        {"evaluation": ev, "report": report},
    )
