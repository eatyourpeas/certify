"""Top-level package for certify.

This package re-exports the batch generation API and provides a stable import
surface so consumers can `from certify.batch_generate import generate_batch`
or `import certify` for convenience.
"""

from .batch_generate import generate_batch  # re-export
from .generate_certificate import main as interactive_main  # convenience
from .generate_certificate import create_certificate  # re-export

__all__ = ["generate_batch", "interactive_main", "create_certificate"]
