"""Derives all 反切 candidates following the rules in 潘悟雲《反切行為與反切原則》."""

# ruff: noqa: N801,N802,N803,N806

from dataclasses import dataclass
from typing import Final

from tshet_uinh.StringLogger import default_logger
from tshet_uinh.音韻地位 import 音韻地位
from tshet_uinh.音韻屬性常量 import 呼韻搭配, 等母搭配, 等韻搭配, 鈍音母

重紐韻: Final[tuple[str, ...]] = tuple("支脂祭真仙宵清侵鹽")


def generate呼(
    母: str,
    組: str | None,
    韻: str,
    上字呼: str | None,
    下字呼: str | None,
    下字組: str | None,
) -> list[str | None]:
    """Return every 呼 candidate implied by the 反切 pieces.

    Args:
        母: The initial of the upper character.
        組: The consonant group assigned to the upper character.
        韻: The rime of the lower character.
        上字呼: The rounding value of the upper character.
        下字呼: The rounding value of the lower character.
        下字組: The consonant group of the lower character.

    Returns:
        list[str | None]: Possible 呼 labels, including ``None`` for neutral cases.
    """
    if 組 == "幫" or 韻 in 呼韻搭配["中立"]:
        呼 = None
    elif 韻 in 呼韻搭配["開"]:
        呼 = "開"
        default_logger.log(f"被切字為{韻}韻，{韻}韻為開口，故被切字為開口")
    elif 韻 in 呼韻搭配["合"]:
        呼 = "合"
        default_logger.log(f"被切字為{韻}韻，{韻}韻為合口，故被切字為合口")
    elif 母 == "云":
        呼 = "合"
        default_logger.log("被切字為云母，云母為合口，故被切字為合口")
    else:
        if 上字呼 == "開" and 下字呼 == "開":
            呼 = "開"
            default_logger.log("反切上下字均為開口，故被切字為開口")
        elif 下字呼 == "合":
            呼 = "合"
            default_logger.log("反切下字為合口，故被切字為合口")
        elif 上字呼 == "合" and 下字組 == "幫":
            呼 = "合"
            default_logger.log("反切上字為合口，下字為幫組，故被切字為合口")
        else:
            呼 = "開合"
            default_logger.log("無法確定被切字的呼，可能為開口或合口")
    return list(呼) if 呼 == "開合" else [呼]


def generate等(母: str, 韻: str, 上字等: str, 下字等: str) -> list[str]:
    """Infer the set of division levels (等) implied by the 反切.

    Args:
        母: The initial of the upper character.
        韻: The lower character's rime.
        上字等: The division level of the upper character.
        下字等: The division level of the lower character.

    Returns:
        list[str]: One or more feasible 等 labels.

    Raises:
        RuntimeError: If the 配合 tables cannot cover the provided combination.
    """
    if 韻 in 等韻搭配["一"]:
        等 = "一"
        default_logger.log(f"被切字為{韻}韻，{韻}韻為一等，故被切字為一等")
    elif 韻 in 等韻搭配["二"]:
        等 = "二"
        default_logger.log(f"被切字為{韻}韻，{韻}韻為二等，故被切字為二等")
    elif 韻 in 等韻搭配["三"]:
        等 = "三"
        default_logger.log(f"被切字為{韻}韻，{韻}韻為三等，故被切字為三等")
    elif 韻 in 等韻搭配["四"]:
        等 = "四"
        default_logger.log(f"被切字為{韻}韻，{韻}韻為四等，故被切字為四等")
    elif 下字等 == "三":
        等 = "三"
        default_logger.log("反切下字為三等，故被切字為三等")
    elif 上字等 != "三" and 下字等 != "三":
        default_logger.log("反切上下字均非三等，故被切字非三等")
        if 韻 in 等韻搭配["一三"]:
            等 = "一"
            default_logger.log(
                f"被切字為{韻}韻，{韻}韻為一等或三等，而被切字非三等，故被切字為一等"
            )
        elif 韻 in 等韻搭配["二三"]:
            等 = "二"
            default_logger.log(
                f"被切字為{韻}韻，{韻}韻為二等或三等，而被切字非三等，故被切字為二等"
            )
        else:
            raise RuntimeError("Unreachable state for 等推導")
    else:
        if 韻 in 等韻搭配["一三"]:
            default_logger.log(f"被切字為{韻}韻，{韻}韻為一等或三等，故被切字為一等或三等")
            if 母 in 等母搭配["二三"] or 母 in 等母搭配["三"]:
                等 = "三"
                default_logger.log(f"被切字為{母}母，{母}母不可能為一等，故被切字為三等")
            elif 母 in 等母搭配["一二四"]:
                等 = "一"
                default_logger.log(f"被切字為{母}母，{母}母不可能為三等，故被切字為一等")
            else:
                等 = "一三"
                default_logger.log("無法確定被切字的等，可能為一等或三等")
        elif 韻 in 等韻搭配["二三"]:
            default_logger.log(f"被切字為{韻}韻，{韻}韻為二等或三等，故被切字為二等或三等")
            if 母 in 等母搭配["一三四"] or 母 in 等母搭配["三"]:
                等 = "三"
                default_logger.log(f"被切字為{母}母，{母}母不可能為二等，故被切字為三等")
            elif 母 in 等母搭配["一二四"]:
                等 = "二"
                default_logger.log(f"被切字為{母}母，{母}母不可能為三等，故被切字為二等")
            else:
                等 = "二三"
                default_logger.log("無法確定被切字的等，可能為二等或三等")
        else:
            raise RuntimeError("Unreachable state for 等推導")
    return list(等) if 等 in {"一三", "二三"} else [等]


