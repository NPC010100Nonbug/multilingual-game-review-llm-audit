# Steam 三语评论「感知到的不公平」标注手册 v0.1（草稿）

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Origin Mode: `plan`
- Origin Date: `2026-08-06`
- Verification Status: `UNVERIFIED`
- Version Label: `codebook_v0.1-draft`
- Evidence Used: `codebook_framework_references.md`；`pilot_draft` 135 条（英、中、日各 45 条）
- Evidence Not Used: `pilot_prompt`、`gold`、`dev`、`train`、任何模型预测

> **状态警告**：这是用于人工试标和发现规则漏洞的第一版，不是冻结版。它不能直接被描述为“已验证的多语言 Steam perceived-unfairness codebook”，也不应在完成 pilot 修订前用于正式 gold 标注。

## 1. 研究问题与标注对象

本项目判断的是：

> **一条 Steam 评论是否表达、认同或清楚暗示了评论者对某项公平规范被违反的感知？**

标注对象是评论文本中的**主观感知**，不是对游戏、开发者或算法的客观事实裁决。`PRESENT` 只说明“评论者把某种体验理解为不公平”，不说明该指控已经被外部证据证实，也不说明相关行为违法、故意或客观不公。

### 1.1 Coding unit

- 基本单位：一条完整 Steam review，包括后来追加的更新文字。
- 证据单位：支持主标签的最短连续原文片段（`evidence_span`）。
- 一条评论可含多个问题；只要其中至少一个问题满足 `PRESENT`，整条评论的主标签就是 `PRESENT`。
- 推荐/不推荐、星级、游戏时长、投票数、作者资料均不参与主标签判断。
- 标注者不得为了判断某条评论而搜索游戏事实、补丁历史或作者背景；只判断文本中表达的 perception。

## 2. 核心构念的概念定义

### 2.1 Perceived fairness（感知到的公平）

评论者认为游戏中的结果、规则、程序、待遇、信息、交易条件或参与机会，符合某个可识别的正当期待、比较基准或应得关系。

上层概念来自三组文献：

1. **Justice 维度**：结果分配、程序、人与人之间的待遇以及信息解释可以分别成为公平判断的对象（Colquitt, 2001；Smith, Bolton, & Wagner, 1999；Blodgett, Hill, & Tax, 1997）。
2. **程序标准**：一致、无偏、基于准确信息、可纠错、考虑相关方利益与伦理，是可能被评论者诉诸的程序规范（Leventhal, 1980）。
3. **交易与价格公平**：不公平判断需要价格、条件、承诺、参照交易或应得关系；“贵”“不值”或低质量本身不等于不公平（Xia, Monroe, & Cox, 2004；Kahneman, Knetsch, & Thaler, 1986；Bolton, Warlop, & Alba, 2003；Zeithaml, 1988）。

### 2.2 Perceived unfairness（感知到的不公平）

本项目的操作性定义为：

> **评论者自己采纳了一项评价性主张：某个结果、规则、机制、程序、待遇、信息、交易或参与条件，违反了可从文本中识别的公平规范、合理期待、比较基准、应得关系或机会平等。**

该定义要求同时出现两个组成部分：

- **公平基准**：例如同一规则应一致适用、胜负应主要由技能决定、付费内容不应给予不正当优势、处罚应有依据并可申诉、购买者应获得承诺的产品、不同玩家不应因可避免的技术安排承受系统性劣势。
- **违反关系**：评论者明确说或清楚暗示上述基准被破坏，而不是只表示不开心、困难、失败、昂贵或有 bug。

游戏语境的具体映射来自 Freeman et al. (2022)、Petrovskaya & Zendle (2022)、Petrovskaya, Deterding, & Zendle (2022) 和 Hirota & Kuribayashi (2011)，但这些研究只覆盖竞技、公平商业化、微交易或网络条件的部分情形，不能被当作本项目全部子类已经验证的证据。

### 2.3 与相邻概念的边界

