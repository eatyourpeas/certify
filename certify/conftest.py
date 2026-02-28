import sys
from pathlib import Path

# When running tests with the current working directory set to the package
# folder (e.g. `cd certify && pytest`), ensure the parent repo root is on
# sys.path so imports like `from certify import ...` and `from main import ...`
# resolve correctly.
PKG_DIR = Path(__file__).parent.resolve()
REPO_ROOT = PKG_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
