"""Sample original image pixels and identify the nearest named palette color."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import json
from pathlib import Path
import sys


@dataclass(frozen=True)
class Color:
    name: str
    rgb: tuple[int, int, int]


def load_palette(path: str | Path) -> list[Color]:
    """Read the existing headerless identifier,name,hex,R,G,B CSV format."""
    palette = []
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        for number, row in enumerate(csv.reader(handle), 1):
            if not row or all(not value.strip() for value in row):
                continue
            try:
                if len(row) != 6 or not row[1].strip():
                    raise ValueError("expected six columns and a nonempty color name")
                rgb = tuple(int(value) for value in row[3:])
                if any(value < 0 or value > 255 for value in rgb):
                    raise ValueError("RGB values must be integers from 0 to 255")
                expected_hex = "#" + "".join(f"{value:02x}" for value in rgb)
                if row[2].strip().lower() != expected_hex:
                    raise ValueError("hex code does not match RGB values")
            except ValueError as exc:
                raise ValueError(f"Invalid palette row {number}: {exc}") from exc
            palette.append(Color(row[1].strip(), rgb))
    if not palette:
        raise ValueError("Palette must contain at least one color")
    return palette


def nearest_color(rgb: tuple[int, int, int], palette: list[Color]) -> Color:
    if not palette:
        raise ValueError("Palette must contain at least one color")
    # Preserve the original detector's rule: the last row wins equal-distance ties.
    return min(
        reversed(palette),
        key=lambda color: sum(abs(a - b) for a, b in zip(rgb, color.rgb)),
    )


def load_image(path: str | Path):
    import cv2

    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(
            f"Cannot read image: {path}. Use an existing supported image file."
        )
    return image


def sample_pixel(image, x: int, y: int, palette: list[Color]) -> dict:
    height, width = image.shape[:2]
    if not 0 <= x < width or not 0 <= y < height:
        raise ValueError(f"Pixel ({x}, {y}) is outside the {width}×{height} image")
    rgb = tuple(int(value) for value in image[y, x][::-1])  # OpenCV stores BGR.
    match = nearest_color(rgb, palette)
    return {
        "x": x,
        "y": y,
        "rgb": list(rgb),
        "hex": "#" + "".join(f"{value:02X}" for value in rgb),
        "color_name": match.name,
        "palette_rgb": list(match.rgb),
    }


def annotate(image, sample: dict):
    import cv2

    display = image.copy()  # Rendering never changes the sampling source.
    height, width = image.shape[:2]
    bar_height = min(42, height)
    r, g, b = sample["rgb"]
    cv2.rectangle(display, (0, 0), (width - 1, bar_height - 1), (b, g, r), -1)
    if width >= 40 and height >= 12:
        text = f"{sample['color_name']} | RGB {r}, {g}, {b}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_width = cv2.getTextSize(text, font, 0.7, 1)[0][0]
        scale = min(0.7, (width - 8) / max(text_width, 1) * 0.7, (bar_height - 4) / 24)
        foreground = (0, 0, 0) if r + g + b >= 600 else (255, 255, 255)
        cv2.putText(
            display,
            text,
            (4, max(8, bar_height - 10)),
            font,
            scale,
            foreground,
            1,
            cv2.LINE_AA,
        )
    return display


def run_gui(image, palette: list[Color]) -> None:
    import cv2

    window = "Color detector — double-click to sample; Esc/Q to exit"
    display = image.copy()

    def on_mouse(event, x, y, flags, param):
        nonlocal display
        if event == cv2.EVENT_LBUTTONDBLCLK:
            sample = sample_pixel(image, x, y, palette)
            display = annotate(image, sample)
            print(json.dumps(sample), flush=True)

    try:
        cv2.namedWindow(window, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(window, on_mouse)
        while True:
            cv2.imshow(window, display)
            key = cv2.waitKey(20) & 0xFF
            if (
                key in (27, ord("q"))
                or cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) < 1
            ):
                break
    finally:
        cv2.destroyAllWindows()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--image", required=True, help="Path to an image")
    parser.add_argument(
        "--palette",
        type=Path,
        default=(
            Path(__file__).resolve().parents[1] / "colors.csv"
            if (Path(__file__).resolve().parents[1] / "colors.csv").is_file()
            else Path(__file__).with_name("colors.csv")
        ),
        help="Headerless palette CSV (defaults to the bundled file)",
    )
    parser.add_argument(
        "--pixel",
        type=int,
        nargs=2,
        metavar=("X", "Y"),
        help="Sample one pixel and print JSON without opening a window",
    )
    args = parser.parse_args(argv)
    try:
        palette = load_palette(args.palette)
        image = load_image(args.image)
        if args.pixel is not None:
            print(json.dumps(sample_pixel(image, *args.pixel, palette)))
        else:
            run_gui(image, palette)
    except (OSError, ValueError, ImportError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        # Surface OpenCV display/backend failures without hiding other programming errors.
        import cv2

        if not isinstance(exc, cv2.error):
            raise
        print(
            f"OpenCV error: {exc}\nA desktop display is required; use --pixel X Y for headless sampling.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
