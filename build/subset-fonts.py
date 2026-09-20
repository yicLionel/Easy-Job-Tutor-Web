#!/usr/bin/env python3
"""Subset the Source Han Sans SC woff files to a practical resume character set.

The full fonts are ~13 MB each, which is too heavy to ship or to load in the
browser. Resumes only need common Chinese, Latin, and punctuation, so we keep
GB2312 hanzi plus the shared symbol ranges and let the PDF library subset the
result again per document.

Usage:
    python build/subset-fonts.py

Reads  fonts/raw-Source_Han_Sans_SC_<Weight>.woff
Writes fonts/Source_Han_Sans_SC_<Weight>.woff
"""
from __future__ import annotations

import sys
from pathlib import Path

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"
WEIGHTS = ("Regular", "Bold")

# Shared symbol ranges: Latin-1, general punctuation, arrows, CJK punctuation,
# fullwidth forms, enclosed alphanumerics, and the common currency/legal marks.
RANGES = (
    (0x0020, 0x00FF),
    (0x2000, 0x206F),
    (0x2190, 0x21FF),
    (0x2460, 0x24FF),
    (0x25A0, 0x25FF),
    (0x3000, 0x303F),
    (0xFF00, 0xFFEF),
)


def gb2312_chars() -> set[str]:
    """Return every character representable in GB2312."""
    chars: set[str] = set()
    for lead in range(0xA1, 0xFA):
        for trail in range(0xA1, 0xFF):
            try:
                chars.add(bytes([lead, trail]).decode("gb2312"))
            except UnicodeDecodeError:
                continue
    return chars


def wanted_characters() -> set[str]:
    chars = set(gb2312_chars())
    for start, end in RANGES:
        chars.update(chr(code) for code in range(start, end + 1))
    return chars


def subset(weight: str, chars: set[str]) -> None:
    source = FONTS / f"raw-Source_Han_Sans_SC_{weight}.woff"
    target = FONTS / f"Source_Han_Sans_SC_{weight}.woff"
    if not source.exists():
        raise SystemExit(f"Missing source font: {source}")

    font = TTFont(source)
    options = Options()
    options.flavor = "woff"
    options.layout_features = ["*"]
    options.desubroutinize = True
    options.drop_tables += ["DSIG"]
    options.notdef_outline = True

    subsetter = Subsetter(options=options)
    subsetter.populate(unicodes={ord(c) for c in chars})
    subsetter.subset(font)
    font.save(target)
    font.close()
    print(f"{target.name}: {source.stat().st_size // 1024} KB -> {target.stat().st_size // 1024} KB")


def main() -> int:
    chars = wanted_characters()
    print(f"Subsetting to {len(chars)} characters")
    for weight in WEIGHTS:
        subset(weight, chars)
    return 0


if __name__ == "__main__":
    sys.exit(main())
