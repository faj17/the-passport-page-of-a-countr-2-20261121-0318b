#!/usr/bin/env python3
"""the-passport-page-of-a-countr-2-20261121-0318 entry: copy the passport
spread image to the output dir.

Standard library only, no network. Deterministic: the same bytes are
copied on every run, so two runs write identical files. The image itself
is drawn by generate.py (Pillow) and committed as entry.png.
"""
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / "entry.png"
    shutil.copyfile(HERE / "entry.png", dest)
    print(f"wrote {dest} ({dest.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
