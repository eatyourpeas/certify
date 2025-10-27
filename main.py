from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from datetime import datetime
import os


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


def main():
    """Example usage of the certificate generator."""
    
    # Example certificate details
    attendee_name = "John Smith"
    course_title = "STPEG 20th Anniversary Meeting"
    location = "Royal Alexandra Children's Hospital (RACH), Brighton"
    date = "27th May 2024"
    
    # Generate the certificate
    output_file = create_certificate(
        attendee_name=attendee_name,
        course_title=course_title,
        location=location,
        date=date,
        output_path="certificate_sample.pdf",
        organiser="South Thames Paediatric Endocrine Group",
        organiser_logo="logo.png",
        host_hospital="Royal Alexandra Children's Hospital (RACH)",
        host_trust="Brighton & Sussex University Hospitals",
        host_name="Dr Charlotte Jackson",
    )
    
    print(f"✓ Certificate generated successfully!")
    print(f"  Attendee: {attendee_name}")
    print(f"  Course: {course_title}")
    print(f"  Location: {location}")
    print(f"  Date: {date}")
    print(f"  Saved to: {output_file}")


if __name__ == "__main__":
    main()
