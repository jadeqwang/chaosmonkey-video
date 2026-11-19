"""G3 134.375-141.250 (165 f). ATTIC v3. 'It isn't fair, it isn't fair / I don't want it in his hair': she does NOT
sing on camera. Top-down (LAP_hands): her hand goes flat over the banded monkey on the page to protect him, pats,
her head (bottom edge) shaking no. The shadow is cast by that hand and touches it (frame's own hand mask, thrown
2.4 cm down-left of the painted window light, soft 2 cm; sidecar v3_G3). Margins: the shared schedule (28 -> 25 %).
Kling v4 HANDS -> G3_end; page art: the pilgrim with the gold band (left page)."""
from shots._attic3 import *

T0, T1 = 3225 / 24, 3390 / 24
S = AtticShot([Seg(T0, T1, 'HANDS', key='G3', floor=0.62, keep=[(800, 480, 520, 380)],
                   page=dict(kind='shift:0.03,-0.2:pilgrim', roi=(440, 150, 1540, 780), quad=[[486, 200], [1498, 205], [1466, 705], [525, 712]], plate=True, clean=False,
                             shadow=dict(d=(-46, 32), soft=10, aniso=0.7, strength=1.0, grow=1.02)),
                   cam=[(T0, 790, 430, 1.32), (T1, 780, 420, 1.4)])], margins=True, margin_state=soft_margins(0.4))


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)
