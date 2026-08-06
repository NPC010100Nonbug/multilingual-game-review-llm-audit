# 数据池切分规格(DATA SPLIT SPEC)

> **单一事实源**。任何对话/脚本要给评论分配用途,以本文件为准。
> 实际的 review_id → 角色归属,存在名单层:`data/splits/split_manifest.csv`。
> 建立:2026-08-06。维护人:Yifan(`NPC010100Nonbug`)。

---

## 0. 一句话

把同一个原始池按**用途**切成 5 个互不重叠的角色;每条 review 有且仅有一个角色;
**只有一条隔离是铁律(gold 对开发全程隐身),其余分开只是卫生。** 全靠 review_id 焊死,不靠记性。

---

## 1. 五个角色

| 角色 | manifest 里的 `role` | 规模(每语言) | 用途 | 谁可以碰 | 从哪切 |
|---|---|---|---|---|---|
| 起草 pilot | `pilot_draft` | 30–50 | AI 读它 → 写 codebook 的定义 / inclusion / exclusion / 例子 | 你 + AI | 原始池(对齐前即可) |
| prompt 调试 pilot | `pilot_prompt` | 30–50 | 调 LLM 标注 prompt,调到听话再冻结 | 你 + LLM | 原始池(对齐前即可) |
| **gold 测试集** | `gold` | **≥100** | **盲评**,考 LLM zero-shot / 微调模型准不准 | **开发期谁都不许碰** | 对齐池 |
| dev 集 | `dev` | 50–100 | 选模型 / 调超参 | 训练期 | 对齐池 |
| 训练集 | `train` | 上千 | LLM 弱标注 → 喂微调 | 训练期 | 对齐池(剩余全部) |

> **规模是当前计划,冻结前可再调**;改了就更新本表 + decision_log。

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
Phase 3a(现在,对齐前):
  ① 从原始池切 pilot_draft   → 写 manifest
  ② 从原始池切 pilot_prompt  → 写 manifest(减去 ①)

Phase 3b(02_align_sample.py 之后,从对齐池切,每步都减去 manifest 已有):
  ③ gold  ≥100   ← 先切、切完立即隔离
  ④ dev   50–100
  ⑤ train = 对齐池剩余全部
```

> 为什么 pilot 可以在对齐前切:codebook 定义"什么算不公平"与时间窗口无关(construct 是 window-independent),
> 所以起草不必等对齐。gold/dev/train 必须来自对齐池(跨语言可比)。
> 无论 pilot 是否落在对齐窗口内,**后减前**都能保证它不会溜进 gold/train。

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

- [ ] `scripts/02a_make_pilot.py`:切 `pilot_draft` + `pilot_prompt`,写 manifest(Phase 3a,待建)
- [ ] `scripts/02_align_sample.py`:对齐池 + 切 `gold`/`dev`/`train`(Phase 3b,待建)
- [ ] `data/splits/split_manifest.csv`:待第一次运行生成
