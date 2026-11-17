# LOG v3 FACES team (bridge H1-H4), preview_v3

## CHECKPOINT 14:57
- **Done:** research (subagent, finished; refs + licences in `refs/lianpu_v3/SOURCES.txt`, text-free crops in
  `refs/lianpu_v3/crops/`); archetype mapping decided (section 1); all 23 faces regenerated as named real 脸谱
  (`design/plates/F_lianpu/v3/`: prompts `faces_v3.json`, generator `gen_faces.py`, candidates + prompt txt in `_cand/`,
  picks `picks.json` (all take a, TANGQIN take b), normaliser `normalise.py` -> `v3/faces/`, index
  `design/plates/F_lianpu/F_faces_v3.json`); child back view with v3 hair (`v3/child/child_back_a.png`);
  `shots/faces_lib.py` rewritten for v3 (ALBUM cell map, painted surface for wide framings, `FaceMediums`, new child);
  `shots/H1.py` `H2.py` `H3.py` edited (medium switch in H1/H2, named cells); v2 copies in `shots/_v2`, `media/comp/_v2`.
- **In progress:** tuning the three media on test frames (scratchpad stills); then full renders of H1-H4.
- **Next:** render H1 H2 H3 H4 `--fresh`, review sheets `work/review/comp_v3/H1..H4.jpg`, fix, write per-shot notes.
- **Pending relay jobs:** none (all generation was synchronous `cf.py`, gpt-image-2).
- **Spend so far:** about $5.0 (25 gpt-image-2 calls at ~$0.2). Ceiling $30.
- **Decisions:** tool = 关羽, threat = 曹操, trick = 汤勤 (豆腐块; 蒋干's patch shape is disputed between sources), kid = the
  unpainted 娃娃生 face (哪吒), no monkey face on the leaf, silver = 木吒 (weakly attested, flagged). Medium switch uses the
  BOOK team's `tools/ink/medium.py` grounds through a faces wrapper (gouache lighter than paper needs its own mark maps).
- **Open questions for the lead:** none blocking. Director may prefer 黄盖 for "tool" (see notes under the table).

Render: `PY -m tools.ink.run shots/<ID>.py --t0 IN --t1 OUT --size 960x540 --fresh --out media/comp/<ID>.mp4`.
v2 comps and scripts are in `media/comp/_v2/`, `shots/_v2/` (H1-H4 and `faces_lib.py`).

## 1. The director's question (H3, 2:42): "do these correspond to what the types of archetypal characters are?"

**In v2: no.** All 23 faces were deliberately "original designs" in the right families (PLATES.md: "F02 avoids Bao
Zheng's crescent, F07 avoids Zhang Fei's butterfly"), and several had no real pattern grammar at all (see the audit,
section 3). The four under the words were a blue face, a black face, a water-white face and a clown: only the last two
meant anything close to their word.

**In v3: yes.** Every face on the leaf is now the conventional 脸谱 of a named character, the sheet follows the
traditional colour code, and the four faces under the four words are these:

| word (onset) | cell | character | 谱式, colour | what the colour/type means in the tradition | why it answers the word |
|---|---|---|---|---|---|
| **Tool** (162.63) | 10 | 关羽 Guan Yu | 红整脸: whole face cinnabar red, 卧蚕眉, 丹凤眼, one black mole (the "破脸" dot) | Red = 忠勇, loyal and brave. Guan Yu is the type itself: the sworn brother who serves his lord to the death | The loyal one, seen from the master's side, is the useful one: the perfect servant. Later courts promoted his cult precisely as a model of service |
| **threat** (163.48) | 3 | 曹操 Cao Cao | 水白整脸: whole face chalk white, thin "奸眉", long triangular slit eyes, a few fine black lines | White = 奸诈, treacherous and suspicious. The face an audience is taught to distrust on sight | The category "dangerous, do not trust it" has had this face for centuries |
| **trick** (164.36) | 13 | 汤勤 Tang Qin (《审头刺汤》) | 丑, 袍带丑: plain skin with the square white 豆腐块 over the nose and inner eyes | The 丑 (also called 小花脸 / 三花脸, "the small painted face") is the clown: wit, tricks, the schemer and the fool. Tang Qin is the sly mounter who schemes against his own benefactor | The clown's patch is the tradition's mark for "this one is a trick / a joke" |
| **kid** (165.24) | 14 | the 娃娃生 face (as 哪吒 Nezha is shown in both Qing albums) | 俊扮: NOT painted. Powdered skin, rouge, a small red dot at 印堂 between the brows, a child's fringe | Children are the one role type the tradition does not give a pattern: a child has no fixed character yet | "Kid" is the category that is no category: an unpainted face. It sits beside the bare cell 15, where the child herself stands, not yet even drawn |

Notes for the director:
- The first row of the leaf plus Guan Yu are the faces of the rhyme every Chinese viewer knows (《说唱脸谱》: 蓝脸的窦尔敦,
  红脸的关公, 黄脸的典韦, 白脸的曹操, 黑脸的张飞). H1 opens on 窦尔敦, the blue face, on the crash.
- Alternatives that are already on the leaf if she prefers them (changing `SEAL_CELLS` / `SHOTS` in `shots/H3.py` and
  `faces_lib.py` is two lines): **tool** = 黄盖 Huang Gai (cell 5, old-red 六分脸), the old general who volunteers to be
  flogged as the instrument of the fire-ship ruse ("周瑜打黄盖"): a sharper pun, a less famous face; or 周仓 (cell 18), Guan
  Yu's weapon-bearer. **trick** = 时迁 (cell 16), the thief, martial clown with the date-pit patch.
- **No monkey face on the leaf** (as v2): the 猴脸 exists (red inverted-peach patch on white, gold eye rings; 杨小楼 / 李万春 /
  李少春 variants, court-album leaf in `refs/lianpu_v3/ogp_1-12_sunwukong.jpg`) and is the stage monkey's own face in the
  hook shots, but the bridge's point is that the categories are the ones laid on him and on the child; his own face is
  not one of the boxes. Easy to add if wanted (one generation, cell swap).

## 2. The album leaf, v3 (cell -> character -> type -> meaning)

Row-major, 6 x 4; cell 15 is bare. `shots/faces_lib.ALBUM`. Verified = pattern grammar stated in at least one fetched
source (list in section 4); K = from general knowledge of the convention, not re-verified this session.

| cell | id | character | 谱式 and colour | traditional meaning | check |
|---|---|---|---|---|---|
| 0 | ZHANGFEI | 张飞 | 黑十字门 "蝴蝶脸": black pillar brow to nose, laughing butterfly sockets, bat brows, pink cheeks | black = rough, blunt, loyal | verified |
| 1 | BAOZHENG | 包拯 | 黑整脸, white crescent, knitted white brows | black = upright, impartial | verified + Met leaf DP280091 as pattern ref |
| 2 | DIANWEI | 典韦 | 黄花三块瓦, a halberd drawn in each white brow | yellow = fierce, ruthless in battle | verified |
| 3 | CAOCAO | 曹操 | 水白整脸, thin 奸眉, slit triangular eyes | white = treacherous, suspicious | verified (Met leaf DP280111 agrees) |
| 4 | XUYANZHAO | 徐延昭 | 紫六分脸, huge white brows, purple strip on the forehead | purple = solemn, steadfast, loyal old minister | family verified, detail K |
| 5 | HUANGGAI | 黄盖 | 老红 (pinkish old-red) 六分脸 | old red = loyal old general | verified |
| 6 | CHENGYAOJIN | 程咬金 | 绿碎脸 | green = impetuous, rash, rough hero | verified (colour; one wiki page says blue; the Met Qing leaf is blue/white/red: the green is the modern convention) |
| 7 | JIANGWEI | 姜维 | 红三块瓦 with the 太极 on the forehead | red = loyal; the taiji = his learning in strategy | verified |
| 8 | DOUERDUN | 窦尔敦 | 蓝花三块瓦, the 护手钩 on red brow grounds | blue = staunch, fierce, unbending | verified |
| 9 | GAODENG | 高登 | 油白三块瓦 | oil-white = overbearing, arrogant (not treachery) | family verified, detail K |
| 10 | GUANYU | 关羽 | 红整脸 | red = loyal and brave | verified |
| 11 | ZHENGEN | 郑恩 (郑子明) | black-and-white 歪脸, 雌雄眼 | crooked face = blunt, comic-ugly, loyal | verified |
| 12 | LUZHISHEN | 鲁智深 | 白僧脸, 舍利珠 on the forehead, kidney sockets, 螳螂眉 | the monk's face | verified (brows K) |
| 13 | TANGQIN | 汤勤 | 丑, square 豆腐块 | the clown: scheming, comic | verified (patch follows the Qing Met leaf DP280175: it spans the inner eyes, red cheek dots) |
| 14 | KID | 娃娃生 (哪吒) | 俊扮: unpainted, red dot at 印堂 | a child has no pattern | verified (cnpoc; both Qing albums show 哪吒 unpainted, Met DP280080) |
| 15 | | bare | | the child stands here | |
| 16 | SHIQIAN | 时迁 | 武丑, date-pit patch on the nose | the nimble thief, the martial clown | patch type verified, detail K |
| 17 | LIUJIN | 刘瑾 | 红太监脸, forehead disc, cleaver sockets, white lower lip | the red here is satirical well-fed flesh, not loyalty: the powerful eunuch | verified |
| 18 | ZHOUCANG | 周仓 | 花元宝脸, pale blue-green ingot forehead | the ingot face: rough loyal retainer | verified |
| 19 | ERLANG | 二郎神 杨戬 | gold 三块瓦 with the vertical third eye | gold = gods | verified + Met leaf DP280075 as pattern ref |
| 20 | JINQIANBAO | 金钱豹 | gold 象形脸: leopard mask on the forehead, coins (no script) on the cheeks | gold = spirits and demons | verified |
| 21 | ZHONGKUI | 钟馗 | 花元宝脸, red ingot forehead with a gold bat | the demon-queller: ugly, kind | verified |
| 22 | XIAHOUDUN | 夏侯惇 | 蓝三块瓦, red arrow wound under his left eye | blue = fierce, staunch | verified (candidate mirrored in `normalise.py` so the wound is on his left) |
| 23 | MUZHA | 木吒 | silver god face | silver = gods and spirits | **weak**: silver for 木吒 is stated by CCTV and the Tianjin museum page only; another catalogue paints him grey. No universally agreed silver face exists; kept because the colour code names silver |

Colour code covered: red (关羽, 姜维; old red 黄盖), black (包拯, 张飞, 郑恩), white 水白 (曹操) and 油白 (高登), yellow (典韦),
blue (窦尔敦, 夏侯惇), green (程咬金), purple (徐延昭), gold (二郎神, 金钱豹), silver (木吒), the monk, the eunuch, the ingot
faces, two clowns (文 豆腐块, 武 枣核), the unpainted child. No face contains writing (项羽's 寿 brows, 杨七郎's 虎 and the
佛/卍 monkey variants were avoided on purpose; 姜维's taiji and 典韦's halberds are symbols, not script).

## 3. Audit of the v2 leaf (what was wrong)

| v2 | v2 label | verdict | v3 |
|---|---|---|---|
| F01 | 整脸 red | generic red, close to 关羽 without his brows/mole | 关羽 proper |
| F02 | 整脸 black, cloud brows, "no crescent" | invented (deliberately not 包拯) | 包拯 |
| F03 | 整脸 purple | invented; purple faces are 三块瓦 / 六分脸 | 徐延昭 六分脸 |
| F04 | 三块瓦 blue | invented layout (blue mask with white rings), not three tiles | 窦尔敦 |
| F05 | 花三块瓦 green | plausible family, no character | 程咬金 碎脸 |
| F06 | 尖三块瓦 yellow | invented (white wedges) | 典韦 |
| F07 | 十字门 black | a literal black cross on white/grey: not the 十字门 grammar (deliberately not 张飞) | 张飞 |
| F08 | 花十字门 red | invented | 姜维 |
| F09, F10 | 六分脸 red / slate | right family; slate is not a 六分脸 colour | 黄盖; 高登 |
| F11, F12 | 碎花脸 | decorative, no character | 钟馗, 周仓 |
| F13 | 歪脸 | half green half red: invented; 歪脸 is crooked features, not split colours | 郑恩 |
| F14 | 丑 豆腐块 | patch had been repainted in code as a thin vertical bar: not a 豆腐块 | 汤勤 |
| F15 | 丑 date-pit | a white eye-mask: invented | 时迁 |
| F16, F17 | 神仙脸 gold / silver | generic; silver with blue flames invented | 二郎神, 金钱豹; 木吒 |
| F18 | 僧道脸 | two black discs for brows: invented | 鲁智深 |
| F19 | 太监脸 | white with rouge: reads as a 旦, not a eunuch face | 刘瑾 |
| F20 | 元宝脸 | tan over blue halves: not the ingot grammar | 周仓 / 钟馗 |
| F21 | 水白脸 | right type, weak (never normalised) | 曹操 |
| F22 | 油白脸 | plausible, generic | 高登 |
| F23 | 整脸 green | invented | 夏侯惇 (blue) |

All 23 replaced. The v2 plates stay in `design/plates/F_lianpu/faces/` (F01 is still the outline reference for generation).

## 4. Research sources

Subagent report (web, 2026-11-17). Colour code and pattern grammar: 中新网 齐如山 summary
(chinanews.com/zxys/jjlp.htm), CCTV 戏曲 (cctv.com/opera/20040707/101132_1.shtml), 澎湃 / Tianjin museum
(thepaper.cn/newsDetail_forward_3605111), the 何永泉 catalogue of 1,113 faces (beijingopera.org/masks/), 台湾传艺中心
(ncfta.gov.tw/cp.aspx?n=1781), 中国京剧艺术网 (cnpoc.cn), zh.wikipedia 脸谱. Baidu Baike was unreachable.
Public-domain images (reference only for looking; the three text-free crops named in `faces_v3.json` "ref" fields were
passed to the image model: 包拯, 二郎神, and the 丑 for 汤勤; all CC0): Met Museum "One hundred portraits of Peking opera
characters" (acc. 30.76.299, CC0) and the 昇平署脸谱 court album (National Library of China via Wikimedia Commons, CC0);
files and licences in `refs/lianpu_v3/SOURCES.txt`. No copyrighted photograph was passed to any model.
Points worth knowing: 丑 really is called 小花脸 / 三花脸; 娃娃生 are 俊扮 (unpainted); neither 哪吒 nor 红孩儿 has a
standard 脸谱; 刘瑾's red and 晁盖's yellow are skin tones, not the colour code; silver is the weakest colour.
