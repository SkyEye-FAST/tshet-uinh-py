"""Validate 廣韻 dataset helpers against iterator, count, and CSV invariants."""

# ruff: noqa: N801,N802,N803,N806

from pathlib import Path

from tshet_uinh.data import 廣韻

DATA_CSV = Path(__file__).resolve().parents[1] / "prepare" / "data.csv"


def collect字頭(entries: list[廣韻.廣韻條目]) -> list[str]:
    """Return a simple list of 字頭 so ordering comparisons stay readable."""
    return [entry.字頭 for entry in entries]


def test_get小韻_and_get原書小韻() -> None:
    """Cross-check split 小韻 data against its unsplit counterpart."""
    小韻3708a = 廣韻.get小韻("3708a")
    小韻3708b = 廣韻.get小韻("3708b")
    assert 小韻3708a is not None
    assert 小韻3708b is not None
    assert len(小韻3708a) == 15
    assert 小韻3708a[0].字頭 == "憶"
    assert len(小韻3708b) == 2
    assert 小韻3708b[0].字頭 == "抑"

    原書小韻3708 = 廣韻.get原書小韻(3708)
    assert 原書小韻3708 is not None
    assert len(原書小韻3708) == 17

    combined = [*collect字頭(小韻3708a), *collect字頭(小韻3708b)]
    assert sorted(combined) == sorted(collect字頭(原書小韻3708))

    小韻597 = 廣韻.get小韻("597")
    assert 小韻597 is not None
    assert collect字頭(小韻597) == ["𤜼"]
    assert 小韻597[0].音韻地位 is None


def test_原書小韻總數() -> None:
    """Ensure the exposed constant matches the canonical 小韻 count."""
    assert 廣韻.原書小韻總數 == 3874


def test_iterators_remain_in_lockstep() -> None:
    """Verify iter原書小韻 and iter條目 walk through data in the same order."""
    條目iterator = iter(廣韻.iter條目())

    for 原書小韻 in 廣韻.iter原書小韻():
        for 條目1 in 原書小韻:
            條目2 = next(條目iterator, None)
            assert 條目2 is not None
            assert 條目1.來源.小韻號 == 條目2.來源.小韻號
            assert 條目1.來源.韻目 == 條目2.來源.韻目
            描述1 = None if 條目1.音韻地位 is None else 條目1.音韻地位.描述
            描述2 = None if 條目2.音韻地位 is None else 條目2.音韻地位.描述
            assert 描述1 == 描述2
            assert 條目1.反切 == 條目2.反切
            assert 條目1.字頭 == 條目2.字頭
            assert 條目1.釋義 == 條目2.釋義

    assert next(條目iterator, None) is None


def test_iter條目_matches_original_csv_dump() -> None:
    """Compare iter條目 output against the raw CSV export row by row."""
    條目iterator = iter(廣韻.iter條目())
    lines = DATA_CSV.read_text(encoding="utf-8").rstrip("\n").splitlines()
    header, *rows = lines
    assert header.startswith("小韻號"), "Unexpected CSV header"

    for line in rows:
        (
            小韻號,
            _index,
            韻目原貌,
            地位描述,
            反切,
            字頭,
            釋義,
            釋義補充,
        ) = line.split(",")

        條目 = next(條目iterator, None)
        assert 條目 is not None
        assert 條目.來源.小韻號 == 小韻號
        assert 條目.來源.韻目 == 韻目原貌
        描述 = "" if 條目.音韻地位 is None else 條目.音韻地位.描述
        assert 描述 == 地位描述
        assert (條目.反切 or "") == (反切 or "")
        定義補充 = f"（{釋義補充}）" if 釋義補充 else ""
        assert 條目.字頭 == 字頭
        assert 條目.釋義 == f"{釋義}{定義補充}"

    assert next(條目iterator, None) is None
