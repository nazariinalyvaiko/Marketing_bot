from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure project root is on sys.path for imports like `marketing_bot.*`
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

# Default to offline mode for tests to avoid external calls
os.environ.setdefault("OFFLINE_MODE", "true") 