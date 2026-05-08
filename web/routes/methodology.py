from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from web.templating import templates

router = APIRouter()


@router.get("/methodology", response_class=HTMLResponse)
def methodology(request: Request):
    return templates.TemplateResponse(request, "methodology.html", {})
