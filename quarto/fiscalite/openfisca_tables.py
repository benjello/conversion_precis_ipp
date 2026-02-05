"""
Build tables from OpenFisca-France parameters for use in Quarto .qmd.

Parameters and units are loaded only from the installed openfisca-france package
via importlib.resources (no filesystem path). Requires: openfisca-france, pyyaml, pandas.

- Parameter YAMLs declare metadata.unit (e.g. '/1' for percent).
- units.yaml in the package defines short_label (e.g. '%'), ratio (e.g. True for /1).
- When format_value is None, table_from_parameters uses these to format cells (e.g. "20 %").

Generic usage:
  from openfisca_tables import table_from_parameters_df
  spec = [("parameters/.../taux_normal.yaml", "Normal"), ...]
  table_from_parameters_df(spec, row_column_name="Type de taux")  # units from package

Predefined TVA table:
  from openfisca_tables import table_tva_historique_df
  table_tva_historique_df()
"""

from __future__ import annotations

import importlib.resources
from typing import Any, Callable

try:
    import yaml
except ImportError:
    yaml = None

try:
    import pandas as pd
except ImportError:
    pd = None


# Default: first year to show; then only years where at least one value changes
DEFAULT_TVA_START_YEAR = 1972

# TVA table: (path in openfisca_france package, row label)
TVA_PARAMETERS_SPEC = [
    ("parameters/taxation_indirecte/tva/taux_particulier_super_reduit.yaml", "Super réduit"),
    ("parameters/taxation_indirecte/tva/taux_reduit.yaml", "Réduit"),
    ("parameters/taxation_indirecte/tva/taux_reduit_2.yaml", "Réduit supérieur"),
    ("parameters/taxation_indirecte/tva/taux_normal.yaml", "Normal"),
    ("parameters/taxation_indirecte/tva/taux_majore.yaml", "Majoré"),
]


def load_parameter_from_package(relative_path: str) -> dict[str, Any] | None:
    """
    Load a parameter YAML from the installed openfisca-france package.

    relative_path: path relative to the package root, e.g.
        "parameters/taxation_indirecte/tva/taux_normal.yaml"
    """
    if yaml is None:
        return None
    try:
        parts = relative_path.split("/")
        ref = importlib.resources.files("openfisca_france")
        for p in parts:
            ref = ref / p
        text = ref.read_text(encoding="utf-8")
        return yaml.safe_load(text)
    except Exception:
        return None


def load_units_from_package() -> dict[str, dict[str, Any]]:
    """
    Load units.yaml from the installed openfisca-france package.

    Returns a dict mapping unit name (e.g. '/1') to unit info (short_label, ratio, etc.).
    """
    if yaml is None:
        return {}
    try:
        ref = importlib.resources.files("openfisca_france") / "units.yaml"
        text = ref.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
        if not isinstance(data, list):
            return {}
        return {u["name"]: u for u in data if isinstance(u, dict) and "name" in u}
    except Exception:
        return {}


def _unit_short_label(unit_info: dict[str, Any] | None) -> str:
    """Extract short_label from a unit entry (handles string or {one, other} dict)."""
    if not unit_info:
        return ""
    sl = unit_info.get("short_label")
    if sl is None:
        return ""
    if isinstance(sl, str):
        return sl
    if isinstance(sl, dict):
        return sl.get("one", sl.get("other", ""))
    return ""


def _unit_short_label_for_year(unit_info: dict[str, Any] | None, year: int | None) -> str:
    """
    Get short_label for a unit, optionally for a given year (for date-dependent units like currency).
    """
    if not unit_info:
        return ""
    if "units" in unit_info and year is not None:
        # Date-dependent unit (e.g. currency): pick sub-unit in effect at start of year
        import datetime
        sub_units = unit_info["units"]
        if hasattr(sub_units, "keys"):
            year_start = datetime.date(year, 1, 1)
            candidates = [d for d in sub_units.keys() if hasattr(d, "year") and d <= year_start]
            if candidates:
                latest = max(candidates, key=lambda d: d.year if hasattr(d, "year") else 0)
                sub = sub_units.get(latest)
                if isinstance(sub, dict):
                    return _unit_short_label(sub)
    return _unit_short_label(unit_info)


