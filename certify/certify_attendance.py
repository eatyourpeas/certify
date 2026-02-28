"""Package shim for certify_attendance inside the `certify` package.

This mirrors the previous top-level `certify_attendance.py` shim but lives
inside the package so `import certify_attendance` can be replaced by
`from certify import certify_attendance` or `import certify`.
"""

from typing import Optional

try:
    from main import create_certificate  # type: ignore
except Exception:  # pragma: no cover - best-effort shim
    create_certificate = None

try:
    from .batch_generate import generate_batch  # type: ignore
except Exception:  # pragma: no cover
    generate_batch = None

__all__ = ["create_certificate", "generate_batch"]
