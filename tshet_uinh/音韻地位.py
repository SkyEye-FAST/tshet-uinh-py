"""Core representation of 《切韻》音韻地位 used throughout the project."""

# ruff: noqa: N801,N802,N803,N806

import re
from collections.abc import Callable, Mapping, Sequence
from typing import Any, TypeVar, cast

from .utils import assert_condition
from .音韻屬性常量 import (
    呼韻搭配,
    所有,
    母到清濁,
    母到組,
    母到音,
    等母搭配,
    等韻搭配,
    鈍音母,
    陰聲韻,
    韻到攝,
)

pattern描述 = re.compile(
    rf"^([{''.join(所有['母'])}])([{''.join(所有['呼'])}]?)"
    rf"([{''.join(所有['等'])}]?)([{''.join(所有['類'])}]?)"
    rf"([{''.join(所有['韻'])}])([{''.join(所有['聲'])}])$"
)

# for 音韻地位.屬於
表達式屬性可取值: dict[str, Sequence[str]] = {
    **所有,
    "音": list("脣舌齒牙喉"),
    "攝": list("通江止遇蟹臻山效果假宕梗曾流深咸"),
    "組": list("幫端知精莊章見影"),
}

T = TypeVar("T")

判斷規則 = tuple[object, T | "判斷規則列表[T]"]
判斷規則列表 = Sequence[判斷規則[T]]
邊緣地位種類指定 = Sequence[str]
部分音韻屬性 = Mapping[str, str | None]

已知邊緣地位 = {
    "並三A陽上",
    "定開四脂去",
    "端開二庚上",
    "端開二麻上",
    "端開四麻平",
    "端開四麻上",
    "定開二佳上",
    "端四尤平",
    "云開三C之上",
    "云開三B仙平",
}

_UNCHECKED: 邊緣地位種類指定 = ("@UNCHECKED@",)


