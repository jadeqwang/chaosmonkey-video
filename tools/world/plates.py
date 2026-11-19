#!/usr/bin/env python3
"""tools/world/plates.py: painted elements for the 3D world (gpt-image-2), one isolated element per sheet on bare paper,
so that tools/world/prep.py can cut it (alpha) and lift it (depth) into a relief card.

    PY=/home/jade/Documents/halys-video/.venv/bin/python
    $PY tools/world/plates.py list
    $PY tools/world/plates.py run NAME [NAME ...] [--n 2] [--dry-run]     # -> design/world/plates/NAME_<k>.png + .txt
    $PY tools/world/plates.py run all

Reference images are the film's own plates (for the hand) and public-domain Huangshan-school paintings (for the rock
language; refs/paintings/v4/huangshan/MANIFEST.md). No Chinese text is ever asked of the model.
"""
import concurrent.futures as cf_
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools/gen'))
OUT = os.path.join(ROOT, 'design/world/plates')

HAND = ("Chinese ink painting with light colour (qianjiang) on unsized cream xuan paper, in the Huangshan school manner of "
        "Mei Qing and Hongren, drawn with the same brush as reference image 1: crisp angular contour lines in dark ink, the "
        "granite built of flat tilted planes and great split vertical blocks, sparse dry axe-cut and hemp-fibre texture strokes, "
        "a few dark moss dots on the edges, pale ochre wash on the lit planes and pale indigo in the shadowed clefts; the wet "
        "brush bleeds slightly into the absorbent paper. ")
ISO = ("The element stands alone in the middle of an otherwise completely bare sheet of paper: nothing else is painted: no "
       "other peaks, no clouds or mist drawn, no ground line, no water, no sky, no sun or moon, no birds, no figures, no "
       "buildings, no text, no calligraphy, no seal, no signature, no border or frame. Flat, even, shadowless scan of the "
       "painting.")
FOOT = "Its foot is not drawn: the lowest fifth of the rock fades out softly into the blank paper, as if into a sea of cloud. "
QL = ("Chinese blue-green landscape painting (qinglu shanshui) on cream paper, the same hand and palette as reference image 1: "
      "fine dark ink contour lines, the rock faces laid in mineral azurite blue and malachite green over the ink, warm "
      "gold-ochre washes at the lower slopes, tiny pines dotted along the ridges. ")
R_HAND = 'design/world/refs/film_hgs_peak.jpg'
R_PINE = 'design/world/refs/hs_dragonpine_crop.jpg'
R_FAN = 'design/world/refs/hs_meiqing_fan_crop.jpg'
R_QL = 'design/world/refs/film_qinglv_crop.jpg'
REFS_HS = [R_HAND, R_PINE, R_FAN]
REFNOTE = (" Reference image 1 shows the film's own brush (follow its line, texture and colour); images 2 and 3 are old "
           "Huangshan paintings: borrow only their rock and pine language, not their composition, text or seals.")

