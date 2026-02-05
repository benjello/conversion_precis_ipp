"""Convert LaTeX chapters to Quarto .qmd. Source dir via TEX2QMD_SOURCE_DIR."""

from pathlib import Path
import os

# Project root (ipp/); package is quarto/tex2qmd/
PACKAGE_DIR = Path(__file__).resolve().parent
QUARTO_DIR = PACKAGE_DIR.parent
IPP_ROOT = QUARTO_DIR.parent


def get_source_dir() -> Path:
    """LaTeX source directory. Set TEX2QMD_SOURCE_DIR to override default."""
    raw = os.environ.get("TEX2QMD_SOURCE_DIR")
    if raw:
        return Path(raw).expanduser().resolve()
    return IPP_ROOT / "source" / "Fiscalité" / "Chapitres"
