"""Minimal in-memory logger used for tracing 反切 decisions."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class StringLogger:
    """Accumulates log lines in memory until they are drained.

    Args:
        enable: When ``True`` messages are recorded; useful during debugging.
        _messages: Backing buffer, normally left at its default.
    """

    enable: bool = False
    _messages: list[str] = field(default_factory=list)

    def log(self, message: str) -> None:
        """Append *message* when logging is enabled.

        Args:
            message: Text to be recorded verbatim.
        """
        if self.enable:
            self._messages.append(message)

    def pop_all(self) -> list[str]:
        """Return all buffered messages and reset the logger."""
        result = self._messages.copy()
        self._messages.clear()
        return result


default_logger = StringLogger()

__all__ = ["StringLogger", "default_logger"]
