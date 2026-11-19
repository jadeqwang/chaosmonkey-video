"""The J1 view v4 (top-down LAP_hands take): the daughter's fingertip presses a carved character on the blank storybook; it
lights (press 189.620 = song cue); the camera pushes in and squares onto the page art until the last frame of J1 (song
frame 4580) is the page art FLAT: BOOK's J1_page_v4 window x 0..2560, y 100..1540 (page px) = the full frame, lit state,
with a soft flashlight falloff on top.  Shared by shots/J1.py (189.7917-190.875) and shots/I4.py (189.375-189.792).
BED+CAR v4.  Numbers and reasons: work/bedcar4/notes/COMP_J1.md

Model (all 1080p px, scaled by ctx.s):
  take plane  = the 1920x1080 take.  PQ = the blank spread on the take (TL TR BR BL).
  art -> take: Ha0 = Hp . A, Hp = homography spread-rect -> PQ, A = scale C about the marked character that puts the
               character at TIPC (just above the fingertip).  C < 1 keeps every line of text on the page (a pure shift
               would push the text over the top of the page): the art is a smaller print on the left/gutter part.
  camera      = Hs(t): take px -> screen px.  Before T_PUSH0..T_PUSH1 a slow similarity push (PUSH_Z); from T_MOVE0 to
               T_MOVE1 the take-plane quad W0 (the art window x 0..2560, y 100..1540 seen on the take) goes to the screen
               corners (corner interpolation like _bedcar3.PagePush.quad, weight chosen so the zoom is exponential in the
               eased time).  At the end the art window IS the frame (exact: 4 point homography).
  A layer     = take with the art printed on its paper (paper_mask keeps it off the hand), lit glow, warped by Hs.
  B layer     = the flat art itself (lit state) warped by Hs.Ha0, crossfaded in over the move, hand gone, flashlight
               falloff FALL multiplied on it.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar4 import *

T_VIEW = 4545 / 24.0            # 189.375: the picture cuts to this view
T_PRESS = 189.620
T_LIT = 4.0 / 24.0              # cross-fade to the lit art over 4 frames from the press
T_PUSH0, T_PUSH1 = T_VIEW, 4555 / 24.0      # slight push in on the take's view
PUSH_Z = 1.04
T_MOVE0, T_MOVE1 = 4555 / 24.0, 4580 / 24.0     # J1 frame 0 .. last frame (190.8333): squares onto the page
PQ = [(481, 241), (1443, 236), (1428, 795), (545, 806)]     # blank spread on the take (1080p px, measured at src 3.0)
TIPC = (796.0, 462.0)           # the carved character sits here: just above the fingertip's end (nail centre is 796,480)
C_ART = 0.5                     # art scale about the character in spread-uv px (see notes)
WIN = [(0, 100), (2560, 100), (2560, 1540), (0, 1540)]      # page-art window of the last frame (page px)
GOLD = np.array([1.0, 0.86, 0.48], F32)
# flashlight falloff on the last frame (multiplied on the flat art): normalised ellipse radius from the pool centre
FALL_C = (0.40, 0.55)           # centre, fraction of frame (x, y)
FALL_FLOOR, FALL_SIG, FALL_POW = 0.50, 1.15, 2.0
PAD = 600                       # art px of replicated border around the art for the B layer


def fall_field(W, H):
    """F = FLOOR + (1-FLOOR) * exp(-(r/SIG)^POW), r = hypot((x-cx)/(W/2), (y-cy)/(H/2)), (cx,cy)=FALL_C*(W,H)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    r = np.hypot((xx + 0.5 - FALL_C[0] * W) / (W / 2.0), (yy + 0.5 - FALL_C[1] * H) / (H / 2.0))
    return (FALL_FLOOR + (1 - FALL_FLOOR) * np.exp(-(r / FALL_SIG) ** FALL_POW)).astype(F32)


