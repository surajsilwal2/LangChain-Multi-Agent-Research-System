import streamlit as st


st.set_page_config(
	page_title="Research Desk",
	page_icon="📘",
	layout="wide",
	initial_sidebar_state="expanded",
)

st.markdown(
	"""
	<style>
	@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

	:root {
		--bg: #f4f7f5;
		--panel: rgba(255,255,255,0.8);
		--panel-solid: #ffffff;
		--ink: #111827;
		--muted: #5d6978;
		--line: rgba(15, 23, 42, 0.08);
		--primary: #0f766e;
		--primary-strong: #115e59;
		--primary-soft: #dff7f3;
		--accent: #f59e0b;
		--accent-soft: #fff1cf;
		--shadow: 0 18px 38px rgba(15, 23, 42, 0.08);
	}

	html, body, [class*="css"] {
		font-family: 'Inter', sans-serif;
		color: var(--ink);
	}

	.stApp {
		background:
			radial-gradient(circle at top right, rgba(15, 118, 110, 0.15), transparent 30%),
			radial-gradient(circle at bottom left, rgba(245, 158, 11, 0.12), transparent 32%),
			var(--bg);
	}

	[data-testid="stSidebar"] {
		background: linear-gradient(180deg, #edf9f6 0%, #f9fbfb 100%);
		border-right: 1px solid var(--line);
	}

	[data-testid="stSidebar"] > div:first-child { padding-top: 1.2rem; }

	.main .block-container {
		padding-top: 2rem;
		padding-bottom: 3rem;
	}

	.brand-mark {
		color: var(--primary-strong);
		font: 600 11px 'JetBrains Mono', monospace;
		letter-spacing: 0.12em;
		text-transform: uppercase;
	}

	.hero {
		background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(223,247,243,0.9));
		border: 1px solid var(--line);
		border-radius: 22px;
		padding: 1.5rem 1.5rem 1.2rem;
		box-shadow: var(--shadow);
		margin-bottom: 1.2rem;
	}

	.page-kicker {
		margin: 0 0 .55rem;
		color: var(--primary);
		font: 700 11px 'JetBrains Mono', monospace;
		letter-spacing: 0.14em;
		text-transform: uppercase;
	}

	.page-title {
		margin: 0;
		font-size: clamp(2.2rem, 3vw, 4rem);
		line-height: 1.03;
		font-weight: 800;
		letter-spacing: -0.06em;
		color: var(--ink);
	}

	.page-subtitle {
		margin: .8rem 0 1.25rem;
		font-size: 1.05rem;
		color: var(--muted);
		max-width: 760px;
	}

	.metric-card {
		background: var(--panel-solid);
		border: 1px solid var(--line);
		border-radius: 16px;
		padding: 1rem 1.1rem;
		box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
	}

	.metric-label {
		font-size: .72rem;
		letter-spacing: 0.12em;
		color: var(--muted);
		text-transform: uppercase;
		font-weight: 700;
	}

	.metric-value {
		font-size: 1.65rem;
		font-weight: 800;
		margin-top: .35rem;
		color: var(--ink);
	}

	.metric-chip {
		display: inline-block;
		padding: .3rem .65rem;
		border-radius: 999px;
		background: var(--primary-soft);
		color: var(--primary-strong);
		font-size: .72rem;
		font-weight: 700;
	}

	.section-label {
		color: var(--primary);
		font: 700 11px 'JetBrains Mono', monospace;
		letter-spacing: 0.12em;
		text-transform: uppercase;
	}

	.panel-card {
		background: rgba(255,255,255,0.7);
		border: 1px solid var(--line);
		border-radius: 18px;
		padding: 1.1rem 1.2rem;
		box-shadow: 0 8px 25px rgba(15, 23, 42, 0.03);
	}

	div.stButton > button[kind="primary"] {
		background: linear-gradient(135deg, var(--primary) 0%, var(--primary-strong) 100%);
		border: none;
		border-radius: 12px;
		color: white;
		font-weight: 700;
		min-height: 2.9rem;
		box-shadow: 0 8px 22px rgba(15, 118, 110, 0.25);
	}

	div.stButton > button[kind="primary"]:hover {
		background: linear-gradient(135deg, var(--primary-strong) 0%, var(--primary) 100%);
		filter: brightness(1.02);
	}

	div[data-testid="stTabs"] button {
		font-weight: 700;
	}

	div[data-testid="stTabs"] button[aria-selected="true"] {
		color: var(--primary-strong);
		border-bottom-color: var(--primary);
	}

	div[data-testid="stAlert"] {
		border-radius: 14px;
		border: 1px solid rgba(15, 118, 110, 0.12);
	}

	.empty-state {
		margin-top: 1.5rem;
		padding: 1.5rem;
		border: 1px dashed rgba(15, 118, 110, 0.28);
		border-radius: 20px;
		background: rgba(255,255,255,0.5);
		color: var(--muted);
	}

	.stTextInput input, .stTextArea textarea {
		border-radius: 12px;
		border: 1px solid rgba(15, 23, 42, 0.12);
		padding: 0.8rem 0.9rem;
	}
	</style>
	""",
	unsafe_allow_html=True,
)


with st.sidebar:
	st.markdown('<div class="brand-mark">Fieldnotes / Research system</div>', unsafe_allow_html=True)
	st.divider()
	st.markdown("### New research run")
	topic = st.text_area(
		"Research topic",
		placeholder="For example: How heat affects urban public health",
		height=120,
		help="Enter a focused question or topic for the research agents.",
	)
	run_clicked = st.button("Run research", type="primary", use_container_width=True)
	st.caption("Search, extract source text, draft the brief, and review the final critique.")


