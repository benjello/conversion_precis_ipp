"""
Build tables from OpenFisca-France parameters (YAML) for use in Quarto .qmd.

Tables can be generated from:
- Local parameters: set OPENFISCA_PARAMETERS_DIR to a path (e.g. parameters/)
- Installed package: pip install openfisca-france, then parameters are loaded from the package
- GitHub raw URLs: used as fallback to fetch TVA YAML if no local/package path

Usage in a Quarto Python chunk:
  from openfisca_tables import table_tva_historique_md
  print(table_tva_historique_md())
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# Try optional dependencies
try:
    import yaml
except ImportError:
    yaml = None

try:
    import pandas as pd
except ImportError:
    pd = None


# Default: first year to show; then only years where at least one rate changes
DEFAULT_TVA_START_YEAR = 1972

# OpenFisca TVA rate file name -> table row label (French)
TVA_RATE_LABELS = {
    "taux_particulier_super_reduit": "Super réduit",
    "taux_reduit": "Réduit",
    "taux_reduit_2": "Réduit supérieur",
    "taux_normal": "Normal",
    "taux_majore": "Majoré",
    "taux_intermediaire": "Intermédiaire",
}


def _get_parameters_dir() -> Path | None:
    """Return path to OpenFisca parameters (local dir or package)."""
    env = os.environ.get("OPENFISCA_PARAMETERS_DIR")
    if env:
        p = Path(env).expanduser().resolve()
        if p.is_dir():
            return p
    # Try openfisca_france package
    try:
        import openfisca_france  # type: ignore[import-untyped]
        base = Path(openfisca_france.__file__).resolve().parent
        params = base / "parameters" / "taxation_indirecte"
        if params.is_dir():
            return params
    except ImportError:
        pass
    # Local parameters next to this script
    local = Path(__file__).resolve().parent / "parameters" / "taxation_indirecte"
    if local.is_dir():
        return local
    return None


def _load_yaml(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    if yaml is None:
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _value_at_year(values: dict[str, Any], year: int) -> float | None:
    """Get parameter value in effect at the start of year (OpenFisca dates are YYYY-MM-DD or date)."""
    if not values or "values" not in values:
        return None
    def _date_key(d: Any) -> Any:
        return d if hasattr(d, "year") else str(d)
    dates = sorted(values["values"].keys(), key=_date_key, reverse=True)
    for d in dates:
        y = d.year if hasattr(d, "year") else int(str(d)[:4])
        if y <= year:
            v = values["values"][d]
            if isinstance(v, dict) and v.get("value") is not None:
                return float(v["value"])
            if isinstance(v, (int, float)):
                return float(v)
    return None


def _fetch_tva_yaml_from_github(filename: str) -> dict[str, Any] | None:
    """Fetch a single TVA parameter file from OpenFisca-France GitHub."""
    if yaml is None:
        return None
    try:
        import urllib.request
        url = (
            "https://raw.githubusercontent.com/openfisca/openfisca-france/master"
            f"/openfisca_france/parameters/taxation_indirecte/tva/{filename}"
        )
        with urllib.request.urlopen(url, timeout=10) as resp:
            return yaml.safe_load(resp.read().decode())
    except Exception:
        return None


def _max_year_in_rate_data(rate_data: list[tuple[str, dict[str, Any]]]) -> int:
    """Return the latest year that appears in any rate parameter values."""
    import datetime
    out = datetime.date.today().year
    for _name, data in rate_data:
        if not data or "values" not in data:
            continue
        for d in data["values"].keys():
            y = d.year if hasattr(d, "year") else int(str(d)[:4])
            out = max(out, y)
    return out


def _years_where_tva_changes(
    start_year: int,
    rate_data: list[tuple[str, dict[str, Any]]],
    max_year: int | None = None,
) -> list[int]:
    """
    Return years from start_year onward where at least one TVA rate changed.

    rate_data: list of (rate_name, yaml_data) in display order.
    max_year: last year to consider (default: latest year in data).
    """
    if not rate_data:
        return []
    if max_year is None:
        max_year = _max_year_in_rate_data(rate_data)

    def profile(y: int) -> tuple[float | None, ...]:
        return tuple(_value_at_year(data, y) for _name, data in rate_data)

    change_years: list[int] = [start_year]
    for y in range(start_year + 1, max_year + 1):
        if profile(y) != profile(y - 1):
            change_years.append(y)
    return change_years


def table_tva_historique(
    annees: list[int] | None = None,
    start_year: int = DEFAULT_TVA_START_YEAR,
    parameters_dir: Path | None = None,
) -> "pd.DataFrame | None":
    """
    Build the "Évolution des taux de TVA en France" table from OpenFisca YAML.

    If annees is None, columns are all years from start_year (default 1972) up to
    the latest data, keeping only years where at least one rate changed.

    Returns a DataFrame with rows = rate types (Super réduit, Réduit, ...) and
    columns = years. Values are in % (e.g. 20 for 20%). Returns None if YAML/pandas unavailable.
    """
    if pd is None:
        return None
    base = parameters_dir or _get_parameters_dir()

    # Rate files to load (in display order)
    rate_files = [
        "taux_particulier_super_reduit",
        "taux_reduit",
        "taux_reduit_2",
        "taux_normal",
        "taux_majore",
    ]
    rate_data: list[tuple[str, dict[str, Any]]] = []

    for name in rate_files:
        data: dict[str, Any] = {}
        if base:
            data = _load_yaml(base / "tva" / f"{name}.yaml") or {}
        if not data and name in (
            "taux_normal",
            "taux_reduit",
            "taux_reduit_2",
            "taux_majore",
            "taux_particulier_super_reduit",
        ):
            data = _fetch_tva_yaml_from_github(f"{name}.yaml") or {}
        if not data:
            continue
        rate_data.append((name, data))

    if not rate_data:
        return None

    if annees is None:
        annees = _years_where_tva_changes(start_year, rate_data)

    rows: list[dict[str, Any]] = []
    for name, data in rate_data:
        label = TVA_RATE_LABELS.get(name, name)
        row: dict[str, Any] = {"Type de taux": label}
        for year in annees:
            val = _value_at_year(data, year)
            if val is not None:
                row[str(year)] = f"{val * 100:.1f}".replace(".0", "").replace(".", ",")
            else:
                row[str(year)] = "–"
        rows.append(row)

    df = pd.DataFrame(rows)
    cols = ["Type de taux"] + [str(y) for y in annees]
    df = df[[c for c in cols if c in df.columns]]
    return df


def _dataframe_to_markdown(df: "pd.DataFrame") -> str:
    """Convert DataFrame to Markdown pipe table without requiring tabulate."""
    lines = []
    cols = list(df.columns)
    lines.append("| " + " | ".join(str(c) for c in cols) + " |")
    lines.append("|" + "|".join("---" for _ in cols) + "|")
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def table_tva_historique_md(
    annees: list[int] | None = None,
    start_year: int = DEFAULT_TVA_START_YEAR,
    parameters_dir: Path | None = None,
) -> str:
    """
    Return the TVA historique table as a Markdown pipe table.

    If annees is None, only years from start_year where at least one rate changed are shown.
    Use in Quarto:   print(table_tva_historique_md())
    """
    df = table_tva_historique(
        annees=annees, start_year=start_year, parameters_dir=parameters_dir
    )
    if df is None:
        return "*Tableau non disponible (installer PyYAML et pandas, et définir OPENFISCA_PARAMETERS_DIR ou installer openfisca-france).*"
    return _dataframe_to_markdown(df)


def table_tva_historique_df(
    annees: list[int] | None = None,
    start_year: int = DEFAULT_TVA_START_YEAR,
    parameters_dir: Path | None = None,
) -> "pd.DataFrame | None":
    """
    Return the TVA historique table as a pandas DataFrame for Quarto to render.

    If annees is None, only years from start_year where at least one rate changed are shown.
    In a Python chunk, simply:  table_tva_historique_df()
    Quarto will render the DataFrame as a table automatically.
    """
    return table_tva_historique(
        annees=annees, start_year=start_year, parameters_dir=parameters_dir
    )
