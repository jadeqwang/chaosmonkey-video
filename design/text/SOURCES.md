# Text sources and proofreading notes (accessed 2026-11-16)

## qianziwen.txt / qianziwen_simplified.txt
- 250 lines x 4 chars = 1000 characters, all distinct (verified by script). One phrase per line, no punctuation.
- Base text: zh.wikipedia.org 千字文, section 文本 (wikitext via action=raw) - modern traditional forms.
- Cross-check: zh.wikisource.org 千字文 (wikitext). Same 250 phrases, 1000 chars; 41 phrases differ only in variant glyph choice
  (e.g. 玄黃/玄黄, 菓珎/果珍, 盖/蓋, 迩/邇, 随/隨, 崐崗/崑岡, 羣/群, 籍/藉, 絃/弦, 讌/宴, 遼/僚, 羲/曦, 脩/修, 飡/餐, 粮/糧, 䟽/疏). The Wikisource page marks further attested variants inline (律召/律呂, 周發殷湯/周發商湯, 鳴鳳在樹/竹, 飽飫烹宰/享宰, 背邙/背芒, 璇璣/璿璣, etc.); Wikipedia's note also gives 天地玄黃 / 天地元黃 and 律召 / 律呂.
- Well-known issue: the text is said to use no repeated character, which holds only because variants are counted as different characters (雲/云, 崑/昆, 巨/鉅, 發/髮, 並/并, 絜/潔, 慼/戚). Collapsing to simplified produces 6 duplicates: 云 昆 巨 发 并 戚 (see `qianziwen_simplified.txt`; 1000 chars, 994 distinct).
- ctext.org was NOT used: its pages forbid automated retrieval (it returns an anti-scraping notice). A human should eyeball lines against ctext or a printed edition before the final cut.
- Simplified = OpenCC t2s (opencc-python-reimplemented); all 250 lines remain 4 chars.

## categories.txt
- Verbatim from zh.wikisource.org 西遊記/第001回, 第002回, 第003回, 第058回, 第098回 (wikitext, extracted by script, no retyping). The Wikisource text uses 臝 in ch.3 and 蠃 in ch.58; simplified rendering normalises both to 裸.
- Corrections to the brief: the quoted 魂字一千三百五十號 passage is in ch.3 (confirmed); the ten-category list 天地神人鬼 / 蠃鱗毛羽昆 is spoken in ch.58, while ch.3 lists 臝蟲 毛蟲 羽蟲 昆蟲 鱗介. 打破頑空須悟空 is at the end of ch.1 (the naming), not ch.2. 一竅通時百竅通 is narration in ch.2 (also 我如今一竅通，百竅通 later in ch.2); it is not part of a verse couplet.
- Second-source check was limited: journeytothewestresearch.com quotes the ch.3 line 另有個簿子，悟空親自檢閱，直到那「魂」字一千三百五十號上，方注著孫悟空名字 identically (it mislabels it as ch.1). shicimingju.com and ctext.org were blocked to scripts. Different editions vary (臝/裸/倮, 簾/帘); recheck against a printed edition before carving.

## shigu.txt
- zh.wikisource.org 石鼓文/第一鼓 (車工·吾車篇), 改變表記 section. Opening couplet parallels Shijing 車攻 (我車既攻，我馬既同). Lines with rare graphs are flagged, 吾馬既寶 (vs 阜) is uncertain; this is a style sample only.
