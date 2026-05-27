FROM python:3.12-slim

WORKDIR /app

COPY server.py .

RUN pip install --no-cache-dir \
    "mcp[cli]>=1.0.0" \
    "httpx>=0.28.0" \
    "beautifulsoup4>=4.12.0" \
    "lxml>=5.0.0"

# MCP_HOST / MCP_PORT can be overridden at runtime
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8002

EXPOSE 8002

CMD ["python", "server.py"]
