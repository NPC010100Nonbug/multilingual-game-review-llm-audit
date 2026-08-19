# EN/ZH 压力集外部表达增补草案（不修改 v1.1）

> **状态：DRAFT，2026-08-12。** 本文件仅以公开、外部 Steam 页面发现候选表达；未读取本项目的 gold、stress 候选或未开放正文。它**不追溯修改** `stress_preregistration.md` v1.1：该文件已声明关键词表冻结并已授权机械检索。本草案只有在维护人明确决定建立 `v1.2 amendment` / `v2`、以新版本完整重跑检索后，才可变成执行规则。

## 1. 目的与使用边界

这不是把三种语言的词条数凑成相同，而是修正 EN/ZH 原表把不同语言的词混在同一格、导致某语言实际可触发的 high-precision 模式过少的问题。

- 词表只能决定**候选进入筛读池**；最终 `PRESENT` / `ABSENT`、subtype/facet 仍由盲法人工标注和冻结 codebook 决定。
- 建议扫描端以 `re.IGNORECASE` 编译英语模式；所有模式仅在相应 `Steam-language bucket` 中运行，不能跨语言复用。
- `high-precision` 的含义是“更可能得到可标为 PRESENT 的候选”，不是自动标签。
- `broad` 用于同时找到可能的 PRESENT 和整体 `ABSENT` hard negative；不能把 `broad` 命中直接算作 PRESENT。
- `access_exclusion` 必须同时有：技术/平台准入限制、实际排除或无法游玩、以及不合理/无正当理由/既有付费期待被破坏的规范线索。只有技术故障，不是该构念。
- 下列正则的 `.{0,n}` 是检索窗口建议；正式使用前须在独立脚本中固定 Unicode 规范化、大小写、标点处理方式，并把实际模式原样登记。

## 2. 英语专属候选词表

