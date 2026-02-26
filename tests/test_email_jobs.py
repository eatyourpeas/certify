import csv
from pathlib import Path

from batch_generate import generate_batch


def test_generate_email_jobs(tmp_path: Path):
    # Create CSV with EventBrite-style headers
    csv_file = tmp_path / "eb.csv"
    rows = [
        {"Attendee first name": "Alice", "Attendee Surname": "Example", "Attendee email": "alice@example.com"},
        {"Attendee first name": "Bob", "Attendee Surname": "Example", "Attendee email": "bob@example.com"},
    ]
    with csv_file.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["Attendee first name", "Attendee Surname", "Attendee email"])
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

    out_dir = tmp_path / "out"

    result = generate_batch(
        input_path=csv_file,
        event_name="Test Event",
        event_year="2026",
        defaults=defaults,
        output_dir=out_dir,
        make_zip=False,
        first_name_field="Attendee first name",
        surname_field="Attendee Surname",
        email_field="Attendee email",
        prepare_emails=True,
    )

    # Two certificates created
    assert len(result["generated"]) == 2

    # Email jobs returned
    assert "email_jobs" in result
    jobs = result["email_jobs"]
    assert len(jobs) == 2
    recipients = {j["recipient"] for j in jobs}
    assert recipients == {"alice@example.com", "bob@example.com"}

    # Filepaths exist
    for j in jobs:
        p = Path(j["filepath"])
        assert p.exists()
