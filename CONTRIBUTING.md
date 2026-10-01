# Contributing

Run the test suite described in [README.md](README.md) before submitting changes. For headless tests, use `opencv-python-headless`; for interactive testing, use `opencv-python` in a separate environment.

Include the exact command, image dimensions/format, expected behavior, actual behavior, and Python/OpenCV versions in bug reports. Use an image you can share publicly.

Keep fixes focused and add regression tests for changed sampling, matching, or input validation behavior. Palette changes must preserve six-column headerless CSV rows and consistent RGB/hex values. Document changes to the matching algorithm or tie-breaking rule.

Desktop rendering needs manual verification on a graphical system. Do not report it as tested when only headless sampling was exercised.
