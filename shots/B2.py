"""B2 22.292-26.125 (92 f). ATTIC v3. 'On 花果山, where the cliffs run steep'.
Part 1 (to 24.5): LAP_front. Mama scoops little Jade into her lap; they open the book in front of them both; Mama starts
in a storyteller's voice (Kling v4 B2a -> LAPF; the scoop plays through 'On 花果山', so this is action, not a singing
close-up: no lip transfer).
Part 2 (24.5 on): LAP_ots, over Mama's shoulder onto the spread, and the camera pushes in. The page art
(media/comp/pages/B3_page.png, BOOK team) is printed on the painted page through ONE fixed quad at the keyframe's full
resolution, so the mountain cannot slide; the push is a 2D warp of that plate whose last third lands exactly on B3's
first frame (LOG_v3_book: the spread rectangle u 0.031-0.969, v 0.105-0.895 fills the frame) while the neon cast and
the heads dissolve into BOOK's flat unlit page, and over the last 8 frames into B3's actual first frame
(media/comp/attic3/B3_frame0.png, extracted from media/comp/B3.mp4: re-extract if BOOK re-renders B3)."""
from shots._attic3 import *
from shots._attic3 import finish, paper_tex, grade_field
from shots._rooms88 import page_mask

T0, TC, T1 = 535 / 24, 24.5, 627 / 24
QUAD = np.float32([[696, 474], [1267, 320], [1364, 781], [888, 909]])       # the painted spread in B2b (1920 px), TL TR BR BL
U0, U1, V0, V1 = 0.031, 0.969, 0.105, 0.895
PW = 2880                                                                   # working width of the hi-res plate
A = AtticShot([Seg(T0, TC, 'LAPF', key='B2a', floor=0.62, keep=[(960, 400, 420, 400)],
                   cam=[(T0, 960, 500, 1.12), (TC, 960, 480, 1.22)])])


def setup(ctx):
    global PL, ART, SUB, G2, B3F
    B3F = load_image('media/comp/attic3/B3_frame0.png', size=(ctx.W, ctx.H))   # BOOK's B3 frame 0 (multiplane: its mountain already stands forward)
    A.setup(ctx)
    ph = PW * 9 // 16
    k = PW / 1920.0
    kf = load_image('media/kf/v3/B2b.jpg', size=(PW, ph))
    art = load_image('media/comp/pages/B3_page.png')
    ah, aw = art.shape[:2]
    ground = np.percentile(art.reshape(-1, 3), 92, axis=0)
    T = np.clip(art / ground, 0, 1).astype(F32)
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [aw, 0], [aw, ah], [0, ah]]), QUAD * k)
    Tw = cv2.warpPerspective(T, M, (PW, ph), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_CONSTANT, borderValue=(1, 1, 1))
    m, _ = page_mask(kf, [660 * k, 270 * k, 1400 * k, 960 * k], None, 11.0)             # bare paper only (not head, not thumbs)
    m = cv2.GaussianBlur(cv2.erode(m, np.ones((5, 5), np.uint8)).astype(F32), (0, 0), 2.0)[..., None]
    lit = kf * ((1 - m) + m * Tw)
    lit = Blade(None, (273, 40, 461, 231), k, PW, ph, kf=kf, wedge=(0.50, 0.78)).apply(lit, 0.0)   # the one sign, in the window upper left
    G = grade_field(kf, keep=[(980 * k / k, 600, 420, 380)], floor=0.62)
    G = {a: cv2.resize(b, (PW, ph)) for a, b in grade_field(cv2.resize(kf, (1920, 1080)), keep=[(1000, 620, 460, 400)], floor=0.62).items()}
    PL = finish(lit, G, paper_tex(PW, ph))
    # BOOK's flat page in the same plate geometry (unlit), for the hand-over
    ART = cv2.warpPerspective(art, M, (PW, ph), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)
    # the sub-rectangle of the spread that B3's first frame shows, in plate px
    Mu = cv2.getPerspectiveTransform(np.float32([[0, 0], [1, 0], [1, 1], [0, 1]]), QUAD * k)
    SUB = cv2.perspectiveTransform(np.float32([[U0, V0], [U1, V0], [U1, V1], [U0, V1]])[None], Mu)[0]


def render(t, ctx):
    if t < TC - 1e-6:
        return A.render(t)
    W, H = ctx.W, ctx.H
    ph = PW * 9 // 16
    u = (t - TC) / (T1 - TC)
    uu = min(1.0, u / 0.74)                                            # the warp has landed before the hand-over starts
    e = uu * uu * (3 - 2 * uu)
    e = 0.12 * uu + 0.88 * e ** 1.15                                    # starts moving at once, lands with the cut
    full = np.float32([[0, 0], [PW, 0], [PW, ph], [0, ph]])
    src = full * (1 - e) + SUB * e
    Hm = cv2.getPerspectiveTransform(src, np.float32([[0, 0], [W, 0], [W, H], [0, H]]))
    f = cv2.warpPerspective(PL, Hm, (W, H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)
    w = min(1.0, max(0.0, (u - 0.42) / 0.32)) ** 1.6
    if w > 0:
        a = cv2.warpPerspective(ART, Hm, (W, H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)
        f = f * (1 - w) + a * w
    w2 = max(0.0, (u - 0.76) / 0.24)                                   # the last 8 frames: the flat page opens into B3's own first frame
    if w2 > 0:
        w2 = min(1.0, w2 * 1.04) ** 1.2
        f = f * (1 - w2) + B3F * w2
    return np.clip(f, 0, 1).astype(F32)
