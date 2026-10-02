"""
Path helpers that work both when running from source AND when running
from a PyInstaller frozen executable (one-file build).

When frozen, data files (database.db, known_faces/, employee_reports/)
live next to the .exe instead of inside the bundled temp folder, so:
  - user data survives app updates
  - the exe can be copied to another laptop together with its data folder
"""

import os
import sys


def is_frozen() -> bool:
    """True when running as a packaged (PyInstaller) executable."""
    return getattr(sys, "frozen", False)


def app_dir() -> str:
    """
    Base directory for the application.

    - Normal run : folder containing the source code.
    - Frozen run : folder containing the .exe file.
    """
    if is_frozen():
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def data_path(*parts: str) -> str:
    """Return an absolute path relative to the app directory."""
    return os.path.join(app_dir(), *parts)
