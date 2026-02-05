"""Generate Quarto fiscalité book from LaTeX sources. Source dir: TEX2QMD_SOURCE_DIR."""
from pathlib import Path
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

    if not source_dir.exists():
        print(f"Source directory not found: {source_dir}", file=sys.stderr)
        print("Set TEX2QMD_SOURCE_DIR to the LaTeX chapters directory.", file=sys.stderr)
        sys.exit(1)

    for tex_name, qmd_name, title in CHAPTERS:
        tex_path = source_dir / tex_name
        qmd_path = OUT_DIR / qmd_name

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
        content = link_legislation_citations(content, LEGISLATION_ENTRIES)
        header = f"---\ntitle: \"{title}\"\n---\n\n"
        qmd_path.write_text(header + content, encoding="utf-8")
        print(f"OK: {tex_name} -> {qmd_name}")

    write_legislation_bib(OUT_DIR / "legislation.bib", LEGISLATION_ENTRIES)
    print("OK: legislation.bib written")

    print(f"Done. To render HTML + PDF: cd {OUT_DIR} && quarto render")
