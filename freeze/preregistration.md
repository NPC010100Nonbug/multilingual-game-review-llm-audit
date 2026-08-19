# 冻结前预登记(PRE-REGISTRATION)— codebook v1.0

> **状态:🔒 已批准并生效(Yifan,2026-08-10)。codebook 已冻结为 `v1.0`。** 阈值在跑检验之前已锁死,事后未回改。
> 诚实红线:不得在看到 κ / 自洽度数字之后再回改及格线(那是事后挑标准)。改阈值 = 记一条
> decision_log + 说明为何在跑之前改。
> 建立:2026-08-10。维护人:Yifan(`NPC010100Nonbug`)。

---

## 0. 为什么要这份文件

§9.3 的两关(独立盲检 #1、单人跨语言漂移 #2)都写了"阈值**预登记**"。
预登记 = **先把"多少分算过"写死,再去标**。否则跑完看着结果定线,等于自己给自己发及格证。
本文件把两个检验的:①用哪批数据 ②谁标 ③算什么指标 ④及格线 ⑤没过怎么办,全部提前固定。

---

## 1. 检验 #1 — 独立 codebook 盲检(测 codebook 写得够不够清楚)

| 项 | 预登记值 |
|---|---|
| **测什么** | 一个**没参与起草**的读者,只靠冻结候选版 codebook,能不能复现主标签与 facet |
| **数据** | `codebook_check` 集:从 **353 pilot 行里、未被 codebook 正文引用的**(即不在那 67 个 anchor/例子 id 中)行随机抽,三语分层 |
| **规模(建议)** | 每语言 **20 条**(合计 60),PRESENT/ABSENT/NA 按 pilot 自然比例分层 |
| **谁标(建议)** | **全新 Claude 实例**(只喂 codebook + 待标行,不给起草记忆)当"独立陌生读者";Yifan 保留仲裁 |
| **对照基准** | Claude 起草期已有的标签(`pilot_labels_claude.jsonl`)作参照面,**非"标准答案"**——不一致=查 codebook 哪条含糊 |
| **主指标** | 主标签(PRESENT/ABSENT/NA)的 **Cohen's κ**;facet 的 per-facet 命中一致率 |
| **及格线(已定 2026-08-10)** | 主标签 **κ ≥ 0.65**(Yifan 选更严档);PRESENT-vs-rest specific agreement **≥ 0.70**;facet 一致率**报告即可**(facet 类多、样本薄,不设硬线) |
| **没过怎么办** | 找出不一致的行 → 定位 codebook 含糊规则 → 补规则/补反例 → **改的是 codebook,不是阈值** → 重新盲检 |

> 说明:κ<0.65 常被读作"judge 判准不牢";但这里 judge 是**同一模型**,低分更可能指向**文档歧义**,
> 所以修的是 codebook。Yifan 定 0.65(比"可接受"下限 0.60 更严)。

---

## 2. 检验 #2 — 单人跨语言判准漂移(test–retest)

> **⚠️ 本次(v1.0)豁免(Yifan 定,2026-08-10)。** 理由:10–14 天日历硬等待会把冻结整体推后约两周,
> pilot 阶段选择先不做单人漂移检验、只靠独立盲检(#1)把关即可。
> **代价须在方法学里如实披露**:v1.0 未量化"同一标注者跨语言判准漂移",而这是单人三语 gold 的已知
> 主威胁,可能与"模型在某语言更差"混淆——列入 README/论文 limitations。
> **harness 已备好**(`scripts/04a_retest.py`),留待 v2 或补做;下面设计原样保留供将来使用。

| 项 | 预登记值(留待将来) |
|---|---|
| **测什么** | 同一份冻结 codebook 下,**你本人**隔一段时间重标,前后对不对得上(intra-rater) |
| **数据** | `retest` 集:从已标 pilot 里抽固定子集,**三语各 15–20 条**,混 PRESENT/ABSENT/NA(含若干 borderline) |
| **谁标** | **Yifan 本人**(gold 是一人标三语,测的就是你自己的漂移;不能让 AI 代) |
| **设计** | T1 今天标 → **藏掉现有标签、随机打乱行序、轮换三语呈现顺序** → **隔 10–14 天** → T2 同法再标一遍 |
| **主指标** | raw agreement、**Cohen's κ**、混淆矩阵、PRESENT-vs-ABSENT specific agreement;分语言各算一份 |
| **及格线(建议)** | 每语言主标签 **κ ≥ 0.60**;**三语间 κ 落差 ≤ 0.15**(落差大=某语言判准更飘,会和"模型在某语言更差"混淆) |
| **没过怎么办** | 漂移大的规则重写 + 补例 → **重测**(又是一轮 10–14 天,或对该规则做小范围快速重标) |

> **日历硬约束:T1→T2 至少隔 10–14 天,压不掉。** 所以这一关是整条冻结路径的长杆:
> **今天不启动 T1,v1.0 最早冻结日就往后推 10–14 天。**

---

## 3. anchor 密度(§9.3 "anchor+字段完整")

| 决定项 | 预登记值(建议) |
|---|---|
| 每个 facet 至少 | **1 正例 + 1 hard negative + 1 borderline** |
| 满配? | 不追求 5×3×3=45 满格;够教边界即可 |
| 缺口处置(冻结时已闭合) | `unfair_by_design`/borderline **已填** `165149867`(battlepass 解锁苦劳 = 货币化/distributive 边界→ABSENT-borderline);`sanction`/hard-negative **已豁免**(pilot 无干净 ABSENT 封号行,记为有信息量的缺失);`access_exclusion`/borderline = `228424527`(PRESENT-borderline,Yifan 最终定 borderline 非正例)。最终 30 anchors,0 角色冲突。 |
| 裁定权 | anchor(尤其 hard negative)的 keep/cut/改理由,**由 Yifan 在 `freeze/anchor_review_sheet.md` 上逐条过** |

---

## 4. 冻结判定(全过才谈 v1.0)

冻结 v1.0 需**同时**满足:
1. 检验 #1 达 §1 及格线(κ≥0.65);
2. ~~检验 #2~~ **本次豁免**(见 §2;限制写入 limitations);
3. §3 anchor 审阅表已由 Yifan 逐条 ✅(含 unfair_by_design/borderline 缺口的指定或豁免);
4. §9.3 其余行(补样披露 / facet 状态 / metadata schema / 文件一致)已闭合(多数 rev7 已做,复核即可)。

全过 → 把 codebook 版本从 `v1-draft-rev7` 改为 **`v1.0`(冻结,永不原地改;改动=v2.0+重标)** → 记 decision_log → **才**开始抽随机 gold。

> **顺序铁律:冻结在前,gold 在后。** gold 一旦抽出即对全部开发隐身。
