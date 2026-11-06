"""HTML builders for the research desk shell.

Every builder returns a string of escaped HTML; no widget is created here so the
functions stay side-effect free and easy to reason about from app.py.
"""

from __future__ import annotations

import html
import re
from urllib.parse import urlparse

from src.ui.icons import icon

_LEADING_H1 = re.compile(r"\A\s*#\s+.*(?:\r?\n)+")

_URL_RE = re.compile(r"https?://[^\s)\]\}\"'<>]+")
_TRAILING_CHARS = ".,;:)]}'\"\u2019\u201d"

_RUN_STATE_LABELS = {
    "idle": "idle",
    "running": "running",
    "complete": "complete",
    "error": "failed",
}


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def strip_leading_heading(markdown_text: str) -> str:
    """Drop a leading "# Title" line.

    The workspace already renders the topic as the document title, so the
    report repeating it as an H1 reads as a duplicate heading. Only the very
    first line is touched and nothing else in the document is rewritten.
    """

    if not markdown_text:
        return markdown_text
    return _LEADING_H1.sub("", markdown_text, count=1)


# --------------------------------------------------------------------------- #
# Sidebar
# ============================================================
def render_brand() -> str:
    return (
        '<div class="fx-brand">'
        '<span class="fx-mark" aria-hidden="true"></span>'
        '<span class="fx-brand-text">'
        '<span class="fx-brand-name">Research Desk</span>'
        '<span class="fx-brand-sub">multi-agent pipeline</span>'
        "</span>"
        "</div>"
    )


def _marker(state: str) -> str:
    if state == "finished":
        return icon("check", 12, 2.6)
    if state in ("failed", "unavailable"):
        return icon("circle-alert", 12, 2.2)
    return ""


def render_stage_rail(views: list[dict[str, str]]) -> str:
    """Four connected stage rows reflecting the callbacks the run emitted."""

    rows: list[str] = []
    for view in views:
        state = view["state"]
        detail = view.get("detail", "")
        detail_html = f'<span class="fx-stage-detail">{_esc(detail)}</span>' if detail else ""
        current = ' aria-current="step"' if state == "running" else ""
        rows.append(
            f'<li class="fx-stage fx-stage--{_esc(state)}"{current}>'
            f'<span class="fx-stage-marker">{_marker(state)}</span>'
            '<span class="fx-stage-body">'
            f'<span class="fx-stage-title">{icon(view["icon"], 14)}'
            f"<span>{_esc(view['title'])}</span></span>"
            f'<span class="fx-stage-state">{_esc(view["state_label"])}{detail_html}</span>'
            "</span>"
            "</li>"
        )
    return f'<ol class="fx-rail" role="list" aria-label="Pipeline stages">{"".join(rows)}</ol>'


def render_run_details(events: list[str]) -> str:
    rows = "".join(
        f'<li class="fx-ev"><span class="fx-ev-idx">{index:02d}</span>'
        f"<span>{_esc(label)}</span></li>"
        for index, label in enumerate(events, start=1)
    )
    return f'<ul class="fx-events" role="list">{rows}</ul>'


# --------------------------------------------------------------------------- #
# Main workspace
# ============================================================
def render_app_bar(run_status: str) -> str:
    label = _RUN_STATE_LABELS.get(run_status, run_status)
    return (
        '<div class="fx-appbar">'
        '<div class="fx-appbar-left">'
        '<span class="fx-apptitle">Research Desk</span>'
        '<span class="fx-appdiv" aria-hidden="true"></span>'
        '<span class="fx-appmeta">4-stage pipeline</span>'
        "</div>"
        f'<span class="fx-runstate fx-runstate--{_esc(run_status)}">'
        '<span class="fx-dot" aria-hidden="true"></span>'
        f"{_esc(label)}</span>"
        "</div>"
    )


def render_idle_workspace(views: list[dict[str, str]]) -> str:
    rows = "".join(
        f'<li class="fx-manifest-row">'
        f'<span class="fx-idx">{index:02d}</span>'
        f'<span class="fx-m-title">{icon(view["icon"], 14)}<span>{_esc(view["title"])}</span></span>'
        f'<span class="fx-m-out">{_esc(view["produces"])}</span>'
        "</li>"
        for index, view in enumerate(views, start=1)
    )
    return (
        '<div class="fx-idle">'
        '<h2 class="fx-idle-title">Nothing researched yet.</h2>'
        '<p class="fx-idle-copy">Enter a topic in the run console. You get a sourced brief, '
        "a critic&rsquo;s score, and the pages it read.</p>"
        f'<ol class="fx-manifest" role="list" aria-label="Pipeline stages and their output">{rows}</ol>'
        "</div>"
    )


def render_document_header(topic: str, score_text: str, critique_state: str) -> str:
    if critique_state in ("unavailable", "absent", "unscored"):
        value = "Unavailable" if critique_state == "unavailable" else "Not returned"
        chip = (
            '<span class="fx-score fx-score--muted">'
            '<span class="fx-score-label">critic score</span>'
            f'<span class="fx-score-value">{value}</span>'
            "</span>"
        )
    else:
        chip = (
            '<span class="fx-score">'
            '<span class="fx-score-label">critic score</span>'
            f'<span class="fx-score-value">{_esc(score_text)}</span>'
            "</span>"
        )

    return (
        '<div class="fx-dochead">'
        f'<h1 class="fx-doc-title">{_esc(topic)}</h1>'
        f'<div class="fx-dochead-meta">{chip}</div>'
        "</div>"
    )


# --------------------------------------------------------------------------- #
# Sources
# ============================================================
def extract_links(text: str, limit: int = 10) -> list[str]:
    """Pull unique URLs out of the search-agent output (no links are invented)."""

    seen: set[str] = set()
    links: list[str] = []
    for match in _URL_RE.findall(text or ""):
        url = match.rstrip(_TRAILING_CHARS)
        if len(url) < 12 or url in seen:
            continue
        seen.add(url)
        links.append(url)
        if len(links) >= limit:
            break
    return links


def render_source_links(links: list[str]) -> str:
    if not links:
        return ""

    rows: list[str] = []
    for url in links:
        parsed = urlparse(url)
        host = parsed.netloc.replace("www.", "") or url
        path = parsed.path or ""
        if parsed.query:
            path = f"{path}?{parsed.query}"
        if len(path) > 74:
            path = f"{path[:71]}\u2026"
        rows.append(
            f'<li class="fx-link-row"><a class="fx-link" href="{_esc(url)}" '
            'target="_blank" rel="noopener noreferrer">'
            f'<span class="fx-link-body"><span class="fx-link-host">{_esc(host)}</span>'
            f'<span class="fx-link-path">{_esc(path or "/")}</span></span>'
            f'<span class="fx-link-icon">{icon("arrow-up-right", 14)}</span>'
            "</a></li>"
        )

    return (
        '<div class="fx-links">'
        '<div class="fx-links-head">links found in search results</div>'
        f'<ul class="fx-link-list" role="list">{"".join(rows)}</ul>'
        "</div>"
    )
