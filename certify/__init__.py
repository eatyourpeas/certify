"""Top-level package for certify.

This package re-exports the batch generation API and provides a stable import
surface so consumers can `from certify.batch_generate import generate_batch`
or `import certify` for convenience.
"""

from .batch_generate import generate_batch  # re-export
from .generate_certificate import main as interactive_main  # convenience

# Expose the create_certificate helper from the top-level `main.py` for
# compatibility (best-effort; main.py stays at the repo root per request).
try:
    from main import create_certificate  # type: ignore
except Exception:  # pragma: no cover - best-effort shim
    create_certificate = None

__all__ = ["generate_batch", "interactive_main", "create_certificate"]
