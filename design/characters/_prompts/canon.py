"""v3 canon sheets (2026-11-17): turnarounds, expressions+mouths, poses, lap pairs, proofs. Built on the accepted v3 heads.
usage: canon.py SUFFIX key:model [key:model ...]     (model = gpt | nbp)   outputs work/sheets_v3/canon/<key>_<model>_<SUFFIX>.jpg (+ .txt)"""
import sys, json, concurrent.futures as cf_
sys.path.insert(0, "tools/gen"); import cf
C = "design/characters/"; RF = C + "refs/"; OUT = "work/sheets_v3/canon/"
HAND = ("Painting hand: Chinese fine-line figure painting on plain cream xuan paper, delicate thin ink outlines, light transparent colour "
        "washes, hair in soft ink wash with a gloss, paper grain showing. Skin warm and rosy, never grey. Not anime, not a photograph, "
        "not a 3D render. Plain bare cream paper, no text, no labels, no numbers, no arrows, no motion lines, no signature, no seal, no border.")
# ---------------------------------------------------------------- person blocks (v3 canon)
LJ = ("Little Jade, 1988, age 5: a small Chinese girl with a big round head and a short round face, very full soft cheeks with a wide warm "
      "pink blush, a tiny button nose, a tiny soft mouth, and LARGE round dark eyes set wide apart, each with thick dark upper lashes and a "
      "bright clear highlight; distinct, fairly strong, straight dark eyebrows. Glossy jet-black hair: a light fringe of a few soft parted "
      "strands with the forehead showing between them, long side locks in front of the ears, a small half-ponytail tied high at the back of "
      "the crown, the rest straight to just past her shoulders. A cropped white zip jacket with a stand collar, one straight horizontal "
      "orange band across the chest and around both upper arms, a small pale-blue dot on her left chest; loose dark navy trousers; bare "
      "feet. No headphones. Small child proportions: a big head, about four and a half heads tall, short limbs, a round tummy.")
LJ_REF = ("Image 1 is her accepted face sheet: reproduce THAT child's face exactly, with eyes as LARGE relative to the face as in image 1, "
          "the same highlights, lashes, blush, strong brows and light parted fringe. Image 2 is the same child in the film's painting hand: "
          "draw with image 2's thin ink line and pale wash, but keep image 1's bigger eyes, rounder shorter face and stronger blush. ")
DA = ("The daughter, 2026, age 4: a small girl of mixed Chinese and European descent with a big round head and a short round face, very "
      "full soft cheeks with a wide warm pink blush, a tiny button nose, a tiny soft mouth, LARGE round dark-brown eyes each with a bright "
      "clear highlight and soft lashes, soft light-brown eyebrows. Warm brown curly hair (brown, never black): centre-parted, a braid "
      "running along each side of her head from the temple to behind the ear, into two low curly pigtails tied with pink bands, loose "
      "curly wisps at the temples and forehead. A pink short-sleeved dress with small puffed sleeves, printed all over with red "
      "strawberries with green tops; white socks, no shoes. Small child proportions: a big head, about four and a half heads tall, short limbs.")
DA_REF = ("Image 1 is her accepted face sheet: reproduce THAT child's face exactly, with eyes as LARGE relative to the face as in image 1, "
          "the same highlights, round cheeks and blush. Image 2 is the same child in the film's painting hand: draw with image 2's thin ink "
          "line and pale wash, but keep image 1's bigger eyes and rounder, shorter face. ")
MA = ("Mama, 1988: a Chinese woman aged 35, young and attractive, smooth unlined warm skin; a soft oval face with a gently pointed chin, "
      "long almond dark eyes, clearly drawn dark straight-ish eyebrows that read behind her glasses, a straight nose, a full smiling mouth; "
      "glossy jet-black hair in a soft late-1980s perm of loose springy curls, side-parted, ending at the jaw (never longer); thin round "
      "wire-rim glasses; a plain cream cotton collarless blouse with a small notched neckline, sleeves pushed up above the elbows; dark "
      "loose trousers; white socks; forearms and hands pink from hot dishwater. NO apron. No wrinkles, no sagging, no grey hair: 35, not 45.")
