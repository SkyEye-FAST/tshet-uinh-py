"""Regression tests ensuring 反切 predictions meet expected accuracy."""

# ruff: noqa: N801,N802,N803,N806
import csv
from pathlib import Path

from tshet_uinh.StringLogger import default_logger
from tshet_uinh.反切 import 執行反切
from tshet_uinh.音韻地位 import 音韻地位

FANQIE_DATASET = Path(__file__).resolve().parents[1] / "prepare" / "王三反切音韻地位表.csv"
MANDATORY_CHAR_FIELDS = ("首字（校後）", "上字（校後）", "下字（校後）")
LEGITIMACY_FIELD = "音節合法性（強合法則留空）"


def _value_or_none(raw: str | None) -> str | None:
    text = (raw or "").strip()
    return text or None


def _build_position(row: dict[str, str], prefix: str) -> 音韻地位:
    return 音韻地位(
        row[f"{prefix}聲母"].strip(),
        _value_or_none(row.get(f"{prefix}呼")),
        row[f"{prefix}等"].strip(),
        _value_or_none(row.get(f"{prefix}類")),
        row[f"{prefix}韻"].strip(),
        row[f"{prefix}聲調"].strip(),
    )


def _iter_valid_rows() -> list[dict[str, str]]:
    with FANQIE_DATASET.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader is not None
        rows: list[dict[str, str]] = []
        for row in reader:
            if any(not row[field].strip() for field in MANDATORY_CHAR_FIELDS):
                continue
            if (
                not row["被切字聲母"].strip()
                or not row["上字聲母"].strip()
                or not row["下字聲母"].strip()
            ):
                continue
            if row[LEGITIMACY_FIELD].strip() == "強非法":
                continue
            if row["被切字切語相關地位不一致"].strip():
                continue
            rows.append(row)
    return rows


def test_反切_predictions_meet_spec_accuracy() -> None:
    """Ensure the Python 執行反切 matches the dataset accuracy thresholds."""
    total = 0
    has_match = 0
    single_match = 0

    for row in _iter_valid_rows():
        target = _build_position(row, "被切字")
        upper = _build_position(row, "上字")
        lower = _build_position(row, "下字")

        predictions = 執行反切(upper, lower)
        total += 1

        if any(candidate.等於(target) for candidate in predictions):
            has_match += 1
        if len(predictions) == 1 and predictions[0].等於(target):
            single_match += 1

    assert total > 0

    accuracy = has_match / total
    assert accuracy > 0.994, f"At-least-one accuracy must exceed 99.4%, got {accuracy:.2%}"

    exact_accuracy = single_match / total
    assert exact_accuracy > 0.851, (
        f"Single-result accuracy must exceed 85.1%, got {exact_accuracy:.2%}"
    )


def test_反切_provides_logger_explanations() -> None:
    """Exercise default_logger output while記錄反切推導過程."""
    target = 音韻地位.from描述("端一東平")
    upper = 音韻地位.from描述("端開一登入")
    lower = 音韻地位.from描述("匣一東平")

    previous_state = default_logger.enable
    default_logger.pop_all()
    default_logger.enable = True
    try:
        predictions = 執行反切(upper, lower)
        logs = default_logger.pop_all()
    finally:
        default_logger.enable = previous_state
        default_logger.pop_all()

    assert any(candidate.等於(target) for candidate in predictions)
    assert logs[:2] == [
        "反切上字為端母，故被切字為端母",
        "反切下字為東韻平聲，故被切字為東韻平聲",
    ], logs
