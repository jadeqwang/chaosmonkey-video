# Fonts for the cliff inscriptions, tablet, ledger, storybook and lyrics

Researched and measured 2026-11-16. Coverage measured with fontTools `getBestCmap()` (`python3 -I`), against
`design/text/qianziwen.txt` (1000 distinct traditional chars), `qianziwen_simplified.txt` (994 distinct), and small test sets.
Downloaded fonts were never executed; each lives in its own folder here with `LICENCE-NOTES.txt` (+ `OFL.txt` where shipped).
NOTE: `refs/fonts` is about 218 MB; consider git-ignoring the .ttf/.otf files (licence notes and proofs are the part worth committing).

## Recommendation

| Role | Font | Licence | Coverage |
|---|---|---|---|
| Cliff seal script (小篆) | **Chong Xi Small Seal 崇羲篆體** (Academia Sinica) `chongxi-seal/崇羲篆体.otf` | CC BY-ND 3.0 TW or later: commercial use OK, **credit required, no modification** | 千字文 993/1000 traditional (7 missing); tablet 10/10; ten categories 11/12 (only variant 臝 missing; 裸 蠃 present); 悟空 一通百通 all present |
| Tablet / ledger kai | **LXGW WenKai 霞鹜文楷** `lxgw-wenkai/` (soft, Klee-derived) — or **館閣楷 GuanGe Kai** `guangekai/` for a heavier carved/MS feel | SIL OFL 1.1 both | 1000/1000 trad, 994/994 simp (GuanGe 993/994) |
| Storybook print face | **匯文明朝體 Huiwen Mincho** `huiwen-mincho/` (distressed woodblock-print Ming) ; plain fallback Noto Serif SC (OFL) | Public Domain per font metadata (see caveat) | 1000/1000 trad, 992/994 simp |
| Latin / English colophon | **EB Garamond** (also Cormorant Garamond and IM Fell English, both already house style) | SIL OFL 1.1 | Latin |
| Bold woodcut poster | Free option found: **刻石錄 顏體 I.Ngaan** (heavy carved kai, GPL) ; or ZCOOL XiaoWei (OFL, simplified-oriented, 662/1000 trad) | see table | see table |

Caveats: no verified free bronze (金文) / Stone-Drum (石鼓文) / clerical (隸書) font exists in the places searched (see Rejected).
The only practical seal font is Chong Xi, so the whole cliff is small seal. Stone Drum sample text is in `design/text/shigu.txt`
and can be used with a hand-drawn/AI-painted pass, not typeset.

### Missing-character strategy for 千字文 in Chong Xi
Missing: 曜 璇 誚 邈 颻 飫 鵾 (lines 238, 239, 248, 161, 194, 203, 195). **Lines 1-160 (640 chars, 天地玄黃 ... 鉅野洞庭) are fully covered**: carve those.
If later lines are wanted: use attested in-font variants 曜->耀 (耀 present), 璇->璿 (present), 鵾->鶤 (present), 颻->搖 (present, 飄搖);
omit or hand-draw 邈 (曠遠綿邈), 飫 (飽飫烹宰), 誚 (愚蒙等誚) - or skip those three lines. Chong Xi has 既 (U+65E2) but not 旣 (U+65E3); use 既.
Seal fonts are keyed on TRADITIONAL codepoints (simplified coverage only 696/994): always typeset from `qianziwen.txt`, never the simplified file.
For ch.3 text use 裸 or 蠃 (臝 absent).

### Licence obligations / credits text
- Chong Xi: credits line: "Seal script: 崇羲篆體 Chong Xi Small Seal, © Academia Sinica 2022, CC BY-ND 3.0 TW (https://xiaoxue.iis.sinica.edu.tw/chongxi/)". Do not subset, convert, or edit the font file (ND). Rendering to pixels/vector outlines of text is ordinary use of the font; do not ship the font file or outline-edited glyph sets as a "font".
- LXGW WenKai / GuanGe Kai / EB Garamond / Noto Serif SC / ZCOOL / IM Fell: OFL 1.1 - no attribution required in output; keep OFL.txt if the font file is redistributed; do not sell the font alone.
- Huiwen Mincho: metadata says Public Domain; I could not read the author's page (HTTP 403), so keep a credit "汇文明朝体" as courtesy and re-check before any commercial release.
- I.Ming (刻石錄明體): IPA Font License v1.0 (accept licence; renamed if modified). I.Ngaan / I.PenCrane: GPL v2+, fine for rendering images; do not redistribute the font files except under GPL.
- TW-Kai 全字庫正楷體: Open Government Data License v1.0: credit "國家發展委員會 / National Development Council".

