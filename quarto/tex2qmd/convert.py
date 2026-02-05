"""LaTeX→QMD conversion: headings, placeholders, tabular blocks, comments."""
import re


def extract_tex_comments(tex_content: str) -> list[tuple[str, str]]:
    """Extract full-line LaTeX comments and the anchor (next non-comment line) for positioning.

    Returns list of (comment_block, anchor). Consecutive % lines are merged into one block.
    Anchor is the next non-empty, non-comment line (stripped, truncated to 70 chars) for
    insertion before that text in the QMD. Empty anchor means comment was at end of file.
    """
    lines = tex_content.splitlines()
    result: list[tuple[str, str]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped.startswith("%"):
            i += 1
            continue
        # Start of a comment block: collect consecutive % lines
        block_lines: list[str] = []
        while i < len(lines) and lines[i].strip().startswith("%"):
            raw = lines[i]
            # Strip leading whitespace and single %
            s = raw.lstrip()
            if s.startswith("%"):
                # Remove one or more % and optional space
                rest = s.lstrip("%").lstrip()
                block_lines.append(rest)
            i += 1
        comment_text = "\n".join(block_lines).strip()
        if not comment_text:
            continue
        # Anchor: next non-empty, non-comment line
        anchor = ""
        while i < len(lines):
            next_line = lines[i].strip()
            if next_line and not next_line.startswith("%"):
                anchor = next_line[:70].strip()
                break
            i += 1
        result.append((comment_text, anchor))
    return result


def _escape_html_comment(text: str) -> str:
    """Escape so text can be used inside HTML comment <!-- ... -->."""
    return text.replace("--", "- -").replace(">", "&gt;")


def inject_qmd_comments(qmd_content: str, comments_with_anchors: list[tuple[str, str]]) -> str:
    """Insert HTML comments into QMD before the line containing each anchor.

    If anchor is empty or not found, the comment is appended at the end.
    """
    if not comments_with_anchors:
        return qmd_content
    qmd_lines = qmd_content.splitlines(keepends=True)
    # Build list of (insert_line_index, comment_text)
    inserts: list[tuple[int, str]] = []
    used_anchors: set[str] = set()
    for comment_text, anchor in comments_with_anchors:
        safe = _escape_html_comment(comment_text)
        comment_line = "<!-- " + safe + " -->\n"
        if not anchor:
            inserts.append((len(qmd_lines), comment_line))
            continue
        # Find first line that contains anchor (avoid reusing same anchor for multiple comments)
        anchor_key = anchor[:50]
        found = False
        for idx, qline in enumerate(qmd_lines):
            if anchor in qline or anchor_key in qline:
                inserts.append((idx, comment_line))
                found = True
                break
        if not found:
            inserts.append((len(qmd_lines), comment_line))
    # Apply inserts in reverse order so indices stay valid
    inserts.sort(key=lambda x: x[0], reverse=True)
    for idx, comment_line in inserts:
        qmd_lines.insert(idx, comment_line)
    return "".join(qmd_lines)


def extract_tex_label_captions(tex_content: str) -> dict[str, str]:
    """Extract label -> caption (title) from \\caption{...\\label{id}} and \\begin{tab|fig}[...]{...\\label{id}}.

    Returns a dict: label -> caption text (the title just before \\label in the .tex).
    Handles nested braces in the caption.
    """
    result: dict[str, str] = {}
    # Patterns that open a "title" block: \caption{ or \begin{tab}[...]{ or \begin{fig}[...]{
    open_pat = re.compile(
        r"\\caption\s*\{|"
        r"\\begin\s*\{\s*tab\s*\}\s*\[[^\]]*\]\s*\{|"
        r"\\begin\s*\{\s*fig\s*\}\s*\[[^\]]*\]\s*\{" 
    )
    i = 0
    while i < len(tex_content):
        m = open_pat.search(tex_content, i)
        if not m:
            break
        start = m.end()  # first char inside the opening {
        depth = 1
        j = start
        caption_start = j
        while j < len(tex_content) and depth > 0:
            if tex_content[j] == "\\" and j + 1 < len(tex_content):
                # Check for \label{...}
                rest = tex_content[j:]
                label_m = re.match(r"\\label\s*\{\s*([^}]+)\s*\}", rest)
                if label_m and depth == 1:
                    caption = tex_content[caption_start:j].strip()
                    # Strip trailing backslash and LaTeX cruft
                    caption = re.sub(r"\\\s*$", "", caption).strip()
                    if caption:
                        result[label_m.group(1).strip()] = caption
                    j += label_m.end()
                    continue
                # Check for \{ or \}
                if rest.startswith("\\{"):
                    j += 2
                    if depth == 1:
                        caption_start = j
                    depth += 1
                    continue
                if rest.startswith("\\}"):
                    j += 2
                    depth -= 1
                    continue
            if tex_content[j] == "{":
                depth += 1
                j += 1
                continue
            if tex_content[j] == "}":
                depth -= 1
                j += 1
                continue
            j += 1
        i = m.end()
    return result


def _latex_caption_to_plain(text: str) -> str:
    """Strip common LaTeX from caption for use as link text."""
    s = text.replace("~", " ").strip()
    # Remove backslash-commands: \'E, \er, \emph{...}, etc.
    s = re.sub(r"\\['`^\"~]\s*\{?([^}]*)\}?", r"\1", s)
    s = re.sub(r"\\er\b", "er", s)
    s = re.sub(r"\\emph\s*\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+\s*", " ", s)
    s = re.sub(r"\\", "", s)
    return " ".join(s.split())


def _normalize_anchor_id(anchor: str) -> str:
    """Normalize anchor id for HTML: spaces not allowed in id, use hyphens so links work."""
    return anchor.strip().replace(" ", "-")


def replace_ref_with_caption(qmd_content: str, label_to_caption: dict[str, str]) -> str:
    """Replace Pandoc ref link text (number or [\\label]) with the table/figure caption when available.

    Patterns: [1](#id){reference-type="ref" reference="id"} or
    [\\[id\\]](#id){reference-type="ref" reference="id"}.
    """
    if not label_to_caption:
        return qmd_content

    # [number or \[label\]](#anchor){reference-type="ref" reference="ref"} (attributes may span lines)
    # Linktext: allow \] and \[ (escaped brackets) or single-line non-bracket chars so we don't
    # match from a stray "[" in table content and eat the table.
    ref_re = re.compile(
        r'\[\s*(?P<linktext>(?:\\[\[\]]|[^\n\[\]])*?)\s*\]\s*\(#(?P<anchor>[^)]+)\)'
        r'\s*\{\s*reference-type\s*=\s*["\']ref["\']\s+reference\s*=\s*["\'](?P<ref>[^"\']+)["\']\s*\}',
        re.DOTALL,
    )

    def repl(m: re.Match) -> str:
        ref = m.group("ref").strip()
        anchor = m.group("anchor").strip()
        caption = label_to_caption.get(ref)
        if not caption:
            return m.group(0)
        # Use caption as link text; strip LaTeX for display; normalize anchor for HTML (no spaces in id)
        safe = _latex_caption_to_plain(caption)
        norm_anchor = _normalize_anchor_id(anchor)
        # Use normalized ref so Quarto generates href="#norm_anchor" matching our span id
        return f"[{safe}](#{norm_anchor}){{reference-type=\"ref\" reference=\"{norm_anchor}\"}}"

    return ref_re.sub(repl, qmd_content)


def remove_pandoc_table_attribute_blocks(content: str) -> str:
    """Replace raw []{#id label=\"id\"} blocks with minimal []{#id} so table ref links still work.

    Pandoc emits these after the caption inside ::: tab blocks. We keep the id so in-text
    refs (e.g. [Caption](#table:xyz)) have a target. Handles straight and curly quotes.
    """
    # Match " []{#id ...}" or "\n  []{#id ...}"; id can contain spaces (e.g. table:historique taxes sante)
    # Capture full id: from # until "label=" (handles both one-line and two-line blocks)
    # Replace with " []{#id}" so the anchor exists and ref links work
    def _keep_anchor(m: re.Match) -> str:
        anchor_id = m.group(1).strip()
        norm_id = _normalize_anchor_id(anchor_id)
        return f" []{{{norm_id}}}"

    content = re.sub(
        r'(?:\n\s*| )\[\]\{(#(?:(?!label\s*=).|\n)+?)\s*label\s*=\s*["\'\u201c\u201d][^"\'\u201c\u201d]*["\'\u201c\u201d]\s*\}',
        _keep_anchor,
        content,
    )
    # Restore ordinal "1er" in dates (Pandoc drops \er from "1\er janvier")
    content = re.sub(r"(\D)1\s+janvier\b", r"\g<1>1er janvier", content)
    # Ensure space before footnote ref when glued to word (avoids "solidarité11" in output)
    content = re.sub(r"([a-zA-Zàâäéèêëïîôùûüç])\[\^", r"\1 [^", content)
    return content


def shift_heading_levels(content: str) -> str:
    """Shift markdown heading levels by one so they become chapter sections (X.1, X.2)."""
    lines = content.split("\n")
    result = []
    for line in lines:
        match = re.match(r"^(#{1,6})\s(.*)$", line)
        if match:
            hashes, rest = match.groups()
            new_depth = min(len(hashes) + 1, 6)
            line = "#" * new_depth + " " + rest
        result.append(line)
    return "\n".join(result)


HEADING_RE = re.compile(r"^(#{1,6})\s")
PLACEHOLDER = "*[À rédiger.]*"


def add_placeholders_to_empty_sections(content: str, placeholder: str = PLACEHOLDER) -> str:
    """Insert placeholder in sections that have no body (heading then only blank lines or next heading)."""
    lines = content.split("\n")
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        result.append(line)
        if HEADING_RE.match(line):
            has_content = False
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if HEADING_RE.match(next_line):
                    break
                if next_line.strip():
                    has_content = True
                    break
                j += 1
            if not has_content:
                result.append("")
                result.append(placeholder)
                result.append("")
        i += 1
    return "\n".join(result)


TABULAR_BLOCK_RE = re.compile(
    r"::: tabular\s*\n(.*?)\n\s*:::",
    re.DOTALL,
)
COLSPEC_RE = re.compile(r"^\\\|(?:c\\\|)+\\?\s*")


def _clean_cell(cell: str) -> str:
    return cell.strip().rstrip("\\").strip()


def _is_data_row(cells: list[str]) -> bool:
    if not cells:
        return False
    first = _clean_cell(cells[0])
    if re.match(r"^(19|20)\d{2}$", first):
        return True
    return any("€" in c for c in cells)


def _fix_tabular_block(match: re.Match) -> str:
    inner = match.group(1)
    lines = [ln.strip() for ln in inner.split("\n") if ln.strip()]
    rows: list[list[str]] = []
    for line in lines:
        cells = [_clean_cell(c) for c in line.split("&")]
        if not any(cells):
            continue
        if not rows and cells:
            cell0 = COLSPEC_RE.sub("", cells[0]).strip()
            cell0 = re.sub(r"^c\\\|(?:c\\\|)*\s*", "", cell0)
            if cell0.startswith("\\***"):
                cell0 = "**" + cell0[4:]
            cells[0] = cell0
        rows.append(cells)
    if not rows:
        return ""

    ncols = max(len(r) for r in rows)
    for r in rows:
        while len(r) < ncols:
            r.append("")

    header_rows: list[list[str]] = []
    data_rows: list[list[str]] = []
    for row in rows:
        if not data_rows and _is_data_row(row):
            data_rows.append(row)
        elif data_rows:
            data_rows.append(row)
        else:
            header_rows.append(row)

    if not header_rows and data_rows:
        header_rows = [data_rows[0]]
        data_rows = data_rows[1:]

    if header_rows:
        header = []
        for c in range(ncols):
            for hr in header_rows:
                if c < len(hr) and hr[c].strip():
                    cell = hr[c].strip()
                    if cell.startswith("\\***"):
                        cell = "**" + cell[4:]
                    header.append(cell)
                    break
            else:
                header.append("")
        header_row = header[:ncols]
        while len(header_row) < ncols:
            header_row.append("")
    else:
        header_row = [""] * ncols

    if data_rows and not data_rows[0][0].strip() and ncols >= 2:
        next_year = None
        for dr in data_rows[1:]:
            if dr[0].strip() and re.match(r"^200[1-9]$", dr[0].strip()):
                next_year = dr[0].strip()
                break
        if next_year == "2001":
            data_rows[0][0] = "2000"

    non_empty_header = sum(1 for c in header_row if c.strip())
    has_fragment = any(
        len(c.strip()) <= 4 and c.strip() and not re.match(r"^\*\*[^*]+\*\*$", c.strip())
        or (c.strip().startswith("**") and c.strip().endswith("**") and len(c.strip()) < 10)
        for c in header_row
    )
    is_likely_malformatted = (
        ncols > 1
        and (non_empty_header < ncols / 2 or (non_empty_header == 1 and ncols > 2) or has_fragment)
    )
    TABLE_MALFORMED_COMMENT = "<!-- Tableau converti depuis LaTeX : en-têtes potentiellement incomplets ou mal fusionnés (vérifier et corriger si besoin). -->"

    def row_to_md(r: list[str]) -> str:
        return "| " + " | ".join(r) + " |"

    out = []
    if is_likely_malformatted:
        out.append(TABLE_MALFORMED_COMMENT)
    out.append(row_to_md(header_row))
    out.append("|" + "|".join(["---"] * ncols) + "|")
    for dr in data_rows:
        out.append(row_to_md(dr[:ncols]))
    return "\n".join(out)


def fix_tabular_blocks(content: str) -> str:
    """Replace ::: tabular ... ::: blocks (broken LaTeX-style) with markdown tables."""
    return TABULAR_BLOCK_RE.sub(_fix_tabular_block, content)
