import base64
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
import yaml

# Keep crown (Streamlit default) by not setting page_icon
st.set_page_config(page_title="HayCash ToolBox", layout="wide", initial_sidebar_state="collapsed")

# Non-skippable access gate (username for identification + shared password)
from simple_auth import require_shared_password
require_shared_password()

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def load_registry():
    cfg_path = ROOT / "apps.yaml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    apps = cfg.get("apps", [])

    required = {"id", "name", "page"}
    for a in apps:
        missing = [k for k in required if k not in a]
        if missing:
            raise ValueError("Each app in apps.yaml must have: id, name, page (and optional icon).")
    return apps


# ---- Load assets
bg_b64 = b64(ASSETS / "bg.jpg")
logo_b64 = b64(ASSETS / "haycash_logo.jpg")

# ---- Splash (Haycash logo only)
if "booted" not in st.session_state:
    st.session_state.booted = False

if not st.session_state.booted:
    st.markdown(
        f"""
        <style>
          .stApp {{
            background: #0b1020;
          }}
          header, footer, [data-testid="stToolbar"] {{
            visibility: hidden;
            height: 0px;
          }}
          .block-container {{
            padding: 0 !important;
            max-width: 100% !important;
          }}
        </style>

        <div style="height:90vh;display:flex;align-items:center;justify-content:center;">
          <img
            src="data:image/jpg;base64,{logo_b64}"
            style="height:170px;filter: drop-shadow(0 0 22px rgba(124,200,255,0.30)); border-radius:14px;"
          />
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(1.8)
    st.session_state.booted = True
    st.rerun()

# ---- Make Streamlit outer page match the space background (removes white edges)
st.markdown(
    f"""
    <style>
      /* Professional font */
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

      .stApp {{
        background: url("data:image/jpg;base64,{bg_b64}") no-repeat center center fixed;
        background-size: cover;
        font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif !important;
      }}

      /* Remove Streamlit default padding so the iframe fills edge-to-edge */
      .block-container {{
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
      }}

      header, footer, [data-testid="stToolbar"] {{
        visibility: hidden;
        height: 0px;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

apps = load_registry()

# ---- Handle navigation action via query param
q = st.query_params
launch_id = q.get("launch", None)

if launch_id:
    target = next((a for a in apps if a["id"] == launch_id), None)
    if not target:
        st.query_params.clear()
        st.rerun()

    # Clear query param so refresh doesn't re-trigger
    st.query_params.clear()

    # Switch to the multipage tool (single server, no subprocess)
    st.switch_page(target["page"])


# ---- Build cards HTML (same look; now links set ./?launch=<id>)
cards_html = ""
for app in apps:
    name = app["name"]
    icon_path = ROOT / app.get("icon", "")
    icon_b64 = b64(icon_path) if icon_path.exists() else ""
    icon_img = f"<img src='data:image/svg+xml;base64,{icon_b64}' />" if icon_b64 else ""

    cards_html += f"""
      <a class="cardlink" href="./?launch={app['id']}">
        <div class="card">
          <div class="card-top">
            <div class="icon">{icon_img}</div>
            <div class="name">{name}</div>
          </div>
          <div class="meta">Streamlit</div>
          <div class="corner"></div>
        </div>
      </a>
    """


page = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
  html, body {{
    height: 100%;
    margin: 0;
    font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
  }}

  body {{
    background: url("data:image/jpg;base64,{bg_b64}") no-repeat center center fixed;
    background-size: cover;
  }}

  .overlay {{
    min-height: 100vh;
    width: 100%;
    background:
      radial-gradient(1200px 600px at 18% 22%, rgba(90,205,255,0.10), transparent 60%),
      radial-gradient(900px 500px at 82% 30%, rgba(124,200,255,0.08), transparent 55%),
      linear-gradient(to bottom, rgba(6,8,14,0.55), rgba(6,8,14,0.78));
    padding: 38px 18px 44px 18px;
    box-sizing: border-box;
  }}

  .wrap {{
    max-width: 1100px;
    margin: 0 auto;
  }}

  .header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    margin-bottom: 26px;
  }}

  .brand {{
    display: flex;
    align-items: center;
    gap: 14px;
  }}

  .brand img {{
    height: 44px;
    border-radius: 10px;
  }}

  .title {{
    color: rgba(255,255,255,0.92);
    font-size: 26px;
    font-weight: 800;
    letter-spacing: 0.2px;
    line-height: 1.2;
  }}

  .subtitle {{
    color: rgba(210,230,255,0.72);
    font-size: 14px;
    margin-top: 4px;
    font-weight: 500;
  }}

  .grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }}

  @media (max-width: 980px) {{
    .grid {{
      grid-template-columns: repeat(2, 1fr);
    }}
  }}

  @media (max-width: 620px) {{
    .grid {{
      grid-template-columns: 1fr;
    }}
  }}

  a.cardlink {{
    text-decoration: none;
  }}

  .card {{
    position: relative;
    border-radius: 18px;
    padding: 18px 18px 16px 18px;
    background: rgba(9,12,20,0.58);
    border: 1px solid rgba(124,200,255,0.18);
    box-shadow: 0 12px 40px rgba(0,0,0,0.35);
    overflow: hidden;
    transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
    min-height: 126px;
  }}

  .card:hover {{
    transform: translateY(-2px);
    border-color: rgba(124,200,255,0.35);
    background: rgba(12,16,26,0.62);
  }}

  .card-top {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}

  .icon {{
    width: 44px;
    height: 44px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(124,200,255,0.10);
    border: 1px solid rgba(124,200,255,0.16);
    flex: 0 0 auto;
  }}

  .icon img {{
    width: 26px;
    height: 26px;
  }}

  .name {{
    color: rgba(255,255,255,0.92);
    font-weight: 800;
    font-size: 16px;
    letter-spacing: 0.2px;
  }}

  .meta {{
    margin-top: 10px;
    color: rgba(210,230,255,0.68);
    font-size: 13px;
    font-weight: 600;
  }}

  .corner {{
    position: absolute;
    right: -30px;
    bottom: -30px;
    width: 140px;
    height: 140px;
    border-radius: 999px;
    background: radial-gradient(circle at 30% 30%, rgba(124,200,255,0.22), transparent 55%);
    filter: blur(0px);
    pointer-events: none;
  }}
</style>
</head>

<body>
  <div class="overlay">
    <div class="wrap">
      <div class="header">
        <div class="brand">
          <img src="data:image/jpg;base64,{logo_b64}" />
          <div>
            <div class="title">HayCash ToolBox</div>
            <div class="subtitle">Select a tool</div>
          </div>
        </div>
      </div>

      <div class="grid">
        {cards_html}
      </div>
    </div>
  </div>
</body>
</html>
"""

components.html(page, height=920, scrolling=False)
