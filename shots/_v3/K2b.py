"""K2b 'He opened the Book of Life and Death' (212.125-213.792, 40 frames). BOOK team, v3 (REVISION_V3 §3.5, §15).

The hall of the Ten Kings (plate H_v3_pages/K2b_1): the kings standing aside in a knot, the judge and his clerk at the
desk, the monkey ON the desk with the brush over the open ledger. From the whole spread (LAP_ots_push_end framing) the
camera pushes to the ledger; K3 is the ledger close. Static inscription 拿过生死簿 beside the curtain.

v3 alive pass (§13): the page moves: a minimax/h3 clip animated from this very page (locked camera, spec
media/gen/specs/bk3_alive_*.json) replaces the still inside the full-spread framing; camera, torch and all typeset
writing outside that are ours. Remove `clip=` to return to the still page.
"""
from shots._pages3 import *

T0, T1 = 5091 / 24, 5131 / 24


def setup(ctx):
    global PS
    PS = PageShot(ctx, 'K2b', T0, T1, z1=1.5, focus=(2400, 1330), radius=(2600, 900), hold=0.1, clip='media/gen/bk3_alive_K2b_h3_t1_1e1eea1fda.mp4')


def render(t, ctx):
    return PS.render(t, ctx)
