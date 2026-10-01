import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue import Queue, Empty

import streamlit as st

from config import Settings
from diagnostics import safe_error

st.set_page_config(page_title="Research Pop · Your curiosity, in good company", page_icon="✳️", layout="wide")
st.markdown(f"<style>{Path(__file__).with_name('style.css').read_text()}</style>", unsafe_allow_html=True)


def secret(name, default=""):
    try:
        return str(st.secrets.get(name, os.environ.get(name, default)))
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return os.environ.get(name, default)


def render_result(result):
    st.success("Your brief is ready. Follow the sources to explore further.")
    report_tab, evidence_tab = st.tabs(["Your report", "Sources & search evidence"])
    with report_tab:
        st.markdown(result["report"])
        st.download_button("Download report ↓", result["report"], "research-pop-report.md", "text/markdown")
    with evidence_tab:
        st.caption("Web search answers are evidence, not a guarantee that every claim is correct.")
        for index, record in enumerate(result["evidence"]):
            with st.expander(f"{index + 1}. {record['agent']} · {record['query']}"):
                st.markdown(record["answer"])
                for source in record["sources"]:
                    st.link_button(source["title"], source["url"])
                st.caption("Search queries: " + "; ".join(record["queries"]))
        st.download_button("Download evidence ↓", json.dumps(result["evidence"], ensure_ascii=False, indent=2),
                           "research-pop-evidence.json", "application/json")


st.markdown('<div class="brand">✳ RESEARCH POP <span>BIG QUESTIONS. CLEARER ANSWERS.</span></div>', unsafe_allow_html=True)
page = st.radio("Explore Research Pop", ["Research studio", "Meet the team", "Launch guide"], horizontal=True, label_visibility="collapsed")

if page == "Research studio":
    st.markdown('''<div class="hero"><div><span class="eyebrow">YOUR CURIOSITY, IN GOOD COMPANY</span>
    <h1>Go down the rabbit hole.<br><em>Come back with clarity.</em></h1>
    <p>Three AI teammates find evidence, challenge claims, and turn your question into a brief you can actually use.</p></div>
    <div class="orbit" aria-hidden="true"><span>✳</span><b>?</b><i>↗</i></div></div>''', unsafe_allow_html=True)
    left, right = st.columns([2.1, 1], gap="large")
    with right:
        st.markdown('<div class="note"><strong>01 / FIND IT</strong><p>Researcher hunts for credible evidence.</p><strong>02 / QUESTION IT</strong><p>Fact Checker looks for gaps and contradictions.</p><strong>03 / MAKE IT CLICK</strong><p>Report Writer brings it together.</p></div>', unsafe_allow_html=True)
        st.caption("Built for students, creators, and curious professionals. Search and model calls use your API quota.")
    with left:
        with st.container(border=True):
            st.subheader("What are you curious about?")
            with st.form("research"):
                topic = st.text_area("Research question", placeholder="How effective is a four-day workweek for small businesses?", height=120, max_chars=1200)
                c1, c2 = st.columns(2)
                audience = c1.selectbox("Who is this for?", ["General readers", "Students", "Business decision-makers", "Content creators"])
                length = c2.selectbox("Brief size", ["Concise: about 600 words", "Detailed: about 1200 words"])
                with st.expander("API connection"):
                    st.caption("Use deployment secrets, or enter your own key for this session. Your key is sent only to Groq.")
                    if secret("GROQ_API_KEY"):
                        st.success("Deployment key is configured. Leave this field empty to use it.")
                    groq_input = st.text_input("Groq API key", type="password")
                    groq_key = groq_input.strip() or secret("GROQ_API_KEY")
                    st.caption("The app owner can change model names in Streamlit Secrets.")
                submitted = st.form_submit_button("Start researching ↗", type="primary", use_container_width=True)
        if submitted:
            if len(topic.strip()) < 10:
                st.error("Give us a little more to work with: write a question of at least 10 characters.")
            elif not groq_key.strip():
                st.error("Add your Groq API key under API connection, or configure Streamlit Secrets.")
            else:
                st.session_state.pop("result", None)
                settings = Settings(groq_key.strip(),
                                    secret("GROQ_MODEL", "openai/gpt-oss-120b"),
                                    secret("GROQ_SEARCH_MODEL", "openai/gpt-oss-120b"))
                queue = Queue()
                from crew import TEAM, run_research
                finished = []
                active = "Starting your team"
                progress = st.progress(0, text="Getting the team together…")
                with st.status("Starting your team…", expanded=True) as status:
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        future = pool.submit(run_research, topic.strip(), audience, length, settings, queue.put)
                        while not future.done() or not queue.empty():
                            try:
                                event = queue.get(timeout=0.2)
                            except Empty:
                                continue
                            active = event["agent"]
                            if event["kind"] == "active":
                                status.update(label=f"Working now: {active}")
                                st.write(f"✳ {active} is on it.")
                            elif event["kind"] == "done":
                                finished.append(active)
                                progress.progress(len(finished) / 3, text=f"{len(finished)} of 3 agents finished")
                                st.write(f"✓ {active} finished.")
                            elif event["kind"] == "tool":
                                status.update(label=f"Working now: {active} · Groq browser search")
                                st.write(f"↗ {active}: searching for evidence.")
                            elif event["kind"] == "warning":
                                st.warning(event["message"])
                        try:
                            st.session_state.result = future.result()
                            status.update(label="All three teammates finished", state="complete", expanded=False)
                        except Exception as exc:
                            status.update(label=f"Research stopped during {active}", state="error")
                            st.error("We couldn't finish this run. Check your API keys, model availability, billing and rate limits. Try a narrower question, then start again.")
                            with st.expander("Error details — copy this to troubleshoot", expanded=True):
                                st.code(safe_error(exc, (settings.groq_key,)), language=None)
                            st.info("No completed report was saved for this run. Failed runs may still use API quota.")
    if "result" in st.session_state:
        st.divider()
        st.subheader(st.session_state.result["topic"])
        render_result(st.session_state.result)
    elif not submitted:
        st.markdown('<div class="empty"><span>✦</span><h3>A good question starts here.</h3><p>Try: “What does the research say about retrieval practice for university students?”</p></div>', unsafe_allow_html=True)

elif page == "Meet the team":
    st.title("Small team. Different perspectives.")
    st.write("Three focused roles keep the workflow simple and make each handoff visible.")
    for icon, name, description in [
        ("↗", "Researcher", "Uses Groq browser search to collect current evidence, dates, and sources."),
        ("◎", "Fact Checker", "Searches independently for contradictory evidence and flags uncertainty."),
        ("✳", "Report Writer", "Searches to close a gap, then writes a clear brief with references.")]:
        with st.container(border=True):
            st.subheader(f"{icon} {name}")
            st.write(description)
    st.info("Groq powers all agent reasoning. Groq also powers the web research tool. Every agent must successfully obtain web search evidence before its task can finish.")

else:
    st.title("From question to first launch.")
    st.markdown(Path(__file__).with_name("DEPLOY.md").read_text())

st.caption("Research Pop · Stay curious. Check the sources. · Reports stay in this browser session; download the ones you want to keep.")
