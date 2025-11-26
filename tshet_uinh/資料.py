"""Data lookup helpers mirroring the structure of the 《廣韻》 dataset."""

# ruff: noqa: N801,N802,N803,N806

from collections.abc import Iterator
from dataclasses import dataclass, replace
from typing import Literal

from tshet_uinh.data import 廣韻, 廣韻impl
from tshet_uinh.utils import insert_into, prepend_values_into
from tshet_uinh.壓縮表示 import decode音韻編碼, encode音韻編碼
from tshet_uinh.音韻地位 import 音韻地位


@dataclass(frozen=True, slots=True)
class 王三來源:
    """Source metadata for 王三's supplemental entries.

    Args:
        文獻: Always ``"王三"`` to distinguish non-廣韻 records.
        小韻號: Identifier assigned in the 王三 corpus.
        韻目: Rhyme heading preserved from the supplemental note.
    """

    文獻: Literal["王三"] = "王三"
    小韻號: str = ""
    韻目: str = ""


來源類型 = 廣韻.廣韻來源 | 王三來源


@dataclass(frozen=True, slots=True)
class 檢索結果:
    """Public-facing search result payload.

    Args:
        字頭: The looked-up character.
        音韻地位: Matching 音韻地位 instance.
        反切: Fanqie gloss; ``None`` when absent.
        釋義: Original explanation text.
        來源: Provenance metadata from 《廣韻》 or 王三.
    """

    字頭: str
    音韻地位: 音韻地位
    反切: str | None
    釋義: str
    來源: 來源類型 | None


@dataclass(frozen=True, slots=True)
class 內部檢索結果:
    """Internal cache structure storing compressed readings.

    Args:
        字頭: Head character tied to the record.
        編碼: Three-character encoding from :func:`encode音韻編碼`.
        反切: Fanqie spelling, if any.
        釋義: Explanation text.
        來源: Either 《廣韻》 or 王三 provenance metadata.
    """

    字頭: str
    編碼: str
    反切: str | None
    釋義: str
    來源: 來源類型 | None


m字頭檢索: dict[str, list[內部檢索結果]] = {}
m音韻編碼檢索: dict[str, list[內部檢索結果]] = {}


def _build_indices() -> None:
    """Populate both head-character and 音韻編碼 indices."""
    for 原書小韻 in 廣韻impl.by原書小韻.values():
        for 條目 in 原書小韻:
            if 條目.音韻編碼 is None:
                continue
            來源 = 廣韻.廣韻來源(小韻號=條目.小韻號, 韻目=條目.韻目原貌)
            記錄 = 內部檢索結果(
                字頭=條目.字頭,
                編碼=條目.音韻編碼,
                反切=條目.反切,
                釋義=條目.釋義,
                來源=來源,
            )
            insert_into(m字頭檢索, 條目.字頭, 記錄)
            insert_into(m音韻編碼檢索, 條目.音韻編碼, 記錄)

    _augment_早期廣韻外字()


def _augment_早期廣韻外字() -> None:
    """Inject 王三 supplements ahead of the base dataset."""
    by字頭: dict[str, list[內部檢索結果]] = {}
    for 字頭, 描述, 反切, 釋義, 小韻號, 韻目 in (
        ("忘", "明三C陽平", "武方", "遺又武放不記曰忘", "797", "陽"),
        ("韻", "云合三B真去", "爲捃", "為捃反音和一", "2420", "震"),
    ):
        地位 = 音韻地位.from描述(描述)
        編碼 = encode音韻編碼(地位)
        記錄 = 內部檢索結果(
            字頭=字頭,
            編碼=編碼,
            反切=反切,
            釋義=釋義,
            來源=王三來源(小韻號=小韻號, 韻目=韻目),
        )
        insert_into(by字頭, 字頭, 記錄)

        insert_into(m音韻編碼檢索, 編碼, 記錄)

    for 字頭, 各條目 in by字頭.items():
        prepend_values_into(m字頭檢索, 字頭, 各條目)


def 結果from內部結果(內部結果: 內部檢索結果) -> 檢索結果:
    """Convert an internal cache entry into a user-visible result.

    Args:
        內部結果: Cached entry that still stores the compact encoding.

    Returns:
        檢索結果: Copy that exposes decoded 音韻地位 and cloned provenance.
    """
    return 檢索結果(
        字頭=內部結果.字頭,
        音韻地位=decode音韻編碼(內部結果.編碼),
        反切=內部結果.反切,
        釋義=內部結果.釋義,
        來源=_clone來源(內部結果.來源),
    )


def _clone來源(來源: 來源類型 | None) -> 來源類型 | None:
    """Return a defensive copy of the provenance object.

    Args:
        來源: Source metadata from either 《廣韻》 or 王三.

    Returns:
        來源類型 | None: Cloned instance, or ``None`` when unavailable.
    """
    if 來源 is None:
        return None
    if isinstance(來源, 王三來源):
        return replace(來源)
    return 廣韻.廣韻來源(小韻號=來源.小韻號, 韻目=來源.韻目)


def iter音韻地位() -> Iterator[音韻地位]:
    """Yield every 音韻地位 that has at least one attested character.

    Returns:
        Iterator[音韻地位]: Generator streaming decoded 音韻地位 objects.
    """
    for 編碼 in m音韻編碼檢索.keys():
        yield decode音韻編碼(編碼)


def query字頭(字頭: str) -> list[檢索結果]:
    """Fetch all entries associated with a given character.

    Args:
        字頭: Target character to look up.

    Returns:
        list[檢索結果]: Ordered results, or an empty list when missing.
    """
    return [結果from內部結果(記錄) for 記錄 in m字頭檢索.get(字頭, [])]


def query音韻地位(地位: 音韻地位) -> list[檢索結果]:
    """Return every character that matches the provided 音韻地位.

    Args:
        地位: 音韻地位 instance to encode and match.

    Returns:
        list[檢索結果]: Matching records, possibly empty if no characters share the reading.
    """
    編碼 = encode音韻編碼(地位)
    return [結果from內部結果(記錄) for 記錄 in m音韻編碼檢索.get(編碼, [])]


_build_indices()

__all__ = [
    "廣韻",
    "王三來源",
    "來源類型",
    "檢索結果",
    "iter音韻地位",
    "query字頭",
    "query音韻地位",
]
