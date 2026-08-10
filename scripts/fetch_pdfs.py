#!/usr/bin/env python3
"""Download a PDF for every entry in docs/publication_links.json.

Sources, in order of preference:
  1. the open-access copy Unpaywall points at (publisher or repository hosted)
  2. arXiv, for preprints
Anything that fails is listed at the end so it can be filled in by hand from Zotero.

    python scripts/fetch_pdfs.py [--outdir DIR] [--only KEY ...]

Files land as <key>.pdf, ready to upload as GitHub release assets.
"""

import argparse
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "docs" / "publication_links.json"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")


def fetch(url: str, dest: Path) -> tuple[bool, str]:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/pdf,text/html;q=0.9,*/*;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            head = r.read(5)
            if head != b"%PDF-":
                return False, f"not a PDF (starts {head!r})"
            body = head + r.read()
    except Exception as e:  # noqa: BLE001 - report whatever the server said
        return False, str(e)[:70]
    if len(body) < 20_000:
        return False, f"suspiciously small ({len(body)} B)"
    dest.write_bytes(body)
    return True, f"{len(body)/1_048_576:.1f} MB"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", default=str(ROOT / "pdfs"))
    ap.add_argument("--only", nargs="*", default=None)
    args = ap.parse_args()

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    cache = json.loads(CACHE.read_text())

    ok, failed = [], []
    items = sorted(cache.items())
    if args.only:
        items = [(k, v) for k, v in items if k in set(args.only)]

    for i, (key, rec) in enumerate(items, 1):
        dest = out / f"{key}.pdf"
        if dest.exists() and dest.stat().st_size > 20_000:
            ok.append(key)
            print(f"[{i:2}/{len(items)}] have {key}")
            continue
        url = rec.get("pdf") or ""
        if not url:
            failed.append((key, "no open-access URL"))
            print(f"[{i:2}/{len(items)}] SKIP {key:24} no open-access URL")
            continue
        good, msg = fetch(url, dest)
        (ok.append(key) if good else failed.append((key, msg)))
        print(f"[{i:2}/{len(items)}] {'OK  ' if good else 'FAIL'} {key:24} {msg}")
        time.sleep(1.0)

    print(f"\n{len(ok)} downloaded into {out}")
    if failed:
        print(f"{len(failed)} missing:")
        for k, why in failed:
            print(f"  {k:26} {why}")


if __name__ == "__main__":
    main()
