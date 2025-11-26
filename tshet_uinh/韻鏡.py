"""Helpers for converting between 韻鏡 coordinates and 音韻地位."""

# ruff: noqa: N801,N802,N803,N806

from dataclasses import dataclass
from functools import cached_property
from typing import Final

from tshet_uinh.StringLogger import default_logger
from tshet_uinh.音韻地位 import 音韻地位
from tshet_uinh.音韻屬性常量 import 等韻搭配, 鈍音母

轉呼: Final[tuple[str | None, ...]] = tuple(
    [
        None,
        None,
        None,
        *"開合開合開開合開合開合開合開合開合開合開合開開開合開合開合開合開合開開開開合開合",
    ]
)
母2idx: Final[tuple[str, ...]] = tuple(
    "幫滂並明端透定泥知徹澄孃見溪羣疑精清從心邪章昌船書常莊初崇生俟影曉匣云以來日"
)
母idx2右位: Final[tuple[int, ...]] = (
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    13,
    14,
    15,
    16,
    17,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    21,
    22,
    23,
)
轉名稱列表: Final[tuple[str, ...]] = (
    "內轉第一",
    "內轉第二",
    "外轉第三",
    "內轉第四",
    "內轉第五",
    "內轉第六",
    "內轉第七",
    "內轉第八",
    "內轉第九",
    "內轉第十",
    "內轉第十一",
    "內轉第十二",
    "內轉第十三",
    "外轉第十四",
    "外轉第十五",
    "外轉第十六",
    "外轉第十七",
    "外轉第十八",
    "外轉第十九",
    "外轉第二十",
    "外轉第二十一",
    "外轉第二十二",
    "外轉第二十三",
    "外轉第二十四",
    "外轉第二十五",
    "外轉第二十六",
    "內轉第二十七",
    "內轉第二十八",
    "內轉第二十九",
    "外轉第三十",
    "內轉第三十一",
    "內轉第三十二",
    "外轉第三十三",
    "外轉第三十四",
    "外轉第三十五",
    "外轉第三十六",
    "內轉第三十七",
    "內轉第三十八",
    "外轉第三十九",
    "外轉第四十",
    "外轉第四十一",
    "外轉第四十二",
    "外轉第四十三",
)
母位置名稱: Final[tuple[str | None, ...]] = (
    None,
    "脣音第一位",
    "脣音第二位",
    "脣音第三位",
    "脣音第四位",
    "舌音第一位",
    "舌音第二位",
    "舌音第三位",
    "舌音第四位",
    "牙音第一位",
    "牙音第二位",
    "牙音第三位",
    "牙音第四位",
    "齒音第一位",
    "齒音第二位",
    "齒音第三位",
    "齒音第四位",
    "齒音第五位",
    "喉音第一位",
    "喉音第二位",
    "喉音第三位",
    "喉音第四位",
    "舌齒音第一位",
    "舌齒音第二位",
)

聲lst: Final[str] = "平上去入"
等lst: Final[str] = "一二三四"
齒音母: Final[tuple[str, ...]] = tuple("精清從心邪章昌船書常莊初崇生俟")
喉音母: Final[tuple[str, ...]] = tuple("影曉匣")
幫組母: Final[tuple[str, ...]] = tuple("幫滂並明")


