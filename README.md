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

You can also ask follow-up questions about the document (e.g. *"Who is the author?"*, *"What is the main argument?"*). If the MCP Fetch server is running, the agent can additionally fetch URLs you share in the chat.

### 🔬 Research Team (`research_coordinator`)

A multi-agent team that researches a topic by fetching live web sources and compiling the findings into a structured report. Switch to it by clicking **Research Agent** in the sidebar.

**How it works:**

```
research_coordinator  (orchestrator)
 ├── web_researcher   → fetches web pages via the MCP Fetch server
 └── report_writer    → compiles findings into a Markdown report
```

**Example prompt:**

> *"Research the impact of large language models on software engineering"*

The coordinator will:
1. Identify 2–4 authoritative URLs
2. Delegate each fetch to the `web_researcher`
3. Pass all findings to the `report_writer`
4. Return a fully sourced Markdown report

> **Note:** Web fetching requires the MCP Fetch server (see §8). Without it the coordinator falls back to the model's training knowledge.

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

Both the **Summarizer** and the **Research Team** will then have access to `fetch_page`. Example prompts:

> *"Please summarize https://example.com/article"*  (Summarizer agent)

> *"Research recent advances in quantum error correction"*  (Research agent)

> **Note:** The main application starts without the MCP server. The `fetch_page` tool is only available when `MCP_FETCH_URL` is configured and the server is reachable.