| 目标桶 | high-precision：候选正例 | broad：候选正例与 hard negative | 人工必须排除/转类 |
|---|---|---|---|
| `distributive` | `\bpay[- ]?(?:to|2)[- ]?win\b`; `(?:paying|paid|premium).{0,40}(?:advantage|edge|stronger|win)`; `(?:weapons?|guns?|vehicles?|characters?).{0,50}(?:locked|lock).{0,50}(?:pay|premium|edition|DLC)`; `(?:f2p|free[- ]?to[- ]?play|non[- ]?paying).{0,60}(?:unfair|disadvantage|cannot compete)` | `premium`, `paid`, `paywall`, `battle ?pass`, `DLC`, `unlock`, `grind`, `edition`, `skin` | 仅抱怨皮肤/外观、价格或肝度；仅描述有 premium 而没有竞争性优势/不平等。 |
| `procedural.cheating_governance` | `(?:cheaters?|hackers?|cheating|hacks?).{0,70}(?:running wild|run rampant|not banned|never banned|ignored)`; `(?:reports?|reporting).{0,70}(?:does nothing|no action|not actioned|ignored)`; `(?:anti[- ]?cheat|anticheat).{0,70}(?:useless|does nothing|not working|failed)`; `(?:devs?|developers?|EA|Valve|officials?).{0,60}(?:do not|don't|never|won't).{0,60}(?:ban|act|care|fix).{0,60}(?:cheat|hack)` | `cheat`, `cheater`, `hacker`, `hack`, `aimbot`, `wall ?hack`, `anti[- ]?cheat`, `VAC`, `report` | 只说“遇到作弊者”但未说治理缺失；玩家互骂 hacker。前者通常是 `ABSENT`，不是治理构念。 |
| `procedural.sanction` | `\b(?:false|wrongful(?:ly)?|unjust(?:ly)?|mistaken).{0,18}(?:perma(?:nent)?|game|VAC)? ?ban(?:ned)?\b`; `(?:banned|ban).{0,90}(?:no reason|no explanation|without.{0,25}reason)`; `(?:appeal|support).{0,90}(?:denied|ignored|no response|won't respond|copy[ -]?paste)` | `ban`, `banned`, `game ban`, `VAC`, `kick`, `appeal`, `support` | 承认作弊或违规后抱怨处罚；纯询问申诉步骤；只谈其他玩家被封。 |
| `procedural.competitive_balance` | `(?:matchmaking|MMR|ranked? match(?:es)?).{0,80}(?:unfair|rigged|one[- ]sided|unbalanced)`; `(?:new|low[- ]?(?:level|rank|MMR)|beginner).{0,80}(?:matched|put|placed).{0,80}(?:high[- ]?(?:level|rank|MMR)|veterans?|prestige|top)`; `matchmaking.{0,60}(?:skill gap|rank disparity|huge gap)` | `matchmaking`, `MMR`, `rank`, `balance`, `one[- ]sided`, `stomp`, `new player`, `veteran`, `aim assist`, `RNG`, `OP` | 一般“角色/武器平衡差”应先判断是否为单纯质量抱怨；若对象是外挂治理，应转 `cheating_governance`。 |
| `procedural.unfair_by_design` | `(?:artificial difficulty|cheap design|unfair design|unfair mechanic)`; `(?:enemies?|boss(?:es)?|AI).{0,70}(?:input read(?:ing)?|read(?:s)? inputs?)`; `(?:enemies?|boss(?:es)?|AI).{0,70}(?:infinite|unlimited).{0,30}(?:stamina|poise|combos?)` | `difficulty`, `hard`, `boss`, `enemy`, `AI`, `artificial`, `cheap`, `one[- ]?shot` | “很难”“打不过”“boss 很强”没有明确机制批评，均不是 PRESENT。 |
| `procedural.access_exclusion` | **只使用条件组合，不设单词型 HP。** `(?:secure ?boot|TPM|kernel[- ]?level anti[- ]?cheat).{0,90}(?:required|require|forced).{0,90}(?:can't play|cannot play|unable to play|locked out|not supported)`; `(?:Linux|Steam Deck|Proton).{0,90}(?:unsupported|cannot play|locked out).{0,90}(?:unreasonable|no reason|pointless|does nothing|forced)?`；人工另核对规范线索 | `secure ?boot`, `TPM`, `Linux`, `Steam Deck`, `Proton`, `kernel`, `BIOS`, `UEFI`, `motherboard`, `cannot launch` | 纯设置教程、普通崩溃、只说不愿开启而未说明被排除/不合理，不能入 PRESENT。 |

## 3. 简体中文专属候选词表

