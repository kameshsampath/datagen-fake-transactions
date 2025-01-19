ARG PYTHON_VERSION=3.11

FROM python:$PYTHON_VERSION-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app/src:$PYTHONPATH" \
    PATH="/app/bin:$PATH"

# Create non-root user and set up directories
RUN adduser -D me && \
    mkdir -p /app/src && \
    mkdir -p /app/bin && \
    chown -R me:me /app

# Set working directory
WORKDIR /app

# Install build dependencies for any potential package compilation
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    git

# Copy and install requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Remove build dependencies to reduce image size
RUN apk del \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    cargo

COPY src/ /app/src/
COPY scripts/producer.py /app/bin/entrypoint

RUN chown -R me:me /app/src /app/bin/

USER me

ENTRYPOINT [ "/app/bin/entrypoint" ]