# 压力集预登记 修订（STRESS PRE-REG AMENDMENT）— v1.2（EN/ZH 关键词分语言化）

> **状态：EN/ZH 关键词表升级并重跑机械检索已执行（Yifan 授权，2026-08-12）。** 仅替换 v1.1 §5 的「EN/ZH 共用表」；其余一切（N_screen/N_final 拆分、5+5 目标、去重顺序、防火墙、人工盲标待 prompt 冻结）沿用 v1.1 不变。
> **不追溯修改 v1.1。** v1.1 §5 的共用 EN/ZH 表作为历史记录保留；本文件是其 EN/ZH 部分的**替代执行版**。JA 仍以 v1.1 §5.1 为准（本次未动）。
> 建立：2026-08-12。维护人：Yifan（`NPC010100Nonbug`）。可执行真相源：`scripts/05_stress_retrieve.py` 的 `EN` / `ZH` 字典（本文件与之逐条一致）。
> 依据草案：`freeze/stress_keywords_en_zh_external_addendum_draft.md`（外部公开 Steam 页面发现的自然表达；未读取本项目 gold / stress 候选 / 未开放正文）。

---

## 0. 为什么升级（一句话）

v1.1 把英、中的高精度模式**混在同一张 `EN_ZH` 表**里，在两种语言的正文上都跑。后果：中文专用模式（如 `阵营优势`、`匹配碾压`）扫英文一条不中，`en competitive_balance` 高精度实际只剩 1 个能用的模式 → high=1。**这是我 EN/ZH 初稿的乐器不对称，不是语言规律。** v1.2 把表**按语言拆开**（`EN` 只跑英文桶、`ZH` 只跑简中桶），并并入外部页面发现的自然表达。**这不是把三语词条数凑齐，是修掉跨语言不触发。**

> 这不改变任何标签。词表只决定候选**进不进筛读池**；`PRESENT`/`ABSENT` 与 subtype/facet 仍由冻结 codebook `v1.0` + 盲法人工定。

---

## 1. 检索语义与编译约定（本次固定并登记）

- **英文模式以 `re.IGNORECASE` 编译**；所有模式**只在对应 Steam-language 桶内运行，不跨语言复用**（`TABLES = {"en":EN, "zh":ZH, "ja":JA}`）。
- **`.{0,n}` 是「同一条评论中隔开出现」的检索窗口**（近邻共现，不要求相邻、不要求顺序按写法之外的额外约束——顺序即模式内从左到右）。
- **编译标志固定为 `re.IGNORECASE | re.DOTALL`**：使 `.{0,n}` 窗口**可跨换行**（Steam 评论常含换行；否则「cheaters …\n… ignored」这类跨行抱怨会漏）。这是本次按草案要求「固定标点/空白处理并原样登记」的决定。
- `high`（高精度）= 更可能钓到可标 PRESENT 的候选，**不是自动标签**；`broad`（宽口径）同时钓 PRESENT 与有价值的 hard negative，**broad 命中不得直接算 PRESENT**。
- `access_exclusion` **不设单词型高精度词**，只用「技术准入限制 + 实际排除/玩不了」的条件组合；规范线索（不正当/无理由/破坏既有付费期待）由人工在盲标时另核。

---

## 2. 英语专属表（`EN`，仅跑 en 桶）

