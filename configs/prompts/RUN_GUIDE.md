# A/B 试标运行指南（v0.1 vs v0.2）

小白版：三个脚本 = **拼开发输入 → 让模型答题 → 打分**。答案键（人工标签）只用来打分，绝不进模型。

> 2026-08-19 更新：`data/runs/<run-id>/input.jsonl`（正文）与 `answer_key.jsonl`（人工答案、无正文）物理分开；09 不会读取后者。只可建立 development run，不能把 gold 或 stress 放进该目录。

## 一次性准备
1. 在 `.env` 里填 `DEEPSEEK_API_KEY=sk-...`（`.env` 已 gitignore，永不进仓库）。
2. 确认要用的模型 ID（tune==freeze==deploy 必须同一个）。
   当前条件还要求 API 回包中的 `model` 必须为 `deepseek-v4-pro`；若冒烟 run 显示其他值，脚本会停止，不能直接上全量。

## 三步

```bash
# ① 拼开发输入：把 247 条人工答案 ID join 上本机 raw 正文+metadata（无网络、无成本）
.venv/bin/python scripts/08_build_eval_input.py --run-id 2026-08-19_deepseek-v4-pro_v0.2-smoke

# ② 估成本（默认 dry-run，不花一分钱，看行数/token/美元估算）
.venv/bin/python scripts/09_annotate.py \
  --config configs/models/deepseek_v4_pro.json \
  --run-dir data/runs/2026-08-19_deepseek-v4-pro_v0.2-smoke \
  --limit 5

# ③ 确认成本后真跑 —— 先 5 条冒烟，再全量
.venv/bin/python scripts/09_annotate.py \
  --config configs/models/deepseek_v4_pro.json \
  --run-dir data/runs/2026-08-19_deepseek-v4-pro_v0.2-smoke \
  --run --limit 5
# 全量请使用新 run-id，再重跑 08 与 09；不要把 smoke 与 full 混在同一 manifest。
# 对 v0.1 比较时，先另建一份只改 prompt 路径、哈希与 condition_id 的 JSON 条件文件。

# ④ 打分（单版）或 A/B 对比（两版并排）
.venv/bin/python scripts/10_score.py \
  --pred data/runs/2026-08-19_deepseek-v4-pro_v0.2-smoke/responses.jsonl
```

## 关键开关（09_annotate.py）
- `--config configs/models/deepseek_v4_pro.json`：唯一运行条件来源；不要用命令行覆盖模型、URL、温度或价格。
- `--run-dir data/runs/<run-id>`：必须是 08 刚生成的开发集包。
- `--run` 不加 = 永远只估算；`--resume` 仅允许在 config、prompt SHA 与 input SHA 都相同的中断 run 上续跑。
- 三个脚本会自动以其所在仓库为根目录，因此复制到 ASUS 后不必改 `/Users/...`；只有非标准目录才设置 `PROJECT_ROOT=/你的/项目目录`。

## 铁律（脚本已内建）
- 答案键 = 考卷，**只用于打分**，永不进 prompt / 模型上下文。
- 带正文的中间产物写在 `data/runs/`（已 gitignore），**永不进 git**。
- 付费前先 dry-run 估成本、你确认后才 `--run`。
- 冻结前登记：模型确切 ID、prompt 文件 SHA-256、temperature、解析规则。冻结 = Yifan 亲自签名。
