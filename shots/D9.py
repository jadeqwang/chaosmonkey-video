"""D9 82.500-85.833 (80 f). ATTIC v3. The fall. One wide, low camera, the window and the blade sign behind the action.
A beat of the look-out pose beside the stack, then she climbs the crooked stack of textbooks to do it higher (on the
stack 83.244), wobbles (83.475), the stack goes (83.798), she comes down (84.127) into Mama's lunging arms (catch
84.351), the last books settle (84.570); Mama: alarm, relief, then a laugh she tries to hide. This fall is what
'do what mama says' answers in G4. Two Kling v4 clips retimed piecewise to those cues: D9a (D9_0 -> D9_a) and
D9b (D9_a -> D9_b -> D9_c)."""
from shots._attic3 import *

T0, TS, T1 = 1980 / 24, 83.4, 2060 / 24
W_ = (1550, 271, 1730, 495)
K = [(1250, 330, 280, 330), (640, 430, 260, 300), (1150, 620, 420, 330)]
S = AtticShot([Seg(T0, TS, 'D9_0', key='D9a', window=(1560, 271, 1750, 495), guide='v3_D9_a', floor=0.6, keep=K,
                   cam=[(T0, 1040, 520, 1.16), (TS, 1040, 520, 1.16)]),
               Seg(TS, T1, 'D9_a', key='D9b', window=W_, guide='v3_D9_a', floor=0.6, keep=K,
                   cam=[(TS, 1040, 520, 1.16), (84.4, 1040, 560, 1.16), (T1, 1080, 600, 1.3)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)