| 相邻概念 | 与本构念的关系 | 默认判断 |
|---|---|---|
| 负面情绪、辱骂、愤怒 | 可能与不公平共同出现，但不是公平判断本身 | 单独出现为 `ABSENT` |
| Complaint / 抱怨 | 范围更宽；bug、等待、难度、失望都可以是抱怨 | 没有公平基准与违反关系时为 `ABSENT` |
| 高难度或失败 | 难不等于不公平 | 只有文本指向任意、双重标准、无反制或规则不对等时才可能 `PRESENT` |
| Bug、崩溃、低帧率、服务器差 | 技术故障不自动构成公平问题 | 只有造成文本明确/隐含的差别机会、排斥或不平等待遇时才可能 `PRESENT` |
| 高价格、低价值 | 价值评价不等于 price unfairness | 只有不合理比较、欺骗、强迫、破坏承诺或付出—交付规范被违反时才可能 `PRESENT` |
| 游戏平衡意见 | “我不喜欢这个数值”不等于公平判断 | 指向不正当优势、单方面规则、无反制或付费优势时才可能 `PRESENT` |
| 客观真实性 | 本项目不核实评论者说法是否事实 | 只标其是否表达 unfairness perception |

## 3. 主标签

### 3.1 `PRESENT`

**简短定义**：评论者表达、认同或清楚暗示至少一项公平规范被违反。

**必须满足**：

1. 评论者在当前文本中**采纳**该主张，而不是只引用、转述或否认别人说“不公平”。
2. 可以从文本中写出一句最低限度的 `normalized_claim`：

   > 评论者认为【对象/机制/主体】不公平，因为【被违反的规范、期待、比较或机会】。

3. `evidence_span` 必须能支持这句话；不能主要依靠标注者的游戏常识补全。

**典型 inclusion routes**：

- 不同玩家、阵营、地区、平台或付费群体被置于不对等的规则、机会、负担或待遇中。
- 作弊、漏洞滥用、P2W、付费跳过或压倒性购买优势破坏了本应由技能/策略决定的竞争。
- 机制、RNG、数值或难度被描述为任意、双重标准、单方面、不可反制，或给一方不正当优势。
- 付款、承诺与实际交付之间存在文本可识别的欺骗、强迫、价格掩蔽、拆分售卖、破坏既有承诺或不合理差别条件。
- 封禁、举报、匹配、退款、申诉或补丁程序被描述为无依据、有偏、一致性不足、无法纠错或缺乏说明。
- 官方/客服被描述为欺骗、故意隐瞒、侮辱、漠视或不给合理解释；必须体现公平待遇或信息规范，而非一般“服务差”。
- 技术或接入安排使特定群体持续处于不平等机会或被排除，且评论文本建立了这种差别关系。

### 3.2 `ABSENT`

**简短定义**：评论中没有足够文本证据显示评论者采纳了公平规范被违反的主张。

包括：

- 正面、中性或与研究问题无关的评价。
- 单纯的负面情绪、辱骂、讽刺、后悔或“不推荐”。
- 单纯说难、输、死得多、武器弱、地图差、内容少、玩家少。
- 单纯说贵、不值、想退款或打折才买。
- 单纯说有 bug、崩溃、卡顿、掉线、无法启动、服务器差。
- 只提到封禁、反作弊、匹配或付费机制，但没有表达它们无依据、有偏、不一致、给出不正当优势或违反承诺。
- 引用“有人说它不公平”但评论者不认同或未表态。
- 关键词出现于游戏名、梗、链接、复制文本或无法理解的片段中。

`ABSENT` 不是“评论者认为公平”，只表示**当前文本不足以证明其表达了不公平感知**。

### 3.3 `NA`：非第三类，而是不可进入任务的记录

主任务仍是二元分类；`NA` 只在 `eligibility = OUT_OF_SCOPE` 时使用，不能送入模型训练或正式指标。

`OUT_OF_SCOPE` 包括：

- 没有可解释语义的乱码、纯链接、纯数字、单个无关符号或广告。
- 抽样语言与实际文本语言完全不符，且没有足够目标语言内容支持判断。
- 文本截断或编码损坏到无法判断作者主张。
- 评论内容与游戏体验完全无关。

