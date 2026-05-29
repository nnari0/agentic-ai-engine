# Agentic AI Engineering

This guide walks you through setting up a GCP account, the Google Cloud CLI, and the agentic AI application that we will extend throughout the lecture. Follow all steps in order. By the end you will have the application running locally — a greeting agent will be ready to answer your questions and help you prepare for the upcoming sessions.

## 1. Prerequisites

Install
- [Python 3.14](https://www.python.org/downloads/)
  - **Windows:** check "Add Python to PATH" during installation, or set manually:
    - `PATH` — add `C:\Users\<YOU>\AppData\Local\Programs\Python\Python314\` and `...\Scripts\`
    - `PYTHONPATH` — (optional) path to your project root so imports resolve correctly
  - **macOS / Linux:** Python is typically available on `PATH` automatically after install
- Create a [Google Cloud Platform](https://console.cloud.google.com) account if you don't already have one
- Install [Google Cloud CLI](https://docs.cloud.google.com/sdk/docs/install-sdk) following the instructions in the link.
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and make sure the Docker daemon is running before building or deploying container images
- Create a [Hugging Face](https://huggingface.co/join) account if you don't already have one

## 2.1. Create a GCP project

1. Go to [Google Cloud Console — New Project](https://console.cloud.google.com/projectcreate)
2. Enter a **Project name** (e.g. `agentic-ai-engineering`)
3. Select a **Billing account** (required for Vertex AI and Cloud Run)
4. Click **Create** and wait for the project to be provisioned
5. Note your **Project ID** (shown below the project name) — you will need it in later steps

> **Tip:** The project ID is immutable and globally unique. It may differ from the project name.

## 2.2 Set a GCP billing limit

1. Open the [Google Cloud Console - Billing](https://console.cloud.google.com/billing)
2. Select the **billing account** linked to your project
3. In the left menu, click **Budgets & Alerts**
4. Click **Create Budget**
5. Choose:
   - **Scope:** Billing account or project
   - **Budget amount:** e.g. $50/month
6. Set **alert thresholds:** 50%, 90%, 100%

This will notify you by email when spending reaches each threshold.


## 2.3 Google Login & Authentication

Initialize gcloud and log in:

```bash
gcloud init
```

List authenticated accounts:

```bash
gcloud auth list
```

If necessary, switch to the correct account:

```bash
gcloud config set account <YOUR_ACCOUNT_EMAIL>
```

Verify the active project:

```bash
gcloud config get-value project
```

Set the active project, if necessary:

```bash
gcloud config set project <PROJECT_ID>
```

Log in and create Application Default Credentials (ADC):

```bash
gcloud auth application-default login
```

Set the ADC quota project, if a corresponding error message appears:

```bash
gcloud auth application-default set-quota-project <PROJECT_ID>
```

> **Note:** The ADC credentials file is saved at:
> - **Windows:** `%APPDATA%\gcloud\application_default_credentials.json`
> - **macOS / Linux:** `~/.config/gcloud/application_default_credentials.json`
>
> Add this path to your `.env` as `GOOGLE_APPLICATION_CREDENTIALS`.

More help: [gcloud CLI cheat sheet](https://docs.cloud.google.com/sdk/docs/cheatsheet)

### Create a Cloud Storage bucket

Create a bucket to store agent artifacts:

```bash
gcloud storage buckets create gs://<BUCKET_NAME> \
  --project=<PROJECT_ID> \
  --location=europe-north1 \
  --uniform-bucket-level-access
```

Replace `<BUCKET_NAME>` with a globally unique name (e.g. `agentic-ai-eng-<PROJECT_ID>`), then set it in `.env`:

```env
GOOGLE_CLOUD_STORAGE_BUCKET=<BUCKET_NAME>
```

> **Note:** Bucket names are globally unique across all GCP projects. A common convention is to include your project ID in the name to avoid conflicts.

## Enable Vertex AI API

Enable the [Vertex AI API](https://console.cloud.google.com/apis/enableflow?apiid=aiplatform.googleapis.com) by following the instruction in the link.


## 3. IDE Setup — VS Code (Recommended)

Install [Visual Studio Code](https://code.visualstudio.com/) and open the project folder.

### Create the virtual environment and select the interpreter

VS Code can create the `.venv` and register the Python interpreter in one step — no terminal required:

1. Open the Command Palette: `Ctrl+Shift+P`
2. Type **Python: Create Environment** and press Enter
3. Select **Venv**
4. Select **Python 3.14.x** as the base interpreter
5. When asked which dependencies to install, tick **`pyproject.toml`** — VS Code will install all packages automatically

VS Code sets the new environment as the active interpreter immediately. You will see **('.venv': venv)** in the status bar at the bottom-left. New terminals opened inside VS Code will have the environment activated automatically.

> **Tip:** If you already created the `.venv` via the terminal, use **Python: Select Interpreter** instead and choose the **('.venv': venv)** entry.

Activate the virtual environment:

**Windows (PowerShell):**
```powershell
& .\.venv\Scripts\Activate.ps1
```

**macOS / Linux (bash / zsh):**
```bash
source .venv/bin/activate
```

## 4. Project Setup

Install [uv](https://docs.astral.sh/uv/):

```bash
pip install uv
```

Install dependencies and set up the project:

```bash
uv lock
uv sync
uv pip install -e .
```

## 5. Configure `.env`

Copy the example and fill in your values:

```bash
cp .env.example .env
```

Required variables:

| Variable | Description |
|---|---|
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to your ADC credentials file |
| `GOOGLE_CLOUD_PROJECT` | Your GCP project ID |
| `GOOGLE_CLOUD_STORAGE_BUCKET` | Your Cloud Storage bucket name |

Optional variables:

| Variable | Default | Description |
|---|---|---|
| `DEFAULT_LLM_MODEL` | `gemini-2.5-flash` | Gemini model used by all agents |
| `MCP_FETCH_URL` | _(empty)_ | SSE endpoint of the MCP Web Fetch server — set to `http://localhost:8002/sse` to enable web-page summarization |

## 6. Run the Application locally

```bash
uvicorn agentic_ai_main:app --reload --port 8000
```

The application will be available at **http://localhost:8000**. The chat interface is served at the root path `/`.

Your Welcome agent is waiting for you.
You can also ask it how to prepare for the lecture :-)

