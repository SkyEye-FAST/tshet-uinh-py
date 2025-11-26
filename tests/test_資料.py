"""Integration tests for the 資料 module queries."""

# ruff: noqa: N801,N802,N803,N806

from pathlib import Path

from tshet_uinh.資料 import query字頭, query音韻地位, 王三來源
from tshet_uinh.音韻地位 import 音韻地位

DATA_CSV = Path(__file__).resolve().parents[1] / "prepare" / "data.csv"


def test_query_head_returns_single_entry_for_東() -> None:
    """Confirm 東 has a single record with the expected 反切."""
    result = query字頭("東")
    assert len(result) == 1
    assert result[0].反切 == "德紅"


def test_query_head_handles_missing_反切() -> None:
    """Ensure characters lacking a 反切 return ``None``."""
    result = query字頭("拯")
    assert len(result) == 1
    assert result[0].反切 is None


def test_query_position_returns_multiple_反切() -> None:
    """Look up a 地位 that has multiple 反切 spellings."""
    position = 音韻地位.from描述("見開四添去")
    entries = query音韻地位(position)
    assert any(entry.字頭 == "趝" and entry.反切 == "紀念" for entry in entries)
    assert any(entry.字頭 == "兼" and entry.反切 == "古念" for entry in entries)


def test_query_position_finds_gwo_rhyme_characters() -> None:
    """戈韻 characters such as 戈/過 appear in the query results."""
    position = 音韻地位.from描述("見合一歌平")
    assert query音韻地位(position)


def test_query_position_returns_empty_when_no_characters() -> None:
    """Return an empty list when the 地位 has no attested characters."""
    position = 音韻地位.from描述("從合三歌平")
    assert query音韻地位(position) == []


def test_query_head_returns_full_metadata_for_zhi() -> None:
    """Verify 字頭「之」 exposes its 地位 and 釋義."""
    result = query字頭("之")
    assert len(result) == 1
    assert result[0].音韻地位.描述 == "章開三之平"
    assert result[0].釋義 == "適也往也閒也亦姓出姓苑止而切四"


def test_query_head_handles_polyphonic_entries() -> None:
    """Polyphonic 字頭 such as 過 should surface multiple readings."""
    result = query字頭("過")
    assert len(result) == 2


def test_query_head_returns_empty_for_unknown_characters() -> None:
    """Characters missing from the dataset should yield zero results."""
    assert query字頭("韓") == []


def test_query_head_includes_source_metadata() -> None:
    """來源 metadata should distinguish 廣韻 and 王三 sources."""
    fei_rhyme_entry = next(entry for entry in query字頭("茝") if entry.音韻地位.屬於("廢韻"))
    assert fei_rhyme_entry.來源 is not None
    assert fei_rhyme_entry.來源.文獻 == "廣韻"
    assert fei_rhyme_entry.來源.韻目 == "海"

    b_type_entry = next(entry for entry in query字頭("韻") if entry.音韻地位.屬於("B類"))
    assert isinstance(b_type_entry.來源, 王三來源)
    assert b_type_entry.來源.韻目 == "震"

    departing_tone_entry = next(entry for entry in query字頭("忘") if entry.音韻地位.屬於("去聲"))
    assert departing_tone_entry.來源 is not None
    assert departing_tone_entry.來源.文獻 == "廣韻"
    assert departing_tone_entry.來源.韻目 == "漾"

    level_tone_entry = next(entry for entry in query字頭("忘") if entry.音韻地位.屬於("平聲"))
    assert isinstance(level_tone_entry.來源, 王三來源)
    assert level_tone_entry.來源.韻目 == "陽"


def test_query_head_matches_original_dataset() -> None:
    """Every CSV row should be discoverable via query字頭."""
    lines = DATA_CSV.read_text(encoding="utf-8").strip().splitlines()
    header, *rows = lines
    assert header.startswith("小韻號"), "Unexpected CSV header"

    for line in rows:
        fields = line.split(",")
        (
            _xiao_yun_id,
            _entry_index,
            original_rhyme_name,
            position_description,
            raw_fanqie,
            head_character,
            raw_definition,
            definition_note,
        ) = fields

        if not position_description:
            continue

        fanqie = raw_fanqie or None
        definition_suffix = f"（{definition_note}）" if definition_note else ""
        definition = f"{raw_definition}{definition_suffix}"
        expected_position = 音韻地位.from描述(position_description)

        matches = query字頭(head_character)
        assert any(
            match.字頭 == head_character
            and match.音韻地位.等於(expected_position)
            and match.反切 == fanqie
            and match.釋義 == definition
            and match.來源 is not None
            and match.來源.文獻 == "廣韻"
            and match.來源.韻目 == original_rhyme_name
            for match in matches
        ), line
