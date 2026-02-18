"""
Copyright (c) 2025 William Wallace
G-Synthetic Project

MIT + G-Synthetic Addendum + Patent Notice. See LICENSE.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# A simple, file-system timeline store:
#   ./timelines/s{saga}/b{book}/c{chapter}/p{page}/x_up.json
#   ./timelines/s{saga}/b{book}/c{chapter}/p{page}/y_up.json

BASE = Path("timelines")

def _page_dir(coord: Tuple[int,int,int,int]) -> Path:
    saga, book, chapter, page = coord
    return BASE / f"s{saga}" / f"b{book}" / f"c{chapter}" / f"p{page:02d}"

def ensure_dirs(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def save_x_up(coord: Tuple[int,int,int,int], original_input: str) -> Path:
    d = _page_dir(coord)
    ensure_dirs(d)
    p = d / "x_up.json"
    payload = {
        "coord": {"saga": coord[0], "book": coord[1], "chapter": coord[2], "page": coord[3]},
        "input_raw": original_input
    }
    p.write_text(json.dumps(payload, indent=2))
    return p

def save_y_up(coord: Tuple[int,int,int,int], arcs_payload: Dict[str, Any]) -> Path:
    d = _page_dir(coord)
    ensure_dirs(d)
    p = d / "y_up.json"
    payload = {
        "coord": {"saga": coord[0], "book": coord[1], "chapter": coord[2], "page": coord[3]},
        "arcs": arcs_payload
    }
    p.write_text(json.dumps(payload, indent=2))
    return p

def read_page(coord: Tuple[int,int,int,int]) -> Dict[str, Any]:
    d = _page_dir(coord)
    data: Dict[str, Any] = {}
    for name in ("x_up.json","y_up.json"):
        fp = d / name
        if fp.exists():
            try:
                data[name] = json.loads(fp.read_text())
            except Exception:
                pass
    return data

def next_page_for(coord_prefix: Tuple[int,int,int]) -> Tuple[int,int,int,int]:
    """Auto-increment page index 00..99 within the s/b/c folder."""
    saga, book, chapter = coord_prefix
    root = BASE / f"s{saga}" / f"b{book}" / f"c{chapter}"
    root.mkdir(parents=True, exist_ok=True)
    existing = sorted([d for d in root.iterdir() if d.is_dir() and d.name.startswith("p")])
    if not existing:
        return (saga, book, chapter, 0)
    last = max(int(d.name[1:]) for d in existing if d.name[1:].isdigit())
    return (saga, book, chapter, min(last + 1, 99))
