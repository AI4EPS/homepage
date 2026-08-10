#!/usr/bin/env python3
"""Publish the PDFs in pdfs/ as GitHub release assets and record their URLs.

The release is a plain file host, so the publication page can offer a PDF next to
each entry without committing ~150 MB of binaries into the repository.

    python scripts/link_pdfs.py --dry-run   # show what would be uploaded
    python scripts/link_pdfs.py             # create/update the release and upload
    python scripts/make_publications.py     # regenerate the page with PDF links

Re-runnable: existing assets are replaced, new ones added. The resulting asset URL
per bibliography key is written back into docs/publication_links.json under "asset",
which make_publications.py reads.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDFS = ROOT / "pdfs"
CACHE = ROOT / "docs" / "publication_links.json"
REPO = "AI4EPS/homepage"
TAG = "papers"
TITLE = "Paper PDFs"
NOTES = (
    "PDFs of publications, hosted so the publication page can link them directly. "
    "Copyright remains with the respective publishers; these are author copies "
    "provided for personal and scholarly use."
)


def gh(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=False)


def ensure_release() -> None:
    if gh("release", "view", TAG, "--repo", REPO).returncode == 0:
        print(f"release '{TAG}' exists")
        return
    r = gh("release", "create", TAG, "--repo", REPO, "--title", TITLE, "--notes", NOTES)
    if r.returncode:
        sys.exit(f"could not create release: {r.stderr.strip()}")
    print(f"created release '{TAG}'")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pdfs = sorted(PDFS.glob("*.pdf"))
    if not pdfs:
        sys.exit(f"no PDFs in {PDFS}")
    total = sum(p.stat().st_size for p in pdfs) / 1_048_576
    print(f"{len(pdfs)} PDFs, {total:.0f} MB total")
    if args.dry_run:
        for p in pdfs:
            print(f"  {p.name:34} {p.stat().st_size/1_048_576:5.1f} MB")
        return

    ensure_release()
    for i, p in enumerate(pdfs, 1):
        r = gh("release", "upload", TAG, str(p), "--repo", REPO, "--clobber")
        print(f"  [{i:2}/{len(pdfs)}] {'ok  ' if not r.returncode else 'FAIL'} {p.name}"
              + ("" if not r.returncode else f"  {r.stderr.strip()[:60]}"))

    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    base = f"https://github.com/{REPO}/releases/download/{TAG}"
    for p in pdfs:
        cache.setdefault(p.stem, {})["asset"] = f"{base}/{p.name}"
    CACHE.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n")
    print(f"\nrecorded {len(pdfs)} asset URLs in {CACHE}")
    print("now run: python scripts/make_publications.py")


if __name__ == "__main__":
    main()
