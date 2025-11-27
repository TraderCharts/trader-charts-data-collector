# ----------------------------
# Stage 1: Base
# ----------------------------
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Copy dependency files first to leverage Docker layer caching
COPY pyproject.toml requirements.txt requirements-dev.txt README.md ./

# Install base dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------
# Stage 2: Development
# ----------------------------
FROM base AS development

# Copy full source code
COPY scripts/ ./scripts
COPY src/ ./src

# Install development dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Development environment variables
ENV MONGODB_URI=mongodb://host.docker.internal:27017

# Interactive entrypoint for development
ENTRYPOINT ["/bin/bash"]

# ----------------------------
# Stage 3: Production / Final
# ----------------------------
FROM base AS production

# Copy full source code
COPY scripts/ ./scripts
COPY src/ ./src

# Install development dependencies as some scripts may require them
RUN pip install --no-cache-dir -r requirements-dev.txt

# Production environment variables (can be overridden via docker-compose env_file)
ENV MONGODB_URI=mongodb://mongo-prod:27017

# ⚠ No default CMD, the container will only run the command you provide
