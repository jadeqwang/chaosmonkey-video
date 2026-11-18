# LOG v3 FACES verify (H1-H4 album leaf): source check + Sun Wukong face

## CHECKPOINT 17:20
- **Done:** everything. Verification table (section 1), monkey face (section 2), disputes (section 3), files (section 4);
  H1-H4 re-rendered (158 / 152 / 80 / 79 frames, 960x540, 24 fps, ffprobe-counted); review sheets
  `work/review/comp_v3/H1..H4.jpg` rebuilt and looked at; `design/plates/PLATES.md` group F rewritten for v3.
  See `## DONE` at the end.
- **In progress / next:** nothing.
- **Spend this pass:** $4.85 (24 gpt-image-2 calls, tags `lianpu_v3_<ID>_c` / `_d`). Ceiling $15.

## 0. Method

Each painted face (`design/plates/F_lianpu/v3/faces/`, downscaled to 680 px contact sheets) was compared with at least
two independent sources fetched this session. Sources used throughout (abbreviations in the table):

- **BO**: 何永泉《京剧脸谱选绘》 digital catalogue, 1,113 faces after named masters, each with 谱式 / main colour / role:
  https://www.beijingopera.org/masks/ (data: https://www.beijingopera.org/data/catalog.json). One painter's album, but
  consistent with CCTV and NCFTA wherever they overlap. Its images are copyrighted: looked at only, never passed to a model.
- **CCTV**: CCTV 戏曲《京剧脸谱的颜色》 http://www.cctv.com/opera/20040707/101132.shtml and `_1.shtml`; also
  http://www.cctv.com/opera/20040625/101998.shtml (谱式).
- **CNPOC**: 中国京剧艺术网 colour / 谱式 primer https://www.cnpoc.cn/cnpoc/gjkt/200807/f1f8824fe1f4433a8f95a53f8e9278fa.shtml
  and the 丑 page https://www.cnpoc.cn/cnpoc/gjkt/ (654def2b…), 包拯 page (200902/09f53e26…), 孙悟空 page
  https://www.cnpoc.cn/cnpoc/gjkt/200902/ece77c901432482da3397980527be8fb.shtml
- **NCFTA**: 台湾传统艺术中心 脸谱 page https://www.ncfta.gov.tw/cp.aspx?n=1781
- **ZHWP**: zh.wikipedia 臉譜 https://zh.wikipedia.org/wiki/臉譜 ; 斬黃袍 https://zh.wikipedia.org/wiki/斬黃袍
- **MET**: Met Museum "One hundred portraits of Peking opera characters", acc. 30.76.299 (CC0),
  https://www.metmuseum.org/art/collection/search/51581 (leaves in `refs/lianpu_v3/`).
- **OGP**: 昇平署脸谱 Qing court album (NLC / WDL, CC0 on Commons), `refs/lianpu_v3/ogp_*`.
- others named per row (sohu / meipian / wenxuecity / douban / jibi.net / chinawenhua / bjd / xikao / ifeng).

Baidu Baike and Zhihu returned 403 to every fetch; anything attributed to them below is from a search-engine summary and
is marked *(snippet)*: never the only support for a verdict. Verdict scale: **correct**; **minor** = a deviation an
opera-literate viewer would not object to; **wrong** = one they would catch. "Fixed" = regenerated this pass (same
generator `gen_faces.py`, gpt-image-2, F01 outline ref, same paper/brush style text; new prompts in `faces_v3.json`).

## 1. Verification table

