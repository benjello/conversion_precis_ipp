"""
OpenFisca tables for the "Fiscalité indirecte" chapter.
"""

from __future__ import annotations

from quarto.openfisca_tables.core import (
    ParameterSpec,
    table_from_parameters,
    table_from_parameters_df,
    table_from_parameters_md,
)

__all__ = [
    "ParameterSpec",
    "TVA_PARAMETERS_SPEC",
    "TABAC_TAUX_NORMAL_SPEC",
    "ALCOOLS_DROITS_SPEC",
    "table_tva_historique",
    "table_tva_historique_md",
    "table_tva_historique_df",
    "table_tabac_taux_normal",
    "table_tabac_taux_normal_df",
    "table_alcools_droits",
    "table_alcools_droits_df",
]


# Default: first year to show; then only years where at least one value changes
DEFAULT_TVA_START_YEAR = 1972
DEFAULT_TABAC_START_YEAR = 1991
DEFAULT_ALCOOLS_START_YEAR = 1991

# TVA table: (path in openfisca_france package, row label)
TVA_PARAMETERS_SPEC: list[ParameterSpec] = [
    ("parameters/taxation_indirecte/tva/taux_particulier_super_reduit.yaml", "Super réduit"),
    ("parameters/taxation_indirecte/tva/taux_reduit.yaml", "Réduit"),
    ("parameters/taxation_indirecte/tva/taux_reduit_2.yaml", "Réduit supérieur"),
    ("parameters/taxation_indirecte/tva/taux_normal.yaml", "Normal"),
    ("parameters/taxation_indirecte/tva/taux_majore.yaml", "Majoré"),
]

# Tabac: taux normal du droit de consommation par type (evolution over time)
TABAC_TAUX_NORMAL_SPEC: list[ParameterSpec] = [
    ("parameters/taxation_indirecte/taxes_tabacs/taux_normal/cigarettes.yaml", "Cigarettes"),
    ("parameters/taxation_indirecte/taxes_tabacs/taux_normal/cigares.yaml", "Cigares"),
    ("parameters/taxation_indirecte/taxes_tabacs/taux_normal/tabac_rouler.yaml", "Tabac à rouler"),
]

# Alcools: droits (currency/hl) par type de boisson (evolution over time)
ALCOOLS_DROITS_SPEC: list[ParameterSpec] = [
    ("parameters/taxation_indirecte/alcools_autres_boissons/alcools_fermentes/vins_tranquilles.yaml", "Vins tranquilles"),
    ("parameters/taxation_indirecte/alcools_autres_boissons/alcools_fermentes/cidres_poires_hydromels.yaml", "Cidres, poirés, hydromels"),
    ("parameters/taxation_indirecte/alcools_autres_boissons/bieres/autres_bieres.yaml", "Bières"),
    ("parameters/taxation_indirecte/alcools_autres_boissons/autres_alcools/autres_alcools.yaml", "Alcools"),
]


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


# --- Tabac table (taux normal droit de consommation par type, evolution) ---


def table_tabac_taux_normal(
    annees: list[int] | None = None,
    start_year: int = DEFAULT_TABAC_START_YEAR,
) -> "pd.DataFrame | None":
    """Évolution des taux normaux du droit de consommation sur les tabacs (par type). Units from package."""
    return table_from_parameters(
        parameters=TABAC_TAUX_NORMAL_SPEC,
        row_column_name="Type de tabac",
        annees=annees,
        start_year=start_year,
        format_value=None,
    )


def table_tabac_taux_normal_df(
    annees: list[int] | None = None,
    start_year: int = DEFAULT_TABAC_START_YEAR,
) -> "pd.DataFrame | None":
    """Return the tabac taux normal table as a DataFrame for Quarto."""
    return table_tabac_taux_normal(annees=annees, start_year=start_year)


# --- Alcools table (droits par type de boisson, evolution) ---


def table_alcools_droits(
    annees: list[int] | None = None,
    start_year: int = DEFAULT_ALCOOLS_START_YEAR,
) -> "pd.DataFrame | None":
    """Évolution des droits (€/hl ou assimilé) par type de boisson. Units from package."""
    return table_from_parameters(
        parameters=ALCOOLS_DROITS_SPEC,
        row_column_name="Type de boisson",
        annees=annees,
        start_year=start_year,
        format_value=None,
    )


def table_alcools_droits_df(
    annees: list[int] | None = None,
    start_year: int = DEFAULT_ALCOOLS_START_YEAR,
) -> "pd.DataFrame | None":
    """Return the alcools droits table as a DataFrame for Quarto."""
    return table_alcools_droits(annees=annees, start_year=start_year)
