"""Inline Lucide icon markup (lucide-static 1.70, ISC licensed).

Only icons that identify a pipeline stage, a state or an action are kept here.
The path data is copied verbatim from lucide-static 1.70; nothing is hand drawn.
"""

from __future__ import annotations

from functools import lru_cache

_PATHS: dict[str, str] = {
    "search": '<path d="m21 21-4.34-4.34" /><circle cx="11" cy="11" r="8" />',
    "book-open": (
        '<path d="M12 5v16" />'
        '<path d="M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2H4'
        'a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z" />'
    ),
    "pen-line": (
        '<path d="M13 21h8" />'
        '<path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352'
        'a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z" />'
    ),
    "clipboard-check": (
        '<rect width="8" height="4" x="8" y="2" rx="1" ry="1" />'
        '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />'
        '<path d="m9 14 2 2 4-4" />'
    ),
    "check": '<path d="M20 6 9 17l-5-5" />',
    "arrow-up-right": '<path d="M7 7h10v10" /><path d="M7 17 17 7" />',
    "circle-alert": (
        '<circle cx="12" cy="12" r="10" />'
        '<line x1="12" x2="12" y1="8" y2="12" />'
        '<line x1="12" x2="12.01" y1="16" y2="16" />'
    ),
}


@lru_cache(maxsize=64)
def icon(name: str, size: int = 16, stroke: float = 1.75) -> str:
    """Return an inline SVG for a Lucide icon that inherits ``currentColor``."""

    paths = _PATHS.get(name)
    if paths is None:
        raise KeyError(f"Unknown icon: {name}")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="{stroke}" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true" focusable="false">{paths}</svg>'
    )