MA_REF = ("Image 1 is her accepted face sheet: reproduce THAT woman's face, age, perm, glasses, blouse and painting hand exactly. ")
JA = ("Jade, 2026: a Chinese woman who looks about 30; an oval face with a softly pointed chin, almond eyes with deep near-black irises "
      "(almost as dark as her hair), dark, fairly strong, slightly asymmetric eyebrows (the eyebrow on the LEFT of the picture is straight; "
      "the eyebrow on the RIGHT of the picture runs straight and then lifts into a soft arch), a straight nose, full lips; thin dark "
      "rectangular half-rim glasses; long black hair with NO fringe: an open forehead, parted slightly off-centre, swept to both sides in "
      "long soft face-framing layers with a loose wave, past the shoulders. A cropped white racer jacket ending above the navel, stand "
      "collar with two snap tabs, worn open over a black mock-neck top; one orange band across the chest and one around each upper arm at "
      "the same height; a small pale-blue dot on her left chest; wide navy cargo trousers with orange straps; white sneakers, grey socks. "
      "Her jacket is plain white apart from the band and the dot: no logos, no lettering, white cuffs.")
JA_REF = ("Image 1 is her accepted face sheet: reproduce THAT woman's face, dark eyes, eyebrows, glasses, hair and painting hand exactly; "
          "keep her natural, real face, do not idealise her into a generic beauty. ")
# ---------------------------------------------------------------- layouts
TURN = ("A character turnaround sheet of ONE person on bare paper, full figures head to toe, all the same scale, evenly spaced in one row: "
        "standing front view; standing three-quarter view; standing pure side view; standing back view; and at the right the same person "
        "seated on the floor. {extra}The face in the front and three-quarter views is alive: bright eyes, a small warm smile. ")
EXPR = ("An acting sheet of ONE person on bare paper, two rows. TOP ROW: six head-and-shoulders portraits, all the same size, each a "
        "different played moment. BOTTOM ROW: at the far left one more head-and-shoulders portrait the same size; then four close-ups of "
        "the lower face only (nose tip to chin), side by side, the four singing mouth shapes in this order: (a) lips closed, humming, with "
        "a slight smile; (b) 'ah', jaw dropped, mouth open tall; (c) 'oh', lips rounded into a small circle; (d) 'ee', lips stretched "
        "wide, teeth showing. Every face is the same person, on-model, eyes full of life. ")
POSE = ("A pose sheet of ONE person on bare paper: {n} full-figure drawings of the same child, all the same scale, evenly spaced, each one "
        "an acted moment with the whole body and a lively face. ")
PAIR = ("A two-character model sheet on bare paper: the SAME pair drawn three times, the same scale, evenly spaced in one row, full "
        "figures. LEFT: front view. MIDDLE: three-quarter view. RIGHT: over-the-shoulder view from behind and slightly above the mother, "
        "looking past her hair and shoulder and over the child's head down onto the open book, whose two pages are large and facing us. ")
JOBS = {}
def job(key, refs, prompt, ar="16:9", size="3072x1728"): JOBS[key] = dict(refs=refs, prompt=prompt, ar=ar, size=size)
H = lambda k: [RF + k + "_heads_v3.jpg", RF + k + "_heads_v3_hand.jpg"]
# ---------------------------------------------------------------- A turnarounds
job("lj_A", H("lj"), TURN.format(extra="Seated figure: sitting cross-legged on a floor mat, hugging a closed picture book to her chest, looking up, hopeful. ")
    + LJ + " " + LJ_REF + "The big cute head must not shrink on the full figures: the head is nearly a quarter of her height. " + HAND)
job("da_A", H("daughter") + [RF + "daughter_dress_ref.jpg"], TURN.format(extra="Seated figure: sitting on the floor with her legs out in front, hands on her knees, looking up with a bright open smile. ")
    + DA + " " + DA_REF + "Image 3 shows her dress and her hairstyle from every side: use it for the dress, the socks and the braid and "
    "pigtails only (no shoes here: white socks). The big cute head must not shrink on the full figures: the head is nearly a quarter of her height. " + HAND)