短评不是自动越界。例如只有一个明确、由作者采纳且指向本游戏的 “rigged / 不公平 / 理不尽” 仍可进入任务，但应提高 `uncertain` 并使用 `other_unspecified`，除非上下文足以判断子类。

## 4. 五步判定流程

每条评论按固定顺序判断，不能从关键词直接跳到标签。

1. **资格**：是否存在可解释、与游戏体验有关的评价？语言是否符合该语言样本？否则 `OUT_OF_SCOPE → NA`。
2. **作者立场**：评论者是在主张/认同，还是在引用、否认、反讽别人关于不公平的说法？只有前者继续。
3. **公平基准**：能否从文本识别“什么本来应该一致、对等、合理、可解释、可纠正或按承诺交付”？
4. **违反关系**：评论者是否明确说或清楚暗示该基准被破坏？第 3、4 步必须同时成立才是 `PRESENT`。
5. **证据与属性**：摘录最短证据，写 `normalized_claim`，选择 subtype、explicitness、confidence、uncertain 和 hard-negative 属性。

若在第 3 步无法写出公平基准，默认 `ABSENT`；不要为了“看起来像抱怨”而替作者补写。

## 5. 辅助 subtype（仅用于误差分析，可多选）

Subtype 不替代主标签；先判 `PRESENT/ABSENT`，再选 subtype。`ABSENT` 不应被强行分配 unfairness subtype。

| subtype | 完整定义与 inclusion | exclusion / tie-breaker | 合成示例 |
|---|---|---|---|
| `competitive_integrity` | 竞争胜负机会因作弊、外挂、恶意漏洞、P2W、不公平匹配、队伍/阵营系统性不对等而被破坏 | “我输了”“对手很强”“匹配慢”不算；普通武器平衡优先放 `mechanism_outcome_balance`，除非文本强调对战机会 | “每场都有外挂，举报后也没人处理，正常玩家根本没有同等获胜机会。” |
| `mechanism_outcome_balance` | 游戏规则、AI、RNG、数值、难度、奖励或 nerf 被描述为任意、双重标准、单方面、无反制或付出与结果不成比例 | “boss 很难”“某武器弱”“我不喜欢改动”不算；付费造成的不对等同时加 `monetary_exchange` | “敌人保留原技能，玩家同一技能却被单方面削弱，而且没有替代反制。” |
| `monetary_exchange` | 价格、微交易、DLC、退款、付费内容或交付条件违反公平交易、承诺、透明或机会规范；含 P2W、pay-or-grind、诱导/强迫消费 | “太贵”“不值”“打折可买”单独为 `ABSENT`；若重点是退款程序，也可同时加 `procedural_governance` | “宣传为完整内容后，发售时把已承诺部分拆成额外付费 DLC。” |
| `procedural_governance` | 封禁、举报、匹配、申诉、退款、审核、补丁或社区治理被描述为无依据、有偏、不一致、不可纠错或不给合理解释 | 单纯“被封了”“客服慢”“不喜欢补丁”不足；必须指向程序规范 | “没有作弊却被封，申诉只有自动回复，也不给任何证据。” |
| `access_technical` | 技术、平台、地区、网络或接入安排造成特定群体持续被排斥或处于不平等机会 | 一般卡顿、崩溃、低帧率和无法启动为 `ABSENT`；只有文本建立差别群体/机会关系时才进入 | “同一服务器只让某地区玩家长期承受额外延迟，使他们在对战中必然吃亏。” |
| `other_unspecified` | 主标签明确为 `PRESENT`，但现有 subtype 无法可靠覆盖，或短评只明确说“不公平”而未给机制 | 不得作为省事的默认项；必须填写 `annotator_note`，其比例过高说明 taxonomy 需要修订 | “这套规则就是不公平。”（没有更多上下文） |

关于人与人之间的尊重和信息解释：v0.1 暂不另设稀疏 subtype。客服侮辱、官方隐瞒或误导可按具体机制进入 `procedural_governance` 或 `monetary_exchange`，并在 `annotator_note` 标记 `interpersonal` / `informational`。若 pilot 反复出现，再在 v0.2 拆出独立类别。

## 6. Explicitness、confidence 与 uncertainty

### 6.1 `explicitness`

