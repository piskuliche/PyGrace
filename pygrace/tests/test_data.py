from pathlib import Path

from pygrace.data import _parse_xy_lines
from pygrace.data import load_datasets


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


def test_load_datasets_csv_xy(tmp_path: Path):
    path = tmp_path / "simple.csv"
    path.write_text("x,y\n0,1\n1,2\n2,3\n", encoding="utf-8")

    datasets = load_datasets([path])

    assert len(datasets) == 1
    assert datasets[0].x == [0.0, 1.0, 2.0]
    assert datasets[0].y == [1.0, 2.0, 3.0]


def test_load_datasets_multicolumn_defaults_to_multiple_sets(tmp_path: Path):
    path = tmp_path / "multi.dat"
    path.write_text(
        "0 10 100\n"
        "1 11 101\n"
        "2 12 102\n",
        encoding="utf-8",
    )

    datasets = load_datasets([path])

    assert len(datasets) == 2
    assert datasets[0].x == [0.0, 1.0, 2.0]
    assert datasets[0].y == [10.0, 11.0, 12.0]
    assert datasets[1].x == [0.0, 1.0, 2.0]
    assert datasets[1].y == [100.0, 101.0, 102.0]


def test_load_datasets_bxy_xy(tmp_path: Path):
    path = tmp_path / "cols.dat"
    path.write_text(
        "9 0 10 99\n"
        "9 1 11 99\n"
        "9 2 12 99\n",
        encoding="utf-8",
    )

    datasets = load_datasets([path], bxy_specs=["2:3"])

    assert len(datasets) == 1
    assert datasets[0].x == [0.0, 1.0, 2.0]
    assert datasets[0].y == [10.0, 11.0, 12.0]
    assert datasets[0].dx is None
    assert datasets[0].dy is None


def test_load_datasets_bxy_x_y_dy(tmp_path: Path):
    path = tmp_path / "cols.dat"
    path.write_text(
        "0 10 0.1\n"
        "1 11 0.2\n"
        "2 12 0.3\n",
        encoding="utf-8",
    )

    datasets = load_datasets([path], bxy_specs=["1:2:3"])

    assert len(datasets) == 1
    assert datasets[0].x == [0.0, 1.0, 2.0]
    assert datasets[0].y == [10.0, 11.0, 12.0]
    assert datasets[0].dx is None
    assert datasets[0].dy == [0.1, 0.2, 0.3]


def test_load_datasets_bxy_x_y_dx_dy(tmp_path: Path):
    path = tmp_path / "cols.dat"
    path.write_text(
        "0 10 0.01 0.1\n"
        "1 11 0.02 0.2\n"
        "2 12 0.03 0.3\n",
        encoding="utf-8",
    )

    datasets = load_datasets([path], bxy_specs=["1:2:3:4"])

    assert len(datasets) == 1
    assert datasets[0].x == [0.0, 1.0, 2.0]
    assert datasets[0].y == [10.0, 11.0, 12.0]
    assert datasets[0].dx == [0.01, 0.02, 0.03]
    assert datasets[0].dy == [0.1, 0.2, 0.3]


def test_load_datasets_invalid_bxy_raises(tmp_path: Path):
    path = tmp_path / "cols.dat"
    path.write_text("0 1\n1 2\n", encoding="utf-8")

    try:
        load_datasets([path], bxy_specs=["1:a"])
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "indices" in str(exc)
