"""Generate Quarto fiscalité book from LaTeX sources. Source dir: TEX2QMD_SOURCE_DIR."""
from pathlib import Path
import re
import subprocess
import sys

from . import IPP_ROOT, get_source_dir
from .convert import (
    shift_heading_levels,
    add_placeholders_to_empty_sections,
    fix_tabular_blocks,
    extract_tex_comments,
    inject_qmd_comments,
    extract_tex_label_captions,
    replace_ref_with_caption,
    remove_pandoc_table_attribute_blocks,
    prefix_footnote_labels,
)
from .legislation import (
    LEGISLATION_ENTRIES,
    link_legislation_citations,
    write_legislation_bib,
)

OUT_DIR = IPP_ROOT / "quarto" / "fiscalite"

# Chapter order and titles (from Guide IPP - fiscalite.tex)
CHAPTERS = [
    ("1-Presentation.tex", "presentation.qmd", "Présentation générale"),
    ("2-Cotisations.tex", "cotisations.qmd", "Les cotisations sociales"),
    ("3-Revenu.tex", "revenu.qmd", "Les impôts sur le revenu"),
    ("4-Patrimoine.tex", "patrimoine.qmd", "Les impôts sur le patrimoine"),
    ("5-Indirecte.tex", "indirecte.qmd", "La fiscalité indirecte"),
    ("8-Glossaire.tex", "glossaire.qmd", "Glossaire"),
]