P = 'portrait'
JOBS = {
    # ---- Huangshan granite pillars (D4-D6 flight; the five become the Buddha's palm) ----------------------------------
    'pillar_scripture': (P, REFS_HS, HAND + "One single tall Huangshan granite pillar, seen from the front. Its front is one broad, "
        "almost flat, smooth vertical face of pale granite, left nearly bare in the middle (a scripture cliff waiting to be "
        "carved), framed by deep vertical clefts and a few stacked blocks at its sides; its summit is a rounded, blunt crown of "
        "rock with two small twisted Huangshan pines on its shoulders, their needles in flat dark pads. The pillar fills the "
        "height of the sheet. " + FOOT + ISO + REFNOTE),
    'pillar_slender': (P, REFS_HS, HAND + "One single very tall and slender Huangshan granite pillar, like a finger of stone, its "
        "sides nearly vertical and parallel, built of a few great stacked blocks with horizontal joints, its summit rounded and "
        "blunt; one twisted pine leans out from a ledge just below the top. A narrow smooth pale face runs down its front. "
        "The pillar fills the height of the sheet and about a fifth of its width. " + FOOT + ISO + REFNOTE),
    'pillar_twin': (P, REFS_HS, HAND + "Two tall Huangshan granite pillars standing side by side, fused at their base, the left one "
        "a little taller, separated by a deep narrow vertical cleft; both have broad smooth pale front faces and rounded "
        "summits; three twisted pines grow from their shoulders and from a ledge in the cleft. They fill the height of the sheet. "
        + FOOT + ISO + REFNOTE),
    'pillar_broad': (P, REFS_HS, HAND + "One massive, broad Huangshan granite peak with a flat-topped, slightly rounded summit, its "
        "front split into three huge vertical slabs with smooth pale faces (cliffs fit for carving), dark clefts between them, "
        "pines in a row along the summit edge and one great pine leaning out from the right shoulder. It fills most of the "
        "sheet. " + FOOT + ISO + REFNOTE),
    'pillar_stacked': (P, REFS_HS, HAND + "One tall Huangshan pillar made of great rounded granite blocks stacked one on another, "
        "slightly leaning, with a balanced boulder crowning the top, a few pines in the joints. It fills the height of the sheet. "
        + FOOT + ISO + REFNOTE),
    'pillar_thumb': (P, REFS_HS, HAND + "One short, thick Huangshan granite pillar, leaning a little to the left, about half as tall "
        "as it is in the other pillars of the range, with a rounded blunt summit and a broad smooth pale front face, two pines on "
        "its shoulder. It fills the lower two thirds of the sheet; the upper third is bare paper. " + FOOT + ISO + REFNOTE),
    'pillar_needle': (P, REFS_HS, HAND + "A cluster of three thin needle-like Huangshan granite spires of different heights, close "
        "together, sharp vertical clefts, tiny pines on their tips. It fills the height of the sheet. " + FOOT + ISO + REFNOTE),
    # ---- near elements that pass the lens --------------------------------------------------------------------------------
    'pine_near': (P, [R_HAND, R_PINE], HAND + "One great twisting Huangshan pine seen close, growing from a small knuckle of granite "
        "at the lower left: the trunk climbs and bends like a dragon, scaly bark in dry ink, long horizontal branches ending in "
        "flat dark pads of needles painted with fine radiating strokes. It fills the whole sheet. Only the pine and its small rock: "
        + ISO + " Reference image 1 shows the film's brush; image 2 is an old painting of a Huangshan pine: borrow its pine, not its text."),
    'ledge_near': ('landscape', REFS_HS, HAND + "A near granite outcrop seen from just above, its rounded top edge running across "
        "the lower half of the sheet, dark ink, strong angular planes, cracks and moss dots, two small pines clinging to it. "
        "It is close to the viewer, so its strokes are large. " + FOOT + ISO + REFNOTE),
    # ---- far country -----------------------------------------------------------------------------------------------------
    'range_far': ('wide', REFS_HS, HAND + "A far range of many slender Huangshan granite pillars and spires in a row across the "
        "sheet, painted only in pale grey ink wash with a few darker accents on their tips, very little texture, their bases "
        "dissolving into blank paper, uneven heights, a few gaps. Only the band of distant pillars, centred on the sheet: "
        + ISO + REFNOTE),
    'range_mid': ('wide', REFS_HS, HAND + "A middle-distance range of Huangshan granite pillars and peaks across the sheet, "
        "drawn in light ink with pale ochre and indigo, clear contours, some pines, their bases dissolving into blank paper; "
        "irregular heights with deep gaps between groups. Only the band of pillars, centred on the sheet: " + ISO + REFNOTE),
    # ---- macro stone (D4) ------------------------------------------------------------------------------------------------
    'granite_macro': ('landscape', [R_HAND], "Chinese ink painting on cream xuan paper, the film's brush as in reference image 1, seen "
        "from very close: a granite rock face fills the whole sheet edge to edge, a broad smooth pale flat area in the middle "
        "(left almost blank, faint mottling of pale ochre and grey wash, a few tiny dark specks of mica and quartz), framed by "
        "angular cracks and dry axe-cut texture strokes near the edges, a few moss dots in the lower right. No text, no "
        "characters, no carving, no seal, no border. Flat even scan."),
    # ---- the 花果山 world (B3 B4 B5): the same hand as B_master -----------------------------------------------------
    'hgs_ledge_near': ('landscape', [R_HAND], HAND.replace('in the Huangshan school manner of Mei Qing and Hongren, ', '') +
        "A near rocky ledge of Flower-Fruit Mountain seen close, its broken top edge running across the lower part of the "
        "sheet, dark ink and pale ochre, one small twisted pine and a few tufts of grass on it, strong angular planes. " + FOOT + ISO +
        " Reference image 1 shows the brush and palette to follow."),
    'hgs_shoulder_l': (P, [R_HAND], HAND.replace('in the Huangshan school manner of Mei Qing and Hongren, ', '') +
        "A secondary rocky peak of Flower-Fruit Mountain, steep, with axe-cut cliffs, two pines, a thin thread of waterfall "
        "left as bare paper. It fills the sheet. " + FOOT + ISO + " Reference image 1 shows the brush and palette to follow."),
    'hgs_shoulder_r': (P, [R_HAND], HAND.replace('in the Huangshan school manner of Mei Qing and Hongren, ', '') +
        "A lower, rounded rocky spur of Flower-Fruit Mountain with stepped ledges and three small pines, axe-cut texture, pale "
        "ochre and indigo. It fills the lower three quarters of the sheet. " + FOOT + ISO + " Reference image 1 shows the brush and palette to follow."),
    # ---- blue-green heaven (J2) -------------------------------------------------------------------------------------------
    'ql_peak_a': (P, [R_QL], QL + "One single tall steep peak with layered ridges and a rounded summit. It fills the height of the sheet. " + FOOT + ISO),
    'ql_peak_b': (P, [R_QL], QL + "One single slender pillar-like peak, a little leaning, with stepped ledges and pines. It fills the height of the sheet. " + FOOT + ISO),
    'ql_peak_c': ('landscape', [R_QL], QL + "A group of three low rounded peaks side by side, the middle one highest. It fills the lower two thirds of the sheet. " + FOOT + ISO),
    'ql_peak_d': (P, [R_QL], QL + "One broad massive peak with two summits and deep folds, rich azurite on the upper faces. It fills the sheet. " + FOOT + ISO),
    'ql_range_far': ('wide', [R_QL], QL + "A far range of many small peaks in a row across the sheet, pale azurite and malachite, light "
        "contours, the bases dissolving into blank paper. Only the band of peaks, centred on the sheet: " + ISO),
    # ---- round 2 (R2_3D, tag wld4_r2): painted cloud forms and a near bough ------------------------------------------------
    'cloud_bank': ('wide', [R_HAND, R_FAN], "Chinese ink painting on cream xuan paper, the film's brush as in reference image 1: a "
        "long low bank of painted clouds seen from the side, made of many rounded billowing cloud heads in a row, each head drawn "
        "with a fine, even, curling outline in grey-black ink (the classical outlined cloud, gou yun), the curls rolling inward "
        "like waves; inside each head a soft pale grey-indigo wash shadow pools along the lower side of the curl and in the folds "
        "between heads, the tops of the heads left as bare bright paper; the base of the bank dissolves softly into blank paper. "
        "Only the cloud bank, centred on the sheet: " + ISO + " Image 2 is an old Huangshan painting: borrow only how its clouds "
        "are drawn, not its rocks, text or seals."),
    'cloud_head': ('landscape', [R_HAND, R_FAN], "Chinese ink painting on cream xuan paper, the film's brush as in reference image 1: "
        "one large cluster of three or four billowing cloud heads piled together, each head drawn with a fine curling outline in "
        "grey-black ink (classical outlined cloud, gou yun), the curls rolling inward, a pale grey-indigo wash shadow along the "
        "underside of every curl and in the clefts between them, their tops bare bright paper; the lower edge thins out into "
        "blank paper in soft wisps. Only the cloud, centred on the sheet: " + ISO + " Image 2 is an old Huangshan painting: borrow "
        "only how its clouds are drawn."),
    'pine_bough': ('landscape', [R_HAND, R_PINE], HAND + "Seen very close: one heavy twisting branch of a Huangshan pine entering from "
        "the left edge of the sheet and reaching across it, scaly bark in dry dark ink, ending in three or four large flat pads "
        "of needles painted with fine radiating strokes in dark ink and a little indigo; no trunk base, no rock, no ground. "
        + ISO + " Reference image 1 shows the film's brush; image 2 is an old painting of a Huangshan pine: borrow its pine only."),
}
SIZES = {'portrait': '1600x3840', 'landscape': '3840x2160', 'wide': '3840x1600'}