job("ma_A", [RF + "mama_heads_v3.jpg", C + "mama/mama_H_heads_v3.jpg"], TURN.format(extra="Seated figure: kneeling-sitting on a floor mat with an open picture book (blank cream pages) on her lap, looking up from it with a storyteller's smile. "
    "In ALL five of these figures she wears NO apron. Then, at the far right and drawn clearly smaller than the others, ONE extra standing figure of her "
    "wearing a damp grey-beige canvas restaurant apron with darker wet patches, tied at the waist over the blouse, her hands behind her untying it. ")
    + MA + " (The apron exists only on the one small extra figure.) " + MA_REF + "Image 2 is the full accepted sheet of the same woman. She is "
    "about seven and a half heads tall, slim, an easy tired grace. From behind and seated her hair still ends at the jaw. " + HAND)
job("ja_A", [RF + "jade_heads_v3.jpg", RF + "jade_clothes_v2.jpg"], TURN.format(extra="Seated figure: sitting cross-legged on the floor with an open picture book (blank cream pages) on her lap and a small black flashlight in one hand, looking down at the book, fond. ")
    + JA + " On the back of the jacket a large pale-blue circle; a small round blank patch with a black ring on her left sleeve. " + JA_REF +
    "Image 2 shows her clothes from every side (bodies only): use image 2 only for the clothes. " + HAND)
# ---------------------------------------------------------------- C expressions + mouths
job("lj_C", H("lj"), EXPR + "TOP ROW, left to right: (1) rapt listening: lips parted, eyes wide and shining, fixed on something just off to "
    "one side, chin lifted, breath held; (2) bargaining for a story: hopeful and a little sly, head tilted, eyebrows raised in the middle, "
    "a coaxing closed smile, looking up from under her lashes; (3) a delighted open grin, eyes crinkled nearly shut, shoulders up; "
    "(4) indignant 'it isn't fair', near tears: brows drawn together, eyes glistening and brimming, lower lip pushed out and trembling; "
    "(5) a sceptical sideways look: head turned a little away, eyes slid to the side, ONE eyebrow raised, a pressed little smile ('is that "
    "true?'); (6) the 'Yes' face, a clever child hiding what she understands: her eyes have flicked up and away to one side, she is "
    "lightly biting one corner of her lower lip, a small secret smile held in, mischief behind an obedient face. BOTTOM ROW far left: (7) "
    "sleepy: eyelids heavy and half closed, a small yawn, head nodding to one side, a soft smile. " + LJ + " " + LJ_REF + HAND)
job("da_C", H("daughter"), EXPR + "TOP ROW, left to right: (1) performing a rap with total self-belief: chin up and forward, eyes bright and "
    "fixed on her audience, mouth open mid-word, one small hand raised chopping the beat; (2) a huge open laugh, eyes squeezed shut, head "
    "thrown back; (3) hesitant and unsure, asking 'would I really?': head tipped back, big eyes looking UP at her mother above her for "
    "reassurance, eyebrows raised in the middle, lips just parted, a small hopeful half-smile; (4) cheeky: ONE eyebrow raised high, a "
    "lopsided closed smile, looking sideways to see if her joke landed; (5) cheeks puffed full like a balloon, lips pursed, blowing across "
    "her own open palm held flat under her chin, eyes following what she blew away, delighted; (6) nodding eagerly: chin tucked down mid-nod, "
    "eyes huge and looking up, a wide closed-mouth smile, pigtails bouncing. BOTTOM ROW far left: (7) fast asleep, head fallen to one side, "
    "eyes closed, mouth softly open, cheeks rosy. " + DA + " " + DA_REF + HAND)
job("ma_C", [RF + "mama_heads_v3.jpg", C + "mama/mama_H_heads_v3.jpg"], EXPR + "TOP ROW, left to right: (1) a storyteller's relish: eyebrows "
    "up, eyes wide and bright, mouth open mid-word, leaning in; (2) laughing with her head tipped back, eyes crinkled shut; (3) blowing "
    "dust across a page: cheeks filled round with air, lips pursed forward into a small 'o', a visible soft puff of breath leaving her "
    "lips, eyes glancing sideways with a twinkle, both hands out of the picture (NO finger anywhere near her mouth; this is blowing, not "
    "hushing); (4) mock-stern 'do what mama says': chin down, one eyebrow raised, lips pressed to hide a smile, one index finger lifted "
    "beside her face, half playing; (5) alarm turning to relief, she has just caught a falling child: eyes still wide, brows up, mouth "
    "open on a gasp that is turning into a shaky laugh, one hand pressed to her chest; (6) tired and glad: shoulders loose, head tilted, "
    "soft eyes, a slow warm closed smile. BOTTOM ROW far left: (7) whispering a secret behind one cupped hand held beside her mouth, "
    "eyes sliding sideways, smiling. " + MA + " " + MA_REF + "Image 2 is the full accepted sheet of the same woman. She stays 35 and pretty in every "
    "expression, including the laughing and the alarmed ones: smooth skin, no lines. " + HAND)
