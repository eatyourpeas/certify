# Compatibility shim to expose a module named `certify_attendance`
# which forwards to the existing top-level modules in this repo.
from typing import Optional

# Import primary APIs from existing files
try:
    from main import create_certificate  # type: ignore
except Exception:  # pragma: no cover - best-effort shim
    create_certificate = None

try:
    from batch_generate import generate_batch  # type: ignore
except Exception:  # pragma: no cover
    generate_batch = None

__all__ = ["create_certificate", "generate_batch"]