| 目标桶 | high-precision：候选正例 | broad：候选正例与 hard negative | 人工必须排除/转类 |
|---|---|---|---|
| `distributive` | `(?:氪金|付费|充值).{0,50}(?:解锁|获得).{0,50}(?:武器|枪械|角色|载具).{0,80}(?:不公平|影响.{0,15}平衡|优势|打不过)`; `(?:不氪|零氪|白嫖).{0,70}(?:打不过|没法玩|不公平|劣势|被虐)`; `(?:P2W|pay[- ]?to[- ]?win|逼氪|强制氪金).{0,80}(?:优势|不公平|平衡|武器|角色|载具)` | `氪金`, `付费`, `充值`, `P2W`, `通行证`, `战令`, `DLC`, `解锁`, `抽卡`, `皮肤`, `价格` | 皮肤/外观付费、单纯价格高、推荐付费省肝、未声称竞争性差别。 |
| `procedural.cheating_governance` | `(?:外挂|挂(?:逼|壁)?|作弊).{0,80}(?:官方|蓝洞|EA|开发|运营|策划).{0,80}(?:不管|不作为|不整治|不封|放任)`; `(?:官方|蓝洞|EA|开发|运营|策划).{0,80}(?:不管|不作为|不整治|不封|放任).{0,80}(?:外挂|挂(?:逼|壁)?|作弊)`; `举报.{0,80}(?:石沉大海|没.{0,12}(?:回应|回复|反馈)|不受理|没用).{0,80}(?:外挂|挂|作弊)?`; `反作弊.{0,80}(?:没用|无用|摆设|形同虚设|不作为)` | `外挂`, `挂`, `作弊`, `锁头`, `透视`, `DMA`, `反作弊`, `举报`, `封号` | 只写“外挂多”，但没有官方/系统治理失败；单纯谩骂其他玩家。 |
| `procedural.sanction` | `(?:误封|误判封禁|无故封号|莫名.{0,10}封|突然.{0,10}永封)`; `(?:申诉|投诉|客服).{0,80}(?:无门|不处理|不回复|石沉大海|不受理|驳回)`; `(?:封号|封禁|永封).{0,80}(?:没.{0,15}理由|不.{0,15}说明|没有.{0,15}证据)` | `封号`, `封禁`, `永封`, `误封`, `申诉`, `客服`, `踢出` | 自认/明示违规；只问客服渠道；只说外挂未封（后者优先 `cheating_governance`）。 |
| `procedural.competitive_balance` | `(?:新手|萌新|低等级|低段位).{0,80}(?:匹配|分配).{0,80}(?:老玩家|大佬|高等级|高段位)`; `(?:匹配机制|匹配).{0,80}(?:不公平|不平衡|一边倒|被碾压|虐菜|等级差|段位差)`; `(?:新手|萌新).{0,80}(?:被.{0,15}(?:虐|碾压)|完全没.{0,12}体验)` | `匹配`, `匹配机制`, `段位`, `等级`, `平衡`, `碾压`, `虐菜`, `新手`, `萌新`, `大佬`, `RNG`, `运气`, `OP` | 只有输赢情绪或角色数值吐槽；若不平等来自外挂，转 `cheating_governance`。 |
| `procedural.unfair_by_design` | `(?:敌人|怪物|AI|BOSS|boss).{0,70}(?:读指令|读取指令|预读.{0,15}(?:操作|指令)?)`; `(?:读指令|读取指令|预读.{0,15}(?:操作|指令)?).{0,70}(?:敌人|怪物|AI|BOSS|boss)`; `(?:恶意设计|不合理设计|不公平机制|人工难度).{0,80}(?:敌人|BOSS|AI|战斗|难度)?`; `(?:敌人|怪物|AI|BOSS|boss).{0,70}(?:无限.{0,15}(?:精力|耐力)|不讲理.{0,15}机制)` | `读指令`, `人工难度`, `恶意设计`, `机制`, `理不尽`, `难度`, `boss`, `BOSS`, `AI`, `即死` | 仅“难”“坐牢”“打不过”；没有可识别的设计/机制批评。 |
| `procedural.access_exclusion` | **只使用条件组合，不设单词型 HP。** `(?:安全启动|Secure ?Boot|TPM).{0,90}(?:强制|必须|要求).{0,90}(?:不能玩|不给进|进不去|无法进入|玩不了)`; `(?:改(?:BIOS|主板|设置)|更换(?:主板|硬件)).{0,80}(?:才能|才可).{0,80}(?:进游戏|玩游戏)`；人工另核对“强迫/不合理/官方自己无法防挂/付费后被挡”等规范线索 | `安全启动`, `Secure ?Boot`, `TPM`, `Linux`, `Steam Deck`, `Proton`, `kernel`, `BIOS`, `主板`, `进不去`, `启动失败` | 技术支持帖、一般死机或单纯 BIOS 教程；没有不正当排除/既有期待破坏的表达。 |

## 4. 公开外部 Steam 依据（只用于候选发现）

