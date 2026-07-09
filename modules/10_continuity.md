# 10_continuity.md

## 0. 工作流入口

适用阶段：`chapter`、`draft`、`revision`、`archive`。

必读文件：

```text
memory/timeline.md
memory/character-state-ledger.md
memory/plot-memory.md
memory/character-memory.md
当前章纲
当前正文
```

## 1. 系统目标

追踪事件先后、人物位置、伤势、物品、能力、目标和知情范围，防止长篇写作中出现前后矛盾。

## 2. 一致性检查

```text
python scripts/consistency_check.py <project-path> --chapter <当前章节>
```

机器检查负责条目结构、ID、章节顺序和状态新鲜度。Agent 负责判断正文事实是否与台账内容语义冲突。

## 3. 章节结束差异

归档前必须整理：

```text
新增事件：
时间推进：
地点变化：
人物身体变化：
人物情绪变化：
物品获得或失去：
能力获得、消耗或限制：
新增知情内容：
关系和目标变化：
```

没有变化的字段写“无”，不得根据常识擅自补全。

## 4. 阻断规则

- 重复事件或人物 ID。
- 时间线章节倒序。
- 人物状态引用未来章节。
- 人物位置、伤势、物品、能力或知情范围与正文直接冲突。
- 归档后应更新但未生成状态差异。

## 5. 输出格式

```text
一致性结论：
阻断项：
重要项：
章节状态差异：
建议更新时间线：
建议更新人物状态：
```