- `explicit`：评论者直接使用公平判断词或清楚的规范词，如 unfair、rigged、double standard、scam、deserved/undeserved、不公平、偏袒、双标、坑人、无缘无故、理不尽、えこひいき、詐欺、理由なく。
- `implicit`：没有这些词，但公平规范与违反关系从文本直接可恢复，例如“没作弊却被封且不给申诉”“付钱后才把已承诺内容锁起来”。

关键词只是 anchor，不是自动标签。词被引用、否定、用于无关对象或没有作者立场时仍可为 `ABSENT`。

### 6.2 `confidence`

- `high`：作者立场、公平基准和违反关系都直接清楚，几乎不需补充推断。
- `medium`：存在一个合理的隐含公平关系，但可能有一个相邻解释。
- `low`：至少两种同样合理的解释，或关键主语、对象、讽刺方向、语言含义不稳定。

### 6.3 `uncertain`

`uncertain` 是单独的过程字段，不是第三种主标签。标注者仍须按当前规则给 `PRESENT` 或 `ABSENT`，并选择原因：

- `implicit_norm`
- `sarcasm_or_irony`
- `missing_context`
- `language_or_translation`
- `scope_boundary`
- `multiple_plausible_readings`
- `subtype_unclear`
- `other`

`confidence=low` 时通常应 `uncertain=true`；反之不强制。

## 7. Hard negatives 与最小对照

Hard negative 是**情绪上很负面、措辞很像正例，但按构念定义仍为 `ABSENT`** 的评论。它们用于避免模型学成“负面情绪检测器”。组织方式借鉴 HateCheck 的 contrastive test，但真实 gold 仍必须来自真实 Steam 评论，合成句只能作为独立诊断材料。

| hard_negative_type | `ABSENT` 合成例 | 与其对应的 `PRESENT` 最小对照 |
|---|---|---|
| `difficulty_only` | “这个 boss 太难了，我死了五十次。” | “这个 boss 对玩家和 AI 使用两套规则，玩家没有任何反制窗口。” |
| `technical_failure_only` | “一直掉帧和崩溃，体验很差。” | “只有某平台玩家被强制到高延迟服务器，因此对战机会明显更差。” |
| `price_value_only` | “太贵，不值这个价。” | “先承诺包含该模式，收款后又把它拆成额外付费内容。” |
| `negative_sentiment_only` | “垃圾游戏，我恨它。” | “举报外挂从不处理，正常玩家只能在被操纵的对局里输。” |
| `failure_only` | “我总是输，队友也很差。” | “系统把新手固定匹配给高段位队伍，双方机会从一开始就不对等。” |
| `generic_balance_dislike` | “我不喜欢这次武器削弱。” | “只有玩家版被削弱，敌人相同技能不变，且没有替代机制。” |

真实 pilot 中若发现近似对照，应记录 `contrast_id`。合成对照不进入 prevalence、训练集或正式 gold 指标。

## 8. 重要边界规则

1. **作弊**：文本肯定作弊真实存在并影响对局时，通常可视为隐含的 `competitive_integrity / PRESENT`；只是谈论反作弊软件、转述作弊争议或说“没遇到外挂”不是正例。
2. **封禁与红信/信誉系统**：只有“无依据、没做错、偏袒、不给证据/申诉”等程序违反关系才是 `PRESENT`；“我被封了”本身不足。
3. **难与理不尽**：日语 `理不尽`、英语 `unfair`、中文“不公平”仍需检查指向和作者立场。若它们直接评价游戏机制，即可成为正例证据；若只是梗、引用或无关用法则不算。
4. **“付了钱却……”**：付款与无法获得被承诺的基本产品/内容形成清楚交换规范时可为 `monetary_exchange / PRESENT`；只有“我付了很多、我后悔”仍为 `ABSENT`。
5. **历史问题已修复**：若评论仍把过去经历描述为公平规范被违反，标 `PRESENT`；若作者明确撤回原判断（如“后来发现是我的设置，不是游戏区别对待”），按最终采纳的立场判断。
6. **反讽与修辞问句**：判断作者实际采纳的命题；无法稳定恢复时保守给当前最合理二元标签，并设 `uncertain=true`。
7. **混合评论**：正面总体评价不抵消其中明确的不公平主张；同样，负面总体评价也不会自动创造不公平主张。
8. **语言错配**：记录 `language_match = match | mixed | mismatch`。完全错配设 `OUT_OF_SCOPE/NA`，不把中文评论算作日语 gold；从同一预定抽样层的候补顺序补位并保留排除日志。
9. **外部知识**：不能因为标注者知道某武器“确实 OP”、某公司“经常封错人”就补成 `PRESENT`。
10. **关键词优先但不决定**：关键词可用于开发期召回候选正例，不能用于正式标签自动赋值，也不能据此估计 prevalence。

