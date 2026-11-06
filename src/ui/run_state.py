"""Run state for the research desk UI.

Everything the UI needs to know about a run is derived from four sources:
the stage definitions below, the progress callbacks the pipeline actually
emitted, the returned result dict, and whether the run failed.

This module is intentionally free of HTML so it stays testable.
"""

from __future__ import annotations

import re
from typing import Literal, NamedTuple

import streamlit as st

RunStatus = Literal["idle", "running", "complete", "error"]
StageState = Literal["not_started", "running", "finished", "failed", "unavailable"]
CritiqueState = Literal["scored", "unscored", "unavailable", "absent"]


class Stage(NamedTuple):
    key: str
    title: str
    callback: str
    produces: str
    icon: str


# The callback strings are the exact labels src/pipelines/pipelines.py emits.
STAGES: tuple[Stage, ...] = (
    Stage("search", "Web search", "Searching for reliable sources", "Top 5 results", "search"),
    Stage("read", "Source reading", "Reading selected sources", "Extracted page text", "book-open"),
    Stage("write", "Report writing", "Drafting the research report", "Draft report", "pen-line"),
    Stage("critique", "Critique", "Reviewing the report", "Feedback and score", "clipboard-check"),
)

CALLBACK_TO_INDEX: dict[str, int] = {stage.callback: index for index, stage in enumerate(STAGES)}

STATE_LABELS: dict[str, str] = {
    "not_started": "Not started",
    "running": "Running",
    "finished": "Finished",
    "failed": "Failed",
    "unavailable": "Unavailable",
}

_STATE_DEFAULTS: dict[str, object] = {
    "research_result": None,
    "research_topic": "",
    "run_events": [],
    "stage_index": -1,
    "run_status": "idle",
    "run_error": None,
    "run_error_summary": None,
    "empty_topic_warning": False,
}

# Failure strings written by the pipeline when the critic step does not return.
_CRITIQUE_FAILURE_PREFIXES = (
    "The critique step was skipped",
    "Critique step failed",
)

_SCORE_PATTERN = re.compile(
    r"(?:score\s*[:\-\u2014]?\s*)?\*{0,2}\s*(\d{1,2}(?:\.\d+)?)\s*\*{0,2}\s*/\s*10",
    re.IGNORECASE,
)


def init_state() -> None:
    """Set defaults once; never clobber a result that is already in session."""

    for key, value in _STATE_DEFAULTS.items():
        st.session_state.setdefault(key, value if not isinstance(value, list) else [])


def begin_run(topic: str) -> None:
    """Clear the previous run so a failure can never show a stale report."""

    st.session_state.research_result = None
    st.session_state.research_topic = topic
    st.session_state.run_events = []
    st.session_state.stage_index = 0
    st.session_state.run_status = "running"
    st.session_state.run_error = None
    st.session_state.run_error_summary = None


def record_event(label: str) -> int:
    """Log a callback and advance the rail to the stage it belongs to."""

    events = st.session_state.run_events
    events.append(label)
    st.session_state.run_events = events
    index = CALLBACK_TO_INDEX.get(label)
    if index is not None:
        st.session_state.stage_index = index
    return st.session_state.stage_index


def finish_run(result: dict) -> None:
    st.session_state.research_result = result
    st.session_state.run_status = "complete"
    if result.get("report"):
        st.session_state.stage_index = len(STAGES) - 1


def fail_run(message: str, summary: str | None = None) -> None:
    st.session_state.run_status = "error"
    st.session_state.run_error = message
    st.session_state.run_error_summary = summary


def parse_score(feedback: str) -> float | None:
    """Pull "X/10" out of the critic's text. Returns None when it is absent."""

    if not feedback:
        return None
    matches = _SCORE_PATTERN.findall(feedback)
    if not matches:
        return None
    for raw in reversed(matches):
        value = float(raw)
        if 0 <= value <= 10:
            return value
    return None


def format_score(value: float | None) -> str:
    return "Not returned" if value is None else f"{value:g}/10"


def critique_state_of(feedback: str) -> CritiqueState:
    if not feedback:
        return "absent"
    stripped = feedback.lstrip()
    if stripped.startswith(_CRITIQUE_FAILURE_PREFIXES):
        return "unavailable"
    return "scored" if parse_score(feedback) is not None else "unscored"


def report_filename(topic: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:60].strip("-")
    return f"{slug or 'research-report'}.md"


def stage_state(
    index: int,
    active_index: int,
    run_status: RunStatus,
    critique: CritiqueState,
) -> StageState:
    if run_status == "complete":
        if index == len(STAGES) - 1 and critique == "unavailable":
            return "unavailable"
        return "finished"
    if run_status == "error":
        if index == active_index:
            return "failed"
        return "finished" if index < active_index else "not_started"
    if index == active_index:
        return "running"
    return "finished" if index < active_index else "not_started"


def stage_views() -> list[dict[str, str]]:
    """Per-stage view data for the rail and the idle manifest."""

    result = st.session_state.research_result or {}
    feedback = result.get("feedback", "") if result else ""
    critique = critique_state_of(feedback) if result else "absent"
    status: RunStatus = st.session_state.run_status
    active_index: int = st.session_state.stage_index
    events: list[str] = st.session_state.run_events

    views: list[dict[str, str]] = []
    for index, stage in enumerate(STAGES):
        state = stage_state(index, active_index, status, critique)
        detail = ""
        if state in ("running", "failed"):
            state_detail = events[-1] if events else stage.callback
            detail = state_detail if CALLBACK_TO_INDEX.get(state_detail) == index else stage.callback
        views.append(
            {
                "key": stage.key,
                "title": stage.title,
                "produces": stage.produces,
                "icon": stage.icon,
                "state": state,
                "state_label": STATE_LABELS[state],
                "detail": detail,
            }
        )
    return views
