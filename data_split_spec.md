# 数据池切分规格(DATA SPLIT SPEC)

> **单一事实源**。任何对话/脚本要给评论分配用途,以本文件为准。
> 实际的 review_id → 角色归属,存在名单层:`data/splits/split_manifest.csv`。
> 建立:2026-08-06。维护人:Yifan(`NPC010100Nonbug`)。

---

## 0. 一句话

把同一个原始池按**用途**切成 6 个互不重叠的角色;每条 review 有且仅有一个角色;
**两条隔离是铁律(gold 与 stress 均对开发全程隐身、绝不进训练),其余分开只是卫生。** 全靠 review_id 焊死,不靠记性。

---

## 1. 六个角色

| 角色 | manifest 里的 `role` | 规模(每语言) | 用途 | 谁可以碰 | 从哪切 |
|---|---|---|---|---|---|
| 起草 pilot | `pilot_draft` | 30–50/语言(**实际已扩至合计 353**,见下注) | AI 读它 → 写 codebook 的定义 / inclusion / exclusion / 例子 | 你 + AI | 原始池(对齐前即可) |
| prompt 调试 pilot | `pilot_prompt` | 30–50 | 调 LLM 标注 prompt,调到听话再冻结 | 你 + LLM | 原始池(对齐前即可) |
| **gold 测试集** | `gold` | **每语言 100 codable**(首批各抽 200 raw) | **盲评**,考 LLM zero-shot / 微调模型准不准 | **开发期谁都不许碰** | 机械合格帧 |
| **stress 压力集** | `stress` | 诊断集,`N_final`≤300(非每语言均量) | **诊断探针**:罕见/困难例的 PRESENT 召回 / facet 误报,单独报、**绝不进训练、不与 gold 合并** | **开发期谁都不许碰(同 gold)** | 机械合格帧(后减前减 pilot+gold) |
| dev 集 | `dev` | 50–100 | 选模型 / 调超参 | 训练期 | 机械合格帧 |
| 训练集 | `train` | 上千 | LLM 弱标注 → 喂微调 | 训练期 | 机械合格帧(剩余全部) |

> **`stress` 是 Tier-1 隔离(与 gold 同级)**:非随机、关键词定向检索的困难例探针;规则见 `freeze/stress_preregistration.md`(v1.1)。富元数据存 `data/splits/stress_final_manifest.csv`,但 **review_id→`role=stress` 必须写回本 manifest**,否则切 train 时会把它当可用数据抽走 = 泄漏。**尚未抽取**(待 prompt 冻结后人工盲标)。

> **规模是当前计划,冻结前可再调**;改了就更新本表 + decision_log。
>
> **⚠️ 抽样方案更新(2026-08-11,取代旧"按月对齐到 JA"设计):** gold 的抽样帧不再叫"对齐池",改为 **`machine_eligible_frame`(机械合格帧)** = raw 去重 + 时间窗(`timestamp_created ≤ 2026-08-01`、主池不设下界)+ 从轻内容过滤(仅剔空/纯符号,不设长度阈)+ **Steam 语言桶**(信任 Steam `language` 字段、不跑 langid、不做事后 language_match 排除)。gold 用 **三语等额 200/语言 + 语言内按游戏比例(最大余数法)** 抽,加权还原语料级数字;**研究对象 = 当前语料环境表现,不主张剥离游戏/时代的纯语言效应**。**HANDOFF.md §4 的"共同窗口 + 按月直方图对齐到 JA 降采"已作废(JA/CS2 会被饿死)。** 完整规则与冻结记录见 `~/Desktop/gold抽样与压力集_方案讨论_2026-08-10.md`(§7/§8,🔒 2026-08-11 已签)。
>
> **注:`pilot_draft` 实际规模(2026-08-10)= 合计 353**(270 随机 + 83 三批目的性补样:distributive 18 / procedural 44 / 跨语言补缺 20)。远超上表初始 30–50/语言——因冻结前需足够证据做 facet 的 `support_volume` / 语言覆盖判定,且 `pilot_draft` **不参与测量**、目的性补样合法(已披露为非随机,见 codebook §9.2)。**gold 规模仍按上表(≥100/语言 codable)。**

---

## 2. 两级隔离(轻重不同,别搞反)

- **Tier 1 — 铁律(违反 = 造假):** `gold` 必须和**一切开发活动**隔离。
  codebook、prompt、few-shot 例子——**建立过程都不许见过 gold 里的任何一条**。
  否则 gold 天然"包过",评估分数虚高 = 数据泄漏 = 自己骗自己。
  gold 之所以可信,唯一原因就是它对整个开发过程隐身。

- **Tier 2 — 卫生(违反 ≠ 造假,但会自欺):** `pilot_draft` 与 `pilot_prompt` 最好分开。
  若两者是同一批评论 → codebook 例子和 LLM few-shot 例子重合 → LLM"背下来"表现好,
  给你**虚假的乐观**。分开才能诚实看出 prompt 在没调过的数据上到底行不行。
  但即便①②不慎重叠,**最终 eval 不会被污染**(eval 在 gold 上,gold 没碰)——所以这是"防自欺",不是"防造假"。

