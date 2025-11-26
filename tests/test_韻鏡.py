"""Regression tests covering 音韻地位 <-> 韻鏡 conversion and operations."""

from tshet_uinh.資料 import iter音韻地位
from tshet_uinh.音韻地位 import 音韻地位
from tshet_uinh.韻鏡 import 音韻地位2韻鏡位置, 韻鏡位置

SKIPPED_DESCRIPTIONS = {
    "日開三祭平",
    "常開三祭平",
    "溪開三B蒸平",
    "曉開三B幽平",
    "生開三鹽平",
    "定開二佳上",
    "云合三C廢上",
    "昌開三廢上",
    "以開三廢上",
    "明三A麻上",
    "並三A陽上",
    "端開二庚上",
    "生合三祭去",
    "初合三祭去",
    "生開三祭去",
    "初合三元去",
    "影開三B蒸入",
    "生開三鹽入",
    "以開三嚴入",
}


def test_diagram_round_trip() -> None:
    """Ensure 音韻地位 <-> 韻鏡位置 conversion remains round-trip safe."""
    for position in iter音韻地位():
        if position.描述 in SKIPPED_DESCRIPTIONS:
            continue

        try:
            diagram = 音韻地位2韻鏡位置(position)
        except Exception as exc:
            raise AssertionError(f"Failed to convert 音韻地位 {position.描述}") from exc

        try:
            recovered = diagram.to音韻地位()
        except Exception as exc:
            raise AssertionError(
                f"Failed to recover 音韻地位 {position.描述} from 韻鏡位置 {diagram.坐標}"
            ) from exc

        expected = position
        if position.屬於("莊組 仙韻"):
            rhyme = "刪" if position.屬於("入聲") else "山"
            expected = position.調整(f"{rhyme}韻 二等")

        assert recovered.等於(expected), (
            f"音韻地位 {recovered.描述} recovered from {diagram.坐標} "
            f"does not equal original {position.描述}"
        )


def test_basic_fanqie_projection() -> None:
    """Verify the horizontal fanqie projection example using diagram composition."""
    upper = 音韻地位.from描述("端開一登入")
    lower = 音韻地位.from描述("匣一東平")
    expected = 音韻地位.from描述("端一東平")

    upper_diagram = 音韻地位2韻鏡位置(upper)
    lower_diagram = 音韻地位2韻鏡位置(lower)

    composed = 韻鏡位置(lower_diagram.轉號, lower_diagram.上位, upper_diagram.右位)
    recovered = composed.to音韻地位()

    assert recovered.等於(expected), (
        f"Expected {expected.描述} but recovered {recovered.描述} from {composed.坐標}"
    )
