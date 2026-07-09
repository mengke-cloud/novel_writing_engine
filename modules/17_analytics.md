# 17_analytics.md

## 0. 定位

用于分析章节长度、人物出场、冲突信号、剧情承诺和质量门禁趋势。

## 1. 执行

```text
python scripts/novel.py analytics <project-path>
python scripts/novel.py analytics <project-path> --output <报告路径>
```

## 2. 数据来源

- 优先统计 `archives/`；没有归档时统计 `drafts/`。
- 人物名称来自人物状态台账和人物设定文件。
- 承诺状态来自 `memory/promise-ledger.md`。
- 质量趋势来自 `.agent/reports/`。

## 3. 指标边界

冲突密度是词语信号，不等同于戏剧张力；人物出场是姓名匹配，不自动合并别名；质量分数是门禁完成度，不代表文学价值。Agent 不得用单一指标要求机械改稿。

## 4. 输出

报告包括章节统计、人物出场章数、承诺回收率、质量分数趋势和方法限制。
