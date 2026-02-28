import os
from pathlib import Path

from certify import create_certificate


def test_create_certificate_generates_pdf(tmp_path: Path):
    out_file = tmp_path / "test_certificate.pdf"
    # Use a non-existent logo so ImageReader path is skipped
    result = create_certificate(
        attendee_name="Unit Test User",
        course_title="Unit Testing Workshop",
        location="Testville",
        date="1st Jan 2026",
        output_path=str(out_file),
        organiser="Test Org",
        organiser_logo="non_existent_logo.png",
        host_hospital="Test Hospital",
        host_trust="Test Trust",
        host_name="Dr Tester",
    )

    assert os.path.exists(result)
    # Basic PDF sanity: file starts with %PDF
    with open(result, "rb") as fh:
        header = fh.read(4)
    assert header == b"%PDF"