def format_value_with_unit(
    value: float,
    param_data: dict[str, Any],
    units: dict[str, dict[str, Any]] | None = None,
    year: int | None = None,
) -> str:
    """
    Format a parameter value using the parameter's unit (metadata.unit) and units.yaml.

    If the unit has ratio=True (e.g. /1 for percent), value is displayed as value*100 + short_label.
    Otherwise value + short_label. Uses French decimal comma.
    For date-dependent units (e.g. currency), short_label is chosen for the given year.
    """
    if units is None:
        units = load_units_from_package()
    unit_name = (param_data.get("metadata") or {}).get("unit")
    unit_info = units.get(unit_name) if unit_name else None
    short_label = _unit_short_label_for_year(unit_info, year)
    ratio = unit_info.get("ratio", False) if unit_info else False

    if ratio:
        # e.g. 0.2 -> "20" or "20,5" + " %"
        s = f"{value * 100:.1f}".replace(".0", "").replace(".", ",")
    else:
        s = f"{value}".replace(".", ",")
    if short_label:
        return f"{s} {short_label}".strip()
    return s


def value_at_year(param_data: dict[str, Any], year: int) -> float | None:
    """
    Get parameter value in effect at the start of year.

    OpenFisca parameters have a "values" dict with date keys (YYYY-MM-DD or date)
    and values that are either a number or {"value": number}.
    """
    if not param_data or "values" not in param_data:
        return None

    def _date_key(d: Any) -> Any:
        return d if hasattr(d, "year") else str(d)

    dates = sorted(param_data["values"].keys(), key=_date_key, reverse=True)
    for d in dates:
        y = d.year if hasattr(d, "year") else int(str(d)[:4])
        if y <= year:
            v = param_data["values"][d]
            if isinstance(v, dict) and v.get("value") is not None:
                return float(v["value"])
            if isinstance(v, (int, float)):
                return float(v)
    return None


def _max_year_in_param_data(param_data_list: list[tuple[str, dict[str, Any]]]) -> int:
    """Latest year that appears in any of the parameter values."""
    import datetime
    out = datetime.date.today().year
    for _label, data in param_data_list:
        if not data or "values" not in data:
            continue
        for d in data["values"].keys():
            y = d.year if hasattr(d, "year") else int(str(d)[:4])
            out = max(out, y)
    return out


def _years_where_any_change(
    start_year: int,
    param_data_list: list[tuple[str, dict[str, Any]]],
    max_year: int | None = None,
) -> list[int]:
    """Years from start_year onward where at least one parameter value changed."""
    if not param_data_list:
        return []
    if max_year is None:
        max_year = _max_year_in_param_data(param_data_list)

    def profile(y: int) -> tuple[float | None, ...]:
        return tuple(value_at_year(data, y) for _label, data in param_data_list)

    change_years: list[int] = [start_year]
    for y in range(start_year + 1, max_year + 1):
        if profile(y) != profile(y - 1):
            change_years.append(y)
    return change_years


# Type for parameter spec: (package_relative_path, row_label)
ParameterSpec = tuple[str, str]


