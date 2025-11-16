#!/bin/bash
# Run Orbiton Agent with proper environment

# Set Python path
export PYTHONPATH="/Users/meomeocoj/prediction-agent-spoon/orbiton-agent:$PYTHONPATH"

# Change to orbiton-agent directory
cd "$(dirname "$0")"

# Run with uv
exec uv run python main.py "$@"
