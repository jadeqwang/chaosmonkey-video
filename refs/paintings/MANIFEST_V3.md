# V3 reference additions: seven topics from the director's review

## CHECKPOINT 2026-11-17 late evening

- **Done (images saved and viewed, entries below):** all seven topics have a first full pass: 01 yellow opera Wukong (19 files), 02 Buddha's palm (6), 03 havoc in heaven (23), 04 peach banquet / gods (18), 05 underworld (4), 06 monkey troop (13), 07 inscriptions (9). Total 92 files under `refs/paintings/v3/`.
- **In progress:** nothing; final report sent to lead (see `## DONE` at the end).
- **Next (only if time):** more traditional images for topic 05 (underworld), which is the thinnest.
- **Gaps (see "Gaps" at the end):** no public-domain pre-1949 photo of 杨小楼 / 李少春 as Wukong; no 钻天盔-with-pompoms close-up; only one opera still of 《闹地府》; Qing 彩绘全本西游记 leaves are low resolution (456x694); 易元吉 聚猿图 (Osaka) not available as open image; no Chinese painting of the five-finger pillars found, the best pillar image is Japanese (1806).
- **Decisions:** Japanese *Ehon Saiyuki* (1806) used where it is the clearest traditional picture of a beat (flagged as Japanese every time). Opera photographs are filed as reference-only even when the photo is CC-licensed. Working files were kept outside the repo and have been removed.
- **Open questions for the lead:** none blocking.

## How to read this file

Same conventions as `MANIFEST.md`. Each entry: file (relative to `refs/paintings/v3/`), title, artist/date/collection, source, licence/status, pixel size, and one line on what it teaches.

