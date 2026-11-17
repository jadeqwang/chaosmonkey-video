"""shots/_margins.py: THE margin schedule for verse 3 (the band), shared by every G shot (room and book).

Owner: team MOUNTAIN. Song clock, 121.4-149.3 s. The paper margins close in from left and right (and a little from
top and bottom) while the picture drains to greys except gold:

  < 121.905          open (no margins), full colour
  121.905 - 130.175  closing slowly (continuous, eased) to a window 62 % of the frame wide
  130.175  (听话 1)  steps in one notch (3-frame slide) to 46 %, then creeps to 42 %
  133.690  (听话 2)  steps to 28 %, creeps to 25 %
  141.450  (听话 G4) steps to the narrowest strip, 22 % (lead: widened from 15 so the face in G5 is whole) of the frame width, and holds
  149.285            snaps away: open, full colour (G6 is bare paper, full frame)

    from shots._margins import margin_state, make_margins, apply_margins
    st = margin_state(t, W, H)    # {'rect': (x0, y0, x1, y1) frame px, 'desat': 0..1, 'progress': 0..1, 'open': bool}
    M = make_margins(W, H)        # in setup(): the same torn paper sheets in every shot (fixed seeds)
    frame = apply_margins(frame, t, M)          # desaturate (gold kept) + lay the sheets at margin_state(t)

All sizes scale with W, H (author at 1920x1080 or any size). The strip is centred horizontally (centre x = W/2).
"""
import numpy as np

from tools.ink.core import ease
from tools.ink.margins import Margins, desaturate
from tools.ink.paper import Paper

T_START, T_STEP1, T_STEP2, T_STEP3, T_SNAP = 121.905, 130.175, 133.690, 141.45, 149.285
SLIDE = 3 / 24.0
# (time, window width as a fraction of W) knots; steps are 3-frame slides between consecutive knots
_W_OPEN = 1.04
_KNOTS = [(T_START, _W_OPEN), (T_STEP1, 0.62), (T_STEP1 + SLIDE, 0.46), (T_STEP2, 0.42), (T_STEP2 + SLIDE, 0.28),
          (T_STEP3, 0.25), (T_STEP3 + SLIDE, 0.22)]
_TB_MAX = 0.045                      # top/bottom margins at the narrowest: 4.5 % of H each
MARGIN_PAPER_SEED = 777              # the margin sheets (not the picture's paper)
MARGIN_EDGE_SEED = 5


def _width(t):
    if t < T_START or t >= T_SNAP:
        return _W_OPEN
    if t >= _KNOTS[-1][0]:
        return _KNOTS[-1][1]
    for (ta, wa), (tb, wb) in zip(_KNOTS, _KNOTS[1:]):
        if ta <= t < tb:
            u = (t - ta) / (tb - ta)
            if tb - ta <= SLIDE + 1e-6:          # a step: quick eased slide
                u = ease(u, 'out')
            elif ta == T_START:                  # the first long close: slow start
                u = ease(u, 'inout')
            # the creeps between steps stay linear
            return wa + (wb - wa) * u
    return _W_OPEN


def margin_state(t, W=1920, H=1080):
    """The margins at song time t: rect = picture window (x0, y0, x1, y1) in frame px (may extend past the frame when
    open), desat = grey amount 0..1 (gold protected), progress 0..1 (0 open, 1 narrowest), open = no margins."""
    w = _width(t)
    p = float(np.clip((_W_OPEN - w) / (_W_OPEN - 0.22), 0, 1))
    half = w * W / 2.0
    tb = (-0.03 + (_TB_MAX + 0.03) * p) * H
    rect = (W / 2.0 - half, tb, W / 2.0 + half, H - tb)
    return {'rect': rect, 'desat': float(min(1.0, p ** 0.7 * 1.08)), 'progress': p, 'open': p <= 0.0}


# Paper-ground shots (the book page itself, e.g. G2; polish-1): paper margins on a paper picture do not read. There the
# PICTURE keeps the page's light in the attic (the neon-lit page: a touch darker, warm, a faint cinnabar cast) and the
# advancing margins are brighter bare paper with a stronger soft torn-edge shadow, so the window visibly narrows.
PAGE_LIGHT = (0.905, 0.845, 0.810)   # multiply on the picture (warm, ~13 % darker, faint red)
SHEET_LIFT = 1.045                   # the margin sheets: bare paper, brighter than the lit page (never pure white)


def make_margins(W=1920, H=1080, ground='room'):
    """The margin sheets (torn edges, lip, contact shadow), identical in every shot that calls this.
    ground='paper': the brighter sheets with a deeper contact shadow, for shots whose picture is the bare page."""
    if ground == 'paper':
        M = Margins(Paper(W, H, 'new', seed=MARGIN_PAPER_SEED), seed=MARGIN_EDGE_SEED, rough=5.0 * W / 1920.0,
                    shadow=0.55, shadow_px=16.0 * W / 1920.0)
        M.paper.rgb = np.clip(M.paper.rgb * SHEET_LIFT, 0, 0.975).astype(np.float32)
        M.ground = 'paper'
        return M
    M = Margins(Paper(W, H, 'new', seed=MARGIN_PAPER_SEED), seed=MARGIN_EDGE_SEED, rough=5.0 * W / 1920.0,
                shadow_px=9.0 * W / 1920.0)
    M.ground = 'room'
    return M


def page_light(frame):
    """The neon-lit page tone (paper-ground shots): applied to the picture whether or not margins show."""
    return (frame * np.asarray(PAGE_LIGHT, np.float32)[None, None]).astype(np.float32)


def apply_margins(frame, t, M, desat=True, paper_tint=True):
    """Drain to greys (gold kept) and lay the margin sheets for time t. Returns a new frame.
    With a make_margins(..., ground='paper') M the picture also gets the lit-page tone (page_light)."""
    st = margin_state(t, M.W, M.H)
    paper = getattr(M, 'ground', 'room') == 'paper'
    if desat and st['desat'] > 0 and not st['open']:
        frame = desaturate(frame, st['desat'], paper=M.paper.ground if paper_tint else None)
    if paper:
        frame = page_light(frame)
    if st['open']:
        return frame
    return M.lay(frame, st['rect'])
