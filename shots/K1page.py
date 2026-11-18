"""K1 page comp 'what he did on the other side?' (207.208-210.542, 80 frames) -> media/comp/pages/K1_full.mp4. BOOK team, v3.

Full-frame version of the K1 page for the BED team (they own media/comp/K1.mp4; this covers the second lyric line).
The road to the underworld as tradition draws it: the monkey asleep under the pine in solid ink; his soul led away on a
rope by two fetchers in dotted ghost-line toward the gate 幽冥界 (signboard typeset, right to left). The camera travels
right to left along the rope, from the sleeper to the gate.

v3 alive pass (§13): the page moves: a minimax/h3 clip animated from this very page (locked camera, spec
media/gen/specs/bk3_alive_*.json) replaces the still inside the full-spread framing; camera, torch and all typeset
writing outside that are ours. Remove `clip=` to return to the still page.
"""
from shots._pages3 import *

T0, T1 = 4973 / 24, 5053 / 24


def setup(ctx):
    global PS
    PS = PageShot(ctx, 'K1', T0, T1, z1=0.95, focus=(980, 950), radius=(2400, 1500), start=(2050, 1150, 0.82), clip='media/gen/bk3_alive_K1_h3_t1_6a4bced5de.mp4')


def render(t, ctx):
    return PS.render(t, ctx)
