import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from color_detection import (
    Color,
    annotate,
    load_palette,
    main,
    nearest_color,
    sample_pixel,
)


PALETTE = Path(__file__).resolve().parents[1] / "colors.csv"


def test_bundled_palette_has_consistent_values():
    colors = load_palette(PALETTE)
    assert len(colors) == 16
    assert nearest_color((255, 0, 0), colors).name == "Red"


def test_equal_distance_keeps_last_row_tie_break():
    assert (
        nearest_color((1, 0, 0), [Color("A", (0, 0, 0)), Color("B", (2, 0, 0))]).name
        == "B"
    )


@pytest.mark.parametrize(
    "text", ["", "a,Red,#FF0000,999,0,0", "a,Red,#000000,255,0,0", "bad,row"]
)
def test_malformed_palette_is_rejected(tmp_path, text):
    path = tmp_path / "palette.csv"
    path.write_text(text)
    with pytest.raises(ValueError):
        load_palette(path)


def test_annotation_does_not_change_future_pixel_samples():
    image = np.full((50, 100, 3), (30, 20, 10), dtype=np.uint8)
    original = image.copy()
    sample = sample_pixel(image, 10, 10, load_palette(PALETTE))
    display = annotate(image, sample)
    np.testing.assert_array_equal(image, original)
    assert not np.shares_memory(display, image)
    assert sample_pixel(image, 10, 10, load_palette(PALETTE))["rgb"] == [10, 20, 30]


def test_tiny_image_can_be_annotated():
    image = np.zeros((1, 1, 3), dtype=np.uint8)
    assert (
        annotate(image, sample_pixel(image, 0, 0, load_palette(PALETTE))).shape
        == image.shape
    )


@pytest.mark.parametrize("x,y", [(-1, 0), (0, -1), (2, 0), (0, 2)])
def test_out_of_bounds_sample_is_rejected(x, y):
    with pytest.raises(ValueError, match="outside"):
        sample_pixel(np.zeros((2, 2, 3), dtype=np.uint8), x, y, load_palette(PALETTE))


def test_cli_works_from_another_directory(tmp_path, monkeypatch, capsys):
    path = tmp_path / "image.png"
    cv2.imwrite(str(path), np.full((3, 3, 3), (0, 0, 255), dtype=np.uint8))
    monkeypatch.chdir(tmp_path)
    assert main(["--image", str(path), "--pixel", "1", "2"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["color_name"] == "Red"
    assert result["rgb"] == [255, 0, 0]


def test_missing_image_reports_actionable_error(tmp_path, capsys):
    assert main(["--image", str(tmp_path / "missing.png"), "--pixel", "0", "0"]) == 2
    assert "Cannot read image" in capsys.readouterr().err
