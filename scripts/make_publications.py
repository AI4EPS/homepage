#!/usr/bin/env python3
"""Generate docs/publication.md from docs/publications.bib.

The bibliography is not maintained here. It is copied from the CV, whose own
pub.bib is regenerated from a Google Scholar export by CV/make_pub.py, so the
chain from Scholar to this website is reproducible end to end:

    Google Scholar  ->  CV/pub.bib  ->  docs/publications.bib  ->  docs/publication.md

To refresh the website after updating the CV:

    python scripts/make_publications.py --from-cv

Do NOT hand-edit docs/publication.md; it is overwritten. Change the formatting
here and re-run.
"""

import argparse
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BIB = ROOT / "docs" / "publications.bib"
OUT = ROOT / "docs" / "publication.md"
LINKS = ROOT / "docs" / "publication_links.json"
CV_BIB = Path.home() / "Library/CloudStorage/Dropbox/Apps/Overleaf/CV/pub.bib"

# The name to bold in every author list.
ME = ("Zhu", "Weiqiang")

# LaTeX escapes that survive into pub.bib, longest pattern first.
ACCENTS = {
    r"\"{u}": "ü", r"\"{o}": "ö", r"\"{a}": "ä", r"\"{i}": "ï", r'\"{\i}': "ï",
    r"\'{e}": "é", r"\'{a}": "á", r"\'{i}": "í", r"\'{\i}": "í", r"\'{o}": "ó",
    r"\'{u}": "ú", r"\'{c}": "ć", r"\'{n}": "ń", r"\'{s}": "ś",
    r"\`{e}": "è", r"\`{a}": "à", r"\`{i}": "ì",
    r"\^{e}": "ê", r"\^{a}": "â", r"\^{o}": "ô", r"\^{i}": "î",
    r"\~{n}": "ñ", r"\~{a}": "ã", r"\~{o}": "õ",
    r"\c{c}": "ç", r"\v{s}": "š", r"\v{c}": "č", r"\v{z}": "ž",
    r"\o{}": "ø", r"\ss{}": "ß",
    r"\&": "&", r"\_": "_", r"\%": "%", r"\$": "$",
}


def delatex(s: str) -> str:
    for pat, rep in ACCENTS.items():
        s = s.replace(pat, rep)
    s = s.replace("---", "—").replace("--", "–")
    s = re.sub(r"[{}]", "", s)
    # A bare backtick would open an inline-code span in Markdown; in this
    # bibliography it only ever stands in for the Hawaiian okina.
    return s.replace("`", "ʻ").strip()


def parse_bib(text: str) -> list[dict]:
    """Return one dict per entry, with a 'key' and 'type' plus its fields."""
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,]+),(.*?)\n\}", text, re.S):
        etype, key, body = m.group(1).lower(), m.group(2).strip(), m.group(3)
        fields = {"key": key, "type": etype}
        for fm in re.finditer(r"(\w+)\s*=\s*\{(.*?)\}\s*,?\s*(?=\n\s*\w+\s*=|\Z)", body, re.S):
            fields[fm.group(1).lower()] = " ".join(fm.group(2).split())
        entries.append(fields)
    return entries


def format_authors(raw: str) -> str:
    """'Zhu, Weiqiang and Wang, Haoyu' -> 'Zhu, W., Wang, H.' with me bolded."""
    out = []
    for name in raw.split(" and "):
        name = name.strip()
        if not name or name.lower() in {"others", "et al."}:
            out.append("et al.")
            continue
        if "," in name:
            last, first = (p.strip() for p in name.split(",", 1))
        else:  # "Weiqiang Zhu" -> last token is the surname
            parts = name.split()
            last, first = parts[-1], " ".join(parts[:-1])
        initials = " ".join(f"{p[0]}." for p in first.replace(".", " ").split() if p)
        shown = f"{delatex(last)}, {initials}" if initials else delatex(last)
        if (last, first.split()[0] if first else "") == ME:
            shown = f"**{shown}**"
        out.append(shown)
    return ", ".join(out)


def venue(e: dict) -> str:
    if e["type"] == "phdthesis":
        return f"Ph.D. Thesis, {delatex(e.get('school', 'Stanford University'))}"
    return delatex(e.get("journal") or e.get("booktitle") or "")


def is_preprint(e: dict) -> bool:
    return "arxiv" in (e.get("journal", "") + e.get("eprint", "")).lower()


def render(e: dict, links: dict) -> str:
    """One bullet: authors (year). Title. *Venue*. doi · pdf

    Preprints use their registered arXiv DOI (10.48550/arXiv.NNNN) so that every
    entry carries the same two links rather than a bare arXiv identifier.
    """
    line = f"- {format_authors(e.get('author', ''))} ({e.get('year', 'n.d.')}). "
    line += f"{delatex(e.get('title', ''))}. "

    rec = links.get(e["key"], {})
    doi = rec.get("doi", "")
    if is_preprint(e):
        m = re.search(r"arXiv:(\S+)", e.get("journal", ""))
        line += "*arXiv preprint*."
        doi = doi or (f"10.48550/arXiv.{m.group(1)}" if m else "")
    elif (v := venue(e)):
        line += f"*{v}*."

    extra = []
    if doi:
        extra.append(f"[doi](https://doi.org/{doi})")
    if rec.get("asset"):
        extra.append(f"[pdf]({rec['asset']})")
    if extra:
        line += " " + " &middot; ".join(extra)
    return line.rstrip()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--from-cv", action="store_true",
                    help=f"copy {CV_BIB} over docs/publications.bib first")
    args = ap.parse_args()

    if args.from_cv:
        if not CV_BIB.exists():
            raise SystemExit(f"CV bibliography not found: {CV_BIB}")
        shutil.copyfile(CV_BIB, BIB)
        print(f"copied {CV_BIB} -> {BIB}")

    entries = parse_bib(BIB.read_text(encoding="utf-8"))
    if not entries:
        raise SystemExit(f"no entries parsed from {BIB}")
    links = json.loads(LINKS.read_text()) if LINKS.exists() else {}
    lines = [
        "# Publications",
        "",
        "[Google Scholar](https://scholar.google.com/citations?user=ApsNeMkAAAAJ&hl=en)"
        " &middot; [ResearchGate](https://www.researchgate.net/profile/Zhu-Weiqiang/publications)",
        "",
        "If you cannot reach a paper through your library, email me and I will send a copy.",
        "",
    ]

    for year in sorted({e.get("year", "") for e in entries}, reverse=True):
        group = sorted((e for e in entries if e.get("year", "") == year),
                       key=lambda e: e.get("author", "").lower())
        lines += [f"## {year}", ""] + [render(e, links) for e in group] + [""]

    OUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    npdf = sum(1 for e in entries if links.get(e["key"], {}).get("asset"))
    print(f"wrote {OUT}: {len(entries)} entries across "
          f"{len({e.get('year', '') for e in entries})} years, {npdf} with a PDF link")


if __name__ == "__main__":
    main()