def _load(name):
    a = cv2.imread(os.path.join(PAGES, name), cv2.IMREAD_COLOR)[..., ::-1].astype(F32) / 255.0
    return a


def _S(s):
    return np.diag([s, s, 1.0])


def setup_j1(ctx):
    global B, P, ARTP, ART0, ART1, TR0, TR1, HA0, W0, S, GM, RECT, FALL, PQ_REG, CM, HM, FILL
    S = ctx.s
    B = Take('J1', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=41)
    ART0 = _load('J1_page_v4.png')
    ART1 = _load('J1_page_charlit_v4.png')
    h, w = ART0.shape[:2]
    # B layer source: the lit art with a PAD border that is the edge replicated and then smeared (no streaks beyond the art)
    ap = np.pad(ART1, ((PAD, PAD), (PAD, PAD), (0, 0)), mode='edge')
    bl = cv2.GaussianBlur(cv2.resize(ap, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA), (0, 0), 40)
    bl = cv2.resize(bl, (ap.shape[1], ap.shape[0]), interpolation=cv2.INTER_LINEAR)
    wgt = np.ones(ap.shape[:2], F32)
    wgt[PAD:-PAD, PAD:-PAD] = 0
    wgt = cv2.GaussianBlur(wgt, (0, 0), 30)
    wgt[PAD + 40:-PAD - 40, PAD + 40:-PAD - 40] = 0                  # inside the art: untouched
    ARTP = (ap * (1 - wgt[..., None]) + bl * wgt[..., None]).astype(F32)
    ARTP[PAD:-PAD, PAD:-PAD] = ART1
    RECT = np.float64([[0, 0], [w, 0], [w, h], [0, h]])
    mk = cv2.imread(os.path.join(PAGES, 'J1_char_mask.png'), cv2.IMREAD_GRAYSCALE).astype(F32) / 255.0
    ys, xs = np.where(mk > 0.5)
    chp = np.float64([xs.mean(), ys.mean()])                      # the marked character, page px
    # transmittance of each art on the take's paper: divide by the paper ground (blank right page)
    TR0 = key_paper(ART0).astype(F32)
    TR1 = key_paper(ART1).astype(F32)
    Hp = cv2.getPerspectiveTransform(RECT.astype(F32), np.float32(PQ)).astype(np.float64)
    Hpi = np.linalg.inv(Hp)
    q = Hpi @ np.array([TIPC[0], TIPC[1], 1.0])
    ptip = q[:2] / q[2]                                            # where TIPC falls on the spread in page px
    A = np.array([[C_ART, 0, ptip[0] - C_ART * chp[0]], [0, C_ART, ptip[1] - C_ART * chp[1]], [0, 0, 1.0]])
    HA0 = Hp @ A                                                   # art px -> take px (1080p)
    W0 = _tf(HA0, WIN)                                             # art window on the take
    PQ_REG = None
    FALL = fall_field(ctx.W, ctx.H)
    # take-plane region where the print may go (the paper) and the carved character mask / glow
    reg = np.zeros((ctx.H, ctx.W), F32)
    cv2.fillPoly(reg, [np.int32(np.round(np.float32(PQ) * S))], 1.0)
    PQ_REG = soften(reg, ctx, 2)
    Hc = _S(S) @ HA0
    CM = cv2.warpPerspective(mk, Hc, (ctx.W, ctx.H), flags=cv2.INTER_LINEAR)
    CM = cv2.GaussianBlur(CM, (0, 0), max(0.6, 1.0 * S)).astype(F32)
    CM = CM / max(CM.max(), 1e-3)
    # the hand / arm / hair / thumb on the book (components of the not-paper mask that hold a seed), and a hand-free paper
    # fill (inpainted once): the take's hand dissolves into it during the move so no ghost hand shows through the flat art
    f0 = B.at(T_PRESS)
    npap = (paper_mask(f0, PQ_REG, warm=False, lo=0.50, soft=0.10, sat=(0.30, 0.42)) < 0.5).astype(np.uint8)
    npap = cv2.morphologyEx(npap, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    nl, lab = cv2.connectedComponents(npap)
    hm = np.zeros((ctx.H, ctx.W), np.uint8)
    for sx, sy in ((800, 600), (1100, 780), (1390, 740), (830, 520)):
        l = lab[int(sy * S), int(sx * S)]
        if l > 0:
            hm[lab == l] = 1
    hm = cv2.dilate(hm, np.ones((int(15 * S) | 1,) * 2, np.uint8)).astype(F32)
    HM = (cv2.GaussianBlur(hm, (0, 0), 3 * S) * PQ_REG).astype(F32)
    k4 = 0.25
    sm = cv2.resize(np.clip(f0 * 255, 0, 255).astype(np.uint8), None, fx=k4, fy=k4, interpolation=cv2.INTER_AREA)
    mm = cv2.resize((hm > 0.5).astype(np.uint8), (sm.shape[1], sm.shape[0]), interpolation=cv2.INTER_NEAREST)
    # carpet outside the book must not bleed in: paint it with the paper's median first
    inb = cv2.resize((PQ_REG > 0.5).astype(np.uint8), (sm.shape[1], sm.shape[0]), interpolation=cv2.INTER_NEAREST)
    med = np.median(sm[(mm == 0) & (inb == 1)].reshape(-1, 3), axis=0)
    sm[inb == 0] = med
    fl = cv2.inpaint(sm, mm, 12, cv2.INPAINT_TELEA)
    FILL = cv2.GaussianBlur(cv2.resize(fl, (ctx.W, ctx.H), interpolation=cv2.INTER_CUBIC), (0, 0), 4 * S).astype(F32) / 255.0
    yy, xx = np.mgrid[0:ctx.H, 0:ctx.W].astype(F32)
    r = np.hypot(xx - TIPC[0] * S, yy - (TIPC[1] - 4) * S) / (13.0 * S)
    GM = np.exp(-0.5 * r * r).astype(F32)


def _tf(H, pts):
    p = np.hstack([np.float64(pts), np.ones((len(pts), 1))]) @ H.T
    return p[:, :2] / p[:, 2:3]


FULL = np.float64([[0, 0], [1920, 0], [1920, 1080], [0, 1080]])


def cam(t):
    """take px -> screen px (1080p) homography at song time t, and the move progress u."""
    ctr = np.array([960.0, 540.0])
    zp = 1 + (PUSH_Z - 1) * ease(float(np.clip((t - T_PUSH0) / (T_PUSH1 - T_PUSH0), 0, 1)), 'inout')
    Z = np.array([[zp, 0, ctr[0] * (1 - zp)], [0, zp, ctr[1] * (1 - zp)], [0, 0, 1.0]])
    u = ease(float(np.clip((t - T_MOVE0) / (T_MOVE1 - T_MOVE0), 0, 1)), 'inout')
    if u <= 0:
        return Z, 0.0
    D0 = _tf(Z, W0)                                               # W0 on screen at the start of the move
    R = (FULL[1, 0] - FULL[0, 0]) / (D0[1, 0] - D0[0, 0])         # zoom still to come
    w = (math.exp(math.log(R) * u) - 1) / (R - 1)                 # linear corners <-> exponential zoom
    D = D0 * (1 - w) + FULL * w
    Hm = cv2.getPerspectiveTransform(np.float32(W0), np.float32(D)).astype(np.float64)
    if u >= 1.0:
        Hm = cv2.getPerspectiveTransform(np.float32(W0), np.float32(FULL)).astype(np.float64)
    return Hm, u


def j1_frame(t, ctx):
    s = ctx.s
    f = B.at(t)
    wl = float(np.clip((t - T_PRESS) / T_LIT, 0, 1))
    # --- A: the take with the art printed on its paper
    mpap = paper_mask(f, PQ_REG, warm=False, lo=0.50, soft=0.10, sat=(0.30, 0.42))
    uu = ease(float(np.clip((t - T_MOVE0) / (T_MOVE1 - T_MOVE0), 0, 1)), 'inout')
    wh = float(smoothstep(0.08, 0.40, uu)) if uu > 0 else 0.0           # the hand dissolves into bare paper
    if wh > 0:
        hk = (HM * wh)[..., None]
        f = f * (1 - hk) + FILL * hk
        mpap = mpap * (1 - HM * wh) + PQ_REG * HM * wh
    Hc = _S(s) @ HA0
    h, w = TR0.shape[:2]
    wq = np.linalg.norm(_tf(HA0, [(0, 0)])[0] - _tf(HA0, [(w, 0)])[0]) * s
    kk = min(1.0, 2.0 * wq / w)
    if kk < 1.0:
        sh = (int(w * kk), int(h * kk))
        t0 = cv2.resize(TR0, sh, interpolation=cv2.INTER_AREA)
        t1 = cv2.resize(TR1, sh, interpolation=cv2.INTER_AREA) if wl > 0 else None
        Hk = Hc @ np.diag([1 / kk, 1 / kk, 1.0])
    else:
        t0, t1, Hk = TR0, TR1, Hc
    Tw = cv2.warpPerspective(t0, Hk, (ctx.W, ctx.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(1, 1, 1))
    if wl > 0:
        T1w = cv2.warpPerspective(t1, Hk, (ctx.W, ctx.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(1, 1, 1))
        Tw = Tw * (1 - wl) + T1w * wl
    f = lay_page(f, Tw, mpap, 0.95)
    if wl > 0:
        a = (wl * np.clip(0.80 * CM + 0.50 * GM, 0, 1) * mpap)[..., None]
        f = f * (1 - a) + GOLD * a
    Hs, u = cam(t)
    Hs_c = _S(s) @ Hs @ np.linalg.inv(_S(s))
    if u > 0 or abs(Hs[0, 0] - 1) > 1e-6:
        out = cv2.warpPerspective(f, Hs_c, (ctx.W, ctx.H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    else:
        out = f
    # --- B: the flat art, lit, crossfaded in over the move (the hand goes with the take)
    wb = float(smoothstep(0.35, 0.90, u)) if u > 0 else 0.0
    if wb > 0:
        art = ARTP                                                    # wl is 1 whenever B shows (T_LIT ends before T_MOVE0)
        Hf = Hs @ HA0 @ np.array([[1, 0, -PAD], [0, 1, -PAD], [0, 0, 1.0]])    # padded art px -> screen
        wa = np.linalg.norm(_tf(Hf, [(0, 0)])[0] - _tf(Hf, [(art.shape[1], 0)])[0]) * s
        kk = min(1.0, 1.5 * wa / art.shape[1])
        if kk < 1.0:
            art = cv2.resize(art, (int(art.shape[1] * kk), int(art.shape[0] * kk)), interpolation=cv2.INTER_AREA)
            Hf = Hf @ np.diag([1 / kk, 1 / kk, 1.0])
        Hf_c = _S(s) @ Hf
        Bf = cv2.warpPerspective(art, Hf_c, (ctx.W, ctx.H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        rect = np.zeros(art.shape[:2], F32)
        m0 = int(PAD * 0.6 * kk)
        rect[m0:-m0 or None, m0:-m0 or None] = 1
        rm = cv2.warpPerspective(rect, Hf_c, (ctx.W, ctx.H), flags=cv2.INTER_LINEAR)
        rm = cv2.GaussianBlur(rm, (0, 0), 20 * s)
        if u >= 1.0:
            rm = np.ones_like(rm)
        Bf = Bf * (1 - wb * (1 - FALL))[..., None]
        k = (wb * rm)[..., None]
        out = out * (1 - k) + Bf * k
    out = np.clip(out, 0, 1).astype(F32)
    if u >= 1.0:
        return out                                                # the exact art frame: no paper fibre on top
    return fin(out, P)