---

## 3. 切分不变量(脚本必须保证)

1. **唯一归属**:一个 review_id 在 manifest 里只出现一次,只有一个 `role`。
2. **后减前**:后切的集合必须**减去 manifest 里已占用的所有 review_id**,再从剩余里抽。
3. **固定 seed**:`SPLIT_SEED = 20260806`(整个项目复用同一个,写死在脚本常量)。
4. **可复现**:任何人拿脚本 + manifest,能复原完全相同的切分。

### 切分顺序(严格按此,保证 Tier 1 firewall)

```
Phase 3a(已完成,建帧前):
  ① 从原始池切 pilot_draft   → 写 manifest
  ② 从原始池切 pilot_prompt  → 写 manifest(减去 ①)

Phase 3b(02_align_sample.py 之后,物化 machine_eligible_frame,每步都减去 manifest 已有):
  ③  gold   ← 三语等额 200/语言,先切、切完立即隔离(只落 review_id、不读文本)
  ③' stress ← 关键词检索出候选 id 可在 prompt 冻结前(只落 candidate id、不读正文);
              prompt 冻结后人工盲标 → 定 final → 以 role=stress 写回 manifest(见 stress_preregistration.md)
  ④  dev    50–100
  ⑤  train  = 机械合格帧剩余全部(后减前 = pilot + gold + stress-final + stress-screening-log)
```

> ⚠️ **③' 必须在 ⑤ 之前**:stress 与 train 同源(都从帧剩余切),若先切 train、后抽 stress 会重叠 → 泄漏。**train 未切前不许切**,以保此序。stress 的检索(机械)可现在做;**打开候选正文、人工入选必须在 prompt 冻结之后**(同 gold 手标那道门)。

> ⚠️ **顺序防泄漏(2026-08-11 强化)**:③ 切 gold **ID** 可以在冻结 prompt 之前(只落 review_id、不读文本);但**打开 gold 文本、人工标注必须在 prompt 冻结之后**——否则先读考题再出题,gold 独立性被污染。见 gold 抽样备忘 §1。
>
> 为什么 pilot 可以在建帧前切:codebook 定义"什么算不公平"与时间窗口无关(construct 是 window-independent),
> 所以起草不必等建帧。gold/dev/train 必须来自 **machine_eligible_frame**(同一抽样帧)。
> 无论 pilot 是否落在时间窗内,**后减前**都能保证它不会溜进 gold/train。

---

## 4. 名单层:`data/splits/split_manifest.csv`

- **跟踪进 git**(review_id 可公开,见 decision_log 2026-07-28)。
- 列:`review_id, appid, lang, role`
  - `lang` ∈ {`en`, `zh`, `ja`};`role` ∈ 见 §1 第二列。
- 这是**机器可读的唯一真相**;本 md 是人读的规则。二者冲突时,以"规则(本 md)"为准,并修 manifest。

---

## 5. 红线回顾(与既有项目约定一致)

- gold **永不用于训练**(训练用到它 = 泄漏)。
- 人工标注在看到模型结果**之前**冻结,之后不改。
- prompt 只在 `pilot_prompt` 上调,冻结后再上 gold/eval。
- 原始文本只留本机(`data/raw` gitignored);只发布 labels / review_ids / ≤10 行 demo。

---

## 6. 状态

- [x] **Phase 3a — pilot 已切**:`pilot_draft` 353 + `pilot_prompt` 135 = **488 行**已在 manifest(经 `02a2_expand` + `02a3/02a4/02a5` 三批目的性补样;非 `02a_make_pilot.py` 单脚本,已合规)。
- [x] **Phase 3b — 机械合格帧已物化**(2026-08-11):`data/processed/machine_eligible_frame.csv`,**419,827 行**(仅 review_id,gitignored)。见 `scripts/02_align_sample.py`。
- [x] **gold 已抽**(2026-08-11,单向门已跨):三语等额 200 + 语言内按游戏比例(最大余数法),**600 行 gold** 已焊进 manifest;设计权重 → `data/splits/gold_design_weights.csv`,NA 补位顺序 → `data/splits/gold_reserve_order.csv`(419,227 行)。**只落 review_id、未读文本**;文本防火墙:prompt 冻结前不许开 gold 文本。
- [ ] `dev` / `train`:仍待从机械合格帧剩余里切(后减前减去 488 pilot + 600 gold),另单独执行。
- **manifest 现状**:`data/splits/split_manifest.csv` = **1089 行**(600 gold / 353 pilot_draft / 135 pilot_prompt)。`SPLIT_SEED=20260806`,每 cell 种子 `f"{SPLIT_SEED}-{appid}-{lang}"`,可复现。
