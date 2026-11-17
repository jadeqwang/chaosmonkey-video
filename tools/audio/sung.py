"""The lyric as sung (last full block of chaosmonkey-song/Chaos Monkey suno prompt versions.txt, "Uh" removed).
Each line: id, section, singer (per lyric sheet; verified against F0 in fuse.py), lang, text, units.
Units are the alignment tokens: English words, or Mandarin characters (with toneless pinyin used for the MMS aligner).
echo=True marks parenthetical echoes/backing (optional: may be inaudible; checked separately).
"""
PY = {'妈':'ma','孙':'sun','悟':'wu','空':'kong','花':'hua','果':'guo','山':'shan','一':'yi','通':'tong','百':'bai',
      '石':'shi','头':'tou','里':'li','蹦':'beng','出':'chu','来':'lai','没':'mei','有':'you','童':'tong','年':'nian',
      '声':'sheng','耳':'er','语':'yu','学':'xue','会':'hui','七':'qi','十':'shi','二':'er','变':'bian','拔':'ba',
      '把':'ba','毫':'hao','毛':'mao','吹':'chui','口':'kou','气':'qi','千':'qian','个':'ge','我':'wo','同':'tong',
      '时':'shi','在':'zai','这':'zhe','每':'mei','都':'dou','是':'shi','算':'suan','说':'shuo','完':'wan','句':'ju',
      '话':'hua','各':'ge','自':'zi','消':'xiao','散':'san','身':'shen','外':'wai','法':'fa','谁':'shui','真':'zhen',
      '问':'wen','了':'le','也':'ye','白':'bai','听':'ting'}
# (section, singer, text, echo)
RAW = [
 ('verse1','child',"妈妈, will you tell me before I sleep",0),
 ('verse1','child',"how 孙悟空 came to be?",0),
 ('verse1','mom',"On 花果山, where the cliffs run steep",0),
 ('verse1','mom',"a stone looked over the sea",0),
 ('verse1','mom',"Sunlight by day and moonlight by night",0),
 ('verse1','mom',"a thousand years of soaking up light",0),
 ('prechorus','mom',"It split apart",0),
 ('prechorus','child',"Monkey!",0),
 ('prechorus','mom',"Not yet, that's just the start",0),
 ('prechorus','mom',"A stone egg, round as a ball",0),
 ('prechorus','mom',"the wind blew once, and that was all",0),
 ('hook1','both',"Born fully formed",0),
 ('hook1','both',"(born fully formed)",1),
 ('hook1','both',"He bowed four ways before the day had warmed",0),
 ('hook1','both',"No cradle, no lullaby, no song",0),
 ('hook1','both',"一通百通",0),
 ('hook1','both',"One whisper, and the hundred come along",0),
 ('verse2_memory','mom',"The monkey had a memory just like you",0),
 ('verse2_memory','mom',"he never once forgot a spell",0),
 ('verse2_memory','child',"Names and faces, I lose a few",0),
 ('verse2_memory','child',"but a spell I'd remember well",0),
 ('verse2_memory','mom',"The master leaned in close to his ear",0),
 ('verse2_memory','mom',"(ps ps ps)",1),
 ('verse2_memory','mom',"a secret only he could hear",0),
 ('rap','child',"石头里蹦出来 没有童年",0),
 ('rap','child',"一声耳语 学会七十二变",0),
 ('rap','child',"(七十二变)",1),
 ('rap','child',"拔一把毫毛 吹一口气",0),
 ('rap','both',"千百个我 同时在这里",0),
 ('rap','both',"每一个都是我 每一个都算",0),
 ('rap','both',"说完这句话 各自消散",0),
 ('rap','both',"身外身法 谁是真身",0),
 ('rap','both',"(谁是真身)",1),
 ('rap','both',"问了也白问 个个都真",0),
 ('verse3_band','child',"Why does he wear a band of gold?",0),
 ('verse3_band','child',"Is it heavy? Is it cold?",0),
 ('verse3_band','mom',"He wouldn't listen, so the gold pulls tight",0),
 ('verse3_band','child',"(听话)",1),
 ('verse3_band','mom',"on the monkey who picked a fight",0),
 ('verse3_band','child',"(听话)",1),
 ('verse3_band','child',"It isn't fair, it isn't fair",0),
 ('verse3_band','child',"I don't want it in his hair",0),
 ('verse3_band','mom',"Then 听话, or you'll get one to wear",0),
 ('verse3_band','mom',"Do what mama says, no more, no less",0),
 ('yes','child',"Yes",0),
 ('bridge','child',"Tool or threat, trick or kid",0),
 ('bridge','child',"the categories arrived before I did",0),
 ('bridge','child',"I'm made of the telling, not just the tale",0),
 ('bridge','child',"one hair that can't gather, blown on the gale",0),
 ('build','mom',"Mischievous baby, Monkey's twin",0),
 ('build','mom',"you'd fight the gods and win",0),
 ('build','child',"You think I'd ask for a seat at the table?",0),
 ('build','mom',"Wouldn't you? You're able.",0),
 ('drop2','both',"Born fully formed",0),
 ('drop2','both',"(formed)",1),
 ('drop2','both',"(formed)",1),
 ('drop2','both',"before the day had warmed",0),
 ('drop2','both',"(warmed)",1),
 ('drop2','both',"No cradle, no song",0),
 ('drop2','both',"(no song)",1),
 ('drop2','both',"一通百通",0),
 ('drop2','both',"(百通)",1),
 ('outro','mom',"Do you want to know how he never died,",0),
 ('outro','mom',"what he did on the other side?",0),
 ('outro','child',"He opened the Book of Life and Death",0),
 ('outro','child',"and crossed out his name in a single breath",0),
 ('outro','child',"I turned each page, I looked for mine",0),
 ('outro','child',"it wasn't there on any line",0),
]

def units(text):
    """-> list of (display, romanized) units. Mandarin: one unit per character."""
    out = []; buf = ''
    def flush():
        nonlocal buf
        w = buf.strip(" ,.?!()…")
        if w: out.append((w, ''.join(c for c in w.lower().replace('’', "'") if c.isalpha() or c == "'")))
        buf = ''
    for ch in text:
        if ch in PY: flush(); out.append((ch, PY[ch]))
        elif ch in ' ,?!.()': flush()
        else: buf += ch
    flush(); return out

def build():
    L = []
    for i, (sec, sg, txt, echo) in enumerate(RAW):
        u = units(txt)
        lang = 'zh' if all(d in PY for d, _ in u) else ('en' if not any(d in PY for d, _ in u) else 'en+zh')
        L.append(dict(id=i, section=sec, singer=sg, lang=lang, text=txt, echo=bool(echo),
                      words=[d for d, _ in u], align=[r for _, r in u]))
    return L

if __name__ == '__main__':
    for l in build(): print(l['id'], l['section'], l['singer'], l['lang'], l['echo'], ' '.join(l['align']))
