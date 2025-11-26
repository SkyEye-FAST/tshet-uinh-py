"""Decode the compact 《廣韻》 payload and build lookup tables."""

# ruff: noqa: N801,N802,N803,N806

import re
from dataclasses import dataclass
from importlib import resources
from typing import Final

from tshet_uinh.utils import insert_into

_RAW_RESOURCE = resources.files("tshet_uinh.data.raw").joinpath("廣韻.txt")
_RAW_TEXT = _RAW_RESOURCE.read_text(encoding="utf-8")

_CODE_KEY_PATTERN = r"[A-Za-z0-9_$@]"
_LINE_PATTERN: Final = re.compile(rf"^((?:{_CODE_KEY_PATTERN}{{3}}..)+)(.*)$")
_CODE_PATTERN: Final = re.compile(r"(...)(..)")


@dataclass(frozen=True, slots=True)
class 內部廣韻條目:
    """Internal representation for a single 廣韻 record.

    Args:
        字頭: Character heading the entry.
        音韻編碼: Three-character compact 音韻編碼, or ``None`` when absent.
        反切: Fanqie spelling; ``None`` when the entry lacks one.
        釋義: Raw gloss text slice.
        小韻號: Identifier shared by all split readings of the same 小韻.
        韻目原貌: Rhyme heading as printed in the source material.
    """

    字頭: str
    音韻編碼: str | None
    反切: str | None
    釋義: str
    小韻號: str
    韻目原貌: str


by原書小韻: dict[int, list[內部廣韻條目]] = {}
by小韻: dict[str, list[內部廣韻條目]] = {}


def _parse_raw_text(raw_text: str) -> None:
    """Populate lookup dictionaries from the compact raw text.

    Args:
        raw_text: Entire encoded dataset loaded from the bundled resource.

    Raises:
        ValueError: If the source text deviates from the expected encoding format.
    """
    原書小韻號 = 0
    韻目原貌 = ""
    for line in raw_text.splitlines():
        if not line:
            continue
        if line.startswith("#"):
            韻目原貌 = line[1:]
            continue
        原書小韻號 += 1
        match = _LINE_PATTERN.match(line)
        if not match:
            raise ValueError(f"Invalid line in raw 廣韻 data: {line[:40]}")
        音韻, 內容 = match.groups()
        各地位反切: list[tuple[str | None, str | None]] = []
        for 編碼str, 反切str in _CODE_PATTERN.findall(音韻):
            各地位反切.append(
                (None if 編碼str == "@@@" else 編碼str, None if 反切str == "@@" else 反切str)
            )
        for segment in filter(None, 內容.split("|")):
            字頭 = segment[0]
            細分 = segment[1] if len(segment) > 1 and segment[1].islower() else ""
            釋義 = segment[2:] if 細分 else segment[1:]
            小韻號 = f"{原書小韻號}{細分}"
            細分index = ord(細分 or "a") - ord("a")
            if 細分index >= len(各地位反切):
                raise ValueError(
                    f"Index {細分index} out of range for 音韻 data on line {原書小韻號}"
                )
            音韻編碼, 反切 = 各地位反切[細分index]
            條目 = 內部廣韻條目(字頭, 音韻編碼, 反切, 釋義, 小韻號, 韻目原貌)

            insert_into(by原書小韻, 原書小韻號, 條目)
            insert_into(by小韻, 小韻號, 條目)


_parse_raw_text(_RAW_TEXT)

__all__ = ["內部廣韻條目", "by原書小韻", "by小韻"]
