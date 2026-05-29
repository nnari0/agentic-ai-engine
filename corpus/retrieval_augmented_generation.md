# Retrieval-Augmented Generation (RAG)

## What is RAG?

Retrieval-Augmented Generation (RAG) is a technique that improves LLM responses
by injecting relevant documents from an external knowledge base at inference time.
Instead of relying solely on the model's training knowledge (which has a cutoff
date and may hallucinate facts), RAG:

1. Encodes the user's query into a vector embedding
2. Searches a vector index for the nearest-neighbour document chunks
3. Injects the retrieved chunks into the LLM's context window as additional context
4. The model generates its response grounded in the retrieved evidence

## Why RAG Matters

| Problem with bare LLMs | RAG solution |
|------------------------|-------------|
| Knowledge cutoff | Corpus can contain up-to-date documents |
| Hallucination | Response is grounded in retrieved text |
| Long context cost | Only relevant chunks are injected |
| Proprietary knowledge | Private documents stay in a controlled corpus |

## Core Components

### Chunking
Long documents are split into overlapping chunks (e.g., 1 024 tokens with a
200-token overlap). Smaller chunks improve retrieval precision; overlap prevents
context from being cut at sentence boundaries.

### Embedding
Each chunk is converted into a dense vector by an embedding model
(e.g., `text-embedding-004`). Similar text has a small cosine distance.

### Vector Index
Chunks and their embeddings are stored in a vector database. At query time the
query embedding is compared to all chunk embeddings; the top-k closest are returned.

### Reranking (optional)
A cross-encoder model rescores the top-k results for higher precision before
injecting them into the LLM context.

## Vertex AI RAG Engine

Vertex AI RAG Engine is a managed service that handles the full RAG pipeline:

- **Corpus management** – create, list, and delete corpora via SDK or REST
- **File import** – ingest PDFs, text, and HTML from GCS; chunking and embedding
  happen automatically
- **Retrieval** – `rag.retrieval_query()` returns the most relevant chunks with
  source attribution
- **Integration** – `VertexAiRagRetrieval` in Google ADK injects the corpus as a
  native Gemini tool; for Gemini 2+ models retrieval is server-side with no
  extra function-call round-trip

### Typical Setup

```python
from vertexai.preview import rag

# Create a corpus
corpus = rag.create_corpus(display_name="my-corpus")

# Import documents from GCS
rag.import_files(
    corpus_name=corpus.name,
    paths=["gs://my-bucket/docs/"],
    chunk_size=1024,
    chunk_overlap=200,
)

# Query
response = rag.retrieval_query(
    text="What is the ReAct pattern?",
    rag_corpora=[corpus.name],
    similarity_top_k=5,
)
for ctx in response.contexts.contexts:
    print(ctx.text)
```

## RAG vs Fine-Tuning

| Dimension | RAG | Fine-tuning |
|-----------|-----|-------------|
| Update frequency | Real-time (add files to corpus) | Requires retraining |
| Cost | Low (retrieval at inference) | High (GPU training cost) |
| Best for | Factual Q&A over a document set | Style, tone, task format |
| Transparency | Sources cited | Black box |

RAG and fine-tuning are complementary: a fine-tuned model with RAG performs
better than either alone for knowledge-intensive tasks.
