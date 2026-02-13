# Auto-generated wrapper to run existing Streamlit app without modifying its code.
import os, runpy

_APP_DIR = os.path.join(os.path.dirname(__file__), "..", "apps/lector_edocat")
_APP_DIR = os.path.abspath(_APP_DIR)
os.chdir(_APP_DIR)

runpy.run_path(os.path.join(_APP_DIR, "app.py"), run_name="__main__")