st.markdown(
	"""
	<div class="hero">
		<div class="page-kicker">Multi-agent research</div>
		<h1 class="page-title">Research desk</h1>
		<p class="page-subtitle">A source-led research workflow built to turn a question into a polished brief and a sharper critique.</p>
	</div>
	""",
	unsafe_allow_html=True,
)

metrics = st.columns(4)
with metrics[0]:
	st.markdown('<div class="metric-card"><div class="metric-label">Pipeline</div><div class="metric-value">4</div><div class="metric-chip">Stages</div></div>', unsafe_allow_html=True)
with metrics[1]:
	st.markdown('<div class="metric-card"><div class="metric-label">Sources</div><div class="metric-value">5</div><div class="metric-chip">Top picks</div></div>', unsafe_allow_html=True)
with metrics[2]:
	st.markdown('<div class="metric-card"><div class="metric-label">Report</div><div class="metric-value">AI</div><div class="metric-chip">Drafted</div></div>', unsafe_allow_html=True)
with metrics[3]:
	st.markdown('<div class="metric-card"><div class="metric-label">Review</div><div class="metric-value">Live</div><div class="metric-chip">Critique</div></div>', unsafe_allow_html=True)


if run_clicked:
	if not topic.strip():
		st.warning("Enter a research topic to start a run.")
	else:
		st.session_state.pop("research_result", None)
		try:
			from src.pipelines.pipelines import run_research_pipeline

			with st.status("Starting research", expanded=True) as progress:
				def update_progress(label: str) -> None:
					progress.update(label=label, state="running", expanded=True)
					progress.write(label)

				result = run_research_pipeline(topic.strip(), progress_callback=update_progress)
				progress.update(label="Research run complete", state="complete", expanded=False)
			st.session_state.research_result = result
			st.session_state.research_topic = topic.strip()
		except Exception as error:
			st.error("The research run could not be completed.")
			with st.expander("Error details"):
				st.code(f"{type(error).__name__}: {error}")


result = st.session_state.get("research_result")
if result:
	st.markdown(f'<div class="section-label">Research brief / {st.session_state.research_topic}</div>', unsafe_allow_html=True)
	report = result.get("report", "No report was returned.")
	st.download_button(
		"Download report as Markdown",
		data=f"# {st.session_state.research_topic}\n\n{report}",
		file_name="research-report.md",
		mime="text/markdown",
	)

	report_tab, review_tab, sources_tab = st.tabs(["Report", "Critique", "Sources"])
	with report_tab:
		st.markdown(f"<div class='panel-card'>{report}</div>", unsafe_allow_html=True)
	with review_tab:
		st.markdown(f"<div class='panel-card'>{result.get('feedback', 'No critique was returned.')}</div>", unsafe_allow_html=True)
	with sources_tab:
		search_column, scrape_column = st.columns(2, gap="large")
		with search_column:
			st.markdown("#### Search results")
			st.markdown(f"<div class='panel-card'>{result.get('search_results', 'No search results were returned.')}</div>", unsafe_allow_html=True)
		with scrape_column:
			st.markdown("#### Extracted source text")
			st.markdown(f"<div class='panel-card'>{result.get('scrape_content', 'No source text was returned.')}</div>", unsafe_allow_html=True)
else:
	st.markdown(
		'<div class="empty-state"><span class="section-label">Workspace ready</span><br><br>'
		'Enter a topic in the left panel to generate a researched report and critique.'
		'</div>',
		unsafe_allow_html=True,
	)


if run_clicked:
	if not topic.strip():
		st.warning("Enter a research topic to start a run.")
	else:
		st.session_state.pop("research_result", None)
		try:
			from src.pipelines.pipelines import run_research_pipeline

			with st.status("Starting research", expanded=True) as progress:
				def update_progress(label: str) -> None:
					progress.update(label=label, state="running", expanded=True)
					progress.write(label)

				result = run_research_pipeline(topic.strip(), progress_callback=update_progress)
				progress.update(label="Research run complete", state="complete", expanded=False)
			st.session_state.research_result = result
			st.session_state.research_topic = topic.strip()
		except Exception as error:
			st.error("The research run could not be completed.")
			with st.expander("Error details"):
				st.code(f"{type(error).__name__}: {error}")


result = st.session_state.get("research_result")
if result:
	st.markdown(f'<div class="section-label">Research brief / {st.session_state.research_topic}</div>', unsafe_allow_html=True)
	report = result.get("report", "No report was returned.")
	st.download_button(
		"Download report as Markdown",
		data=f"# {st.session_state.research_topic}\n\n{report}",
		file_name="research-report.md",
		mime="text/markdown",
	)

	report_tab, review_tab, sources_tab = st.tabs(["Report", "Critique", "Sources"])
	with report_tab:
		st.markdown(report)
	with review_tab:
		st.markdown(result.get("feedback", "No critique was returned."))
	with sources_tab:
		search_column, scrape_column = st.columns(2, gap="large")
		with search_column:
			st.markdown("#### Search results")
			st.markdown(result.get("search_results", "No search results were returned."))
		with scrape_column:
			st.markdown("#### Extracted source text")
			st.markdown(result.get("scrape_content", "No source text was returned."))
else:
	st.markdown(
		'<div class="empty-state"><span class="section-label">Workspace ready</span><br><br>'
		'Enter a topic in the left panel to generate a researched report and critique.'
		'</div>',
		unsafe_allow_html=True,
	)
