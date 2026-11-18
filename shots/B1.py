"""B1 song frames 372-534 (163 f). ATTIC v3. Sings on camera: little Jade.
'妈妈, will you tell me before I sleep / how 孙悟空 came to be?'
Over Mama's shoulder, close on little Jade, her hand on Mama's forearm (a bid for attention): she pats, tugs on 'tell me'
(16.82), pleads with her head tilted, bounces on 孙悟空 (19.66), then holds still and watches Mama's face, hopeful and a
little sly; on the last word Mama turns to her (her profile comes into frame) and her hand closes over the small hand;
the child beams. Acted Kling v4 take on media/kf/v3/B1c.jpg + lip transfer (docs/LIPSYNC_V3.md), clip frame 0 at T0
(pick key B1c). The first version, a side-by-side two-shot (media/kf/v3/B1.jpg, takes ls_B1_act*), could not carry
the singing: her face was tracked on only 80 % of its frames (gate FAIL); it is kept as media/comp/attic3/B1_twoshot.mp4."""
from shots._attic3 import *

T0, T1 = 372 / 24, 535 / 24
S = AtticShot([Seg(T0, T1, 'B1c', key='B1c', tmap=[[T0, 0.0], [T0 + 7, 7.0]], floor=0.66, keep=[(760, 330, 400, 380)],
                   cam=[(T0, 960, 540, 1.0), (T1, 900, 480, 1.12)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)