## 9. 每条标注的字段

### 9.1 必填核心字段

| 字段 | 取值/格式 | 规则 |
|---|---|---|
| `review_id` | Steam recommendation id | 唯一键 |
| `appid` | `730 / 1517290 / 1245620` | 仅用于分层与误差分析 |
| `lang_sampled` | `en / zh / ja` | 抽样所在语言格 |
| `language_match` | `match / mixed / mismatch` | 由文本实际语言判断 |
| `eligibility` | `IN_SCOPE / OUT_OF_SCOPE` | 先于主标签 |
| `out_of_scope_reason` | 枚举或空 | 越界时必填 |
| `unfair_label` | `PRESENT / ABSENT / NA` | `NA` 仅用于越界，不是第三类 |
| `evidence_span_text` | 原文最短片段或空 | `PRESENT` 必填；只保存在本地 |
| `evidence_start` / `evidence_end` | 字符偏移 | 对未经改写的原始 `review` 字段按 Unicode code point 计数，使用 0-based 半开区间 `[start, end)`；可公开并指回可重建文本 |
| `normalized_claim` | 一句释义或空 | `PRESENT` 必填，不得添加文本没有的意图或事实 |
| `subtype` | 上述列表，多选 | `PRESENT` 必填；无法归类用 `other_unspecified` |
| `explicitness` | `explicit / implicit / NA` | `PRESENT` 填写 |
| `confidence` | `high / medium / low` | 所有 in-scope 评论填写 |
| `uncertain` | `true / false` | 不改变二元主标签 |
| `uncertainty_reason` | 枚举或空 | `uncertain=true` 时必填 |
| `hard_negative` | `true / false` | 仅 `ABSENT` 可为 true |
| `hard_negative_type` | 枚举或空 | hard negative 时填写 |
| `annotator_note` | 简短说明或空 | 只记录规则相关信息，不写作者身份推测 |
| `codebook_version` | 如 `v0.1` | 每条都必须绑定版本 |

### 9.2 过程与裁决字段

| 字段 | 用途 |
|---|---|
| `annotator_id` | 使用稳定匿名 ID，如 `human_01` |
| `annotation_round` | `pilot_r1 / pilot_r2 / gold_t1 / gold_t2 / adjudication` |
| `original_label` | 保留每一轮独立判断，不覆盖 |
| `adjudicated_label` | 发生复标分歧后形成的最终标签 |
| `adjudication_reason` | 指向具体规则或新增规则 |
| `adjudication_date` | 记录裁决时间 |
| `contrast_id` | 真实 hard negative 对应的正例 ID；没有则空 |
| `source_role` | `pilot_draft / pilot_prompt / gold / dev / train`，用于防泄漏 |

隐私规则：公开仓库不提交原始 review、作者资料或本地 `evidence_span_text`。公开标签若需证据定位，优先保存 review_id 与字符偏移；`normalized_claim` 公开前需检查是否复述了可识别信息。

## 10. 未来的数据标注方法

### 阶段 A：用完整 `pilot_draft` 修订 codebook