## Candidate table (downloaded and measured)

Coverage = covered/total for trad 千字文 | simp 千字文 | tablet 花果山福地水簾洞天(10 distinct) | categories 12 chars (天地神人鬼裸蠃臝鱗毛羽昆).

| Font | Style | Licence + URL | File | trad | simp | tablet | cats | Verdict |
|---|---|---|---|---|---|---|---|---|
| Chong Xi Small Seal 崇羲篆體 | small seal 小篆 (Shuowen-based) | CC BY-ND 3.0 TW+, https://xiaoxue.iis.sinica.edu.tw/chongxi/copyright.htm, https://creativecommons.org/licenses/by-nd/3.0/tw/ | `chongxi-seal/崇羲篆体.otf` | 993/1000 | 696/994 | 10/10 | 11/12 | **PRIMARY seal** |
| LiuShu WenMai Xiaozhuan v0.8 | small seal | OFL 1.1 (README) https://github.com/jianyue2026/liushuwenmai-xiaozhuan | `liushu-wenmai/LiuShuWenMaiXiaozhuan-v0.8.ttf` | 54/1000 | 53/994 | 2/10 | 2/12 | too few glyphs; comparison only |
| LXGW WenKai 霞鹜文楷 | kai, soft | OFL 1.1 https://github.com/lxgw/LxgwWenKai | `lxgw-wenkai/霞鹜文楷-Regular.ttf` | 1000 | 994 | 10 | 12 | **kai pick** (already house style: LXGW WenKai TC Bold in holdfire) |
| 館閣楷 GuanGe Kai 1.7.3 | kai, carved MS | OFL 1.1 (font), MIT (scripts) https://github.com/wainshine/guangeti | `guangekai/館閣楷-Regular.ttf` | 1000 | 993 | 10 | 12 | good alt, heavier/rougher |
| TW-Kai 全字庫正楷體 | kai, MOE-style | Open Government Data License v1.0 https://data.gov.tw/en/license | `qzqz/全字庫正楷體-98_1.ttf` | 1000 | 993 | 10 | 12 | OK; plain, 50 MB, huge charset |
| 刻石錄明體 (= I.Ming) | Ming, carved-stone feel | IPA Font License v1.0 http://ipafont.ipa.go.jp/ipa_font_license_v1.html | `keshilu/刻石录明體.ttf` | 1000 | 991 | 10 | 12 | usable print alt |
| 刻石錄顏體 (= I.Ngaan) | heavy 顏-style kai, bold | GPL v2+ http://www.gnu.org/licenses/gpl.txt | `keshilu/刻石录顏體.ttf` | 999 (鵾) | 713 | 10 | 12 | woodcut-poster/bold display option |
| 刻石錄鋼筆鶴體 (= I.PenCrane-B) | pen-crane | GPL v2+ | `keshilu/刻石录鋼筆鶴體.ttf` | 999 (鵾) | 715 | 10 | 12 | not needed |
| 匯文明朝體 Huiwen Mincho | woodblock-print Ming (rough edges) | Public Domain (font metadata); see caveat | `huiwen-mincho/匯文明朝體.otf` | 1000 | 992 | 10 | 12 | **print pick** |
| Noto Serif SC | Song/Ming | OFL 1.1 https://github.com/google/fonts/tree/main/ofl/notoserifsc | `noto-serif-sc/NotoSerifSC[wght].ttf` | 1000 | 994 | 10 | 12 | clean fallback print face |
| ZCOOL XiaoWei 站酷小薇 | display serif (simplified-oriented) | OFL 1.1 | `zcool-xiaowei/ZCOOLXiaoWei-Regular.ttf` | 662/1000 | 984/994 | 9 (no 簾) | 10 | simplified only; lyrics display option |
| EB Garamond (+Italic) | Latin Garamond | OFL 1.1 | `eb-garamond/` | - | - | - | - | **Latin pick** |
| IM Fell English | Latin, old press | OFL 1.1 | `im-fell/` (also in holdfire) | | | | | house style |
| Libre Caslon Text | Latin | OFL 1.1 | `libre-caslon/` | | | | | alt |
| Cormorant Garamond | Latin | OFL 1.1 (in holdfire `render/assets/fonts/`) | not copied | | | | | house style (poems); alt |
| Spectral | Latin | OFL 1.1 (Google Fonts; not downloaded) | - | | | | | candidate only |

Chong Xi 千字文 missing chars: 曜 璇 誚 邈 颻 飫 鵾. LiuShu missing: 946 of 1000 (not worth listing).

