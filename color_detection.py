"""Compatibility entry point for the packaged color detector."""

from color_detector import *  # noqa: F403
from color_detector import main

if __name__ == "__main__":
    raise SystemExit(main())