---

## 7. Available Agents

### 👋 Welcome Agent (`greeting_agent`)

The default agent. It greets students, points to the README for setup help, and recommends preparation resources for the lecture.

### 📝 Summarizer Agent (`summarizer_agent`)

Summarizes text documents and web pages. Switch to it by clicking **Summarizer Agent** in the sidebar.

**Capabilities:**

| Input | How |
|---|---|
| Text file (`.txt`, `.md`, `.csv`, …) | Click the **paperclip** button that appears in the input bar |
| PDF or image | Same paperclip button — Gemini reads them natively |
| Web page | Paste a URL into the chat (requires the MCP Fetch server — see §8) |
| Pasted text | Type or paste directly into the chat |

For every document the agent returns:

1. **Title / Topic** — what the document is about
2. **Key Points** — the most important facts (bullet list)
3. **Summary** — a concise paragraph
4. **Takeaway** — the single most important insight

After producing a summary the agent also:
- Calls the A2A Critic and appends a **## Critique** section (see §9)
- Saves the full summary as a `.md` artifact to GCS — visible in the **Artifacts** panel (see §11)
- Searches the RAG corpus for related context before answering knowledge questions (see §12)
- Stores the conversation in the Memory Bank for recall across sessions (see §10)

You can also ask follow-up questions about the document (e.g. *"Who is the author?"*, *"What is the main argument?"*). If the MCP Fetch server is running, the agent can additionally fetch URLs you share in the chat.

### 🔬 Research Orchestrator (`research_orchestrator`)

A multi-agent pipeline that researches a topic by fetching live web sources and compiling the findings into a structured report. Switch to it by clicking **Research Orchestrator** in the sidebar.

**How it works:**

```
research_orchestrator  (orchestrator)
 ├── researcher_agent  → checks RAG corpus, then fetches web pages via MCP
 └── writer_agent      → compiles findings into a Markdown report + saves artifact
```

**Example prompt:**

> *"Research the impact of large language models on software engineering"*

The orchestrator will:
1. Identify 2–4 authoritative URLs
2. Delegate each fetch to `researcher_agent` (which checks the RAG corpus first)
3. Pass all findings to `writer_agent`
4. Return a fully sourced Markdown report, automatically saved as a `.md` artifact

After the run, open the **Artifacts** panel to download the report (see §11). Add background documents to the **RAG Docs** panel to enrich future research runs (see §12).

> **Note:** Web fetching requires the MCP Fetch server (see §8). Without it the orchestrator falls back to the model's training knowledge.