def main() -> None:
    source_dir = get_source_dir()
    source_dir.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "chapters").mkdir(parents=True, exist_ok=True)

    if not source_dir.exists():
        print(f"Source directory not found: {source_dir}", file=sys.stderr)
        print("Set TEX2QMD_SOURCE_DIR to the LaTeX chapters directory.", file=sys.stderr)
        sys.exit(1)

    for tex_name, qmd_name, title in CHAPTERS:
        tex_path = source_dir / tex_name
        chapter_name = qmd_name.replace(".qmd", "")
        chapter_dir = OUT_DIR / "chapters" / chapter_name
        chapter_dir.mkdir(parents=True, exist_ok=True)
        qmd_path = chapter_dir / qmd_name

        if not tex_path.exists():
            print(f"Skip (missing): {tex_path}")
            continue

        # Match pandoc's encoding so anchor text finds the right line in qmd (pandoc uses latin1 when tex is not UTF-8)
        try:
            tex_content = tex_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            tex_content = tex_path.read_text(encoding="latin-1")
        comments_with_anchors = extract_tex_comments(tex_content)

        result = subprocess.run(
            [
                "pandoc",
                str(tex_path),
                "-f", "latex",
                "-t", "markdown",
                "-o", str(qmd_path),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Pandoc failed for {tex_name}: {result.stderr}", file=sys.stderr)
            continue

        content = qmd_path.read_text(encoding="utf-8", errors="replace")
        label_to_caption = extract_tex_label_captions(tex_content)
        content = replace_ref_with_caption(content, label_to_caption)
        content = inject_qmd_comments(content, comments_with_anchors)
        content = remove_pandoc_table_attribute_blocks(content)
        content = shift_heading_levels(content)
        content = add_placeholders_to_empty_sections(content)
        content = fix_tabular_blocks(content)
        content = prefix_footnote_labels(content, chapter_name)
        content = link_legislation_citations(content, LEGISLATION_ENTRIES)
        if qmd_name == "indirecte.qmd":
            content = inject_openfisca_tables_indirecte(content)
        header = f"---\ntitle: \"{title}\"\n---\n\n"
        qmd_path.write_text(header + content, encoding="utf-8")
        print(f"OK: {tex_name} -> {qmd_name}")

    write_legislation_bib(OUT_DIR / "legislation.bib", LEGISLATION_ENTRIES)
    print("OK: legislation.bib written")

    print(f"Done. To render HTML + PDF: cd {OUT_DIR} && quarto render")


def inject_openfisca_tables_indirecte(content: str) -> str:
    sys_path_chunk = (
        "```{python}\n"
        "#| include: false\n"
        "# OpenFisca tables import path\n"
        "import sys\n"
        "from pathlib import Path\n"
        "\n"
        "cwd = Path.cwd().resolve()\n"
        "# Add book folder that contains chapters/\n"
        "for candidate in [cwd, *cwd.parents]:\n"
        "    if (candidate / \"chapters\" / \"__init__.py\").exists():\n"
        "        if str(candidate) not in sys.path:\n"
        "            sys.path.insert(0, str(candidate))\n"
        "        break\n"
        "# Add repo root (for quarto.openfisca_tables.core)\n"
        "for candidate in [cwd, *cwd.parents]:\n"
        "    if (candidate / \"quarto\" / \"openfisca_tables\" / \"core.py\").exists():\n"
        "        if str(candidate) not in sys.path:\n"
        "            sys.path.insert(0, str(candidate))\n"
        "        break\n"
        "```\n"
        "\n"
    )
    tva_chunk = (
        "```{python}\n"
        "#| label: historique-taux-tva\n"
        "#| tbl-cap: \"Évolution des taux de TVA en France depuis 1972.\"\n"
        "#| cap-location: top\n"
        "#| echo: false\n"
        "from quarto.openfisca_tables.core import get_table_or_static\n"
        "from chapters.indirecte.openfisca_tables import table_tva_historique_df\n"
        "get_table_or_static(table_tva_historique_df, \"chapters/indirecte/tables/tva_historique_static.md\").style.hide(axis=\"index\")\n"
        "```\n"
    )
    tabac_chunk = (
        "```{python}\n"
        "#| label: taxes-tabac\n"
        "#| tbl-cap: \"Évolution des taux normaux du droit de consommation sur les tabacs (par type).\"\n"
        "#| cap-location: top\n"
        "#| echo: false\n"
        "from quarto.openfisca_tables.core import get_table_or_static\n"
        "from chapters.indirecte.openfisca_tables import table_tabac_taux_normal_df\n"
        "get_table_or_static(table_tabac_taux_normal_df, \"chapters/indirecte/tables/tabac_taux_normal_static.md\").style.hide(axis=\"index\")\n"
        "```\n"
    )
    alcools_chunk = (
        "```{python}\n"
        "#| label: taxes-alcools\n"
        "#| tbl-cap: \"Évolution des droits par type de boisson (€/hl ou assimilé).\"\n"
        "#| cap-location: top\n"
        "#| echo: false\n"
        "from quarto.openfisca_tables.core import get_table_or_static\n"
        "from chapters.indirecte.openfisca_tables import table_alcools_droits_df\n"
        "get_table_or_static(table_alcools_droits_df, \"chapters/indirecte/tables/alcools_droits_static.md\").style.hide(axis=\"index\")\n"
        "```\n"
    )

    if "OpenFisca tables import path" in content:
        content = re.sub(
            r"```{python}\n#\| include: false\n# OpenFisca tables import path.*?```\n\n",
            sys_path_chunk,
            content,
            flags=re.DOTALL,
        )
    else:
        content = sys_path_chunk + content

    content = _replace_table_block_by_id(content, "table:historique-taux-tva", tva_chunk)
    content = _replace_table_block_by_id(content, "table:taxes-tabac", tabac_chunk)
    content = _replace_table_block_by_id(content, "table:taxes-alcools", alcools_chunk)

    # Update tabac sentence to match the new OpenFisca table
    content = re.sub(
        r"tableau\s*\[Fiscalité applicable aux tabacs au 1er janvier 2013\.\]\(#table:taxes-tabac\)\{reference-type=\"ref\" reference=\"table:taxes-tabac\"\}.*?tabacs\.\s*\\?\n",
        "tableau [Évolution des taux normaux du droit de consommation sur les tabacs (par type).](#table:taxes-tabac){reference-type=\"ref\" reference=\"table:taxes-tabac\"} résume les changements intervenus sur les taux.\n",
        content,
        flags=re.DOTALL,
    )

    # Update alcools sentence to match the new OpenFisca table; insert chunk if missing
    if "table:taxes-alcools" in content:
        content = re.sub(
            r"tableau\s*\[Fiscalité applicable aux alcools au 1er janvier 2013\.\]\(#table:taxes-alcools\)\{reference-type=\"ref\" reference=\"table:taxes-alcools\"\}.*?2013\.\s*\\?\n",
            "tableau [Évolution des droits par type de boisson (€/hl ou assimilé).](#table:taxes-alcools){reference-type=\"ref\" reference=\"table:taxes-alcools\"} présente l'évolution des droits applicables aux boissons alcoolisées.\n",
            content,
            flags=re.DOTALL,
        )
        if "table_alcools_droits_df" not in content:
            content = content.replace(
                "tableau [Évolution des droits par type de boisson (€/hl ou assimilé).](#table:taxes-alcools){reference-type=\"ref\" reference=\"table:taxes-alcools\"} présente l'évolution des droits applicables aux boissons alcoolisées.\n",
                "tableau [Évolution des droits par type de boisson (€/hl ou assimilé).](#table:taxes-alcools){reference-type=\"ref\" reference=\"table:taxes-alcools\"} présente l'évolution des droits applicables aux boissons alcoolisées.\n"
                + alcools_chunk,
            )

    return content


def _replace_table_block_by_id(content: str, table_id: str, replacement: str) -> str:
    lines = content.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("::: tab") or line.startswith(":::: tab"):
            j = i + 1
            while j < len(lines) and lines[j].strip() not in (":::", "::::"):
                j += 1
            if j < len(lines):
                block_lines = lines[i : j + 1]
                block_text = "\n".join(block_lines)
                if table_id in block_text:
                    out.append(replacement.rstrip("\n"))
                else:
                    out.extend(block_lines)
                i = j + 1
                continue
        out.append(line)
        i += 1
    return "\n".join(out)


if __name__ == "__main__":
    main()
