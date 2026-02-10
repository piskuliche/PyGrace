from pygrace.data import _parse_xy_lines


def test_parse_xy_lines_basic():
    lines = [
        "# comment",
        "@ command",
        "1 2",
        "3 4 5",
        "bad line",
    ]
    x, y = _parse_xy_lines(lines)
    assert x == [1.0, 3.0]
    assert y == [2.0, 4.0]
