#!/usr/bin/env python3
"""main.py — entrypoint for news-image-20261124.

Copies the committed front-page image to /output/entry.png.
Standard library only: the grader runtime installs nothing, so this file
imports os and shutil and nothing else. The image itself is composed
locally by compose.py (PIL) and committed as image.jpg; this program
never draws, never fetches, never reads the network.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "image.jpg")


def main():
    out_dir = os.environ.get(
        "MAKEFUN_OUTPUT_DIR", os.environ.get("OUTPUT_DIR", "/output"))
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dest)
    print(f"wrote {dest} ({os.path.getsize(dest)} bytes)")


if __name__ == "__main__":
    main()
