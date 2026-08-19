# 压力集预登记(STRESS-SET PRE-REGISTRATION)— v1.1

> **状态:🔒 关键词表(§5/§5.1)已冻结 + 机械检索已授权(Yifan,2026-08-12)。** 人工盲标仍待 prompt 冻结后开门(§4)。签字前的探索性说明只对「人工入选」部分继续有效;检索本身是机械、只落 candidate id、不读正文。
> **本文件替换** `~/Desktop/gold抽样与压力集_方案讨论_2026-08-10.md` §9 的「拟登记 v0」。v0 存档追溯用,不再执行。
> 目的:先把规则钉死,防止事后按结果挑选(选择性 / 循环论证)。压力集**不与 representative gold 合并、不加权、不进任何头条/语料级数字**。
> 建立:2026-08-11。维护人:Yifan(`NPC010100Nonbug`)。依据:codebook `v1.0`(🔒 2026-08-10)。

---

## 0. 一句话与 v0→v1.1 的核心变化

压力集 = **罕见/困难例诊断探针**(PRESENT、borderline、低资源 JA),模型无关的关键词检索 → 人工盲标 → 只报诊断口径。

**v1.1 相较 v0 的唯一根本改动:把「筛读量 `N_screen`」和「最终入选量 `N_final`」拆开。** v0 的「读满 300 就停」会让某格出现「8 个正例、却只有 1–2 个负例」,负例不够 → 没法诚实报 false-positive rate。v1.1 让筛读量可放大(逐格 ≤120,稀疏格 ≤200),但最终入选量仍受控(≤300、正负相对均衡)。其余 12 条是围绕这条主轴的正确细化(见 §2–§14)。

---

## 1. 规模:两个数量分开记

| 量 | 含义 | 上限 |
|---|---|---|
| `N_screen` | 人工实际读过并判断的候选数 | 不设全局上限;逐格 ≤120(标准)/ ≤200(稀疏格扩展) |
| `N_final` | 最终进入压力集的数据数 | ≤ **300** |

`N_final` 组成:

| 部分 | 上限 |
|---|---:|
| 核心压力集 | 288 |
| 边界补充集 | 12 |
| **合计** | **300** |

**核心 288** = 3 语言 × **6 目标桶** × (8 PRESENT + 8 hard negative) = 18 格 × 16 = 288。

**6 个「目标桶」**(术语:不都叫 facet —— `distributive` 是 subtype,其余 5 个才是 procedural facet):

```
distributive
procedural.cheating_governance
procedural.sanction
procedural.unfair_by_design
procedural.competitive_balance
procedural.access_exclusion
```

> 不对称说明:`distributive` 整个 subtype 当一个桶,`procedural` 拆 5 个 facet(与 codebook §4.2.1 一致)。故 distributive 格通常好填、procedural 稀有格难填;报告时不得把「distributive 案例多」当成实质结论。

---

## 2. 每格入选目标(🔒 采纳 5+5 现实目标,Yifan 2026-08-11 定)

每个「语言 × 目标桶」:

- 核心 PRESENT:**现实目标 5,stretch 8**;
- 核心 hard negative:**现实目标 5,stretch 8**;
- **两侧都到 5 = 该格「已覆盖」**;两侧都到 8 = 该格「满配」;
- 候选不足时允许低于 5,**但必须报告真实数量**;
- **不得降低 codebook 门槛凑数**;
- **不得用其他 facet 的案例冒充该格**;
- **删除 v0 的「找到 8 个 PRESENT 就停」** —— 那会造成正负不平衡。

> round-robin 纪律(见 §8):先让 18 格都到 **5+5**,有余力再逐格冲 **8+8**,最后处理边界补充集。

---

## 3. 核心集 vs 边界集(分开,不混算 1:1)

**核心 PRESENT** 须:人工最终标签 `PRESENT`;最终 subtype/facet 确实含该目标桶;原则上 `borderline=false`;`confidence` ∈ {high, medium}。

**核心 hard negative** 须:命中该目标桶检索词;人工最终主标签 `ABSENT`(**不是 NA**);原则上 `borderline=false`;`confidence` ∈ {high, medium}。

