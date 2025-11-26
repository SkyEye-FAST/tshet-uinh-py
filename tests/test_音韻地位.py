"""Comprehensive regression tests for the 音韻地位 API."""

# ruff: noqa: N801,N802,N803,N806

import pytest

from tshet_uinh.資料 import iter音韻地位
from tshet_uinh.音韻地位 import 判斷規則列表, 音韻地位

CONCISE_CASES = [
    ("精開三鹽平", "精鹽平", "省略呼、等"),
    ("見開二佳平", "見開佳平", "省略等（按韻）"),
    ("章開三麻上", "章開麻上", "省略等（按聲母）"),
    ("定開四脂去", "定開脂去", "省略等（特殊）"),
    ("幫三C凡入", "幫凡入", "省略C類"),
    ("見開三B庚平", "見開三庚平", "省略B類"),
    ("明三A清平", "明清平", "省略等、A類"),
    ("云合三B支去", "云支去", "省略呼、等、類"),
    ("云合三B蒸入", "云B蒸入", "不省略類"),
    ("見開一歌平", "見開一歌平", "不省略"),
    ("端開四麻平", "端開四麻平", "不省略"),
]
CONCISE_CASE_IDS = [case[0] for case in CONCISE_CASES]

INVALID_DESCRIPTION_CASES = [
    ("精開三祭入", r"unexpected 祭韻入聲"),
    ("莊開二陽平", r"unexpected 陽韻二等"),
    ("定開三脂去", r"unexpected 定母三等"),
    ("明合一魂平", r"unexpected 呼 for 脣音"),
    ("端開一東平", r"unexpected 呼 for 開合中立韻"),
    ("章三麻平", r"missing 呼"),
    ("見合三A幽上", r"unexpected 幽韻合口"),
    ("幫四A先平", r"unexpected 類 for 非三等"),
    ("章開三A支平", r"unexpected 類 for 銳音聲母"),
    ("云合三A支平", r"unexpected 云母A類"),
    ("明三清上", r"missing 類"),
    ("幫三B清入", r"unexpected 清韻B類"),
    ("明三陽去", r"missing 類 \(should be C typically\)"),
    ("幫三C嚴入", r"unexpected 嚴韻脣音"),
    ("幫三C之平", r"unexpected 之韻脣音"),
    ("初開三真去", r"unexpected 真韻開口莊組"),
    ("知開三庚平", r"unexpected 庚韻三等知母"),
]
INVALID_DESCRIPTION_IDS = [case[0] for case in INVALID_DESCRIPTION_CASES]


def test_凡入_attributes() -> None:
    """Verify derived attributes for 幫三C凡入."""
    current = 音韻地位.from描述("幫三C凡入")

    assert current.母 == "幫"
    assert current.呼 is None
    assert current.等 == "三"
    assert current.類 == "C"
    assert current.韻 == "凡"
    assert current.聲 == "入"

    assert current.清濁 == "全清"
    assert current.音 == "脣"
    assert current.攝 == "咸"

    assert current.描述 == "幫三C凡入"
    assert current.簡略描述 == "幫凡入"
    assert current.表達式 == "幫母 開合中立 三等 C類 凡韻 入聲"

    assert current.等於(音韻地位.from描述("幫凡入", True))


def test_支平_attributes() -> None:
    """Verify derived attributes for 羣開三A支平."""
    current = 音韻地位.from描述("羣開三A支平")

    assert current.母 == "羣"
    assert current.呼 == "開"
    assert current.等 == "三"
    assert current.類 == "A"
    assert current.韻 == "支"
    assert current.聲 == "平"

    assert current.清濁 == "全濁"
    assert current.音 == "牙"
    assert current.攝 == "止"

    assert current.描述 == "羣開三A支平"
    assert current.簡略描述 == "羣開A支平"
    assert current.表達式 == "羣母 開口 三等 A類 支韻 平聲"

    assert current.等於(音韻地位.from描述("羣開A支平", True))


def test_adjust_behaviour_and_validation() -> None:
    """Exercise 調整() flows and validation failures."""
    position = 音韻地位.from描述("幫三C元上")

    assert position.調整({"聲": "平"}).描述 == "幫三C元平"
    assert position.調整("平聲").描述 == "幫三C元平"
    with pytest.raises(ValueError, match=r"missing 呼"):
        position.調整({"母": "見"})
    assert position.調整({"母": "見", "呼": "合"}).描述 == "見合三C元上"
    assert position.調整("見母 合口").描述 == "見合三C元上"
    assert position.調整("仙韻 A類").描述 == "幫三A仙上"
    with pytest.raises(ValueError, match=r"unrecognized expression: 壞耶"):
        position.調整("壞耶")
    with pytest.raises(ValueError, match=r"unrecognized expression: 見影母"):
        position.調整("見影母")
    with pytest.raises(ValueError, match=r"duplicated assignment of 母"):
        position.調整("見母 影母")
    with pytest.raises(ValueError, match=r"unrecognized expression: 見母合口"):
        position.調整("見母合口")
    assert position.描述 == "幫三C元上"


