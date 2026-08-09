"""Unit tests for inference response parser."""

from pipeline.inference.parser import parse_structured_response


def test_parse_structured_response() -> None:
    text = (
        "CAPTION: A red temple under blue sky.\n"
        "TAGS: temple, architecture, sky\n"
        "OBJECTS: roof, column, cloud\n"
    )
    caption, tags, objects = parse_structured_response(text)

    assert caption == "A red temple under blue sky."
    assert tags == ["temple", "architecture", "sky"]
    assert objects == ["roof", "column", "cloud"]


def test_parse_fallback_plain_text() -> None:
    caption, tags, objects = parse_structured_response("just a plain sentence")

    assert caption == "just a plain sentence"
    assert tags == []
    assert objects == []