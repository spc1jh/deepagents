#!/bin/bash
# Deep Agents CLI launcher
# Usage: ./deepagents.sh [workspace_path]
# Example: ./deepagents.sh /home/ubuntu/my-coding-test
# Example: ./deepagents.sh  (uses current directory)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="deepagents-cli"

# First argument is workspace path; default to current directory
WORKSPACE="${1:-$(pwd)}"

# Create workspace directory if it does not exist
mkdir -p "$WORKSPACE"
WORKSPACE="$(cd "$WORKSPACE" && pwd)"  # resolve to absolute path

# Auto-build image if it does not exist
if ! docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
    echo "🔨 Building deepagents-cli Docker image..."
    docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"
    echo "✅ Build complete."
fi

echo ""
echo "🚀 Starting Deep Agents CLI"
echo "📁 Workspace: $WORKSPACE"
echo "--------------------------------------"

# Build volume args for optional files
EXTRA_ARGS=()

# Mount memory database for persistence across sessions
MEMORY_DIR="$HOME/.deepagents"
mkdir -p "$MEMORY_DIR"
EXTRA_ARGS+=(-v "$MEMORY_DIR:/root/.deepagents")

# Mount MCP config if available
if [ -f "$HOME/.mcp.json" ]; then
    EXTRA_ARGS+=(-v "$HOME/.mcp.json:/root/.mcp.json:ro")
fi

# Pass API keys from current environment
API_KEY_ARGS=()
[ -n "$ANTHROPIC_API_KEY" ] && API_KEY_ARGS+=(-e "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY")
[ -n "$OPENAI_API_KEY" ] && API_KEY_ARGS+=(-e "OPENAI_API_KEY=$OPENAI_API_KEY")
[ -n "$OPENROUTER_API_KEY" ] && API_KEY_ARGS+=(-e "OPENROUTER_API_KEY=$OPENROUTER_API_KEY")
[ -n "$DEEPAGENTS_DEFAULT_MODEL" ] && API_KEY_ARGS+=(-e "DEEPAGENTS_DEFAULT_MODEL=$DEEPAGENTS_DEFAULT_MODEL")
[ -n "$TAVILY_API_KEY" ] && API_KEY_ARGS+=(-e "TAVILY_API_KEY=$TAVILY_API_KEY")

docker run -it --rm \
    --name deepagents-session \
    -v "$WORKSPACE:/workspace" \
    "${EXTRA_ARGS[@]}" \
    "${API_KEY_ARGS[@]}" \
    "$IMAGE_NAME"