class 音韻地位:
    """Encapsulates a single 《切韻》音韻地位.

    Use this type whenever code needs to reason about the six canonical attributes
    （母、呼、等、類、韻、聲） alongside optional 邊緣地位 allowances.
    """

    __slots__ = ("母", "呼", "等", "類", "韻", "聲")

    母: str
    呼: str | None
    等: str
    類: str | None
    韻: str
    聲: str

    def __init__(
        self,
        母: str,
        呼: str | None,
        等: str,
        類: str | None,
        韻: str,
        聲: str,
        邊緣地位種類: 邊緣地位種類指定 | None = None,
    ) -> None:
        """Validate and persist the six attributes.

        Args:
            母: 幫, 滂, 並, 明, …
            呼: 開, 合 or None
            等: 一, 二, 三, 四
            類: A/B indicate a front-vowel (重紐),
                C indicates a non-front vowel,
                or None.
            韻: 東, 冬, 鍾, 江, …, 祭, 泰, 夬, 廢
            聲: 平, 上, 去, 入
            邊緣地位種類: Optional whitelist of marginal 音韻地位 kinds.

        Raises:
            ValueError: If any attribute violates the phonological constraints.
        """
        type(self).驗證(母, 呼, 等, 類, 韻, 聲, 邊緣地位種類 or ())
        self.母 = 母
        self.呼 = 呼
        self.等 = 等
        self.類 = 類
        self.韻 = 韻
        self.聲 = 聲

    @property
    def 清濁(self) -> str:
        """Return the voicing class derived from the initial (全清, 次清, 全濁, 次濁)."""
        return 母到清濁[self.母]

    @property
    def 音(self) -> str:
        """Return the articulatory group (脣, 舌, 齒, 牙, 喉)."""
        return 母到音[self.母]

    @property
    def 攝(self) -> str:
        """Return the 攝 associated with the current rime."""
        return 韻到攝[self.韻]

    @property
    def 韻別(self) -> str:
        """Return whether the rime belongs to 陰, 陽 or 入."""
        if self.聲 == "入":
            return "入"
        return "陰" if self.韻 in 陰聲韻 else "陽"

    @property
    def 組(self) -> str | None:
        """Return the initial group name, if defined."""
        return 母到組[self.母]

    @property
    def 描述(self) -> str:
        """Return the canonical concatenated description string."""
        呼 = self.呼 or ""
        類 = self.類 or ""
        return f"{self.母}{呼}{self.等}{類}{self.韻}{self.聲}"

    @property
    def 簡略描述(self) -> str:
        """Return a compact description with redundant fields omitted."""
        呼 = self.呼
        類 = self.類
        等 = self.等
        if 類 and 類搭配(self.母, self.韻)[0] == 類:
            類 = None
        if 呼 == "合" and self.母 == "云":
            呼 = None
        elif 呼 and self.韻 in 呼韻搭配[呼]:
            呼 = None
        if 等 == "三" and self.母 in "羣邪俟":
            等 = ""
        elif self.母 in 等母搭配["三"] or self.韻 not in (*等韻搭配["一三"], *等韻搭配["二三"]):
            等 = ""
        return f"{self.母}{呼 or ''}{等}{類 or ''}{self.韻}{self.聲}"

    @property
    def 表達式(self) -> str:
        """Produce the expression used by :meth:`屬於`."""
        呼字段 = f"{self.呼}口 " if self.呼 else "開合中立 "
        類字段 = f"{self.類}類 " if self.類 else "不分類 "
        return f"{self.母}母 {呼字段}{self.等}等 {類字段}{self.韻}韻 {self.聲}聲"

    @property
    def 字母(self) -> str:
        """Return the 三十六字母 label that corresponds to the initial."""
        if self.等 == "三" and self.類 == "C" and self.母 in "幫滂並明":
            idx = "幫滂並明".index(self.母)
            return "非敷奉微"[idx]
        if self.母 in "莊初崇生俟章昌船書常":
            idx = "莊初崇生俟章昌船書常".index(self.母)
            return "照穿牀審禪"[idx % 5]
        if self.母 in {"云", "以"}:
            return "喻"
        return self.母

    @property
    def 韻圖等(self) -> str:
        """Return the adjusted division index used by the 韻鏡."""
        if self.母 in "莊初崇生俟":
            return "二"
        if self.類 == "A" or (self.等 == "三" and self.母 in "精清從心邪以"):
            return "四"
        return self.等

    def 調整(
        self,
        調整屬性: 部分音韻屬性 | str,
        邊緣地位種類: 邊緣地位種類指定 | None = None,
    ) -> "音韻地位":
        """Return a new instance with selected attributes overwritten.

        The original instance remains unchanged.

        Args:
            調整屬性: Either a whitespace-delimited string or a mapping of overrides.
            邊緣地位種類: Optional marginal whitelist forwarded to the constructor.

        Raises:
            ValueError: Propagated from the constructor when validation fails.
        """
        if isinstance(調整屬性, str):
            屬性object: dict[str, str | None] = {}

            def set_attr(屬性: str, value: str | None) -> None:
                assert_condition(屬性 not in 屬性object, f"duplicated assignment of {屬性}")
                屬性object[屬性] = value

            for token in 調整屬性.strip().split():
                if token == "開合中立":
                    set_attr("呼", None)
                    continue
                if token == "不分類":
                    set_attr("類", None)
                    continue
                match = re.match(r"^(.)([母口等類韻聲])$", token)
                if not match:
                    raise ValueError(f"unrecognized expression: {token}")
                value, key = match.groups()
                set_attr("呼" if key == "口" else key, value)
            attrs: 部分音韻屬性 = 屬性object
        else:
            attrs = 調整屬性

        母 = cast(str, attrs.get("母", self.母))
        呼 = attrs.get("呼", self.呼)
        等 = cast(str, attrs.get("等", self.等))
        類 = attrs.get("類", self.類)
        韻 = cast(str, attrs.get("韻", self.韻))
        聲 = cast(str, attrs.get("聲", self.聲))
        return type(self)(母, 呼, 等, 類, 韻, 聲, 邊緣地位種類 or ())

    @staticmethod
    def 驗證(
        母: str,
        呼: str | None,
        等: str,
        類: str | None,
        韻: str,
        聲: str,
        邊緣地位種類: 邊緣地位種類指定,
    ) -> None:
        """Validate the six attributes against phonological constraints.

        Args:
            母: Initial consonant.
            呼: Rounding marker.
            等: Division.
            類: 重紐類別。
            韻: Rime label.
            聲: Tone category.
            邊緣地位種類: Explicit marginal whitelist entries.

        Raises:
            ValueError: If any constraint fails.
        """

        def reject(msg: str) -> None:
            raise ValueError(f"invalid 音韻地位 <{母},{呼 or ''},{等},{類 or ''},{韻},{聲}>: {msg}")

        for 屬性, 值, nullable in (
            ("母", 母, False),
            ("呼", 呼, True),
            ("等", 等, False),
            ("類", 類, True),
            ("韻", 韻, False),
            ("聲", 聲, False),
        ):
            if 值 is None:
                if not nullable:
                    reject(f"missing {屬性}")
                continue
            if 值 not in 所有[屬性]:
                replacements: dict[str, dict[str, str]] = {
                    "母": {"娘": "孃", "群": "羣"},
                    "韻": {"眞": "真", "欣": "殷"},
                }
                suggestion = replacements.get(屬性, {}).get(值)
                extra = f" (did you mean: {suggestion}?)" if suggestion else ""
                reject(f"unrecognized {屬性}: {值}{extra}")

        if 聲 == "入" and 韻 in 陰聲韻:
            reject(f"unexpected {韻}韻入聲")

        for 搭配等, 搭配母 in 等母搭配.items():
            if 母 in 搭配母 and 等 not in 搭配等:
                reject(f"unexpected {母}母{等}等")

        for 搭配各等, 搭配各韻 in 等韻搭配.items():
            if 韻 in 搭配各韻:
                if 等 in 搭配各等:
                    break
                if "三" in 搭配各等 and 等 == "四" and 母 in "端透定泥":
                    break
                reject(f"unexpected {韻}韻{等}等")

        if 母 in "幫滂並明":
            if 呼 is not None:
                reject("unexpected 呼 for 脣音")
        elif 韻 in 呼韻搭配["中立"]:
            if 呼 is not None:
                reject("unexpected 呼 for 開合中立韻")
        elif 韻 in {*呼韻搭配["開"], *呼韻搭配["合"], *呼韻搭配["開合"]}:
            expected: str | None
            if 韻 in 呼韻搭配["開合"]:
                expected = None
            elif 韻 in 呼韻搭配["開"]:
                expected = "開"
            elif 韻 in 呼韻搭配["合"]:
                expected = "合"
            else:
                expected = None
            if expected is None:
                if 呼 not in {"開", "合"}:
                    reject("missing 呼 (should be 開或合)")
            elif 呼 == expected:
                pass
            elif 呼 is None:
                reject(f"missing 呼 (should be {expected})")
            else:
                reject(f"unexpected {韻}韻{呼}口")
        else:
            if 呼 not in {"開", "合"}:
                reject("missing 呼")

        if 等 != "三":
            if 類 is not None:
                reject("unexpected 類 for 非三等")
        elif 母 not in 鈍音母:
            if 類 is not None:
                reject("unexpected 類 for 銳音聲母")
        else:
            典型搭配類, 可用類 = 類搭配(母, 韻)
            if 類 is None:
                suggestion = (
                    f" (should be {典型搭配類} typically)"
                    if len(典型搭配類) == 1 and 典型搭配類 != 可用類
                    else ""
                )
                reject(f"missing 類{suggestion}")
            elif 類 not in 可用類:
                if 母 == "云" and 類 == "A":
                    reject("unexpected 云母A類")
                reject(f"unexpected {韻}韻{類}類")

        if 母 in "幫滂並明":
            if 韻 in "之魚殷痕嚴":
                reject(f"unexpected {韻}韻脣音")
        elif 韻 == "凡":
            reject("unexpected 凡韻非脣音")

        if 母 in "莊初崇生俟":
            if 等 == "三" and 韻 == "清":
                reject(f"unexpected {韻}韻莊組")
            if 呼 == "開" and 韻 in {"真", "殷"}:
                reject(f"unexpected {韻}韻開口莊組")
        else:
            if 韻 == "臻":
                reject("unexpected 臻韻非莊組")
            if 韻 == "庚" and 等 != "二" and 母 not in 鈍音母:
                reject(f"unexpected 庚韻{等}等{母}母")

        if 邊緣地位種類 == _UNCHECKED or (
            母 + (呼 or "") + 等 + (類 or "") + 韻 + 聲 in 已知邊緣地位
        ):
            return

        邊緣地位指定集 = set(邊緣地位種類)
        assert_condition(
            len(邊緣地位指定集) == len(tuple(邊緣地位種類)),
            "duplicates in 邊緣地位種類",
        )

        marginal_tests = [
            ("陽韻A類", True, 韻 == "陽" and 類 == "A", "陽韻A類"),
            (
                "端組類隔",
                True,
                母 in "端透定泥" and (等 == "二" or (等 == "四" and 韻 not in 等韻搭配["四"])),
                f"{韻}韻{等}等{母}母",
            ),
            ("咍韻脣音", True, 韻 == "咍" and 母 in "幫滂並明", "咍韻脣音"),
            ("匣母三等", True, 母 == "匣" and 等 == "三", "匣母三等"),
            ("羣邪俟母非三等", True, 母 in "羣邪俟" and 等 != "三", f"{母}母{等}等"),
            ("云母開口", False, 母 == "云" and 呼 == "開" and 韻 not in "宵幽侵鹽嚴", "云母開口"),
        ]

        known_kinds = {kind for kind, *_ in marginal_tests}
        for kind in 邊緣地位種類:
            if kind not in known_kinds:
                raise ValueError(f"unknown type of marginal 音韻地位: {kind}")

        for kind, strict, condition, errmsg in marginal_tests:
            if condition and kind not in 邊緣地位指定集:
                suffix = "" if strict else f" (note: marginal 音韻地位, include '{kind}' to allow)"
                reject(f"unexpected {errmsg}{suffix}")
            if strict and not condition and kind in 邊緣地位指定集:
                reject(
                    "expect marginal 音韻地位: "
                    f"{kind} (note: don't specify unless it describes this 音韻地位)"
                )

    @classmethod
    def from描述(
        cls,
        音韻描述: str,
        簡略描述: bool = False,
        邊緣地位種類: 邊緣地位種類指定 | None = None,
    ) -> "音韻地位":
        """Parse a textual description into an :class:`音韻地位`.

        Args:
            音韻描述: Description string containing 母、呼、等、類、韻、聲.
            簡略描述: Allow omitting fields that can be inferred.
            邊緣地位種類: Optional marginal whitelist forwarded to the constructor.

        Raises:
            ValueError: When the description is malformed or missing不可推導的等值.
        """
        match = pattern描述.match(音韻描述)
        if not match:
            raise ValueError(f"invalid 描述: {音韻描述}")
        母, 呼, 等, 類, 韻, 聲 = match.groups()
        呼 = 呼 or None
        類 = 類 or None
        等 = 等 or ""
        if not 等 and not 簡略描述:
            raise ValueError("等 is required in 描述")

        if 簡略描述:
            if not 呼 and 母 not in "幫滂並明":
                if 母 == "云" and 韻 in 呼韻搭配["開合"]:
                    呼 = "合"
                else:
                    for 呼候選 in ("開", "合"):
                        if 韻 in 呼韻搭配[呼候選]:
                            呼 = 呼候選
                            break
            if not 等:
                if 母 in (*等母搭配["三"], *"羣邪俟"):
                    等 = "三"
                else:
                    for 等候選 in ("一", "二", "三", "四"):
                        if 韻 in 等韻搭配.get(等候選, ()):
                            if 等候選 == "三" and 母 in "端透定泥":
                                等 = "四"
                            else:
                                等 = 等候選
                            break
            if not 類 and 等 == "三" and 母 in 鈍音母:
                典型搭配類, _ = 類搭配(母, 韻)
                if len(典型搭配類) == 1:
                    類 = 典型搭配類
            if not 等:
                raise ValueError("等 is required in 描述")

        return cls(母, 呼, 等, 類, 韻, 聲, 邊緣地位種類 or ())

    def 等於(self, other: "音韻地位") -> bool:
        """Return ``True`` when both objects share the same 描述 string."""
        return self.描述 == other.描述

    def __str__(self) -> str:
        """Return the canonical 描述 string."""
        return self.描述

    def 屬於(self, 表達式: str | Sequence[str], *參數: object) -> bool:
        """Evaluate whether this 音韻地位 satisfies the expression.

        Args:
            表達式: String or sequence of strings containing logical operators.
            *參數: Optional delayed conditions evaluated lazily.

        Raises:
            ValueError: When the expression is malformed or references unknown terms.
        """
        segments: list[str] = [表達式] if isinstance(表達式, str) else list(表達式)
        tokens: list[tuple[object, str]] = []
        for index, segment in enumerate(segments):
            for raw in _tokenize(segment):
                token = _classify_token(raw)
                if token in {"(", ")", "and", "or", "not"}:
                    tokens.append((token, raw))
                else:
                    tokens.append((_eval_token(self, raw), raw))
            if index < len(參數):
                lazy = LazyParameter.from_value(參數[index], self)
                tokens.append((lazy, str(lazy)))

        if not tokens:
            raise ValueError("empty expression")

        cursor = 0
        end_token = ("end", "end of expression")

        def peek() -> tuple[object, str]:
            return tokens[cursor] if cursor < len(tokens) else end_token

        def read() -> tuple[object, str]:
            nonlocal cursor
            token = tokens[cursor] if cursor < len(tokens) else end_token
            cursor += 1 if cursor < len(tokens) else 0
            return token

        def parse_or(required: bool) -> object | None:
            first = parse_and(required)
            if first is None:
                return None
            operands = [first]
            while True:
                token, _ = peek()
                if token == "or":
                    read()
                    operands.append(parse_and(True))
                else:
                    break
            if len(operands) == 1:
                return operands[0]
            return ("or", operands)

        def parse_and(required: bool) -> object | None:
            first = parse_not(required)
            if first is None:
                return None
            operands = [first]
            while True:
                token, _ = peek()
                if token == "and":
                    read()
                    operands.append(parse_not(True))
                    continue
                next_operand = parse_not(False)
                if next_operand is None:
                    break
                operands.append(next_operand)
            if len(operands) == 1:
                return operands[0]
            return ("and", operands)

        def parse_not(required: bool) -> object | None:
            negate = False
            seen_not = False
            while True:
                token, _ = peek()
                if token == "not":
                    seen_not = True
                    negate = not negate
                    read()
                else:
                    break
            token, raw = peek()
            if isinstance(token, (bool, LazyParameter)):
                read()
                operand = token
            elif token == "(":
                read()
                operand = parse_or(True)
                closing, closing_raw = read()
                if closing != ")":
                    raise ValueError(f"expect ')', got: {closing_raw}")
            elif seen_not or required:
                expected = "operand or '('" if seen_not else "expression"
                raise ValueError(f"expect {expected}, got: {raw}")
            else:
                return None
            if negate:
                return ("not", [operand])
            return operand

        expr = parse_or(True)
        if read()[0] != "end":
            raise ValueError("unexpected trailing tokens")

        def eval_operand(operand: object) -> bool:
            if isinstance(operand, bool):
                return operand
            if isinstance(operand, LazyParameter):
                return operand.eval()
            if not isinstance(operand, tuple) or len(operand) != 2:
                raise ValueError("invalid expression tree")
            op, operands_obj = operand
            if not isinstance(operands_obj, list):
                raise ValueError("invalid operand list")
            operands = operands_obj
            if op == "not":
                return not eval_operand(operands[0])
            if op == "and":
                return all(eval_operand(item) for item in operands)
            if op == "or":
                return any(eval_operand(item) for item in operands)
            raise ValueError(f"unknown operator: {op}")

        return eval_operand(expr)

    def 判斷(
        self,
        規則: 判斷規則列表[T],
        throws: bool | str = False,
        fall_through: bool = False,
    ) -> T | None:
        """Evaluate a nested decision table and return the associated payload.

        Args:
            規則: Sequence of ``(condition, result)`` pairs; results may be nested rule lists.
            throws: ``True`` or a custom string to raise when nothing matches.
            fall_through: Whether to continue evaluating after nested Exhaustion.

        Returns:
            T | None: Matched payload, or ``None`` if nothing matched and ``throws`` is ``False``.

        Raises:
            ValueError: Raised for invalid rule shapes, parse failures, or when ``throws`` requests
                an exception.
        """
        Exhaustion = object()

        def is_rule_list(obj: object) -> bool:
            if not isinstance(obj, Sequence) or isinstance(obj, (str, bytes)):
                return False
            return all(
                isinstance(item, Sequence) and not isinstance(item, (str, bytes)) and len(item) == 2
                for item in obj
            )

        def loop(rule_list: 判斷規則列表[T]) -> T | object:
            for 規則項 in rule_list:
                if len(規則項) != 2:
                    raise ValueError("規則需符合格式")
                表達式, 結果 = 規則項
                if callable(表達式):
                    表達式 = 表達式()
                if isinstance(表達式, str):
                    condition = bool(表達式) and self.屬於(表達式)
                else:
                    condition = bool(表達式)
                if condition:
                    if is_rule_list(結果):
                        res = loop(cast(判斷規則列表[T], 結果))
                        if res is Exhaustion and fall_through:
                            continue
                        return res
                    return cast(T, 結果)
            return Exhaustion

        result = loop(規則)
        if result is Exhaustion:
            if throws is False:
                return None
            message = throws if isinstance(throws, str) else "未涵蓋所有條件"
            raise ValueError(message)
        return cast(T, result)


