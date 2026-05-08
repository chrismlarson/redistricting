from pathlib import Path
import os

REPO_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = Path(__file__).resolve().parent

STORAGE_DIR = Path(os.environ.get("REDISTRICTING_STORAGE", REPO_ROOT / "storage"))
DB_PATH = STORAGE_DIR / "prod.db"
IMAGES_DIR = STORAGE_DIR / "images"

WEB_DATA_DIR = Path(os.environ.get("REDISTRICTING_WEB_DATA", REPO_ROOT / "web-data"))

UPLOAD_MAX_BYTES = 10 * 1024 * 1024
URL_PREFIX = os.environ.get("REDISTRICTING_URL_PREFIX", "/redistricting")

STORAGE_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
