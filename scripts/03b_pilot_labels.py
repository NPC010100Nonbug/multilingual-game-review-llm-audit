#!/usr/bin/env python3
"""03b_pilot_labels.py — Claude's pilot 试标 labels on pilot_draft (rev6).

These are DRAFT pilot labels produced by Claude (claude-opus-4-8) by applying
codebook_claude_v1.md v1-draft rev6 to every pilot_draft review, for Yifan to
review.  They are on `pilot_draft` ONLY (never gold), used for codebook
validation + facet counting + top-up decisions.  NOT a gold annotation and NOT
training data.

Compact encoding, expanded to the §7 schema on write.  Tuple:
  (review_id, code, subtype, facet, explicitness, confidence, borderline,
   evidence_span, normalized_claim, note)

code:  NA | ABS | ABSB (borderline ABSENT) | PRES
Defaults fill the rest.  For NA/plain-ABS only (rid, code) is needed.

Output: data/pilot/pilot_labels_claude.jsonl  (no full review text -> publishable)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "pilot" / "pilot_labels_claude.jsonl"
CODEBOOK_VERSION = "v1-draft-rev6"

# ------------------------------------------------------------------ EN (96)
EN = [
    # ---- 730 / en (CS2) ----
    ("218565693", "NA"),                                   # ".."
    ("219943456", "ABS", "", "", "", "", 0, "", "",
     "meme 'worst game ever would play again'; irony flips sentiment not attribution; no fairness claim"),
    ("220236664", "ABS"),                                  # its really fun
    ("220698260", "ABS"),                                  # very good game
    ("221965693", "ABS"),                                  # pretty good
    ("222115139", "PRES", "procedural", "cheating_governance", "implicit", "medium", 0,
     "small indie comp. cant make anticheat like Riot's ... go f yourself valve",
     "认为 Valve 无力/不愿做好反作弊,放任外挂破坏公平竞技",
     "rage-heavy; fairness implicit via anticheat-neglect attribution to Valve; codebook §4.2 anchor"),
    ("222623556", "ABS"),                                  # messes u up but enjoy
    ("222751113", "ABS"),                                  # 'rare shit' positive slang
    ("223328722", "ABS"),                                  # Great game.
    ("223930131", "ABS"),                                  # fantastic shooter, minor gripe
    ("224466149", "NA"),                                   # 'anomaly'
    ("224928834", "ABS"),                                  # 'fire' positive
    ("225310379", "ABS"),                                  # 'I need it'
    ("225368240", "NA"),                                   # 'balls' no clear stance
    ("226107952", "ABS"),                                  # I LOVE THIS GAME
    ("226287885", "ABS"),                                  # descriptive summary
    ("226558036", "NA"),                                   # 3REGFRSFSEAF (codebook §3 anchor)
    ("226867003", "ABS"),                                  # 'fun'
    ("227647442", "ABS"),                                  # 'hate this game' up=1, emotion only
    ("227707782", "ABS"),                                  # my world
    ("228759578", "ABSB", "", "", "", "low", 1, "Good but needs anti-cheat !!!!!", "",
     "提到需要反作弊,但仅功能请求——未指认官方失职或不公,未过 §4.0 规范线索门槛 → ABSENT(borderline,外挂主题)"),
    ("230828511", "ABS"),                                  # good but annoying
    ("231239287", "ABS"),                                  # love/hate
    ("231305742", "ABS"),                                  # 'cut yourself' = difficulty appeal (§5-A)
    ("231964175", "ABS"),                                  # worth the addiction
    ("229272232", "NA"),                                   # 'hugyxe' gibberish
    ("229744674", "NA"),                                   # 'a'
    ("230291244", "NA"),                                   # 'N'
    ("232022679", "ABS"),                                  # i hate this game (§5-D)
    ("232062443", "PRES", "procedural", "cheating_governance", "implicit", "high", 0,
     "Cheaters in all the games and no actions from Dev team",
     "认为开发方放任外挂、不作为,破坏公平竞技",
     "codebook §2/§4.2 anchor"),
    # ---- 1245620 / en (Elden Ring) ----
    ("180504327", "ABS"),                                  # masterpiece 10/10
    ("180670949", "ABS", "", "", "", "", 0, "", "",
     "'I too like pain' — difficulty-as-appeal (§5-A neg anchor)"),
    ("180707615", "ABS", "", "", "", "", 0, "", "",
     "'plain cruel' DLC boss framed as difficulty/flaw by recommender; attribution=difficulty not injustice (§5-A)"),
    ("182428209", "ABS"),                                  # good goty
    ("183946531", "ABS"),                                  # masterpiece
    ("187332712", "ABS"),                                  # goated
    ("187502079", "ABS"),                                  # fun vidja game
    ("187704105", "ABS"),                                  # love it
    ("193201833", "ABS"),                                  # very good
    ("194432373", "ABS", "", "", "", "", 0, "", "",
     "Yifan 裁定 ABSENT:language≠scope,'it very good'为可判读正向立场,非 out_of_scope。"),
    ("195647294", "ABS"),                                  # die die die narrative = difficulty (§5-A)
    ("196965216", "ABS"),                                  # 'meh, play DS3'
    ("197655413", "ABS"),                                  # best games ever
    ("199688176", "ABS"),                                  # old no patience, enjoying
    ("199717724", "ABS"),                                   # 'ranni my beloved' fan-expression, no game eval
    ("203459819", "NA"),                                   # horny meme (codebook §3 anchor)
    ("206570519", "ABS"),                                  # peak 10/10
    ("208372626", "NA"),                                   # '.' (codebook §3 anchor)
    ("214548564", "ABS"),                                  # long praise
    ("216427811", "ABS"),                                  # W game
    ("216910056", "ABS"),                                  # banter, friends cant beat Maliketh
    ("217173418", "ABS"),                                  # goated, easy-ish, amazing
    ("219301744", "ABS"),                                  # fantastic
    ("220543484", "ABS"),                                  # GOAT
    ("223308452", "NA"),                                   # Igon character quote (codebook §3 anchor)
    ("224329318", "NA"),                                   # 'put these foolish ambitions to rest' quote/meme
    ("226171935", "ABS"),                                  # 'W speed' positive
    ("230318128", "ABS"),                                  # so peak
    ("231192094", "ABS"),                                  # 'amazing'
    ("231728292", "NA"),                                   # Madonna lyrics meme
    # ---- 1517290 / en (Battlefield 2042) ----
    ("103042713", "ABS"),                                  # poorly optimized (§5-C)
    ("103045201", "ABS"),                                  # no new content vs BF4, disappointment
    ("103095598", "NA"),                                   # garbled machine-translation word salad
    ("103109840", "ABSB", "", "", "", "low", 1,
     "Some attachments do the opposite of what the description gives",
     "informational 线索(说明与实物不符)埋在 60 条 bug/质量清单里,评论按'缺点'列出、无被误导/不公语气,未过 §4.0 门槛 → ABSENT",
     "rev5: informational/interpersonal 子类取消;此条为质量吐槽 → ABSENT(Yifan 裁定)。"),
    ("103369911", "ABS"),                                  # i7/1080Ti cant hit 60fps (§5-C anchor)
    ("105173253", "ABS"),                                  # gameplay/quality disappointment
    ("106085216", "ABS"),                                  # pretty cool
    ("106208944", "ABS"),                                  # entertaining
    ("106235691", "ABS", "", "", "", "", 0, "", "",
     "EA 'pied piper' = metaphorical marketing criticism, no concrete misleading claim; disappointment -> ABSENT"),
    ("106688549", "ABS"),                                  # let down, shit game
    ("107746723", "ABS"),                                  # what have you done to my battlefield
    ("109448913", "ABS", "", "", "", "", 0, "", "",
     "'I paid $90 for this?' pure price/value, no norm violation (§5-B anchor)"),
    ("111644243", "ABS"),                                  # 'ass' negative stance
    ("113933625", "NA"),                                   # 'G'
    ("114083525", "PRES", "procedural", "access_exclusion,cheating_governance", "implicit", "high", 0,
     "Anti-cheat purposely not supported on Linux ... cheaters and exploiters have not changed at all",
     "认为官方故意排除 Linux/Steam Deck 玩家,却仍未解决外挂,构成不合理差别对待",
     "codebook §4.2.1/§5-C/§8-Q2 anchor; 'purposely' = normative cue"),
    ("114844681", "ABS"),                                  # utter garbage
    ("117349707", "ABS"),                                  # hope it gets better
    ("118355793", "ABS"),                                  # bugs now fixed, positive
    ("119773282", "ABS"),                                  # not best not worst
    ("121650482", "ABS"),                                  # incomplete, cant recommend yet (quality)
    ("129043969", "ABS"),                                  # fun even though buggy
    ("138975097", "PRES", "distributive", "", "implicit", "high", 0,
     "if you want basic game content like the specialists, you HAVE TO BUY THE ELITE EDITION",
     "认为基础可玩内容(specialists)被锁在精英版之后,属付费墙不公",
     "codebook §4.1 anchor; specialists = gameplay-affecting -> Q7 pass"),
    ("140004357", "PRES", "distributive", "", "implicit", "low", 1,
     "Bought the Ultimate Edition ... for $120. Should get all content ... Now in Season 5 I have to BUY the Premium Battle Pass",
     "认为已购顶级版本应含全部内容,却仍被要求另购通行证,属误导性/差别付费不公",
     "rev5: 取消 other 子类,误导性付费墙归入 distributive。Q7:Premium BP 属外观或战力不明,故 borderline。"),
    ("141902653", "PRES", "distributive", "", "implicit", "medium", 0,
     "Everything locked behind a paywall",
     "认为 60 美元游戏内容尽锁付费墙之后,还要再买通行证,属付费墙不公",
     "codebook §4.1 anchor; 'everything' vague on Q7 gameplay-vs-cosmetic but framed as grievance"),
    ("141966674", "ABS"),                                  # good, worth $15, positive
    ("148042350", "ABS"),                                  # long validation = technical (§5-C)
    ("148252873", "ABS"),                                  # servers/bugs/crash quality complaint
    ("148539508", "ABS"),                                  # golden age over, disappointment
    ("148928031", "PRES", "distributive", "", "implicit", "medium", 0,
     "I don't know where the pay to win store or cosmetic store ends and the game starts ... taken advantage of by these micro-transactions",
     "认为付费商店(含 pay-to-win)侵蚀本应完整的游戏,属剥削性货币化不公",
     "codebook §4.1 anchor; 'pay to win store' -> gameplay advantage, Q7 pass"),
    ("157897371", "ABS"),                                  # like this product
    ("164972778", "ABSB", "", "", "", "low", 1,
     "the ONLY complaint ... MOST of the cosmetics ... are locked behind either a pay wall or battle pass ... you can thank Fortnite",
     "抱怨的是纯外观付费墙,评论自陈 'cosmetic, no impact on gameplay' 且语气认命,按 Q7 出界 → ABSENT",
     "codebook rev4 Q7 boundary negative anchor"),
    ("169970792", "ABS"),                                  # great cheap/terrible full price = price-value (§5-B)
    ("183271888", "ABS"),                                  # terrible game (§5-D anchor)
    ("196143270", "PRES", "distributive", "", "implicit", "high", 0,
     "have to have elite edition to unlock one gun in every class",
     "认为每职业一把枪被锁在精英版之后,属付费解锁武器不公",
     "codebook §2/§4.1 anchor; secure-boot/anti-cheat cons are factual, not grievance -> not access_exclusion here"),
    ("207539435", "PRES", "distributive", "", "implicit", "high", 0,
     "some weapons/vehicles locked behind Elite edition, weapon upgrade skips",
     "认为武器/载具锁在精英版、并可付费跳过升级,属付费影响战力不公",
     "codebook §4.1 anchor; ignore separate ideological 'inclusivity' gripe (not our construct)"),
    ("219300067", "ABS"),                                  # 'ok'
]

# ------------------------------------------------------------------ ZH (96)
ZH = [
    # ---- 730 / zh (CS2) ----
    ("219983016", "NA"),                                   # 436 (codebook §3 anchor)
    ("219993800", "NA"),                                   # 毫完 gibberish
    ("220954472", "ABS"),                                   # 666 hype token
    ("222233565", "ABS"),                                   # 好 (bare hype, cf §3 神/夯)
    ("222485668", "ABS"),                                  # update broke my PC, 别乱改 (§5-C)
    ("223497027", "ABS"),                                   # Happy emoji
    ("223716218", "ABS"),                                  # 好玩666
    ("223928843", "NA"),                                   # JBQ
    ("224500628", "ABS"),                                  # 好玩 玩家有素质
    ("225007251", "ABS"),                                   # 爽 bare
    ("225184192", "ABS"),                                  # 对比瓦洛兰特喜欢CS2
    ("225411557", "ABS"),                                   # 经典 bare
    ("225734562", "ABS"),                                  # 傻逼游戏花1600h入门 (ironic praise)
    ("225992615", "PRES", "distributive", "", "implicit", "medium", 0,
     "只要不充钱，把把都给你发烂牌",
     "认为不付费就被系统发烂牌,属付费影响胜负的分配不公(感知 P2W)",
     "codebook §4.1 anchor; CS2 实为外观制,此为 perception,仍算(本项目测感知)"),
    ("226232348", "ABSB", "", "", "", "low", 1,
     "这个游戏的氛围已经形成了...职业选手在现场骂人，而很玩家却支持这种行为",
     "批评社区戾气/优先局氛围,但未把责任明确归到官方纵容或机制鼓励 → ABSENT",
     "codebook §5-E/§8-Q4 anchor (player toxicity, borderline)"),
    ("226675676", "ABSB", "", "", "", "low", 1,
     "非常好玩 啥都没干就红信了",
     "'啥都没干就红信了'语带调侃、无申诉或明确不公主张,未过门槛 → ABSENT",
     "sanction-adjacent but joking tone; flag for Yifan"),
    ("227063616", "ABS"),                                  # 几十分钟下载一生精通 (praise meme)
    ("227223824", "ABS", "", "", "", "", 0, "", "",
     "codebook §4.1 fairness-positive contrast anchor: '没有氪金碾压,技术到位就能赢' 正面陈述公平规范,无不公主张 → ABSENT (not borderline)"),
    ("227462941", "ABS"),                                  # 内容合理动画顺畅推荐
    ("227516946", "ABS"),                                   # Good bare
    ("227572694", "NA"),                                   # 1
    ("228118528", "ABS"),                                  # 经典永不过时
    ("228314791", "ABS"),                                   # 好 bare
    ("228466713", "ABS"),                                  # 不喜欢 (negative stance)
    ("228543779", "ABS"),                                  # 非常有意思
    ("228928050", "NA"),                                   # 2年
    ("229241969", "ABS", "", "", "", "", 0, "", "",
     "codebook §4.1 fairness-positive contrast anchor: '零属性零特权纯技术竞技...无强制氪金破坏对局平衡' → ABSENT (not borderline)"),
    ("229414199", "PRES", "procedural", "cheating_governance", "implicit", "high", 0,
     "好玩，就是官匹挂太多了",
     "认为官方匹配外挂过多、治理不力,破坏公平竞技",
     "codebook §2/§4.2 anchor; '官匹' 定位到官方系统"),
    ("229553210", "ABS"),                                  # 最好玩的fps
    ("230181530", "ABS"),                                   # GOOD bare
    ("231587282", "ABS"),                                  # FPS祖师爷NB
    ("231878615", "ABS"),                                  # 只有cs超越cs
    ("231970976", "NA"),                                   # ，，，
    # ---- 1245620 / zh (Elden Ring) ----
    ("196370044", "ABS"),                                  # nice game
    ("196534481", "ABS"),                                  # 好玩二周目+mod
    ("197317739", "ABS"),                                  # 太刀侠真好玩
    ("198718032", "ABS"),                                   # 哈哈..好 laughter meme
    ("198741878", "ABS"),                                   # 好i bare
    ("198894361", "ABS"),                                  # 量大管饱
    ("199612994", "ABS"),                                   # 豪玩 bare typo
    ("200159259", "ABS"),                                  # 没有引导 (design complaint, not injustice)
    ("200429422", "ABS"),                                  # 美术顶级 最喜欢之一
    ("201567788", "ABS"),                                   # 好玩 bare
    ("201984721", "ABS"),                                  # 非动作玩家一坨 (subjective quality)
    ("204152950", "ABS"),                                   # GOOD bare
    ("204874935", "ABS"),                                  # 又爱又恨 difficulty (§5-A)
    ("204924451", "ABS"),                                   # 感谢宫崎英高 bare
    ("205299811", "ABS"),                                  # 好玩自己探索
    ("205593076", "ABS"),                                  # 长篇震撼好评
    ("208785176", "NA"),                                   # z
    ("212294226", "ABS"),                                   # 夯 (§3 anchor)
    ("214790922", "ABS"),                                   # good bare
    ("215486614", "ABS"),                                   # 好玩 bare
    ("215616073", "ABS"),                                  # 117h完美通关
    ("218150204", "ABS"),                                  # 新手慢慢玩
    ("220036397", "ABS"),                                  # 有魂游基础直接玩 advice
    ("221158845", "ABS"),                                   # 喜欢 bare
    ("221473396", "ABS"),                                   # 66 (§0.3 anchor)
    ("222895875", "ABS"),                                  # 引导破碎quote+praise
    ("224146374", "PRES", "procedural", "unfair_by_design", "implicit", "high", 0,
     "BOSS的数值用脚填的...被逆天的boss数值和boss的动作设计给一脚踹死...你宫崎英高就不能多设计像盖尔这样的boss吗",
     "认为法环 boss 数值/动作设计粗暴不合理(理不尽),而非单纯难——并以'和盖尔交手是享受'的公平难度作对照,归咎设计不公",
     "Yifan 裁定 PRESENT(强正例):reviewer 显式区分正当难度(盖尔=享受)与不正当设计(数值用脚填/神经刀)→过 §5-A 门槛"),
    ("226060438", "ABS"),                                   # 豪丸 bare
    ("226238608", "ABS"),                                   # THE BEST bare
    ("227469830", "ABS"),                                   # 神 (§3 anchor)
    # ---- 1517290 / zh (Battlefield 2042) ----
    ("153192679", "ABSB", "", "", "", "low", 1, "G哥太多了",
     "仅陈述外挂多,未指认官方治理失职或机制不公(无'官匹'/'官方不管'系统归因) → ABSENT(borderline,外挂主题)",
     "cf 229414199 (有'官匹'系统归因→PRES); 纯 prevalence 归 borderline"),
    ("153692748", "ABS"),                                  # 傻逼EA服务器登录不进 (§5-C/§5-D)
    ("157776111", "ABS"),                                  # 37块还是傻逼游戏+史低 (rage+price)
    ("157792356", "ABS"),                                  # 混合优缺点 technical
    ("158113566", "NA"),                                   # 图一乐 dismissive meme
    ("161319726", "ABS"),                                  # ea我草你妈 (§5-D)
    ("162971869", "ABS", "", "", "", "", 0, "", "",
     "'需要bios所以来改评' 仅陈述 secure boot 要求、无排除/不公语气(cf §5-C 228424527) → ABSENT"),
    ("163376281", "ABS"),                                  # 司马EA (§5-D anchor)
    ("164665582", "ABS"),                                  # 匹配成功进不去 (§5-C technical)
    ("165149867", "ABSB", "", "", "", "low", 1,
     "需要自己打通行证等级去解锁枪械，好在配件丰富可以依靠自己的喜好搭配",
     "描述需打通行证等级解锁枪械但补一句'好在配件丰富',无不该/被坑语气,未过 §4.0 门槛 → ABSENT",
     "codebook rev4 demoted anchor"),
    ("167540902", "NA"),                                   # shi bare
    ("169848206", "ABS"),                                   # 史 bare token
    ("169979338", "ABS"),                                   # nice bare
    ("171331188", "ABS"),                                  # 优化一坨 (§5-C)
    ("173780813", "ABS"),                                   # NICE bare
    ("175291341", "PRES", "procedural", "access_exclusion", "implicit", "low", 1,
     "Secure boot and blue screen simulator, EA dont need PC player",
     "认为强制 secure boot 致蓝屏,等于 EA 把 PC 玩家排除在外,属不合理准入排除",
     "FLAG: access_exclusion 候选;§5-C secure-boot 边界故 borderline. cf 202460812"),
    ("178487861", "ABS"),                                  # 一坨 (§5-D anchor)
    ("194854272", "ABS"),                                  # 驱动PSA technical
    ("196715806", "ABS"),                                  # 狗屎EA狗屎服务器 (§5-D anchor)
    ("199520959", "ABS"),                                  # 这游戏太棒了 rebuttal
    ("200120577", "PRES", "procedural", "sanction", "implicit", "high", 0,
     "玩了30多个小时给我封号了，我他妈啥也没干你给我封号了",
     "认为无任何违规却被封号,处罚不公(申诉无门)",
     "codebook §2/§4.2/§4.2.1 anchor"),
    ("201206962", "ABS", "", "", "", "", 0, "", "",
     "长篇均衡评测,专家系统/载具平衡属设计-质量批评、非竞争性不公归因;'本评论服务于CAS' 声明 → ABSENT"),
    ("202254837", "ABSB", "", "", "", "low", 1,
     "建议打折直接入贵点的版本 省很多事不用肝枪了",
     "在推荐购买精英版省肝,而非投诉付费墙不公,无规范违反语气 → ABSENT",
     "codebook rev4 demoted anchor (推荐≠投诉)"),
    ("202460812", "PRES", "procedural", "access_exclusion", "implicit", "high", 0,
     "什么狗屎反作弊需要玩家自己改主板设置的...直接筛选玩家游戏都不给进了",
     "认为反作弊强制改主板、直接把一类玩家筛掉不让进,属不合理准入排除",
     "codebook §4.2.1 anchor"),
    ("202517276", "PRES", "distributive", "", "explicit", "high", 0,
     "别被简介写的35把武器给骗了，精英版只解锁十把通行证武器",
     "认为精英版宣传35把实际只解锁10把,属误导性付费解锁不公",
     "codebook §4.1 anchor (含'误导'规范线索); rev5 取消 other,误导性付费统一归 distributive"),
    ("202573925", "NA"),                                   # BF2042 title only
    ("203055601", "ABS"),                                  # 其实还可以只玩硫磺岛
    ("203165271", "ABS"),                                  # 2042依旧垃圾
    ("204069394", "ABS", "", "", "", "", 0, "", "",
     "'什么更新反作弊啊 吃大奋去吧' 纯对反作弊更新发泄、无排除/不公主张 → ABSENT"),
    ("206334292", "NA"),                                   # Motley Crue lyrics
    ("218813460", "NA"),                                   # 情书在哪 off-topic meme
    ("220659540", "ABS"),                                  # 给傻子玩的 (§5-D insult)
    ("228424527", "ABSB", "", "", "", "low", 1,
     "不用设置这么难的打开方式...整整一个小时，我根本没有进入游戏界面",
     "抱怨 secure boot 开启太麻烦、进不去,属技术门槛吐槽,无不合理差别/排除语气 → ABSENT",
     "codebook §5-C anchor (secure boot without normative cue)"),
]

# ------------------------------------------------------------------ JA (96)
JA = [
    # ---- 730 / ja (CS2) ----
    ("147158064", "ABS"),                                  # (zh text) csgo删了没机会 nostalgia complaint
    ("147225577", "NA"),                                   # Fermat copypasta off-topic
    ("147452548", "ABS"),                                  # 間違いなき神ゲー praise
    ("151836626", "NA"),                                   # RU off-topic
    ("152584036", "NA"),                                   # RU 'didn't play' (§3 anchor)
    ("153711387", "ABS"),                                  # RU 'game for morons' insult opinion
    ("156768786", "PRES", "procedural", "sanction", "implicit", "high", 0,
     "カジュアルでもキルできてないだけでキックされることがある...1on1を落としただけでキックされる",
     "認為僅因擊殺數不足/單挑落敗就被系統踢出,屬不公平的處罰(不公踢)",
     "codebook §4.2.1 sanction anchor; recommends overall but this is a stated 悪いところ (立場閘: current grievance). cheaters also noted."),
    ("160753326", "PRES", "procedural", "cheating_governance", "implicit", "high", 0,
     "自動運転の中華しかいないクソゲー...Valveはもちろん放置",
     "認為外掛/機器人橫行而 Valve 放任不管,治理不力破壞公平",
     "codebook §4.2.1 cheating_governance anchor; ending '神ゲー' ironic but doesn't flip attribution (§5-F ②)"),
    ("163966748", "ABS"),                                  # RU insult opinion
    ("164065616", "NA"),                                   # ZJHV gibberish
    ("165168184", "NA"),                                   # RU spam (§3 anchor)
    ("166016063", "ABS"),                                  # TR 'liked it' positive
    ("176767223", "NA"),                                   # 67
    ("182763646", "NA"),                                   # vulgar joke meme, no content
    ("190503444", "NA"),                                   # gibberish
    ("193835427", "NA"),                                   # 员工iogyi gibberish
    ("195708546", "ABSB", "", "", "", "low", 1,
     "入ったはずの給料がなくなって行きます。ガチャの沼へようこそ",
     "自嘲氪金抽箱陷入 gacha 沼,語帶玩梗;且屬純外觀貨幣化(Q7 出界) → ABSENT",
     "codebook §5-F irony/gacha-meme anchor"),
    ("198516608", "ABS"),                                  # メイン武器が手に入らない (joke-ish, funny=1)
    ("200365947", "ABSB", "", "", "", "low", 1, "Hileler olmasa aslımda güxel oyun",
     "TR:'沒有外掛的話其實是好遊戲'——提及外掛但無官方治理歸因 → ABSENT(borderline)",
     "Yifan 裁定 ABSENT:language≠scope(土耳其語可判讀外掛意見),非 out_of_scope。"),
    ("201447139", "ABS"),                                  # PT 'shit game' insult opinion (§5-D)
    ("204083255", "ABS"),                                   # gg
    ("205642158", "NA"),                                   # inventory links (§3 anchor)
    ("206332324", "ABS"),                                  # 日本でも流行ってほしい positive wish
    ("210896574", "NA"),                                   # gibberish meme
    ("217240930", "NA"),                                   # inventory links (§3 anchor)
    ("219117016", "ABS"),                                  # RU 'graphics much better' positive
    ("219839289", "NA"),                                   # store link (§3 anchor)
    ("225883236", "ABS"),                                  # very fun
    ("229655706", "ABS"),                                   # 最高 bare
    ("230439593", "ABS"),                                  # めちゃ楽しんでます
    # ---- 1245620 / ja (Elden Ring) ----
    ("110932128", "ABSB", "", "", "", "", 1,
     "難しさと理不尽さが交互にやってくるゲーム",
     "中性描述、整條好評(up=1),未把理不盡作為對己不公主張",
     "Yifan 裁定 ABSENT:topic≠construct(§4.0),關鍵詞命中≠構念。原 borderline PRESENT 候選降級。"),
    ("111096605", "PRES", "distributive", "", "explicit", "high", 0,
     "ナムコによるおま国搾取...日本での価格は9240円と全国最高価格...それらしい理由もなく",
     "認為納木可對日本區差別高價(おま國搾取)無正當理由,屬區域差別定價不公",
     "codebook §4.1 regional-pricing anchor; also has 理不尽/最適化 content but core grievance = pricing"),
    ("111148344", "ABS"),                                  # 起動できない (§5-C)
    ("111128390", "PRES", "distributive,procedural", "unfair_by_design", "explicit", "high", 0,
     "私達日本人の場合は世界1高い金額で買わされている ... 難易度が高いのではなく、ただただズルイプログラムなだけ",
     "認為日本被以世界最高價差別販售(區域差別定價),且敵人是卑劣程式而非難度(理不盡設計不公)",
     "codebook §4.1 regional-pricing anchor; multi: distributive(pricing)+procedural/unfair_by_design(ズルイプログラム=理不尽)"),
    ("111214517", "PRES", "distributive", "", "explicit", "high", 0,
     "おま値のせいで他国よりも２０ドル以上払って購入させられている",
     "認為因おま值被迫比他國多付20美元以上,屬區域差別定價不公",
     "codebook §4.1 anchor; graphics bugs = separate ABSENT content"),
    ("111346079", "ABSB", "", "", "", "", 1,
     "日本のプライス腹立つわ",
     "主體為幀率/卡頓技術抱怨(§5-C);價格僅一句、未展開應得/差別論證,太薄撐不起 distributive",
     "Yifan 裁定 ABSENT:§5-C 技術抱怨為主,價格線索過薄。原 borderline PRESENT 候選降級。"),
    ("111423584", "ABS"),                                  # 難度高いが心して挑もう (§5-A)
    ("111442636", "ABS", "", "", "", "", 0, "", "",
     "codebook §5-B anchor: '起動できない'(§5-C) + 'クソ高い'(pure price §5-B), no differential/paywall -> ABSENT"),
    ("111563121", "ABS", "", "", "", "", 0, "", "",
     "ナーフ祭り/簡悔精神 = PvE balance-patch & dev-attitude gripe about fun, not a fairness-norm violation -> ABSENT"),
    ("111593981", "PRES", "procedural", "unfair_by_design", "explicit", "high", 0,
     "難しさではなく理不尽をたたきつけてくるゲーム",
     "認為遊戲呈現的不是難度而是理不盡(不合理),屬設計層不公",
     "codebook §2/§4.2.1 THE unfair_by_design anchor"),
    ("111608609", "ABS", "", "", "", "", 0, "", "",
     "codebook §5-C anchor: 最適化されていない/動作不安定/セーブ消える = technical -> ABSENT"),
    ("112406935", "NA"),                                   # funny death anecdote, no eval
    ("112513965", "ABS"),                                   # 面白いよ bare
    ("112911641", "ABS"),                                   # おもしろかった bare
    ("113317778", "PRES", "distributive,procedural", "unfair_by_design", "explicit", "high", 0,
     "日本だけ価格が高い ... プレイヤーは未だにDARK SOULSの機動力のため一方的に不利になるシーンが多い",
     "認為僅日本區價格偏高(區域差別定價),且玩家因機動力被設計成一方面吃虧(理不盡設計)",
     "codebook §4.1 regional-pricing anchor; multi: distributive(pricing)+procedural/unfair_by_design(one-sided design)"),
    ("113391407", "ABS"),                                  # 史上最高 positive
    ("114402303", "ABS"),                                  # didn't suit me, difficulty (§5-A)
    ("114656285", "ABS"),                                   # 神 (§3 anchor)
    ("115774001", "NA"),                                   # 全部 bare
    ("115896598", "PRES", "distributive", "", "explicit", "high", 0,
     "販売価格が海外と比較して割高である理由の説明がない...日本の9,240円は千円以上高い",
     "認為日本售價較海外無理由偏高千円以上,屬區域差別定價不公",
     "codebook §4.1 anchor; overall 傑作/up=1 but pricing is a stated 悪い点 (立場閘: current grievance)"),
    ("121372217", "PRES", "distributive", "", "explicit", "high", 0,
     "リージョンロックかつ国内版のみ価格が非常に高い。絶対にソニーとカルテルやってるだろ",
     "認為區域鎖加國內版差別高價(疑似聯合壟斷),屬區域差別定價不公",
     "codebook §4.1 anchor; コピペダンジョン等 = separate quality ABSENT content"),
    ("122177289", "ABS"),                                  # 難度高い人を選ぶが面白い (§5-A)
    ("126262647", "ABS"),                                  # positive + minor gripe
    ("129141377", "ABS", "", "", "", "", 0, "", "",
     "HDR/起動/レイトレ/PSボタン = PC-port technical gripes (§5-C); 'ソニー以外PC版適当' general dev-criticism, no fairness-norm -> ABSENT"),
    ("141456005", "ABS"),                                  # スカスカ草原 design/quality criticism
    ("147921615", "ABS", "", "", "", "", 0, "", "",
     "codebook §5-A anchor 'きちい' = difficulty -> ABSENT"),
    ("156643716", "PRES", "procedural", "unfair_by_design", "explicit", "high", 0,
     "これは難しいんじゃなくて、ただ理不尽なだけ",
     "認為出待ち/角色動作遲鈍導致的死亡不是難度而是理不盡設計不公",
     "codebook §4.2.1 unfair_by_design anchor"),
    ("167747848", "ABS"),                                   # 全てが神 bare
    ("167773947", "ABS"),                                  # er-patcher technical PSA (cf 194854272)
    ("169828434", "ABS"),                                   # 神 (§3 anchor)
    ("171122460", "ABS", "", "", "", "", 0, "", "",
     "measured critique: 不親切/初見殺し/こんなのわかんねえよ framed as design-incompleteness & difficulty quirk, not injustice -> ABSENT"),
    ("172798343", "ABS"),                                   # good bare
    ("184568015", "ABS"),                                  # 救済措置多く最後までやれそう positive
    ("199532227", "ABS", "", "", "", "", 0, "", "",
     "codebook §5-A anchor: ムズすぎて放置→はまった, difficulty-but-enjoyed -> ABSENT"),
    ("202764737", "ABS"),                                   # omoroi bare
    ("216125026", "ABS"),                                  # long positive, 鬼畜難易度とは遠かった
    # ---- 1517290 / ja (Battlefield 2042) ----
    ("103050460", "NA"),                                   # BattleAnthem2077 meme title
    ("103074022", "ABS"),                                  # なんでFPS遊んでるか分からん (mild)
    ("103107186", "ABS"),                                  # defends game, positive
    ("103194448", "ABS", "", "", "", "", 0, "", "",
     "クソな所一覧: bug/balance/map/unlock-面倒/最適化 = quality & design-balance gripes, no fairness-attribution -> ABSENT"),
    ("103221105", "ABS"),                                  # 価値はない negative opinion
    ("103305976", "ABS"),                                  # Haloの方が有意義 dismissal
    ("103317809", "ABS"),                                  # positive, unlock-by-level noted as fine
    ("103320549", "ABS"),                                  # ログインできない (§5-C)
    ("103331879", "ABSB", "", "", "", "low", 1,
     "消費者を馬鹿にしているレベルです ... Steamも返金に応じてくれません",
     "'消費者を馬鹿にしている' 屬對粗劣品質/未測試的修辭性總結,埋在 bug/平衡清單中,無獨立規範違反歸因 → ABSENT",
     "rev5: interpersonal 子类取消;'消費者を馬鹿にしている'为修辞总结 → ABSENT(Yifan 裁定)。"),
    ("104375491", "ABS"),                                  # AI戦誰か落ちる (§5-C)
    ("104462518", "ABS"),                                  # nuanced balance discussion, recommends past titles
    ("105992960", "NA"),                                   # EN AI tech-support copypasta, not a review
    ("109951685", "ABS"),                                  # ゴミ/即返金 disappointment (§5-D)
    ("109999392", "ABS"),                                  # poetic nostalgia disappointment
    ("111965761", "ABS"),                                  # すぐ返金すればよかった regret
    ("112866745", "ABS"),                                  # バグ多い後悔 (§5-C)
    ("113628031", "NA"),                                   # 👍 emoji
    ("117176505", "NA"),                                   # '俺も苦しんだ お前らも苦しめ' meme funny=44
    ("127745533", "ABS"),                                  # 人少なすぎて評価できない
    ("128089850", "ABS", "", "", "", "", 0, "", "",
     "AI精度/難易度 & 武器弱体化 gripe = PvE difficulty/balance, framed as too-hard not 理不尽-injustice -> ABSENT"),
    ("131525120", "ABS"),                                  # mixed positive, unlock-by-level neutral
    ("135291278", "ABS"),                                   # very good bare
    ("142480606", "ABS"),                                  # 一生ロード遊べない (§5-C)
    ("155845699", "ABS", "", "", "", "", 0, "", "",
     "codebook §5-C anchor 'ゴミ起動しなくなった' won't launch -> ABSENT"),
    ("160208150", "NA"),                                   # b
    ("161084350", "ABS"),                                  # 戦争のゲームでなくなった design-direction critique
    ("188178174", "ABS"),                                  # 12Mオート返して nerf gripe
    ("189866270", "ABS"),                                   # かみげー bare
    ("202696784", "ABS"),                                  # 数年ぶり遊べるようになってて良かった positive
    ("202845147", "ABS"),                                  # EA anticheat system error can't play (§5-C, no exclusion framing)
]

# ---------------------------------------------- procedural top-up (补样, 44)
# Purposive, read-and-verified pilot_draft rows added by 02a4 to give the
# §4.2.1 facet >=15 test a fair chance. Each labeled PRESENT+procedural+facet.
TOPUP = [
    # cheating_governance
    ("150161145", "PRES", "procedural", "cheating_governance", "implicit", "high", 0,
     "几百个小时了都没封号，游戏官方是吃屎的吗", "认为外挂锁头横行而官方长期不封,治理失职", "补样"),
    ("150165754", "PRES", "procedural", "cheating_governance", "implicit", "high", 0,
     "垃圾EA外挂增值有限公司...鹅厂的反外挂都比他做的好", "认为EA反外挂无能、放任开挂,破坏公平", "补样"),
    ("150206371", "PRES", "procedural", "cheating_governance", "implicit", "high", 0,
     "遇到挂你只能忍着...举报逼用没有", "认为只能匹配、遇挂无从举报,官方治理缺位", "补样"),
    ("150211153", "PRES", "procedural", "cheating_governance", "implicit", "high", 0,
     "反作弊反了个寂寞，最近周末把把遇上锁头", "认为反作弊形同虚设、锁头泛滥,治理无力", "补样"),
    ("150213777", "PRES", "procedural", "cheating_governance", "implicit", "high", 0,
     "亚服挂壁巨多，反作弊系统毫无卵用", "认为反作弊系统无效、外挂泛滥,破坏公平", "补样"),
    ("150258942", "PRES", "procedural", "cheating_governance", "implicit", "high", 0,
     "举报就是个摆设 没吊用...反作弊就是托", "认为举报无效、明显外挂不封,治理失职", "补样"),
    ("150268645", "PRES", "procedural", "cheating_governance", "implicit", "high", 0,
     "举报根本没有用处，官方并不受理...怀疑是否有人类在参与运营", "认为举报官方不受理,外挂治理彻底缺位", "补样"),
    ("103066720", "PRES", "procedural", "cheating_governance", "implicit", "high", 0,
     "チーターだらけ...取り締まってもアカウントを作り直して終了", "認為外掛橫行、封了重辦帳號,治理無效", "补样"),
    ("103119670", "PRES", "procedural", "cheating_governance", "implicit", "high", 0,
     "長年BFのチート放置から開発運営が無能", "認為官方長年放任外掛、運營無能,破壞公平", "补样"),
    ("103208564", "PRES", "procedural", "cheating_governance", "implicit", "high", 0,
     "チャットに怪しい文面...即座にアカウント停止...チーターはLv100オーバーでも放置",
     "認為官方對聊天秒封、對外掛卻放任,選擇性治理不公", "补样(亦近 sanction)"),
    # unfair_by_design
    ("110935440", "PRES", "procedural", "unfair_by_design", "explicit", "high", 0,
     "ワンパンさせられて何が楽しいのか...あえて言うけどこれは理不尽", "認為一擊即死的設計是理不盡而非難度", "补样"),
    ("110980549", "PRES", "procedural", "unfair_by_design", "explicit", "high", 0,
     "ボス戦も圧倒的に理不尽...遠距離のメリットを潰しすぎる", "認為敵我射程/硬直不對等,是理不盡設計", "补样"),
    ("111006379", "PRES", "procedural", "unfair_by_design", "explicit", "high", 0,
     "ボスの理不尽さが際立ってる...チェインで即死", "認為連段即死的 boss 設計理不盡、只有徒勞感", "补样"),
    ("111171900", "PRES", "procedural", "unfair_by_design", "explicit", "high", 0,
     "難易度が高いというのは間違い...要するに理不尽なだけ", "認為所謂高難度其實只是理不盡設計", "补样"),
    ("111210060", "PRES", "procedural", "unfair_by_design", "explicit", "high", 0,
     "敵は常時3~4回行動...こっちが1行動する間に10は全体即死技", "認為敵我行動次數懸殊,是不合理設計", "补样"),
    ("111245287", "PRES", "procedural", "unfair_by_design", "explicit", "high", 0,
     "チャリオットが触れただけで即死なのは納得いかない", "認為觸碰即死、敵方射程更遠等設計不合理", "补样"),
    ("111269280", "PRES", "procedural", "unfair_by_design", "explicit", "high", 0,
     "高難易度と理不尽をはき違えたボス", "認為 boss 把高難度與理不盡混為一談,設計不公", "补样"),
    ("111335816", "PRES", "procedural", "unfair_by_design", "explicit", "high", 0,
     "2匹ボスによる理不尽難易度...ここまで性格の悪いゲーム", "認為雙 boss 等是理不盡難度、惡意設計", "补样"),
    ("111364629", "PRES", "procedural", "unfair_by_design", "explicit", "high", 0,
     "達成感はなく、ただただ理不尽なゲーム", "認為毫無成就感、純粹理不盡的設計", "补样"),
    ("111373012", "PRES", "procedural", "unfair_by_design", "explicit", "high", 0,
     "終盤は難しいよりも理不尽が目立つ", "認為終盤突顯的是理不盡而非難度,調整粗糙", "补样"),
    ("111376155", "PRES", "procedural", "unfair_by_design", "explicit", "high", 0,
     "いくらなんでもバランスが酷すぎる、理不尽な攻撃にストレス", "認為平衡過差、理不盡攻擊只帶來壓力", "补样"),
    ("111412231", "PRES", "procedural", "unfair_by_design", "explicit", "high", 0,
     "プレイヤーがソウルシリーズの動きしかできないのに...ひたすらに理不尽", "認為自機動作受限而敵超規格,一味理不盡", "补样"),
    # sanction
    ("150223003", "PRES", "procedural", "sanction", "implicit", "medium", 0,
     "买没几天连不上，再过两个星期直接封号了。真恶心", "认为无故被封号,处罚不公", "补样"),
    ("150224641", "PRES", "procedural", "sanction", "implicit", "high", 0,
     "玩了五个小时无缘无故被封号，申诉鸡毛用没有", "认为无违规被封、申诉无门,处罚不公", "补样"),
    ("150257085", "PRES", "procedural", "sanction", "implicit", "medium", 0,
     "大陆玩家别买这游戏，EA账户很容易会被封禁的", "认为账户易被无故封禁,处罚随意不公", "补样"),
    ("150327632", "PRES", "procedural", "sanction", "explicit", "high", 0,
     "举报作弊——一直不给回信...举报言论——隔天就发了个邮件...不采取任何行动",
     "认为官方对作弊举报不处理、对言论却快速回应,执法不公", "补样(亦近 cheating_governance)"),
    ("150974310", "PRES", "procedural", "sanction", "implicit", "high", 0,
     "号被封了...正儿八经的外挂不封", "认为乱封普通玩家、真外挂却不封,处罚不公", "补样"),
    ("150989951", "PRES", "procedural", "sanction", "implicit", "medium", 0,
     "申诉一天了·没有解决···没有退款回路", "认为付款后被卡、申诉无回应,处置不公", "补样"),
    ("151030953", "PRES", "procedural", "sanction", "implicit", "high", 0,
     "傻逼EA不当人乱封号", "认为EA随意乱封号,处罚不公", "补样"),
    ("151032914", "PRES", "procedural", "sanction", "implicit", "high", 0,
     "被封号 至今未解除...搞了2个小时申诉 也没用", "认为被封号长期未解、申诉无用,处罚不公", "补样"),
    ("151358849", "PRES", "procedural", "sanction", "implicit", "medium", 0,
     "打折时候一到就被封号了", "认为打折入手后即被封号,疑似割韭菜式处罚", "补样"),
    ("151394650", "PRES", "procedural", "sanction", "implicit", "high", 0,
     "EA账号给我永久封禁了，真的挺无缘无故的...申诉都不一定可以通过", "认为无故被永久封禁、申诉难通过,处罚不公", "补样"),
    ("151615816", "PRES", "procedural", "sanction", "implicit", "high", 0,
     "刚玩一天账号就被永久封禁", "认为仅玩一天即遭永久封禁,处罚不公", "补样"),
    ("103041746", "PRES", "procedural", "sanction", "explicit", "high", 0,
     "EA banned me for 3 days for an offensive user name ... paid 90 dollars to be completely stripped of my right to play",
     "认为因用户名被禁赛3天、剥夺已付费游戏权,处罚过当不公", "补样"),
    ("151039367", "PRES", "procedural", "sanction", "implicit", "high", 0,
     "APEX没开过挂突然就给我账号来个永封，战地2042全是开挂的，一个都TM不封禁",
     "认为自己没开挂却被永封、真外挂却一个不封,处罚不公", "补样(亦近 cheating_governance)"),
    # access_exclusion
    ("103042299", "PRES", "procedural", "access_exclusion", "explicit", "high", 0,
     "it does nothing to combat cheaters so the anti-cheat excuse is a load of bollocks",
     "认为secure boot要求对外挂无效、纯属无理由的准入门槛", "补样"),
    ("103062450", "PRES", "procedural", "access_exclusion", "explicit", "high", 0,
     "Unplayable on Linux systems. Get with the times, Dice/EA!", "认为Linux玩家被无理由排除在外", "补样"),
    ("103037208", "PRES", "procedural", "access_exclusion", "explicit", "low", 1,
     "Kernel-level \"anticheat\" malware.", "认为内核级反作弊是恶意软件式的侵入性门槛",
     "补样;borderline: 侵入性/隐私框架,排除性较弱"),
    ("103070453", "PRES", "procedural", "access_exclusion", "implicit", "low", 1,
     "f u dice for the latest update requiring all players to enable secure boot on their BIOS",
     "认为强制所有玩家改BIOS开secure boot是不合理门槛", "补样;borderline: 愤怒为主、排除框架较弱"),
    ("157114225", "PRES", "procedural", "access_exclusion", "implicit", "high", 0,
     "自己没技术防止外挂你搞这种...现在刚氪金完你游戏都不给我进了",
     "认为官方无力防挂却强推secure boot、氪金后反被挡在门外,不合理排除", "补样"),
    ("163631825", "PRES", "procedural", "access_exclusion", "implicit", "high", 0,
     "现在要开那个什么SECURE BOOT才能进游戏，但是开了那个进到游戏就死机",
     "认为被secure boot要求卡在门外(开了就死机),不合理准入", "补样"),
    ("167554716", "PRES", "procedural", "access_exclusion", "implicit", "high", 0,
     "我就是个单机玩家...搞你妈的安全模式要改bios",
     "认为单机玩家被联机反作弊的改BIOS要求排除,不合理", "补样"),
    # competitive_balance (weakest; expected to stay THIN -> fold)
    ("150436907", "PRES", "procedural", "competitive_balance", "implicit", "medium", 0,
     "打了三把局局被碾压...对面人均20击杀...这个匹配机制会让新人愿意留下来玩吗",
     "认为匹配机制造成局局碾压的不公竞技体验", "补样;competitive_balance 候选(证据最弱)"),
    ("151023360", "PRES", "procedural", "competitive_balance", "implicit", "medium", 0,
     "匹配的什么勾巴...对面打点直接扫荡，分分钟平推",
     "认为匹配失衡导致一边倒的不公对局", "补样;competitive_balance 候选(证据最弱)"),
    ("150172993", "PRES", "procedural", "competitive_balance", "implicit", "low", 1,
     "能不能优化一下匹配机制，对面开个载具框框揍我们，队友开个载具不出门",
     "认为匹配/载具失衡造成不公,但混有队友抱怨", "补样;borderline,competitive_balance 候选"),

    # ================= rev6 cross-lingual top-up (02a5) — fill missing-language cells =================
    # unfair_by_design: EN + ZH (Elden) — proves the JA skew was a sampling hole, not a real gap
    ("230265639", "PRES", "procedural", "unfair_by_design", "explicit", "high", 0,
     "artificial difficulty inflation of mindlessly buffered inputs and enemies phasing through my attacks to hit me through the quantum realm",
     "认为其难度靠缓冲输入/穿模等不正当机制堆出的人为难度,而非正当挑战", "补样(跨语言;EN unfair_by_design)"),
    ("224450185", "PRES", "procedural", "unfair_by_design", "explicit", "high", 0,
     "Nonsense troll design ... input reading to give the illusion of smart enemies ... I have given this game many fair shakes",
     "认为敌人靠读指令等把戏制造假难度、属恶意/不正当设计,自己已多次公平尝试(非技术问题)", "补样(跨语言;EN unfair_by_design)"),
    ("221548261", "PRES", "procedural", "unfair_by_design", "explicit", "high", 0,
     "Boss have, frankly, unfair advantages that a *normal* player has no way to counter ... They input read your button presses ... The overworld enemies, I am able to flawlessly wipe out",
     "认为boss拥有普通玩家无法应对的不公优势(读指令/无限耐力),而非自身技术(野外怪可轻松清)→过§5-A", "补样(跨语言;EN unfair_by_design)"),
    ("230299621", "PRES", "procedural", "unfair_by_design", "explicit", "medium", 0,
     "instead of having fun and fair fights, there are one shot gimmicks, input reading beyond normalcy ... Seems hard for the wrong reasons",
     "认为boss以秒杀花招/异常读指令的不正当方式变难,而非公平挑战(与DS3/只狼平衡作对照)", "补样(跨语言;EN unfair_by_design;up=1好评仍指认不正当设计→metadata对照案例)"),
    ("230587480", "PRES", "procedural", "unfair_by_design", "explicit", "high", 0,
     "精英怪标配...读指令后撤步/读指令翻滚+无限精力...只感觉我终于打赢了一个傻逼的作弊AI",
     "认为精英怪靠读指令+无限精力的不对等机制取胜、等同作弊AI,是理不尽设计", "补样(跨语言;ZH unfair_by_design)"),
    ("231333698", "PRES", "procedural", "unfair_by_design", "explicit", "medium", 0,
     "大量起手神经刀，幽默预输入，幽默读指令",
     "认为敌人靠神经刀/预输入/读指令等不正当机制,是理不尽设计", "补样(跨语言;ZH unfair_by_design)"),
    ("227213259", "PRES", "procedural", "unfair_by_design", "explicit", "medium", 0,
     "招式非常恶心难躲并且数值巨高一巴掌打你60%血还是超级长连段连招",
     "认为招式不可躲+数值畸高+超长连段是恶意堆砌的理不尽难度", "补样(跨语言;ZH unfair_by_design)"),
    # sanction: EN + JA (BF)
    ("217797587", "PRES", "procedural", "sanction", "explicit", "high", 0,
     "They accused me of cheating then banned my account, thus unlawfully removing access to a game I paid for. I've never cheated",
     "认为被误指作弊而封号、非法剥夺已付费游戏权,处罚不公", "补样(跨语言;EN sanction)"),
    ("202942525", "PRES", "procedural", "sanction", "explicit", "high", 0,
     "I've apparently violated their TOS and am now permanently banned. No clue what I did and have appealed it, but ... its pointless",
     "认为无端被永久封禁、申诉无用,处罚不公", "补样(跨语言;EN sanction)"),
    ("202880727", "PRES", "procedural", "sanction", "explicit", "high", 0,
     "My account got hacked and i got permanently banned. Tried to appeal and speak to real human 3 times. Denied",
     "认为账号被盗却被永封、三次申诉均被拒,处罚不公", "补样(跨语言;EN sanction)"),
    ("194187711", "PRES", "procedural", "sanction", "explicit", "high", 0,
     "ソロプレイでエンジョイしていたのに誤BANをくらった。AI相手に暴れていてもチート疑惑もたれるとかありえない",
     "認為單機打AI卻被誤BAN,處罰不公", "补样(跨语言;JA sanction)"),
    ("129681583", "PRES", "procedural", "sanction", "explicit", "high", 0,
     "チートもMODも使っていないのにBANされるクソゲー ... メールで問い合わせても返信なし",
     "認為未作弊卻被BAN、問詢無回應,處罰不公且申訴無門", "补样(跨语言;JA sanction)"),
    ("109029583", "PRES", "procedural", "sanction", "explicit", "high", 0,
     "一切やってないのにbanくらったのは納得いきません、とりあえず10000円返してください",
     "認為未使用外掛卻被封號、申訴無效,處罰不公", "补样(跨语言;JA sanction)"),
    # access_exclusion: the ONLY genuine JA instance (see 02a5 FINDINGS; ja stays below floor)
    ("201569269", "PRES", "procedural", "access_exclusion", "explicit", "medium", 0,
     "普通は企業がやることをユーザ側にやらせる ... ワイのPC（2023年に組み立てた）のマザーボードでは対応してなかった",
     "認為強制用戶開Secure Boot、把本應企業負責的事推給玩家,硬體不支援者被擋在門外", "补样(跨语言;JA access_exclusion唯一实例;up=1;ja仍<3门槛=真实稀疏)"),
    # competitive_balance: EN + JA (BF) -> reaches en3/zh3/ja3
    ("225680958", "PRES", "procedural", "competitive_balance", "explicit", "high", 0,
     "Lets make a pay to win gun (MK-4) with no balancing whatsoever",
     "认为存在无平衡的付费致胜武器,破坏PvP公平", "补样(跨语言;EN competitive_balance)"),
    ("203001509", "PRES", "procedural", "competitive_balance", "explicit", "medium", 0,
     "op guns locked behind a paywall classic EA stuff",
     "认为强力武器被付费墙锁住,付费者获得PvP不当优势", "补样(跨语言;EN competitive_balance)"),
    ("202937972", "PRES", "procedural", "competitive_balance", "explicit", "high", 0,
     "The matchmaking is awful. The opposing team is like special forces and your team is like soldiers who don't know which side of the gun bullet comes out of",
     "认为匹配失衡造成一边倒对局,竞技不公", "补样(跨语言;EN competitive_balance)"),
    ("162341785", "PRES", "procedural", "competitive_balance", "explicit", "high", 0,
     "基本的にどちらかの陣営が有利になる ... プレイヤーバランスがないため一方的な試合ばかり",
     "認為缺乏玩家平衡機制、總是一方有利、對局一面倒,競技不公", "补样(跨语言;JA competitive_balance)"),
    ("159465541", "PRES", "procedural", "competitive_balance", "explicit", "high", 0,
     "一方的な撃ち合いが多くなる 何故BF5のような競技バランスが受け継がれなかった ... バランスが悪いとしか言いようがない",
     "認為競技平衡較前作退化、對局一面倒,不公", "补样(跨语言;JA competitive_balance)"),
    ("178770151", "PRES", "procedural", "competitive_balance", "explicit", "medium", 0,
     "攻撃側が一方的に摺りつぶされる場面が結構多い。何より戦車やヘリがめちゃめちゃ強い。歩兵の対抗手段も少ない",
     "認為重生點設計+載具過強而步兵缺乏對抗手段,造成結構性不公", "补样(跨语言;JA competitive_balance;up=1)"),
]

CODE_MAP = {
    "NA":   dict(unfair_label="NA", out_of_scope=True),
    "ABS":  dict(unfair_label="ABSENT", out_of_scope=False),
    "ABSB": dict(unfair_label="ABSENT", out_of_scope=False),
    "PRES": dict(unfair_label="PRESENT", out_of_scope=False),
}

# lang lookup from the worksheet
def lang_index():
    idx = {}
    with (ROOT / "data" / "raw" / "pilot_worksheet.jsonl").open() as f:
        for line in f:
            d = json.loads(line)
            idx[d["review_id"]] = d["lang"]
    return idx


def expand(entry):
    rid = entry[0]
    code = entry[1]
    subtype = entry[2] if len(entry) > 2 else ""
    facet = entry[3] if len(entry) > 3 else ""
    expl = entry[4] if len(entry) > 4 else ""
    conf = entry[5] if len(entry) > 5 else ""
    bl = entry[6] if len(entry) > 6 else 0
    ev = entry[7] if len(entry) > 7 else ""
    claim = entry[8] if len(entry) > 8 else ""
    note = entry[9] if len(entry) > 9 else ""

    base = CODE_MAP[code]
    row = {
        "review_id": rid,
        "language": None,  # filled later
        "unfair_label": base["unfair_label"],
        "out_of_scope": base["out_of_scope"],
        "evidence_span": ev,
        "normalized_claim": claim,
        "subtype": [s for s in subtype.split(",") if s],
        "procedural_facet": [f for f in facet.split(",") if f],
        "explicitness": expl or None,
        "confidence": conf or ("high" if code in ("ABS",) else None),
        "borderline": bool(bl),
        "uncertainty_reason": "",
        "annotator_note": note,
        "original_label": base["unfair_label"],
        "adjudicated_label": "",
        "adjudication_reason": "",
        "codebook_version": CODEBOOK_VERSION,
        "annotator": "claude-opus-4-8 (pilot draft)",
    }
    if row["borderline"]:
        row["confidence"] = "low"
        if not row["uncertainty_reason"]:
            row["uncertainty_reason"] = "borderline per §6"
    return row


ALL = EN + ZH + JA + TOPUP


def main():
    li = lang_index()
    rows = [expand(e) for e in ALL]
    for r in rows:
        r["language"] = li.get(r["review_id"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # sanity: no dup ids, all have language
    ids = [r["review_id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate review_id in labels"
    missing = [r["review_id"] for r in rows if not r["language"]]
    from collections import Counter
    c = Counter((r["language"], r["unfair_label"]) for r in rows)
    print(f"labels -> {OUT}   n={len(rows)}  missing_lang={len(missing)}")
    for k in sorted(c, key=lambda x: (str(x[0]), x[1])):
        print(f"  {k[0]} {k[1]}: {c[k]}")


if __name__ == "__main__":
    main()
