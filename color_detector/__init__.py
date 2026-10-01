"""Deterministic pixel sampling and named-color lookup."""

from .detector import (
    Color,
    annotate,
    load_image,
    load_palette,
    main,
    nearest_color,
    run_gui,
    sample_pixel,
)

__all__ = [
    "Color",
    "annotate",
    "load_image",
    "load_palette",
    "main",
    "nearest_color",
    "run_gui",
    "sample_pixel",
]