**进边界补充集(不占核心 8+8 配额)**:`borderline=true` / `confidence=low` / PRESENT-ABSENT 特别易混 / 多 facet 归类有合理争议。边界集 ≤12,建议每语言约 4;不足按实保留,不硬凑。

> **cross-facet contrast(关键)**:一条最终是 `PRESENT`、只是 facet 与检索目标不同 → **不算整体 hard negative**,记为 `cross-facet contrast`(`stress_role=cross_facet`),不计入该格 hard-negative 配额。硬负例必须是整体 ABSENT,否则误报数被算错。

---

## 4. 候选来源与防泄漏火墙

压力集候选必须:

- 来自冻结的 `machine_eligible_frame`(419,827 行);
- **后减前**:排除全部 pilot(488)+ 全部 representative gold(600)= 基线 **1088 行**,以**抽取当时的** `split_manifest.csv` 快照为准;
- 一个 `review_id` 只承担一个数据角色;
- **打开候选正文前,codebook / prompt / 关键词表 / 随机种子 / 本规则全部冻结**;
- 全部人工标签在**看到任何模型预测之前**完成。

**A. 写回 split_manifest(v1.1 补,防我们自己的白名单导出漏掉压力集):**
最终入选的 stress `review_id` 必须**以 `role=stress` 写回 `split_manifest.csv`**(富元数据 stress_role/quota_credit_cell 等留在 `stress_final_manifest.csv`)。**且必须在切 train 之前**(见 §切分时序 ③')。这样 train 的后减前自动减掉 stress、给 ASUS 的白名单导出(`role=='train'`)零特判就挡掉它。**若 stress 只活在旁边的独立文件、不写回 manifest,train 会把它当可用数据抽走 = 泄漏。**

**B. 筛读过但未入选(screened-rejected)的检疫:**
这些 `review_id` 记入 `stress_screening_log.csv`。**本轮(v1)评估前不得用于调 prompt / few-shot / 训练模型**;最早在 v1 评估结束后才可转为 v2 开发资料。落地:切 train 时,后减前额外减去 `stress_screening_log` 的全部 review_id(数量相对 41 万帧可忽略,代价极小)。

**C. 与 gold 同级的火墙:** 本人手标、在任何模型结果出现前提交并冻结、**绝不进训练**。检索命中词族 / 目标桶 / 精度层 / provenance **不喂标注者**(见 §10 盲法)。

---

## 5. 关键词分两层(高精度 / 宽口径)—— 初稿,待 Yifan 逐格增删

> **⚠️ EN/ZH 部分已由 `stress_preregistration_v1.2.md` 取代(Yifan 授权,2026-08-12)。** 下面这张 EN/ZH **共用**表暴露出「中文模式扫英文不触发」的乐器不对称(en competitive_balance high=1),v1.2 已把它**按语言拆成 EN / ZH 两表**并重跑检索。**下表保留作历史记录,不再用于检索**;JA 仍以 §5.1 为准。
> **🔒 原冻结说明(Yifan,2026-08-12,历史):** 分两层的用意与 round-robin 纪律仍有效(见 §8)。**一旦冻结,不得再据检索结果回改(预登记纪律)。** v1.2 的升级发生在**开正文之前**、只据候选计数修乐器,符合此纪律。
> 分两层的用意:高精度词偏向钓 PRESENT;宽口径词既钓 PRESENT 也钓有价值的 hard negative。**round-robin 时两层交替读**,避免只读高精度导致 hard negative 不足(§8)。
> **日语以 §5.1 为准**(下表内的日语片段仅作历史参考,不再用于检索)。

| 目标桶 | 高精度(偏 PRESENT,EN/ZH) | 宽口径(兼钓 hard negative,EN/ZH) |
|---|---|---|
| `distributive` | P2W、pay-to-win、付费致胜、氪金武器、精英版才解锁、误导性付费墙 | 氪金、付费、price、价格、unlock、通行证、battlepass、DLC、精英版 |
| `cheating_governance` | 官方不管外挂、anti-cheat useless、no action from devs、Valve放置 | cheat、外挂、hacker、hack、作弊、挂 |
| `sanction` | false ban、误封、无故封号、申诉无门、剥夺已付费权 | ban、封号、封禁、banned、踢 |
| `competitive_balance` | rigged matchmaking、阵营优势、匹配碾压 | matchmaking、匹配、平衡、balance、RNG、carry |
| `unfair_by_design` | input reading、读指令、无限精力/无限耐力、artificial difficulty | 难度、boss、读指令 |
| `access_exclusion` | Secure Boot 排除玩家、不支持 Linux/Deck、强制换主板/硬件才准入、kernel 反作弊排除 | Secure Boot、TPM、Linux、Steam Deck、kernel、主板 |

### §5.1 日语检索表(正式版,取代主表中的日语片段;🔒 2026-08-12 Yifan 定稿)

> **语义:** 高精度列的 `A.*(B|C)` = **同一条评论中 A 与 (B 或 C) 同现**(可隔开、不要求相邻,检索脚本对每个括号组独立 `search`、全部命中才算该词命中,不强制先后顺序)。单词型(如 `P2W`、`おま値`、`誤BAN`)= 直接出现即命中。

| 目标桶 | 高精度:优先找 PRESENT | 宽口径:兼找 hard negative |
|---|---|---|
| `distributive` | `P2W`;`課金.*(有利\|強い\|勝て)`;`無課金.*(不利\|勝てない\|厳しい)`;`課金.*(武器\|キャラ\|解放).*(有利\|必須)`;`おま値` | `課金`、`無課金`、`解放`、`アンロック`、`DLC`、`バトルパス`、`おま国`、`日本だけ`、`価格` |
| `cheating_governance` | `(チーター\|チート).*(野放し\|放置)`;`チート対策.*(していない\|機能していない)`;`通報しても.*(対応\|BAN).*ない` | `チート`、`チーター`、`ハッカー`、`ウォールハック`、`aimbot`、`コンバーター`、`VAC` |
| `sanction` | `誤BAN`、`誤バン`、`冤罪BAN`;`濡れ衣.*BAN`;`身に覚え.*BAN`;`BAN.*(理由.*ない\|説明.*ない\|解除されない\|異議申立)` | `BAN`、`垢BAN`、`垢バン`、`アカウント停止`、`永久BAN`、`キック` |
| `competitive_balance` | `不公平.*(マッチング\|MMR)`;`(低MMR\|初心者\|低ランク).*(高MMR\|格上\|上位).*(マッチ\|当た)`;`マッチング.*(格差\|一方的)` | `マッチング`、`MMR`、`ランク`、`バランス`、`格差`、`一方的`、`PAD`、`エイムアシスト`、`RNG`、`運ゲー`、`OP` |
| `unfair_by_design` | `理不尽な(仕様\|設計\|敵\|AI)`;`(入力読み\|読んでくる).*(ボス\|敵\|AI\|仕様)`;`(敵\|AI)だけ.*(無限\|スタミナ\|有利\|強い)` | `理不尽`、`初見殺し`、`簡悔`、`難しい`、`死にゲー`、`即死`、`ボス` |
| `access_exclusion` | 不设单词型高精度词,只用组合:`(Secure Boot\|セキュアブート\|TPM).*(強制\|必須).*(非対応\|マザーボード\|遊べない)`,再由人工确认是否有「排除/不合理」的规范判断 | `Secure Boot`、`セキュアブート`、`TPM`、`Linux`、`Steam Deck`、`Proton`、`マザーボード`、`起動できない` |

**v1.1 已并入的两处纠正(相对 v0):**
- `課金アンロック` 归 **`distributive`**(付费解锁内容),**不归** `access_exclusion`(v0 §③ 曾误置)。
- `kernel` / `unlock` / `ban` 等过宽单词**不能单独当高精度词**,放入宽口径层或必须与上下文词组合。

**日语形态/同义合并**(变体计入同一词桶,仅用于检索与去重计数):課金=課金/廃課金/重課金/無課金;チート=チート/チーター;BAN=BAN/垢BAN/バン/アカウント停止;理不尽=理不尽/理不尽な;おま国=おま国/おま値。EN:ban/banned/banning、cheat/cheater/cheating、hack/hacker/hacking。ZH:封号/封禁、外挂/挂。

---

## 6. 去重必须在降采之前(防隐蔽选择偏差)

正确顺序:

1. 搜全部冻结关键词;
2. 每条评论保存其命中的**所有**词族(`matched_keyword_families`);
3. 按 `review_id` 去重;
4. 对规范化后完全相同的文本再去重;
5. **然后**才生成随机顺序、施加候选上限。

> 否则一条命中 5 个关键词的评论会获得 5 次被抽机会 = 隐蔽选择偏差。一条评论可同时属于多个词族,但**人工只读一次、最终只计一次**。

---

## 7. 取消固定 facet 抢占优先级(v0 §③ 的「作弊>封号>准入…」删除)

- 候选可同时属于多个候选桶;
- **检索归类不决定最终标签**;
- 人工标完后,按**最终标签**分配配额;
- 一条评论只获得一个 `quota_credit_cell`,但保留全部真实 subtype/facet 标签。
- 一条 PRESENT 同时符合多个未满目标桶时:① 优先分给**完成比例最低**的格;② 完成比例相同 → 冻结的稳定哈希/固定种子决定;③ 不由标注者临时挑。

> v0 的固定优先级会让稀少的 `access_exclusion` 被作弊关键词提前抢走。改为「最终标签定归属」后,常见 facet 不再挤占稀有 facet。

---

## 8. 固定随机顺序 + 分批 round-robin 筛读

每个「语言 × 目标桶 × 精度层」生成固定随机序,种子:

```
f"{SPLIT_SEED}-stress-v1-{lang}-{target_bucket}-{precision_tier}"      # SPLIT_SEED=20260806
```

人工每批 **20 条** round-robin:

1. 先让所有 18 格尝试到 **5 PRESENT + 5 hard negative**;
2. 再让所有可行格冲 **8 + 8**;
3. 最后处理 ≤12 边界补充案例。

> 高精度层与宽口径层**交替读**,避免只读高精度导致 hard negative 不足。round-robin 防止英语作弊大池过早吃光时间、而日语稀有格还没被检查。

---

## 9. 人工停止规则(取消全局「读满 300 停」)

**标准筛读阶段(每格):** ≤120 条独立候选,每 20 条一批;该格同时达 8P+8HN 即停。

**稀疏格扩展阶段:** 若读满 120 后 PRESENT 或 hard negative 任一侧仍 <5 → 启用**预先冻结的扩展词表** → 继续读,累计 ≤200 → 仍不足则停并报实得数。

每格停止条件 = **同时达 8P+8HN** ∨ **冻结候选池真正耗尽** ∨ **累计筛读达 200**,三者先到即停。

> **认识论诚实红线:** 「读到 200 仍不足」只能写成 **「在预登记检索方法与 200 条筛读预算内未达目标」**,**不得**写成「该语言不存在这种 facet」。120/200 是**工作量控制线**,不是统计学上的语料穷尽。

---

## 10. 标注者盲法

人工标注表**可显示**:评论正文;Steam 语言桶;codebook 允许、且模型也会获得的 metadata(§4.0 那组,**不含作者身份**)。

**不得显示**:命中了什么关键词;系统希望它属于哪个 facet;高精度/宽口径来源;当前哪个格缺多少;pilot 的 curated tag;模型预测或置信度。

> 否则标注者会因「知道这是在找 access_exclusion」而把边界案例往该 facet 偏。

---

## 11. 游戏维度:不做硬配额,按真实 locus 报告

游戏**不作为新的硬配额维度**(否则生成大量理论上不合理的空格)。保留 `appid/game` 字段,按真实 locus 报告(与 codebook §4.2.1 locus 一致):

- `unfair_by_design`:目前只支持《艾尔登法环》内三语诊断;
- `competitive_balance`、`access_exclusion`、`sanction`:主要《战地2042》内;
- `cheating_governance`:尽量同时保留 CS2 与《战地2042》;
- `distributive`:记录实际游戏构成,不默认三款游戏都有同一付费机制。

> 对单游戏 facet,只能写「同一游戏不同语言中的压力表现」,**不得把差异直接解释成纯语言效应**(与项目总基调一致)。

---

## 12. 冻结前小规模盲复标(利用新增人工阅读能力)

- 从最终压力集分层随机抽 ~30 条,每语言×目标桶至少 1 条;
- 间隔 ≥7 天;
- 隐藏第一次标签与候选来源;
- 保存 `original` / `retest` /(必要时)`adjudicated` 三套。
- 复标发生在**最终人工标签冻结前、任何模型输出前**。

> 复用现有 `scripts/04a_retest.py` 与 `data/splits/retest_manifest.csv` 的 harness。

---

## 13. 应保存的文件

```
freeze/stress_preregistration.md      # 本文件(冻结后 🔒)
data/splits/stress_candidate_manifest.csv
data/splits/stress_screening_log.csv
data/splits/stress_final_manifest.csv
```

`stress_final_manifest.csv` 至少含字段:

```
review_id
appid
steam_language
matched_keyword_families
eligible_target_buckets
precision_tier
candidate_rank
screening_batch
human_unfair_label
human_subtype
human_procedural_facet
borderline
confidence
uncertainty_reason
quota_credit_cell
stress_role            # present / hard_negative / boundary / cross_facet
stop_reason
```

> 评论**全文**继续只留本机受控 / gitignored 文件(`data/raw/`),不进这些可发布 manifest。**同时**:最终入选 id 以 `role=stress` 写回 `split_manifest.csv`(§4-A)。

---

## 14. 报告限制(硬性)

压力集**只报**:各语言各目标桶的 PRESENT 召回;hard negative 误报率;facet 混淆;borderline 错误类型;每格准确数量与置信区间;每个游戏的实际 locus。

**不得**:与 representative gold 合并;算加权总体准确率;推算 PRESENT 在真实语料中的比例;把压力集表现称为自然评论分布下的模型表现;因某格只有 5–8 条就做稳定的语言优劣排名。

---

## 冻结参数速览

```
目标桶数:6            语言数:3            总格数:18
每格核心 PRESENT:现实目标 5,stretch 8
每格核心 hard negative:现实目标 5,stretch 8
核心压力集上限:288    边界补充集上限:12    最终压力集上限:300
人工筛读:
  - 每格标准阶段:≤120
  - 稀疏格扩展阶段:累计 ≤200
  - 无全局筛读上限
  - 每批 20,round-robin
后减前基线:488 pilot + 600 gold = 1088(以抽取时 split_manifest 快照为准)
种子:f"{SPLIT_SEED}-stress-v1-{lang}-{target_bucket}-{precision_tier}",SPLIT_SEED=20260806
```

---

## 切分时序(在 data_split_spec §3 之上补 ③')

```
③  gold  ID(已抽 600)
③' stress:先跑关键词检索(可在 prompt 冻结前,只落 candidate id、不读正文)
          → prompt 冻结后人工盲标 → 定 final
          → 以 role=stress 写回 split_manifest
④  dev
⑤  train = 机械合格帧剩余(后减前 = pilot + gold + stress-final + stress-screening-log)
```

> **门:** 检索(§5–§8 的机械部分)可现在做;**打开候选正文、人工入选(§2/§3/§9 的标注部分)必须在 prompt 冻结之后**(§4)—— 与 gold 手标同一道门。**train 未切前不许切**,以保 ③' 在 ⑤ 之前。

---

## 签字

- [x] Yifan 已定稿 §5/§5.1 关键词表(日语补充见 §5.1),🔒 2026-08-12。
- [x] Yifan 授权机械检索(2026-08-12)→ 记 decision_log → 跑 `scripts/05_stress_retrieve.py`(只落 candidate id、不读正文)。
- [ ] **(仍待)prompt 冻结后**方可打开候选正文、人工盲标 → 定 final → 以 `role=stress` 写回 `split_manifest.csv`。

> **人工入选前:本集只算探索性案例分析,不是正式压力测试。** 检索已授权、机械执行。
