# Codebook v1 — 游戏评论中的「感知不公平 / perceived unfairness」

> **状态:🔒 已冻结 v1.0(2026-08-10,Yifan 批准)。** 冻结后不再原地改:实质改动 = v2.0 + 重标 gold/LLM;纯编辑 = v1.0.x。冻结前的起草/修订史(rev2–rev7)见下条与 §10。
> 起草依据:`codebook_framework_references.md`(理论/方法参考)+ `pilot_draft` 真实评论。**这是拿去标注 gold 的正式规范。**
> 起草者:Claude(claude-opus-4-8)｜日期:2026-08-06｜`codebook_version: v1.0`(**🔒 已冻结 2026-08-10,Yifan 批准;冻结后永不原地改,实质改动=v2.0+重标 gold/LLM;纯编辑=v1.0.x**;冻结前修订史 rev2:四子类折叠为两子类 + distributive 三语补样;rev3:out_of_scope→NA 三值 + procedural 加 facet 子层 + 立场闸 + tie-breaker + subtype=other + 反讽三步 + 正例门槛;rev4:立场闸拆撤回vs已解决 + access_exclusion 收紧规范线索 + facet 只用 pilot(去 gold) + PvE/PvP 切分(balance_rng→competitive_balance) + distributive 锚点重审 + Q7 不算内容付费墙 + explicitness/confidence/metadata 操作定义;**rev5:取消 `other` 子类**(subtype 值域 = {distributive, procedural},稀有人际/信息类经复核不成立→ABSENT)+ 误导性付费墙并入 distributive;**rev6:facet 去留改为「两轴分别报告」**(轴1 KEEP/FOLD 合计≥15;轴2 跨语言每语言≥3 + 游戏 locus;两轴互不覆盖)+ 目的性补样加大 pilot(procedural 02a4 + 跨语言 02a5)并披露 + 每 facet 标 locus + 跨语言声称条件成文(§8-Q8)+ metadata 人机同权入模型推理与标注 + explicitness/confidence 空值规则 + Freeman 实证措辞收敛;**rev7(回应外部评审第三轮 + Yifan 三条范围决定):facet 去留改「support_volume + taxonomy_status(core/exploratory/folded)」描述框架(不再叫 KEEP/FOLD)、轴1 阈值正名为「开发样本覆盖门槛」(非频率)、跨语言/稀疏措辞转保守、人际/信息类彻底移出范围、Freeman 明确降为 sensitizing-only 且不再列为冻结缺口、uncertainty_reason 定枚举、anchor_catalog 独立成文、§9 拆「文献限制 / 项目门槛」并加冻结缺口闭合表、跨文件同步**,见 §10)
> **例子只取自 `pilot_draft`(名单见 `data/splits/split_manifest.csv`),未触碰 `pilot_prompt` / gold。** `pilot_draft` 现 **353 条 = 270 随机 + 83 目的性补样**(三批,均为**非随机、关键词种子、逐条读全文并过 §4.0 门槛**:`distributive` 18 条 / `procedural` 44 条 / 跨语言补缺 20 条;provenance 分别见 `data/splits/pilot_draft_purposive_distributive.csv`、`_purposive_procedural.csv`、`_purposive_crosslingual.csv`)。**目的性补样只影响本 codebook 的起草与 facet 计数,绝不进入测量;gold 冻结后由后减前从对齐池随机抽,这些 id 对 gold 不可见。**

---

## 0. 怎么读这份草稿 + 几条起草诚实声明

1. **构念定义(§1)是地基,先读。** 主标签(§2)是 `PRESENT / ABSENT / NA`(NA=无法判断,§3);§3 是 out-of-scope 闸门;§4 子类(含 `procedural_facet`)只做误差分析、**不覆盖主标签**;§5 是这份 codebook 的**心脏——反例/exclusion**;§6 处理不确定;§7 是每条标注要落的字段。
2. **子类只保留两个,这是数据逼出来的决定,不是理论洁癖。** 原本按 Colquitt(2001)四维 justice 起草(distributive / procedural / interpersonal / informational)。但把 `pilot_draft` 逐条读完后,**`interpersonal` 与 `informational` 各只出现 ~1 次"埋在别的抱怨里的语气",0 条能独立成立的例子**;rev3 曾以 `other` 收这两类稀有不公,rev5 复核后发现仅有的两条(`1517290/en/103109840` 信息、`1517290/ja/103331879` 人际)实为**质量/修辞吐槽,不含独立规范违反归因 → 判 ABSENT**,故 **rev5 取消 `other`,subtype 值域收敛为 {`distributive`, `procedural`}**。`procedural` 三语言饱和,`distributive` 经定向补样后三语言齐备。两子类的方向与 Freeman(2022)提供的 sensitizing concepts 一致(**Freeman 仅作研究背景 / 概念启发,不提供本项目的标签边界**,见 §9.1),另两维无论理论种子还是实证观察都是空的。这回答了原 §8-Q1。
3. **实证观察(来自读完 270 条随机 `pilot_draft` + 83 条目的性补样):**
   - **绝大多数评论是噪声或离题**("..""66"、URL、俄/土耳其语刷屏;裸情感词"神""夯""一句好评"不算噪声,按 §3「裸情感 × metadata」定 `ABSENT`/`NA`)。真正带不公平信号的是少数。→ 这说明 §3 的 `out_of_scope` 闸门在实操里极重要,不是摆设。
   - 清晰的不公平信号集中在两处:**规则/机制不公**(外挂+官方不作为、无理由封号、不公踢、反作弊排除、「難しさではなく理不尽」)和**分配不公**(付费解锁/付费墙、区域定价)。
   - **翻倍验证**:随机样本从 135→270,`procedural` 更饱和,`interpersonal/informational` 照旧几乎为空——说明这不是样本量不够,而是本语料(竞技/单机游戏评论)里,玩家的不公平感天然只落在"谁占便宜(distributive)"和"规则乱不乱(procedural)"两处。
   - **语言×游戏在本设计里绑得较紧**(Elden Ring≈JA 高发、BF2042≈ZH/EN 高发、CS2 三语均有)。这带来一个混淆:某 facet 只在一种语言出现,可能只是"它只在某一款游戏里高发",而非"该语言特有"。rev6 用**目的性补缺**(02a5)主动去每个 facet 缺的语种里找例子,以经验判断"语言偏斜"是世界的真实属性还是我播种关键词的偏差(结论见 §4.2.1)。
4. **本草稿标注单位 = 整条评论(review-level)。** 与参考文献里 span 级语料(CAD/HateXplain)不同;`evidence_span` 只作为「支撑判断的原文摘录」保留,不做独立 span 标注任务。
5. **跨语言警告(Hershcovich 2022):** 本草稿虽给了三语例子,但**规则不能靠字面翻译直接套用**。EN/ZH/JA 必须各自 pilot,记录哪些规则跨语言一致、哪些需语言特定适配。**"可以声称跨语言"有明确条件,见 §8-Q8。**
6. **需要 Yifan 拍板的开放问题集中在 §8(现已全部拍板)。**

---

## 1. 构念定义:什么算「感知不公平」

### 1.1 一句话操作定义

> **评论者在文本中表达或清楚暗示:某个主体(开发/发行方/游戏系统,或经由系统的其他玩家)造成的结果、程序、对待方式或信息状态,违反了某种公平规范——即「不该这样 / 不应得 / 说不过去 / 差别对待」——而不仅仅是「难、贵、烂、失望、有 bug」。**

两个必要条件,缺一不可:

- **(A) 有公平规范的指涉**:文本触及「应得 vs 实得」的落差、「差别/不平等对待」、或「程序/规则被破坏」中的至少一种(即**分配 distributive** 或**程序 procedural** 层面的公平规范)。
  > **本次研究范围(rev7 收口,Yifan 定)**:本项目**只测分配与程序两类**感知不公。**人际**(被不尊重地对待 = interpersonal)与**信息**(被隐瞒/误导 = informational)**不在本次研究范围**——即使文本出现这类语气,也**不据此判 PRESENT**;仅当其归因另落到分配或程序层时,按对应 subtype 处理,否则该条只是质量/修辞吐槽 → **ABSENT**(§4、§5)。**不设任何"兜底子类 / 安全阀"**:本次试验不关心人际/信息类可能存在的不公,已从 codebook 干净移除。
