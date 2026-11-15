import os
import re
from urllib.parse import urlsplit

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Research Studio",
    page_icon="R",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse at 12% 0%, rgba(80, 72, 180, .20), transparent 36%),
            radial-gradient(ellipse at 92% 10%, rgba(31, 154, 151, .12), transparent 30%),
            #0b1020;
        color: #eef2ff;
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMainBlockContainer"] {
        max-width: 1180px;
        padding-top: 2.2rem;
        padding-bottom: 4rem;
    }
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, .94);
        border-right: 1px solid rgba(148, 163, 184, .14);
    }
    .brand {
        color: #a5b4fc;
        font-size: .78rem;
        font-weight: 700;
        letter-spacing: .18em;
        text-transform: uppercase;
        margin-bottom: .8rem;
    }
    .hero-title {
        color: #f8fafc;
        font-size: clamp(2.4rem, 5vw, 4.2rem);
        font-weight: 750;
        letter-spacing: -.055em;
        line-height: 1.03;
        margin: .2rem 0 1rem;
    }
    .hero-title span {
        background: linear-gradient(90deg, #a5b4fc, #5eead4);
        background-clip: text;
        -webkit-background-clip: text;
        color: transparent;
    }
    .hero-copy {
        color: #aab6cb;
        font-size: 1.08rem;
        line-height: 1.7;
        max-width: 680px;
    }
    .workflow-card {
        background: linear-gradient(145deg, rgba(30, 41, 69, .88), rgba(15, 23, 42, .72));
        border: 1px solid rgba(148, 163, 184, .18);
        border-radius: 18px;
        padding: 1.25rem 1.4rem;
        margin-top: .6rem;
    }
    .workflow-title {
        color: #e2e8f0;
        font-size: .82rem;
        font-weight: 700;
        letter-spacing: .12em;
        margin-bottom: .8rem;
        text-transform: uppercase;
    }
    .workflow-step {
        color: #cbd5e1;
        font-size: .94rem;
        padding: .45rem 0;
    }
    .workflow-step b { color: #5eead4; margin-right: .55rem; }
    div[data-testid="stForm"] {
        background: rgba(15, 23, 42, .78);
        border: 1px solid rgba(148, 163, 184, .2);
        border-radius: 18px;
        padding: 1.2rem 1.3rem .6rem;
    }
    div[data-testid="stTextInput"] input {
        background: #111a2e;
        border-color: rgba(148, 163, 184, .25);
        border-radius: 10px;
        color: #f8fafc;
        min-height: 3rem;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #818cf8;
        box-shadow: 0 0 0 1px #818cf8;
    }
    div[data-testid="stButton"] button[kind="primary"],
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(100deg, #6366f1, #0f9f9a);
        border: 0;
        border-radius: 10px;
        color: white;
        font-weight: 700;
        min-height: 3rem;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover,
    div[data-testid="stFormSubmitButton"] button:hover {
        border: 0;
        filter: brightness(1.12);
    }
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, .58);
        border: 1px solid rgba(148, 163, 184, .16);
        border-radius: 14px;
        padding: .9rem 1rem;
    }
    .muted { color: #94a3b8; font-size: .9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## Research Studio")
    st.caption("A compact multi-agent research workflow")
    st.divider()
    st.markdown("### How it works")
    st.markdown(
        "1. **Search** finds useful web sources.\n"
        "2. **Reader** extracts key facts.\n"
        "3. **Writer** creates a concise report.\n"
        "4. **Critic** reviews the result."
    )
    st.divider()
    st.caption("Powered by Groq, LangChain, and Tavily")

st.markdown('<div class="brand">Multi-agent research workspace</div>', unsafe_allow_html=True)
hero, workflow = st.columns([1.65, 1], gap="large", vertical_alignment="center")

with hero:
    st.markdown(
        '<div class="hero-title">A question in.<br><span>A sourced brief out.</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-copy">Turn a research question into a clear, concise report. '
        "Specialized agents search the web, read a relevant source, write the brief, "
        "and review the result.</div>",
        unsafe_allow_html=True,
    )

with workflow:
    st.markdown(
        """
        <div class="workflow-card">
          <div class="workflow-title">Your research team</div>
          <div class="workflow-step"><b>01</b> Scout reliable sources</div>
          <div class="workflow-step"><b>02</b> Extract useful evidence</div>
          <div class="workflow-step"><b>03</b> Draft a focused report</div>
          <div class="workflow-step"><b>04</b> Review quality and clarity</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
with st.form("research_form"):
    topic = st.text_input(
        "What would you like to research?",
        key="research_topic",
        placeholder="For example: How is AI changing data analysis work?",
    )
    submitted = st.form_submit_button(
        "Generate research brief",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if not topic.strip():
        st.warning("Enter a research question to get started.")
    else:
        missing_keys = [
            key for key in ("GROQ_API_KEY", "TAVILY_API_KEY") if not os.getenv(key)
        ]
        if missing_keys:
            st.error(
                "Add GROQ_API_KEY and TAVILY_API_KEY to your .env file, then restart the app."
            )
        else:
            from pipeline import run_research_pipeline

            with st.status("Preparing your research...", expanded=True) as status:
                def update_status(message: str) -> None:
                    status.update(label=message, state="running", expanded=True)

                result = run_research_pipeline(topic.strip(), on_progress=update_status)
                status.update(
                    label="Research brief complete",
                    state="complete",
                    expanded=False,
                )
            st.session_state["research_result"] = result
            st.session_state["completed_topic"] = topic.strip()

result = st.session_state.get("research_result")
if result:
    st.write("")
    st.divider()
    st.markdown("## Your research brief")
    st.caption(f"Topic: {st.session_state.get('completed_topic', '')}")

    report = result.get("report", "")
    search_results = result.get("search_results", "")
    scraped_content = result.get("scraped_content", "")
    feedback = result.get("feedback", "")
    sources = list(dict.fromkeys(re.findall(r"https?://[^\s<>)}\]]+", search_results)))
    word_count = len(report.split())

    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("Research stages", "4 agents")
    metric_b.metric("Sources found", len(sources))
    metric_c.metric("Report length", f"{word_count} words")

    report_tab, research_tab, review_tab = st.tabs(
        ["Final report", "Research notes", "Critic review"]
    )
    with report_tab:
        report_col, download_col = st.columns([5, 1.4], vertical_alignment="center")
        with report_col:
            st.markdown("### Research report")
        with download_col:
            safe_topic = re.sub(r"[^a-z0-9]+", "-", st.session_state.get("completed_topic", "").lower()).strip("-")
            st.download_button(
                "Download .md",
                data=report,
                file_name=f"{safe_topic or 'research-report'}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        st.markdown(report)
        if sources:
            st.markdown("#### Sources")
            source_columns = st.columns(min(len(sources), 3))
            for index, source in enumerate(sources[:6]):
                source = source.rstrip(".,;")
                domain = urlsplit(source).netloc or source
                with source_columns[index % len(source_columns)]:
                    st.link_button(
                        domain,
                        source,
                        use_container_width=True,
                    )

    with research_tab:
        st.markdown("### Web search")
        st.markdown(search_results or "No search summary was returned.")
        with st.expander("Detailed source notes"):
            st.markdown(scraped_content or "No detailed source notes were returned.")

    with review_tab:
        st.markdown("### Critic review")
        st.markdown(feedback or "No review was returned.")

    st.caption("Review source links and claims before using this report.")
