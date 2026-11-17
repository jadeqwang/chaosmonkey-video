"""tools.ink: the Chaos Monkey compositing engine. Paper, ink, stone and light, rendered in code. See README.md."""
from .core import *          # noqa
from .paper import Paper, key_paper, key_dark, aged_ink, deckle_mask, ink_to_rgba, estimate_ground   # noqa
from .camera import Camera, Scene, mist_band, sample   # noqa
from .ink import wash, stroke, splash, splat_shape, bloom, dissolve, hairline, InkAnim, Bloom, Splash, spline  # noqa
from .timing import Timing   # noqa
from .ink import compose, brush_monkey   # noqa
