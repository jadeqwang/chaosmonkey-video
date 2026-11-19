"""A3 9.708-12.583 (69 f). ATTIC v4 (A3a re-made from the v4 set: tired Mama wipes her hands in the lit door, hook rail empty, window not in
frame; A3b = the v3 segments kept EXACTLY, apron 11.68-12.04, hook 12.220, towel 12.400). Earlier v3 note: She hears the stairs: from behind little Jade (pushing herself up, head to the
door) across the dark attic, Mama comes up into the warm stair door, tired, wiping her hands on her apron (A3a, to
11.25). Then at the hook rail (A3b): she lifts the apron off over her head (11.68-12.04), hangs it on the first hook
(12.220), drapes the towel on the second (12.400), and turns, softening, as she sees the child awake.
Kling v4: A3a single; A3b first+last (A3b -> A3b_end). 'RARE EARTH' is typeset under the pale-blue circle on the back
of little Jade's jacket in A3a (tracked to the circle; REVISION_V3 §12)."""
from shots._attic4 import *
from shots._attic3 import SANS_NARROW, _glyph_mask

T0, TC, T1 = 233 / 24, 270 / 24, 302 / 24
S = None
_TXT = {}


def rare_earth(f, t, i, sg):
    """Find the pale-blue circle on her back in this frame; set RARE EARTH under it, on the cloth."""
    if sg.kf != 'A3a':
        return f
    H, W = f.shape[:2]
    s = W / 1920.0
    x0, y0, x1, y1 = int(880 * s), int(600 * s), int(1500 * s), int(1080 * s)
    sub = f[y0:y1, x0:x1]
    blue = ((sub[..., 2] > 0.72 * sub[..., 0]) & (sub.mean(axis=2) > 0.25)).astype(np.uint8)
    blue = cv2.morphologyEx(blue, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    n, lb, st, cen = cv2.connectedComponentsWithStats(blue)
    if n < 2:
        return f
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    if st[k, cv2.CC_STAT_AREA] < 300 * s * s:
        return f
    r = 0.5 * (st[k, cv2.CC_STAT_WIDTH] + st[k, cv2.CC_STAT_HEIGHT]) / 2
    cx, cy = cen[k][0] + x0, cen[k][1] + y0
    st_ = getattr(rare_earth, 'state', None)                  # smooth the track
    cur = np.array([cx, cy, r])
    rare_earth.state = cur if st_ is None or abs(st_[0] - cx) > 60 * s else st_ * 0.5 + cur * 0.5
    cx, cy, r = rare_earth.state
    key = int(round(r))
    if key not in _TXT:
        m = _glyph_mask('RARE EARTH', SANS_NARROW, max(8, int(r * 0.52)), pad=2).astype(F32)
        _TXT[key] = cv2.GaussianBlur(m, (0, 0), 0.5)
    m = _TXT[key]
    h, w = m.shape
    px, py = int(cx - w / 2), int(cy + r * 1.22)
    if px < 0 or py < 0 or px + w > W or py + h > H:
        return f
    a = (m * 0.72)[..., None]
    ink = np.array([0.20, 0.22, 0.27], F32)
    f[py:py + h, px:px + w] = f[py:py + h, px:px + w] * (1 - a) + ink * a
    return f


S = AtticShot([Seg4(T0, TC, 'A3a', key='A3a', tmap=[[T0, 0.0], [TC, TC - T0]], floor=0.6,
                    keep=[(780, 150, 190, 380), (800, 430, 450, 650)], cam=[(T0, 960, 540, 1.0), (TC, 940, 520, 1.05)]),
               Seg(TC, T1, 'A3b', key='A3b', window=(1669, 554, 1892, 857), guide='v3_D9_a', floor=0.62,
                   keep=[(760, 360, 360, 420), (1150, 500, 300, 420)], cam=[(TC, 900, 540, 1.06), (T1, 880, 520, 1.12)])],
              pre=rare_earth)


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)
