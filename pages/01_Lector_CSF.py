# Auto-generated wrapper to run existing Streamlit app without modifying its code.
import os
import runpy
from pathlib import Path

from simple_auth import require_shared_password

require_shared_password()

# Repo root (works on Streamlit Cloud and locally)
ROOT = Path(__file__).resolve().parents[1]

# Target app folder inside repo
APP_DIR = ROOT / "apps" / "cdf_isaac"

# Change working directory so relative paths inside the tool still work
os.chdir(APP_DIR)

# Run the original Streamlit app
runpy.run_path(str(APP_DIR / "app_isaac.py"), run_name="__main__")
