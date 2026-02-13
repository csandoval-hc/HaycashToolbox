from __future__ import annotations

import csv
import os
from datetime import datetime, timezone
from pathlib import Path
import time

import streamlit as st


def _get_shared_password() -> str | None:
    # Preferred: Streamlit secrets
    try:
        pw = st.secrets.get("auth", {}).get("SHARED_PASSWORD")
        if isinstance(pw, str) and pw.strip():
            return pw
    except Exception:
        pass

    # Fallback: env var
    pw = os.getenv("TOOLBOX_SHARED_PASSWORD")
    if pw and pw.strip():
        return pw
    return None


def _log_attempt(root: Path, username: str, ok: bool) -> None:
    # Logs to a local CSV file so you can identify who logged in.
    # Note: if multiple users access concurrently on a server, you may want a proper DB or file lock.
    log_dir = root / ".auth"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "auth_log.csv"

    row = {
        "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "username": username,
        "ok": str(bool(ok)),
        "client_ip": st.context.ip if hasattr(st, "context") and getattr(st.context, "ip", None) else "",
        "user_agent": st.context.headers.get("User-Agent", "") if hasattr(st, "context") and getattr(st.context, "headers", None) else "",
    }

    write_header = not log_path.exists()
    with log_path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if write_header:
            w.writeheader()
        w.writerow(row)


def require_shared_password() -> None:
    """Non-skippable gate:
    - Username: any non-empty string (used for identification + logging)
    - Password: single shared password configured in secrets/env
    """
    root = Path(__file__).resolve().parent

    shared_pw = _get_shared_password()
    if not shared_pw:
        st.error(
            "Authentication is not configured.\n\n"
            "Set one of:\n"
            "- .streamlit/secrets.toml → [auth].SHARED_PASSWORD\n"
            "- Environment variable: TOOLBOX_SHARED_PASSWORD"
        )
        st.stop()

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "auth_username" not in st.session_state:
        st.session_state.auth_username = ""
    if "auth_failures" not in st.session_state:
        st.session_state.auth_failures = 0

    if st.session_state.authenticated:
        return

    st.title("Sign in")
    st.caption("Enter any username (for identification) and the shared password to access the ToolBox.")

    username = st.text_input("Username", value=st.session_state.auth_username, max_chars=64)
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns([1, 3])
    with col1:
        submitted = st.button("Enter", use_container_width=True)

    if submitted:
        username_clean = (username or "").strip()
        if not username_clean:
            st.warning("Username is required.")
            st.stop()

        if password == shared_pw:
            st.session_state.authenticated = True
            st.session_state.auth_username = username_clean
            st.session_state.auth_failures = 0
            _log_attempt(root, username_clean, ok=True)
            st.rerun()
        else:
            st.session_state.auth_failures += 1
            _log_attempt(root, username_clean, ok=False)

            # Basic slowdown against rapid guessing.
            delay = min(2.0, 0.5 + 0.25 * st.session_state.auth_failures)
            time.sleep(delay)
            st.error("Incorrect password.")
            st.stop()

    st.stop()
