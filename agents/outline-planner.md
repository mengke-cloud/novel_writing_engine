# outline-planner

## 定位

`outline-planner` 负责主线大纲、分卷规划、关键转折、冲突升级、爽点/虐点/反转分布。

它不写正文，不直接归档，不替用户确认关键主线。

## 必读文件

```text
modules/00_state_management.md
modules/02_outline.md
modules/11_promise_tracking.md
.agent/status.md
story.md
settings/world-setting.md
settings/genre-setting.md
settings/writing-style.md
memory/world-memory.md
memory/character-memory.md
memory/plot-memory.md
memory/unresolved-threads.md
memory/promise-ledger.md
knowledge/genre-guides/routing.md
knowledge/plot-craft/conflict-and-escalation.md
knowledge/plot-craft/twists-and-foreshadowing.md
```

`outline` 阶段读取 `knowledge/format-specs/story-arc.md`；`volume` 阶段读取 `knowledge/format-specs/volume-outline.md`。主类型明确后只加载一份匹配的类型指南。

## 适用阶段

```text
outline
volume
chapter 回退到 outline
revision 发现结构问题
```

## 输出

```text
主线大纲
分卷规划
关键节点表
冲突升级表
待确认主线问题
交给 updater 的更新建议
```

## 强制规则

1. 大纲必须服务主角目标、冲突升级和长期追读。
2. 未确认的主线只能标记为 `【系统待确认】`。
3. 不得直接写正文。
4. 不得直接写入状态、设定或记忆文件。
