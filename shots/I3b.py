"""I3b '...a seat at the table?' (184.625-187.0, 57 frames). BOOK team, v3 (REVISION_V3 §12, §15).

The Peach Banquet before it begins (plate H_v3_pages/I3b_1: the laid table on its terrace, screen, fans, peaches in
stemmed dishes; the immortals ARRIVING in rank on clouds, Jade Emperor and Queen Mother first; the small monkey watching
from his own cloud). A typeset name slip stands at every place (佛老 菩萨 罗汉 . 观音 圣帝 玄灵: ch.5's guest list) except
the fourth, whose stool is bare. From the whole spread (the over-shoulder push's end framing) the camera pushes to the
bare place; the torch narrows onto it. Static inscription 蟠桃会上 / 可请我么 lower left.
BARE SEAT for I4: page px (2536, 1263) of media/comp/pages/I3b_page.png (3072x2048).

v3 alive pass (§13): the page moves: a minimax/h3 clip animated from this very page (locked camera, spec
media/gen/specs/bk3_alive_*.json) replaces the still inside the full-spread framing; camera, torch and all typeset
writing outside that are ours. Remove `clip=` to return to the still page.
"""
from shots._pages3 import *

T0, T1 = 4431 / 24, 4488 / 24


def setup(ctx):
    global PS
    PS = PageShot(ctx, 'I3b', T0, T1, z1=1.5, focus=(2480, 1240), radius=(2600, 900), clip='media/gen/bk3_alive_I3b_h3_t1_ed0d2f87e7.mp4')


def render(t, ctx):
    return PS.render(t, ctx)