job("ja_C", [RF + "jade_heads_v3.jpg", C + "jade/jade_H_heads_v3.jpg"], EXPR + "TOP ROW, left to right: (1) reading aloud to her child: eyes "
    "lowered to a book below the picture edge, lips parted mid-word, a fond half-smile; (2) reading it like a dare: looking straight at us "
    "over the top of her glasses, both eyebrows up, a daring grin; (3) warm and completely certain, encouraging, 'you're able': a steady "
    "direct gaze, leaning slightly toward us, a small sure smile; (4) laughing, eyes crinkled, head tilted; (5) singing softly: eyes half "
    "closed, mouth gently open on a long note, relaxed; (6) tender, looking down at a sleeping child below the picture edge: head bowed, "
    "eyes lowered and soft, the smallest smile. BOTTOM ROW far left: (7) instead of a head, a narrow car rear-view mirror seen from the "
    "back seat, showing only her eyes, glasses and eyebrows reflected in it, the eyes smiling (crinkled at the corners). " + JA + " " +
    JA_REF + "Image 2 is the full accepted sheet of the same woman. " + HAND)
# ---------------------------------------------------------------- B poses
job("lj_B", H("lj"), POSE.format(n="seven") + "Top row of four, bottom row of three. (1) lying on her back on a floor mat under a thin "
    "blanket, wide awake, hands on her tummy, big eyes open looking up at the ceiling, mid-blink, waiting for someone; (2) sitting on the "
    "mat, leaning sideways and reaching one arm out to touch a grown-up's forearm that enters from the edge of the paper (only the adult's "
    "pink forearm and pushed-up cream sleeve are seen): a bid for attention, looking up, hopeful; (3) standing on ONE leg on top of a "
    "wobbly stack of four big books, the other knee raised, one hand flat above her eyebrows shading her eyes like a monkey look-out, the "
    "other arm out for balance, wobbling, tongue between her teeth, very proud; (4) mid-fall off the books: tipping backwards in the air, "
    "both arms flung out, eyes and mouth round with surprise, hair flying, books sliding; (5) cheeks puffed full, blowing across her own "
    "open palm held flat in front of her mouth, eyes following what she blew; (6) two fingertips resting on the middle of her own forehead, "
    "looking up, brows drawn, a real question worrying her; (7) kneeling over an open picture book (blank cream pages) on the floor, one "
    "hand spread palm-down over the page to protect it, lower lip out, looking up indignantly. " + LJ + " " + LJ_REF +
    "The head stays big and the face as cute as image 1 in every pose. " + HAND)
job("da_B", H("daughter") + [RF + "daughter_dress_ref.jpg"], POSE.format(n="five") + "Top row of three, bottom row of two. (1) strapped into a grey "
    "forward-facing child car seat with a five-point harness, performing a rap: both small hands held up APART at shoulder width, edges "
    "down like little karate chops on the beat (the hands never touch, never palms together), chin leading, mouth open mid-word, feet in "
    "white socks kicking; (2) sitting, pinching ONE single hair between finger and thumb held up close in front of her nose and squinting "
    "at it with one eye nearly shut, utterly serious; (3) cheeks puffed full, blowing the hair off her open flat palm, eyes following "
    "where it goes, delighted; (4) lying on her tummy over a big open picture book (blank cream pages), feet in the air, pressing ONE "
    "index fingertip onto the page the way a child presses a lift button, tongue-tip out; (5) fast asleep on her side on a bed, mouth "
    "softly open, one arm flung out, one foot hanging off the edge. " + DA + " " + DA_REF + "Image 3 shows her dress and hairstyle: use it "
    "for the dress and hair only. The head stays big and the face as cute as image 1 in every pose. " + HAND)
