# Validation · Groq-only update · 2026-10-01

- Replaced the search provider with Groq SDK server-side browser search, documented at https://console.groq.com/docs/tool-use/built-in-tools/browser-search.
- Uses `openai/gpt-oss-120b`, `tools=[{"type":"browser_search"}]`, `tool_choice="required"`, and low reasoning effort. No structured-output mode is requested.
- Source extraction uses Groq SDK response models and executed browser/search results. Model-written answer links do not establish successful evidence on their own.
- Removed the second provider's key, settings, dependency and UI controls. One Groq key is used for reasoning and search.
- The scoped CrewAI cache_breakpoint compatibility fix remains in place.
- Offline tests cover completion payload sanitation, agent/task construction, search extraction, rejection of missing evidence, call limits, request tool configuration, errors, navigation, and success/failure states. Network calls and Crew kickoff are mocked.
- Live browser-search access and a complete real run remain unverified because user API credentials were not supplied. Groq quota, permissions, browser-search availability and charges still apply.
- Browser screenshot checks and Streamlit Community Cloud deployment were not completed here. The browser-only deployment guide is included.
