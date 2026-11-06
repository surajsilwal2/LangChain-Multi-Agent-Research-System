"""Injection point for the app's design system."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

CSS_PATH = Path(__file__).resolve().parent / "styles" / "app.css"


def load_css() -> str:
    """Read the stylesheet on each rerun so edits show without a server restart."""

    return CSS_PATH.read_text(encoding="utf-8")


def inject_styles() -> None:
    """Mount the stylesheet once, right after set_page_config."""

    st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)
