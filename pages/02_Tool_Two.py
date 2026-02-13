import base64
from pathlib import Path
import streamlit as st

from simple_auth import require_shared_password
require_shared_password()
from pathlib import Path
import base64

def _get_bg_b64() -> str:
    img_path = Path(__file__).resolve().parents[1] / "assets" / "bg.jpg"
    return base64.b64encode(img_path.read_bytes()).decode("utf-8")

bg_b64 = _get_bg_b64()

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()

bg_b64 = b64(ASSETS / "bg.jpg")

st.set_page_config(page_title="Tool Two · HayCash ToolBox", layout="wide")

st.markdown(
    f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

      .stApp {
        background: url("data:image/jpg;base64,{bg_b64}") no-repeat center center fixed;
        background-size: cover;
        font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif !important;
      }
      .block-container {
        padding-top: 2rem !important;
        max-width: 1100px !important;
      }
      header, footer, [data-testid="stToolbar"] {
        visibility: hidden;
        height: 0px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Tool Two")
st.caption("Placeholder multipage tool.")

st.info("Replace this page's contents with your tool UI (keep the require_shared_password() call at the top).")