@dataclass(frozen=True, slots=True)
class 類data:
    """Carry the resolved 重紐類別 together with an explanatory note.

    Args:
        類: The resolved class, or ``None`` when no decision is needed.
        解釋: Human-readable explanation logged for tracing.
    """

    類: str | None
    解釋: str | None


# 類需特殊處理，故寫法與上述兩函式不同
def rawGenerate類(
    下字音韻地位: 音韻地位,
    母: str,
    組: str | None,
    韻: str,
    上字類: str | None,
    呼: str | None,
    等: str,
) -> 類data:
    """Resolve 重紐類別 whenever the rules demand it.

    Args:
        下字音韻地位: The full profile of the lower character.
        母: The initial of the upper character.
        組: The consonant group of the upper character.
        韻: The lower character's rime.
        上字類: The upper character's 重紐類別, if known.
        呼: The candidate 呼 under evaluation.
        等: The candidate division level under evaluation.

    Returns:
        類data: The selected 類 plus an optional explanation.
    """
    if 等 != "三" or 母 not in 鈍音母:
        return 類data(None, None)
    if 韻 == "幽":
        if 組 == "幫":
            return 類data(
                "B", "被切字為幽韻，且為幫組，故被切字為 B 類"
            )  # 幫組、「惆」、「烋」爲 B 類
        return 類data("A", "被切字為幽韻，且非幫組，故被切字為 A 類")
    if 韻 == "蒸":
        if 組 == "幫" or 呼 == "合":
            return 類data(
                "B", "被切字為蒸韻，且為幫組或合口，故被切字為 B 類"
            )  # 幫組、合口、「抑」爲 B 類
        return 類data("C", "被切字為蒸韻，且非幫組或合口，故被切字為 C 類")
    if 韻 == "庚":
        return 類data("B", "被切字為庚韻，故被切字為 B 類")
    if 韻 not in 重紐韻:
        return 類data("C", "被切字非重紐韻，故被切字為 C 類")  # TODO: confirm this
    if 母 == "云":
        return 類data("B", "被切字為云母，故被切字為 B 類")
    if 上字類 == "A":
        return 類data("A", "反切上字為 A 類，故被切字為 A 類")
    if 上字類 == "B":
        return 類data("B", "反切上字為 B 類，故被切字為 B 類")
    if 下字音韻地位.屬於("A類 或 以母 或 精組"):
        return 類data("A", "反切下字為 A 類、以母或精組，故被切字為 A 類")
    if 下字音韻地位.屬於("B類 或 云母"):
        return 類data("B", "反切下字為 B 類或云母，故被切字為 B 類")
    return 類data("AB", "無法確定被切字的類，可能為 A 類或 B 類")


def 執行反切(上字音韻地位: 音韻地位, 下字音韻地位: 音韻地位) -> list[音韻地位]:
    """Yield every 音韻地位 compatible with the supplied 反切 pair.

    Args:
        上字音韻地位: The profile of the upper (initial) character.
        下字音韻地位: The profile of the lower (rime) character.

    Returns:
        list[音韻地位]: All combinations that pass 音韻地位 validation.
    """
    母 = 上字音韻地位.母
    組 = 上字音韻地位.組
    上字呼 = 上字音韻地位.呼
    上字等 = 上字音韻地位.等
    上字類 = 上字音韻地位.類
    default_logger.log(f"反切上字為{母}母，故被切字為{母}母")

    韻 = 下字音韻地位.韻
    聲 = 下字音韻地位.聲
    下字呼 = 下字音韻地位.呼
    下字組 = 下字音韻地位.組
    下字等 = 下字音韻地位.等
    default_logger.log(f"反切下字為{韻}韻{聲}聲，故被切字為{韻}韻{聲}聲")

    所有呼 = generate呼(母, 組, 韻, 上字呼, 下字呼, 下字組)
    所有等 = generate等(母, 韻, 上字等, 下字等)

    # 在特定呼、特定等的條件下處理類
    results: list[音韻地位] = []

    條件_解釋: list[tuple[str, str | None]] = []
    忽略: list[str] = []

    for 呼 in 所有呼:
        for 等 in 所有等:
            if len(所有呼) > 1 and len(所有等) > 1:
                條件 = f"當呼為{呼}口、等為{等}等時，"
            elif len(所有呼) > 1:
                條件 = f"當呼為{呼}口時，"
            elif len(所有等) > 1:
                條件 = f"當等為{等}等時，"
            else:
                條件 = ""

            決策 = rawGenerate類(下字音韻地位, 母, 組, 韻, 上字類, 呼, 等)
            條件_解釋.append((條件, 決策.解釋))
            類列表 = ["A", "B"] if 決策.類 == "AB" else [決策.類]
            for 類 in 類列表:
                try:
                    results.append(音韻地位(母, 呼, 等, 類, 韻, 聲))
                except ValueError as exc:
                    忽略.append(
                        f"忽略無效的音韻地位「{母}{呼 or ''}{等}{類 or ''}{韻}{聲}」，原因：{exc}"
                    )

    if 條件_解釋:
        解釋集合 = {解釋 for _, 解釋 in 條件_解釋}
        # 如果所有解釋均相同，則只需輸出一次解釋，無需輸出條件
        if len(解釋集合) == 1:
            唯一 = next(iter(解釋集合))
            if 唯一:
                default_logger.log(唯一)
                # 如果解釋不全相同，則對每個條件，都輸出對應的解釋
        else:
            for 條件, 解釋 in 條件_解釋:
                if 解釋:
                    default_logger.log(f"{條件}{解釋}")

    for msg in 忽略:
        default_logger.log(msg)

    return results


__all__ = ["執行反切"]
