"""Round-b corrections and proof frames, layered on canon.py (kept separate so round-a prompts stay as run)."""
def add(m):
    J = m.JOBS; RF = m.RF; C = m.C
    # --- round b: adults drifted slightly in the lap sheets (thin brows, plainer/older Mama); Mama's forearms were not pink; car-seat hands a shrug
    J["lap_attic"]["refs"] = J["lap_attic"]["refs"] + [RF + "mama_face_v3.jpg"]
    J["lap_attic"]["prompt"] += (" IMPORTANT, Mama's likeness (image 4 is her face, large): she is 35, pretty, with a soft oval face and gently "
        "pointed chin (not a square jaw), smooth unlined skin, and clearly drawn DARK, fairly thick eyebrows that read strongly behind the "
        "glasses, exactly as in images 1 and 4. Her forearms and hands are visibly pink-red from hot dishwater.")
    J["lap_bed"]["refs"] = J["lap_bed"]["refs"] + [RF + "jade_face_v3.jpg"]
    J["lap_bed"]["prompt"] += (" IMPORTANT, Jade's likeness (image 4 is her face, large): eyebrows drawn in dark ink, fairly strong, clearly "
        "visible above the glasses frame (the left-of-picture brow straight, the right-of-picture brow straight then arched); irises deep "
        "black-brown; the same natural face as images 1 and 4. In the front view her eyes are open, looking down at the page through her glasses.")
    J["ma_A"]["prompt"] += (" IMPORTANT: on every figure her bare forearms and hands are washed a clear pink-red (hot dishwater), distinctly "
        "pinker than her face and neck.")
    J["da_B"]["prompt"] += (" IMPORTANT for drawing (1): her two hands are held vertical like blades, thumbs up, fingers pointing forward, palms "
        "facing EACH OTHER a shoulder-width apart, one hand higher than the other, mid-chop downward: little karate chops, not a shrug, "
        "palms never facing up.")
    # --- proof frames (film room look)
    ROOM_A = ("A Chinese painting of night, ink and light colour on cream xuan paper, in one hand: fine-line baimiao outlines for the faces and "
        "hands with light colour washes, dark ink washes for the room, the paper grain showing through everywhere. The attic above a "
        "restaurant, 1988, at night: sloped wooden ceiling, floor mats, bare floorboards with thin bright amber lines of kitchen light "
        "between them; one pool of red neon light from a small dusty window that is OUT of frame (only its red glow, no readable letters). "
        "Faces drawn in delicate fine ink lines with a light flesh wash, as in a Song or Ming figure painting, not anime, not a photograph, "
        "not a digital render. No text, no signature, no seal, no border. ")
    ROOM_B = ("A Chinese painting of dusk, ink and light colour on cream xuan paper, in one hand: fine-line baimiao outlines for the faces and "
        "hands with light colour washes, dark ink and dusk-violet washes for the room, the paper grain showing through everywhere. A child's "
        "bedroom, 2026, at dusk: the side of a low bed with a rumpled quilt, soft violet shadow, the only light a small black flashlight "
        "whose white beam falls on an open book and bounces up. Faces drawn in delicate fine ink lines with a light flesh wash, as in a "
        "Song or Ming figure painting, not anime, not a photograph, not a digital render. No text, no signature, no seal, no border, no logos. ")
    LIGHT = ("LIGHT AND SKIN (most important): the coloured light is a thin transparent glaze laid OVER normally painted faces. Under it both "
        "faces keep their own warm, rosy flesh wash and pink blush on the cheeks; the lit side is tinted, the shadow side is warm umber, "
        "never grey, never blue-grey, never ashen. The eyes stay as large as on the face sheets, with dark irises and a bright clear "
        "highlight in each eye. Hair stays glossy jet-black ink with a coloured sheen only at its edge. ")
    m.job("proof_attic", [RF + "mama_heads_v3.jpg", RF + "lj_heads_v3.jpg", "design/characters/pairs/lap_attic_v3.jpg", RF + "lj_heads_v3_hand.jpg", RF + "mama_face_v3.jpg"],
        ROOM_A + "Close two-shot, eye level, both faces large in the frame (head and shoulders to the waist; the book's top edge at the "
        "bottom of the frame): Mama sits on a floor mat with little Jade in her lap, both facing us, the child's back against her mother's "
        "chest, Mama's arms around her holding an open picture book in front of them both. Mama is mid-word, a storyteller's relish, "
        "eyebrows up, eyes on the page, her chin just beside the child's hair; little Jade leans back into her, rapt, lips parted, her big "
        "eyes fixed on the page, one small hand on the book's edge. Red neon glow falls from the right across both faces and the page; a "
        "little amber light comes up from the floorboards. Only these two people. " + LIGHT +
        "MAMA: " + m.MA + " IMPORTANT: Mama is 35, young and pretty, a soft oval face, smooth skin, dark clearly drawn eyebrows, glossy "
        "jet-black jaw-length perm (curly, not straight, not brown, not grey), thin round wire glasses. "
        "LITTLE JADE: " + m.LJ + " IMPORTANT: her head is big and her face short and round; her hair is glossy jet-black even where the red "
        "light falls on it. "
        "Reference images: image 1 is Mama's accepted face sheet; image 2 is little Jade's accepted face sheet (her face and eye size); "
        "image 3 is their lap pose sheet (the pose and relative sizes); image 4 is little Jade in the painting hand; image 5 is Mama's "
        "face, large. Use them for likeness only; repaint in this painting.")
    m.job("proof_bed", [RF + "jade_heads_v3.jpg", RF + "daughter_heads_v3.jpg", "design/characters/pairs/lap_bed_v3.jpg", RF + "daughter_heads_v3_hand.jpg", RF + "jade_face_v3.jpg"],
        ROOM_B + "Close two-shot, eye level, both faces large in the frame (head and shoulders to the waist; the book's top edge at the "
        "bottom of the frame): Jade sits on the floor against the side of the bed with her daughter in her lap, both facing us, the child's "
        "back against her mother's chest; one of Jade's hands holds the open picture book in front of them, the other holds a small black "
        "flashlight aimed down at the page. The daughter has tipped her head back to look UP at her mother, unsure, asking 'would I "
        "really?', eyebrows raised in the middle, lips parted; Jade looks down into her eyes, warm and completely certain, a small sure "
        "smile, her chin near the child's curls. White light bounces up from the page onto both faces from below; dusk-violet shadow "
        "behind them. Only these two people. " + LIGHT +
        "JADE: " + m.JA + " IMPORTANT: her irises are deep black-brown; her eyebrows are dark, fairly strong and clearly visible above "
        "the glasses (left-of-picture brow straight, right-of-picture brow straight then arched); no fringe. "
        "THE DAUGHTER: " + m.DA + " IMPORTANT: her head is big and her face short and round; her hair is warm brown, never black. "
        "Reference images: image 1 is Jade's accepted face sheet; image 2 is the daughter's accepted face sheet (her face and eye size); "
        "image 3 is their lap pose sheet (the pose and relative sizes); image 4 is the daughter in the painting hand; image 5 is Jade's "
        "face, large. Use them for likeness only; repaint in this painting.")
    # --- proof_attic second pass: Mama read 38-40 (faint lines beside the mouth), perm a little long, red pool weak
    J["proof_attic2"] = dict(J["proof_attic"], prompt=J["proof_attic"]["prompt"] + (" SECOND IMPORTANT: draw Mama's face with as few lines as "
        "on her face sheet: no lines from nose to mouth, no lines under the eyes, no hollow cheeks; a smooth young cheek with a little warm "
        "blush; her curls stop at the jaw line and do not reach the shoulders. The red neon pool is clearly red: it washes the right side of "
        "both figures, the mat and the page in transparent cinnabar red, while their faces stay warm and rosy underneath. Little Jade is "
        "rapt: she is looking down at the page, not at us."))