def run_one(name, k, dry=False):
    import cf
    orient, refs, prompt = JOBS[name]
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, f'{name}_{k}.png')
    if os.path.exists(out):
        return name, k, 'exists'
    params = {'size': SIZES[orient], 'quality': 'high', 'output_format': 'png', 'images': ['file:' + r for r in refs]}
    open(out[:-4] + '.txt', 'w').write('model: openai/gpt-image-2\n' + json.dumps(params) + '\n\n' + prompt + '\n')
    try:
        r = cf.generate('openai/gpt-image-2', dict(params, prompt=prompt), out, tag=os.environ.get('PLATES_TAG', 'wld4_plate'), dry_run=dry)
        return name, k, r
    except Exception as e:
        return name, k, f'ERROR {e}'


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == 'list':
        for k, v in JOBS.items():
            print(k, v[0], len(v[1]), 'refs')
        sys.exit()
    n = 1
    if '--n' in a:
        n = int(a[a.index('--n') + 1]); del a[a.index('--n'):a.index('--n') + 2]
    dry = '--dry-run' in a
    names = [x for x in a[1:] if not x.startswith('--')]
    if names == ['all']:
        names = list(JOBS)
    with cf_.ThreadPoolExecutor(6) as ex:
        for r in ex.map(lambda nk: run_one(*nk, dry), [(nm, k) for nm in names for k in range(1, n + 1)]):
            print(*r, flush=True)
