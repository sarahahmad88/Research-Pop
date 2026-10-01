# Research Pop

A modular, three-agent research studio for students, creators, and curious professionals. Streamlit hosts the interface; CrewAI orchestrates a sequential Researcher → Fact Checker → Report Writer workflow. Groq powers agent reasoning. A custom Groq tool uses server-side browser search for all three agents. Only one API key is required.

Start with [the browser-only deployment guide](DEPLOY.md). No local installation is required by the user.

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit screens, session state, live agent progress and downloads |
| `agents/researcher.py` | Researcher factory |
| `agents/fact_checker.py` | Fact Checker factory |
| `agents/writer.py` | Report Writer factory |
| `crew.py` | Tasks, handoffs, tool-use guardrails and callbacks |
| `tools.py` | Groq browser-search tool, source metadata, budgets and safe errors |
| `config.py` | Settings and Groq-backed CrewAI LLM |
| `style.css` | Responsive ivory/violet visual system and reduced motion |
| `.streamlit/config.toml` | Streamlit theme |
| `requirements.txt` | Version-pinned direct dependencies |
| `secrets.example.toml` | Placeholder settings; never store actual keys in GitHub |
| `groq_example.py` | Correct standalone Groq SDK example |
| `tests/test_app.py` | Offline behavior and tool boundary tests |

## How tool use works

Every task instructs its agent to call `groq_web_research`. A task guardrail checks for at least one successful web search result for that specific agent. An agent that skips the tool or only encounters failures cannot finish successfully. The tool sends `tools=[{"type": "browser_search"}]` with `tool_choice="required"`. It rejects responses without executed browser/search metadata and source URLs. Search results are evidence, not independent verification of every claim.

Each tool has at most three API attempts; caches are disabled so one agent cannot satisfy another's tool requirement through cached results. CrewAI task context passes the briefs forward. There is no manager agent, database, local web scraper, vector store, or local model. The source panel retains source URLs, annotations and executed-tool evidence from Groq. Generated report citations remain model-written; inspect them against the evidence tab.

Worker threads never call Streamlit. A queue delivers progress to the main UI thread. Reports persist within the current Streamlit browser session and can be exported as Markdown; raw evidence is downloadable as JSON. Failures clear the previous result when a new valid run begins and show a retry state.

## Libraries and API references

Documentation checked on 2026-10-01:

- CrewAI LLM and Groq configuration: https://docs.crewai.com/en/concepts/llms
- CrewAI custom tools: https://docs.crewai.com/en/concepts/tools
- Groq browser-search API: https://console.groq.com/docs/tool-use/built-in-tools/browser-search
- Groq model catalog: https://console.groq.com/docs/models
- Streamlit deployment, Python and Secrets: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

CrewAI uses `groq/openai/gpt-oss-120b` through its LiteLLM integration. The direct Groq SDK uses `openai/gpt-oss-120b` without the provider prefix. The class is `Groq`, not `Grog`. The browser-search model is independently configurable with `GROQ_SEARCH_MODEL` and must support `browser_search`.

## Deployment scope

This is a deployable starter with a complete basic research journey. It does not include accounts, durable history, PDF export, public-service abuse controls, or a hard global spend cap. Avoid confidential research questions: prompts and evidence go to Groq. Keep the app private when using owner keys. Hosting capacity and provider quotas determine practical concurrency.

See `VALIDATION.md` for exactly what was tested and any remaining limits.
