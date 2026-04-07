FROM python:3.12-slim

# Install system tools used by deepagents CLI (git, ripgrep, curl, etc.)
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ripgrep \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy full libs/ so relative path references resolve correctly
# (libs/cli depends on ../deepagents via [tool.uv.sources])
COPY libs/ /app/libs/
RUN uv pip install --system -e /app/libs/cli


# Set workspace directory
WORKDIR /workspace

# Required for Textual TUI rendering
ENV TERM=xterm-256color

ENTRYPOINT ["deepagents"]