1. 人工标注者阅读 v0.1 后，**独立标完现有 135 条 `pilot_draft`**；不查看 AI 建议、`pilot_prompt` 或模型输出。
2. 先完成第一轮，再由 AI 按同一 v0.1 对这 135 条给出独立标签。两者分歧只用于发现定义漏洞，不能当作正式可靠性或模型准确率。
3. 按语言、游戏、主标签、subtype、hard-negative 类型和越界原因建立 coverage matrix。
4. 当前随机 pilot 中正例和部分 subtype 预计稀少。不得删掉随机样本或用定向样本替代它；应**额外增加一个 positive-enriched development supplement**：用多语言高召回关键词/机制词召回候选，再由人工按 codebook 判断。
5. 定向补充只用于边界发现，不估计真实比例，不进入 gold，不进入正式训练。继续以小批次追加，直到连续两批不再产生新规则；这是本项目的工作性停止规则，不是文献中的普遍阈值。
6. 把每个分歧归为：定义含糊、inclusion 缺失、exclusion 缺失、语言表达差异、subtype 重叠、上下文不足或标注失误。修订为 v0.2，并保留版本变更记录。

此阶段结合了 MacQueen et al. (1998) 的 entry 结构、DeCuir-Gunby et al. (2011) 的理论驱动与数据驱动结合、O'Connor & Joffe (2020) 的独立 pilot—比较分歧—新样本重测流程，以及 GoEmotions 的多轮 taxonomy 修订思路。

### 阶段 B：跨语言规则适配

1. 使用同一上层构念与同一二元判定逻辑，不把英文关键词表直接翻译成中日文规则。
2. 分别整理 EN/ZH/JA 的显式表达、隐含表达、反讽、俚语和语言错配案例。
3. 允许语言特定例句和 lexical anchors；不允许语言特定的主标签定义。
4. 对等意义的三语 synthetic minimal pairs 可作为诊断集，但不进入 gold 或 prevalence。

这是对 Hershcovich et al. (2022) 跨文化适配风险的项目化处理；它不能证明三种语言的构念已经天然等价。

### 阶段 C：冻结 codebook，单独调试 LLM prompt

1. v0.2 达到可执行状态后提交 Git tag/commit，记录冻结日期与 hash。
2. 只在 `pilot_prompt` 上调 LLM 的指令、few-shot、输出 JSON、温度与解析规则。
3. `pilot_draft` 可作为 codebook 例子来源，但不能用来宣称 prompt 泛化表现；`pilot_prompt` 不得回流成为 codebook 的“成功例”。
4. 如果 `pilot_prompt` 暴露的是 codebook 本身的重大缺陷，允许退回修订，但已看过的 `pilot_prompt` 随即成为开发材料；必须另抽未见过的 `pilot_prompt_v2` 才能继续校准。
5. 在解封 gold 前，同时冻结 codebook 和 prompt。

### 阶段 D：人工 gold 标注

1. `gold` 从按游戏共同时间窗对齐后的目标总体中预先抽取，每种语言至少 100 条；不因预期类别稀少而故意缩小。
2. 标注界面隐藏 `voted_up`、模型预测、LLM 解释、作者资料和互动数；保留原文、必要的游戏名与语言。
3. 人工标注者按随机顺序完成 `gold_t1`，不看模型结果。
4. 由于当前是单人三语标注，不能报告 inter-rater reliability。为检测同一标注者跨时间漂移，建议在 2–4 周洗脱期后把**全部 gold** 重新随机排序并做 `gold_t2`；报告 test–retest raw agreement、Cohen's kappa、PRESENT prevalence 和混淆矩阵。该方法是针对当前限制的项目方案，参考文件已明确指出尚缺少直接对应文献，不能包装成已验证标准。
5. 保留 t1、t2 两轮原始标签。分歧逐条裁决，填写 `adjudicated_label` 和理由；不得覆盖原标签。
6. gold 中的 `OUT_OF_SCOPE` 按预先生成的同层候补顺序替换，并保留排除日志；不能人工挑选“更容易”的替代评论。
7. 如果看过 gold 后修改主定义、inclusion、exclusion 或 tie-breaker，该 gold 已被开发过程污染，必须从从未看过的 ID 重新抽取正式 gold。纯拼写修正且不改变判定可只升 patch 版本并记录。

若代表性 gold 的 `PRESENT` 很少，不得把已标 gold 改造成类别平衡集。可以增加 gold 总量，或另建明确标为 `diagnostic_challenge` 的正例/硬负例富集集合；两者的指标与用途必须分开报告。

