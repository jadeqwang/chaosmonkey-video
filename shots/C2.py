"""C2 45.167-46.167 (24 f). ATTIC v4 (hair fixed: keyframes media/kf/v4/C2h.jpg + C2e.jpg, Kling take at4_C2_k4_t2 retimed so the hands are up by 0.55 s). 'Monkey!' (45.275): top-down onto the spread in her lap (LAP_hands); both small
hands shoot up from the bottom edge into the light and hover flat over the left page, fingers waggling like ears.
The shadow on the page is the MONKEY head in profile (layout/assets/monkey_silhouette.json), standing on the wrists of
those very hands in each frame (tracked from the frame's hand mask), thrown away from the window (the painted
window is upper right, so the throw is down-left), 5.7 cm at 4 cm height, soft (sidecar v3_C2: offset 0.057 m,
penumbra 4 cm along the throw). Page art: the split stone on the right page. Kling v4 HANDS -> C2_end."""
from shots._attic4 import *

T0, T1 = 1084 / 24, 1108 / 24
S = AtticShot([Seg4(T0, T1, 'C2h', key='C2', window=[[1630, -25], [1840, 100], [1760, 315], [1550, 190]], wedge=(0.35, 0.65), floor=0.62, keep=[(960, 480, 620, 380)],
                   page=dict(dthr=0.10, kind='right:design/plates/B_huaguoshan/B_stone_crack.png', roi=(440, 150, 1540, 780), quad=[[486, 200], [1498, 205], [1466, 705], [525, 712]], plate=True, clean=False,
                             shadow=dict(sil=True, h=330, up=0.22, ox=-10, d=(-70, 18), soft=5, aniso=0.9, strength=1.0, grow=1.04)),
                   cam=[(T0, 940, 500, 1.18), (T1, 930, 490, 1.26)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)
