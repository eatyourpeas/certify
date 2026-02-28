"""Batch certificate generator (packaged).

This is the same code as the top-level `batch_generate.py` but packaged under
the `certify` package to allow `import certify` style imports.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
import zipfile
import io
import tempfile
import os
from typing import Dict, List

from .generate_certificate import create_certificate


def normalize_key(k: str) -> str:
    return k.strip().lower()


def read_input_file(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    if path.suffix.lower() in (".txt", ".list"):
        text = path.read_text(encoding="utf-8")
        for line in (l.strip() for l in text.splitlines()):
            if not line:
                continue
            rows.append({"attendee_name": line})
        return rows

    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            normalized = {
                normalize_key(k): (v.strip() if v is not None else "")
                for k, v in r.items()
                if k is not None
            }
            rows.append(normalized)
    return rows


def pick_name_from_row(
    row: Dict[str, str],
    first_name_field: str | None = None,
    surname_field: str | None = None,
    title_field: str | None = None,
) -> str:
    for key in ("attendee_name", "name", "full_name"):
        v = row.get(key)
        if v:
            return v

    if first_name_field and surname_field:
        fn = row.get(normalize_key(first_name_field))
        sn = row.get(normalize_key(surname_field))
        if fn and sn:
            return f"{fn} {sn}".strip()

    fn = row.get(normalize_key("Attendee first name"))
    sn = row.get(normalize_key("Attendee Surname"))
    if fn and sn:
        return f"{fn} {sn}".strip()

    raise ValueError(
        "No attendee name found in row; expected name or attendee first/surname columns"
    )


def build_kwargs_from_row(
    row: Dict[str, str],
    defaults: Dict[str, str],
    first_name_field: str | None = None,
    surname_field: str | None = None,
    title_field: str | None = None,
) -> Dict[str, str]:
    kw = defaults.copy()
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

    kw["attendee_name"] = pick_name_from_row(
        row,
        first_name_field=first_name_field,
        surname_field=surname_field,
        title_field=title_field,
    )

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
    in_memory: bool = False,
    first_name_field: str | None = "Attendee first name",
    surname_field: str | None = "Attendee Surname",
    title_field: str | None = None,
    email_field: str | None = "Attendee email",
    prepare_emails: bool = False,
):
    rows = read_input_file(input_path)
    if not rows:
        raise SystemExit("No attendees found in input file")

    folder_name = f"{event_year}_{event_name.replace(' ', '_')}"
    out_dir = Path(folder_name) if output_dir is None else output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    generated_files: List[Path] = []
    generated: List[Dict[str, object]] = [] if in_memory else []
    email_map: Dict[str, Dict[str, object]] = {}
    skipped_rows: List[int] = []
    errors: List[str] = []
    duplicates: Dict[str, List[int]] = {}
    seen_names: Dict[str, object] = {}
    zip_file = None

    for i, row in enumerate(rows, start=1):
        try:
            try:
                attendee_name = pick_name_from_row(
                    row,
                    first_name_field=first_name_field,
                    surname_field=surname_field,
                    title_field=title_field,
                )
            except ValueError:
                email_val = None
                if email_field:
                    email_val = row.get(normalize_key(email_field))
                if email_val:
                    attendee_name = email_val
                    errors.append(
                        f"Row {i}: name missing; using email {email_val} as name"
                    )
                else:
                    skipped_rows.append(i)
                    errors.append(f"Row {i}: missing name and email; skipped")
                    continue

            kw = build_kwargs_from_row(
                row,
                defaults,
                first_name_field=first_name_field,
                surname_field=surname_field,
                title_field=title_field,
            )
            kw["attendee_name"] = attendee_name
            output_path = out_dir / kw["output_filename"]
            print(
                f"[{i}/{len(rows)}] Generating: {kw['attendee_name']} -> {output_path}"
            )
            norm_name = kw["attendee_name"].strip().lower()
            if norm_name in seen_names:
                duplicates.setdefault(kw["attendee_name"], []).append(i)
                existing_path = seen_names[norm_name]
                if email_field:
                    em = row.get(normalize_key(email_field))
                    if em:
                        if in_memory:
                            for g in generated:
                                if (
                                    isinstance(g, dict)
                                    and g.get("filename") == existing_path
                                ):
                                    email_map.setdefault(
                                        em,
                                        {
                                            "name": kw["attendee_name"],
                                            "pdf_bytes": g.get("pdf_bytes"),
                                            "filename": g.get("filename"),
                                        },
                                    )
                                    break
                        else:
                            email_map.setdefault(
                                em, {"name": kw["attendee_name"], "path": existing_path}
                            )
                continue

            if in_memory:
                tf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                tf.close()
                tmp_out = Path(tf.name)
                created = create_certificate(
                    attendee_name=kw["attendee_name"],
                    course_title=kw["course_title"],
                    location=kw["location"],
                    date=kw["date"],
                    output_path=str(tmp_out),
                    organiser=kw.get("organiser", defaults.get("organiser")),
                    organiser_logo=kw.get(
                        "organiser_logo", defaults.get("organiser_logo")
                    ),
                    host_hospital=kw.get(
                        "host_hospital", defaults.get("host_hospital")
                    ),
                    host_trust=kw.get("host_trust", defaults.get("host_trust")),
                    host_name=kw.get("host_name", defaults.get("host_name", "")),
                )
                with open(created, "rb") as fh:
                    pdf_bytes = fh.read()
                try:
                    os.unlink(created)
                except Exception:
                    pass
                filename = kw.get("output_filename", Path(created).name)
                generated.append(
                    {
                        "name": kw["attendee_name"],
                        "filename": filename,
                        "pdf_bytes": pdf_bytes,
                    }
                )
                seen_names[norm_name] = filename
                if email_field:
                    em = row.get(normalize_key(email_field))
                    if em:
                        email_map.setdefault(
                            em,
                            {
                                "name": kw["attendee_name"],
                                "pdf_bytes": pdf_bytes,
                                "filename": filename,
                            },
                        )
            else:
                created = create_certificate(
                    attendee_name=kw["attendee_name"],
                    course_title=kw["course_title"],
                    location=kw["location"],
                    date=kw["date"],
                    output_path=str(output_path),
                    organiser=kw.get("organiser", defaults.get("organiser")),
                    organiser_logo=kw.get(
                        "organiser_logo", defaults.get("organiser_logo")
                    ),
                    host_hospital=kw.get(
                        "host_hospital", defaults.get("host_hospital")
                    ),
                    host_trust=kw.get("host_trust", defaults.get("host_trust")),
                    host_name=kw.get("host_name", defaults.get("host_name", "")),
                )
                generated_files.append(Path(created))
                seen_names[norm_name] = Path(created)
                if email_field:
                    em = row.get(normalize_key(email_field))
                    if em:
                        email_map.setdefault(
                            em, {"name": kw["attendee_name"], "path": Path(created)}
                        )
        except Exception as e:
            errors.append(f"Row {i}: Error generating certificate: {e}")

    if make_zip:
        if in_memory and generated:
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for g in generated:
                    if isinstance(g, dict):
                        zf.writestr(g["filename"], g["pdf_bytes"])
            zip_file = buf.getvalue()
            print("ZIP created in-memory (bytes)")
        elif generated_files:
            zip_file = out_dir.with_suffix(".zip")
            print(f"Creating ZIP archive: {zip_file}")
            with zipfile.ZipFile(zip_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for f in generated_files:
                    zf.write(f, arcname=f.name)
            print(f"ZIP created: {zip_file}")
    print("Done.")
    gen_count = len(generated) if in_memory else len(generated_files)
    print(f"Generated {gen_count} certificates in: {out_dir}")

    if duplicates:
        print("\nDuplicates detected (generated one certificate each):")
        for name, occ in duplicates.items():
            print(f" - {name}: {len(occ)+1} occurrences (rows: {occ})")

    if skipped_rows:
        print("\nSkipped rows (missing name and email):")
        print(" ", skipped_rows)

    if errors:
        print("\nErrors / warnings:")
        for e in errors:
            print(" -", e)

    email_jobs: List[Dict[str, object]] = []
    if email_map:
        subject = defaults.get("course_title", "Certificate")
        for em, info in email_map.items():
            name = info.get("name") if isinstance(info, dict) else None
            path = info.get("path") if isinstance(info, dict) else None
            pdf_bytes = info.get("pdf_bytes") if isinstance(info, dict) else None
            body = f"Dear {name or em},\n\nPlease find attached your certificate for {defaults.get('course_title', '')}.\n\nBest,\n{defaults.get('organiser', '')}"
            job: Dict[str, object] = {
                "recipient": em,
                "name": name,
                "subject": subject,
                "body": body,
                "meta": {"event": event_name},
            }
            if pdf_bytes is not None:
                job["pdf_bytes"] = pdf_bytes
                job["filename"] = info.get("filename")
            else:
                job["filepath"] = str(path) if path is not None else None
            email_jobs.append(job)

    if email_jobs and prepare_emails:
        print("\nPrepared email jobs (not sent):")
        for job in email_jobs:
            target = job.get("filepath") or job.get("filename") or "<in-memory>"
            print(f" - {job['recipient']} -> {target}")

    return {
        "generated": generated if in_memory else generated_files,
        "zip": (
            zip_file
            if make_zip and (generated if in_memory else generated_files)
            else None
        ),
        "email_jobs": email_jobs,
        "duplicates": duplicates,
        "skipped_rows": skipped_rows,
        "errors": errors,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Batch certificate generator")
    p.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to CSV or TXT file with attendee names",
    )
