#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <book_dir_name> [chapter_qmd]"
  echo "Example: $0 fiscalite chapters/indirecte/indirecte.qmd"
  exit 2
fi

ROOT_DIR="/home/benjello/projets/conversion_precis_ipp"
BOOK_NAME="$1"
BOOK_DIR="$ROOT_DIR/quarto/$BOOK_NAME"
CHAPTER_QMD="${2:-chapters/indirecte/indirecte.qmd}"

if [[ ! -d "$BOOK_DIR" ]]; then
  echo "[check] Book directory not found: $BOOK_DIR"
  exit 1
fi

echo "[check] Regenerating QMDs for $BOOK_NAME..."
PYTHONPATH="$ROOT_DIR/quarto" uv run python -m "tex2qmd.${BOOK_NAME}"

if [[ -z "${QUARTO_PYTHON:-}" ]]; then
  if command -v uv >/dev/null 2>&1; then
    QUARTO_PYTHON="$(uv python find)"
    export QUARTO_PYTHON
    echo "[check] QUARTO_PYTHON not set, using $QUARTO_PYTHON (uv)"
  else
    DEFAULT_QUARTO_PYTHON="$ROOT_DIR/.venv/bin/python"
    if [[ -x "$DEFAULT_QUARTO_PYTHON" ]]; then
      export QUARTO_PYTHON="$DEFAULT_QUARTO_PYTHON"
      echo "[check] QUARTO_PYTHON not set, using $QUARTO_PYTHON"
    else
      echo "[check] QUARTO_PYTHON is not set. Using current python: $(command -v python3)"
    fi
  fi
else
  echo "[check] QUARTO_PYTHON=${QUARTO_PYTHON}"
fi

echo "[check] Rendering ${CHAPTER_QMD}..."
quarto render "$BOOK_DIR/$CHAPTER_QMD"

echo "[check] OK"
