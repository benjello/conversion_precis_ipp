"""Legislation: in-text patterns → [@key], and .bib generation. Single source of truth in LEGISLATION_ENTRIES."""
from pathlib import Path

# Each entry: key, patterns, title, issued (YYYY-MM-DD), optional shorthand, optional url (Légifrance LODA).
# Longer patterns first. URL: Légifrance LODA (legifrance.gouv.fr/loda/id/JORFTEXT...).
LEGISLATION_ENTRIES: list[dict] = [
    {"key": "loi1914", "patterns": ["loi du 15 juillet 1914"], "title": "Loi du 15 juillet 1914", "issued": "1914-07-15", "shorthand": "Instauration de l'impôt sur le revenu"},
    {"key": "loi1920", "patterns": ["loi du 25 juin 1920"], "title": "Loi du 25 juin 1920", "issued": "1920-06-25", "shorthand": "Pérennisation de l'impôt sur le revenu"},
    {"key": "loi1942", "patterns": ["loi du 14 mars 1942"], "title": "Loi du 14 mars 1942", "issued": "1942-03-14", "shorthand": "Réforme fiscale (Vichy)"},
    {"key": "loi1790", "patterns": ["loi des 5 et 19 décembre 1790"], "title": "Loi des 5 et 19 décembre 1790", "issued": "1790-12-19", "shorthand": "Droits d'enregistrement"},
    {"key": "loi1901", "patterns": ["loi du 25 février 1901"], "title": "Loi du 25 février 1901", "issued": "1901-02-25", "shorthand": "Impôt progressif sur les successions"},
    {"key": "loi2007-22aout", "patterns": ["loi du 22 août 2007"], "title": "Loi du 22 août 2007", "issued": "2007-08-22", "shorthand": "Exonération droits succession conjoint"},
    {"key": "loi2007-21aout", "patterns": ["loi du 21 août 2007"], "title": "Loi du 21 août 2007", "issued": "2007-08-21", "shorthand": "TEPA (travail, emploi, pouvoir d'achat)", "url": "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000278649"},
    {"key": "loi2011-900", "patterns": ["Loi n° 2011-900 du 29 juillet 2011", "loi n° 2011-900"], "title": "Loi n° 2011-900 du 29 juillet 2011 de finances rectificative", "issued": "2011-07-29", "shorthand": "Finances rectificative 2011"},
    {"key": "loi1998", "patterns": ["loi de finances de 1998", "loi 97-1269"], "title": "Loi de finances pour 1998", "issued": "1997-12-30", "shorthand": "LFI 1998"},
    {"key": "loi2001", "patterns": ["loi de finances de 2001", "loi de finances pour 2001", "loi de finances pour 2001 (-1352"], "title": "Loi de finances pour 2001", "issued": "2000-12-30", "shorthand": "LFI 2001"},
    {"key": "loi2006-rectif", "patterns": ["loi de finances rectificative de 2006"], "title": "Loi de finances rectificative pour 2006", "issued": "2006-12-30", "shorthand": "LF rectificative 2006"},
    {"key": "loi2009", "patterns": ["loi de finances de 2009"], "title": "Loi de finances pour 2009", "issued": "2008-12-27", "shorthand": "LFI 2009"},
    {"key": "loi2009-rectif", "patterns": ["loi de finances rectificative du 20/04/2009", "loi de finances rectificative du 20 avril 2009"], "title": "Loi de finances rectificative du 20 avril 2009", "issued": "2009-04-20", "shorthand": "LF rectificative 2009"},
    {"key": "loi2010", "patterns": ["loi de finances 2010", "loi de finances pour 2010"], "title": "Loi de finances pour 2010", "issued": "2009-12-30", "shorthand": "LFI 2010", "url": "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000021557902"},
    {"key": "loi2010-1657", "patterns": ["loi 2010-1657 du 29 décembre 2010", "article 190 de la loi 2010-1657"], "title": "Loi n° 2010-1657 du 29 décembre 2010 de finances pour 2011", "issued": "2010-12-29", "shorthand": "LFI 2011"},
    {"key": "loi2013", "patterns": ["loi de finances pour 2013", "projet de loi de finances pour 2013"], "title": "Loi de finances pour 2013", "issued": "2012-12-29", "shorthand": "LFI 2013"},
    {"key": "loi2014", "patterns": ["loi de finances pour 2014"], "title": "Loi de finances pour 2014", "issued": "2013-12-29", "shorthand": "LFI 2014"},
    {"key": "loi1999", "patterns": ["loi du 27 juillet 1999"], "title": "Loi du 27 juillet 1999", "issued": "1999-07-27", "shorthand": "Taxe sur les tabacs"},
]


def _link_legislation_one(content: str, key: str, pattern: str) -> str:
    citation_suffix = f" [@{key}]"
    placeholder = "\uE000LEGREF\uE001" + key + "\uE002"
    content = content.replace(pattern + citation_suffix, placeholder)
    content = content.replace(pattern, pattern + citation_suffix)
    content = content.replace(placeholder, pattern + citation_suffix)
    return content


def link_legislation_citations(content: str, entries: list[dict]) -> str:
    """Replace legislation phrases with 'phrase [@key]'. Longer patterns first."""
    pairs: list[tuple[str, str]] = []
    for e in entries:
        for p in e["patterns"]:
            pairs.append((e["key"], p))
    pairs.sort(key=lambda x: -len(x[1]))
    for key, pattern in pairs:
        content = _link_legislation_one(content, key, pattern)
    return content


def write_legislation_bib(path: Path, entries: list[dict]) -> None:
    """Write legislation.bib from LEGISLATION_ENTRIES. Uses @misc with type=legislation for CSL."""
    lines = [
        "% Textes de loi — généré par le package quarto/tex2qmd (tex2qmd-fiscalite).",
        "% Ne pas éditer à la main ; modifier LEGISLATION_ENTRIES dans quarto/tex2qmd/legislation.py.",
        "",
    ]
    for e in entries:
        k = e["key"]
        title = e["title"].replace("\\", "\\\\").replace('"', '\\"')
        issued = e["issued"]
        shorthand = e.get("shorthand", "").replace("\\", "\\\\").replace('"', '\\"')
        url = e.get("url", "")
        lines.append(f'@misc{{{k},')
        lines.append(f'  type = {{legislation}},')
        lines.append(f'  title = {{{title}}},')
        lines.append(f'  date = {{{issued}}},')
        lines.append(f'  issued = {{{issued}}},')
        if shorthand:
            lines.append(f'  note = {{{shorthand}}},')
        if url:
            lines.append(f'  url = {{{url}}},')
        lines.append("}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
