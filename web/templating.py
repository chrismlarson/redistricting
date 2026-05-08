from pathlib import Path

from fastapi.templating import Jinja2Templates

from web.config import URL_PREFIX, WEB_DIR

templates = Jinja2Templates(directory=str(Path(WEB_DIR) / "templates"))
templates.env.globals["URL_PREFIX"] = URL_PREFIX


def fmt_pct(value, places: int = 2, signed: bool = False) -> str:
    if value is None:
        return "n/a"
    sign = "+" if signed and value > 0 else ""
    return f"{sign}{value * 100:.{places}f}%"


def fmt_decimal(value, places: int = 3) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{places}f}"


def fmt_int(value) -> str:
    if value is None:
        return "n/a"
    return f"{int(value):,}"


templates.env.filters["fmt_pct"] = fmt_pct
templates.env.filters["fmt_decimal"] = fmt_decimal
templates.env.filters["fmt_int"] = fmt_int