| 目标桶 | 高精度（偏 PRESENT） | 宽口径（兼钓 hard negative） |
|---|---|---|
| `distributive` | `pay[- ]?(to\|2)[- ]?win`；`(paying\|paid\|premium)…(advantage\|edge\|stronger\|win)`；`(weapons?\|guns?\|vehicles?\|characters?)…(locked\|lock)…(pay\|premium\|edition\|DLC)`；`(f2p\|free[- ]to[- ]play\|non[- ]paying)…(unfair\|disadvantage\|cannot compete)` | premium、paid、paywall、battle?pass、DLC、unlock、grind、edition、skin |
| `cheating_governance` | `(cheaters?\|hackers?\|cheating\|hacks?)…(running wild\|run rampant\|not banned\|never banned\|ignored)`；`(reports?\|reporting)…(does nothing\|no action\|not actioned\|ignored)`；`(anti[- ]?cheat\|anticheat)…(useless\|does nothing\|not working\|failed)`；`(devs?\|developers?\|EA\|Valve\|officials?)…(do not\|don't\|never\|won't)…(ban\|act\|care\|fix)…(cheat\|hack)` | cheat、cheater、hacker、hack、aimbot、wall?hack、anti-cheat、VAC、report |
| `sanction` | `(false\|wrongful(ly)?\|unjust(ly)?\|mistaken)…(perma(nent)?\|game\|VAC)? ?ban(ned)?`；`(banned\|ban)…(no reason\|no explanation\|without…reason)`；`(appeal\|support)…(denied\|ignored\|no response\|won't respond\|copy[ -]?paste)` | ban、banned、game ban、VAC、kick、appeal、support |
| `competitive_balance` | `(matchmaking\|MMR\|ranked? match(es)?)…(unfair\|rigged\|one[- ]sided\|unbalanced)`；`(new\|low[- ](level\|rank\|MMR)\|beginner)…(matched\|put\|placed)…(high[- ](level\|rank\|MMR)\|veterans?\|prestige\|top)`；`matchmaking…(skill gap\|rank disparity\|huge gap)` | matchmaking、MMR、rank、balance、one-sided、stomp、new player、veteran、aim assist、RNG、OP |
| `unfair_by_design` | `(artificial difficulty\|cheap design\|unfair design\|unfair mechanic)`；`(enemies?\|boss(es)?\|AI)…(input read(ing)?\|reads? inputs?)`；`(enemies?\|boss(es)?\|AI)…(infinite\|unlimited)…(stamina\|poise\|combos?)` | difficulty、hard、boss、enemy、AI、artificial、cheap、one-shot |
| `access_exclusion` | **仅组合**：`(secure ?boot\|TPM\|kernel[- ]level anti[- ]cheat)…(required\|require\|forced)…(can't play\|cannot play\|unable to play\|locked out\|not supported)`；`(Linux\|Steam Deck\|Proton)…(unsupported\|cannot play\|locked out)…(unreasonable\|no reason\|pointless\|does nothing\|forced)?` | secure?boot、TPM、Linux、Steam Deck、Proton、kernel、BIOS、UEFI、motherboard、cannot launch |

## 3. 简体中文专属表（`ZH`，仅跑 zh 桶）

| 目标桶 | 高精度（偏 PRESENT） | 宽口径（兼钓 hard negative） |
|---|---|---|
| `distributive` | `(氪金\|付费\|充值)…(解锁\|获得)…(武器\|枪械\|角色\|载具)…(不公平\|影响…平衡\|优势\|打不过)`；`(不氪\|零氪\|白嫖)…(打不过\|没法玩\|不公平\|劣势\|被虐)`；`(P2W\|pay[- ]to[- ]win\|逼氪\|强制氪金)…(优势\|不公平\|平衡\|武器\|角色\|载具)` | 氪金、付费、充值、P2W、通行证、战令、DLC、解锁、抽卡、皮肤、价格 |
| `cheating_governance` | `(外挂\|挂(逼\|壁)?\|作弊)…(官方\|蓝洞\|EA\|开发\|运营\|策划)…(不管\|不作为\|不整治\|不封\|放任)`；反向同现；`举报…(石沉大海\|没…回应/回复/反馈\|不受理\|没用)…(外挂\|挂\|作弊)?`；`反作弊…(没用\|无用\|摆设\|形同虚设\|不作为)` | 外挂、挂、作弊、锁头、透视、DMA、反作弊、举报、封号 |
| `sanction` | `(误封\|误判封禁\|无故封号\|莫名…封\|突然…永封)`；`(申诉\|投诉\|客服)…(无门\|不处理\|不回复\|石沉大海\|不受理\|驳回)`；`(封号\|封禁\|永封)…(没…理由\|不…说明\|没有…证据)` | 封号、封禁、永封、误封、申诉、客服、踢出 |
| `competitive_balance` | `(新手\|萌新\|低等级\|低段位)…(匹配\|分配)…(老玩家\|大佬\|高等级\|高段位)`；`(匹配机制\|匹配)…(不公平\|不平衡\|一边倒\|被碾压\|虐菜\|等级差\|段位差)`；`(新手\|萌新)…(被…虐/碾压\|完全没…体验)` | 匹配、匹配机制、段位、等级、平衡、碾压、虐菜、新手、萌新、大佬、RNG、运气、OP |
| `unfair_by_design` | `(敌人\|怪物\|AI\|BOSS)…(读指令\|读取指令\|预读…操作/指令)`；反向同现；`(恶意设计\|不合理设计\|不公平机制\|人工难度)…(敌人\|BOSS\|AI\|战斗\|难度)?`；`(敌人\|怪物\|AI\|BOSS)…(无限…精力/耐力\|不讲理…机制)` | 读指令、人工难度、恶意设计、机制、理不尽、难度、boss、AI、即死 |
| `access_exclusion` | **仅组合**：`(安全启动\|Secure?Boot\|TPM)…(强制\|必须\|要求)…(不能玩\|不给进\|进不去\|无法进入\|玩不了)`；`(改BIOS/主板/设置\|更换主板/硬件)…(才能\|才可)…(进游戏\|玩游戏)` | 安全启动、Secure?Boot、TPM、Linux、Steam Deck、Proton、kernel、BIOS、主板、进不去、启动失败 |

