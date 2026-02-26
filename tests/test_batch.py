import csv
from pathlib import Path
import zipfile

from batch_generate import generate_batch


def test_generate_batch_creates_pdfs_and_zip(tmp_path: Path):
    # Prepare CSV input
    csv_file = tmp_path / "attendees.csv"
    rows = [{"name": "Alice Example"}, {"name": "Bob Example"}]
    with csv_file.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    # Call generate_batch
    event_name = "Test Event"
    event_year = "2026"
    defaults = {
        "organiser": "Test Org",
        "organiser_logo": "nonexistent_logo.png",
        "course_title": "Unit Testing Workshop",
        "location": "Testville",
        "date": "1st Jan 2026",
        "host_hospital": "Test Hospital",
        "host_trust": "Test Trust",
        "host_name": "",
    }

    out_dir = tmp_path / f"{event_year}_{event_name.replace(' ', '_')}"

    generate_batch(
        input_path=csv_file,
        event_name=event_name,
        event_year=event_year,
        defaults=defaults,
        output_dir=out_dir,
        make_zip=True,
    )

    # Expect two PDFs and a ZIP
    pdfs = list(out_dir.glob("*_certificate.pdf"))
    assert len(pdfs) == 2

    zip_file = tmp_path / f"{out_dir.name}.zip"
    assert zip_file.exists()
    with zipfile.ZipFile(zip_file, "r") as zf:
        assert len(zf.namelist()) == 2
