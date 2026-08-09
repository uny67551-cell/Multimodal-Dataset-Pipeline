"""Parse structured VLM text outputs."""

from __future__ import annotations # eliminate sequencial relationships between functions

def _split_csv(value: str) -> list[str]:
    """Split a comma-separated string into clean items."""
    items: list[str] = []
    for part in value.split(","): 
        item = part.strip()
        if item:
            items.append(item)
    return items

def parse_structured_response(text: str) -> tuple[str | None, list[str], list[str]]:
    """
    Parse model output in the format:
    CAPTION: ...
    TAGS: a, b, c
    OBJECTS: x, y
    """
    caption: str | None = None
    tags: list[str] = []
    objects: list[str] = []
    for raw_line in text.splitlines(): # split the text into lines
        line = raw_line.strip()
        if not line:
            continue
        upper = line.upper()
        if upper.startswith("CAPTION:"):
            caption = line.split(":", 1)[1].strip() or None # [1] is the second element of the splited list
        elif upper.startswith("TAGS:"):
            tags = _split_csv(line.split(":", 1)[1])
        elif upper.startswith("OBJECTS:"):
            objects = _split_csv(line.split(":", 1)[1])
    # Fallback: if model ignored the format, keep whole text as caption.
    if caption is None and not tags and not objects:
        cleaned = text.strip()
        caption = cleaned or None
    return caption, tags, objects
