#!/bin/bash

# Claude Agent SDK Handson Test Script
# Runs all Python files in src directory


set -e

PYTHON=/opt/homebrew/Cellar/python@3.14/3.14.0_1/bin/python3

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
STEP_DIR="$1"

cd "$PROJECT_ROOT"

echo "=== Claude Agent SDK Handson Tests ==="
echo ""



# Find and run all Python files in src subdirectories
for py_file in src/"$STEP_DIR"/*.py src/"$STEP_DIR"/*/*.py src/"$STEP_DIR"/*/*/*.py; do
    if [ -f "$py_file" ]; then
        echo "Running: $py_file"
        $PYTHON "$py_file"
        echo "---"

    fi
done

echo ""
echo "=== All tests completed ==="
