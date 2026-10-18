"""Stage 1 extract validation + layout tests."""

import pytest

from app.pipeline.extract import ExtractError, extract_text


def test_plain_text_layout():
    text, layout = extract_text(b"hello world", "cv.txt")
    assert text == "hello world"
    assert layout["file_type"] == "txt"
    assert layout["has_text"] is True
    assert layout["single_column"] is True


def test_unsupported_type_rejected():
    with pytest.raises(ExtractError):
        extract_text(b"data", "cv.rtf")


def test_empty_file_rejected():
    with pytest.raises(ExtractError):
        extract_text(b"", "cv.pdf")


def test_oversize_rejected():
    with pytest.raises(ExtractError):
        extract_text(b"x" * (5 * 1024 * 1024 + 1), "cv.txt")
