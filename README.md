# Color detection using Python

A desktop OpenCV demo that samples an image pixel on a double-click and displays the nearest color name and its RGB values. It uses a palette lookup, not a trained AI model.

## Install

Use Python 3.10 or newer with a graphical desktop. From a terminal:

```bash
git clone https://github.com/Foysal-A-Al/Color_detection-using-python.git
cd Color_detection-using-python
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Or on Linux/macOS:

```bash
source .venv/bin/activate
```

Then install dependencies:

```bash
python -m pip install -r requirements.txt
```

These are dependency ranges, not a tested lockfile.

## Run

Run from the repository directory, because the script reads `colors.csv` from the current working directory:

```bash
python color_detection.py --image "path/to/image.jpg"
```

Double-click a pixel to display its nearest palette color and sampled RGB values. Press **Esc** to exit. Use a readable image file; the current script does not validate failed image loading. A headless server cannot display the OpenCV window without a graphical display.

## Palette and matching

The included palette contains 16 basic colors. `colors.csv` has no header, and each row has six columns:

```text
identifier,display_name,hex,R,G,B
```

For example, an actual data row is:

```text
red,Red,#FF0000,255,0,0
```

RGB values must be integers from 0 to 255. Add your own entries to expand the palette. For a sampled RGB pixel, the script minimizes `abs(R-R_palette) + abs(G-G_palette) + abs(B-B_palette)`; ties choose the last matching row. The result is the closest entry in this palette, not an exact name for every possible color or a perceptually calibrated measurement.

## Current limitations

The display annotation is drawn onto the source image. Sampling the annotation area therefore reads the overlay, not the original pixel. Fixed annotation dimensions may also clip on small images. Image-load validation and rendering overlays on a separate copy are useful future improvements.
