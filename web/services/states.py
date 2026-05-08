"""Registry of states the running service can evaluate.

V1 ships TN only. Adding a state means dropping its precinct/county/VTD
shapefiles into web-data/{abbr}/ on the server and adding an entry here.
The metric pipeline itself is state-agnostic.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from web.config import REPO_ROOT, WEB_DATA_DIR

# Fallback chain: production uses web-data/, local dev tolerates the
# legacy data/ directory the CLI uses.
_DATA_DIRS = [WEB_DATA_DIR, REPO_ROOT / "data"]


def _find(rel_path: str) -> Path:
    for base in _DATA_DIRS:
        p = base / rel_path
        if p.exists():
            return p
    return _DATA_DIRS[0] / rel_path


@dataclass(frozen=True)
class StateData:
    abbr: str
    fips: str
    name: str
    precinct_path: Path
    county_path: Path
    vtd_path: Path
    precinct_dem_col: str = "G20PREDBID"
    precinct_rep_col: str = "G20PRERTRU"
    precinct_pop_col: str = "TOTPOP"


_STATES: Dict[str, StateData] = {
    "TN": StateData(
        abbr="TN",
        fips="47",
        name="Tennessee",
        precinct_path=_find("tn/tn_2020.shp"),
        county_path=_find("tn/tl_2024_us_county.shp"),
        vtd_path=_find("tn/tl_2020_47_vtd20.shp"),
        precinct_pop_col="",  # VEST 2020 TN has empty TOTPOP
    ),
}


def supported_states() -> list[StateData]:
    return [s for s in _STATES.values() if s.precinct_path.exists()]


def get_state(abbr: str) -> StateData:
    abbr = abbr.upper()
    if abbr not in _STATES:
        raise KeyError(f"State '{abbr}' is not registered")
    return _STATES[abbr]
