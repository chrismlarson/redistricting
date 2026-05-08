import hashlib
import json
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from web.config import UPLOAD_MAX_BYTES, URL_PREFIX
from web.db import get_session
from web.models import Evaluation
from web.services.evaluator import evaluate_plan
from web.services.states import get_state, supported_states
from web.templating import templates

router = APIRouter()

CHAMBERS = [
    ("us_house", "U.S. House"),
    ("state_senate", "State Senate"),
    ("state_house", "State House"),
]


def _make_slug(name: str, csv_bytes: bytes) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "evaluation"
    digest = hashlib.sha256(csv_bytes).hexdigest()[:10]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{base}-{stamp}-{digest}"


@router.get("/evaluate", response_class=HTMLResponse)
def evaluate_form(request: Request):
    return templates.TemplateResponse(
        request,
        "evaluate.html",
        {
            "states": supported_states(),
            "chambers": CHAMBERS,
            "error": None,
        },
    )


@router.post("/evaluate")
async def evaluate_submit(
    request: Request,
    state_abbr: str = Form(...),
    chamber: str = Form(...),
    seat_count: int = Form(...),
    name: str = Form(...),
    notes: str = Form(""),
    plan_csv: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    if chamber not in {c[0] for c in CHAMBERS}:
        raise HTTPException(status_code=400, detail="Unknown chamber")
    if seat_count <= 0 or seat_count > 200:
        raise HTTPException(status_code=400, detail="seat_count out of range")
    name = name.strip()[:120]
    notes = notes.strip()[:1000]
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")

    try:
        state = get_state(state_abbr)
    except KeyError:
        raise HTTPException(status_code=400, detail=f"State '{state_abbr}' not supported")

    csv_bytes = await plan_csv.read()
    if len(csv_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty CSV upload")
    if len(csv_bytes) > UPLOAD_MAX_BYTES:
        raise HTTPException(status_code=413, detail="CSV upload too large")

    slug = _make_slug(name, csv_bytes)
    if session.exec(select(Evaluation).where(Evaluation.slug == slug)).first():
        return RedirectResponse(url=f"{URL_PREFIX}/r/{slug}", status_code=303)

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        tmp.write(csv_bytes)
        tmp_path = Path(tmp.name)

    try:
        try:
            report = evaluate_plan(
                state=state,
                chamber=chamber,
                seat_count=seat_count,
                name=name,
                notes=notes,
                slug=slug,
                vtd_csv_path=tmp_path,
            )
        except (ValueError, KeyError) as exc:
            return templates.TemplateResponse(
                request,
                "evaluate.html",
                {
                    "states": supported_states(),
                    "chambers": CHAMBERS,
                    "error": str(exc),
                },
                status_code=400,
            )
    finally:
        try:
            tmp_path.unlink()
        except OSError:
            pass

    ev = Evaluation(
        slug=slug,
        name=name,
        state_abbr=state.abbr,
        chamber=chamber,
        seat_count=seat_count,
        notes=notes,
        report_json=json.dumps(report),
        is_seed=False,
    )
    session.add(ev)
    session.commit()

    return RedirectResponse(url=f"{URL_PREFIX}/r/{slug}", status_code=303)