---

## 8. MCP Web Fetch Server

The MCP Fetch server is a standalone microservice that exposes a `fetch_page` tool over the [Model Context Protocol](https://modelcontextprotocol.io/). The Summarizer agent connects to it to download and clean web pages before summarizing them.

### Run with Docker (recommended)

```bash
# Build the image
docker build -t mcp-fetch ./mcp_servers/fetch

# Run on port 8002
docker run -p 8002:8002 mcp-fetch
```

### Run locally (without Docker)

```bash
# Install dependencies (already included via uv sync)
pip install "mcp[cli]>=1.0.0" httpx "beautifulsoup4>=4.12.0" "lxml>=5.0.0"

# Start the server
python mcp_servers/fetch/server.py
```

The server listens on `http://0.0.0.0:8002` and exposes the SSE endpoint at `/sse`.

### Connect agents to the server

Add the following line to your `.env` and restart the main application:

```env
MCP_FETCH_URL=http://localhost:8002/sse
```

Both the **Summarizer** and the **Research Orchestrator** will then have access to `fetch_page`. Example prompts:

> *"Please summarize https://example.com/article"*  (Summarizer agent)

> *"Research recent advances in quantum error correction"*  (Research Orchestrator)

> **Note:** The main application starts without the MCP server. The `fetch_page` tool is only available when `MCP_FETCH_URL` is configured and the server is reachable.

---

## 9. A2A Critic Agent

The Critic agent is a standalone service that evaluates AI-generated summaries using the [Agent-to-Agent (A2A) protocol](https://github.com/a2aproject/A2A). After the Summarizer produces a summary it automatically calls the Critic, which returns a structured quality evaluation.

**What the Critic evaluates:**

| Dimension | Description |
|---|---|
| Accuracy | Does the summary faithfully represent the source? |
| Completeness | Are all key points covered? |
| Clarity | Is the language easy to understand? |
| Conciseness | Is it appropriately brief? |

The result is appended to the chat as a **## Critique** section with per-dimension scores (1–10) and actionable improvement suggestions.

### Run with Docker (recommended)

The critic agent uses **Vertex AI** with Application Default Credentials — the same credentials as the main application.

```bash
# Build the image
docker build -t a2a-critic ./a2a_agents/critic

# Run on port 8001 — mount your ADC credentials file
docker run -p 8001:8001 \
  -v ~/.config/gcloud:/root/.config/gcloud:ro \
  -e GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json \
  -e GOOGLE_CLOUD_PROJECT=<your-project-id> \
  a2a-critic
```

### Run locally (without Docker)

```bash
# No extra env vars needed — inherits your active ADC session
python a2a_agents/critic/server.py
```

### Connect the Summarizer agent

Add the following to your `.env` and restart the main application:

```env
CRITIC_A2A_URL=http://localhost:8001/.well-known/agent.json
```

The Summarizer will now call the Critic after every summary and display the evaluation inline.

### Deploy to HuggingFace Spaces

1. Create a new **Docker** Space on [huggingface.co/spaces](https://huggingface.co/spaces)
2. Push the contents of `a2a_agents/critic/` to the Space repository
3. In the Space **Settings → Secrets**, add:
   - `GOOGLE_CLOUD_PROJECT` — your GCP project ID
   - `GOOGLE_CLOUD_LOCATION` — e.g. `europe-north1`
   - `GOOGLE_APPLICATION_CREDENTIALS_JSON` — the full JSON content of your ADC credentials file
4. Add a startup line to `server.py` (or a wrapper script) that writes the JSON secret to a file and sets the env var:
   ```python
   import json, os, pathlib
   creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON", "")
   if creds_json:
       path = pathlib.Path("/tmp/gcloud_credentials.json")
       path.write_text(creds_json)
       os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(path)
   ```
5. Set `AGENT_URL` to your Space's public URL (e.g. `https://your-name-a2a-critic.hf.space/`)
6. Update `CRITIC_A2A_URL` in your main app's `.env`:
   ```env
   CRITIC_A2A_URL=https://your-name-a2a-critic.hf.space/.well-known/agent.json
   ```

> **Note:** The main application works without the critic server. The `critique_summary` tool returns a graceful skip message when `CRITIC_A2A_URL` is empty or the server is unreachable.

---

## 10. Long-Term Memory (Vertex AI Memory Bank)

The Summarizer agent can remember past conversations across sessions using the **Vertex AI Memory Bank**. Every time the agent finishes a turn it saves the conversation to a persistent memory store. On the next session, relevant past conversations are automatically surfaced to the agent and, when needed, the agent can also search memory explicitly.

### How it works

```
Session A (today)
  user: "Summarize this ML paper…"
  agent: produces summary → saves session to Memory Bank ✓

Session B (tomorrow, new session)
  agent startup: preload_memory injects relevant past conversations into context
  user: "Do you remember the ML paper we discussed?"
  agent: recalls the summary from Session A ✓

  user: "Find everything we discussed about transformers"
  agent: calls load_memory("transformers") → returns matching past turns ✓
```

Two memory tools cooperate:

| Tool | When it runs | What it does |
|---|---|---|
| `preload_memory` | Automatically at the start of every turn | Injects the most relevant past conversations silently into the model context — no user action needed |
| `load_memory` | When the agent decides it is useful | Explicit semantic search over the Memory Bank — returns matching past conversations as text |

The session is saved to the Memory Bank automatically after every agent turn via the `after_agent_callback`.

### Setup

The Memory Bank runs on **Vertex AI Agent Engine**, which is only available in `us-central1` (as of 2025), even if your main project uses a different region.

**1. Enable the required API**

```bash
gcloud services enable aiplatform.googleapis.com --project=<PROJECT_ID>
```

**2. Add Memory Bank variables to `.env`**

```env
# Region for the Memory Bank — must be us-central1
MEMORY_BANK_LOCATION=us-central1

# Agent Engine backing the Memory Bank.
# Leave empty on first start — the app creates one automatically and logs its ID.
# Copy the ID here afterwards to avoid re-creating it on every restart.
AGENT_ENGINE_ID=
```

**3. Start the app and copy the Agent Engine ID**

On the very first start with an empty `AGENT_ENGINE_ID` the app provisions a new Agent Engine (~60 s). The ID is printed in the server logs:

```
agent_engine_id=projects/my-project/locations/us-central1/reasoningEngines/1234567890
```

Copy this value into `.env`:

```env
AGENT_ENGINE_ID=1234567890
```

Subsequent starts will reuse the existing engine (< 1 s).

### Example conversation

Open the **Summarizer** agent and have a multi-session conversation:

**Session 1** — Upload or paste a document:

> *"Please summarize the following paper: [paste text]"*

The agent produces a structured summary, the A2A Critic evaluates it, and the full conversation is saved to the Memory Bank automatically.

**Session 2** — Start a fresh session (reload the page or switch away and back):

> *"What did we work on last time?"*

The agent replies based on the automatically injected past context — no need to repeat the document.

> *"Do you remember the section about model architecture?"*

The agent searches memory explicitly and surfaces the relevant paragraph from the previous session.

> *"How many documents have we summarized in total?"*

The agent can call `list_state` for the current session or `load_memory` for cross-session history.

### Session inspection (debug)

Two REST endpoints let you inspect the live session state without touching the UI:

```bash
# Current session state variables (last_topic, docs_summarized, …)
curl "http://localhost:8000/api/v1/session/state?agent_id=summarizer_agent"

# Last 20 events in the session (author, text snippet, state changes)
curl "http://localhost:8000/api/v1/session/events?agent_id=summarizer_agent&limit=20"
```

> **Note:** The Memory Bank is optional. If `MEMORY_BANK_LOCATION` is not set, the agent works normally but past sessions are not remembered.

---

## 11. Artifact Storage (GCS)

Agents can produce downloadable files called **artifacts** — the Summarizer saves every summary as a `.md` file and the Research Orchestrator saves every report as a `.md` file. Artifacts are stored in your Cloud Storage bucket and are versioned automatically.

### Viewing and downloading artifacts

1. Select the **Summarizer** or **Research Orchestrator** agent in the sidebar
2. Click the **📎 Artifacts** tab — it appears automatically for agents that support artifacts
3. Each file is listed with its filename and a download arrow (⬇)

### How artifacts are created

The agents call the `save_artifact` tool after completing their primary task:

| Agent | When | Filename |
|---|---|---|
| Summarizer | After every structured summary | `<topic>_summary.md` |
| Research Orchestrator | After every research report | `<topic>_report.md` |

Filenames are derived automatically from the document title or research topic.

### Where artifacts are stored in GCS

```
gs://<GOOGLE_CLOUD_STORAGE_BUCKET>/
  <app_name>/<user_id>/<session_id>/<filename>/<version>
```

Each call to `save_artifact` increments the version. The Artifacts panel always shows the latest version.

### Custom artifacts

Any agent with access to the `save_artifact` tool can persist content. Pass a filename (`.md` for Markdown, `.txt` for plain text, `.pdf` for PDF) and the content string. Example agent instruction:

> *"Summarize this document and save the result as `my_notes.md`"*

---

## 12. RAG Documents (Knowledge Base)

The **RAG Docs** panel lets you build a persistent knowledge base that both the Summarizer and the Research Orchestrator can query before reaching out to the web. Documents are stored in a **Vertex AI RAG corpus** and retrieved semantically at query time.

### How retrieval works

```
user asks a question
  → agent calls retrieve_from_corpus("query")
      → Vertex AI returns the most relevant text chunks (top-5)
          → agent uses chunks as grounded context
              → agent fetches web only if corpus result is insufficient
```

For Gemini 2+ models retrieval is handled server-side as a native tool — no extra function-call round-trip is needed.

### Setup

**1. Enable the Vertex AI RAG Engine API**

The RAG Engine uses the same `aiplatform.googleapis.com` API as the rest of Vertex AI. If you already enabled it in §2.2, nothing more is needed.

**2. Add the RAG corpus variable to `.env`** (optional on first start)

```env
# Leave empty to auto-create a corpus on first start.
# After the first start, copy the corpus name printed in the logs:
RAG_CORPUS=
```

On the first start the app looks for an existing corpus named `agentic-ai-engineering-rag` and creates one if it does not exist. The corpus name is printed in the server logs:

```
RAG corpus created  corpus_name=projects/.../locations/.../ragCorpora/123
```

Copy this value into `.env` to skip auto-discovery on subsequent starts:

```env
RAG_CORPUS=projects/<PROJECT_ID>/locations/<LOCATION>/ragCorpora/<ID>
```

### Adding documents via the UI

The **RAG Docs** sidebar panel accepts any file that has already been uploaded to your Cloud Storage bucket.

1. Upload the file to GCS (using the `gcloud` CLI or the Cloud Console):
   ```bash
   gcloud storage cp my_document.pdf gs://<BUCKET_NAME>/corpus/
   ```
2. Select the **Summarizer** or **Research Orchestrator** agent
3. Click the **🗂️ RAG Docs** tab
4. Paste the GCS URI into the input field:
   ```
   gs://<BUCKET_NAME>/corpus/my_document.pdf
   ```
5. Click **Import** — the file is chunked and embedded automatically

Supported file types: `.pdf`, `.txt`, `.md`, `.html`, `.docx`

### Adding documents via the seed script

The `corpus/` directory contains three sample documents about AI agents, RAG, and Google Cloud. Run the seed script once to upload and import them all:

```bash
python corpus/seed_corpus.py
```

The script:
1. Uploads every `.md` file in `corpus/` to `gs://<BUCKET>/corpus/`
2. Imports the GCS URIs into the RAG corpus (chunked at 1 024 tokens, 200-token overlap)
3. Prints the corpus resource name — copy it into `.env` as `RAG_CORPUS`

### Sample corpus documents

| File | Content |
|---|---|
| `corpus/ai_agents_and_orchestration.md` | ReAct pattern, orchestrator / sub-agent design, Google ADK components |
| `corpus/retrieval_augmented_generation.md` | RAG pipeline, chunking, Vertex AI RAG Engine, RAG vs fine-tuning |
| `corpus/vertex_ai_and_google_cloud_ai.md` | Gemini models, Vertex AI services, Cloud Run deployment, GCS |

After seeding, try asking the Research Orchestrator:

> *"Research how RAG differs from fine-tuning"*

The researcher will pull the relevant chunks from the corpus before fetching any URLs.

### Managing documents

The RAG Docs panel lists all imported files. Each file has a **✕** delete button to remove it from the corpus.

To list or delete files via the REST API:

```bash
# List all documents in the corpus
curl "http://localhost:8000/api/v1/rag/files"

# Delete a document by resource name
curl -X DELETE "http://localhost:8000/api/v1/rag/files?file_name=<resource_name>"
```

> **Note:** The RAG corpus is optional. If the corpus cannot be created (e.g. the API is not enabled), the agents fall back to web search only. No error is shown to the user.

