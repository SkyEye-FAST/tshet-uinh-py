"""Encode and decode compact representations of :class:`tshet_uinh.音韻地位.音韻地位`."""

# ruff: noqa: N801,N802,N803,N806

from typing import Final, cast

from .utils import assert_condition
from .音韻地位 import _UNCHECKED, 音韻地位
from .音韻屬性常量 import 所有, 等韻搭配

編碼表: Final[tuple[str, ...]] = tuple(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789$_"
)
韻序表: Final[tuple[str, ...]] = tuple(
    "東＊冬鍾江支脂之微魚虞模齊祭泰佳皆夬灰咍廢真臻文殷元魂痕寒刪山先仙"
    "蕭宵肴豪歌＊麻＊陽唐庚＊耕清青蒸登尤侯幽侵覃談鹽添咸銜嚴凡"
)


def encode音韻編碼(地位: 音韻地位) -> str:
    """Compress an 音韻地位 into a three-character token.

    Args:
        地位: Target phonological profile.

    Returns:
        str: Two base-64-like digits for 母/韻, plus one digit for 呼+類+聲.
    """
    母序 = 所有["母"].index(地位.母)
    韻序 = 韻序表.index(地位.韻) + int(地位.韻 in "東歌麻庚" and 地位.等 not in {"一", "二"})

    # NOTE the value `-1` is expected when the argument is `None`
    呼序 = 所有["呼"].index(地位.呼) + 1 if 地位.呼 is not None else 0
    類序 = 所有["類"].index(地位.類) + 1 if 地位.類 is not None else 0

    呼類聲序 = (呼序 << 4) | (類序 << 2) | 所有["聲"].index(地位.聲)

    return 編碼表[母序] + 編碼表[韻序] + 編碼表[呼類聲序]


def decode音韻編碼(編碼: str) -> 音韻地位:
    """Expand a three-character token back into :class:`音韻地位`.

    Args:
        編碼: Token produced by :func:`encode音韻編碼`.

    Returns:
        音韻地位: Fully reconstructed phonological state.

    Raises:
        ValueError: Raised when the token contains invalid digits or indices.
    """
    assert_condition(len(編碼) == 3, lambda: f"Invalid 編碼: {編碼!r}")

    def _lookup_index(char: str) -> int:
        idx = 編碼表.index(char) if char in 編碼表 else -1
        assert_condition(idx != -1, lambda: f"Invalid character in 編碼: {char!r}")
        return idx

    母序, 韻序, 呼類聲序 = [_lookup_index(char) for char in 編碼]
    assert_condition(母序 < len(所有["母"]), lambda: f"Invalid 母序號: {母序}")
    母 = cast(str, 所有["母"][母序])

    assert_condition(韻序 < len(韻序表), lambda: f"Invalid 韻序號: {韻序}")
    韻 = cast(str, 韻序表[韻序])
    if 韻 == "＊":
        韻 = cast(str, 韻序表[韻序 - 1])
    等: str | None = None
    for 韻等, 各韻 in 等韻搭配.items():
        if 韻 in 各韻:
            等 = 韻等[1 if 韻序表[韻序] == "＊" else 0]
            if 等 == "三" and 母 in "端透定泥":
                等 = "四"
            break
    assert_condition(等 is not None, lambda: f"Cannot resolve 等 for 韻: {韻}")

    呼序 = 呼類聲序 >> 4
    assert_condition(呼序 <= len(所有["呼"]), lambda: f"Invalid 呼序號: {呼序}")
    呼 = cast(str, 所有["呼"][呼序 - 1]) if 呼序 else None

    類序 = (呼類聲序 >> 2) & 0b11
    assert_condition(類序 <= len(所有["類"]), lambda: f"Invalid 類序號: {類序}")
    類 = cast(str, 所有["類"][類序 - 1]) if 類序 else None

    聲序 = 呼類聲序 & 0b11
    聲 = cast(str, 所有["聲"][聲序])

    return 音韻地位(母, 呼, cast(str, 等), 類, 韻, 聲, _UNCHECKED)


__all__ = ["encode音韻編碼", "decode音韻編碼"]
