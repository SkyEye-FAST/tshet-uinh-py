"""Tests covering the StringLogger helper in isolation."""

from collections.abc import Iterator

import pytest

from tshet_uinh.StringLogger import default_logger


@pytest.fixture(autouse=True)
def reset_logger_state() -> Iterator[None]:
    """Ensure each test starts with a disabled logger and empty buffer."""
    previous = default_logger.enable
    default_logger.enable = False
    default_logger.pop_all()
    try:
        yield
    finally:
        default_logger.enable = previous
        default_logger.pop_all()


def test_string_logger_behaviour() -> None:
    """Ensure buffering only occurs when the logger is enabled."""
    default_logger.enable = True
    default_logger.log("測試 1")
    default_logger.log("測試 2")
    assert default_logger.pop_all() == ["測試 1", "測試 2"]
    assert default_logger.pop_all() == []

    default_logger.enable = False
    default_logger.log("這條不應該被記錄")
    assert default_logger.pop_all() == []
