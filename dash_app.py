"""Dash entrypoint for deploying the TechnoTaggr visualization app.

This wrapper ensures the `technotaggr` package is importable in environments
like Plotly Cloud where the project isn't automatically installed with its
`src/` layout. It simply creates the Dash app from the package code and exposes
the `app`/`server` variables expected by the platform.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the src layout is on the import path when running directly
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if SRC_DIR.exists():
    sys.path.insert(0, str(SRC_DIR))

from .visualization import create_dashboard

# Create the Dash app and expose WSGI server for hosting platforms
app = create_dashboard()
server = app.server

if __name__ == "__main__":
    app.run(debug=True)
