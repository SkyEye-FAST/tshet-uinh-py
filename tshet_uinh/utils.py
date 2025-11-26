"""Shared helper utilities used across modules."""

from collections.abc import Callable, MutableMapping, Sequence
from typing import TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


def assert_condition(condition: bool, message: str | Callable[[], str]) -> None:
    """Raise :class:`ValueError` when the condition fails.

    Args:
        condition: Predicate that must evaluate to ``True``.
        message: Error text or a thunk returning the final message.

    Raises:
        ValueError: Raised when ``condition`` is ``False``, using the provided message.
    """
    if not condition:
        detail = message() if callable(message) else message
        raise ValueError(detail)


def insert_into(map_obj: MutableMapping[K, list[V]], key: K, value: V) -> None:
    """Append a single value to the list stored under ``key``.

    Args:
        map_obj: Mapping whose values are mutable lists.
        key: Target key to create or extend.
        value: Element appended to the end of the stored list.
    """
    map_obj.setdefault(key, []).append(value)


def prepend_values_into(map_obj: MutableMapping[K, list[V]], key: K, values: Sequence[V]) -> None:
    """Insert a batch of values at the front of the stored list.

    Args:
        map_obj: Mapping whose values are mutable lists.
        key: Target key that either already exists or will be created.
        values: Sequence to prepend, preserving its original order.
    """
    if key in map_obj:
        map_obj[key] = list(values) + map_obj[key]
    else:
        map_obj[key] = list(values)


__all__ = ["assert_condition", "insert_into", "prepend_values_into"]
