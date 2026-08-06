# HANDOFF — 多语言游戏评论 LLM(感知不公平)训练项目

> 目的:让**下一个全新对话**不看历史也能无缝接手。
> 更新时间:2026-08-05。维护人:Yifan(GitHub `NPC010100Nonbug`)。
> 仓库:`~/Documents/multilingual-game-review-llm-audit`。

---

## 0. 一句话现状

**Phase 1(环境/探针)+ Phase 2(Steam 采集)已完成并提交(commit `12e710f`)。当前入口:Phase 3 —— 先写 codebook(标注规范),再写 `02_align_sample.py`(对齐+分层抽样)。**

---

## 1. 项目是什么

- **构念(construct)**:玩家评论里表达的 **perceived unfairness(感知到的不公平)**。
- **语言**:英语 EN / 简体中文 ZH / 日语 JA,三语横向比较。
- **从审计升级为训练项目(2026-08-04 决策 B)**:不只调 API 打分,而是真的**微调一个多语言模型**,练两块 Yifan 想补的能力 —— **标注** + **训练/微调**。截止期已放松,深度优先。
- **三数据集架构**:
  - **人工 gold 测试集**(手标,每语言 ≥100,**永不用于训练** —— 训练用到它=数据泄漏)。
  - **LLM 弱标注训练集**(每语言上千条,弱监督/蒸馏)。
  - dev/开发集。
- **模型/算力**:微调 `xlm-roberta-base`;**训练跑在 ASUS TUF F15(RTX 4060 8GB, CUDA)**,Mac 负责采集/标注/分析,**Git 是两台机器的同步桥**。
- **三方对比**:微调模型 vs LLM zero-shot vs 人工 gold;外加**跨语言迁移矩阵**(在一种语言上训、到另外两种上测)。

### 诚实红线(必须守)
- 若仓库将来发给 AISS Lab,**README/邮件必须写明**:项目从"仅 API 审计"成长为"蒸馏+微调",绝不隐瞒训练部分。
- API key 绝不进仓库;`.env` gitignored(若误推立即吊销)。
- `data/raw`、`data/processed` gitignored,**原始评论文本只留本机**;只发布 labels / review_ids / ≤10 行 demo。
- 构建 `reviews.csv` 时**丢弃作者身份**(steamid、personaname、profile_url)。
- 人工 gold **永不用于训练**;标注在看到模型结果**之前**冻结,之后不改。
- Prompt 只在 pilot 集上调,冻结后再上 gold/eval。
- 任何**付费/批量 API 调用前**先估成本、要用户确认;Steam 公共 API 免费无 key,无需确认。
- 不为了省事缩小样本(见 memory `dont-shrink-sample-for-convenience`)。

---

## 2. 已建的脚本(都在 `scripts/`,已提交)

| 脚本 | 作用 | 关键点 |
|---|---|---|
| `00_probe_counts.py` | 探针:对比 `purchase_type=steam` vs `all` | 结论:用 `all`(默认 `steam` 会丢 key/免费获取的评论;CS2 中文差 3.47×)。 |
| `00c_inspect_raw.py` | 无 API 的原始文件体检 | 打印每个 `data/raw/*.jsonl` 的条数 + 最旧/最新日期。 |
| `01_collect.py` | v3 floor-based 采集器 | 先全量拉 JA 定义每款游戏的时间 floor,再把 EN/ZH 回采到该 floor(capped 15k)。用 `purchase_type=all`;CS2 用 `min_timestamp=1695772800` 砍掉 CS:GO 时代。 |
| `01b_deep_collect.py` | **可续跑**的深采器(EN/ZH) | 边写边存、checkpoint 原子写、指数退避重试、诚实停止(reached_end / reached_floor / cursor_stalled)。fresh 启动会删掉旧 capped 文件从 `*` 重走;JA 文件从不动。 |

### Steam API 速记
- `https://store.steampowered.com/appreviews/<appid>?json=1`
- 参数:`language`(schinese/english/japanese)、`filter=recent`(最新在前)、`num_per_page`(≤100)、`cursor`(首页 `*`)、`purchase_type=all`。
- **没有按日期区间查询的接口** —— 采集只能"最新往旧翻页"。

---

## 3. Phase 2 的核心实证发现(⚠️ 决定了后面所有对齐)

**Steam 的 `recent`+cursor 数据流有一个远低于 `total_reviews` 的深度天花板。** 翻到某一页会返回空页(`reached_end`),而这个"底"通常在几万~约 12–13 万条就到了,和真实总量无关。

- **硬证据**:CS2 中文 `total_reviews=1,404,644`,但数据流只喂到 **42,797(约 3%)** 就到底,最旧日期 2026-03-05。
- 所以**对密集游戏,回采到 2023 是不可能的**(这从"猜测"变成了"实测")。