## Rejected / not usable (no file kept)

| Font | Reason |
|---|---|
| 方正甲骨文 FZJiaGuWen (oracle bone) | "个人非商业" per free-font index (https://www.foundertype.com/index.php/FontInfo/index/id/5528). Deleted. |
| 阿里妈妈刀隶体 Alimama DaoLiTi (clerical, carved) | Licence unverified: official wording found says free for Alibaba merchants; could not confirm general commercial use (https://www.alibabafonts.com). Deleted. Would be the best clerical/woodcut match if the licence is confirmed. |
| 青柳隸書 Aoyagi Reisho SIMO | Terms are in a usage .txt inside the archive; unverified. Deleted. |
| 临海隶书 | No licence stated. Deleted. |
| 京華老宋体 KingHwa OldSong | No licence in font; author page not fetchable (403). Deleted. |
| ShuowenSeal-* (xiaoshihou514), Seal Sans (Ghimist) | Seal-block (Plane 3) fonts; former derived from Unicode chart glyphs "for research only", latter AGPL-3.0; not downloaded. |
| 北师大说文小篆, 華瑞小篆體, 方正小篆, 汉仪篆书, Seal Hanzi | proprietary / unclear (per zh.wikipedia user page 已知的小篆字体). |
| 開元小篆 Kaiyuan Small Seal | OFL, but README says "not yet released" (https://github.com/frankslin/kaiyuan-small-seal-font). Watch it. |
| 霞鹜篆书 LXGW Seal | OFL but only ~75 glyphs. |
| 全字庫說文解字 (6,721 chars) | Government open licence, but could not locate a direct download. Possible second seal font for the 3 missing chars (邈 飫 誚); not verified. |
| 峄山碑篆体 (3,754 chars) | Maoken "author declaration" terms; not located/downloaded. |
| 方正 free fonts (FZ KaiTi etc.), 字魂, 汉仪 | need authorisation / commercial. |
| 金文 / 大篆 / 石鼓文 / free 隸書 | None found with a clear free licence (GitHub, free-font indexes, Wikipedia list). Searched 王漢宗/cwTeX/AR PL names only by index; no seal/bronze faces among them. |

## Proof sheets (`refs/fonts/_proofs/`)

- `chongxi_qzw80.png` (2123 x 888) / `liushu_qzw80.png`: first 80 chars, 20 right-to-left columns of one 4-char phrase each; top = white-on-black rubbing, bottom = cinnabar-filled red on grey stone. LiuShu shows boxed placeholders (not covered).
- `chongxi_categories.png` / `liushu_categories.png`: 天地神人鬼 (right column) and 裸鱗毛羽昆 (left column), large.
- `kai_tablet_compare.png`: 花果山福地，水簾洞洞天 as vertical lines, right to left: LXGW WenKai, GuanGe Kai, TW-Kai, I.Ming, I.Ngaan, Huiwen Mincho, Noto Serif SC, ZCOOL XiaoWei (ZCOOL lacks 簾).
- `seal_compare_8chars.png`: 天地玄黃日月盈昃 / 一通百通 / 悟空 in both seal candidates.

Sanity checks (Chong Xi): no tested glyph is mapped to `.notdef` or has an outline identical to `.notdef`; none is empty; no two characters share an outline;
median bitmap IoU against LXGW regular-script glyphs is 0.20 (max 0.35), i.e. none is a regular-script fallback; proof sheets visually confirm genuine seal forms
(e.g. 天, 日, 月, 空, 悟).

## Already installed / house style

- System: `fc-list :lang=zh` shows only Droid Sans Fallback (DroidSansFallbackFull.ttf). Nothing else; use the files here.
- holdfire (`/home/jade/Documents/1-music-shipped/holdfire/render/assets/fonts/`): Cormorant Garamond (VF + italic; poems/human voice), IM Fell English (Nrm/It, lyric "ink" scenes), Ma Shan Zheng subsets (brush Latin/CJK), LXGW WenKai TC Bold (subset), Noto Sans SC Black (subset), Instrument Serif, Anton, Archivo, Big Shoulders Display, Michroma, Open Sans, IBM Plex Mono, JetBrains Mono, VT323, Reenie Beanie, Bodoni Moda, Noto Sans Cuneiform. Docs: `docs/take1/STYLE_BIBLE.md`, `docs/take2/LYRICS.md`, `docs/RENDERER.md`.
- To stay consistent: English lyrics in Cormorant Garamond (+ italic) or IM Fell English; Chinese brush/kai from Ma Shan Zheng or LXGW WenKai - the latter is the kai pick here.