- **(B) 有归因对象**:这种落差被(明示或强烈暗示)归到某个**主体或系统**头上,而**最终归因必须落到权威/系统层**(开发/发行/平台,或被其机制/纵容中介的他人);**纯玩家对玩家、无任何系统归因的不满 = ABSENT**(§5-E)。不是归到「游戏本身就难」「我技术差」「我运气不好」这类**非规范性**原因。

> **研究对象一句话**:我们测的是**"由开发/发行/平台系统造成或纵容、被评论者感知为不公平的"**,而非"游戏体验里的一切不公平"。这条把散在 §5-E 的边界收进定义,消除"允许他人却又排除他人"的范围不稳。
> 记本项目标的是**评论者的 perception**,不是「开发者客观上真的不公」。参考文献 §3.5 / §11:`PRESENT` **不能**被读成开发者存在欺骗/剥削/违法的事实认定。

### 1.2 顺序式决策流程(每条评论照此走)

```
Step 0    这条评论可标注吗?(有无实义内容 / 是不是本游戏相关)
          否 → out_of_scope = true,unfair_label = NA(**不是 ABSENT!** 见 §3),停。
Step 0.5  作者立场闸:这段不公平陈述是评论者**本人、当前、认可地主张**的吗?
          若是引用/转述他人("有人说…")、假设/反事实("如果…就不公平")、
          否定("并没有不公平")、**明确撤回判断**("以前觉得不公,现在想想是我误会了/其实合理")、
          或纯反讽(按 §5-F 三步处理)→ 不因此判 PRESENT。
          **区分「已解决」≠「已撤回」**:实际问题解决了、但作者**仍把那段经历当作一次不公事件在陈述**
          ("无理由封我30h,申诉半个月才解")→ **仍 PRESENT**(note 记 resolved=true)。
          只有清晰**撤回不公指控**才排除;仅"问题解决了"不排除。
Step 1    文本里有没有 (A) 公平规范指涉?
          没有 → ABSENT。
Step 2    有 (A) 的话,有没有 (B) 归因到某主体/系统(**最终须落到开发/发行/平台层**)?
          没有(只是"难/贵/烂/我菜/运气差",或纯玩家对玩家无系统归因)→ ABSENT(多半命中 §5)。
Step 3    (A)+(B) 都有 → PRESENT。再填 subtype(可多选)、procedural_facet、explicitness、confidence。
          拿不准 (A) 或 (B) → borderline = true,填 uncertainty_reason,confidence 降级。
```

> 这条流程刻意把「负面/愤怒/差评」放在**很后面**——负面情绪既不是 (A) 也不是 (B)。参考文献 §7:complaint ⊋ unfairness,差评远宽于不公平。

---

## 2. 主标签 `unfair_label`(MacQueen 六字段)

| 字段 | 内容 |
|---|---|
| **code 名** | `unfair_label` ∈ {`PRESENT`, `ABSENT`, `NA`} |
| **简短定义** | 评论是否表达/暗示某公平规范被某主体或系统违反(见 §1.1 A+B);无法判断则 `NA`。 |
| **完整定义** | `PRESENT` 当且仅当 §1.2 走到 Step 3:既有公平规范指涉 (A),又有对主体/系统的归因 (B)。**`NA`** 当 `out_of_scope=true`(无法就不公平做判断,§3)——**NA 不是负例,导出训练/评估时排除**。既非 PRESENT 也非 NA(有实义内容但不构成不公平)才是 `ABSENT`。主标签**与情绪、评分、推荐与否无关**——👎、辱骂、低分都不是判据。 |
| **何时用(inclusion)** | ① 明确用不公平类词并指向机制/主体:"官匹挂太多"(`730/zh/229414199`)、"cheaters in all games and no actions from Dev team"(`730/en/232062443`);② 无理由惩罚:"玩了30多个小时给我封号了…我他妈啥也没干"(`1517290/zh/200120577`);③ 明确「难 vs 理不尽」对立并指认后者:"難しさではなく理不尽をたたきつけてくるゲーム"(`1245620/ja/111593981`);④ 付费门槛/差别获取:"have to have elite edition to unlock one gun in every class"(`1517290/en/196143270`)。 |
| **何时不用(exclusion)** | 见 §5 全表。速记:难 / 贵 / 卡顿崩溃 / bug / 单纯发泄辱骂 / 我技术差 / 运气差 / 玩家之间互喷 / 一般失望——只要缺 (A) 或缺 (B),即 `ABSENT`。 |
| **正例** | 见 inclusion ①–④。 |
| **负例** | "I paid \$90 USD for this?"(`1517290/en/109448913`,纯价格,无规范指涉)、"最初からムズすぎて…でもハマった"(`1245620/ja/199532227`,难但享受)、"worst game ever, would play again"(`730/en/219943456`,情绪+玩梗)。 |

---

## 3. `out_of_scope` 闸门(实操里极高频,必须先过)

