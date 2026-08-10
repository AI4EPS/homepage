#!/usr/bin/env python3
"""Copy PDFs out of the local Zotero library for any paper still missing from pdfs/.

Zotero holds the copies that publishers refuse to serve to scripts, so this fills the
gap left by fetch_pdfs.py. Items are matched by DOI first, then by a strict title
similarity, and only PDF attachments that actually exist on disk are copied.

    python scripts/fetch_from_zotero.py [--all] [--min-score 0.92]

The database is copied before reading, so a running Zotero does not block the query.
"""

import argparse
import difflib
import json
import shutil
import sqlite3
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "docs" / "publication_links.json"
PDFS = ROOT / "pdfs"
ZOTERO = Path.home() / "Documents" / "zotero"


def zotero_items(db: Path) -> list[dict]:
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    rows = con.execute("""
        SELECT i.itemID,
               MAX(CASE WHEN f.fieldName='title' THEN v.value END) AS title,
               MAX(CASE WHEN f.fieldName='DOI'   THEN v.value END) AS doi
        FROM items i
        JOIN itemData id ON id.itemID = i.itemID
        JOIN itemDataValues v ON v.valueID = id.valueID
        JOIN fields f ON f.fieldID = id.fieldID
        GROUP BY i.itemID
    """).fetchall()
    con.close()
    return [dict(r) for r in rows if r["title"]]


def attachments(db: Path, item_id: int) -> list[Path]:
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    rows = con.execute("""
        SELECT ia.path, it.key AS akey
        FROM itemAttachments ia
        JOIN items it ON it.itemID = ia.itemID
        WHERE ia.parentItemID = ? AND ia.contentType = 'application/pdf'
    """, (item_id,)).fetchall()
    con.close()
    out = []
    for r in rows:
        p = r["path"] or ""
        if p.startswith("storage:"):
            out.append(ZOTERO / "storage" / r["akey"] / p[len("storage:"):])
        elif p.startswith("attachments:"):
            out.append(Path(p[len("attachments:"):]))
        elif p:
            out.append(Path(p))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--all", action="store_true", help="also re-copy papers already in pdfs/")
    ap.add_argument("--min-score", type=float, default=0.92)
    args = ap.parse_args()

    src = ZOTERO / "zotero.sqlite"
    if not src.exists():
        raise SystemExit(f"no Zotero database at {src}")
    tmp = Path(tempfile.mkdtemp()) / "zotero.sqlite"
    shutil.copyfile(src, tmp)

    items = zotero_items(tmp)
    by_doi = {(i["doi"] or "").lower().strip(): i for i in items if i["doi"]}
    print(f"{len(items)} Zotero items ({len(by_doi)} with DOIs)")

    cache = json.loads(CACHE.read_text())
    PDFS.mkdir(exist_ok=True)
    have = {p.stem for p in PDFS.glob("*.pdf") if p.stat().st_size > 20_000}
    todo = {k: v for k, v in cache.items() if args.all or k not in have}
    print(f"{len(todo)} papers to look for\n")

    copied, nomatch, nofile = [], [], []
    for key, rec in sorted(todo.items()):
        def stored(item_id: int) -> Path | None:
            return next((p for p in attachments(tmp, item_id)
                         if p.exists() and p.stat().st_size > 20_000), None)

        item = by_doi.get((rec.get("doi") or "").lower().strip())
        src_pdf = stored(item["itemID"]) if item else None
        if not src_pdf:
            # Duplicate records are common, and only one copy usually holds the file,
            # so walk the best title matches and take the first that has a PDF.
            title = (rec.get("title") or "").lower()
            ranked = sorted(items, key=lambda x: difflib.SequenceMatcher(
                None, title, x["title"].lower()).ratio(), reverse=True)[:8]
            item = None
            for cand in ranked:
                if difflib.SequenceMatcher(None, title, cand["title"].lower()).ratio() < args.min_score:
                    break
                if (found := stored(cand["itemID"])):
                    item, src_pdf = cand, found
                    break
        if not item:
            nomatch.append(key)
            print(f"  --   {key:26} not in Zotero")
            continue
        if not src_pdf:
            nofile.append(key)
            print(f"  --   {key:26} matched, but no stored PDF")
            continue
        shutil.copyfile(src_pdf, PDFS / f"{key}.pdf")
        copied.append(key)
        print(f"  ok   {key:26} {src_pdf.stat().st_size/1_048_576:5.1f} MB")

    total = len({p.stem for p in PDFS.glob('*.pdf')})
    print(f"\ncopied {len(copied)};  {total}/{len(cache)} papers now have a PDF")
    if nofile:
        print(f"matched but no attachment ({len(nofile)}): {', '.join(nofile)}")
    if nomatch:
        print(f"not found in Zotero ({len(nomatch)}): {', '.join(nomatch)}")


if __name__ == "__main__":
    main()