### 阶段 E：LLM 弱标注训练集

1. 用冻结 prompt 对 `train` 生成弱标签，输出与人工表相同的主标签、证据、claim、subtype 和置信字段。
2. LLM 弱标签是训练信号，不是真值；所有解析失败、拒答、NA 和低置信案例都保留日志。
3. 不得根据 gold 得分反向修改 prompt、codebook、筛选规则或训练数据。模型选择只能使用 `dev`。
4. 是否过滤低置信弱标签必须事先写成实验条件，并在同一 dev/gold 上比较“全量”与“过滤”版本；不能为了得到更好结果事后删除难例。
5. 人工 gold 永不进入训练或 few-shot。

## 11. 质量控制与报告

最低报告内容：

- 每语言、每游戏的 `IN_SCOPE / OUT_OF_SCOPE / PRESENT / ABSENT` 数量。
- PRESENT prevalence，并说明是代表性 gold 还是定向 diagnostic。
- 主标签 raw agreement、Cohen's kappa、混淆矩阵；kappa 与 prevalence 一起解释，不能只报一个数。
- `uncertain`、`confidence` 和各 uncertainty reason 分布。
- 每个 subtype 与 hard-negative 类型的覆盖率。
- 所有 gold test–retest 分歧及裁决规则。
- codebook 版本、冻结 commit、标注日期、标注者数量与局限。
- 跨语言差异的三种可能来源：真实表达/构念差异、采样差异、同一标注者的语言判准漂移。

v0.1 不设置“达到某个 kappa 就自动通过”的普遍阈值。冻结应至少满足：没有未解决的主标签规则矛盾；每个已观察到的边界类型都有 inclusion/exclusion 或 tie-breaker；跨语言例子经过独立试标；版本和泄漏边界可审计。任何数值门槛若以后采用，必须在看正式 gold 结果前预先登记，并说明它是项目决策而不是文献共识。

## 12. v0.1 依据与证据边界

### 12.1 概念定义主要依据

- Colquitt (2001)、Leventhal (1980)：justice 维度与程序规范。
- Xia et al. (2004)、Kahneman et al. (1986)、Bolton et al. (2003)、Zeithaml (1988)：价格公平与一般价值评价的边界。
- Smith et al. (1999)、Blodgett et al. (1997)：消费者—企业场景中的结果、程序与互动公平。
- Freeman et al. (2022)、Petrovskaya & Zendle (2022)、Petrovskaya et al. (2022)、Hirota & Kuribayashi (2011)：竞技、商业化、微交易与网络机会中的游戏语境。

### 12.2 标注方法主要依据

- MacQueen et al. (1998)、DeCuir-Gunby et al. (2011)：code name、定义、inclusion、exclusion、例子和迭代字段。
- O'Connor & Joffe (2020)：预定 coding unit、独立 pilot、按分歧修订并在新样本重测。
- Röttger et al. (2022)、Davani et al. (2022)、Oortwijn et al. (2021)：prescriptive annotation、保留主观分歧与分开保存裁决。
- CAD、Social Bias Frames、HateXplain、X-CI：主标签、evidence、normalized claim/rationale 和属性字段分离。
- HateCheck：hard negatives、minimal pairs 与独立 diagnostic set。
- Hershcovich et al. (2022)：跨语言/跨文化适配不能退化成字面翻译。
- Gebru et al. (2021) 与 Hugging Face Dataset Card：标注过程、数据用途、限制与风险记录。

完整书目信息、链接、各来源可借用内容与不可外推边界见 [`codebook_framework_references.md`](./codebook_framework_references.md)。该参考文件是定向检索结果而非系统综述；尤其 Freeman et al. (2022) 的完整编码表尚未取得，单人三语 test–retest 方法也仍缺直接对应文献。

## 13. 版本变更记录

| 版本 | 日期 | 状态 | 变化 |
|---|---|---|---|
| `v0.1-draft` | 2026-08-06 | 未冻结 | 依据参考框架与 135 条 `pilot_draft` 建立二元主标签、五个实质 subtype 加一个兜底项、hard negatives、字段与未来标注流程 |