| cell | character | claim checked | sources | verdict | what was done |
|---|---|---|---|---|---|
| 0 | 张飞 | 净; 黑十字门 / 蝴蝶脸 (郝寿臣's name), black pillar forehead to nose, butterfly laughing eyes, bat brows, pink cheeks; black = 刚直/粗豪 | BO 07-045 《长坂坡》 https://www.beijingopera.org/masks/07-045-zhang-fei/ , 07-017; meipian https://www.meipian.cn/4mpbsxvf ("从额顶一直勾到鼻尖以下", 《芦花荡》 蝠型眉, 笑眼窝 蝴蝶); sohu https://www.sohu.com/a/231097355_562513 ; CNPOC; CCTV | minor (was: mouth a closed black crescent; pillar stopped above the nose tip) | **Fixed** (take d): unbroken pillar past the nose tip, black 嘴叉 bands from the nostrils to the jaw, red laughing mouth, white chin with two dots |
| 1 | 包拯 | 黑整脸, white 月牙, knitted white brows; black = 刚正, impartial | BO 12-067 (铡美案, "黑整脸，又叫无双脸"; crescent orientation varies by school; maroon cheeks attested); CNPOC 包拯 page (crescent = judges by day and night); CCTV; MET DP280091 | correct | none |
| 2 | 典韦 | 黄花三块瓦, halberd (戟) in each white brow; yellow = 骠悍, 凶残 | BO 07-008 ("白眉子中画有他使用的兵器戟形"), 07-016; CCTV (《战宛城》中的典韦 as the yellow example); CNPOC ("黄色…如宇文成都、典韦") | correct (optional red 印堂 accents) | none |
| 3 | **曹操 (threat)** | 水白整脸, 奸眉, slit eyes; white = 奸诈. Mole above one brow? | BO 07-004, 07-015, 07-021 (all 水白脸; 袁世海 version thicker up-turned brows, pink 印堂); CNPOC (白 = 奸臣); ZHWP 臉譜 (曹操 the example); MET DP280111 《阳平关》 (symmetric dots, 印堂 mark) | minor -> fixed: the single mole is **not attested** anywhere; the 印堂 mark and eye-corner wrinkles were missing | **Fixed** (take d): no mole; flesh-pink 印堂 with a curved black stroke; fine wrinkles fanning from the eye corners and along the nasolabial folds; long tapering eye outlines |
| 4 | 徐延昭 (flagged) | 铜锤; 紫六分脸, big white brows, purple forehead pillar; purple = 刚正威严, 忠义 | BO 15-051 《大保国》 ("六分脸，紫为主色"; listed as 徐彦昭), 15-053 《探皇陵》; CCTV ("紫色介于黑红两色之间…《大保国》中的徐延昭"); sohu https://www.sohu.com/a/970492185_121124707 (紫六分脸, 裘派) | **verified**: character, play, 谱式, colour; hue was wrong (lilac) | **Fixed** (take d): deep maroon-aubergine opera 紫, pillar to the hairline, oval black dots at the brow heads, light eye outlines |
| 5 | 黄盖 | 红六分脸 (老脸), grey-shaded white brows; red = loyal old general | BO 07-052 https://www.beijingopera.org/masks/07-052-huang-gai/ ("六分脸…红、白为主色…眉子要套灰色"); CCTV (忠勇良将…如黄盖) | minor -> fixed: painted salmon pink; CCTV treats pink (粉红) as a separate colour for other old men, so it could misread | **Fixed** (take d): saturated oil red, red pillar, brow-head dots |
| 6 | 程咬金 | 绿碎脸; green = 勇猛暴躁 | BO 09-013 (侯喜瑞), 09-018 (袁世海, 《响马传》) both "绿碎脸"; CCTV ("《响马传》中的程咬金"); CNPOC | correct | none (the Qing MET leaf DP280134 is blue: an older variant) |
| 7 | 姜维 | 红三块瓦, 太极图 on the forehead; red = 忠勇; taiji = 足智多谋 | BO 07-108 《天水关》 ("脑门儿上勾'太极图'，以示人物足智多谋"), 07-118 《铁笼山》; sohu https://www.sohu.com/a/340664771_650777 ("勾红三块瓦脸，额上有一太极图"); CNPOC | minor-to-noticeable: thin bar brows did not make three tiles; black nostril blobs | **Fixed** (take d): white-edged black eye/brow wedges dividing three red tiles, red nose, 嘴叉 to the jaw. (Link to Zhuge Liang: snippets only; the log no longer states it) |
| 8 | 窦尔敦 | 蓝花三块瓦, his double hooks on red/yellow brows; blue = 刚强, 桀骜不驯 | BO 16-008, 16-057..061 (郝寿臣 version: "黑眉子上的红底黄色图形"; 侯/裘 versions "眉间白纹"); CCTV 101998 ("《连环套》中的窦尔墩（兰花三块瓦）"); NCFTA; CNPOC | correct / minor (forehead is the 郝/侯 white-line type; 袁世海's is a red 茨菰叶) | none |
| 9 | 高登 (flagged) | 《艳阳楼》; 油白三块瓦, black pointed brows; 油白 = 刚愎, overbearing | sina blog https://blog.sina.com.cn/s/blog_50c78a970102wshg.html ("油白色三块瓦脸"); sohu https://www.sohu.com/a/413390096_716473 ("油白脸多为刚愎自用的狂妄武夫，如高登、马谡"); xikao stage photos; NCFTA (白 = 剛愎自用) | **verified**, minor (stage versions add nose-hair strokes and a drunken pink flush *(snippet)*) | none |
| 10 | **关羽 (tool)** | 红整脸 (揉红), 卧蚕眉, 丹凤眼, black mole = 破脸; red = 忠勇 | NCFTA ("腮上黑痔有「點破」之意…恭敬之忱"); ZHWP 臉譜 ("如重枣，卧蚕眉，单凤眼和七星痔"); wenxuecity https://www.wenxuecity.com/blog/201504/68605/26964.html ; CNPOC (红 = 忠勇义烈, 关羽 named) | correct | none (sources split one mole vs 七星痣; one is the commoner modern stage form) |
| 11 | 郑恩 (郑子明) | 黑歪脸, 雌雄眼, forehead spiral | ZHWP 斬黃袍 (the play) and 臉譜 ("郑子明…雌雄眼…破脸的典型"); NCFTA (歪臉; 鄭子明 額上螺旋形 = 執拗); douban https://www.douban.com/doulist/27222354/ (郝寿臣 version, 《打龙棚》) | correct | none (the old log's 《送京娘》 is not supported; plays are 《斩黄袍》《打龙棚》) |
| 12 | 鲁智深 (brows flagged) | 白僧脸, red 舍利 圆光, 腰子眼窝, brows | BO 13-009 《野猪林》 ("和尚脸…螳螂眉子生动，眉间的'圆光'"), 13-004 (钱金福); jibi.net 15_58_49_118 (孔雀眉, 腰子眼窝, 白僧脸, 粉红脸颊, 眉中九点); CNPOC ("《野猪林》…鲁智深画白脸") | minor: brows **verified** as 螳螂眉 (BO, 袁世海) with 孔雀眉 in other versions; the painted hooked brows read as either. Missing the small 戒疤 dots | none (dots too small to read at the leaf's scale) |
| 13 | **汤勤 (trick)** | 丑 (方巾丑), square 豆腐块; 丑 / 小花脸 / 三花脸 = comic, scheming | bjd (方巾丑 list: "《一捧雪》的汤勤…奸狡轻狂、忘恩负义的势利小人"); CNPOC 丑 page ("文丑多在眼睛和鼻子周围画豆腐块状或腰子状"); CCTV (丑角: 腰子, 豆腐, 枣核); zhihu *(snippet)* "汤勤是方型'豆腐块儿'粉脸勾菱形眼" | **wrong** (detail): the red cheek dots came from the Qing 旗牌 (herald) leaf used as ref; no 汤勤 source has them | **Fixed** (take c, no ref): square white block over both eyes and the nose bridge, lozenge eye outlines, sly side glance, no red |
| 14 | **娃娃生 / 哪吒 (kid)** | 俊扮 (unpainted), rouge, red dot at 印堂 | chinawenhua https://www.chinawenhua.com.cn/zyishu/2019/11666.html ("娃娃生…眉心上方部位点一个红色圆点"); CNPOC 哪吒 page (孩儿发, red dot on 印堂); MET DP280080 哪吒 leaf (unpainted) | correct | none (real 孩儿发 has side hair and tufts, not a fringe: optional) |
| 16 | 时迁 -> **孙悟空** | see section 2 | | | |
| 17 | 刘瑾 | 《法门寺》, 净; 红太监脸, 舍利珠 on the forehead, white lower lip | BO 15-008 https://www.beijingopera.org/masks/15-008-liu-jin/ ("下嘴唇夸张的白色，是表现刘瑾骄横、傲慢"; 太监脸: 枣核/柳叶眉, 菱角嘴, 舍利珠 = 宫刑, "太监脸多以红脸为主"); xikao 《法门寺》 cast; chinawriter https://www.chinawriter.com.cn/n1/2025/0423/c442005-40466462.html | minor -> fixed (thin eyeliner eyes; bright ringed disc) | **Fixed** (take c): flat maroon 舍利珠, broad flat black eye blocks, dark red nose patch, 菱角 mouth with white lower lip. Meaning: red is satire / "假忠义", not loyalty (郝寿臣's "脑满肠肥" reading is *(snippet)* only) |
| 18 | 周仓 | 花元宝脸, pale 淡青 forehead | BO 07-063, 07-088, 07-090 (花元宝脸; red 印堂 column, maroon cheeks); CCTV ("《卧牛山》、《单刀会》中的周仓勾淡青色脑门"); ifeng https://inews.ifeng.com/50929006/news.shtml (forehead colour varies by play) | minor -> fixed (teal forehead, no red 印堂, pure black cheeks) | **Fixed** (take d): grey-blue ingot forehead with red centre stripe, maroon cheek fields |
| 19 | 二郎神 杨戬 | 金三块瓦, vertical third eye; gold = gods | BO 10-030 《闹天宫》 ("三块瓦脸，金为主色。脑门儿勾眼形"); CCTV (杨戬 gold in 《安天会》); NCFTA ("楊戩畫有三眼"); MET DP280075 | correct | none (play is 《闹天宫》/《安天会》; 《宝莲灯》 not verified) |
| 20 | 金钱豹 | gold 神怪脸, leopard head on the forehead, coins on the cheeks | BO 10-083 ("神怪脸，金为主色…脑门儿上的眉、眼、鼻、口清晰，两颊勾金钱"); ZHWP 臉譜 ("脸膛贴金，脑门上勾豹头形花纹"); CCTV (《红梅山》 gold) | minor -> fixed (naturalistic leopard picture; rows of small coins) | **Fixed** (take c): stylised leopard head worked into the forehead paint, one large coin per cheek, no script |
| 21 | 钟馗 | 花元宝脸, red forehead, bat (蝠 = 福) | BO 09-103..107 (09-106: "恨福来迟"; 09-107: red forehead because he died striking his head); jibi.net 16375445 (bat on the 印堂, 蝠 = 福) | correct (bat colour varies: blue / pale yellow / gold) | none |
| 22 | 夏侯惇 | 蓝三块瓦, mark under his LEFT eye (lost to an arrow) | BO 07-049 《长坂坡》 ("蓝三块瓦脸。左眼下有失目标记"), 07-009; NCFTA ("夏侯惇眼眶受過箭傷，故畫上紅點表示") | minor -> fixed: a dripping blood streak; the convention is a red dot | **Fixed** (take d, not mirrored): small red dot ringed in white under his left eye (viewer's right) |
| 23 | 木吒 (silver, disputed) -> **时迁** | "silver = gods" via 木吒 | CCTV only ("《攻潼关》中的木咤勾银色脸"; sohu 331395892 copies it verbatim); **contrary**: BO 10-044 《闹天宫》 木吒 = "揉脸，灰为主色". Colour code: NCFTA (银 = 神仙, 妖怪), chinaculture (gold and silver = gods / monsters), CCTV (金银 for 神怪) | **not supported** as a face: one source, contradicted by another; no full silver face with two sources was found (银角大王 has silver only in the horn marks; 巨灵神, 龙王, 李靖 are not silver) | **Dropped.** "Silver" removed from our colour claims; gold (二郎神, 金钱豹, the monkey's gold eyes) stays. Cell 23 now holds 时迁 |
| 23 | 时迁 (flagged) | 武丑; patch | CNPOC 丑 page (武丑 patch 更窄小, 枣核 e.g. 杨香武); douban 27222354 (时迁 《巧连环》, 王长林 style: "勾筝形大尖粉脸，寓意身轻如燕，甚合鼓上蚤绰号"); wenxuecity (时迁 武丑, 《雁翎甲》); BO 13-056 image (large pointed white patch over both eyes with a serrated lower edge, black inner lines); MET DP280157 朱光祖 (武丑 patch over both eyes, black inner lines) | **wrong** in v3a: a plain thin stripe on the nose, no line work | **Fixed** (take d, ref = CC0 Met 朱光祖 crop): kite-shaped 筝形 white patch rising onto the forehead, spanning both eyes, serrated lower edge, lozenge on the nose, black inner lines. No flea/bat emblem (none attested) |

**Count (the 23 v3a faces):** correct 10 (包拯, 典韦, 程咬金, 窦尔敦, 高登, 关羽, 郑恩, 娃娃生, 二郎神, 钟馗); minor 10
(张飞, 曹操, 徐延昭 hue, 黄盖, 姜维, 鲁智深, 刘瑾, 周仓, 金钱豹, 夏侯惇; all fixed except 鲁智深); wrong 3 (汤勤's red
dots, 时迁's patch, 木吒's unsupported silver). All four word-faces now verified: 关羽 correct as was; 曹操, 汤勤 fixed; 娃娃生 correct.

Meanings that needed correcting in the old log: 姜维's taiji is "足智多谋" (BO), the Zhuge-Liang-disciple gloss is
snippet-only; 郑恩's play is 《斩黄袍》/《打龙棚》 not 《送京娘》; 二郎神's play is 《闹天宫》/《安天会》; 夏侯惇's is
《长坂坡》; silver is no longer claimed. Blue: CNPOC 刚强 / 桀骜不驯; NCFTA adds 陰險 (a shade of "scheming").

## 2. 孙悟空 (the monkey face) on the leaf

**Pattern (verified):** 象形脸 (BO 10-001/002/014/029/061: "孙悟空的脸谱就是在猴子面部特征上加以美化而形成的", after
郑法祥, 杨小楼, 李万春, 李少春, 小盛春). CNPOC 孙悟空 page: red encloses eyes, nose and mouth, "周围勾白，耳鬓涂黄", like an
inverted peach. jibi.net https://www.jibi.net/News/jpsx/9_14_12_669.html : 李万春's "倒栽桃" (北派; 杨小楼 "一口钟", 李少春
"反葫芦"), gold eye rings = 火眼金睛. NCFTA: pink sockets before 《安天会》, gold after he eats the peaches and elixir;
forehead 觔斗云 before enlightenment, 卍/佛 after, so the **script-free form is the cloud-curl forehead**. The CC0 Qing
court album leaf (OGP 1-12, `refs/lianpu_v3/ogp_1-12_sunwukong.jpg`) shows the red heart frame, gold eyes and white
surround with black hair strokes, and was passed to the model as the second reference (the crop has no text).
Painted (take d): red inverted peach, gold-filled eye lobes ringed white, black monkey nose and beaked mouth, white
ground with black fur strokes, pale yellow at the temples, a black cloud curl on the forehead, no writing. It matches the
stage monkey's own face (CANON / `monkey_v3_model_sheet`: peach-shaped cinnabar field, gold eyes, white face).

**Cell 16 (row 3, col 5), replacing 时迁; 时迁 moves to cell 23, replacing 木吒.** Why:
- Not a word-face (10, 3, 13, 14) and not the bare cell 15.
- It is the cell **right beside the bare cell where the child stands**. H4 opens on the bare cell (CAM0 spans leaf
  x 1266-2504, so the left part of cell 16's face is in frame from the first frame of H4) and the pull-out reveals the
  monkey's face next to her before anything else; in H3 the kid framing ends at x 2322, exactly on the rule, so the
  monkey does not compete with "kid". In H2 cell 16 is the first face of the fast four-face roll (158.255), framed at
  0.70 zoom, so it is seen landing.
- The two weak faces were 时迁 (wrong patch; the second clown, redundant with 汤勤) and 木吒 (unsupported silver). Rather
  than lose the 武丑, 时迁 was repainted correctly and moved to the corner cell 23, and the face that goes is 木吒.
- The leaf's colour code keeps every attested colour; what it loses is only the unsupported silver.

## 3. Disputed between sources (left as is, noted)
- 程咬金 green (all modern 京剧 sources) vs blue (Qing Met leaf; one zhidao question): older/regional variant.
- 徐延昭: one snippet says the face was once black (梆子 uses a black 六分脸); purple is the 京剧 standard.
- 黄盖 brow-head dots: BO has them; 钱金福's version reportedly not *(snippet)*.
- 包拯 crescent orientation varies by school and is reportedly a late-Qing addition *(snippet)*.
- 关羽: one cheek mole (NCFTA) vs 七星痣 (ZHWP).
- 鲁智深 brows: 螳螂眉 (BO 袁世海, jibi 11_19) vs 孔雀眉 (two jibi pages).
- 汤勤: 方巾丑 (bjd) vs 官衣丑 *(snippet)*; lozenge eyes are snippet-only (kept, they are generic 丑 drawing).
- 时迁: 枣核 (generic 武丑) vs 筝形 (王长林's 时迁). Painted the 筝形 kite.
- 周仓 forehead varies by play (淡青 in 单刀会 per CCTV, purple per ifeng); kept 淡青.
- 钟馗 bat colour (blue / pale yellow / gold).
- 夏侯惇: BO 07-009 says the eye mark is only drawn after 《长坂坡》; inconsistent, not followed.
- Silver: only CCTV names a silver face (木咤 in 《攻潼关》); BO's 木吒 is grey. Dropped.
- 孙悟空: which master "owns" 倒栽桃 (李万春 per jibi, 郑法祥 per another page *(snippet)*).

## 4. Files changed
- `design/plates/F_lianpu/v3/faces_v3.json`: new prompts for the 12 regenerated faces + `MONKEY` (old prompts in the
  `_cand/<ID>_a.txt` / `_b.txt` files). `TANGQIN` no longer uses the 旗牌 ref; `SHIQIAN` uses the CC0 朱光祖 crop;
  `MONKEY` uses the CC0 OGP crop.
- `design/plates/F_lianpu/v3/picks.json`: 12 new picks, `MONKEY: d`, `MUZHA` removed.
- `design/plates/F_lianpu/v3/normalise.py`: mirror only `XIAHOUDUN` take a; flood fill seeds on the first bare-paper
  corner (two takes had a speck in the top-left corner and normalised to the whole sheet).
- `design/plates/F_lianpu/F_faces_v3.json` rewritten (23 faces incl. MONKEY, without MUZHA; MUZHA.png stays on disk, unused).
- `design/plates/F_lianpu/v3/faces/_v3a/`: the previous normalised faces. All candidates kept in `_cand/`.
- `shots/faces_lib.py` `ALBUM`: 16 = MONKEY, 23 = SHIQIAN. H1-H4 scripts unchanged (cells 16 and 23 are H2 landings).

## 5. Renders

Backups of the v3a comps: `media/comp/_v3a/H1..H4.mp4`. Re-rendered with `work/faces_v3/render.sh H1..H4` (times from
`docs/shots.json`), frames 158 / 152 / 80 / 79 at 960x540, 24 fps. Sheets `work/review/comp_v3/H1..H4.jpg`, looked at:
- H1: the ten close faces read cleanly; 曹操 now has the pink 印堂 and no mole (f20), 刘瑾's flat eye blocks and white
  lip (f86), 夏侯惇's ringed red dot under his left eye (f99), 金钱豹's stylised forehead leopard and single coins (f72).
- H2: 孙悟空 lands in the fast roll beside 刘瑾 (f57); on the full leaf (f70-f151) the monkey's red peach and gold eyes are
  the most distinct face in row 3, beside the bare cell; the shadow-puppet switch (f95) still reads.
- H3: Tool = 关羽, threat = 曹操 (new), trick = 汤勤 (new square block, no red), kid = the unpainted child: each word has
  one face; the monkey only enters at the right edge during the widen after "kid" (f79).
- H4: the monkey face is at the right edge from f0 and fully beside the child by f23, then the whole leaf.
Not verified: 1920x1080 render; playback in motion (judged from sheets).

## DONE 17:20

**Verification (23 v3a faces, two or more sources each):** 10 correct (包拯, 典韦, 程咬金, 窦尔敦, 高登, 关羽, 郑恩,
娃娃生, 二郎神, 钟馗); 10 minor deviations (张飞, 曹操, 徐延昭, 黄盖, 姜维, 鲁智深, 刘瑾, 周仓, 金钱豹, 夏侯惇); 3 wrong
(汤勤's red cheek dots, 时迁's thin plain stripe, 木吒's silver: one source only and contradicted). All flagged faces
resolved: 徐延昭 verified (紫六分脸, 《大保国》; hue repainted from lilac to opera maroon-purple); 高登 verified (油白三块瓦);
鲁智深's brows verified as 螳螂眉 (袁世海) / 孔雀眉 (other versions); 时迁 repainted with the 筝形 kite patch; silver dropped.
Word-faces: 关羽 correct; 曹操 repainted (unattested mole removed, 印堂 added); 汤勤 repainted (square 豆腐块, no red);
the child's unpainted face correct.
**Repainted (11):** 张飞, 曹操, 徐延昭, 黄盖, 姜维, 刘瑾, 周仓, 金钱豹, 夏侯惇, 汤勤, 时迁. 鲁智深 left (missing 戒疤 dots
are below the leaf's resolution).
**孙悟空:** 倒栽桃 猴脸 (red inverted peach, gold eyes, white fur-stroked ground, cloud curl, no writing), CC0 Qing court
album leaf as pattern ref; in **cell 16**, beside the bare cell 15 where the child stands. It replaces 时迁 there; 时迁
(repainted) moves to cell 23, replacing 木吒. Net: the face that leaves the leaf is the unsupported silver 木吒.
**Disputed between sources:** section 3 (程咬金 green vs blue; 关羽 one mole vs 七星痣; 鲁智深 brows; 汤勤 方巾丑 vs 官衣丑;
时迁 枣核 vs 筝形; 周仓 forehead colour by play; silver).
**Spend:** $4.85 of $15. Nothing committed. Temp files in `work/tmp/fv/` removed; the old prompts and picks are kept as
`design/plates/F_lianpu/v3/_cand/faces_v3_v3a_prompts.json` and `picks_v3a.json`.