| ID | 语言 | 相近游戏/页面类型 | 可支持的表达族（概述，不是频率估计） | 用途 |
|---|---|---|---|---|
| E1 | EN | [PUBG 负评](https://steamcommunity.com/app/578080/negativereviews/?browsefilter=toprated&l=english&snr=1_5_100010_) | cheaters running wild；reporting does nothing；开发者未封禁 | `cheating_governance` |
| E2 | EN | [Hunt: Showdown 负评](https://steamcommunity.com/app/594650/negativereviews/) | 新手/低等级被放入高等级对局；MMR 与 matchmaking 不公平 | `competitive_balance` |
| E3 | EN | [War Thunder 讨论](https://steamcommunity.com/app/236390/discussions/0/4031350479980248008/) | pay to win；不付费者处于不公平劣势 | `distributive` |
| E4 | EN | [Rainbow Six Siege 误封讨论](https://steamcommunity.com/app/359550/discussions/1/596266329491638679/) | falsely/permanently banned；appeal denied；未给理由 | `sanction` |
| E5 | EN | [Dark Souls III 讨论](https://steamcommunity.com/app/374320/discussions/0/597391264850126885/) | artificial difficulty 与单纯难度的区分 | `unfair_by_design` |
| E6 | EN | [Battlefield 6 Secure Boot 讨论](https://steamcommunity.com/app/2807960/discussions/0/600786083349820262/) | Secure Boot 被要求；不能启用者无法游玩 | `access_exclusion` |
| Z1 | ZH | [PUBG 简中评测](https://steamcommunity.com/app/578080/reviews/?browsefilter=trendmonth&filterLanguage=schinese&l=schinese) | 官方不整治外挂；举报无反馈；误判封禁/申请复核 | `cheating_governance`、`sanction` |
| Z2 | ZH | [Dota 2 简中评测](https://steamcommunity.com/app/570/reviews/?browsefilter=toprated&l=schinese) | 新手保护不足；低等级玩家与老手相遇、反复被压制 | `competitive_balance` |
| Z3 | ZH | [Furi 简中负评](https://steamcommunity.com/app/423230/negativereviews/?browsefilter=trendyear&filterLanguage=schinese&l=schinese&p=1) | boss/战斗逻辑“读指令” | `unfair_by_design` |
| Z4 | ZH | [人中之龙 极简中页面](https://steamcommunity.com/app/3717330?l=schinese) | 敌人“读指令”与战斗系统批评并列 | `unfair_by_design` |
| Z5 | ZH | [Hired Ops 简中评测](https://steamcommunity.com/app/374280/reviews/?browsefilter=toprated&filterLanguage=schinese&l=hungarian) | 模式一方优势、付费系统与武器/装备解锁语汇 | `competitive_balance`、`distributive`（仅作宽口径发现） |
| Z6 | ZH（术语验证） | [Battlefield 6 Secure Boot 讨论](https://steamcommunity.com/app/2807960/discussions/0/600786083349941326/?ctp=3&l=tchinese) | Secure Boot、主板不支持、无法游玩、反作弊要求 | `access_exclusion` 技术术语；**繁中页面不得用于声称简中频率** |

## 5. 外部证据的限度

1. 上表证明的是表达在相近游戏的公开 Steam 语境中实际出现过，**不证明**其在 CS2、Battlefield 2042、Elden Ring 的目标语言桶中常见。
2. E4/E6/Z6 是讨论页而非商店评论；它们只用于补充自然表达与技术术语，不能与目标语料混成任何发生率统计。
3. Z5 的页面 URL 显示为非简中界面但含简中评测内容；故不作为简中用语的核心依据。简中核心依据以 Z1–Z4 为主。
4. 任何新增模式即使来自外部页面，也可能带来大量 hard negative；这正是 broad 层和盲法人工筛读要保留的原因。

## 6. 若要将本草案升级为可执行版本

1. 维护人逐条决定保留、删除或降为 broad，尤其审核 `distributive` 的“竞争性优势”限制和 `access_exclusion` 的规范线索门槛。
2. 把选择后的模式另存为 `stress_preregistration_v1.2.md`（或 v2），写明替代了 v1.1 §5 的 EN/ZH 片段、修改日期和理由；保留 v1.1 不改。
3. 用新版本对**完整 machine-eligible frame**重新做仅 ID/命中词族的机械检索、去重、固定种子排序；旧候选池不应与新池拼接。
4. 只有该修订版、prompt、codebook 和随机种子再次冻结后，才可打开任何 stress 候选正文进行盲法人工标注。
5. 若不建立正式修订版，则保持 v1.1 原样执行，并将本文件留作 v2 开发资料；不得把本文件词条偷偷插入 v1.1 的检索结果。
