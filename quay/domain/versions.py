"""Version numbers like 0.36.2, compared the way people read them."""
from __future__ import annotations

import re


def parse(text: str | None) -> tuple[int, ...] | None:
    """`v0.36.2`, `0.36.2-1` and `0.36.2` all give (0, 36, 2); anything unreadable gives None."""
    match = re.match(r"\s*v?(\d+(?:\.\d+)*)", text or "")
    return tuple(int(p) for p in match.group(1).split(".")) if match else None


def is_newer(latest: str | None, installed: str | None) -> bool:
    a, b = parse(latest), parse(installed)
    if a is None or b is None:
        return False
    width = max(len(a), len(b))
    return a + (0,) * (width - len(a)) > b + (0,) * (width - len(b))
