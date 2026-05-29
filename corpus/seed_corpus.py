"""Seed the Vertex AI RAG corpus with the sample documents in this directory.

Usage:
    python corpus/seed_corpus.py

The script:
  1. Uploads every .md file in the corpus/ directory to GCS
     (gs://<GOOGLE_CLOUD_STORAGE_BUCKET>/corpus/<filename>)
  2. Imports the GCS URIs into the RAG corpus
     (auto-creates the corpus when RAG_CORPUS env var is not set)

Reads the project-root .env file automatically (same variables as the main app):
  GOOGLE_CLOUD_PROJECT          – GCP project ID (required)
  GOOGLE_CLOUD_LOCATION         – region, default: europe-north1
  GOOGLE_CLOUD_STORAGE_BUCKET   – GCS bucket name, default: agentic-ai-eng-bucket
  RAG_CORPUS                    – existing corpus resource name (optional)
  GOOGLE_APPLICATION_CREDENTIALS – path to ADC credentials file (required)
"""

from __future__ import annotations

import os
import pathlib

from dotenv import load_dotenv

# Load .env from the project root (one level above corpus/).
load_dotenv(pathlib.Path(__file__).parent.parent / ".env")

import vertexai
from google.cloud import storage
from vertexai.preview import rag

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "europe-north1")
BUCKET = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET", "agentic-ai-eng-bucket")
RAG_CORPUS = os.getenv("RAG_CORPUS", "")
CORPUS_DISPLAY_NAME = "agentic-ai-engineering-rag"
GCS_PREFIX = "corpus"

CORPUS_DIR = pathlib.Path(__file__).parent
SEED_FILES = sorted(CORPUS_DIR.glob("*.md"))


def upload_to_gcs(bucket_name: str, local_path: pathlib.Path, gcs_path: str) -> str:
    """Upload a local file to GCS and return the gs:// URI."""
    client = storage.Client(project=PROJECT)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(str(local_path), content_type="text/plain")
    uri = f"gs://{bucket_name}/{gcs_path}"
    print(f"  Uploaded {local_path.name} → {uri}")
    return uri


def get_or_create_corpus() -> str:
    """Return an existing corpus resource name or create a new one."""
    if RAG_CORPUS:
        if not RAG_CORPUS.startswith("projects/"):
            print(
                f"WARNING: RAG_CORPUS='{RAG_CORPUS}' does not look like a valid corpus "
                f"resource name (expected 'projects/.../locations/.../ragCorpora/...').\n"
                f"Ignoring it and searching for an existing corpus instead."
            )
        else:
            print(f"Using configured corpus: {RAG_CORPUS}")
            return RAG_CORPUS

    for corpus in rag.list_corpora():
        if corpus.display_name == CORPUS_DISPLAY_NAME:
            print(f"Found existing corpus: {corpus.name}")
            return corpus.name

    print(f"Creating new corpus: {CORPUS_DISPLAY_NAME}")
    corpus = rag.create_corpus(display_name=CORPUS_DISPLAY_NAME)
    print(f"Created corpus: {corpus.name}")
    return corpus.name


def main() -> None:
    vertexai.init(project=PROJECT, location=LOCATION)

    if not SEED_FILES:
        print("No .md files found in corpus/ directory.")
        return

    print(f"\nUploading {len(SEED_FILES)} file(s) to gs://{BUCKET}/{GCS_PREFIX}/\n")
    gcs_uris = []
    for path in SEED_FILES:
        gcs_path = f"{GCS_PREFIX}/{path.name}"
        uri = upload_to_gcs(BUCKET, path, gcs_path)
        gcs_uris.append(uri)

    corpus_name = get_or_create_corpus()

    print(f"\nImporting {len(gcs_uris)} file(s) into corpus …")
    transformation_config = rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(
            chunk_size=1024,
            chunk_overlap=200,
        ),
    )
    response = rag.import_files(
        corpus_name=corpus_name,
        paths=gcs_uris,
        transformation_config=transformation_config,
    )
    print(f"Import complete: {response.imported_rag_files_count} file(s) imported.")
    print(f"\nCorpus resource name: {corpus_name}")
    print("Set this as RAG_CORPUS in your .env if you want to skip auto-discovery:\n")
    print(f"  RAG_CORPUS={corpus_name}\n")


if __name__ == "__main__":
    main()
