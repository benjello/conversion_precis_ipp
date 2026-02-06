#!/bin/sh
# Serve the book from public/ so that links like /presentation.html work.
# Open http://localhost:8765/ in your browser.
cd "$(dirname "$0")/public"
if command -v uv >/dev/null 2>&1; then
  uv run python -m http.server 8765
else
  python3 -m http.server 8765
fi
