"""Parse Tennessee SB7004/SA7001 amendment PDF into a block-equivalency table.

The bill describes each of 9 congressional districts as a structured list:
- Whole counties (assigned entirely to the district)
- Split counties: list VTDs (precincts) assigned wholly, then VTD-with-block
  carve-outs ("VTD: ... :  Block 705001010, Block 705001011, ...")

Output CSV schema: district, county, vtd, block
- For whole-county rows: vtd and block are empty.
- For whole-VTD rows: block is empty.
- For split-VTD rows: one row per block.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

import pypdf

DISTRICT_RE = re.compile(r"District\s+(\d+)\s*:")
# Whole-county line, or split-county-header (ends with ":")
COUNTY_LINE_RE = re.compile(r"^([A-Z][A-Za-z\.\-' ]+?)\s+County(\s*:)?\s*$")
# VTD line: "VTD: <name>" possibly followed by ":" if it then lists blocks
VTD_LINE_RE = re.compile(r"^VTD\s*:\s*(.+?)(\s*:)?\s*$")
BLOCK_RE = re.compile(r"Block\s+(\d{6,12})")


def _readPdfText(pdf_path: Path) -> str:
    reader = pypdf.PdfReader(str(pdf_path))
    return "\n".join(p.extract_text() for p in reader.pages)


def _normalizeLines(text: str) -> list[str]:
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        # Drop boilerplate footers: "- 51 - 019155" etc.
        if re.match(r"^-\s*\d+\s*-(\s+\d+)?$", s):
            continue
        out.append(s)
    return out


def parseAssignments(pdf_path: Path):
    """Yield rows of (district:int, county:str, vtd:str, block:str|None).

    State machine:
    - On "District N:" → set current district, reset county/vtd
    - On "<Name> County" or "<Name> County:" → set county, reset vtd, emit
      a whole-county row if the line had no trailing ":" (and we don't see
      VTD/Block lines following it before the next county/district)
    - On "VTD: <name>" or "VTD: <name>:" → set vtd; emit whole-VTD row
      unless the line ends with ":" (then it'll be followed by Blocks)
    - On lines containing "Block <num>" → emit block rows under (district,
      county, vtd)

    To cope with the "whole county vs split county" ambiguity we look ahead:
    if the next non-empty line under a county is "VTD:" or "Block", the
    county is split — drop the whole-county emission. We implement this by
    deferring whole-county and whole-VTD emissions until we see what comes
    next.
    """
    text = _readPdfText(pdf_path)
    lines = _normalizeLines(text)

    district = None
    county = None
    vtd = None
    pending_county = None   # (county) - hasn't been confirmed whole yet
    pending_vtd = None      # (vtd)    - hasn't been confirmed whole yet
    awaiting_blocks_vtd = None  # VTD that ended with ":" — fall back to whole-VTD if no blocks arrive
    saw_block_for_awaiting = False

    def flushPendingCountyAsWhole(rows):
        nonlocal pending_county
        if pending_county is not None and district is not None:
            rows.append((district, pending_county, "", ""))
        pending_county = None

    def flushPendingVtdAsWhole(rows):
        nonlocal pending_vtd
        if pending_vtd is not None and district is not None and county is not None:
            rows.append((district, county, pending_vtd, ""))
        pending_vtd = None

    def flushAwaitingBlocksAsWhole(rows):
        """Bill drafting quirk: 'VTD: X:' with no following blocks. Treat as whole-VTD."""
        nonlocal awaiting_blocks_vtd, saw_block_for_awaiting
        if awaiting_blocks_vtd is not None and not saw_block_for_awaiting and district is not None and county is not None:
            rows.append((district, county, awaiting_blocks_vtd, ""))
        awaiting_blocks_vtd = None
        saw_block_for_awaiting = False

    rows: list[tuple] = []

    for raw in lines:
        m_dist = DISTRICT_RE.search(raw)
        if m_dist:
            flushAwaitingBlocksAsWhole(rows)
            flushPendingVtdAsWhole(rows)
            flushPendingCountyAsWhole(rows)
            district = int(m_dist.group(1))
            county = None
            vtd = None
            continue

        m_county = COUNTY_LINE_RE.match(raw)
        if m_county and "VTD" not in raw and "Block" not in raw:
            flushAwaitingBlocksAsWhole(rows)
            flushPendingVtdAsWhole(rows)
            flushPendingCountyAsWhole(rows)
            cname = m_county.group(1).strip()
            has_colon = m_county.group(2) is not None
            county = cname
            vtd = None
            if has_colon:
                # Split county — wait for VTDs/Blocks; don't emit whole-county row
                pending_county = None
            else:
                pending_county = cname
            continue

        m_vtd = VTD_LINE_RE.match(raw)
        if m_vtd:
            flushAwaitingBlocksAsWhole(rows)
            # If we had a pending whole-county, this proves it's split — drop it
            pending_county = None
            flushPendingVtdAsWhole(rows)
            vname = m_vtd.group(1).strip().rstrip(":").strip()
            has_colon = m_vtd.group(2) is not None or raw.rstrip().endswith(":")
            vtd = vname
            if has_colon:
                pending_vtd = None  # blocks will follow
                awaiting_blocks_vtd = vname
                saw_block_for_awaiting = False
            else:
                pending_vtd = vname
                awaiting_blocks_vtd = None
            continue

        # Block enumeration line(s)
        blocks = BLOCK_RE.findall(raw)
        if blocks:
            pending_county = None
            pending_vtd = None
            saw_block_for_awaiting = True
            if district is None or county is None or vtd is None:
                # Defensive: should not happen
                continue
            for blk in blocks:
                rows.append((district, county, vtd, blk))
            continue

    # End of doc — flush trailing pending whole entries
    flushAwaitingBlocksAsWhole(rows)
    flushPendingVtdAsWhole(rows)
    flushPendingCountyAsWhole(rows)

    return rows


def writeCsv(rows, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["district", "county", "vtd", "block"])
        w.writerows(rows)


def summarize(rows):
    by_district = {}
    for d, c, v, b in rows:
        rec = by_district.setdefault(d, {"counties": set(), "vtds": set(), "blocks": 0,
                                          "whole_counties": set()})
        rec["counties"].add(c)
        if v:
            rec["vtds"].add((c, v))
        if b:
            rec["blocks"] += 1
        if not v and not b:
            rec["whole_counties"].add(c)
    return by_district


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--out", type=Path, default=Path("data/tn/sa7001_assignments.csv"))
    args = ap.parse_args(argv)

    rows = parseAssignments(args.pdf)
    writeCsv(rows, args.out)
    summary = summarize(rows)
    print(f"Wrote {len(rows)} rows -> {args.out}")
    for d in sorted(summary):
        s = summary[d]
        print(f"District {d}: {len(s['counties'])} counties touched "
              f"({len(s['whole_counties'])} whole), "
              f"{len(s['vtds'])} VTDs partial, "
              f"{s['blocks']} blocks listed")


if __name__ == "__main__":
    sys.exit(main())