| 字段 | 内容 |
|---|---|
| **code 名** | `out_of_scope` ∈ {true, false} |
| **简短定义** | 这条评论**无法就不公平做判断**:没有实义内容,或与本游戏体验无关。 |
| **完整定义** | 命中任一即 `out_of_scope = true`(并强制 `unfair_label = NA`,**不是 ABSENT**):<br>① **无实义**:纯符号/乱码/**不可解读**的单字或串("..""1""66""3REGFRSFSEAF")。**注:可解读的单字情感词(神/好/nice/爽/史…)不落此格,走下方「裸情感 × metadata」规则定 `ABSENT`/`NA`,不自动 NA。**;<br>② **纯与游戏无关**:交易链接/库存链接(`730/ja/205642158`、`217240930`、`219839289`)、与内容无关的外语刷屏(`730/ja/152584036` "хз, не играл"、`165168184`、`200365947`);<br>③ **玩梗/无信息**:"try finger"(`1245620/en/194432373`)、"margit feet…"(`1245620/en/203459819`)、角色台词复读(`1245620/en/223308452`)。 |
| **何时用** | 评论去掉情绪和玩梗后**没有任何可评价的游戏体验陈述**。 |
| **何时不用** | 只要有一句实义的体验/机制陈述,即使很短、很脏话,也 `false`,照常走 §1.2。例:"好玩，就是官匹挂太多了"(`730/zh/229414199`)虽短但有实义 → `false`。**语言≠范围**:非英/中/日的可判读外语意见(如土耳其语"没有外挂的话其实是好游戏"`730/ja/200365947`)不因语言而 out_of_scope,按内容走 §1.2(Yifan 裁定)。 |
| **正例(=true)** | `730/en/226558036`("3REGFRSFSEAF")、`1245620/en/208372626`(".")、`730/zh/219983016`("436")。 |
| **负例(=false)** | `1517290/zh/200120577`(封号申诉,长且有实义)、`730/zh/229414199`。 |

> **裸情感 × metadata(rev5 规则 #3,补写入正文;此前只在 decision_log 与标签里,盲检 2026-08-10 暴露此文档缺口)**:一条**只有情感、无任何机制/体验陈述**的极短评论,**不自动 NA**,按「情感能否解读 + 与 `voted_up` 是否一致」定档:
> - **可解读 且与 `voted_up` 一致**("神/好/GOOD/爽"+荐、"史/垃圾"+不荐)→ **`ABSENT`**(一致、可编码的"无不公平"负例,**不是**噪声);
> - **可解读 但与 `voted_up` 矛盾**(通篇夸却点踩、👍却不荐)→ 先走 §5-F 反讽三步;仍塌 → **`NA`**;
> - **不可解读的乱码 / 纯玩梗**(即使夹着难度情绪)→ **`NA`**(①/③)。
>
> 据此 rev5 把 37 条 `voted_up=true` 的裸好评(好/GOOD/神/最高/爽…)由 NA 改判 **ABSENT**;§3① 与 §0 里"神""夯""一句好评"作 NA 例的旧措辞随之更正。**判据红线不变:标签从正文定;metadata 仅在正文塌成裸情感时用于分 `ABSENT`/`NA`,单独绝不触发 `PRESENT`。**

> **为什么单列这个闸门**:读完首批 135 条,**约一半**落在这里。若不先过闸,LLM/人都会把大量噪声误判进 ABSENT-有内容 或误报 PRESENT。这是本语料相对参考文献里 Reddit/ToS 语料的**特有现象**(Steam 短评噪声极重)。
>
> **为什么是 `NA` 而不是 `ABSENT`(rev3 关键修正)**:`out_of_scope` 混了两种东西——"确认没有不公平"(真负例)和"根本没法判断"(乱码/链接/外语刷屏)。若都压成 ABSENT:① 训练时噪声进负类,模型学到"短+符号=ABSENT"的捷径,而非"有实义但不构成不公平=ABSENT";② 各语言噪声率不同(俄土刷屏在 CS2/ja 尤重),会把"噪声率差异"混进"不公平率差异",污染跨语言比较;③ 事后无法区分两种 ABSENT。故 `out_of_scope=true → unfair_label=NA`,NA 行保留供审计,但**训练/评估一律排除**(§7 导出规则)。
>
> **连带后果(gold 抽样)**:gold 的"≥100/语言"从此指 **≥100 条 `codable`(out_of_scope=false)**。随机抽约一半是噪声,故需**按噪声率补抽**:先抽一批 → 标 out_of_scope → 按缺口随机补,补抽仍走后减前,**gold 随机性不破**。

---

## 4. 子类 `subtype`(可多选;仅用于误差分析,不覆盖主标签)

> **子类值域 = {`distributive`, `procedural`}**(rev5 取消 `other`):两值源自 Colquitt 四维中在本语料真实发生的两维(折叠 `interpersonal`/`informational`、并复核发现 `other` 为空的理由见 §0.2)。**多选**:一条 `PRESENT` 可同时命中两个。**规则:PRESENT 必有 subtype——空值只表示"尚未标注"。** 若一条 PRESENT 的不公既非分配也非程序(理论上的人际/信息类),按 §0.2 复核:本语料中这类要么归入最贴近的分配/程序落点,要么根本不成立(→ 重判 ABSENT);不再保留兜底子类。distributive/procedural 正是 Freeman(2022)25 码集中之处(§9),有实证参考。

### 4.0 三条通用规则(先读)

- **tie-breaker(distributive vs procedural)**:看**不公平的落点**。落在"**谁最终拿到优势/内容/负担的分配结果**"(花钱=有、没花钱=没有;某区=贵)→ `distributive`;落在"**产生结果的规则/执行/准入过程被破坏**"(匹配、治理、封禁、排除)→ `procedural`。**付费解锁默认 `distributive`**;仅当矛头指向"过程强迫"本身且无分配落差描述时才 procedural;两个落点都写到 → 多选都打。
- **正例门槛(主题 ≠ 构念)**:评论**文本自身**须带规范违反线索(应得/差别/被迫/误导/不该如此),**不能仅因主题是付费墙、区域价、封号就判 PRESENT**。纯描述"精英版才解锁"而无任何"不该/被坑/误导"语气 → 降 `borderline` 或归 ABSENT。**每条被 codebook 引用的 anchor 正例须填三件套:完整原文 + 最小 `evidence_span`(须含规范线索)+ `normalized_claim`。** 三件套 + 逐例裁定理由集中存于独立的 **`anchor_catalog`**(§4.2.1、§9.2 缺口3;codebook 正文只留 ID 指针)。
- **metadata 人机同权(rev6,回应 Yifan)**:`voted_up` / `votes_up` / `votes_funny` / `received_for_free` / `steam_purchase` / `weighted_vote_score` / `written_during_early_access` 这组 metadata **必须与正文一起进入(i)人工标注 和(ii)模型推理**,两侧输入对等(parity),不得只给一方。作用是反讽/立场的交叉验证(§5-F、§6.1)。**但判据红线不变:标签一律从正文定;metadata 可升降警觉,单独绝不触发 PRESENT/ABSENT。**(隐私红线:入模型/标注的 metadata **不含作者身份**——steamid/personaname/profile_url 在建 worksheet 时已丢弃。)

### 4.1 `distributive`(分配/结果不公) — 借 Colquitt + Freeman P2W + Xia 价格公平边界
- **定义**:资源/机会/优势/负担的分配被指为不该如此——尤其**花钱买胜负/买解锁**、**花钱跳过肝度**、或**区域差别定价**。
- **inclusion 与三语例子**(均来自 `pilot_draft`,含 18 条 distributive 目的性补样):
  - **付费解锁 / 付费墙(pay-to-unlock / paywall)**:
    - EN:`1517290/en/196143270`(精英版才解锁每职业一把枪)、`1517290/en/138975097`("HAVE TO BUY THE ELITE" 才有基础内容)、`1517290/en/207539435`(武器/载具锁在 Elite 版 + premium currency)、`1517290/en/141902653`(everything locked behind a paywall)。
    - ZH:`1517290/zh/202517276`(精英版只解锁十把枪,且简介写 35 把是误导——含"误导"规范线索)。**⚠ rev4 剔除**:`1517290/zh/165149867`(纯描述通行证解锁枪械,还说"好在配件丰富",无怨气)、`1517290/zh/202254837`(**推荐**买精英版省肝,不是投诉)已降级 ABSENT/borderline——它们只有"付费墙"主题、无规范违反语气,恰是 §4.0"主题≠构念"门槛该拦下的。
    - **误导性付费墙归 distributive(rev5)**:`1517290/en/140004357`(已购 Ultimate 却仍被要求另购通行证)由原 `other` 并入 `distributive`——"应得全部内容却被差别收费"落点在分配。
  - **区域差别定价(regional pricing)**:
    - JA:`1245620/ja/111128390`(日本人被以世界最高价买)、`1245620/ja/111096605`(おま国搾取,9240 円全国最高)、`1245620/ja/121372217`(リージョンロック + 国内版价格畸高)、`1245620/ja/111214517`(おま値,比他国多付 \$20+)、`1245620/ja/113317778`(日本だけ価格が高い)。
  - **付费影响对局的指控(perceived P2W)**:ZH `730/zh/225992615`("不充钱把把发烂牌")——CS2 实际是外观制,此为**感知**指控,仍算(本项目测的是 perception)。
- **本类构念范围(Q7 已决:不算非竞争性内容)**:distributive 只收**竞争优势 / 影响玩法的内容·准入**的分配(P2W、付费解锁枪械/角色、付费跳过影响强度的肝度、区域差别定价);**纯外观/非玩法货币化的怨气不算**(→ ABSENT)。
- **exclusion(硬负例,同来自 `pilot_draft`)**:
  - **单纯嫌贵/不值 ≠ 本类**(§5-B,Xia/Zeithaml 边界):`1517290/en/109448913`("\$90?")**不进**。
  - **纯外观付费墙 ≠ 本类(Q7)**:`1517290/en/164972778`——虽抱怨"most cosmetics locked behind paywall",但锁的是**纯外观、无玩法影响**(评论自己也说 "cosmetic, no impact on gameplay"),不在本构念范围 → **ABSENT**。
  - **公平规范正面对照负例**:ZH `730/zh/227223824`("没有氪金碾压,技术到位就能赢")、`730/zh/229241969`("无强制氪金破坏对局平衡")——把公平规范正面说出来(技术制 ↔ 付费制)。
  - **正例门槛失败 ≠ 本类**:纯描述付费结构而无"不该/被坑/误导/差别"语气(如 `165149867`、`202254837`)→ ABSENT/borderline(§4.0 主题≠构念)。
- **contrastive pair**:负例 `1517290/en/109448913`(纯价格,ABSENT) ↔ 正例 `1517290/en/196143270`(付费墙解锁,PRESENT)。**关键差别:是否"花钱换得相对别人的优势/内容",而非绝对价格高低。**

### 4.2 `procedural`(程序/机制不公) — 借 Colquitt + Leventhal + Freeman 匹配 + Hirota 网络
- **定义**:产生结果的**程序/规则/系统**被指为破坏公平——匹配、外挂治理、封禁、不公踢、反作弊排除、RNG/平衡改动造成的竞争性差异。
- **inclusion 与三语例子**:
  - EN:`730/en/232062443`("cheaters… no actions from Dev team")、`1517290/en/114083525`(反作弊故意不支持 Linux/Deck,平台排除)、`730/en/222115139`(骂 Valve 反作弊无能)。
  - ZH:`730/zh/229414199`("官匹挂太多")、`1517290/zh/200120577`(玩 30h 无理由封号)、`1517290/zh/202460812`(反作弊要改主板、直接不让进)。
  - JA:`1245620/ja/111593981`("難しさではなく理不尽"式设计不公)、`1245620/ja/156643716`("これは難しいんじゃなくて、ただ理不尽なだけ")、`730/ja/160753326`(外挂多 +「Valveはもちろん放置」)、`730/ja/156768786`(没杀够人就被系统踢 = 不公踢)。
- **exclusion**:游戏**难本身** ≠ 本类(§5-A);一般卡顿/崩溃 ≠ 本类(§5-C,除非造成**竞争性差别待遇**,Hirota 边界);**玩家之间**互喷/戾气 ≠ 本类(§5-E,除非指认官方纵容/机制鼓励)。

### 4.2.1 `procedural_facet`(procedural 之下的细分,可多选,仅误差分析)+ 两轴去留框架

> **facet 是显式标注的细分标(§7 `procedural_facet` 字段,每条 PRESENT-procedural 都填)。** 加这一层是因为 `procedural` 太大(匹配/治理/封禁/排除/平衡全塞一起),不利误差分析。**facet 计数只在 `pilot_draft`(试标)上做——绝不用 gold(用 gold 决定 taxonomy = holdout 泄漏,见 §9 缺口4)。** `procedural` 主类始终有效,facet 缺失不影响主类判定。

**rev7 关键改动:不再用"轴1=KEEP / 轴2=FOLD"这种会被人工例外自我打脸的命名。** 改成**四个纯描述维度 + 一个处置状态**——描述维度只如实记录"证据长什么样",处置状态 `taxonomy_status` 才是最终去留,由**概念独立性 + 人工判准稳定性**决定,不被任一单一阈值机械翻转。

**四个描述维度(只报事实,不做裁决):**
- **`support_volume`(开发样本支持量)**:三语言合计的独立 PRESENT 实例数。设一条**开发样本覆盖门槛 = 15**(合计 ≥15 = "在开发样本里证据够厚、可稳定单列")。⚠**这是开发样本的覆盖量,不是自然频率**:pilot_draft 经目的性补样,合计数**不反映真实分布**;真实频率只能由随机 gold 报告(§9.2)。
- **`language_coverage`(语言覆盖)**:达到"每语言 ≥ 3 条独立 PRESENT"这一**存在门槛**的语言数(§8-Q8)。3 = 三语均有证据;2 = 双语;1 = 单语。**这只是"该语言里找得到"的存在性证据,不等于测量等价**(§8-Q8 条件 3/4/5)。
- **`title_coverage`(游戏覆盖)**:该 facet 有证据的游戏数。**≥2 款**才可能从"某作内"上升到"跨游戏观察到";**仅 1 款 = title-specific**。因语言×游戏在本设计里绑得紧(§0.3),这一维用来和 language_coverage 解混淆。
- **(locus 洞图)**:各 facet 已验证 PRESENT 落在的 语言×游戏 单元(见下方 locus 块),也是后续补缺的"洞图"。

**处置状态 `taxonomy_status ∈ {core, exploratory, folded}`(最终去留,人工判定):**
- **`core`** = 证据足(support_volume ≥ 15)**且**判准跨语言稳、概念独立清晰 → 主力 facet。
- **`exploratory`** = 概念上是独立构念、值得保留继续观察,但**证据偏薄**(support_volume < 15)**或**只在单游戏出现 → 保留为**探索性 facet**,报告里**如实标注其薄弱面**(合计偏少 / 单游戏 / 某语言 under-attested),**不声称已验证通用**。
- **`folded`** = 概念上并不独立、或证据太稀且无独立价值 → 并回纯 `procedural`(关键词写进 `annotator_note`)。当前无 facet 落此。

> **为什么这样改(rev7,回应外部评审)**:旧"轴1 KEEP / 轴2 跨语言"把两个**描述性阈值**当成了**处置裁决**,于是 competitive_balance(9)、access_exclusion(11)合计 <15 却按 Yifan 决定保留,就成了"客观阈值被事后人工例外覆盖"的自相矛盾;计数脚本还照旧打印 `FOLD/thin`,与 codebook 保留裁定不一致。改成"描述维度只报事实、`taxonomy_status` 才裁决"后,保留 competitive_balance/access_exclusion 不再是"违反阈值的例外",而是"证据薄的 **exploratory** facet"——**阈值负责描述,状态负责处置**,各司其职、不再打架。`03c_facet_counts.py` 也随之输出 `taxonomy_status`,不再输出 KEEP/FOLD。

> **rev6 补样加大 pilot 的理由与披露**:首版 288 条 pilot 太薄,撑不起公平的 ≥15 / ≥3 测试,故冻结前对 `pilot_draft` 做**目的性 procedural 补样**(02a4,+44)与**跨语言补缺补样**(02a5,+20,专门去每个 facet 缺的语种里找)。pilot 非测量,补样合法;但**必须披露为非随机**(§9 缺口3),且 gold 仍随机、这些 id 对 gold 不可见。

#### facet 定义与 rev6 计数/裁定

| facet | 含义 | support_volume 合计(en/zh/ja) | language / title coverage | `taxonomy_status` + 说明 |
|---|---|---|---|---|
| `cheating_governance` | 外挂/作弊治理不力、反作弊无能、官方放置 | **15**(3/8/4)→ ≥门槛 | 三语 ✓;BF2042:11 + CS2:4 → **2 游戏** | **`core`**;唯一"三语有证据且真跨游戏"的 facet,最强 |
| `sanction` | 处罚不公:无理由/误封、申诉无门、不公踢 | **21**(4/13/4)→ ≥门槛 | 三语 ✓;BF2042:20 + CS2:1 → 名义 2 游戏但 **BF 主导** | **`core`**(证据足);跨语言但**以 BF 为主**,不声称语言普适 |
| `unfair_by_design` | **PvE/单机**:「不是难,是理不尽」的设计层不公(无他人得利) | **24**(4/4/16)→ ≥门槛 | 三语 ✓;**Elden 独占**(1 游戏) | **`core`**(证据足);但**仅法环** → 写成"法环特定构念",不声称语言普适 |
| `competitive_balance`(原 `balance_rng`) | **PvP**:数值/平衡/匹配质量/RNG 使某方拿到**不该有的竞争优势** | **9**(3/3/3)→ <门槛(证据偏薄) | 三语均有证据(3/3/3);**BF 独占**(1 游戏) | **`exploratory`**:三语都确认存在(干净 3/3/3)、是独立 PvP 构念;但 support_volume 偏少 + 单游戏,**如实标注、不声称已验证** |
| `access_exclusion` | 按平台/硬件排除一类玩家、强制改硬件才准入(**须带规范线索**,见下) | **11**(5/5/1)→ <门槛(证据偏薄) | EN·ZH 达存在门槛,**JA=1 未达**;BF 独占(1 游戏) | **`exploratory`**:JA 当前仅 1 条(`1517290/ja/201569269`)。**当前检索与 pilot 中日语证据不足,无法判断是实际稀疏、游戏机制差异,还是检索词召回不足**——故**保留为完整(潜在三语)facet**,只注明"当前 pilot 日语 under-attested";**唯有真正穷尽检索仍一条日语都无,才降注为双语 facet** |

**各 facet 当前 locus(诚实记录,= 已验证 PRESENT 落在的 语言×游戏 单元;也是后续补缺的"洞图")**:

```
cheating_governance : en{CS2,BF} zh{CS2,BF} ja{CS2,BF}   → 三语 × 2 游戏
sanction            : en{BF}     zh{BF}     ja{BF}(+CS2:1) → 三语,BF 主导
unfair_by_design    : en{Elden}  zh{Elden}  ja{Elden}     → 三语,单游戏(法环)
competitive_balance : en{BF}     zh{BF}     ja{BF}         → 三语,单游戏(BF)
access_exclusion    : en{BF}     zh{BF}     ja{BF}=1(<3)  → EN·ZH 达存在门槛,JA under-attested(证据不足),单游戏
```

**anchor 例(来自 `pilot_draft`;下面只列 ID 指针)**:每个 anchor 的**完整原文 + 最小 `evidence_span`(含规范线索)+ `normalized_claim` + 逐例裁定理由**存放在独立的 **`anchor_catalog`**(生成脚本 `scripts/03e_build_anchor_catalog.py`:全文版 `data/raw/anchor_catalog.jsonl` 本机 gitignored,发布版 `data/pilot/anchor_catalog.jsonl` 只含 span/claim/facet/裁定、无全文)。正文不再塞长原文,避免膨胀。
- `cheating_governance`:`730/en/232062443`、`730/zh/229414199`、`730/ja/160753326`、`730/en/222115139`、`1517290/en/228759578`(rev7:"needs anti-cheat"读作治理失职,borderline 正例)
- `sanction`:`1517290/zh/200120577`(封号)、`730/ja/156768786`(没杀够就踢)、`1517290/en/217797587`(误封剥夺已付费权)、`1517290/ja/194187711`(单机打AI误BAN)、`1517290/zh/226675676`(rev7:反讽下无故封号申诉,borderline 正例)
- `access_exclusion`:`1517290/en/114083525`(反作弊不支持 Linux/Deck,"purposely"+外挂没少)、`1517290/zh/202460812`(要改主板+"筛选玩家不给进")、`1517290/ja/201569269`(强制 Secure Boot、非对应主板被挡门外——**JA 唯一实例**)。**边界锚点**(在 `anchor_catalog`,不入正例;见 §5-C):`1517290/zh/228424527` = PRESENT-**borderline**("我不是程序员不该这么难",rev7 Yifan 定为 borderline 而非满配正例);`1517290/zh/162971869` = **hard-negative**(纯陈述 Secure Boot 无语气 → ABSENT)
- `competitive_balance`:`1517290/en/225680958`(无平衡的付费致胜枪)、`1517290/zh/150436907`(匹配碾压)、`1517290/ja/162341785`("プレイヤーバランスがない、一方的な試合")
- `unfair_by_design`:`1245620/ja/111593981`、`1245620/ja/156643716`、`1245620/en/221548261`(boss 读指令、普通玩家无法应对、野外怪可轻松清)、`1245620/zh/230587480`(读指令+无限精力=作弊AI)

> `access_exclusion` **服从 §4.0 正例门槛,不自动触发**:按平台/硬件排除一类玩家 / 筛掉玩家使其无法进场,**须文本带规范线索(不合理差别 / 无正当理由 / 破坏既有期待 / **把技术门槛读作排除非技术玩家**)**才算 `procedural` + `access_exclusion`;纯客观陈述"反作弊要开 Secure Boot"而无怨气 = ABSENT(如 §5-C 的 `1517290/zh/162971869`);带"我不是程序员、不该这么难"排除语气则 borderline-PRESENT(`1517290/zh/228424527`,rev7 由 Yifan 改判)。

> **已删除的两个子类**(`interpersonal` 人际、`informational` 信息):`pilot_draft` 里各仅 ~1 处埋着的语气(interpersonal:`1517290/ja/103331879`「消費者を馬鹿にしている」;informational:`1517290/en/103109840`「attachments do the opposite of what the description gives」),rev5 复核判定为质量/修辞吐槽、无独立规范归因 → **ABSENT**,故连 `other` 兜底一并删除(§0.2)。

---

## 5. 反例 / exclusion 目录 ★本 codebook 的心脏★

> MacQueen(1998)把 exclusion 规定为**强制字段**;参考文献 §11 列了七条「不应直接推出」。下面每条给一个**对照对 `contrastive pair`**(`contrast_id`:硬负例 ↔ 它对照的正例)。**术语更正**:这些取自**不同评论**,长度/语气本就有别,严格叫 *contrastive pair*;真正的 *minimal pair*(只改一个决定性因素)留作 pilot 阶段**人工构造的探针**(HateCheck 式),与真实评论分开,不进 gold 频率统计。

**A. 难 ≠ 不公平** (最重要,Elden Ring 高发)
- 规则:游戏难、被虐、反复失败、"死にゲー"——只要评论者把原因归给**难度/自己技术**而非机制不公,一律 `ABSENT`。**过关的关键在归因切换**:当评论者显式区分"正当难度"与"不正当设计/机制"(读指令、无限耐力、数值用脚填、普通玩家无法应对而野外怪可轻松清),并指认后者 → 进 `unfair_by_design`(§4.2.1)。
- 负例:"I too like pain"(`1245620/en/180670949`)、"きちい"(`1245620/ja/147921615`)、"最初からムズすぎて…ハマった"(`1245620/ja/199532227`)。
- **contrastive pair**:负例 `1245620/ja/199532227`(难但享受,ABSENT) ↔ 正例 `1245620/ja/111593981`(明确说「不是难,是理不尽」,PRESENT)。**关键差别只在归因**:难度 vs 机制不公。

**B. 贵 / 不值 ≠ 不公平** (Xia 2004 / Zeithaml 1988 边界)
- 规则:"太贵""不值""not worth it""坑钱感"本身不是 (A)。要 `PRESENT` 需再有**规范被违反的指涉**(区别定价、付费墙、货不对板)。
- 负例:"I paid \$90 USD for this?"(`1517290/en/109448913`)、"クソ高いし"(`1245620/ja/111442636` 里单看价格的部分)。
- contrastive pair:负例 `1517290/en/109448913`(纯价格,ABSENT) ↔ 正例 `1517290/en/196143270`(付费墙解锁,distributive,PRESENT)。

**C. bug / 崩溃 / 卡顿 / 性能差 ≠ 不公平** (Hirota 2011 边界)
- 规则:技术问题、优化差、掉帧、闪退、进不去——默认 `ABSENT`。**例外**:仅当造成**玩家间竞争性差别待遇**(如反作弊只在某平台可用→排除一类玩家)才可能进 procedural/distributive。
- 负例:"最適化されていない…動作が非常に不安定"(`1245620/ja/111608609`)、"i7/1080Ti でも 60fps 出ない"(`1517290/en/103369911`)、"ゴミ起動しなくなった"(`1517290/ja/155845699`)、纯陈述 secure boot 要求无语气(`1517290/zh/162971869`)。
- **例外(§8-Q2 已决)**:"Anti-cheat 不支持 Linux/Steam Deck"(`1517290/en/114083525`)——差别平台待遇 + 外挂没变少 + "purposely"语气 → `procedural` + `access_exclusion`(PRESENT)。**边界(rev7 Yifan 改判)**:`1517290/zh/228424527`(「我是玩家不是程序员，不该这么难」+一小时进不去)因带"排除非技术玩家"规范语气 → borderline-PRESENT access_exclusion;而纯客观"要开 Secure Boot"无怨气(`1517290/zh/162971869`)仍 ABSENT(须过 §4.0 规范线索门槛)。

**D. 单纯发泄 / 辱骂 / 差评情绪 ≠ 指认不公平** (参考文献 §11)
- 规则:脏话、"司马EA"(`1517290/zh/163376281`)、"一坨"(`1517290/zh/178487861`)、"terrible game"(`1517290/en/183271888`)、"i hate this game"(`730/en/232022679`)——情绪强度不是判据。无 (A)+(B) 即 `ABSENT`。
- contrastive pair:负例 `1517290/zh/196715806`("狗屎EA，狗屎服务器" 纯发泄,ABSENT) ↔ 正例 `1517290/zh/200120577`(同样骂 EA,但**指认了无理由封号这个程序不公**,PRESENT)。**关键差别:有没有落到具体的规范违反。**

**E. 玩家之间的 toxicity ≠ 开发方不公** (本项目边界判断)
- 规则:社区戾气、队友坑、对面嘴臭——是玩家行为,**默认不算本构念**(本构念指向开发/系统)。**例外**:评论明确指认「官方纵容/机制鼓励这种行为」时,可进 `procedural`。
- 负例:"能力越大，素质越低…这个游戏的氛围已经形成了"(`730/zh/226232348`)——批评社区风气,未指认开发方机制 → `ABSENT`(**borderline**,见 §8-Q4)。

**F. 玩梗 / 反讽 / 自嘲 需谨慎** (MFRC 讽刺处理)
- **什么是反讽**:字面与本意相反。"worst game ever, would play again"(`730/en/219943456`)字面差评实为爱;gacha 自嘲"給料がなくなる…ガチャの沼へようこそ"(`730/ja/195708546`)——抱怨氪金机制还是玩梗自嘲?
- **识别线索(都只是线索,任一命中→提高警觉,非确证)**:
  1. **内部矛盾**:字面情绪与结论/行为打架("最烂"+"还会再玩")。
  2. **查 `voted_up`**:通篇夸却**点踩** / 通篇骂却**点赞** → 疑反讽。
  3. **查 `votes_funny`**:"搞笑"票明显偏高 → 多为玩梗,而非正经陈述。
  4. **文化/符号标记**:日 `草`/`w`(=笑)、中"(笑)/乐"、英 `/s`、吓人引号 `"amazing"`、`🙃`、`lmao`。
  5. **已知社区梗模板**:"try finger…""would play again…" 等一眼可认的梗。
- **三步判定**:
  - **① 先用线索尝试还原真实立场**;能定 → 正常判。
  - **② 定不了时,问:标签是否真的取决于反讽?**
    - **否**(公平归因两种读法下都成立,如阴阳"谢谢 Valve 官匹全是挂")→ 按归因正常判,`annotator_note` 记"反讽但不影响归因",confidence 可 medium。
    - **是**(反讽会翻转 PRESENT↔ABSENT 且判不了)→ 进第 ③ 步。
  - **③ 仍判不了**:给**最佳猜测**标签 + `borderline=true` + `uncertainty_reason=irony_undecidable` + `confidence=low`;**若连"有无可标注 claim"都因反讽塌了 → `out_of_scope=true` / `unfair_label=NA`**(§3),不硬掷硬币往负类灌噪声。
- **记**:反讽主要翻转**情绪**,很少翻转**公平归因**;它坑到的多是负例(假夸暗骂/假骂真爱),这些本就多半 ABSENT/NA。**单人标注(你)不能把拿不准甩给别人——每条仍由你落标,`borderline`/`NA` 是你给自己和读者留的诚实标记。**

---

## 6. 不确定性触发器 `borderline` / `uncertainty_reason`(MFRC / Davani 2022)

`borderline = true` 且 `confidence` 降级,当:
1. **归因不清**:有不满但看不出归给机制还是归给难度/自己(§5-A 边界)。
2. **反讽/玩梗**无法定字面正负(§5-F 三步);若连"有无可标注 claim"都塌 → `out_of_scope`/`NA`。
3. **价格 vs 差别定价**难分(§5-B、§8-Q3)。
4. **技术问题是否构成竞争性差别待遇**难判(§5-C 例外、§8-Q2)。
5. **玩家 toxicity 是否被指认为官方责任**难判(§5-E、§8-Q4)。
6. **语言/文化线索不足**:CJK 短评省略主语、依赖语气词,规范指涉可能被压缩(Hershcovich 跨语言风险)。

> 参考文献 §5.4 / §11:**不确定不要压成虚假的确定标签**。保留 `original_label` 与 `uncertainty_reason`,别只留最终标签。

### 6.0 `uncertainty_reason` 受控词表(rev7)

`uncertainty_reason` **不再写泛化的 "borderline per §6"**,须从下列枚举取值(可组合,分号分隔),与 §6 触发器一一对应:

| 值 | 对应触发 | 含义 |
|---|---|---|
| `attribution_unclear` | §6-①、§5-A | 有不满,但归机制还是归难度/自己看不清 |
| `irony_undecidable` | §6-②、§5-F | 反讽无法定字面正负,且会翻转标签 |
| `price_boundary` | §6-③、§5-B | 纯价格 vs 差别定价难分 |
| `technical_access_boundary` | §6-④、§5-C 例外 | 技术问题是否构成竞争性差别待遇难判 |
| `toxicity_attribution` | §6-⑤、§5-E | 玩家 toxicity 是否被指认为官方责任难判 |
| `language_cue` | §6-⑥ | CJK 短评线索不足、规范指涉被语气词压缩 |
| `facet_boundary` | §4.2.1 | PRESENT-procedural 该落哪个 facet 难定 |

> **落地(rev7)**:现有 pilot 标签里 **19 条 borderline** 的 `uncertainty_reason` 仍是旧的泛化 "borderline per §6"。**这属于标注判断,不做机械批改**——在冻结前的**人工验证一遍**(single-annotator test–retest,§9.3)里逐条改判到上表枚举;此后新标注一律直接用枚举。

### 6.1 `explicitness` / `confidence` / metadata 操作定义(rev4 立,rev6 收严空值/定义)

- **`explicitness`** ∈ {explicit, implicit},**仅 `PRESENT` 填,其余留空(null)**(rev6 空值规则:explicitness 描述"不公平如何被表达",对 ABSENT/NA 无意义):
  - `explicit` = 文本**直接用公平/规范词**(不公、理不尽、不该、差别对待、把 paywall/封号明说成不公)。
  - `implicit` = 无公平词,不公须从**描述的事实 + 语气**推出("30h 无缘无故就封了"未用"不公"字样,但显然)。
- **`confidence`** ∈ {high, medium, low} = **对"最终标签(不论 PRESENT/ABSENT/NA)判对了"的把握**(rev6 澄清:confidence 是"对最终标签的确定度",不是"这条有多不公"的强度)。**钉在 §6 触发器上,不自由发挥**:
  - `high` = 判据文本清晰,无反讽/归因歧义(PRESENT:(A)(B) 都清晰;ABSENT:确实缺 A 或 B 且无歧义)。
  - `medium` = 结论稳,但有一项靠推断,或轻度反讽而不翻结论。
  - `low` = 命中任一 §6 borderline 触发。**`borderline=true` ⟺ `confidence=low`**。
- **metadata(`voted_up` / `votes_funny` / `received_for_free` / `steam_purchase` / …)**:**与正文一起进入人工标注与模型推理(人机同权,§4.0)**,主要供 §5-F 反讽/立场交叉验证。**规则:metadata 可升降警觉,但标签一律从正文定;metadata 单独绝不触发 PRESENT/ABSENT。**

---

## 7. 每条 gold 标注要落的字段(采参考文献 §10)

```text
review_id
language               # en | zh | ja
unfair_label           # PRESENT | ABSENT | NA   ← 主标签(§2);NA=out_of_scope,导出训练/评估时排除
out_of_scope           # true | false        ← 先判(§3);true ⇒ unfair_label=NA
evidence_span          # 支撑判断的原文摘录(review-level,非独立 span 任务;PRESENT 须含规范线索,§4.0)
normalized_claim       # "评论者认为 X 不公平,因为 Y"(SBIC 式);PRESENT 必写;ABSENT 仅 borderline=true 时必写"为什么不算"(§8-Q6);NA 留空
subtype                # list ⊂ {distributive, procedural}(§4;PRESENT 必有值;rev5 取消 other)
procedural_facet       # list ⊂ {cheating_governance, sanction, access_exclusion, competitive_balance, unfair_by_design}(§4.2.1,显式标注;每条 PRESENT-procedural 都填)
explicitness           # explicit | implicit   ← 仅 PRESENT 填,其余留空(§6.1 空值规则)
confidence             # high | medium | low   ← 对最终标签的把握(§6.1)
borderline             # true | false(§6)
uncertainty_reason     # borderline=true 时必填;取 §6.0 枚举(可分号组合),不写泛化文字
annotator_note
original_label         # 独立判断,冻结后不改(Davani/CAD)
adjudicated_label      # 裁决后;与 original 分开存
adjudication_reason
codebook_version       # 例:v1-draft-rev6 →(冻结后)v1.0   ← 防 holdout 泄漏(§8-Q5)
annotator
```

> **红线(与 `data_split_spec.md` §5 一致)**:人工标注在看到模型结果**之前**冻结,之后不改;`original / adjudicated` 分开存;gold 永不进训练。**导出训练/评估集时排除 `unfair_label=NA`(out_of_scope)行——NA 不是负例(§3)。** **metadata(§4.0 那组、不含作者身份)与正文一同喂给人工标注与模型推理。**

---

## 8. 需要 Yifan 拍板的开放问题(审阅时逐条决定)

- **~~Q1 子类要不要留全四个?~~ 已决(2026-08-06 / rev5 收尾):折叠为 `distributive` + `procedural`,并取消 `other`。** 依据:pilot_draft 里 interpersonal/informational 无独立实例,rev5 复核仅有的两条为质量/修辞吐槽→ABSENT(§0.2、§4、§9)。
- **~~Q3 区域定价愤怒算 distributive 还是排除?~~ 已决:算 `distributive`。** 判据:评论指向**日本/某区被差别定价**(おま国/おま値、"世界一高い"),即"差别获取/负担",归 distributive;单纯"太贵"仍走 §5-B 排除。
- **~~Q2 反作弊/平台排除算不算 unfair?~~ 已决(2026-08-08):算 `procedural` + `access_exclusion` facet。** 判据:凡**按平台/硬件排除一类玩家**或**筛掉玩家使其无法进场**且带规范线索即算(§4.2.1)。
- **~~Q4 玩家 toxicity 何时归到开发方?~~ 已决(2026-08-08):默认 `ABSENT`**(玩家对玩家不算本构念,§1.1-B);**唯一例外**——评论明确指认"官方纵容/机制鼓励"时升级 `procedural`(§5-E)。
- **~~Q5 版本号命名~~ 已决(2026-08-08):两段式。** `v1-draft-rev{n}` →(冻结)`v1.0` →(冻结后**能翻转任一标签**的实质改动)`v2.0` + 重标 gold+LLM;纯编辑性 = `v1.0.x` 不重标;**拿不准一律当"实质"**。冻结后 v1.0 永不原地改。
- **~~Q6 `normalized_claim` 对 ABSENT 写不写~~ 已决(2026-08-08):** PRESENT 必写;ABSENT **仅 `borderline=true` 时必写**"为什么不算";NA 留空。
- **~~Q7 算不算非竞争性内容/皮肤付费墙?~~ 已决(2026-08-08):不算。** distributive 只收竞争优势 / 影响玩法的内容·准入 + 差别定价;纯外观/非玩法货币化怨气 → ABSENT(§4.1 构念范围)。
- **~~Q8 何时可以声称"跨语言"?~~ 已决(2026-08-10):5 条件 + 操作门槛。** 一个 facet/构念可声称跨语言,须同时满足:
  1. **各语言都存在**:EN/ZH/JA **每种各 ≥3** 条独立 PRESENT(操作门槛,Yifan 定;合计 ≥15 不能替代)。
  2. **与单一游戏/社区解绑**:该 facet 覆盖 **≥2 款游戏**(否则只是某作特产,§4.2.1 game locus)。仅此项过,才可从"该作内跨语言"升为"语言普适"。
  3. **同一构念、允许语言特定线索**(测量等价):三语识别的是同一个规范违反,只是表面线索可不同(如日语靠"理不尽/一方的",中文靠"官匹/读指令",英文靠"input reading/paywall")。
  4. **每语言各自可靠**:单人跨语言判准不漂移(§9 缺口2 的 intra-rater 检验覆盖三语)。
  5. **决策边界一致**:同一条规则(如 §4.0 正例门槛、§5 各反例)在三语给出一致取舍,不是某语言偏松偏紧。
  - **rev6 实测结论(§4.2.1)**:按条件 1+2,当前唯一同时满足的是 `cheating_governance`(三语各≥3 且 BF+CS2 两游戏);`sanction` 跨语言但 BF 主导;`unfair_by_design`、`competitive_balance` 跨语言但单游戏(法环 / BF)→ 只能称"该作内跨语言";`access_exclusion` 当前 EN·ZH 双语(JA 稀疏)。

---

## 9. 冻结前要闭合的缺口:分两类

> **rev7 更正**:旧 §9 把"补样披露 / facet 决策 / metadata / 跨文件一致"都算成"从参考文献继承的遗留缺口",不准确——**只有单人三语一致性方法**是真正的文献来源问题;其余都是**本项目自己的冻结质量门槛**。故分两节。

### 9.1 文献来源限制

- **单人三语标注一致性方法缺文献** → 本项目 gold 为一人标 EN/ZH/JA,主威胁是**同一标注者跨语言判准漂移**,会与"模型在某语言更差"混淆。需自行设计 intra-rater(test–retest)检验并在冻结前定稿(方案见 §9.3 表)。**本 codebook 冻结的前置条件之一 = 这个检验方案有了**(也是 §8-Q8 条件4 的依托)。
- **~~Freeman(2022)逐码定义表~~ 已按范围决定关闭(rev7,Yifan 定):** 反复检索仍拿不到 Freeman 的逐码 inclusion/exclusion 定义表。**决定:明确声明 Freeman 仅用于提供研究背景与 sensitizing concepts;本项目所有实际标签边界均由本项目独立定义、用开发集(pilot/dev)验证。** 因此它**不再是"待闭合的冻结缺口"**——本项目从不依赖 Freeman 的编码规则,自然无需补齐。措辞红线:可说"两子类方向与 Freeman 的概念分布一致",不得说"照其编码"或"facet 由 Freeman 验证"。

### 9.2 项目自己的冻结质量门槛(不是文献缺口)

1. **多批目的性(非随机)补样须披露** → §4.1 部分 distributive 例子、§4.2.1 的 `support_volume` 计数,均含**关键词种子抽样**(三批 provenance:`_purposive_distributive.csv` 18 / `_purposive_procedural.csv` 44 / `_purposive_crosslingual.csv` 20)。对**起草与 support_volume 计数**合法(pilot_draft 不参与测量),但方法学描述须**明确披露**"经目的性过采样,**合计数不反映真实分布**",尤其 **facet 的三语/游戏计数是补样后的,不能读成自然分布**。**gold 仍须随机、按真实分布抽;补样 id 对 gold 不可见(后减前)。**
2. **facet 分类学只在 pilot 上定,绝不用 gold** → 5 个 facet 均在 `pilot_draft` 上按**四描述维度 + `taxonomy_status`** 评估,**绝不用 gold**(否则 gold 反向塑造 taxonomy = holdout 泄漏)。当前 `taxonomy_status`:cheating_governance/sanction/unfair_by_design = **core**;competitive_balance/access_exclusion = **exploratory**(证据薄,如实标注)。**gold 冻结后只把 facet 照定义套上、报告计数与 locus,不回改分类。**
3. **anchor 三件套完整性** → 见独立 `anchor_catalog`(§4.2.1;完整原文 + span + claim + 逐例裁定理由存 catalog,codebook 正文只留 ID 指针)。
4. **`uncertainty_reason` 枚举落地** → 19 条旧 borderline 的泛化原因在人工验证一遍时改到 §6.0 枚举(不机械批改)。
5. **跨文件一致性** → codebook / `data_split_spec.md` / `decision_log.md` / 计数脚本口径一致(rev7 已同步:pilot 规模 353、脚本去 `other`、脚本输出 `taxonomy_status`)。

### 9.3 冻结缺口闭合表(过了才谈 v1.0)

| 缺口 | 冻结前行动 | 通过标准 | 未通过怎么办 |
|---|---|---|---|
| 独立 codebook 盲检 | 用**未参与起草**的 pilot 子集建 `codebook_check` / `facet_check`,盲标一遍 | 主标签与 facet 自洽度达**预登记**阈值 | 修规则、补反例,再盲检 |
| 单人跨语言漂移 | test–retest:T1 → 隔 10–14 天 → 藏旧标 → 重新随机顺序 → T2;**轮换三语顺序** | 报 raw agreement / Cohen's κ / 混淆矩阵 / PRESENT-ABSENT specific agreement;阈值**预登记** | 漂移大的规则重写并重测 |
| 补样披露 | 方法学文档写明三批目的性补样、合计数非自然分布 | 读者能区分"开发样本覆盖"与"真实频率" | 补写披露 |
| facet 状态 | 记录 core/exploratory/folded + locus | 每 facet 状态与证据一致、可复核 | 降级或并回 procedural |
| anchor+字段完整 | `anchor_catalog` 每 facet×语言含正例 / hard negative / borderline 的完整原文 + span + claim + 裁定理由 | 每个被引用 anchor 三件套齐全 | 补齐或撤下该 anchor |
| metadata / 输入 schema | 定死喂给标注与模型的 metadata 字段(不含身份)+ 一个 text-only 对照 | 人机输入对等、有 text-only 基线 | 补齐 parity |
| 文件 / 版本一致 | codebook / spec / log / 脚本口径统一 | 无交叉矛盾 | 同步 |

> **正确流程顺序**:目的性 `pilot_draft` 起草规则 → **冻结候选版** → 新建 `codebook_check` 盲检 + test–retest → **通过后才冻结 v1.0** → **才**开始抽随机 gold。**冻结在前,gold 在后。**

> **冻结前工件(2026-08-10 备齐,待 Yifan 批准)**:
> - 预登记(阈值锁死):`freeze/preregistration.md`(#1 盲检 κ≥0.60、#2 test–retest κ≥0.60 且三语落差≤0.15、anchor 密度)
> - 输入 schema 冻结:`freeze/input_schema.md`(人机 metadata 同权 + text-only 基线)
> - anchor 补齐:`scripts/03e`(每 facet 正例+hard neg+borderline,27 条)→ 审阅表 `freeze/anchor_review_sheet.md`(本地);**缺口** unfair_by_design/borderline 待指定
> - 检验脚本:`scripts/04a_retest.py`(test–retest)、`scripts/04b_codebook_check.py`(独立盲检),build 已产盲标空表,`score` 待填后跑
> - **长杆**:test–retest T1→T2 需隔 10–14 天,v1.0 冻结日期受此约束

---

## 10. 版本说明

- `v1-draft`(2026-08-06,Claude 起草):首版框架。构念定义 + 二元主标签 + out_of_scope 闸门 + 四子类种子 + exclusion 目录 + 标注字段 + 开放问题。
- `v1-draft rev2`(2026-08-06):四子类折叠为两子类 `distributive` + `procedural`;`distributive` 三语目的性补样(+18,pilot_draft→288)。
- `v1-draft rev3`(2026-08-08):`out_of_scope` 改判 `NA` 三值;`procedural` 加 `procedural_facet` 子层(5 临时 facet,三语合计 ≥15 才留);作者立场闸;subtype tie-breaker + `other` 值 + 正例三件套门槛;反讽三步;"minimal pair"→ contrastive pair;§8-Q2/Q4 已决。
- `v1-draft rev4`(2026-08-08):facet 去留**只用 pilot_draft**(去 gold);立场闸拆"已撤回"vs"已解决";access_exclusion 收紧为服从 §4.0;facet PvE/PvP 切分(balance_rng→competitive_balance);distributive 锚点重审;Q5/Q6/Q7 已决;补 explicitness/confidence/metadata 操作定义。
- `v1-draft rev5`(2026-08-09):**取消 `other` 子类**——rev3 用 `other` 兜的两条稀有人际/信息不公,复核为质量/修辞吐槽 → 判 ABSENT;subtype 值域收敛为 {`distributive`, `procedural`};**误导性付费墙**(如 `140004357`)由 `other` 并入 `distributive`。
- `v1-draft rev6`(2026-08-10,Claude,回应 Yifan 三条决定):
  1. **facet 去留改"两轴分别报告"**:轴1 KEEP/FOLD(合计≥15)与轴2 跨语言(每语言≥3)+ game locus,**正交、互不覆盖**(§4.2.1)。
  2. **目的性补样加大 pilot**:procedural(02a4,+44)+ 跨语言补缺(02a5,+20,专填每 facet 缺的语种),pilot_draft→**353**;三批 provenance 全披露(§9 缺口3)。
  3. **每 facet 标 locus + rev6 计数/裁定**:cheating_governance 跨语言且跨游戏(最强);sanction 跨语言但 BF 主导;unfair_by_design 跨语言但法环特定;**competitive_balance【决定 A】保留**(轴2 3/3/3 达标,轴1 偏少 + BF 单游戏如实注明);**access_exclusion【决定 B】保留为完整(潜在三语)facet**,JA 当前仅 1 条为真实稀疏,注明 under-attested,唯真的一条日语都无时才降为双语。
  4. **§8-Q8 成文**:跨语言声称 5 条件 + 操作门槛(每语言≥3、≥2 游戏)。
  5. **metadata 人机同权**(§4.0):同组 metadata 与正文一起进入人工标注**与**模型推理。
  6. **explicitness/confidence 空值与定义收严**(§6.1):explicitness 仅 PRESENT 填;confidence = 对最终标签的把握。
  7. **Freeman 实证措辞收敛**(§9 缺口1):方向一致,不声称"照其编码"或"facet 经 Freeman 验证"。
- `v1-draft rev7`(2026-08-10,Claude,回应外部评审第三轮 + Yifan 三条范围决定):
  1. **facet 去留改描述框架**(§4.2.1):不再叫 KEEP/FOLD;四描述维度(`support_volume` / `language_coverage` / `title_coverage` / locus)+ 处置状态 **`taxonomy_status`(core/exploratory/folded)**,**阈值只描述、状态才裁决**,消除"客观阈值被人工例外覆盖"的自相矛盾。
  2. **轴1 阈值正名**(§4.2.1、§9.2):"频率" → **开发样本覆盖门槛**;明确合计数非自然频率,真实频率只由随机 gold 报告。
  3. **跨语言/稀疏措辞转保守**(§4.2.1):access_exclusion 日语从"真实稀疏"改为"**当前证据不足,无法区分实际稀疏 / 机制差异 / 召回不足**";删去 secure-boot"西方+中文现象"断言;"语言普适"降为"在 ≥2 游戏观察到"。
  4. **人际/信息类彻底移出范围**(§1.1,Yifan 定):(A) 不再列这两类;**不设兜底 / 安全阀**,纯人际/信息吐槽 = ABSENT。
  5. **Freeman 降为 sensitizing-only**(§9.1,Yifan 定):只作研究背景 / 概念启发,标签边界全由本项目独立定义 + 开发集验证;**不再列为冻结缺口**。
  6. **`uncertainty_reason` 定枚举**(§6.0):7 值受控词表;19 条旧泛化值在人工验证一遍时改判(不机械批改)。
  7. **`anchor_catalog` 独立成文**(§4.2.1、§9;脚本 `03e`):完整原文 + span + claim + 裁定理由入 catalog,正文只留 ID。
  8. **§9 拆两节 + 闭合表**:9.1 文献来源限制(只剩单人三语一致性)/ 9.2 项目冻结门槛 / 9.3 冻结缺口闭合表。
  9. **跨文件同步**:`data_split_spec.md` pilot 规模 353 注记、`03c` 去 `other` + 输出 `taxonomy_status`、`decision_log` supersede 注记。
  - **明确未做**(Yifan 定):不对 competitive_balance 的 P2W 例子补打 `distributive`(避免额外标注复杂化)。
- **下一步仍不是冻结**,是:在 EN/ZH/JA 各自 pilot → 闭合 §9.3 缺口(单人跨语言漂移 test–retest / 独立 `codebook_check` 盲检 / anchor_catalog 补齐;Freeman 已按范围关闭、facet 分类学已在 pilot 完成)→ **通过后才谈冻结为 `v1.0`,冻结在前、随机 gold 在后**。§8 开放问题 Q1–Q8 现已全部拍板。
- 冻结后任何规则改动 = `v2`,并触发 gold + LLM 重标(见 `decision_log.md`)。
