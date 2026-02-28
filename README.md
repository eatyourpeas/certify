# Certify - Certificate Generator

![PyPI - Version](https://img.shields.io/pypi/v/certify-attendance?style=flat-square&color=%2398FB98)

A flexible, reusable Python tool to generate personalized PDF certificates for course attendees using ReportLab.

**Primarily designed for South Thames Paediatric Endocrine Group (STPEG)**, but built to be customizable for any organization.

## Features

- ✨ Generate professional PDF certificates from command line
- 📝 Customizable organizer name and logo
- 🎨 Professional styling with organization branding
- � Automatic folder organization by year and event
- �🔧 Easy-to-use interactive mode
- 📦 Built with ReportLab for high-quality PDF output
- 🔄 Fully reusable - designed for any organization

## Sample Certificate

Here's an example of a generated certificate for Dr Simon Chapman attending the STPEG Autumn Meeting 2025:

![Sample Certificate](2025_STPEG_Autumn_Meeting/sample_certificate_preview.png)

See the [full PDF sample](2025_STPEG_Autumn_Meeting/sample_certificate.pdf) for the complete certificate.

## Setup

This project uses `uv` as the Python package manager for fast, reliable dependency management.

### Prerequisites

- Python 3.13+
- `uv` (install via: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/eatyourpeas/Certify.git
   cd Certify
   ```

2. **Activate the environment:**
   ```bash
   source ~/.local/bin/env
   source .venv/bin/activate
   ```

3. **Dependencies are already installed:**
   - `reportlab` - PDF generation
   - `pillow` - Image processing

## Usage

### Interactive Mode (Recommended)

```bash
# Interactive (packaged)
uv run python -m certify.generate_certificate
```

You will be prompted to enter:

- **Event name** - Name of the course/conference
- **Event year** - Year (defaults to current year)
- **Organiser name** - Organization hosting the event (defaults to "South Thames Paediatric Endocrine Group")
- **Organiser logo** - Path to PNG logo file (defaults to "logo.png")
- **Attendee's name** - Name of the certificate recipient
- **Course/event title** - Title of the course attended
- **Location** - Where the event took place
- **Date** - Event date (e.g., "27th May 2024")
- **Host hospital** - Hospital name (optional, for institutional context)
- **Host trust** - NHS trust name (optional, for institutional context)
- **Host name** - Individual organizer (e.g., "Dr Charlotte Jackson") (optional)
- **Output filename** - Where to save the certificate (optional, auto-generated from attendee name)

### Programmatic Mode

Use the `create_certificate()` function in your own scripts:

```python
from certify import create_certificate

output_file = create_certificate(
    attendee_name="Jane Doe",
    course_title="Endocrinology Workshop",
    location="Royal Alexandra Children's Hospital",
    date="27th May 2024",
    organiser="Your Organization Name",
    organiser_logo="path/to/your/logo.png",
    host_hospital="Kingston Hospital",
    host_trust="NHS Trust",
    host_name="Dr John Smith",
    output_path="jane_doe_certificate.pdf"
)

print(f"Certificate saved to: {output_file}")
```

### Batch Mode (CSV / TXT)

Generate certificates for many attendees at once using `batch_generate.py`.

CSV: By default the importer is optimised for EventBrite exports — it recognises the exact column names
`Attendee first name` and `Attendee Surname` (including casing and spaces). It will also accept common
single-column name headers such as `name`, `full_name`, or `attendee_name`.

Additional per-row override columns are supported: `output_filename`, `host_name`, `organiser`, `organiser_logo`, `course_title`, `location`, `date`, `host_hospital`, `host_trust`.

TXT: a simple newline-separated list of attendee names.

Example (EventBrite CSV):

```bash
uv run python -m certify.batch_generate --input attendees.csv \
   --event-name "STPEG Autumn Meeting" \
   --course-title "STPEG Autumn Meeting 2025" \
   --location "Brighton" \
   --date "27th May 2025" \
   --zip
```

If your CSV uses different column names you can override the field mapping:

```bash
uv run python -m certify.batch_generate --input attendees.csv \
   --first-name-field "Given Name" --surname-field "Family Name" \
   --event-name "STPEG Autumn Meeting" --course-title "..." --location "..." --date "..."
```

The script creates a folder named `<year>_<eventname>` and writes one PDF per attendee. Use `--zip` to create a ZIP archive containing all generated certificates.

-----------------

#### Email preparation

`batch_generate.py` can also prepare email jobs for each attendee so an external service
or web layer can send them. By default the importer recognises the EventBrite export
columns `Attendee first name`, `Attendee Surname` and `Attendee email` and will map
email addresses to generated certificate files.

CLI flags:

- `--email-field` (default: `Attendee email`) — CSV column to read recipient addresses from.
- `--prepare-emails` — prepare and print a list of email jobs mapping recipient -> certificate file (does not send).

Behaviour notes:

- `generate_batch()` returns a dict including `email_jobs`, an array of simple objects with the keys: `recipient`, `name`, `filepath`, `subject`, `body`, and `meta`. This is intended to be consumed by a service layer (FastAPI/Flask) responsible for sending.
- Duplicate attendees are deduplicated (one certificate generated) and the run summary logs duplicates and skipped rows.
- Sending emails is intentionally left to the consuming service. Implementations can use SMTP, Microsoft Graph, or platform-specific adapters to send or create drafts.

Example: prepare email jobs (no send)

```bash
uv run python -m certify.batch_generate --input attendees.csv \
   --event-name "STPEG Autumn Meeting" \
   --course-title "STPEG Autumn Meeting 2025" \
   --location "Brighton" \
   --date "27th May 2025" \
   --prepare-emails
```

### Quick Test

To test with default STPEG values:

```bash
# Quick test (packaged entry points)
uv run python -m certify.generate_certificate
```

This generates `certificate_sample.pdf` with example data.

## Customization

### For Different Organizations

1. **Logo Setup:**
   - Place your organization's logo as a PNG file in the project directory
   - Use any filename (pass the path to `organiser_logo` parameter)
   - Recommended size: At least 500×500 pixels for best quality

2. **Default Values:**
   - Change the defaults in `main.py` function parameters
   - Or specify custom values every time via interactive mode

3. **Certificate Appearance:**
   Edit `certify/generate_certificate.py` to customize:
   - **Colors**: Line 35 (`org_color = colors.HexColor("#003366")`)
   - **Fonts**: Lines 34-35
   - **Layout/positioning**: Adjust the `inch` values in draw functions
   - **Border style**: Lines 41-44

### Example: Using a Different Logo

```bash
uv run python -m certify.generate_certificate
# When prompted:
# Organiser logo: /path/to/my_logo.png
```

### Example: Using for a Different Organization

```bash
uv run python -m certify.generate_certificate
# When prompted:
# Event name: AI Workshop 2024
# Organiser name: TechCorp Training Institute
# Organiser logo: techcorp_logo.png
# ... continue with other details
```

## File Organization

Certificates are automatically organized into folders by year and event name:

```
Certify/
├── 2024_STPEG_Training_Conference/
│   ├── michael_rogers.pdf
│   ├── sarah_mitchell.pdf
│   └── ...
├── 2024_Advanced_Workshop/
│   ├── jane_doe.pdf
│   └── ...
└── main.py
```

## Project Structure

```
Certify/
├── certify/                   # Main package
│   ├── __init__.py           # Package exports (create_certificate, generate_batch)
│   ├── generate_certificate.py # Core certificate generation function
│   └── batch_generate.py      # Batch processing and email job preparation
├── tests/                     # Unit tests
├── pyproject.toml             # Project configuration & dependencies
├── uv.lock                    # Locked dependency versions
├── logo.png                   # Default STPEG logo (customize for your organization)
├── LICENSE                    # MIT License
├── README.md                  # This file
└── [year_eventname]/          # Auto-generated folders for organized certificates
   └── certificates.pdf
```

## Project Management with `uv`

### Install a New Dependency

```bash
uv add package_name
```

### Run a Script

```bash
uv run python script.py
```

### Sync Environment

```bash
uv sync
```

## Troubleshooting

### `uv` command not found

Ensure `uv` is in your PATH:

```bash
source ~/.local/bin/env
```

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Logo not displaying

- Ensure the PNG file exists at the specified path
- Check file permissions (should be readable)
- Verify the file is a valid PNG image
- Use absolute paths if relative paths don't work

### Module not found errors

Make sure you're using `uv run`:

```bash
uv run python -m certify.generate_certificate
```

Or activate the virtual environment and use the module syntax:

```bash
source .venv/bin/activate
python -m certify.generate_certificate
```

## Next Steps

- ✅ Customize the `organiser` and `organiser_logo` for your organization
- 🌐 Build a web interface with Flask or FastAPI
- 💾 Integrate with a database for auto-generating certificates on course completion
- 📧 Add email functionality to automatically send certificates to attendees

## Defaults (STPEG Configuration)

This tool is optimized for South Thames Paediatric Endocrine Group with the following defaults:

- **Organiser:** South Thames Paediatric Endocrine Group
- **Logo:** `logo.png`
- **Host Hospital:** Royal Alexandra Children's Hospital
- **Host Trust:** Brighton & Sussex University Hospitals

All parameters can be overridden for use with other organizations.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, feature requests, or to adapt this for your organization, please reach out through GitHub.

---

**Made with ❤️ for STPEG and shared for the community**
