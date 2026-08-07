# Stage 1: Build dependencies
FROM python:3.14-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir uv

COPY pyproject.toml .
# Install dependencies into a virtualenv
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install -e .

# Stage 2: Runtime
FROM python:3.14-slim
WORKDIR /app

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose Webhook server port
EXPOSE 8000

# Default command runs the webhook server
CMD ["python", "src/infrastructure/webhook_server.py"]
