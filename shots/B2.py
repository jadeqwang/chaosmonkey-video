"""B2 22.292-26.125 (92 f). ATTIC v4. 'On 花果山, where the cliffs run steep' (Mama sings, 23.06-26.1).
Part 1 (to 24.6): LAP_front (v4_B2, keyframe media/kf/v4/B2.jpg, crop media/kf/v4/B2_crop.jpg = box 920,200,1600x900): ONE Seedance 2.5 take
(at4ls_B2_4: she sings and acts, the child giggles; no mouth pasted), clip frame 0 at song 21.8933, speed 1.
Part 2 (24.6 on): over the shoulder (v4_B2_ots, media/kf/v4/B2_ots.jpg); a Kling take (at4_B2_ots_k4_t1: breathing, page-edge flutter,
child's hand settling; pages blank) is the plate; the push is a perspective warp whose last third lands on B3's first frame, with
BOOK's flat page art (media/comp/pages/B3_page.png) printed through one fixed quad. Hand-over: first frame of media/comp/B3.mp4
(WORLD's new B3, extracted to work/tmp/B3_f0_v4.png; sync via the same contract as v3: spread u 0.031-0.969, v 0.105-0.895)."""
import cv2
from shots._attic4 import *

T0, TC, T1 = 535 / 24, 24.6, 627 / 24
QUAD = np.float32([[352, 388], [1180, 146], [1328, 638], [500, 880]])      # the painted spread in B2_ots (1920 px), TL TR BR BL
U0, U1, V0, V1 = 0.031, 0.969, 0.105, 0.895
A = AtticShot([Seg4(T0, TC, 'B2_crop', key='B2', tmap=[[21.8933, 0.0], [26.8933, 5.0]], floor=0.8, keep=[(300, 100, 1400, 900)],
                    cam=[(T0, 960, 540, 1.0), (TC, 960, 540, 1.0)])])
CLIP = 'media/gen/at4_B2_ots_k4_t1_9e591cf1d0.mp4'


def setup(ctx):
    global FR, ART, SUB, B3F
    A.setup(ctx)
    W, H = ctx.W, ctx.H
    B3F = load_image('work/tmp/B3_f0_v4.png', size=(W, H))
    cap = cv2.VideoCapture(str(ROOT / CLIP)); FR = []
    while len(FR) < 45:
        ok, f = cap.read()
        if not ok:
            break
        FR.append(cv2.resize(f[:, :, ::-1], (1920, 1080), interpolation=cv2.INTER_CUBIC).astype(F32) / 255.0)
    art = load_image('media/comp/pages/B3_page.png')
    ah, aw = art.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [aw, 0], [aw, ah], [0, ah]]), QUAD)
    ART = cv2.warpPerspective(art, M, (1920, 1080), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)
    Mu = cv2.getPerspectiveTransform(np.float32([[0, 0], [1, 0], [1, 1], [0, 1]]), QUAD)
    SUB = cv2.perspectiveTransform(np.float32([[U0, V0], [U1, V0], [U1, V1], [U0, V1]])[None], Mu)[0]


def render(t, ctx):
    if t < TC - 1e-6:
        return A.render(t)
    W, H = ctx.W, ctx.H
    u = (t - TC) / (T1 - TC)
    uu = min(1.0, u / 0.74)
    e = uu * uu * (3 - 2 * uu)
    e = 0.12 * uu + 0.88 * e ** 1.15
    pl = FR[min(len(FR) - 1, int(round((t - TC) * 24)))]
    full = np.float32([[0, 0], [1920, 0], [1920, 1080], [0, 1080]])
    src = full * (1 - e) + SUB * e
    Hm = cv2.getPerspectiveTransform(src, np.float32([[0, 0], [W, 0], [W, H], [0, H]]))
    f = cv2.warpPerspective(pl, Hm, (W, H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)
    w = min(1.0, max(0.0, (u - 0.42) / 0.32)) ** 1.6
    if w > 0:
        a = cv2.warpPerspective(ART, Hm, (W, H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)
        f = f * (1 - w) + a * w
    w2 = max(0.0, (u - 0.76) / 0.24)
    if w2 > 0:
        w2 = min(1.0, w2 * 1.04) ** 1.2
        f = f * (1 - w2) + B3F * w2
    return np.clip(f, 0, 1).astype(F32)
