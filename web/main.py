from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from web.config import IMAGES_DIR, URL_PREFIX, WEB_DIR
from web.db import init_db
from web.routes import evaluate_route, index, methodology, results

app = FastAPI(
    title="Redistricting fairness evaluation",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@app.on_event("startup")
def _startup() -> None:
    init_db()


app.mount(
    f"{URL_PREFIX}/static/css",
    StaticFiles(directory=str(WEB_DIR / "static" / "css")),
    name="static_css",
)
app.mount(
    f"{URL_PREFIX}/static/images",
    StaticFiles(directory=str(IMAGES_DIR)),
    name="static_images",
)

app.include_router(index.router, prefix=URL_PREFIX)
app.include_router(methodology.router, prefix=URL_PREFIX)
app.include_router(results.router, prefix=URL_PREFIX)
app.include_router(evaluate_route.router, prefix=URL_PREFIX)
