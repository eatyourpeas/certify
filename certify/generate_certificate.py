"""Interactive certificate generator (packaged).

Packaged copy of the top-level `generate_certificate.py` to live under the
`certify` package so consumers can `import certify`.
"""

from main import create_certificate
import sys
import os
from pathlib import Path
from datetime import datetime


def get_user_input():
    print("\n" + "=" * 60)
    print("CERTIFICATE GENERATOR - Interactive Mode")
    print("=" * 60 + "\n")

    event_name = input("Enter event name (for folder organization): ").strip()
    if not event_name:
        print("Error: Event name cannot be empty")
        sys.exit(1)

    event_year = input("Enter event year [default: current year]: ").strip()
    if not event_year:
        event_year = str(datetime.now().year)
    else:
        if not event_year.isdigit() or len(event_year) != 4:
            print("Error: Year must be 4 digits (e.g., 2024)")
            sys.exit(1)

    organiser = input(
        "Enter organiser name [default: South Thames Paediatric Endocrine Group]: "
    ).strip()
    if not organiser:
        organiser = "South Thames Paediatric Endocrine Group"

    organiser_logo = input(
        "Enter path to organiser logo PNG [default: logo.png]: "
    ).strip()
    if not organiser_logo:
        organiser_logo = "logo.png"

    attendee_name = input("Enter attendee's name: ").strip()
    if not attendee_name:
        print("Error: Attendee name cannot be empty")
        sys.exit(1)

    course_title = input("Enter course/event title: ").strip()
    if not course_title:
        print("Error: Course title cannot be empty")
        sys.exit(1)

    location = input("Enter location: ").strip()
    if not location:
        print("Error: Location cannot be empty")
        sys.exit(1)

    date = input("Enter date (e.g., '27th May 2024'): ").strip()
    if not date:
        print("Error: Date cannot be empty")
        sys.exit(1)

    host_hospital = input(
        "Enter host hospital [default: Royal Alexandra Children's Hospital]: "
    ).strip()
    if not host_hospital:
        host_hospital = "Royal Alexandra Children's Hospital"

    host_trust = input(
        "Enter host trust [default: Brighton & Sussex University Hospitals]: "
    ).strip()
    if not host_trust:
        host_trust = "Brighton & Sussex University Hospitals"

    host_name = input(
        "Enter host name (e.g., 'Dr Charlotte Jackson') [optional]: "
    ).strip()

    output_filename = input(
        "Enter output filename [default: {attendee_name}_certificate.pdf]: "
    ).strip()
    if not output_filename:
        output_filename = f"{attendee_name.replace(' ', '_')}_certificate.pdf"
    elif not output_filename.endswith(".pdf"):
        output_filename += ".pdf"

    return {
        "event_name": event_name,
        "event_year": event_year,
        "organiser": organiser,
        "organiser_logo": organiser_logo,
        "attendee_name": attendee_name,
        "course_title": course_title,
        "location": location,
        "date": date,
        "host_hospital": host_hospital,
        "host_trust": host_trust,
        "host_name": host_name,
        "output_filename": output_filename,
    }


def main():
    try:
        details = get_user_input()
        folder_name = (
            f"{details['event_year']}_{details['event_name'].replace(' ', '_')}"
        )
        folder_path = Path(folder_name)
        folder_path.mkdir(exist_ok=True)
        output_path = folder_path / details["output_filename"]
        print("\nGenerating certificate...", end=" ", flush=True)
        output_file = create_certificate(
            attendee_name=details["attendee_name"],
            course_title=details["course_title"],
            location=details["location"],
            date=details["date"],
            output_path=str(output_path),
            organiser=details["organiser"],
            organiser_logo=details["organiser_logo"],
            host_hospital=details["host_hospital"],
            host_trust=details["host_trust"],
            host_name=details["host_name"],
        )
        print("✓")
        print("\n" + "=" * 60)
        print("CERTIFICATE GENERATED SUCCESSFULLY!")
        print("=" * 60)
        print(f"  Organiser: {details['organiser']}")
        print(f"  Attendee:  {details['attendee_name']}")
        print(f"  Course:    {details['course_title']}")
        print(f"  Location:  {details['location']}")
        print(f"  Date:      {details['date']}")
        if details["host_name"]:
            print(f"  Host:      {details['host_name']}")
        print(f"  Hospital:  {details['host_hospital']}")
        print(f"  Trust:     {details['host_trust']}")
        print(f"  Saved to:  {output_file}")
        print("=" * 60 + "\n")

    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
