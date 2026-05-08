from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

Chamber = Literal["us_house", "state_senate", "state_house"]


@dataclass
class PlanSpec:
    name: str
    state_fips: str
    state_abbr: str
    chamber: Chamber
    seat_count: int

    plan_path: Path
    precinct_path: Path
    county_path: Path

    plan_district_col: str = "DISTRICT"
    precinct_dem_col: str = "G20PREDBID"
    precinct_rep_col: str = "G20PRERTRU"
    precinct_pop_col: str = "TOTPOP"

    target_crs: str = "EPSG:5070"

    notes: str = ""

    @property
    def population_deviation_threshold(self) -> float:
        # Congressional: courts strike >1% without strong justification.
        # State legislative: <10% presumptively OK.
        return 0.01 if self.chamber == "us_house" else 0.10

    def report_path(self, reports_dir: Path = Path("reports")) -> Path:
        return reports_dir / f"{self.name}.md"
