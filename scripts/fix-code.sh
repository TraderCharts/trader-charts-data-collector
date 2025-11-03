#!/bin/bash
set -e

echo "🔧 Applying automatic code fixes..."
black .
isort .
ruff check --fix .
echo "✅ All fixes applied automatically!"