@dataclass
class 韻鏡位置:
    """Describe a single coordinate on the 韻鏡 chart.

    Args:
        轉號: Diagram index (1–43 inclusive).
        上位: Row index (1–16 inclusive).
        右位: Column index (1–23 inclusive).
    """

    轉號: int
    上位: int
    右位: int

    def __post_init__(self) -> None:
        """Validate that the coordinate stays inside the chart bounds."""
        if not 1 <= self.轉號 <= 43:
            raise ValueError("轉號必須在 1 到 43 之間")
        if not 1 <= self.上位 <= 16:
            raise ValueError("上位必須在 1 到 16 之間")
        if not 1 <= self.右位 <= 23:
            raise ValueError("右位必須在 1 到 23 之間")

    @cached_property
    def 轉名稱(self) -> str:
        """Return the human-readable diagram name (e.g., 「內轉第一圖」)."""
        return f"{轉名稱列表[self.轉號 - 1]}圖"

    @cached_property
    def 坐標(self) -> str:
        """Return the coordinate formatted as ``(轉號,上位,右位)``."""
        return f"({self.轉號},{self.上位},{self.右位})"

    @cached_property
    def 韻鏡等(self) -> int:
        """Return the raw division index (1–4) from the chart row."""
        return ((self.上位 - 1) % 4) + 1

    @cached_property
    def 韻(self) -> str:
        """Return the rime that corresponds to this coordinate."""
        return 轉號上位右位2韻(self.轉號, self.上位, self.右位)

    @cached_property
    def 切韻等(self) -> str:
        """Map the chart division back to the 切韻 division, logging exceptions."""
        韻鏡等 = self.韻鏡等

        if self.轉號 == 6 and self.上位 == 12 and self.右位 == 7:
            default_logger.log(f"韻鏡地位 {self.坐標}（即「地」字）為特殊情況，對應切韻四等")
            return "四"  # 「地」字為真四等
        if self.轉號 == 29 and self.上位 == 4 and self.右位 == 5:
            default_logger.log(f"韻鏡地位 {self.坐標}（即「爹」字）為特殊情況，對應切韻四等")
            return "四"  # 「爹」字為真四等
        if 韻鏡等 == 4 and self.韻 not in 等韻搭配["四"]:
            default_logger.log(
                f"韻鏡四等本應對應切韻四等，但{self.韻}韻非四等韻，故為假四等真三等，實際為切韻三等"
            )
            return "三"  # 假四等真三等
        if 韻鏡等 == 2 and self.韻 not in (*等韻搭配["二"], *等韻搭配["二三"]):
            if 12 < self.右位 <= 17:
                default_logger.log(
                    f"韻鏡二等本應對應切韻二等，但{self.韻}韻非二等韻，故為假二等真三等，實際為切韻三等"
                )
                return "三"  # 限定為齒音，假二等真三等
            raise ValueError("假二等真三等必須為齒音")
        if self.轉號 == 33 and (
            (self.右位 == 16 and 韻鏡等 == 2)
            or (self.右位 == 14 and (self.上位 == 10 or self.上位 == 14))
        ):
            default_logger.log(
                "韻鏡二等本應對應切韻二等，但「生」、「省」、「索」、「㵾」、「柵」為特殊情況，屬於莊三化二，故實際為切韻三等"
            )
            return "三"  # 「生」、「省」、「索」、「㵾」、「柵」莊三化二

        韻鏡等漢字 = 等lst[韻鏡等 - 1]
        should_note = 韻鏡等 in (2, 4)
        default_logger.log(
            f"韻鏡{韻鏡等漢字}等對應切韻{韻鏡等漢字}等{('（一般情況）' if should_note else '')}"
        )
        return 韻鏡等漢字

    @cached_property
    def 母(self) -> str:
        """Return the initial consonant implied by the column and division."""
        # 幫非組
        if self.右位 <= 4:
            母 = 幫組母[self.右位 - 1]
            default_logger.log(f"{母位置名稱[self.右位]}，對應{母}母")
            return 母

        # 端知組
        if self.右位 <= 8:
            # TODO: is 切韻等 correct? can handle 蛭,17,4,15?
            group = "端透定泥" if self.切韻等 in ("一", "四") else "知徹澄孃"
            母 = group[self.右位 - 5]
            range_label = "一四" if self.切韻等 in ("一", "四") else "二三"
            default_logger.log(f"{母位置名稱[self.右位]}，且為切韻{range_label}等，對應{母}母")
            return 母

        # 見組
        if self.右位 <= 12:
            母 = "見溪羣疑"[self.右位 - 9]
            default_logger.log(f"{母位置名稱[self.右位]}，對應{母}母")
            return 母

        # 齒音
        if self.右位 <= 17:
            if self.韻鏡等 in (1, 4):
                母 = "精清從心邪"[self.右位 - 13]
                default_logger.log(f"{母位置名稱[self.右位]}，且為韻鏡一四等，對應{母}母")
                return 母
            if self.韻鏡等 == 3:
                母 = "章昌船書常"[self.右位 - 13]  # TODO: 常船位置
                default_logger.log(f"{母位置名稱[self.右位]}，且為韻鏡三等，對應{母}母")
                return 母
            if self.韻鏡等 == 2:
                母 = "莊初崇生俟"[self.右位 - 13]
                default_logger.log(f"{母位置名稱[self.右位]}，且為韻鏡二等，對應{母}母")
                return 母
            raise ValueError("invalid 韻鏡等")

        # 喉音
        if self.右位 <= 20:
            母 = 喉音母[self.右位 - 18]
            default_logger.log(f"{母位置名稱[self.右位]}，對應{母}母")
            return 母

        # 喻母
        if self.右位 == 21:
            if self.韻鏡等 == 3:
                default_logger.log(f"{母位置名稱[self.右位]}，且為韻鏡三等，對應云母")
                return "云"
            default_logger.log(f"{母位置名稱[self.右位]}，且非韻鏡三等，對應以母")
            return "以"

        # 舌齒音
        if self.右位 <= 23:
            母 = "來日"[self.右位 - 22]
            default_logger.log(f"{母位置名稱[self.右位]}，對應{母}母")
            return 母
        raise ValueError("invalid 右位")

    @cached_property
    def 呼(self) -> str | None:
        """Infer whether the position uses 開口、合口, or is neutral."""
        if self.母 in 幫組母 or self.韻 in "模侯尤":
            return None
        呼 = 轉呼[self.轉號 - 1]
        if 呼 is not None:
            default_logger.log(f"{self.轉名稱}對應的呼為{呼}口")
        return 呼

    @cached_property
    def 聲(self) -> str:
        """Return the tone inferred from the row, honoring hand-annotated quirks."""
        raw聲 = 聲lst[(self.上位 - 1) // 4]
        if self.轉號 in (9, 10, 13, 14) and raw聲 == "入":
            default_logger.log(
                f"此位置處於入聲位，但第 {self.轉號} 轉入聲標註「去聲寄此」，故實際為去聲"
            )
            return "去"
        default_logger.log(f"此位置處於{raw聲}聲位，故為{raw聲}聲")
        return raw聲

    @cached_property
    def 類(self) -> str | None:
        """Return the 重紐類 (A/B/C) when the coordinate describes a鈍音三等 rime."""
        if self.切韻等 != "三" or self.母 not in 鈍音母:
            return None
        if self.韻 == "幽":
            if self.母 in 幫組母 or (self.轉號 == 37 and self.上位 == 4 and self.右位 == 10):
                default_logger.log(
                    "幽韻幫組及「惆」字對應 B 類。注意「飍」、「烋」為 A、B 類對立，"
                    "「烋」為 B 類，但此處無法區分二者"
                )
                return "B"
            # 幫組、「惆」為 B 類
            # 注意「飍」、「烋」為 A、B 類對立，「烋」為 B 類，但此處無法區分二者
            default_logger.log("幽韻非幫組且非「惆」字對應 A 類")
            return "A"
        if self.韻 == "蒸":
            if self.母 in 幫組母 or self.呼 == "合":
                default_logger.log(
                    "蒸韻幫組或合口對應 B 類。注意「憶」、「抑」為 B、C 類對立，"
                    "「抑」為 B 類，但此處無法區分二者"
                )
                return "B"
            # 幫組、合口為 B 類
            # 注意「憶」、「抑」為 B、C 類對立，「抑」為 B 類，但此處無法區分二者
            default_logger.log("蒸韻非幫組且非合口對應 C 類")
            return "C"
        if self.韻 not in "支脂祭真仙宵清侵鹽庚幽":
            default_logger.log(f"{self.韻}韻對應 C 類")
            return "C"
        if self.韻鏡等 == 4:
            default_logger.log("韻鏡四等對應 A 類（一般情況）")
            return "A"
        if self.韻鏡等 == 3:
            default_logger.log("韻鏡三等對應 B 類（一般情況）")
            return "B"
        raise ValueError("不可預期的類判定")

    @cached_property
    def 描述(self) -> str:
        """Return a verbose description of this coordinate.

        Returns:
            str: Diagram label, mother position, tone, and division fused as text.
        """
        raw聲 = 聲lst[(self.上位 - 1) // 4]
        韻鏡等漢字 = 等lst[self.韻鏡等 - 1]
        return f"{self.轉名稱}·{母位置名稱[self.右位]}·{raw聲}聲位·韻鏡{韻鏡等漢字}等"

    def to音韻地位(self) -> 音韻地位:
        """Convert the coordinate into an :class:`音韻地位` instance.

        Returns:
            音韻地位: The phonological record associated with this spot.

        Raises:
            ValueError: Propagated when derived attributes fail validation.
        """
        return 音韻地位(self.母, self.呼, self.切韻等, self.類, self.韻, self.聲)

    def 等於(self, other: "韻鏡位置") -> bool:
        """Return whether two coordinates refer to the same cell.

        Args:
            other: A second coordinate for comparison.

        Returns:
            bool: ``True`` only when all three indices are identical.
        """
        return self.轉號 == other.轉號 and self.上位 == other.上位 and self.右位 == other.右位


# 右位: 為區分尤/幽韻
def 轉號上位右位2韻(轉號: int, 上位: int, 右位: int) -> str:
    """Resolve the rime name from the raw chart coordinate.

    Args:
        轉號: Diagram index inside the 韻鏡.
        上位: Row number (1–16).
        右位: Column number (1–23).

    Returns:
        str: The rime that best matches the coordinate.

    Raises:
        ValueError: Raised when the coordinate combination is unsupported.
    """
    raw聲 = 聲lst[(上位 - 1) // 4]
    韻鏡等 = ((上位 - 1) % 4) + 1
    is齒音 = 12 < 右位 <= 17
    轉名稱 = f"{轉名稱列表[轉號 - 1]}圖"

    match 轉號:
        case 1:
            default_logger.log("此位置屬於東韻")
            return "東"
        case 2:
            if 韻鏡等 == 1:
                if raw聲 == "上":
                    default_logger.log(
                        f"{轉名稱}、上聲、韻鏡一等未標註對應韻，實際為冬韻，與其餘三聲相同"
                    )
                    return "冬"
                default_logger.log("此位置屬於冬韻")
                return "冬"
            default_logger.log("此位置屬於鍾韻")
            return "鍾"
        case 3:
            default_logger.log("此位置屬於江韻")
            return "江"
        case 4 | 5:
            default_logger.log("此位置屬於支韻")
            return "支"
        case 6 | 7:
            default_logger.log("此位置屬於脂韻")
            return "脂"
        case 8:
            default_logger.log("此位置屬於之韻")
            return "之"
        case 9 | 10 if raw聲 == "入":
            default_logger.log("此位置屬於廢韻")
            return "廢"
        case 9 | 10:
            default_logger.log("此位置屬於微韻")
            return "微"
        case 11:
            default_logger.log("此位置屬於魚韻")
            return "魚"
        case 12:
            if 韻鏡等 == 1:
                default_logger.log("此位置屬於模韻")
                return "模"
            default_logger.log("此位置屬於虞韻")
            return "虞"
        case 13:
            if raw聲 == "入":
                default_logger.log("此位置屬於夬韻")
                return "夬"
            if 韻鏡等 == 1:
                default_logger.log("此位置屬於咍韻")
                return "咍"
            if 韻鏡等 == 2:
                default_logger.log("此位置屬於皆韻")
                return "皆"
            if 韻鏡等 == 4:
                default_logger.log("此位置屬於齊韻")
                return "齊"
            if 韻鏡等 == 3:
                if raw聲 == "去":
                    default_logger.log("此位置屬於祭韻")
                    return "祭"
                default_logger.log(f"{轉名稱}、平上聲、韻鏡三等未標註對應韻，實際為咍韻")
                return "咍"
                # 咍韻三等平上聲均為特殊字，而咍韻三等去聲恰好無字，該處所排入字全為祭韻字
                # 祭韻字佔用去聲位
            raise ValueError(f"invalid 韻鏡等 {韻鏡等}")
        case 14:
            if raw聲 == "入":
                default_logger.log("此位置屬於夬韻")
                return "夬"
            if 韻鏡等 == 1:
                default_logger.log("此位置屬於灰韻")
                return "灰"
            if 韻鏡等 == 2:
                default_logger.log("此位置屬於皆韻")
                return "皆"
            if 韻鏡等 == 4:
                default_logger.log("此位置屬於齊韻")
                return "齊"
            if 韻鏡等 == 3 and raw聲 == "去":
                default_logger.log("此位置屬於祭韻")
                return "祭"
            raise ValueError(f"invalid combination 轉 14 韻鏡三等{raw聲}聲")  # 祭韻字佔用去聲位
        case 15 | 16:
            if 韻鏡等 == 2:
                default_logger.log("此位置屬於佳韻")
                return "佳"
            if raw聲 == "去":
                if 韻鏡等 == 1:
                    default_logger.log("此位置屬於泰韻")
                    return "泰"
                if 韻鏡等 == 4:
                    default_logger.log("此位置屬於祭韻")
                    return "祭"
            raise ValueError("invalid 轉 15/16 combination")
        case 17:
            if 韻鏡等 == 1:
                default_logger.log("此位置屬於痕韻")
                return "痕"
            if 韻鏡等 in (3, 4):
                default_logger.log("此位置屬於真韻")
                return "真"
            if 韻鏡等 == 2:
                default_logger.log("此位置屬於臻韻")
                return "臻"
            raise ValueError("invalid 韻鏡等")
        case 18:
            if 韻鏡等 == 1:
                default_logger.log("此位置屬於魂韻")
                return "魂"
            default_logger.log("此位置屬於真韻")
            return "真"
        case 19:
            default_logger.log("此位置屬於殷韻")
            return "殷"
        case 20:
            default_logger.log("此位置屬於文韻")
            return "文"
        case 21 | 22:
            if 韻鏡等 == 3:
                default_logger.log("此位置屬於元韻")
                return "元"
            if 韻鏡等 == 4:
                default_logger.log("此位置屬於仙韻")
                return "仙"
            if 韻鏡等 == 2:
                if raw聲 == "入":
                    default_logger.log(
                        f"此位置標註為山韻，但{轉名稱}、入聲、韻鏡二等刪、山韻排反，實際為刪韻"
                    )
                    return "刪"
                default_logger.log("此位置屬於山韻")
                return "山"
            raise ValueError("invalid 韻鏡等")
        case 23 | 24:
            if 韻鏡等 == 1:
                default_logger.log("此位置屬於寒韻")
                return "寒"
            if 韻鏡等 == 3:
                default_logger.log("此位置屬於仙韻")
                return "仙"
            if 韻鏡等 == 4:
                default_logger.log("此位置屬於先韻")
                return "先"
            if 韻鏡等 == 2:
                if raw聲 == "入":
                    default_logger.log(
                        f"此位置標註為刪韻，但{轉名稱}、入聲、韻鏡二等刪、山韻排反，實際為山韻"
                    )
                    return "山"
                default_logger.log("此位置屬於刪韻")
                return "刪"  # TODO: 處理仙韻 (see tests)
            raise ValueError("invalid 韻鏡等")
        case 25:
            if 韻鏡等 == 1:
                default_logger.log("此位置屬於豪韻")
                return "豪"
            if 韻鏡等 == 2:
                default_logger.log("此位置屬於肴韻")
                return "肴"
            if 韻鏡等 == 3:
                default_logger.log("此位置屬於宵韻")
                return "宵"
            if 韻鏡等 == 4:
                default_logger.log("此位置屬於蕭韻")
                return "蕭"
            raise ValueError("invalid 韻鏡等")
        case 26:
            default_logger.log("此位置屬於宵韻")
            return "宵"
        case 27 | 28:
            default_logger.log("此位置屬於歌韻")
            return "歌"
        case 29 | 30:
            default_logger.log("此位置屬於麻韻")
            return "麻"
        case 31 | 32:
            if 韻鏡等 == 1:
                default_logger.log("此位置屬於唐韻")
                return "唐"
            default_logger.log("此位置屬於陽韻")
            return "陽"
        case 33 | 34:
            if 韻鏡等 in (2, 3):
                default_logger.log("此位置屬於庚韻")
                return "庚"
            if 韻鏡等 == 4:
                default_logger.log("此位置屬於清韻")
                return "清"
            raise ValueError("invalid 韻鏡等")
        case 35:
            if 韻鏡等 == 2:
                default_logger.log("此位置屬於耕韻")
                return "耕"
            if 韻鏡等 == 3:
                default_logger.log("此位置屬於清韻")
                return "清"
            if 韻鏡等 == 4:
                default_logger.log("此位置屬於青韻")
                return "青"
            raise ValueError("invalid 韻鏡等")
        case 36:
            if 韻鏡等 == 2:
                default_logger.log("此位置屬於耕韻")
                return "耕"
            if 韻鏡等 == 4:
                default_logger.log("此位置屬於青韻")
                return "青"
            raise ValueError("invalid 韻鏡等")
        case 37:
            if 韻鏡等 == 1:
                default_logger.log("此位置屬於侯韻")
                return "侯"
            if 韻鏡等 in (2, 3):
                default_logger.log("此位置屬於尤韻")
                return "尤"
            if 韻鏡等 == 4:
                if is齒音 or 右位 == 21:
                    default_logger.log(
                        f"此位置標註為幽韻，但{轉名稱}、韻鏡四等位有尤、幽二韻混排，其中齒音與以母為尤韻"
                    )
                    return "尤"  # 尤、幽韻在韻鏡四等混排，齒音與以母為尤韻
                default_logger.log(
                    f"此位置標註為幽韻，但{轉名稱}、韻鏡四等位有尤、幽二韻混排，其中非齒音且非以母為幽韻"
                )
                return "幽"
            raise ValueError("invalid 韻鏡等")
        case 38:
            default_logger.log("此位置屬於侵韻")
            return "侵"
        case 39:
            if 韻鏡等 == 1:
                default_logger.log("此位置屬於覃韻")
                return "覃"
            if 韻鏡等 == 2:
                default_logger.log("此位置屬於咸韻")
                return "咸"
            if 韻鏡等 == 3:
                default_logger.log("此位置屬於鹽韻")
                return "鹽"
            if 韻鏡等 == 4:
                default_logger.log("此位置屬於添韻")
                return "添"
            raise ValueError("invalid 韻鏡等")
        case 40:
            if 韻鏡等 == 1:
                default_logger.log("此位置屬於談韻")
                return "談"
            if 韻鏡等 == 2:
                default_logger.log("此位置屬於銜韻")
                return "銜"
            if 韻鏡等 == 3:
                default_logger.log("此位置屬於嚴韻")
                return "嚴"
            if 韻鏡等 == 4:
                default_logger.log("此位置屬於鹽韻")
                return "鹽"
            raise ValueError("invalid 韻鏡等")
        case 41:
            default_logger.log("此位置屬於凡韻")
            return "凡"
        case 42 | 43:
            if 韻鏡等 == 1:
                default_logger.log("此位置屬於登韻")
                return "登"
            default_logger.log("此位置屬於蒸韻")
            return "蒸"
        case _:
            raise ValueError("未知轉號")
    raise ValueError("未知轉號")


def 音韻地位2韻鏡位置(當前音韻地位: 音韻地位) -> 韻鏡位置:
    """Map an :class:`音韻地位` back to its unique chart coordinate.

    Args:
        當前音韻地位: The phonological record to project onto the chart.

    Returns:
        韻鏡位置: The matching coordinate within the table.

    Raises:
        ValueError: Raised when no legal position can be inferred.
    """
    母 = 當前音韻地位.母
    呼 = 當前音韻地位.呼
    等 = 當前音韻地位.等
    類 = 當前音韻地位.類
    韻 = 當前音韻地位.韻
    聲 = 當前音韻地位.聲

    # calculate 韻鏡等
    need_add_one = 類 == "A" or (當前音韻地位.母 in "精清從心邪以" and 等 == "三") or 韻 == "幽"
    # 重紐四等、假四等真三等、幽韻為四等位
    need_minus_one = 當前音韻地位.母 in "莊初崇生俟" and 等 == "三"  # 假二等真三等
    韻鏡等 = 等lst.index(等) + 1 + (1 if need_add_one else -1 if need_minus_one else 0)

    # calculate 轉號
    轉號 = _母類呼韻聲2轉號(母, 呼, 類, 韻, 聲, 韻鏡等)

    # calculate 上位
    need寄入 = 韻 in "廢夬"
    上位 = (3 if need寄入 else 聲lst.index(聲)) * 4 + 韻鏡等

    # calculate 右位
    右位 = 母idx2右位[母2idx.index(母)]

    return 韻鏡位置(轉號, 上位, 右位)


def _母類呼韻聲2轉號(
    母: str,
    呼: str | None,
    類: str | None,
    韻: str,
    聲: str,
    韻鏡等: int,
) -> int:
    if 呼 is None:
        # TODO: cannot use 開口?
        should_use合口 = (
            韻 in "微廢夬元寒歌"
            or (韻 in "佳皆" and 聲 == "去")
            or (韻 == "刪" and 聲 != "入")
            or (韻 == "山" and 聲 == "入")
            or (韻 == "仙" and 聲 == "去" and 類 == "B")
        )
        呼 = "合" if should_use合口 else "開"

    match 韻:
        case "東":
            return 1
        case "冬" | "鍾":
            return 2
        case "江":
            return 3
        case "支":
            return 4 if 呼 == "開" else 5
        case "脂":
            return 6 if 呼 == "開" else 7
        case "之":
            return 8
        case "微" | "廢":
            return 9 if 呼 == "開" else 10
        case "魚":
            return 11
        case "虞" | "模":
            return 12
        case "齊" | "夬" | "皆":
            return 13 if 呼 == "開" else 14
        case "咍":
            return 13
        case "灰":
            return 14
        case "祭" if 韻鏡等 == 3:
            return 13 if 呼 == "開" else 14
        case "祭" if 韻鏡等 == 4:
            return 15 if 呼 == "開" else 16
        case "祭":
            raise ValueError(f"韻鏡等 {韻鏡等} invalid for 祭韻")
        case "佳" | "泰":
            return 15 if 呼 == "開" else 16
        case "痕" | "臻":
            return 17
        case "魂":
            return 18
        case "真":
            return 17 if 呼 == "開" else 18
        case "殷":
            return 19
        case "文":
            return 20
        case "元":
            return 21 if 呼 == "開" else 22
        case "山" if 聲 == "入":
            return 23 if 呼 == "開" else 24
        case "山":
            return 21 if 呼 == "開" else 22
        case "刪" if 聲 == "入":
            return 21 if 呼 == "開" else 22
        case "刪":
            return 23 if 呼 == "開" else 24
        case "仙" if 韻鏡等 == 3:
            return 23 if 呼 == "開" else 24
        case "仙" if 韻鏡等 in (2, 4):
            return 21 if 呼 == "開" else 22
        case "仙":
            raise ValueError("error")
        case "寒" | "先":
            return 23 if 呼 == "開" else 24
        case "蕭" | "肴" | "豪":
            return 25
        case "宵":
            return 26 if (類 == "A" or 母 in "精清從心邪以") else 25
        case "歌":
            return 27 if 呼 == "開" else 28
        case "麻":
            return 29 if 呼 == "開" else 30
        case "陽" | "唐":
            return 31 if 呼 == "開" else 32
        case "庚":
            return 33 if 呼 == "開" else 34
        case "清" if 韻鏡等 == 3 and 呼 == "開":
            return 35
        case "清" if 韻鏡等 == 3:
            raise ValueError("error: no 合口")
        case "清" if 韻鏡等 == 4:
            return 33 if 呼 == "開" else 34
        case "清":
            raise ValueError("error")
        case "耕" | "青":
            return 35 if 呼 == "開" else 36
        case "尤" | "侯" | "幽":
            return 37
        case "侵":
            return 38
        case "鹽" if 韻鏡等 == 3:
            return 39
        case "鹽" if 韻鏡等 == 4:
            return 40
        case "鹽":
            raise ValueError(f"韻鏡等 {韻鏡等} invalid for 鹽韻")
        case "覃" | "咸" | "添":
            return 39
        case "談" | "銜":
            return 40
        case "嚴" if 韻鏡等 == 3:
            return 40
        case "嚴":
            raise ValueError(f"韻鏡等 {韻鏡等} invalid for 嚴韻")
        case "凡":
            return 41
        case "登" | "蒸":
            return 42 if 呼 == "開" else 43
        case _:
            raise ValueError("未知韻種")


__all__ = ["韻鏡位置", "音韻地位2韻鏡位置", "轉號上位右位2韻"]