def test_basic_membership() -> None:
    """Check simple 屬於 predicates for 幫三C凡入."""
    current = 音韻地位.from描述("幫三C凡入")

    assert current.屬於("幫母")
    assert current.屬於("幫精組")
    assert not current.屬於("精組")
    assert not current.屬於("AB類")
    assert current.屬於("C類")
    assert current.屬於("BC類")
    assert not current.屬於("喉音")
    assert current.屬於("仄聲")
    assert not current.屬於("舒聲")
    assert current.屬於("清音")
    assert not current.屬於("全濁")
    assert not current.屬於("次濁")
    assert current.屬於("開合中立")
    assert not current.屬於("開口 或 合口")
    assert current.屬於("幫組 C類")
    assert not current.屬於("陰聲韻")


def test_complex_membership_and_rules() -> None:
    """Cover advanced 屬於 expressions and 判斷() logic."""
    current = 音韻地位.from描述("幫三C凡入")

    assert current.屬於("非 一等")
    assert current.屬於("非 (一等)")
    assert current.屬於("非 ((一等))")
    assert current.屬於("非 (非 三等)")
    assert current.屬於("非 非 非 一等")
    assert current.屬於("三等 或 一等 且 來母")
    assert not current.屬於("(三等 或 一等) 且 來母")

    assert current.屬於(("一四等 或 ", ""), current.描述 == "幫三C凡入")
    assert current.屬於(("", " 或 ", ""), lambda: "三等", lambda: "短路〔或〕")
    assert not current.屬於(("非 ", " 且 ", ""), lambda: "三等", lambda: "短路〔且〕")

    with pytest.raises(ValueError, match=r"unrecognized test condition: 立即求值"):
        current.屬於(("", " 或 ", ""), lambda: "三等", "立即求值")

    result = current.判斷(
        [
            ("遇果假攝 或 支脂之佳韻", ""),
            ("蟹攝 或 微韻", "i"),
            ("效流攝", "u"),
            (
                "深咸攝",
                [
                    ("舒聲", "m"),
                    ("入聲", "p"),
                ],
            ),
            (
                "臻山攝",
                [
                    ("舒聲", "n"),
                    ("入聲", "t"),
                ],
            ),
            (
                "通江宕梗曾攝",
                [
                    ("舒聲", "ng"),
                    ("入聲", "k"),
                ],
            ),
        ],
        "無韻尾規則",
    )
    assert result == "p"


def test_invalid_expressions() -> None:
    """Ensure 屬於() rejects malformed expressions."""
    current = 音韻地位.from描述("幫三C凡入")
    belongs = current.屬於

    with pytest.raises(ValueError, match=r"empty expression"):
        belongs("")
    with pytest.raises(ValueError, match=r"expect expression, got: \)"):
        belongs("三等 且 ()")
    with pytest.raises(ValueError, match=r"expect expression, got: end of expression"):
        belongs("一等 或")
    with pytest.raises(ValueError, match=r"expect expression, got: 或"):
        belongs("或 一等")
    with pytest.raises(ValueError, match=r"expect expression, got: 或"):
        belongs("三等 且 (或 一等)")
    with pytest.raises(ValueError, match=r"expect operand or '\(', got: end of expression"):
        belongs("三等 且 非")
    with pytest.raises(ValueError, match=r"unknown 韻: 桓"):
        belongs("桓韻")
    with pytest.raises(ValueError, match=r"unknown 韻: 桓"):
        belongs(("", ""), "桓韻")
    with pytest.raises(ValueError, match=r"unknown 韻: 桓"):
        belongs("三等 或 桓韻")
    with pytest.raises(ValueError, match=r"unknown 類: 重, 紐"):
        belongs("重紐A類")


def test_rule_exceptions() -> None:
    """Confirm 判斷() reports invalid rule rows."""
    current = 音韻地位.from描述("幫三C凡入")

    with pytest.raises(ValueError, match=r"unknown 聲: 促"):
        current.判斷(
            [
                ("遇果假攝 或 支脂之佳韻", ""),
                (
                    "深咸攝",
                    [
                        ("舒聲", "m"),
                        ("促聲", "p"),
                    ],
                ),
                ("短路！", ""),
            ]
        )

    with pytest.raises(ValueError, match=r"壞耶"):
        current.判斷([], "壞耶")


def test_rule_null_and_fallthrough() -> None:
    """Validate fall-through behaviour of 判斷()."""
    current = 音韻地位.from描述("幫三C凡入")

    assert current.判斷([]) is None
    assert current.判斷([("見母", 42)]) is None

    rules: 判斷規則列表[int] = [
        ("幫組", []),
        ("幫母 凡韻", 43),
    ]
    assert current.判斷(rules) is None
    with pytest.raises(ValueError, match=r"壞耶"):
        current.判斷(rules, "壞耶")


