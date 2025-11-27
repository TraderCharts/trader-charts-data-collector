#!/bin/bash
set -e  # Stop script if any command fails

echo "🔍 Running code quality checks (CI mode)..."
black --check --diff .
isort --check-only --diff .
ruff check .
echo "✅ All code quality checks passed!"