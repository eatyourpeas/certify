import csv
from pathlib import Path

from batch_generate import generate_batch


def test_generate_batch_in_memory(tmp_path: Path):
    csv_file = tmp_path / "attendees.csv"
    rows = [{"name": "Alice Example"}, {"name": "Bob Example"}]
    with csv_file.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

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

    result = generate_batch(
        input_path=csv_file,
        event_name="Test Event",
        event_year="2026",
        defaults=defaults,
        output_dir=tmp_path / "out",
        make_zip=True,
        in_memory=True,
    )

    assert isinstance(result, dict)
    gen = result["generated"]
    assert isinstance(gen, list)
    assert len(gen) == 2
    for item in gen:
        assert "pdf_bytes" in item
        assert item["pdf_bytes"][:4] == b"%PDF"

    # zip returned as bytes
    assert isinstance(result.get("zip"), (bytes, bytearray))
    assert len(result["zip"]) > 0
