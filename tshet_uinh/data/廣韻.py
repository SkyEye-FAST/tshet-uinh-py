"""High-level traversal and lookup helpers for the 《廣韻》 dataset."""

# ruff: noqa: N801,N802,N803,N806

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Literal

from tshet_uinh.壓縮表示 import decode音韻編碼
from tshet_uinh.音韻地位 import 音韻地位

from . import 廣韻impl as impl


@dataclass(frozen=True, slots=True)
class 廣韻來源:
    """Canonical provenance metadata for a single 廣韻 entry.

    Args:
        文獻: Always ``"廣韻"`` so downstream consumers can attribute the source.
        小韻號: Identifier that may include a suffix (``a``/``b`` …) when a 小韻 splits into
            multiple 音韻地位.
        韻目: Original rhyme label recorded in the text, which may diverge from the
            computed 音韻地位.
    """

    文獻: Literal["廣韻"] = "廣韻"
    小韻號: str = ""
    韻目: str = ""


@dataclass(frozen=True, slots=True)
class 廣韻條目:
    """Fully decoded 廣韻 entry exposed to callers.

    Args:
        字頭: The grapheme that heads the entry.
        音韻地位: Decoded 音韻地位 object; ``None`` when the source marks an invalid value.
        反切: Fanqie spelling, omitted when the text uses other kinds of glossing.
        釋義: Original explanation text.
        來源: Source metadata describing the 小韻 number and rhyme heading.
    """

    字頭: str
    音韻地位: 音韻地位 | None
    反切: str | None
    釋義: str
    來源: 廣韻來源


def iter條目() -> Iterator[廣韻條目]:
    """Iterate through every 廣韻 entry in canonical order.

    Returns:
        Iterator[廣韻條目]: Generator that yields each entry exactly once.
    """
    for 條目列表 in iter原書小韻():
        yield from 條目列表


def iter小韻號() -> Iterator[str]:
    """Yield every 小韻 identifier, including split variants like ``3708b``.

    Returns:
        Iterator[str]: Keys ordered the same way as they appear in the parsed dataset.
    """
    return iter(impl.by小韻.keys())


def get小韻(小韻號: str) -> list[廣韻條目] | None:
    """Fetch every entry associated with a specific 小韻.

    Args:
        小韻號: Identifier such as ``3708b`` that may include a letter suffix for split readings.

    Returns:
        list[廣韻條目] | None: All entries under that 小韻, or ``None`` when the identifier
            is missing.
    """
    條目 = impl.by小韻.get(小韻號)
    if 條目 is None:
        return None

    return [條目from內部條目(item) for item in 條目]


def iter小韻() -> Iterator[list[廣韻條目]]:
    """Iterate over each 小韻, preserving the grouping of split readings.

    Returns:
        Iterator[list[廣韻條目]]: Generator yielding the full list for each identifier.
    """
    for 小韻號 in iter小韻號():
        條目 = get小韻(小韻號)
        if 條目 is not None:
            yield 條目


原書小韻總數 = len(impl.by原書小韻)


def get原書小韻(原書小韻號: int) -> list[廣韻條目] | None:
    """Fetch entries by the original unsplit 小韻 number.

    Args:
        原書小韻號: Numeric identifier between 1 and ``原書小韻總數``.

    Returns:
        list[廣韻條目] | None: All entries under that number, or ``None`` if it does not exist.
    """
    條目 = impl.by原書小韻.get(原書小韻號)
    if 條目 is None:
        return None

    return [條目from內部條目(item) for item in 條目]


def iter原書小韻() -> Iterator[list[廣韻條目]]:
    """Iterate over every original 小韻 without splitting multi-reading entries.

    Returns:
        Iterator[list[廣韻條目]]: Generator yielding the grouped entries for each book order index.
    """
    for index in range(1, 原書小韻總數 + 1):
        條目 = get原書小韻(index)
        if 條目 is not None:
            yield 條目


def 條目from內部條目(內部條目: impl.內部廣韻條目) -> 廣韻條目:
    """Convert the compact internal structure into a :class:`廣韻條目`.

    Args:
        內部條目: Parsed object produced by :mod:`tshet_uinh.data.廣韻impl`.

    Returns:
        廣韻條目: Public representation with an eagerly decoded 音韻地位 and provenance.
    """
    return 廣韻條目(
        字頭=內部條目.字頭,
        音韻地位=None if 內部條目.音韻編碼 is None else decode音韻編碼(內部條目.音韻編碼),
        反切=內部條目.反切,
        釋義=內部條目.釋義,
        來源=廣韻來源(小韻號=內部條目.小韻號, 韻目=內部條目.韻目原貌),
    )


__all__ = [
    "廣韻來源",
    "廣韻條目",
    "原書小韻總數",
    "iter條目",
    "iter小韻號",
    "iter小韻",
    "iter原書小韻",
    "get小韻",
    "get原書小韻",
]
