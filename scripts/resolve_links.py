#!/usr/bin/env python3
"""Resolve a DOI and an open-access PDF link for every entry in docs/publications.bib.

pub.bib carries no identifiers, so each title is matched against Crossref and the
winning DOI is checked against Unpaywall for a legally hosted open-access copy.
Results are cached in docs/publication_links.json and read by make_publications.py,
so the slow network pass runs only when new papers appear.

    python scripts/resolve_links.py            # fill in entries missing from the cache
    python scripts/resolve_links.py --refresh  # re-resolve everything

Only Unpaywall's own best_oa_location is used, which points at the publisher's or a
repository's copy. Nothing is rehosted, so no publisher's redistribution terms apply.
"""

import argparse
import difflib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_publications import BIB, delatex, parse_bib  # noqa: E402

CACHE = Path(__file__).resolve().parent.parent / "docs" / "publication_links.json"
MAILTO = "zhuwq@berkeley.edu"
MIN_SCORE = 0.90  # title-similarity floor; Crossref always answers, so score it


def get(url: str, timeout: int = 30):
    req = urllib.request.Request(url, headers={"User-Agent": f"AI4EPS-homepage (mailto:{MAILTO})"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def crossref_doi(title: str, year: str) -> tuple[str, float] | tuple[None, float]:
    q = urllib.parse.quote(title)
    url = f"https://api.crossref.org/works?rows=5&mailto={MAILTO}&query.bibliographic={q}"
    try:
        items = get(url)["message"]["items"]
    except Exception:
        return None, 0.0
    best, best_score = None, 0.0
    for it in items:
        cand = (it.get("title") or [""])[0]
        score = difflib.SequenceMatcher(None, title.lower(), cand.lower()).ratio()
        # a year mismatch of more than one is a strong signal it is the wrong record
        iy = str((it.get("issued", {}).get("date-parts") or [[None]])[0][0] or "")
        if year and iy and abs(int(iy) - int(year)) > 1:
            score -= 0.15
        if score > best_score:
            best, best_score = it, score
    return (best["DOI"] if best and best_score >= MIN_SCORE else None), best_score


def unpaywall(doi: str) -> dict:
    try:
        d = get(f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={MAILTO}")
    except Exception:
        return {}
    loc = d.get("best_oa_location") or {}
    return {
        "is_oa": bool(d.get("is_oa")),
        "pdf": loc.get("url_for_pdf") or "",
        "landing": loc.get("url_for_landing_page") or "",
        "license": loc.get("license") or "",
        "host": loc.get("host_type") or "",
    }


def arxiv_id(entry: dict) -> str:
    m = re.search(r"arXiv:(\S+)", entry.get("journal", ""))
    return m.group(1) if m else ""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--refresh", action="store_true", help="re-resolve entries already cached")
    args = ap.parse_args()

    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    entries = parse_bib(BIB.read_text(encoding="utf-8"))
    todo = [e for e in entries if args.refresh or e["key"] not in cache]
    print(f"{len(entries)} entries, {len(todo)} to resolve")

    for i, e in enumerate(todo, 1):
        key, title = e["key"], delatex(e.get("title", ""))
        rec: dict = {"title": title}
        aid = arxiv_id(e)
        if aid:  # preprints already have a free, author-hosted copy
            rec |= {"doi": "", "pdf": f"https://arxiv.org/pdf/{aid}", "is_oa": True,
                    "license": "arxiv", "host": "repository", "score": 1.0}
        else:
            doi, score = crossref_doi(title, e.get("year", ""))
            rec |= {"doi": doi or "", "score": round(score, 3)}
            if doi:
                time.sleep(0.4)
                rec |= unpaywall(doi)
            else:
                rec |= {"is_oa": False, "pdf": "", "license": "", "host": ""}
        cache[key] = rec
        flag = "OA " if rec.get("is_oa") else "   "
        print(f"  [{i:2}/{len(todo)}] {flag}{key:24} {rec.get('doi','') or rec.get('pdf','')[:44]}")
        time.sleep(0.4)

    CACHE.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n")
    oa = sum(1 for v in cache.values() if v.get("is_oa"))
    nodoi = [k for k, v in cache.items() if not v.get("doi") and not v.get("pdf")]
    print(f"\nwrote {CACHE}\n  {oa}/{len(cache)} open access")
    if nodoi:
        print(f"  unresolved ({len(nodoi)}): {', '.join(nodoi)}")


if __name__ == "__main__":
    main()
