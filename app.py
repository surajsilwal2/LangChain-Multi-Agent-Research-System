"""Research Desk - Streamlit entry point.

The UI shell lives in ``src/ui``: theme injection, run state and HTML builders.
This file only wires the sidebar run console to the pipeline and renders the
results workspace.
"""

from __future__ import annotations

import streamlit as st
import groq

from src.ui.components import (
    extract_links,
    render_app_bar,
    render_brand,
    render_document_header,
    render_idle_workspace,
    render_run_details,
    render_source_links,
    render_stage_rail,
    strip_leading_heading,
)
from src.ui.run_state import (
    begin_run,
    critique_state_of,
    fail_run,
    finish_run,
    format_score,
    init_state,
    parse_score,
    record_event,
    report_filename,
    stage_views,
)
from src.ui.theme import inject_styles

st.set_page_config(
    page_title="Research Desk",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()
init_state()


# --------------------------------------------------------------------------- #
# Sidebar: run console
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown(render_brand(), unsafe_allow_html=True)

    with st.container(key="composer"):
        topic = st.text_area(
            "Research topic",
            placeholder="How heat affects urban public health",
            height=104,
            help="Web search, source reading, report writing and critique run in sequence.",
        )
        run_clicked = st.button("Run research", type="primary", use_container_width=True)

    rail_slot = st.empty()
    rail_slot.markdown(render_stage_rail(stage_views()), unsafe_allow_html=True)

    if st.session_state.run_events:
        with st.container(key="runlog"):
            with st.expander("Run details", expanded=False):
                st.markdown(
                    render_run_details(st.session_state.run_events),
                    unsafe_allow_html=True,
                )


# --------------------------------------------------------------------------- #
# Run
# --------------------------------------------------------------------------- #
if run_clicked:
    submitted_topic = topic.strip()
    if not submitted_topic:
        st.session_state.empty_topic_warning = True
    else:
        begin_run(submitted_topic)
        rail_slot.markdown(render_stage_rail(stage_views()), unsafe_allow_html=True)

        with st.sidebar:
            with st.container(key="runlog-live"):
                with st.status("Starting research", expanded=False) as status:

                    def update_progress(label: str) -> None:
                        record_event(label)
                        status.update(label=label, state="running")
                        rail_slot.markdown(render_stage_rail(stage_views()), unsafe_allow_html=True)

                    try:
                        from src.pipelines.pipelines import run_research_pipeline

                        result = run_research_pipeline(
                            submitted_topic,
                            progress_callback=update_progress,
                        )
                    except Exception as error:  # surfaced in the workspace, not swallowed
                        failed_stage = (
                            st.session_state.run_events[-1]
                            if st.session_state.run_events
                            else "pipeline startup"
                        )
                        if isinstance(error, groq.RateLimitError):
                            summary = (
                                f"Groq's rate limit was reached during {failed_stage}. "
                                "Wait for the limit to reset, then run the research again."
                            )
                        elif isinstance(error, groq.APIConnectionError):
                            summary = (
                                f"Could not connect to Groq during {failed_stage} after retries. "
                                "Check your internet connection and Groq API availability, then try again."
                            )
                        else:
                            summary = (
                                f"Research failed during {failed_stage} "
                                f"({type(error).__name__}). Expand Error details for the technical message."
                            )
                        fail_run(f"{type(error).__name__}: {error}", summary)
                        status.update(label="Research run failed", state="error", expanded=False)
                    else:
                        finish_run(result)
                        status.update(label="Research run complete", state="complete", expanded=False)

        rail_slot.markdown(render_stage_rail(stage_views()), unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# Workspace
# --------------------------------------------------------------------------- #
st.markdown(render_app_bar(st.session_state.run_status), unsafe_allow_html=True)

if st.session_state.pop("empty_topic_warning", False):
    st.warning("Enter a research topic to start a run.")

if st.session_state.run_error:
    st.error(st.session_state.run_error_summary or "The research run could not be completed.")
    with st.expander("Error details", expanded=False):
        st.code(st.session_state.run_error, language="text")

result = st.session_state.research_result
submitted_topic = st.session_state.research_topic

with st.container(key="workspace"):
    if not result:
        st.markdown(render_idle_workspace(stage_views()), unsafe_allow_html=True)
    else:
        feedback = result.get("feedback") or ""
        critique_state = critique_state_of(feedback)
        report = result.get("report") or ""

        heading_column, action_column = st.columns([0.72, 0.28], vertical_alignment="bottom")
        with heading_column:
            st.markdown(
                render_document_header(
                    submitted_topic,
                    format_score(parse_score(feedback)),
                    critique_state,
                ),
                unsafe_allow_html=True,
            )
        with action_column:
            with st.container(key="doc-actions"):
                st.download_button(
                    "Download .md",
                    data=f"# {submitted_topic}\n\n{report}",
                    file_name=report_filename(submitted_topic),
                    mime="text/markdown",
                    icon=":material/download:",
                    key="download_report_md",
                )

        report_tab, critique_tab, sources_tab = st.tabs(["Report", "Critique", "Sources"])

        with report_tab:
            with st.container(key="doc-body"):
                st.markdown(strip_leading_heading(report) or "No report was returned.")

        with critique_tab:
            with st.container(key="critique-body"):
                st.markdown(feedback or "No critique was returned.")

        with sources_tab:
            search_text = result.get("search_results") or ""
            scrape_text = result.get("scrape_content") or ""
            links = extract_links(search_text)

            with st.container(key="sources"):
                if links:
                    st.markdown(render_source_links(links), unsafe_allow_html=True)
                with st.expander("Search results", expanded=True):
                    st.code(search_text or "No search results were returned.", language="markdown")
                with st.expander("Extracted source text", expanded=False):
                    st.code(scrape_text or "No source text was returned.", language="markdown")
