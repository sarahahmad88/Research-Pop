### 1. Get your Groq API key

Create a Groq account at https://console.groq.com and create an API key. Confirm your account can use `openai/gpt-oss-120b` and its built-in `browser_search` tool. Keep the key private. Browser search runs on Groq servers and may incur charges.

### 2. Download and unzip this project

Download `research-pop.zip` and extract it using your computer's built-in unzip feature. Open the extracted `research-pop` folder. You do not need Python, a terminal, or a code editor.

### 3. Create a GitHub repository

Sign in at https://github.com. Click **+ → New repository**. Name it `research-pop`, select **Private**, tick **Add a README file**, and click **Create repository**.

### 4. Upload through GitHub's website

Click **Add file → Upload files**. Drag the contents of the extracted `research-pop` folder into the upload area, preserving the `agents` and `tests` folders. Upload the contents, not the enclosing folder and not the ZIP. Commit the upload to `main`.

At the repository root, check that `app.py`, `requirements.txt`, `crew.py`, `tools.py`, `config.py`, `style.css`, `DEPLOY.md`, and `README.md` appear. The three agent files belong in `agents/`.

Some file pickers hide folders beginning with a dot. If `.streamlit/config.toml` did not upload, click **Add file → Create new file**, type `.streamlit/config.toml` as the filename, and copy its content from the supplied file. Commit it. Do the same for `.gitignore` if necessary. The app works without the theme file, but it supplies the intended colors. Never create or upload a file containing real API keys.

### 5. Connect Streamlit

Open https://share.streamlit.io and sign in with GitHub. Authorize access to this repository. Click **Create app**, choose **Yup, I have an app** if prompted, and select:

- Repository: `your-username/research-pop`
- Branch: `main`
- Main file path: `app.py`

### 6. Add secrets and choose Python

Open **Advanced settings**, select **Python 3.12**, and paste this into **Secrets**, replacing the API-key placeholder:

```toml
GROQ_API_KEY = "your-real-groq-key"
GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_SEARCH_MODEL = "openai/gpt-oss-120b"
```

Click **Save**, then **Deploy**. Streamlit installs the cloud-side Python packages from `requirements.txt`. CrewAI has several dependencies, so allow extra time on the first deployment. No tools are installed on your computer.

### 7. Run your first question

Ask: **What does the research say about retrieval practice for university students?** Select **Students** and the concise brief, then click **Start researching**. Watch the active agent change from Researcher to Fact Checker to Report Writer. Check **Sources & search evidence** and download your report.

### 8. Fix common first-launch problems

- **Missing keys:** Open the app's settings and update Secrets; confirm the names match exactly.
- **401 or 403 / access:** Check your Groq key, model permissions, and browser-search access. Browser search is unavailable on regional/sovereign endpoints.
- **429 / quota:** Wait and try again, or adjust the provider's billing and rate limits. Browser search and inference may incur charges. A run allows up to three browser-search requests per agent, nine total, with additional Groq reasoning calls.
- **Model not found:** Check the official provider model catalogs and update `GROQ_MODEL` or `GROQ_SEARCH_MODEL` in Secrets. Use `openai/gpt-oss-120b` or `openai/gpt-oss-20b` for `GROQ_SEARCH_MODEL`.
- **No search evidence:** Try a focused factual question. The app intentionally stops rather than producing a report without successful searches.
- **Installation error:** Check **Manage app → logs**. Use Python 3.12 and the exact supplied requirements; do not upload the ZIP as your code.
- **App sleeps or restarts:** Reopen it. Session reports are temporary; download reports before closing the browser. Do not rerun repeatedly while a request is working.

### 9. Update the app later

Edit a file using GitHub's pencil button and commit the change. Streamlit redeploys the repository. API keys belong only in Streamlit Secrets or the session's password fields.

### 10. Share with care

Keep your initial app access private. When server keys are configured, viewers use the owner's API quota. For an open demo, remove server API keys and have viewers enter their own session keys. This starter has no per-user billing, durable history, or global concurrency limiter. Add those before launching a large public service.
