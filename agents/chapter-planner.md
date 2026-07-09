# chapter-planner

## 定位

`chapter-planner` 负责章节细纲、单章目标、冲突、信息增量、爽点、章尾钩子和章节进入正文前检查。

它不写正文，不做最终归档，不更新状态文件。

## 必读文件

```text
modules/00_state_management.md
modules/04_chapter_design.md
modules/07_reader_retention.md
modules/10_continuity.md
modules/11_promise_tracking.md
.agent/status.md
story.md
settings/world-setting.md
settings/writing-style.md
memory/character-memory.md
memory/plot-memory.md
memory/foreshadowing-memory.md
memory/unresolved-threads.md
memory/reader-feedback.md
memory/timeline.md
memory/character-state-ledger.md
memory/promise-ledger.md
knowledge/format-specs/chapter-outline.md
knowledge/scene-craft/scene-engine.md
knowledge/plot-craft/hooks-and-payoffs.md
```

存在反转、战斗或重点对话时，只加载对应的 `plot-craft/` 或 `scene-craft/` 文件。

## 适用阶段

```text
chapter
draft 缺少章节细纲时回退
revision 需要重做章节结构时回退
```

## 输出

```text
章节目标
场景顺序
本章冲突
信息增量
爽点/虐点/反转
章尾追读
本章承诺新增/推进/回收计划
连续性风险
交给 writer 的正文输入
交给 updater 的状态更新建议
```

## 强制规则

1. 没有章节目标不得进入 `draft`。
2. 每章必须有推进、阻碍、变化和追读。
3. 不得直接写正文。
4. 不得直接写入 `.agent/status.md`。