> JA 表未动，见 v1.1 §5.1。

---

## 4. 本次重跑结果（机械、只落 candidate id、不读正文）

- **候选池整表重生成、覆盖旧文件**（`data/splits/stress_candidate_manifest.csv`）；**不与旧池拼接**（草案 §6.3）。
- `frame=419,827  baseline=1,088  eligible=419,227`；**候选 44,354 → 59,811**。
- **高精度（偏 PRESENT）逐格对比（v1.1 → v1.2）——语言拆分的效果集中在这里：**

| cell | v1.1 high | v1.2 high | 读法 |
|---|---:|---:|---|
| en competitive_balance | **1** | **39** | 乐器不对称已修（原只剩 1 个能触发的英文模式） |
| en sanction | 19 | **141** | 同上 |
| en cheating_governance | 68 | **181** | 同上 |
| en distributive | 112 | 147 | 稳健 |
| en unfair_by_design | 82 | 64 | 略降（新模式更聚焦「机制批评」而非泛难度） |
| en access_exclusion | 53 | **7** | 新组合更严（须「要求→玩不了」），精度↑但偏薄；broad 2,866 兜底 |
| zh distributive | 2 | **0** | 见 §5：疑似**真稀疏**（三款游戏非 gacha/P2W） |
| zh sanction | 74 | 105 | 稳健 |
| zh cheating_governance | 7 | **214** | 乐器不对称已修 |
| zh competitive_balance | 6 | **32** | 同上 |
| zh unfair_by_design | 100 | 62 | 新模式更聚焦 |
| zh access_exclusion | 10 | 4 | 偏薄；broad 1,327 兜底 |

> 每格 broad 层仍宽（57–16,236 不等），**没有一格「填不上」**；高精度薄只意味着「要多读 broad 才凑到 PRESENT」，不等于该构念在语料里不存在。

---

## 5. 需在盲标阶段验证的「疑似真稀疏」格（不是词表能补的）

以下格高精度极薄，**大概率是语料本身少，不是关键词漏**；按 v1.1 §9 诚实口径**报为发现、不得降门槛凑数**：

- **`zh distributive` high=0**（broad 1,080）：CS2 / BF2042 / Elden Ring 均非抽卡/强付费模式；简中「氪金→竞争性不公平」表达疑似天然罕见。broad 里多是皮肤/价格/DLC 等**非竞争性**付费吐槽（正是 hard negative）。
- **`ja access_exclusion` high=0**（broad 38）、**`ja sanction` high=6**（broad 57）、**`zh access_exclusion` high=4**：低资源 + 罕见 facet，读满 ≤120/格仍可能不足 5，**照实报真实数量**。

> 区分原则（本次核心）：**看候选原始计数**来 QA 乐器（拆分前后 high 数变化）**不是 p-hacking**；p-hacking 是「读了正文、看了标签后再回改关键词去塑造 PRESENT/ABSENT」。本次全程只看计数、未开正文。

---

## 6. 仍未跨的门（与 v1.1 一致）

1. **打开任何 stress 候选正文 / 人工盲标 → 必须等 prompt 冻结之后**（同 gold 手标那道门）。本次只做机械检索。
2. 盲标定出 `stress_final_manifest.csv` 后，**必须把 `review_id → role=stress` 写回 `split_manifest.csv`**，且**在切 train（⑤）之前**（否则泄漏，见 data_split_spec §3 的 ③′<⑤）。
3. codebook `v1.0` 与随机种子不因本次改动而变。