### 已采到的原始语料(约 560M,gitignored,只在 Mac)
| 游戏 | JA | EN(最旧) | ZH(最旧) |
|---|---|---|---|
| CS2 (730) | 1,943 | 118,372(2026-02-13) | 42,797(2026-03-05) |
| BF2042 (1517290) | 3,160 | 133,203(2021-11-19,到发售) | 31,999(2023-11-15) |
| Elden Ring (1245620) | 5,939 | 77,690(2024-11-22) | 20,292(2025-05-27) |

> 除 BF2042 EN 基本到底外,其余 `reached_floor=False`(没到 JA 的 2023 floor)。

---

## 4. 由此确定的对齐方案(Phase 3 的 `02_` 要实现的)

**在每款游戏的"共同窗口"内做跨语言比较。**
- 共同窗口 = 三语言各自"最旧日期"里**最晚的那个**(交集)。三款都由**中文**卡住左边界:
  - CS2 ≈ 2026-03 → now(~5 个月)
  - BF2042 ≈ 2023-11 → now(~2.7 年)
  - Elden ≈ 2025-05 → now(~15 个月)
- **两个约束并存**:**中文卡窗口的"够不够远"(左边界)**;**日语卡窗口内的"抽多少条"(稀疏)**。
- **对齐做法**:窗口内**按月分箱**,以 **JA 的每月直方图为目标**,EN/ZH 每箱抽 `k × (该月 JA 条数)`(同一个 k 跨所有月/语言,杀掉时间混淆)。箱内随机、固定 seed;JA=0 的月→0;缺口如实记录;抽完**重叠直方图复核**。
- **样本量后果**:CS2 在 k=1 时 ≈ 275/语言(小 → 更适合当 eval/对照);**BF2042 + Elden 扛训练量**。

### 已被否掉的替代方案(别再走回头路)
- ❌ "按比例每段随机抽几百条"当成能补数据 —— 抽样只作用于已下载数据,变不出没采到的评论。
- ❌ "先拉 2023→now 再对齐" —— 逃不过密度天花板。
- ❌ 字数下限过滤减量 —— 客户端过滤不省 API;且引入选择偏差(不公平评论可能是短句怒骂)+ 跨语言不可比(50 个 CJK 字 ≫ 50 个拉丁字母,把语言混淆又带回来了)。

---

## 5. 待办(Phase 3 起)

0. **数据池切分**(所有标注/训练的地基,规格已定):见 `data_split_spec.md`。五个互不重叠角色 `pilot_draft / pilot_prompt / gold / dev / train`;**唯一铁律 = gold 对开发全程隐身**;①②分开只是防自欺;全靠 `data/splits/split_manifest.csv`(review_id→role,已跟踪进 git)焊死,`SPLIT_SEED=20260806`。待建脚本:`02a_make_pilot.py`(切两个 pilot)、`02_align_sample.py`(切 gold/dev/train)。
1. **codebook / 标注规范**(建议先做):把"perceived unfairness"拆成可操作维度(匹配/对局机制、付费与数值、惩罚与封禁、客服与退款、外挂环境……),每维配正例;**最关键是反例**("难 ≠ 不公平""单纯发泄 ≠ 指认不公平")。已定标签方案见 decision_log(2026-07-28):**二元主标签 unfair=1/0 + 单独 `uncertain` 标志位**。
2. **`02_align_sample.py`**:实现 §4 的"共同窗口 + 按月分层降采到 JA"。
3. **人工 gold 标注**(每语言 ≥100,盲标,按冻结的 codebook,**永不训练**)。
4. **LLM 双标注**:弱标注(训练用)+ zero-shot(eval 用);**付费前估成本+确认**。
5. **微调 `xlm-roberta-base`(ASUS)**;三方 eval + 跨语言迁移矩阵。
6. **README**:诚实写"审计→训练"的由来 + 记录 Steam API 深度天花板这条 limitation。

---

## 6. 关键文档索引

- **数据池切分规格(单一事实源):`data_split_spec.md`(仓库根);名单:`data/splits/split_manifest.csv`。**
- codebook 参考文献库:`codebook/codebook_framework_references.md`。
- 决策全记录:`decision_log.md`(仓库根)。
- 训练版指导手册(现行执行文档):`~/Documents/找老板/多语言游戏评论LLM_训练版_项目指导手册_v3_2026-08-04.md`。
- 旧 v2 审计手册(**存档,勿删**,记录原始"仅 API"申请承诺,顶部有 supersede 横幅):`~/Documents/找老板/多语言LLM测量审计_项目指导手册_2026-07-28.md`。
- 长期记忆:`~/.claude/projects/-Users-npc001-Documents----/memory/game-review-llm-project-status.md`。

---

## 7. 协作风格(接手的助手请照做)

- 做**平等的合作者**:客观陈述事实,用户错就直接反驳,不迎合。
- 教学用"教授带学生"模式:**先讲概念 → 布置 1–3 个小任务 → 检查文件/输出 → 让学生解释每个文件/每个数字**。
- **不许猜,要实证**("不能猜")。不确定就写脚本量,或如实说"不知道/没验证"。
- 不过度承诺:能保证"稳定/可续跑/诚实报告",不能保证"一定拉到 2023"——事实也确实证明拉不到。
