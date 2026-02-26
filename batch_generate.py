#!/usr/bin/env python3
"""Batch certificate generator.

Reads a list of attendee names (CSV or newline-separated TXT) and generates
certificates in a folder named <year>_<eventname>. Optionally creates a ZIP.

Usage examples:
  python batch_generate.py --input attendees.csv --event-name "STPEG Autumn Meeting" \
    --course-title "STPEG Autumn Meeting 2025" --location "Brighton" --date "27th May 2025" --zip

CSV expected header: one column containing attendee name. Common headers:
  name, full_name, attendee_name
Other columns supported as per-row overrides: output_filename, host_name,
organiser, organiser_logo, course_title, location, date, host_hospital, host_trust
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
import zipfile
from typing import Dict, List

from main import create_certificate


def normalize_key(k: str) -> str:
    return k.strip().lower()


def read_input_file(path: Path) -> List[Dict[str, str]]:
    """Return list of row dicts. For TXT, use a single column 'attendee_name'."""
    rows: List[Dict[str, str]] = []
    if path.suffix.lower() in (".txt", ".list"):
        # Each non-empty line is a name
        text = path.read_text(encoding="utf-8")
        for line in (l.strip() for l in text.splitlines()):
            if not line:
                continue
            rows.append({"attendee_name": line})
        return rows

    # Default: CSV
    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            normalized = {
                normalize_key(k): v.strip() for k, v in r.items() if k is not None
            }
            rows.append(normalized)
    return rows


def pick_name_from_row(row: Dict[str, str]) -> str:
    for key in ("attendee_name", "name", "full_name"):
        v = row.get(key)
        if v:
            return v
    raise ValueError(
        "No attendee name found in row; expected 'name' or 'attendee_name'"
    )


def build_kwargs_from_row(
    row: Dict[str, str], defaults: Dict[str, str]
) -> Dict[str, str]:
    kw = defaults.copy()
    # Apply per-row overrides for known keys
    for k in (
        "organiser",
        "organiser_logo",
        "course_title",
        "location",
        "date",
        "host_hospital",
        "host_trust",
        "host_name",
        "output_filename",
    ):
        if row.get(k):
            kw[k] = row[k]

    # Attendee name
    kw["attendee_name"] = pick_name_from_row(row)

    # Ensure output filename exists
    if not kw.get("output_filename"):
        safe_name = kw["attendee_name"].replace(" ", "_")
        kw["output_filename"] = f"{safe_name}_certificate.pdf"

    return kw


def generate_batch(
    input_path: Path,
    event_name: str,
    event_year: str,
    defaults: Dict[str, str],
    output_dir: Path | None = None,
    make_zip: bool = False,
):
    rows = read_input_file(input_path)
    if not rows:
        raise SystemExit("No attendees found in input file")

    folder_name = f"{event_year}_{event_name.replace(' ', '_')}"
    out_dir = Path(folder_name) if output_dir is None else output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    generated_files: List[Path] = []

    for i, row in enumerate(rows, start=1):
        try:
            kw = build_kwargs_from_row(row, defaults)
            output_path = out_dir / kw["output_filename"]
            print(
                f"[{i}/{len(rows)}] Generating: {kw['attendee_name']} -> {output_path}"
            )
            created = create_certificate(
                attendee_name=kw["attendee_name"],
                course_title=kw["course_title"],
                location=kw["location"],
                date=kw["date"],
                output_path=str(output_path),
                organiser=kw.get("organiser", defaults.get("organiser")),
                organiser_logo=kw.get("organiser_logo", defaults.get("organiser_logo")),
                host_hospital=kw.get("host_hospital", defaults.get("host_hospital")),
                host_trust=kw.get("host_trust", defaults.get("host_trust")),
                host_name=kw.get("host_name", defaults.get("host_name", "")),
            )
            generated_files.append(Path(created))
        except Exception as e:
            print(f"Error generating certificate for row {i}: {e}")

    if make_zip and generated_files:
        zip_file = out_dir.with_suffix(".zip")
        print(f"Creating ZIP archive: {zip_file}")
        with zipfile.ZipFile(zip_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in generated_files:
                zf.write(f, arcname=f.name)
        print(f"ZIP created: {zip_file}")

    print("Done.")
    print(f"Generated {len(generated_files)} certificates in: {out_dir}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Batch certificate generator")
    p.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to CSV or TXT file with attendee names",
    )
    p.add_argument(
        "--event-name", required=True, help="Event name (used for output folder)"
    )
    p.add_argument(
        "--event-year",
        default=str(datetime.now().year),
        help="Event year (default: current year)",
    )
    p.add_argument(
        "--course-title",
        required=True,
        help="Course/event title to print on certificates",
    )
    p.add_argument("--location", required=True, help="Location string for certificates")
    p.add_argument("--date", required=True, help="Date string for certificates")
    p.add_argument("--organiser", default="South Thames Paediatric Endocrine Group")
    p.add_argument("--organiser-logo", default="logo.png")
    p.add_argument("--host-hospital", default="Royal Alexandra Children's Hospital")
    p.add_argument("--host-trust", default="Brighton & Sussex University Hospitals")
    p.add_argument("--host-name", default="", help="Optional host name for footer")
    p.add_argument(
        "--output-dir",
        default=None,
        help="Optional output directory (overrides generated folder name)",
    )
    p.add_argument(
        "--zip", action="store_true", help="Create a zip of generated certificates"
    )
    return p.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    defaults = {
        "organiser": args.organiser,
        "organiser_logo": args.organiser_logo,
        "course_title": args.course_title,
        "location": args.location,
        "date": args.date,
        "host_hospital": args.host_hospital,
        "host_trust": args.host_trust,
        "host_name": args.host_name,
    }

    output_dir = Path(args.output_dir) if args.output_dir else None

    generate_batch(
        input_path=input_path,
        event_name=args.event_name,
        event_year=args.event_year,
        defaults=defaults,
        output_dir=output_dir,
        make_zip=args.zip,
    )


if __name__ == "__main__":
    main()