# ---------------------------------------------------------------- pairs
job("lap_attic", [RF + "mama_heads_v3.jpg", RF + "lj_heads_v3.jpg", RF + "lj_heads_v3_hand.jpg"], PAIR +
    "The pair: Mama sits cross-legged on a thin floor mat with her five-year-old daughter, little Jade, sitting in her lap; BOTH face the "
    "same way (the child's back rests against her mother's chest). Mama's two arms come around the child from behind and her hands hold "
    "an open picture book (blank cream pages, nothing printed) upright in front of them both, resting on the child's knees; the child's "
    "small hands rest on the lower edge of the book. The child leans back into her mother, bare feet sticking out; the mother's chin is "
    "just above and beside the child's hair, cheek near her temple. Warm, affectionate, alive: in the front view Mama is mid-word with her "
    "eyebrows up, reading, and the child stares at the page, rapt, lips parted; in the three-quarter view the child twists to look up at "
    "her mother, grinning, and Mama smiles down at her. True relative sizes: Mama is 160 cm tall, little Jade 108 cm: seated in the lap, "
    "the top of the child's head reaches her mother's chin; the child's head is big for her small body. "
    "MAMA: " + MA + " Image 1 is Mama's accepted face sheet: reproduce her face, age and perm exactly. "
    "LITTLE JADE: " + LJ + " Image 2 is little Jade's accepted face sheet (her face: eyes as LARGE as there, highlights, blush, brows, "
    "fringe); image 3 is little Jade in the film's painting hand (draw with its thin line and pale wash, keep image 2's bigger eyes). " + HAND)
job("lap_bed", [RF + "jade_heads_v3.jpg", RF + "daughter_heads_v3.jpg", RF + "daughter_heads_v3_hand.jpg"], PAIR +
    "The pair: Jade sits on the floor with her back against the side of a low bed (only a strip of mattress and quilt edge is drawn behind "
    "her), knees up a little, with her four-year-old daughter sitting in her lap; BOTH face the same way (the child's back rests against "
    "her mother's chest). Jade's arms come around the child from behind: one hand holds an open picture book (blank cream pages, nothing "
    "printed) in front of them both, resting on the child's knees; her other hand holds a small black flashlight pointed at the book, its "
    "white light pooling on the pages and bouncing softly up onto both faces. The child's small hands hold the lower corners of the book. "
    "The child leans back into her mother, legs out in white socks; the mother's chin is just above and beside the child's curls. Warm, "
    "affectionate, alive: in the front view Jade reads aloud with a fond half-smile, eyes on the page, and the child looks at the page "
    "with big eyes, mouth a little open; in the three-quarter view the child tips her head back to look up at her mother, asking "
    "something, and Jade looks down at her, warm and certain. True relative sizes: Jade is 165 cm tall, the daughter 102 cm: seated in "
    "the lap, the top of the child's head reaches just under her mother's chin; the child's head is big for her small body. "
    "JADE: " + JA + " Image 1 is Jade's accepted face sheet: reproduce her face, dark eyes, eyebrows, glasses and hair exactly. "
    "THE DAUGHTER: " + DA + " Image 2 is the daughter's accepted face sheet (her face: eyes as LARGE as there, highlights, blush); "
    "image 3 is the daughter in the film's painting hand (draw with its thin line and pale wash, keep image 2's bigger eyes). " + HAND)

def run(j):
    k, m = j.split(":"); J = JOBS[k]; refs = ["file:" + r for r in J["refs"]]
    if m == "nbp":
        model, params = "google/nano-banana-pro", dict(aspect_ratio=J["ar"], image_size="2K", output_format="jpg", image_input=refs[:3])
    else:
        model, params = "openai/gpt-image-2", dict(size=J["size"], quality="high", output_format="jpeg", images=refs)
    out = f"{OUT}{k}_{m}_{sys.argv[1]}.jpg"
    open(out.replace(".jpg", ".txt"), "w").write(f"model: {model}\n" + json.dumps(params) + "\n\n" + J["prompt"])
    try: return cf.generate(model, dict(params, prompt=J["prompt"]), out, tag="sheets_v3")
    except Exception as e: return f"FAIL {e}"
if __name__ == "__main__":
    import importlib, os
    if os.path.exists("work/sheets_v3/canon_extra.py"):
        sys.path.insert(0, "work/sheets_v3"); importlib.import_module("canon_extra").add(sys.modules[__name__])
    jobs = sys.argv[2:]
    with cf_.ThreadPoolExecutor(10) as ex:
        for k, r in zip(jobs, ex.map(run, jobs)): print(k, str(r)[:200], flush=True)
