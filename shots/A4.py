"""A4 song frames 302-371 (70 f). ATTIC v4. Mama kneels at frame right and takes the book little Jade holds up (pink hands, no apron);
she claps and squeezes her eyes shut with joy. Keyframe media/kf/v4/A4.jpg from the v4 set (window upper left, stack behind the book);
Kling take from media/comp/attic4/picks.json key A4."""
from shots._attic4 import *

T0, T1 = 302 / 24, 372 / 24
S = AtticShot([Seg4(T0, T1, 'A4', key='A4', tmap=[[T0, 0.0], [T1, T1 - T0]], window=(332, -30, 936, 452), wedge=(0.15, 0.30), floor=0.6,
                    keep=[(590, 240, 240, 230), (1040, 80, 220, 260), (790, 490, 300, 240)],
                    cam=[(T0, 960, 540, 1.0), (T1, 930, 530, 1.05)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)