def 類搭配(母: str, 韻: str) -> tuple[str, str]:
    """Return the typical and permissible 重紐類 pairing for the given rime.

    Args:
        母: Initial consonant.
        韻: Rime label.

    Raises:
        ValueError: If the rime is not part of the supported inventory.
    """
    pairs = [
        ("C", list("東鍾之微魚虞廢殷元文歌尤嚴凡")),
        ("AB", list("支脂祭真仙宵麻幽侵鹽")),
        ("A", ["清"]),
        ("B", ["庚"]),
        ("BC", ["蒸"]),
        ("CA", ["陽"]),
    ]
    result: tuple[str, str] | None = None
    for 類組, 韻組 in pairs:
        if 韻 in 韻組:
            normalized = "C" if 類組 == "CA" else 類組
            result = (normalized, 類組)
            break
    if result is None:
        raise ValueError(f"unknown 韻: {韻}")
    if 母 == "云":
        normalized = result[0].replace("A", "")
        return normalized, result[1].replace("A", "")
    return result


def _tokenize(segment: str) -> list[str]:
    """Split a condition string into tokens while tolerating full-width symbols."""
    normalized = segment.replace("（", "(").replace("）", ")")
    tokens: list[str] = []
    i = 0
    while i < len(normalized):
        ch = normalized[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "()!~":
            tokens.append(ch)
            i += 1
            continue
        if ch in "&|":
            j = i
            while j < len(normalized) and normalized[j] == ch:
                j += 1
            tokens.append(normalized[i:j])
            i = j
            continue
        start = i
        while i < len(normalized) and not normalized[i].isspace() and normalized[i] not in "()!~&|":
            i += 1
        tokens.append(normalized[start:i])
    return tokens


def _classify_token(raw: str) -> object:
    """Map raw token text to logical markers or literal strings."""
    lowered = raw.lower()
    if raw == "(":
        return "("
    if raw == ")":
        return ")"
    if raw in {"!", "~", "非"} or lowered == "not":
        return "not"
    if raw in {"且"} or lowered == "and" or set(raw) == {"&"}:
        return "and"
    if raw in {"或"} or lowered == "or" or set(raw) == {"|"}:
        return "or"
    if raw == "&&":
        return "and"
    if raw == "||":
        return "or"
    return raw


def _eval_token(obj: 音韻地位, token: str) -> bool:
    """Evaluate a single predicate token against the given 音韻地位."""
    token = token.strip()
    if not token:
        return True
    match = re.match(r"^(陰|陽|入)聲韻$", token)
    if match:
        return obj.韻別 == match.group(1)
    if token == "仄聲":
        return obj.聲 != "平"
    if token == "舒聲":
        return obj.聲 != "入"
    match = re.match(r"^(開|合)口$", token)
    if match:
        return obj.呼 == match.group(1)
    if token == "開合中立":
        return obj.呼 is None
    if token == "不分類":
        return obj.類 is None
    match = re.match(r"^(清|濁)音$", token)
    if match:
        return obj.清濁.endswith(match.group(1))
    match = re.match(r"^[全次][清濁]$", token)
    if match:
        return obj.清濁 == match.group(0)
    if token == "鈍音":
        return obj.母 in 鈍音母
    if token == "銳音":
        return obj.母 not in 鈍音母
    match = re.match(r"^(.+?)([母等類韻音攝組聲])$", token)
    if match:
        values = list(match.group(1))
        key = match.group(2)
        possible = 表達式屬性可取值.get(key)
        if possible is None:
            raise ValueError(f"unknown key: {key}")
        invalid = [value for value in values if value not in possible]
        if invalid:
            raise ValueError(f"unknown {key}: {', '.join(invalid)}")
        attr_map = {
            "母": obj.母,
            "等": obj.等,
            "類": obj.類,
            "韻": obj.韻,
            "音": obj.音,
            "攝": obj.攝,
            "組": obj.組,
            "聲": obj.聲,
        }
        value = attr_map.get(key)
        return value in values
    raise ValueError(f"unrecognized test condition: {token}")


class LazyParameter:
    """Wrap a delayed predicate used inside :meth:`屬於`."""

    def __init__(self, inner: Callable[[], Any], 地位: 音韻地位):
        """Store the deferred callable and the 音韻地位 used for evaluation."""
        self._inner: Callable[[], Any] | bool | str = inner
        self._地位 = 地位

    @classmethod
    def from_value(cls, param: object, 地位: "音韻地位") -> "bool | LazyParameter":
        """Normalize arbitrary parameters into either booleans or lazy predicates."""
        if isinstance(param, str):
            return 地位.屬於(param)
        if callable(param):
            return cls(param, 地位)
        return bool(param)

    def eval(self) -> bool:
        """Evaluate (and memoize) the predicate result."""
        if callable(self._inner):
            value = self._inner()
            if isinstance(value, str):
                self._inner = self._地位.屬於(value)
            else:
                self._inner = bool(value)
        return bool(self._inner)

    def __str__(self) -> str:
        """Return a debug-friendly representation of the cached payload."""
        return str(self._inner)


__all__ = [
    "音韻地位",
    "判斷規則列表",
    "邊緣地位種類指定",
    "部分音韻屬性",
    "LazyParameter",
    "_UNCHECKED",
]