**Use rule (repeat of the lead's rule):**
- `PD-art` = old artwork, public domain by age; may be passed to a generative model as an image input.
- `REFERENCE-ONLY` = photograph of a living stage production or a 20th-century film. Look at it, describe it in words, never pass it to a generative model as an image input. This applies even where the photograph itself is CC BY (the costume and staging are someone's current work). CC BY / BY-SA photos need attribution if ever republished.
- `COMPARE` in a filename = shown only as a point of comparison, not as a model.

**Sources used:** Wikimedia Commons (API; thumbnails at Commons' standard widths 1920/3840, a few originals), The Met Open Access (CC0), Cleveland Museum of Art Open Access (CC0), LACMA collections site, Journey to the West Research blog archive (scans of the 2008 *清彩绘全本西游记* and the 1888 *新說西遊記圖像*), Waseda University Library copy of *絵本西遊記* via Commons, one Taiwanese production's press photos via a review blog.

**Already in the library, do not duplicate, but relevant here** (paths relative to `refs/paintings/`):
- Buddha / Five Elements Mountain: `monkeys/woodcuts_xiyouji/xyj_wanli_vol02_p28.jpg` (五行山定心猿), `monkeys/woodcuts_li_zhuowu/lizhuowu_ed_p052_ch07.png`.
- Havoc in heaven: `monkeys/woodcuts_xiyouji/xyj_wanli_vol01_p73.jpg` (天神捉怪), `xyj_wanli_vol02_p12.jpg` (小聖施威), `monkeys/woodcuts_li_zhuowu/lizhuowu_ed_p048_ch05.png`, `p050_ch06.png`.
- Underworld: `monkeys/woodcuts_xiyouji/xyj_wanli_vol01_p47.jpg` (入地除名), `monkeys/woodcuts_li_zhuowu/lizhuowu_ed_p044_ch03.png`, the Ten Kings scrolls `blocking/10_jin_chushi_ten_kings_met_*.jpg`, `blocking/10b_cleveland_kings_of_hells_leaf*.jpg`, `ledger_and_books/dizang_ten_kings_*.jpg`.
- Banquet table: `blocking/07_huizong_literary_gathering_npm.jpg` (文會圖).
- Monkey face paint: `opera/shengpingshu_opera_faces/` (the Qing court album; the Sun Wukong face is Commons "Office of Great Peace Album of Opera Faces 1-12").
- Inscriptions: `ink_idiom/ni_zan_rongxi_studio.jpg`, `ink_idiom/cma_shitao_reminiscences_qinhuai_album.jpg`.

---

## 01. Sun Wukong in the yellow Peking opera costume - `01_wukong_opera_yellow/`

**What the stills show (costume notes in words, for prompts).** In 《闹天宫》 today the Great Sage wears a close-fitting yellow quilted jacket (猴衣) covered in a black key-fret / whorl pattern, edged with leopard-spot fur at collar, cuffs, hem and the two hanging front flaps; red silk scarf knotted at the throat over a white collar, with a black tie below the chin; red trousers embroidered with gold whorls (some productions: yellow trousers with the same black pattern); thin-soled yellow boots; a soft yellow-and-black knotted cap (猴帽) with a small topknot, or a hard cap with pompoms. The face is a red peach/heart shape over the eyes and nose on a white ground, gold-ringed eyes, fine black lines around the mouth. The staff is a plain silver or red-and-gold pole about body height. As king on his throne he wears a yellow dragon robe (蟒) and a crown with pompoms. The monkey soldiers wear plain yellow satin with a scalloped collar and soft yellow caps. This is the look Jade remembers; it is a stage convention, with details varying by troupe.

#### `opera_hih02_wukong_front_staff_with_little_monkey.jpg` - 《大闹天宫》 Havoc in Heaven, Jilin Peking Opera House, Yang Xuebin (杨雪斌) as Sun Wukong
- Photographer 陈文 (Flickr univers-finder) | 2014-12-19, Tianchan Theatre, Shanghai | 1920x1272 (original 4928x3264)
- Source: https://commons.wikimedia.org/wiki/File:Havoc_in_Heaven_Peking_Opera_2.jpg | Licence: CC BY 2.0 photo; **REFERENCE-ONLY**
- Teaches: full front view of the yellow costume with staff held low across the body; a little monkey and the giant-god in armour beside him give the scale contrast.

#### `opera_hih02_DETAIL_costume_jacket_cap_face.jpg` - detail crop of the above (from the 3840-px rendition)
- 900x1500 | same source and licence; **REFERENCE-ONLY**
- Teaches: THE costume detail sheet: fret pattern, leopard trim, scarf, cap, red trousers with gold whorls, the face paint, hand grip on the staff.

#### `opera_hih11_wukong_staff_flower_solo.jpg` - same production
- Source: https://commons.wikimedia.org/wiki/File:Havoc_in_Heaven_Peking_Opera_11.jpg | CC BY 2.0; **REFERENCE-ONLY** | 1920x1440
- Teaches: staff flower (棍花) alone on an empty stage; the staff blurs into a fan, body stays upright and calm.

#### `opera_hih14_wukong_crouch_among_hammer_generals.jpg` - same production
- Source: https://commons.wikimedia.org/wiki/File:Havoc_in_Heaven_Peking_Opera_14.jpg | CC BY 2.0; **REFERENCE-ONLY** | 1920x1272
- Teaches: alternative all-yellow costume with black whorl pattern (jacket and trousers); low monkey crouch, cheeky, between much bigger armoured generals.

#### `opera_hih18_wukong_enthroned_mang_robe_crown.jpg` - same production
- Source: https://commons.wikimedia.org/wiki/File:Havoc_in_Heaven_Peking_Opera_18.jpg | CC BY 2.0; **REFERENCE-ONLY** | 1920x1272
- Teaches: Wukong as king: squatting on the table-throne in yellow dragon robe and pompom crown beside a red banner. Monkey posture inside royal dress.

#### `opera_hih19_wukong_back_view_vs_soldiers.jpg` - same production
- Source: https://commons.wikimedia.org/wiki/File:Havoc_in_Heaven_Peking_Opera_19.jpg | CC BY 2.0; **REFERENCE-ONLY** | 1920x1272
- Teaches: back/side view of the costume; one monkey facing a row of four blue heavenly soldiers in lunge.

#### `opera_hih22_wukong_vs_green_general_motion.jpg` - same production
- Source: https://commons.wikimedia.org/wiki/File:Havoc_in_Heaven_Peking_Opera_22.jpg | CC BY 2.0; **REFERENCE-ONLY** | 1920x1272
- Teaches: mid-fight motion blur, how the jacket flaps fly.

#### `opera_arhats16_wukong_plain_yellow_with_staff.jpg`, `opera_arhats22_wukong_spin_pose.jpg`, `opera_arhats23_wukong_one_leg_pose.jpg` - 《十八罗汉斗悟空》, Fujian Peking Opera Troupe
- Photographer 陈文 | 2015-03-16, Tianchan Theatre, Shanghai | 1920 px wide
- Sources: https://commons.wikimedia.org/wiki/File:Eighteen_Arhats_Peking_Opera_16.jpg, `..._22.jpg`, `..._23.jpg` | CC BY 2.0; **REFERENCE-ONLY**
- Teaches: the plain yellow 猴衣 with red sash and soft cap (the on-the-road look); 22 and 23 are clean solo action silhouettes: a spin and a one-legged 亮相.

#### `opera_beijing_wukong_hand_shading_eyes.jpg` - Sun Wukong at a Beijing opera theatre
- Photographer "d'n'c" (Flickr) | 2006-02-12 | 600x800 (full original)
- Source: https://commons.wikimedia.org/wiki/File:Sun_Wukong_at_Beijing_opera_-_Journey_to_the_West.jpg | CC BY-SA 2.0; **REFERENCE-ONLY**
- Teaches: the hand-shading-eyes pose (搭凉棚) with the staff planted; yellow costume with armour-style collar and apron.

#### `opera_liyuan_wukong_armoured_collar.jpg` - Peking opera at Liyuan Theatre (梨园剧场)
- Same photographer, 2006-02-12 | 600x800 | Source: https://commons.wikimedia.org/wiki/File:Peking_opera_Liyuan_Theatre_2.jpg | CC BY-SA 2.0; **REFERENCE-ONLY**
- Teaches: three-quarter view; hard cap with front pompom, red-blue collar piece over yellow.

#### `opera_beijing_wukong_yellow_leopard_spot_duel.jpg` - "Monkey King, Journey to the West", Beijing opera
- Photographer Tom Thai | 2008-08-16 | 1920x1280 | Source: https://commons.wikimedia.org/wiki/File:Beijing_Opera_(京剧)_(3590073500).jpg | CC BY 2.0; **REFERENCE-ONLY**
- Teaches: yellow costume with black spot pattern and pink trousers; duel stance, staff crossing a spear at knee height.

#### `opera_monkeyking_taipei_wukong_yellow_front_dragon_palace.jpg` - 《美猴王》 (The Monkey King), Taipei production led by 朱陸豪
- Press photo, "Courtesy of Trend Education Foundation" | 1536x864
- Source: https://shaopeng.blog/wanders/the-monkey-king-new-peking-opera-production-for-a-classic-tale | Copyright of the production; **REFERENCE-ONLY**
- Teaches: clean, well-lit front view of the all-yellow costume with black pattern and cap, staff held level; other characters dwarfed behind water-cloth flags.

#### `shaoju_1962_liu_lingtong_wukong.jpg` - Zhejiang Shaoju (绍剧) Sun Wukong, 1962
- From 《人民画报》 1962 no. 1 (probably 六龄童 in 《孙悟空三打白骨精》) | 882x1315
- Source: https://commons.wikimedia.org/wiki/File:1962-01_1962年_浙江绍剧_孙悟空.jpg | Commons: public domain (PRC photograph over 50 years old); treat as **REFERENCE-ONLY** (stage production; US status not certain)
- Teaches: the southern (Shao opera) Wukong: gold satin, green scarf, staff upright, one hand shading the eyes, one knee raised. The classic pose in one frame.

#### `shadow_puppet_haining_wukong.jpg` - Haining shadow-play figure of Sun Wukong
- Photographer 猫猫的日记本 | 2014 | 1920x2889 | Source: https://commons.wikimedia.org/wiki/File:Characters_of_Haining_Shadow_play_01_2014-08.JPG | CC BY-SA 4.0 photo of a folk-craft figure; study reference
- Teaches: the same character flattened to a silhouette: pheasant feathers, staff, jointed limbs. Useful for the paper/ink cut-out idiom.

#### `COMPARE_xiyou_yuanzhi_portrait_sun_xingzhe.jpg` - 孫行者 portrait from 《西遊原旨圖像》
- Anonymous, 19th century woodcut | 1280x1822 | Source: https://commons.wikimedia.org/wiki/File:Xiyou.PNG | PD-art
- Teaches: comparison: the book-illustration Wukong before opera fixed the yellow look: monk's clothes, tiger-skin kilt, staff over the shoulder, standing on a cloud.

#### `COMPARE_havoc_in_heaven_1961_cel_wukong.jpg`, `COMPARE_havoc_in_heaven_1961_cel_wukong_vs_nezha.jpg` - 《大鬧天宮》 (Shanghai Animation Film Studio, 1961/64), cel art
- 960x741 and 500x409 | Sources: https://commons.wikimedia.org/wiki/File:The_Monkey_King_in_Havoc_in_Heaven_(1961-1964_film)_-_Cel_Animation_Art.jpg and `File:The_Monkey_King_fights_the_god_Nezha_in_Havoc_in_Heaven_(1961-1964_film)_-_Cel_Animation_Art.jpg`
- Status: Commons tags these public domain (PRC film over 50 years old); US status uncertain. **COMPARISON ONLY, NON-TRADITIONAL, do not copy and do not use as image input.**
- Teaches: how Zhang Guangyu's 1961 design simplified the opera look (yellow top, red trousers, leopard kilt, green scarf, heart-shaped face). Shows why Jade's memory and this film overlap, and what we must not reproduce.

---

## 02. The somersault in the Buddha's hand and Five Elements Mountain - `02_buddha_palm_wuxingshan/`

**Iconography.** Chapter 7. After the furnace escape Wukong fights to the doors of the Hall of Miraculous Mists; the Jade Emperor sends for the Buddha. Traditional pictures split the episode into three moments. (1) The wager: Wukong, small and usually in plain white with a red sash, stands alone in the middle of a ring of thunder generals, facing the Buddha who has arrived on a cloud with Ananda and Kashyapa. (2) The pillars: he somersaults to the edge of the sky and finds five flesh-pink pillars rising from cloud; he writes "齊天大聖到此一遊" on the middle one. The viewer is shown they are fingers (nails, knuckle creases) while the monkey has not understood yet; light radiates from behind them. (3) The mountain: the hand turns over and becomes 五行山; Chinese editions usually show only the result: a mountain with the Buddha's seal-slip on top and the monkey's head and one arm sticking out at the foot. I found no pre-modern Chinese picture that shows the monkey actually tumbling inside the open palm; the Ming and Qing editions show the Buddha above the mountain or the wager. The clearest pre-modern pictures of the pillars and the hand are Japanese (1806 and mid-19th century), drawn from the same text.

**Best direct references:** (1) `ehon_saiyuki_1806_wukong_in_buddhas_palm_five_finger_pillars.jpg` for the pillar reveal; (2) `qing_album_leaf28_wager_before_buddha_thunder_generals.jpg` for the wager (and for topic 03: one small figure ringed by a host); (3) `qing_album_leaf29_under_five_elements_mountain_guanyin.jpg` plus the existing `monkeys/woodcuts_xiyouji/xyj_wanli_vol02_p28.jpg` for the mountain.

#### `ehon_saiyuki_1806_wukong_in_buddhas_palm_five_finger_pillars.jpg` - "悟空自驚在佛掌中" (Wukong is startled to find himself in the Buddha's palm), 《絵本西遊記》 first series
- Illustrated by Ōhara Tōya (大原東野), Japan, first published 1806; Waseda University Library copy he21_02500, vol. 3 | 2883x2343
- Source: https://commons.wikimedia.org/wiki/File:WUL-he21_02500_絵本西遊記_03.pdf (page 9) | PD-art (Japanese, not Chinese)
- Teaches: THE composition: five finger-pillars with nails and whorls standing in cloud at left, "齊天大聖" written on the middle finger, rays fanning out behind; at right the monkey lands on a cloud bank with his staff, tiny against them. Cloud drawn as dotted scallops.

#### `ehon_saiyuki_1806_wukong_before_the_buddha.jpg` - Wukong before the Buddha, same book (vol. 3, page 10)
- 2892x2362 | same source | PD-art (Japanese)
- Teaches: the beat before or after: the Buddha seated with halo and a ray rising from his head, the monkey kneeling on a tiled terrace, gods peering from the gate.

#### `qing_album_leaf28_wager_before_buddha_thunder_generals.jpg` - the wager, 《清彩绘全本西游记》
- Anonymous, Qing dynasty, colour on silk album; reproduced in the 2008 Zhongguo Shudian abridged edition, vol. 1 p. 28 | 456x694 (low resolution, only scan found)
- Source: https://journeytothewestresearch.com/2021/02/07/archive-20-qing-period-color-illustrated-complete-edition-of-journey-to-the-west/ (vol. 1 PDF) | PD-art (the painting; the modern caption text is cropped off)
- Teaches: Wukong in white stands alone at the centre, hands on hips, chin up; a full ring of thunder gods (winged, beaked, hammer and chisel) and generals around him; the Buddha with two monks on a gold cloud at right. The defiance picture.

#### `qing_album_leaf29_under_five_elements_mountain_guanyin.jpg` - under the mountain, same album, vol. 1 p. 29
- 456x694 | same source | PD-art
- Teaches: only the monkey's head shows in a cleft of a tall green-blue rock; Guanyin and Moksha stand before it. The quiet aftermath.

#### `japanese_saiyuki_book_buddha_hand_spread.jpg`, `japanese_saiyuki_book_buddha_hand_page.jpg` - Sun Wukong and the palm of Shakyamuni
- Illustrated by Matsukawa Hanzan (松川半山, 1818-1882), from 《浄土宗回向文和訓図会》, Edo period | 1920x1194 and 1920x2891
- Sources: https://commons.wikimedia.org/wiki/File:孫悟空と釈迦の手のひら_Sun_Wukong_and_the_palm_of_Shakyamuni_Buddha.jpg and `File:孫悟空_Sun_Wukong_or_Monkey_King_and_Shakyamuni_Buddha_02.jpg` | PD-art (uploader's scan, tagged public domain; Japanese)
- Teaches: a second, simpler version: a whole upright hand rising out of cloud with rays, the monkey flying toward it on a cloud. Proof that "giant hand in cloud + small flying monkey" is the standard shorthand.

---

## 03. The monkey defiant against the gods and winning (大闹天宫) - `03_havoc_in_heaven/`

**Iconography.** Chapters 4 to 7. The pictures are almost always set in cloud with no ground line. Wukong is the smallest figure and the only one moving diagonally; the gods come in groups with banners, each identified by an attribute: Li Jing with the pagoda, Nezha as a child on fire-wheels with ring and spear, the Four Heavenly Kings (sword, pipa, umbrella, snake), Juling Shen with an axe, Erlang with the three-pointed two-edged blade, a hawk and the hound. Standard beats: the 齊天大聖 banner raised on Flower-Fruit Mountain; single duels (Juling Shen, Nezha); Wukong's plucked hairs turned into a swarm of small monkeys against the Four Kings; Erlang and his six brothers arriving under a yellow banner; the duel of transformations; capture when Laozi drops the diamond snare and the hound bites his leg. In the novel he loses to Erlang plus Laozi; the "wins" picture comes from the 1950s opera rewrite, where the last tableau is Wukong aloft with the troop under the banner. The older Erlang imagery (搜山圖, 13th to 16th century) shows the god seated calmly while his demon soldiers hunt animal spirits, monkeys included: it is the visual source for "a host hunting one creature".

**Best direct references:** (1) `qing_album_leaf22_erlang_duel_in_clouds.jpg` and `qing_album_leaf14_wukong_vs_nezha.jpg` for colour and cloud staging; (2) `ehon_saiyuki_1806_four_heavenly_gods_vs_wukong_hair_monkeys.jpg` for one against a host with the swarm; (3) `02_buddha_palm_wuxingshan/qing_album_leaf28_wager_before_buddha_thunder_generals.jpg` for the still, defiant stand. For the host itself: `cma_daoist_album_leaf14_heavenly_marshals_on_clouds.jpg`.

#### `qing_album_leaf14_wukong_vs_nezha.jpg` - Wukong against Nezha, 《清彩绘全本西游记》 vol. 1 p. 14
- Anonymous, Qing | 456x694 | Source: JTTW Research Archive #21 (URL under topic 02) | PD-art
- Teaches: two figures only, on two cloud tiers: Nezha above on fire-wheels with spear, the monkey below swinging the staff upward; a fallen yellow banner at the bottom edge tells who is winning.

#### `qing_album_leaf21_erlang_host_banner_hound.jpg` - Erlang arrives, same album p. 21
- 456x694 | PD-art
- Teaches: Erlang as a young man in white with hawk on wrist, the hound on a leash, a big yellow banner, his sworn brothers packed in the top-left corner; three quarters of the leaf is empty cloud.

#### `qing_album_leaf22_erlang_duel_in_clouds.jpg` - the duel, same album p. 22
- 456x694 | PD-art
- Teaches: the monkey low-left with twin pheasant feathers and staff, Erlang and two boys diving at him from upper right, the black hound running between; a strong diagonal.

#### `qing_album_leaf26_capture_diamond_snare.jpg` - capture, same album p. 26
- 456x694 | PD-art
- Teaches: Laozi in a halo top-right letting the ring fall, the hound at the monkey's leg, soldiers closing from all sides: the moment the host wins. Useful as the "almost lost" beat.

#### `ehon_saiyuki_1806_qitian_dasheng_banner.jpg` - "悟空歸簾洞為軍防", 《絵本西遊記》 vol. 2
- Ōhara Tōya, 1806 (Waseda copy; red owner's scribbles on this spread) | 2966x2378 | Source: https://commons.wikimedia.org/wiki/File:WUL-he21_02500_絵本西遊記_02.pdf (page 11) | PD-art (Japanese)
- Teaches: monkeys hauling the "齊天大聖" banner up a pole while Wukong in armour reviews them. The banner-raising beat.

#### `ehon_saiyuki_1806_juling_shen_vs_wukong.jpg` - "玉帝封元帥降簾洞", vol. 2 page 13
- 2972x2371 | same source | PD-art (Japanese)
- Teaches: single duel, giant armoured god with axe against a small armoured monkey with the red staff.

#### `ehon_saiyuki_1806_four_heavenly_gods_vs_wukong_hair_monkeys.jpg` - "四大天神與悟空戰", vol. 2 page 19
- 2989x2353 | same source | PD-art (Japanese)
- Teaches: Wukong at right on a tree-line, a stream of dozens of tiny stick-monkeys pouring from him across the page into a knot of four armoured gods who reel back. The swarm drawn as calligraphic squiggles: very animatable.

#### `ehon_saiyuki_1806_erlang_and_wukong_giant_forms_battle.jpg` - "兩將現神變大合戰", vol. 2 page 21
- 3005x2368 | same source | PD-art (Japanese)
- Teaches: the two fighters fill the spread at giant size against a tiny mountain horizon; scale inversion.

#### `ehon_saiyuki_1806_erlang_hound_laozi_snare.jpg` - "金琢擊悟空", vol. 3 page 3
- 2883x2332 | Source: https://commons.wikimedia.org/wiki/File:WUL-he21_02500_絵本西遊記_03.pdf | PD-art (Japanese)
- Teaches: gods watching from a palace balcony upper-left, Erlang and hound mid-left, the monkey struck at right.

#### `ehon_saiyuki_1806_wukong_vs_wang_lingguan_at_lingxiao.jpg` - "祐聖(真君)戰悟空", vol. 3 page 7
- 2889x2343 | same source | PD-art (Japanese)
- Teaches: the fight at the palace doors after the furnace: whirlwind lines, tilted architecture, three bodies tangled.

#### `xinshuo_xiyouji_1888_ch06_guanyin_watches_erlang_host.jpg` - chapter 6 illustration, 《新說西遊記圖像》
- Lithograph edition, 味潛齋, Shanghai, 1888 | 545x867 (low resolution) | Source: https://journeytothewestresearch.com/2025/02/16/ (Archive #47 PDF) | PD-art
- Teaches: Guanyin small at the top watching; below, a tumbling cloud of gods and the monkey; fine-line late-Qing figure style.

#### `long_corridor_havoc_in_heaven_beam_painting.jpg` - 大闹天宫, beam painting in the Long Corridor, Summer Palace
- Painter unknown, late 19th century (repainted since) | photo by Shizhao, 2008 | 1920x844 | Source: https://commons.wikimedia.org/wiki/File:Havoc_in_Heaven_at_Long_Corridor.JPG | Commons: public domain
- Teaches: the folk/architectural version: monkey on an orange cloud at centre-right, Nezha and soldiers at left; dark, but shows the long horizontal format.

#### `cma_search_the_mountain_leaf41_erlang_commands_hunt.jpg`, `cma_search_the_mountain_leaf42_demon_soldiers_spear_spirits.jpg` - Album of Daoist and Buddhist Themes: Search the Mountain (搜山圖), leaves 41 and 42
- Anonymous, Southern Song, 1200s, ink on paper | Cleveland Museum of Art 2004.1.41, 2004.1.42 | 3400x3041 each
- Sources: https://clevelandart.org/art/2004.1.41 , https://clevelandart.org/art/2004.1.42 | CC0, PD-art
- Teaches: 41: Erlang seated in armour, relaxed, with hound and attendants while soldiers drag in captives; 42: demon soldiers lunging with a long spear at animal spirits wrapped in flame. Pure ink line (baimiao): closest in idiom to our ink look. Faint; raise contrast to read.

#### `cma_daoist_album_leaf14_heavenly_marshals_on_clouds.jpg`, `cma_daoist_album_leaf16_heavenly_marshals_on_clouds.jpg` - same album: Procession of Daoist Deities, leaves 14 and 16
- Cleveland 2004.1.14, 2004.1.16 | 3400x3041 | https://clevelandart.org/art/2004.1.14 , https://clevelandart.org/art/2004.1.16 | CC0, PD-art
- Teaches: six or seven named heavenly marshals per leaf, each on his own cloud, each with a different weapon and stance, name written beside him. A model sheet for the heavenly host.

#### `ming_erlang_search_the_mountain_section_erlang_enthroned_with_host.jpg`, `..._section_spear_hunt.jpg`, `..._section_demon_soldiers_seize_spirits.jpg` - 二郎搜山圖 (Erlang searches the mountain), three sections
- Anonymous, Ming dynasty, handscroll, colour on silk | Museum of Fine Arts, Boston (per Commons) | 4727x2989 each (1/8 tiles of the 37822x2989 original)
- Source: https://commons.wikimedia.org/wiki/File:明佚名设色绢本二郎搜山图.jpg | PD-art
- Teaches: the host in colour: Erlang seated under banners among dozens of soldiers; soldiers spearing a deer spirit; soldiers seizing spirits in human disguise. Faces, weapons and banners for heavenly soldiers.

#### `opera_hih07_heavenly_host_lineup.jpg`, `opera_hih04_nezha_li_jing_generals.jpg`, `opera_hih21_host_with_wind_flag.jpg`, `opera_hih16_wukong_vs_nezha_duel.jpg` - 《大闹天宫》, Jilin Peking Opera House, 2014
- Photographer 陈文 | 1920 px | Sources: https://commons.wikimedia.org/wiki/File:Havoc_in_Heaven_Peking_Opera_7.jpg , `..._4.jpg`, `..._21.jpg`, `..._16.jpg` | CC BY 2.0; **REFERENCE-ONLY**
- Teaches: 07 and 04: the heavenly host as a stage tableau (Li Jing with long black beard at centre, Nezha in pink lotus-petal costume, painted-face generals, weapons raised in a fan); 21: the host with a wind flag; 16: Wukong and Nezha crossing weapons, alone on the stage.

---

## 04. The table of the gods / the Peach Banquet (蟠桃會) - `04_peach_banquet_gods/`

**Iconography.** Two different traditions meet here. (a) The banquet itself, 瑤池宴 / 蟠桃會 / 群仙祝壽: the Queen Mother of the West sits behind a long table set on a terrace in front of a standing screen, canopy fans behind her, attendants in a half-circle, a second table for the guest of honour beside hers; dishes of peaches in stemmed bowls; phoenixes or cranes dance in the open court in front; the invited immortals do not sit, they arrive, on foot over waves or on clouds, cranes and beasts, from the opposite side of the picture. The gods are almost never shown seated in rows at table as in a Western feast. (b) The assembly of gods, 朝元圖: all the deities walk in procession in one direction toward the supreme deity; the great emperors are larger, haloed, and seated or standing under fans, with jade maidens, musicians and guardian marshals around them. In *Journey to the West* the banquet is seen only before it starts: the seven fairies picking peaches in the garden, and Wukong alone at the laid tables drinking the wine. So the honest traditional picture for "the monkey at the gods' table" is one monkey at a long empty banquet table with peach dishes, with the grand company shown separately, arriving.

**Best direct references:** (1) `lacma_banquet_of_xiwangmu_detail_banquet_table.jpg` for the table and seating; (2) `yongle_palace_chaoyuan_tu_segment3.jpg` for the gods as a host; (3) `qing_album_leaf15_peach_garden_seven_fairies.jpg` / `qing_album_leaf18_wukong_drinks_stolen_wine_pavilion.jpg` for the story beat.

#### `lacma_banquet_of_xiwangmu_screen_full.jpg`, `lacma_banquet_of_xiwangmu_detail_banquet_table.jpg`, `lacma_banquet_of_xiwangmu_detail_immortals_crossing_waves.jpg` - The Banquet of Seowangmo (Xiwangmu), Queen Mother of the West (瑤池宴圖)
- Unknown, Korea, Joseon dynasty, 18th-19th century (inscribed 丙申), eight-panel screen, ink, colour and gold on silk | LACMA M.2000.15.31a-h | 4096x1646, 2586x4096, 3423x4096
- Source: https://collections.lacma.org/object/99537 | PD-art by age (LACMA credits "photo © Museum Associates/LACMA"; fine for study, check before republishing). Korean court painting following Ming Chinese models.
- Teaches: the full canonical layout in one image: right half, two banquet tables on a terrace under pines with the Queen Mother and King Mu behind them, screens and fans, attendants, phoenix dancing in front; left half, immortals crossing dark waves and flying in. The detail shows the table: red frontal cloth, rows of stemmed dishes, who sits and who stands.

#### `met_paying_homage_to_xiwangmu_fan.jpg` - Paying homage to Xiwangmu, the Queen Mother of the West
- Unidentified artist, China, 15th century, fan mounted as album leaf, ink and colour on silk | The Met 23.33.3 | 3600x3529
- Source: https://www.metmuseum.org/art/collection/search/45666 | CC0, PD-art
- Teaches: Chinese Ming version in miniature: palace terrace, the goddess receiving visitors. Dark silk; composition more than detail.

#### `met_panel_with_immortals_embroidery.jpg` - Panel with immortals (群仙祝壽)
- China, 18th century, silk and metal-thread embroidery on satin | The Met 30.75.31 | 2700x3600
- Source: https://www.metmuseum.org/art/collection/search/68527 | CC0, PD-art
- Teaches: vertical arrangement: palace in clouds at top with figures arriving by crane, immortals gathered on the terrace and in the garden below; flat colour on deep blue, good for a simple staged tableau.

#### `xie_wenli_xiwangmu_with_attendant.jpg` - Xiwangmu, the Queen Mother of the West, with an attendant carrying peaches
- Xie Wenli, c. 1751-1800 (Qing), hanging scroll | British Museum (per Commons) | 1280x2224
- Source: https://commons.wikimedia.org/wiki/File:Xie_Wenli's_painting_of_Xi_Wangmu.jpg | PD-art
- Teaches: how the hostess herself is drawn when shown alone: tall, pale robes with long blue-green ribbons, a girl beside her holding a tray of peaches, under a pine (Commons notes a monkey bringing peaches lower in the scroll).

#### `yongle_palace_chaoyuan_tu_segment3.jpg`, `yongle_palace_chaoyuan_tu_segment7.jpg` - 朝元圖 (Homage to the Primordial), Hall of the Three Pure Ones, Yongle Palace
- Ma Junxiang (馬君祥) and workshop, Yuan dynasty, 1325, wall painting, Ruicheng, Shanxi | 3840x2698, 3840x2618 (originals about 11000x8000)
- Sources: https://commons.wikimedia.org/wiki/File:元_马君祥等_朝元图（永乐宫三清殿壁画）分段3.tiff and `..._分段7.tif` | PD-art
- Teaches: how a crowd of gods is built: one large enthroned or standing emperor per group, haloed, with parasol fans; ranks of officials, jade maidens and armoured marshals stacked three deep, all turned the same way; an incense burner on a lotus stand in front. Robes in green, blue, white with long unbroken contour lines.

#### `eighty_seven_immortals_full_scroll_overview.jpg`, `eighty_seven_immortals_section_haloed_emperor_attendants.jpg`, `eighty_seven_immortals_section_musicians_jade_maidens.jpg` - 八十七神仙卷 (Eighty-seven Immortals)
- Anonymous, Tang or Song (traditionally linked to Wu Daozi), ink on silk handscroll | Xu Beihong Memorial Museum, Beijing | 7000x757 overview; 3600x2800 crops from the 25902x2800 scan
- Source: https://commons.wikimedia.org/wiki/File:Eighty-seven_Celestials.jpg | PD-art
- Teaches: the procession in pure ink line with no colour: banners, canopies, musicians, lotus railings and cloud scrolls under their feet. Line rhythm for robes and ribbons; the best match for drawing a divine company in our ink idiom.

#### `cma_daoist_album_leaf01_enthroned_celestial_emperor_court.jpg` - Album of Daoist and Buddhist Themes: Procession of Daoist Deities, leaf 1
- Anonymous, Southern Song, 1200s, ink on paper | Cleveland 2004.1.1 | 3400x3203 | https://clevelandart.org/art/2004.1.1 | CC0, PD-art
- Teaches: the seated supreme deity: throne on a stepped dais inside a railed terrace, two fans behind, four attendants each side, two guards with axes at the foot of the stairs. A ready-made "high seat of heaven", frontal and symmetrical.

#### `ehon_saiyuki_1806_jade_emperor_court.jpg` - "上帝視妖光" (the Jade Emperor sees the strange light), 《絵本西遊記》 vol. 1 page 16
- Ōhara Tōya, 1806 | 2977x2368 | Source: https://commons.wikimedia.org/wiki/File:WUL-he21_02500_絵本西遊記_01.pdf | PD-art (Japanese)
- Teaches: the Jade Emperor in his pavilion with officials lined below.

#### `ehon_saiyuki_1806_peach_garden_seven_fairies.jpg` - "悟空桃園逢七仙女", vol. 2 page 15
- 2981x2361 | Source: https://commons.wikimedia.org/wiki/File:WUL-he21_02500_絵本西遊記_02.pdf | PD-art (Japanese)
- Teaches: seven fairies with baskets clustered at left, the monkey stalking in from the right among walled peach beds.

#### `qing_album_leaf15_peach_garden_seven_fairies.jpg`, `qing_album_leaf18_wukong_drinks_stolen_wine_pavilion.jpg` - 《清彩绘全本西游记》 vol. 1 pp. 15 and 18
- Anonymous, Qing | 456x694 each | Source: JTTW Research Archive #21 | PD-art
- Teaches: 15: fairies in pale robes picking peaches from heavy red-fruited trees by a pavilion; 18: a lone figure drinking at a table in an open pavilion among cloud and roofs. Colour key: pink peaches, grey-blue roofs, buff cloud.

#### `opera_hih20_seven_fairies_peach_table.jpg` - 《大闹天宫》, Jilin Peking Opera House, 2014
- Photographer 陈文 | 1920x1272 | Source: https://commons.wikimedia.org/wiki/File:Havoc_in_Heaven_Peking_Opera_20.jpg | CC BY 2.0; **REFERENCE-ONLY**
- Teaches: how opera stages the banquet: one table in red embroidered cloth with two dishes of peaches stands for the whole feast; fairies in pale blue and pink with water sleeves.

#### `opera_monkeyking_taipei_wukong_steals_peaches_banquet_table.jpg` - 《美猴王》, Taipei
- Press photo, courtesy Trend Education Foundation | 1536x864 | Source: shaopeng.blog (URL under topic 01) | copyright; **REFERENCE-ONLY**
- Teaches: the monkey alone behind the banquet table, in green-gold robe and pompom crown, both hands lifting a cup to his face; three stands of peaches and a gold ewer on red cloth. The "monkey at the gods' table" image.

---

## 05. The trip to the underworld - `05_underworld/`

**Iconography.** Chapter 3. Wukong feasts with the demon kings, gets drunk and falls asleep under a pine by the iron bridge. In his dream two men carrying a warrant with his name on it (勾死人; later tradition makes them Black and White Impermanence, or Ox-Head and Horse-Face) loop a rope on him and pull his soul, stumbling, to a walled city whose iron sign reads 幽冥界. He wakes to where he is, takes the staff from his ear, beats the two fetchers to pulp, and fights his way in; the ghost soldiers scatter. The Ten Kings come out in a row in court dress and bow. In the Hall of Darkness (森羅殿) he sits at the centre, has the judge bring the registers, finds "魂字一千三百五十號 孫悟空", inks out his own name and then every monkey's, throws the book down and fights his way out; he trips on a clump of grass and wakes under the pine. Pictures show three moments: (1) the sleeping body at the tree with the soul being led off (the soul drawn fainter than the body); (2) the gate, with the fetchers flat on the ground and the staff raised at the signboard; (3) the hall: kings standing aside in a group, a judge with the ledger at a desk under a curtain, the monkey with the brush. The hall always borrows the Ten Kings court formula: desk with frontal cloth, screen behind, clerks, ox- and horse-headed guards at the steps. Opera 《闹地府》 keeps the same order and opens on the judge (判官) alone.

**Best direct references:** (1) `ehon_saiyuki_1806_soul_fetchers_lead_sleeping_wukong.jpg` for the dream journey; (2) `qing_album_leaf10_youmingjie_gate_soul_fetchers.jpg` for the gate; (3) `ehon_saiyuki_1806_striking_the_register_senluo_hall.jpg` together with the existing `monkeys/woodcuts_xiyouji/xyj_wanli_vol01_p47.jpg` for the ledger.

#### `ehon_saiyuki_1806_soul_fetchers_lead_sleeping_wukong.jpg` - "悟空眠松下到冥界" (Wukong sleeps under the pine and arrives in the dark realm), 《絵本西遊記》 vol. 2 page 5
- Ōhara Tōya, 1806 (Waseda copy; pink crayon marks by a former owner) | 2982x2369
- Source: https://commons.wikimedia.org/wiki/File:WUL-he21_02500_絵本西遊記_02.pdf (also extracted as `File:悟空眠松下到㝠界.jpg`) | PD-art (Japanese)
- Teaches: exactly the beat asked for: right page, the monkey slumped asleep at the foot of a pine in solid black line; left page, two fetchers with staffs hauling his soul toward a gate, all three drawn in dotted ghost-line with no solid contour, inside a cloud of stipple. Body in ink, soul in dots: a ready-made device for us.

#### `qing_album_leaf10_youmingjie_gate_soul_fetchers.jpg` - at the gate of 幽冥界, 《清彩绘全本西游记》 vol. 1 p. 10
- Anonymous, Qing | 456x694 | Source: JTTW Research Archive #21 | PD-art
- Teaches: a red-and-gold 牌樓 with the sign "幽冥界" rising out of mist; the monkey swings the staff up at the sign; the two fetchers lie tangled on the ground, one hat rolled away. Everything else is empty buff ground: the underworld as a gate in fog.

#### `ehon_saiyuki_1806_striking_the_register_senluo_hall.jpg` - "悟空抹冥簿延猿命" (Wukong wipes the register), vol. 2 page 7
- 2905x2375 | Source: same PDF (also `File:悟空抹㝠薄延猿命.jpg`) | PD-art (Japanese)
- Teaches: hall labelled 森羅殿; the king (冥王) and the judge (掌案判官) stand to the left looking dismayed; the monkey sits at the centre on the tiled floor with a red brush-stroke through the open book; horned guards cower at right; a round mirror on a stand (業鏡) behind.

#### `opera_monkeyking_taipei_havoc_in_hell_wukong_leaves_underworld.jpg` - 《美猴王》 act 2 "Havoc in Hell", Taipei production led by 朱陸豪
- Press photo, courtesy Trend Education Foundation | 1536x864 | Source: shaopeng.blog (URL under topic 01) | copyright; **REFERENCE-ONLY**
- Teaches: the only stage still of 闹地府 found: the monkey in red aloft on a cloud prop at left, waving; below, the judge in black with red beard, the king in red, and a ring of ghost soldiers in black and white crouching. Staging note from the same review: the act opens with the judge alone, back to the audience, balanced on one leg on a table set on a high platform, in silence, then spitting fire; the ghosts (big-head, small-head, belly) are played for comedy.

---

## 06. Monkey troops alive on Flower-Fruit Mountain - `06_monkey_troop/`

**Notes.** The existing library has the Song gibbon paintings (易元吉 attributions, 宣宗 "Gibbons at play"). These additions are troops: many animals in one frame doing different things. For animating a troop painting the two *Ehon Saiyuki* spreads are the most useful because every monkey is a separate, readable silhouette.

#### `ehon_saiyuki_1806_monkey_troop_at_waterfall.jpg` - the troop at the Water Curtain waterfall, 《絵本西遊記》 vol. 1 page 17
- Ōhara Tōya, 1806 | 2986x2360 | Source: https://commons.wikimedia.org/wiki/File:WUL-he21_02500_絵本西遊記_01.pdf | PD-art (Japanese; the animals are Japanese macaques)
- Teaches: about twenty monkeys strung along a ridge: sitting, scratching, pointing, on all fours, one leaping into the fall with arms up. Each is two or three ink masses plus a face. The single best troop reference.

#### `ehon_saiyuki_1806_monkeys_feast_in_cave.jpg` - "石猴洞中…" the feast in the cave, vol. 1 page 19
- 2954x2344 | same source | PD-art (Japanese)
- Teaches: a dozen monkeys packed round a low table, one pouring from a kettle, others reaching, eating, turning to talk. Group as one dark mass with hands and faces picked out.

#### `ehon_saiyuki_1806_wukong_among_little_monkeys.jpg` - Wukong among the small monkeys, vol. 1 page 30
- 2919x2339 | same source | PD-art (Japanese)
- Teaches: scale and attitude: the clothed king squatting, small monkeys sitting round him grooming and listening.

#### `qing_album_leaf02_monkeys_at_waterfall.jpg`, `qing_album_leaf13_monkey_banquet_in_cave.jpg` - 《清彩绘全本西游记》 vol. 1
- Anonymous, Qing | 456x694 each | Source: JTTW Research Archive #21 | PD-art
- Teaches: the Chinese colour version: tawny monkeys perched on rocks either side of a white waterfall under peach branches; and monkeys in jackets feasting at a long table inside a cave hung with red curtains.

#### `met_mori_sosen_monkeys_at_play_pair.jpg`, `..._detail1.jpg`, `..._detail2.jpg` - Monkeys at Play
- Mori Sosen (森狙仙), Japan, late 18th century to before 1807, pair of hanging scrolls, ink and colour on silk | The Met 14.76.17, .18 | 2293x3600, 2201x3600, 1923x3600
- Source: https://www.metmuseum.org/art/collection/search/49058 | CC0, PD-art (Japanese)
- Teaches: real monkey behaviour drawn from life: grooming, clutching young, reaching; fur built from fine dry strokes over wash. For how a hand, a hunched back or a turned head actually looks.

#### `npm_song_gibbons_at_play_in_loquat_tree.jpg` - 宋人 枇杷猿戲圖 (Gibbons at play in a loquat tree)
- Anonymous, Song dynasty, hanging scroll, ink and colour on silk | National Palace Museum, Taipei | 3840x6088 (original 12207x19352)
- Source: https://commons.wikimedia.org/wiki/File:宋人枇杷猿戏图轴.绢本设色.台北故宫博物院藏.jpg | PD-art
- Teaches: the Chinese classic of two animals in relation: one black gibbon hanging by one arm and looking down, the other seated on the trunk looking up. Fur as soft dark mass with a pale face ring; a ready two-beat loop (swing / watch).

#### `cma_mori_sosen_monkeys_mother_and_young.jpg` - Monkeys
- Mori Sosen (森狙仙), Japan, Edo period, ink and colour on silk | Cleveland Museum of Art 1990.129 | 3840x2924 (original 14374x10944)
- Source: https://commons.wikimedia.org/wiki/File:Mori_Sosen_-_Monkeys_-_1990.129_-_Cleveland_Museum_of_Art.tiff | CC0, PD-art (Japanese)
- Teaches: a mother hunched over two young, grooming: the curled posture, hands and feet, and fur rendered hair by hair over grey wash.

#### `opera_hih01_monkey_troop_group_pose.jpg`, `opera_hih05_monkey_troop_line_with_staffs.jpg` - 《大闹天宫》, Jilin Peking Opera House, 2014
- Photographer 陈文 | 1920x1272 | Sources: https://commons.wikimedia.org/wiki/File:Havoc_in_Heaven_Peking_Opera_1.jpg , `..._5.jpg` | CC BY 2.0; **REFERENCE-ONLY**
- Teaches: the stage troop: twelve monkeys in plain yellow piled into one pyramid, all scratching and peering in different directions; and a diagonal line of crouched monkeys each with a pompom staff.

#### `opera_monkeyking_taipei_troop_under_qitian_dasheng_banner.jpg` - 《美猴王》, Taipei
- Press photo, courtesy Trend Education Foundation (carries the production's title lettering) | 1920x1080 | Source: shaopeng.blog | copyright; **REFERENCE-ONLY**
- Teaches: the victory tableau: the whole troop in yellow massed under the vertical "齊天大聖" banner, three Wukongs in the middle.

---

## 07. Calligraphy inscriptions beside paintings (題跋 / 題畫詩) - `07_inscriptions/`

**What to take from these, for placing lyric calligraphy.** The inscription sits in the unpainted area and is treated as part of the composition's weight: usually top right or top left, opposite the main mass of the picture. Columns run top to bottom and right to left; column tops are level, bottoms ragged; two to five columns is typical for an album leaf. Character size is small relative to the picture (a column is roughly one twentieth to one fifteenth of the leaf's width). One or two red seals close the text at the lower left of the last column; sometimes one more seal sits alone in the opposite bottom corner to balance. The ink of the writing matches the darkest ink in the painting. Nothing is boxed or framed.

#### `met_shitao_wilderness_colors_leaf_a_river_pavilion.jpg`, `..._leaf_e_mountain_village.jpg`, `..._leaf_h_blue_peaks.jpg`, `..._leaf_l_bridge_cottage.jpg` - Wilderness Colors (野色), four of twelve leaves
- Shitao (石濤), c. 1700, album, ink and colour on paper | The Met 1972.122a-l | about 2850x3600 each
- Source: https://www.metmuseum.org/art/collection/search/49176 | CC0, PD-art
- Teaches: four placements on the same leaf format. (a) three short columns top right over open water, seal below, a second seal bottom left; (e) a tight block top left above the peaks; (h) columns set into the sky between two mountain masses; (l) two tiny columns in the top right corner, nearly a signature. Best models for a short lyric line in a landscape's blank.

#### `met_shitao_returning_home_spread_poem_facing_boat.jpg` - Returning Home (歸棹), one opening
- Shitao, c. 1695, album of twelve leaves, each painting facing a leaf of calligraphy | The Met 1976.280 | 3501x2736
- Source: https://www.metmuseum.org/art/collection/search/49173 | CC0, PD-art
- Teaches: the other option: poem on its own facing page, six columns of running script, painting opposite almost empty (one boat, a line of hills). "Calligraphy accompanying a painting" in the most literal form; good for a held lyric card.

#### `met_wu_zhen_fisherman.jpg` - Fisherman (漁父圖)
- Wu Zhen (吳鎮), c. 1350, handscroll, ink on paper | The Met 1989.363.33 | 3600x2700
- Source: https://www.metmuseum.org/art/collection/search/41468 | CC0, PD-art
- Teaches: poem in cursive floating in the empty water to the right of the boat, at the same height as the trees on the left: text used as a counterweight.

#### `met_ni_zan_woods_valleys_mount_yu.jpg` - Woods and Valleys of Mount Yu (虞山林壑圖)
- Ni Zan (倪瓚), dated 1372, hanging scroll, ink on paper | The Met 1973.120.8 | 1986x3600
- Source: https://www.metmuseum.org/art/collection/search/45636 | CC0, PD-art
- Teaches: the artist's small neat inscription in the upper sky, later owners' inscriptions and seals added around it: how a blank sky fills up over time, and how small the script is against the scroll.

#### `met_zhao_mengfu_twin_pines_level_distance.jpg` - Twin Pines, Level Distance (雙松平遠圖)
- Zhao Mengfu (趙孟頫), c. 1310, handscroll, ink on paper | The Met 1973.120.5 | 3600x874
- Source: https://www.metmuseum.org/art/collection/search/40508 | CC0, PD-art
- Teaches: horizontal format: the long inscription stands as a block at the far left end after a stretch of empty water; title and seal at the far right.

#### `met_jin_nong_blossoming_plum.jpg` - Blossoming plum (梅花圖)
- Jin Nong (金農), dated 1759, hanging scroll, ink on paper | The Met 1989.363.160 | 1717x3600
- Source: https://www.metmuseum.org/art/collection/search/49243 | CC0, PD-art
- Teaches: the opposite extreme: a long text in blocky "lacquer script" filling the space between branches, text as texture. Use as a warning about density as much as a model.

---

## Gaps and things not found

- **Pre-1949 photographs** of 杨小楼, 李少春 or 李万春 as Wukong: none found in open collections or on Commons. The earliest stage photo here is 1962 (Shaoju).
- **钻天盔 / 草王盔 with pompoms, close-up, and the yellow 制度衣 with blue roundels** described in `docs/research/OPERA_WUSHU.md`: no open image. The stills show the soft knotted cap and one hard cap with a front pompom (`opera_liyuan_...`), and the pompom crown on the king costume (`opera_hih18_...`).
- **Chinese painting of the five finger-pillars or of the monkey inside the open palm:** not found before the 20th century; Ming/Qing editions show the wager or the finished mountain. The pillar picture is Japanese, 1806.
- **Qing 彩绘全本西游记:** only the 2008 abridged reprint at about 456x694 per leaf was reachable. Good for composition and colour, too small for detail.
- **Opera stills of 《闹地府》:** one press photo only (Taipei production). No stills of the ledger scene itself on stage.
- **易元吉 《聚猿圖》** (Osaka City Museum of Fine Arts) and Chinese 百猿圖 scrolls: no open-access image found; the troop references are Japanese woodcuts, the Qing album, and Mori Sosen.
- **蟠桃會 Chinese handscrolls** (Nelson-Atkins "Festival of the Peaches of Longevity" 蟠桃圖, and "One Hundred Immortals on a Journey" 蟠桃會): only 1000-px images on the museum site, not saved. Pages: https://art.nelson-atkins.org/objects/11738 and https://art.nelson-atkins.org/objects/1822 .
- **1888 《新說西遊記圖像》:** scan is about 545x867 per picture; one kept.

## DONE 2026-11-17 late evening

Final report (same text sent to the lead):

- 92 images in seven folders under `refs/paintings/v3/`, all viewed; this manifest holds per-image entries, iconography summaries for topics 02 to 05, and best picks.
- Best picks. 01: `01_wukong_opera_yellow/opera_hih02_DETAIL_costume_jacket_cap_face.jpg`, `opera_hih02_wukong_front_staff_with_little_monkey.jpg`, `shaoju_1962_liu_lingtong_wukong.jpg` (all reference-only). 02: `02_buddha_palm_wuxingshan/ehon_saiyuki_1806_wukong_in_buddhas_palm_five_finger_pillars.jpg`, `qing_album_leaf28_wager_before_buddha_thunder_generals.jpg`, `qing_album_leaf29_under_five_elements_mountain_guanyin.jpg`. 03: `03_havoc_in_heaven/qing_album_leaf22_erlang_duel_in_clouds.jpg`, `ehon_saiyuki_1806_four_heavenly_gods_vs_wukong_hair_monkeys.jpg`, `cma_daoist_album_leaf14_heavenly_marshals_on_clouds.jpg`. 04: `04_peach_banquet_gods/lacma_banquet_of_xiwangmu_detail_banquet_table.jpg`, `yongle_palace_chaoyuan_tu_segment3.jpg`, `qing_album_leaf18_wukong_drinks_stolen_wine_pavilion.jpg`. 05: `05_underworld/ehon_saiyuki_1806_soul_fetchers_lead_sleeping_wukong.jpg`, `qing_album_leaf10_youmingjie_gate_soul_fetchers.jpg`, `ehon_saiyuki_1806_striking_the_register_senluo_hall.jpg`. 06: `06_monkey_troop/ehon_saiyuki_1806_monkey_troop_at_waterfall.jpg`. 07: the four `07_inscriptions/met_shitao_wilderness_colors_leaf_*.jpg`.
- Gaps: as listed under "Gaps and things not found".
