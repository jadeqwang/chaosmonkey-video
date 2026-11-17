"""L3 235.833-238.333 (60 f). Team ROOMS-88. The film's first frame again (A1): the neon hums red; at 237.840 the
hum cuts and the sign goes off, hard, no fade: the A1_off plate, then black to the end of audio.
"""
from shots._rooms88 import *
import shots.A1 as A1

T0, T1 = 5660 / 24, 5720 / 24
T_OFF = 237.840


def setup(ctx):
    A1.setup(ctx)


def render(t, ctx):
    if t < T_OFF:
        hum = 1.0 - 0.025 * (0.5 + 0.5 * math.sin(t * 2 * math.pi * 6.0))   # a faint mains hum in the tube
        f = A1.plate(t, hum)
        return finish(f, A1.G, A1.TEX)
    f = finish(A1.OFF.copy(), A1.G, A1.TEX)
    return f * 0.30                                          # off: the dark room sinks to black (the ink floor)
