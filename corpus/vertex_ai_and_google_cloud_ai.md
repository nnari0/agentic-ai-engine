# Vertex AI and Google Cloud AI Platform

## Vertex AI Overview

Vertex AI is Google Cloud's unified machine learning platform. It brings together
data engineering, model training, deployment, and MLOps tooling under a single API
surface. Key service areas:

### Generative AI

- **Gemini models** – Google's multimodal LLM family (text, image, audio, video,
  code). The Gemini 2.x line supports native tool use, code execution, and
  server-side RAG retrieval without extra API round-trips.
- **Model Garden** – a catalogue of first-party (Google) and third-party
  (Mistral, Llama, Anthropic) models accessible via a unified API.
- **Generative AI Studio** – a web UI for prompt engineering and model evaluation.

### Agent Infrastructure

| Service | Purpose |
|---------|---------|
| Vertex AI Agent Engine | Managed runtime for deploying ADK agents at scale |
| Vertex AI RAG Engine | Managed retrieval-augmented generation corpus service |
| Vertex AI Memory Bank | Long-term memory across agent sessions |
| Vertex AI Search | Enterprise search with LLM-powered summarisation |

### MLOps

- **Vertex AI Pipelines** – Kubeflow-based ML pipeline orchestration
- **Model Registry** – versioned model storage with lineage tracking
- **Feature Store** – managed feature engineering and serving
- **Experiments** – experiment tracking comparable to MLflow/W&B

## Gemini API Key Concepts

### Multimodal Input
Gemini accepts text, images, PDFs, audio, and video in a single request.
Parts are passed as a `types.Content` object with a list of `types.Part`.

### Tool Use (Function Calling)
The model can request a tool call by returning a `FunctionCall` part.
The caller executes the function, returns a `FunctionResponse`, and the model
continues reasoning. Native tools (Search, Code Execution, RAG) bypass this
loop entirely and run server-side.

### Context Window
Gemini 2.0 Flash: 1 M tokens  
Gemini 1.5 Pro: 2 M tokens  
Large context enables long-document processing without chunking.

### Grounding
- **Google Search grounding** – answers are grounded in live Search results
- **Vertex AI RAG grounding** – answers are grounded in a private corpus
- Both grounding modes include source attribution in the response

## Cloud Run and Deployment

Agentic AI backends are commonly deployed on Cloud Run:

- Fully managed serverless containers
- Scales to zero (no idle cost)
- HTTP(S) and WebSocket support
- IAM-based authentication with Workload Identity Federation

Typical deployment steps:
1. Build a Docker image (`docker build`)
2. Push to Artifact Registry (`docker push`)
3. Deploy to Cloud Run (`gcloud run deploy`)
4. Set environment variables (`GOOGLE_CLOUD_PROJECT`, `RAG_CORPUS`, etc.)

## Google Cloud Storage (GCS)

GCS is an object store used throughout the agentic stack:

- **Artifact storage** – `GcsArtifactService` saves agent-produced files
- **RAG corpus source** – documents are ingested from GCS URIs
- **Model outputs** – batch prediction results land in GCS
- **Structured data** – CSV/Parquet files for BigQuery loading

Bucket naming convention for this project: `agentic-ai-eng-bucket`  
Corpus documents path: `gs://agentic-ai-eng-bucket/corpus/`