@pytest.mark.parametrize(
    ("full", "concise", "message"),
    CONCISE_CASES,
    ids=CONCISE_CASE_IDS,
)
def test_concise_round_trip(full: str, concise: str, message: str) -> None:
    """Round-trip representative 簡略描述 cases."""
    position = 音韻地位.from描述(full)
    assert position.簡略描述 == concise, f"to 簡略描述: {message}"
    from_concise = 音韻地位.from描述(concise, True)
    assert from_concise.描述 == position.描述, f"from 簡略描述: {message}"


def test_symbolic_fields() -> None:
    """Verify 字母 and 韻圖等 projections."""
    assert 音韻地位.from描述("幫三C凡入").字母 == "非"
    assert 音韻地位.from描述("幫三B真平").字母 == "幫"
    assert 音韻地位.from描述("常開三清平").字母 == "禪"
    assert 音韻地位.from描述("常開三清平").韻圖等 == "三"
    assert 音韻地位.from描述("生開三庚平").字母 == "審"
    assert 音韻地位.from描述("生開三庚平").韻圖等 == "二"
    assert 音韻地位.from描述("精開三之上").韻圖等 == "四"
    assert 音韻地位.from描述("羣開三A支平").韻圖等 == "四"
    assert 音韻地位.from描述("羣開三B支平").韻圖等 == "三"
    assert 音韻地位.from描述("幫三C陽入").韻圖等 == "三"
    assert 音韻地位.from描述("見開三A幽上").韻圖等 == "四"
    assert 音韻地位.from描述("明三A清平").韻圖等 == "四"
    assert 音韻地位.from描述("並三A陽上").韻圖等 == "四"
    assert 音韻地位.from描述("云合三C虞平").字母 == "喻"
    assert 音韻地位.from描述("云合三C虞平").韻圖等 == "三"
    assert 音韻地位.from描述("以合三虞平").字母 == "喻"
    assert 音韻地位.from描述("以合三虞平").韻圖等 == "四"


def test_iterates_all_positions() -> None:
    """Iterate 資料 positions and confirm round-trip consistency."""
    for position in iter音韻地位():
        rebuilt = 音韻地位.from描述(position.描述)
        assert rebuilt.描述 == position.描述
        assert position.屬於(position.表達式)


def test_constructor_rejects_variant_characters() -> None:
    """Reject variant-character rime names in constructor."""
    with pytest.raises(ValueError, match=r"unrecognized 韻: 眞 \(did you mean: 真\?\)"):
        音韻地位("章", "開", "三", None, "眞", "平")


@pytest.mark.parametrize(
    ("description", "pattern"),
    INVALID_DESCRIPTION_CASES,
    ids=INVALID_DESCRIPTION_IDS,
)
def test_invalid_descriptions(description: str, pattern: str) -> None:
    """Validate error handling for illegal 描述 strings."""
    with pytest.raises(ValueError, match=pattern):
        音韻地位.from描述(description)


def test_marginal_expansion_cases() -> None:
    """Check the allowed values for 邊緣地位."""
    for description in [
        "影開三B蒸平",
        "影合三B蒸平",
        "影合三C蒸平",
        "知合三蒸平",
        "心合三蒸平",
        "生合三蒸平",
        "影開三B幽平",
        "知開三幽平",
        "心開三幽平",
        "章開三幽平",
        "並三B麻平",
    ]:
        assert 音韻地位.from描述(description).描述 == description

    for description in ["云開三B蒸平", "云開三C蒸平"]:
        with pytest.raises(ValueError, match=r"unexpected 云母開口 \(note: marginal 音韻地位"):
            音韻地位.from描述(description)
        assert 音韻地位.from描述(description, False, ["云母開口"]).描述 == description


def test_marginal_types() -> None:
    """Verify handling of 邊緣地位."""

    def passes(description: str, kinds: list[str]) -> None:
        assert 音韻地位.from描述(description, False, kinds).描述 == description

    def fails(description: str, kinds: list[str], pattern: str) -> None:
        with pytest.raises(ValueError, match=pattern):
            音韻地位.from描述(description, False, kinds)

    fails("見一東平", ["壞耶"], r"unknown type of marginal 音韻地位: 壞耶")

    passes("定開四脂去", [])
    passes("定開二佳上", [])
    passes("端四尤平", [])

    fails("透開二佳上", [], r"unexpected 佳韻二等透母")
    fails("端開四清上", [], r"unexpected 清韻四等端母")
    passes("端開四清上", ["端組類隔"])
    fails(
        "端開四青上",
        ["端組類隔"],
        r"expect marginal 音韻地位: 端組類隔 \(note: don't specify",
    )

    fails("云開三C之平", [], r"unexpected 云母開口 \(note: marginal 音韻地位")
    passes("云開三C之平", ["云母開口"])
    passes("云合三B支平", ["云母開口"])

    fails("泥開四陽上", [], r"unexpected 陽韻四等泥母")
    passes("泥開四陽上", ["端組類隔"])
    fails("端開四庚上", ["端組類隔"], r"unexpected 庚韻四等端母")

    fails("匣三C東平", [], r"unexpected 匣母三等")
    passes("匣三C東平", ["匣母三等"])
    passes("匣開三A真平", ["匣母三等"])
