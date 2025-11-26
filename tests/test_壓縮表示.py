"""End-to-end tests for the 壓縮表示 encoding helpers."""

import pytest

from tshet_uinh.壓縮表示 import decode音韻編碼, encode音韻編碼
from tshet_uinh.資料 import iter音韻地位
from tshet_uinh.音韻地位 import 音韻地位


def test_encoding_known_examples() -> None:
    """Ensure specific well-known entries match the compressed codes."""
    assert encode音韻編碼(音韻地位.from描述("幫三C凡入")) == "A9P"
    assert encode音韻編碼(音韻地位.from描述("羣開三A支平")) == "fFU"

    assert decode音韻編碼("A9P").描述 == "幫三C凡入"
    assert decode音韻編碼("fFU").描述 == "羣開三A支平"


def test_encoding_round_trip_for_all_data() -> None:
    """Round-trip every 音韻地位 surfaced by the 資料 module."""
    for current_position in iter音韻地位():
        encoded = encode音韻編碼(current_position)
        decoded = decode音韻編碼(encoded)
        assert decoded.等於(current_position), (
            f"{current_position.描述} -> {encoded} -> {decoded.描述}"
        )


def test_decode_invalid_codes() -> None:
    """Invalid three-character codes should raise ValueError with details."""
    with pytest.raises(ValueError, match=r"Invalid 編碼: 'A'"):
        decode音韻編碼("A")

    with pytest.raises(ValueError, match=r"Invalid character in 編碼: '@'"):
        decode音韻編碼("@@@")

    with pytest.raises(ValueError, match=r"Invalid 母序號: 38"):
        decode音韻編碼("mAA")
