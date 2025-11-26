"""Handy expression snippets consumed by :meth:`tshet_uinh.音韻地位.音韻地位.屬於`."""

from typing import Final

from .音韻屬性常量 import 呼韻搭配, 等韻搭配

一等韻: Final[str] = "".join(等韻搭配["一"]) + "韻"
二等韻: Final[str] = "".join(等韻搭配["二"]) + "韻"
三等韻: Final[str] = "".join(等韻搭配["三"]) + "韻"
四等韻: Final[str] = "".join(等韻搭配["四"]) + "韻"
一三等韻: Final[str] = "".join(等韻搭配["一三"]) + "韻"
二三等韻: Final[str] = "".join(等韻搭配["二三"]) + "韻"

分開合韻: Final[str] = "".join(呼韻搭配["開合"]) + "韻"
開口韻: Final[str] = "".join(呼韻搭配["開"]) + "韻"
合口韻: Final[str] = "".join(呼韻搭配["合"]) + "韻"
開合中立韻: Final[str] = "".join(呼韻搭配["中立"]) + "韻"

__all__ = [
    "一等韻",
    "二等韻",
    "三等韻",
    "四等韻",
    "一三等韻",
    "二三等韻",
    "分開合韻",
    "開口韻",
    "合口韻",
    "開合中立韻",
]
