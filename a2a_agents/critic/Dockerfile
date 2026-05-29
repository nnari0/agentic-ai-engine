FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py server.py ./

# Required: mount credentials at runtime via -v and set this path
ENV GOOGLE_APPLICATION_CREDENTIALS=""
# Required: your GCP project ID
ENV GOOGLE_CLOUD_PROJECT=""
# Optional: Vertex AI region (default matches the main app)
ENV GOOGLE_CLOUD_LOCATION=europe-north1

# Optional overrides
ENV CRITIC_LLM_MODEL=gemini-2.5-flash
ENV A2A_HOST=0.0.0.0
ENV A2A_PORT=8001
# Set AGENT_URL to the public URL when deploying (e.g. your HuggingFace Space URL)
ENV AGENT_URL=http://localhost:8001/

EXPOSE 8001

CMD ["python", "server.py"]
