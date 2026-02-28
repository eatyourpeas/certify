"""Interactive certificate generator (packaged).

Packaged copy of the top-level `generate_certificate.py` to live under the
`certify` package so consumers can `import certify`.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader


def create_certificate(
    attendee_name: str,
    course_title: str,
    location: str,
    date: str,
    output_path: str = "certificate.pdf",
    organiser: str = "South Thames Paediatric Endocrine Group",
    organiser_logo: str = "logo.png",
    host_hospital: str = "Royal Alexandra Children's Hospital",
    host_trust: str = "Brighton & Sussex University Hospitals",
    host_name: str = "",
) -> str:
    """
    Generate a personalized certificate as a PDF.

    Args:
        attendee_name: Name of the course attendee
        course_title: Title of the course/event
        location: Location where the course took place
        date: Date of the course (e.g., "27th May 2024")
        output_path: Path where the PDF will be saved (default: "certificate.pdf")
        organiser: Name of the organizing body (default: "South Thames Paediatric Endocrine Group")
        organiser_logo: Path to organiser logo PNG file (default: "logo.png")
        host_hospital: Name of the hosting hospital (default: "Royal Alexandra Children's Hospital")
        host_trust: Name of the hosting trust (default: "Brighton & Sussex University Hospitals")
        host_name: Name of the host/organizer (e.g., "Dr Charlotte Jackson")

    Returns:
        Path to the generated PDF file
    """

    # Create PDF in landscape orientation
    c = canvas.Canvas(output_path, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Set up fonts and colors
    title_font = "Helvetica-Bold"
    body_font = "Helvetica"
    org_color = colors.HexColor("#003366")  # Dark blue

    # Add logo in bottom right corner if it exists
    if os.path.exists(organiser_logo):
        try:
            img = ImageReader(organiser_logo)
            logo_width = 3.0 * inch
            logo_height = 3.0 * inch
            c.drawImage(
                img,
                width - logo_width - 0.3 * inch,  # Right side with margin
                0.3 * inch,  # Bottom side with margin
                width=logo_width,
                height=logo_height,
                preserveAspectRatio=True,
            )
        except Exception as e:
            print(f"Warning: Could not load logo from {organiser_logo}: {e}")

    # Add decorative border
    c.setLineWidth(3)
    c.setStrokeColor(org_color)
    margin = 0.3 * inch
    c.rect(margin, margin, width - 2 * margin, height - 2 * margin, stroke=1, fill=0)

    # Organization header - Organiser name
    c.setFont(title_font, 18)
    c.setFillColor(org_color)
    c.drawCentredString(width / 2, height - 1.0 * inch, organiser)

    # Main certificate text
    c.setFont(title_font, 18)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height / 2 + 2 * inch, "This is to certify that")

    # Attendee name (large, prominent)
    c.setFont(title_font, 28)
    c.setFillColor(org_color)
    c.drawCentredString(width / 2, height / 2 + 1.2 * inch, attendee_name)

    # Attended text
    c.setFont(title_font, 18)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height / 2 + 0.4 * inch, "Attended the")

    # Course title
    c.setFont(title_font, 20)
    c.setFillColor(org_color)
    c.drawCentredString(width / 2, height / 2 - 0.3 * inch, course_title)

    # Location and date
    c.setFont(body_font, 16)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height / 2 - 1 * inch, location)
    c.drawCentredString(width / 2, height / 2 - 1.5 * inch, date)

    # Host information at the bottom
    footer_y = 1.5 * inch
    c.setFont(body_font, 12)
    c.setFillColor(colors.black)

    if host_name:
        c.drawCentredString(width / 2, footer_y, f"Host: {host_name}")
        c.drawCentredString(width / 2, footer_y - 0.35 * inch, host_hospital)
        c.drawCentredString(width / 2, footer_y - 0.65 * inch, host_trust)
    else:
        c.drawCentredString(width / 2, footer_y, host_hospital)
        c.drawCentredString(width / 2, footer_y - 0.35 * inch, host_trust)

    # Footer with generation timestamp
    c.setFont(body_font, 10)
    c.setFillColor(colors.grey)
    c.drawString(
        margin,
        0.5 * inch,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    )

    # Save the PDF
    c.save()
    return os.path.abspath(output_path)


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
