# Color Detection with Python

[![CI](https://github.com/Foysal-A-Al/Color_detection-using-python/actions/workflows/ci.yml/badge.svg)](https://github.com/Foysal-A-Al/Color_detection-using-python/actions/workflows/ci.yml)

Sample any pixel in an image, see its exact RGB/hex value, and find its nearest named palette color. Use the desktop viewer for interactive exploration or the headless CLI for scripts and reproducible checks.

This is a deterministic color lookup demo, not a trained AI classifier. The bundled palette contains 16 basic colors; the reported name is the closest palette entry, not a calibrated perceptual measurement.

## Install

Python 3.10+ is recommended. Clone and create an isolated environment:

```bash
git clone https://github.com/Foysal-A-Al/Color_detection-using-python.git
cd Color_detection-using-python
python -m venv .venv
```

Activate using `.venv\Scripts\Activate.ps1` in Windows PowerShell, or `source .venv/bin/activate` on Linux/macOS:

```bash
python -m pip install -r requirements.txt
```

## Interactive viewer

```bash
python color_detection.py --image "path/to/image.jpg"
```

Double-click a pixel to display the nearest name and original RGB values. Each selection is also printed as JSON in the terminal. Press **Esc**, **Q**, or close the window to exit. A graphical desktop is required.

Annotations are rendered on a copy; repeated sampling of the annotation area still reads the original image. Coordinates are zero-based: X increases to the right, Y downward. Images are read as three-channel BGR and converted to RGB for output; transparency and embedded color profiles are not analyzed.

## Headless sampling

No window is opened when `--pixel X Y` is provided:

```bash
python color_detection.py --image "path/to/image.jpg" --pixel 20 30
```

For a pure red pixel, the JSON contains `"rgb": [255, 0, 0]`, `"hex": "#FF0000"`, and `"color_name": "Red"`. `palette_rgb` gives the RGB of the nearest named entry. Invalid files, palettes, or coordinates return exit code 2 with a readable error.

For a server/CI environment, install `opencv-python-headless` instead of `opencv-python`. Do not install both in the same environment. Headless OpenCV supports `--pixel` but cannot display the interactive viewer.

## Custom palettes

```bash
python color_detection.py --image photo.png --palette custom_colors.csv --pixel 10 10
```

From a checkout, the default `colors.csv` is resolved relative to the project; an installed wheel uses its bundled palette. Invoking by absolute path works from another directory. Custom palettes use six columns with **no header**:

```csv
red,Red,#FF0000,255,0,0
blue,Blue,#0000FF,0,0,255
```

Columns: identifier, display name, hex, R, G, B. Names must be nonempty, RGB components integers in `[0,255]`, and hex values consistent with RGB. Empty palettes and malformed rows are rejected.

Matching minimizes `|R-R_palette| + |G-G_palette| + |B-B_palette|`. Equal-distance ties choose the last row, preserving the original behavior. Expand the palette for finer naming; perceptual color-distance methods would be a separate extension.

## Tests and contributions

The project can also be installed as a package: `python -m pip install -e ".[dev]"`, then use `color-detect --image photo.png --pixel 10 10`. Build a wheel/source distribution with `python -m build`. These commands install desktop OpenCV by default. The release workflow requires a separately configured PyPI trusted publisher; no registry publication is performed by normal commits or pull requests.

```bash
python -m pip install 'pytest>=8,<9'
python -m pytest -q
```

CI uses headless OpenCV on Python 3.10 and 3.12. Tests cover CLI output, RGB channel order, source-pixel preservation, invalid inputs, palette consistency, bounds, and tiny images. See [CONTRIBUTING.md](CONTRIBUTING.md).