def table_from_parameters(
    parameters: list[ParameterSpec],
    row_column_name: str = "Paramètre",
    annees: list[int] | None = None,
    start_year: int | None = None,
    format_value: Callable[[float], str] | None = None,
) -> "pd.DataFrame | None":
    """
    Build a table from a list of OpenFisca parameters (generic).

    parameters: list of (path_in_package, row_label), e.g.
        [("parameters/.../taux_normal.yaml", "Normal"), ...]
    row_column_name: name of the first column (row labels).
    annees: years to show as columns. If None, years from start_year where at least
        one parameter changes.
    start_year: first year when annees is None (required if annees is None).
    format_value: optional formatter for numeric cells, e.g. lambda v: f"{v*100:.1f}".replace(".", ",").
        If None, uses str(value).

    Returns a DataFrame with row_column_name + one column per year. Missing values as "–".
    """
    if pd is None:
        return None

    param_data_list: list[tuple[str, dict[str, Any]]] = []
    for path, label in parameters:
        data = load_parameter_from_package(path)
        if data is None:
            continue
        param_data_list.append((label, data))

    if not param_data_list:
        return None

    if annees is None:
        if start_year is None:
            return None
        annees = _years_where_any_change(start_year, param_data_list)

    # When format_value is None, use parameter units (metadata.unit + units.yaml)
    use_units = format_value is None
    if use_units:
        units = load_units_from_package()

    rows: list[dict[str, Any]] = []
    for label, data in param_data_list:
        row: dict[str, Any] = {row_column_name: label}
        for year in annees:
            val = value_at_year(data, year)
            if val is not None:
                if use_units:
                    row[str(year)] = format_value_with_unit(val, data, units, year)
                else:
                    row[str(year)] = format_value(val)
            else:
                row[str(year)] = "–"
        rows.append(row)

    df = pd.DataFrame(rows)
    cols = [row_column_name] + [str(y) for y in annees]
    df = df[[c for c in cols if c in df.columns]]
    return df


def table_from_parameters_md(
    parameters: list[ParameterSpec],
    row_column_name: str = "Paramètre",
    annees: list[int] | None = None,
    start_year: int | None = None,
    format_value: Callable[[float], str] | None = None,
    unavailable_message: str = "*Tableau non disponible (installer openfisca-france, pyyaml et pandas).*",
) -> str:
    """Return the table as a Markdown pipe table."""
    df = table_from_parameters(
        parameters=parameters,
        row_column_name=row_column_name,
        annees=annees,
        start_year=start_year,
        format_value=format_value,
    )
    if df is None:
        return unavailable_message
    return _dataframe_to_markdown(df)


def table_from_parameters_df(
    parameters: list[ParameterSpec],
    row_column_name: str = "Paramètre",
    annees: list[int] | None = None,
    start_year: int | None = None,
    format_value: Callable[[float], str] | None = None,
) -> "pd.DataFrame | None":
    """Return the table as a pandas DataFrame for Quarto to render."""
    return table_from_parameters(
        parameters=parameters,
        row_column_name=row_column_name,
        annees=annees,
        start_year=start_year,
        format_value=format_value,
    )


def _dataframe_to_markdown(df: "pd.DataFrame") -> str:
    """Convert DataFrame to Markdown pipe table."""
    lines = []
    cols = list(df.columns)
    lines.append("| " + " | ".join(str(c) for c in cols) + " |")
    lines.append("|" + "|".join("---" for _ in cols) + "|")
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join(lines)


# --- TVA table (predefined use of table_from_parameters) ---
# Uses metadata.unit and units.yaml from the package for formatting (e.g. "20 %").


def table_tva_historique(
    annees: list[int] | None = None,
    start_year: int = DEFAULT_TVA_START_YEAR,
) -> "pd.DataFrame | None":
    """
    Build the "Évolution des taux de TVA en France" table from openfisca-france parameters.
    Unit formatting (e.g. %) comes from parameter metadata and units.yaml.
    """
    return table_from_parameters(
        parameters=TVA_PARAMETERS_SPEC,
        row_column_name="Type de taux",
        annees=annees,
        start_year=start_year,
        format_value=None,  # use units from package
    )


def table_tva_historique_md(
    annees: list[int] | None = None,
    start_year: int = DEFAULT_TVA_START_YEAR,
) -> str:
    """Return the TVA historique table as a Markdown pipe table."""
    return table_from_parameters_md(
        parameters=TVA_PARAMETERS_SPEC,
        row_column_name="Type de taux",
        annees=annees,
        start_year=start_year,
        format_value=None,
    )


def table_tva_historique_df(
    annees: list[int] | None = None,
    start_year: int = DEFAULT_TVA_START_YEAR,
) -> "pd.DataFrame | None":
    """Return the TVA historique table as a pandas DataFrame for Quarto. In a chunk: table_tva_historique_df()"""
    return table_tva_historique(annees=annees, start_year=start_year)
