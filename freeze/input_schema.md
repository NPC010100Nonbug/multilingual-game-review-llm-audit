# 标注 / 模型输入 schema(冻结前定死)— §9.3 "metadata / 输入 schema"

> **状态:草稿,待 Yifan 批准后随 v1.0 一起冻结。**
> 目的:把**喂给人工标注**和**喂给模型**的字段定成**同一套**(人机同权),避免 gold 里编码了模型
> 拿不到的信号 → 评估不公。另定一个 **text-only 基线**作对照。
> 建立:2026-08-10。依据:decision_log 2026-08-08 rev5 的"metadata 人机同权"决定。

---

## 1. 为什么要这份文件

codebook §4.0 + rev5 规则 #3 让**人工标注用到了 metadata**(反讽 §5-F 用 `voted_up`/`votes_funny`,
bare-word 规则用 `voted_up`)。若人看得到、模型看不到 → gold 天然含模型无法企及的信号 → 评估虚高/虚低。
**解法:模型推理时喂同一组 metadata。** 本文件把"同一组"定死。

---

## 2. 主输入(人工标注 + 模型,两边完全一致)

| 字段 | 类型 | 说明 | 给人 | 给模型 |
|---|---|---|---|---|
| `review` | str | 评论正文(唯一文本输入) | ✅ | ✅ |
| `voted_up` | bool | 荐/不荐(反讽、bare-word 规则要用) | ✅ | ✅ |
| `votes_funny` | int | "欢乐"数(反讽交叉验证) | ✅ | ✅ |
| `votes_up` | int | "有用"数 | ✅ | ✅ |
| `received_for_free` | bool | 是否免费获取 | ✅ | ✅ |
| `steam_purchase` | bool | 是否 Steam 内购买 | ✅ | ✅ |
| `weighted_vote_score` | float | 加权评分 | ✅ | ✅ |
| `written_during_early_access` | bool | 是否抢先体验期所写 | ✅ | ✅ |
| `appid` | str | 游戏(730/1517290/1245620) | ✅ | ✅ |
| `lang` | str | en/zh/ja | ✅ | ✅ |

> 语言字段给模型:zero-shot 时可作 prompt 语言提示;微调时按需。**保持人机一致即可。**

---

## 3. text-only 基线(对照臂,必须单独跑)

只喂 `review` + `appid` + `lang`,**不给任何 metadata**。
用途:量化"metadata 到底贡献了多少"——若 text-only 与全字段差距很小,说明 gold 对 metadata 依赖低,
跨语言比较更稳;差距大则需在论文里明确讨论。**两臂都在冻结后的 gold 上评估。**

---

## 4. 明确排除(绝不喂给人 / 模型)

| 字段 | 为什么排除 |
|---|---|
| `steamid` / `personaname` / `profile_url` / 任何作者身份 | 隐私红线;当前 worksheet 已不含,采集下游也须 drop |
| `curated_tag` / `curated_reason` | **目的性补样的种子标签**——喂了就等于直接泄漏"我本来想让它是哪个 facet",标注/评估作废 |
| `provenance` | 内部来源(random / purposive 批次),仅审计用,喂了会引入非构念线索 |
| `original_label` / `adjudicated_label` / 任何既有标签 | 盲标 / 评估时当然不给 |

---

## 5. 冻结检查(过了才随 v1.0 冻结)

- [ ] 人工标注实际用到的 metadata ⊆ §2 主输入(无"人偷偷多看了一个字段")
- [ ] 模型推理输入 = §2 主输入(逐字段核对,人机对等)
- [ ] text-only 基线臂已在管线里预留(§3)
- [ ] §4 排除字段在喂给标注/模型前被程序性剔除(不靠记性)
