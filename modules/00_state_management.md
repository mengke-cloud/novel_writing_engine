# 00_state_management.md

## 1. 模块定位

本模块负责定义 `novel-writing-engine` 的项目状态系统。

`.agent/status.md` 是小说项目的唯一状态源。所有继续写作、阶段推进、文件更新、记忆更新和模块调度，都必须先读取并遵守该文件。

本模块不负责创作正文，不负责生成大纲，不负责设计人物。它只负责规定状态如何记录、如何判断、如何更新、如何修复。

---

## 2. 状态源文件

状态源文件固定为：

```text
.agent/status.md
```

每次进入小说项目任务前，必须先读取：

```text
story.md
.agent/status.md
settings/world-setting.md
settings/genre-setting.md
settings/writing-style.md
memory/world-memory.md
memory/character-memory.md
memory/plot-memory.md
memory/style-memory.md
memory/foreshadowing-memory.md
memory/unresolved-threads.md
memory/reader-feedback.md
memory/README.md
```

如果部分文件缺失，不得假装已经读取。必须先标记为项目结构缺失，并进入修复流程。

---

## 3. 必备字段

`.agent/status.md` 必须包含以下字段：

```text
project_name:
engine_version:
skill_version:
created_at:
updated_at:
phase:
current_phase:
current_volume:
current_chapter:
current_task:
last_task:
next_action:
blocked_reason:
```

字段含义：

```text
project_name:
  小说项目名称。

engine_version:
  当前项目初始化或同步时使用的 novel-writing-engine 版本。

skill_version:
  兼容旧字段。当前阶段保留，与 engine_version 保持一致。

created_at:
  项目初始化日期。

updated_at:
  最近一次状态更新日期。

phase:
  当前阶段。新版字段，调度时优先读取。

current_phase:
  兼容旧字段。当前阶段保留，与 phase 保持一致。

current_volume:
  当前卷编号。未进入分卷前为 0。

current_chapter:
  当前章节编号。未进入章节前为 0。

current_task:
  当前任务标识。用于说明当前正在推进什么。

last_task:
  最近完成的任务。兼容旧字段。

next_action:
  下一步动作。必须具体到可执行任务。

blocked_reason:
  阻塞原因。无阻塞时留空。
```

---

## 4. 字段兼容规则

读取阶段时优先使用新版字段：

```text
phase
current_task
next_action
engine_version
```

兼容旧字段：

```text
current_phase
last_task
skill_version
```

如果新版字段与旧字段同时存在但不一致：

```text
phase != current_phase -> 以 phase 为准，并将 current_phase 标记为待同步
engine_version != skill_version -> 以 engine_version 为准，并将 skill_version 标记为待同步
current_task 与 last_task 不一致 -> 不强制修复，二者含义不同
```

---

## 5. 阶段枚举

`phase` 只能使用以下值：

```text
setup
outline
volume
chapter
draft
revision
retention
archive
paused
```

禁止发明新的阶段值。确需扩展阶段，必须先更新本模块、`templates/status.md.template` 和 `agents/novel-agent.md`。

---

## 6. 阶段定义

```text
setup:
  基础设定阶段。用于确认题材、世界观、主角目标、核心卖点、写作风格。

outline:
  主线大纲阶段。用于生成或修订整本书的大方向、核心冲突、主要转折。

volume:
  分卷规划阶段。用于规划当前卷目标、卷内冲突升级、卷末结果。

chapter:
  章节细纲阶段。用于规划当前章目标、冲突、信息增量、爽点、章尾钩子。

draft:
  正文生成阶段。用于根据章节细纲写正文、续写或扩写。

revision:
  改稿阶段。用于结构修复、逻辑修复、节奏压缩、语言润色和去 AI 味。

retention:
  追读检查阶段。用于检查爽点密度、疲劳点、读者期待和章末钩子。

archive:
  归档阶段。用于保存定稿章节、更新记忆、推进到下一章。

paused:
  暂停阶段。用于目标不明确、用户暂停、信息不足或存在阻塞。
```

---

## 7. 阶段流转规则

标准流转：

```text
setup -> outline -> volume -> chapter -> draft -> revision -> retention -> archive -> chapter
```

允许回退：

```text
outline -> setup
volume -> outline
chapter -> volume
draft -> chapter
revision -> draft
retention -> revision
archive -> retention
```

回退条件：

```text
1. 用户否定已生成内容。
2. 发现关键设定冲突。
3. 当前阶段缺少必要输入。
4. 章节正文与细纲明显不一致。
5. 追读检查发现必须重写的结构问题。
```

禁止行为：

```text
1. setup 未完成时直接进入 draft。
2. 没有章节细纲时直接写正文。
3. 用户未确认关键设定时进入正式大纲或正文。
4. archive 未更新记忆就推进下一章。
```

---

## 8. 阶段进入条件

```text
setup:
  项目刚初始化，或基础设定缺失，或用户要求重新讨论设定。

outline:
  已确认基础设定，且需要整本书主线规划。

volume:
  已有主线大纲，且需要规划当前卷。

chapter:
  已有当前卷目标，且需要规划当前章节。

draft:
  已有当前章节细纲，且用户确认可以写正文。

revision:
  已有正文草稿，且需要改稿、润色或去 AI 味。

retention:
  已有可读章节版本，且需要读者视角检查。

archive:
  当前章节已被用户接受，准备归档和更新记忆。

paused:
  用户暂停、目标不明确、缺少关键信息或状态损坏。
```

---

## 9. 状态更新条件

以下情况必须更新 `.agent/status.md`：

```text
1. phase 发生变化。
2. current_volume 发生变化。
3. current_chapter 发生变化。
4. current_task 发生变化。
5. next_action 发生变化。
6. blocked_reason 发生变化。
7. 用户确认或否定关键设定。
8. 章节从 draft 进入 revision、retention 或 archive。
9. archive 完成后推进到下一章。
```

每次状态更新必须同步更新：

```text
updated_at
last_task
next_action
```

如果更新 `phase`，必须同步 `current_phase`，保持兼容。

---

## 10. 记忆更新条件

以下情况必须更新 `memory/`：

```text
1. 世界观规则被用户确认 -> memory/world-memory.md
2. 人物身份、目标、关系或状态变化 -> memory/character-memory.md
3. 主线事件实际发生 -> memory/plot-memory.md
4. 文风偏好或禁用表达被确认 -> memory/style-memory.md
5. 新增或回收伏笔 -> memory/foreshadowing-memory.md
6. 新增悬念或待解决线索 -> memory/unresolved-threads.md
7. 出现追读风险、爽点不足或疲劳点 -> memory/reader-feedback.md
8. 记忆写入格式或职责不清 -> memory/README.md
```

禁止只在聊天中记住这些信息。凡是影响后续创作的内容，都必须写入项目文件。

---

## 11. 修复规则

如果 `scripts/detect_project.py` 返回 `needs_repair`：

```text
1. 读取检测结果中的 missing_status_fields。
2. 对照本模块补齐缺失字段。
3. 不得改动正文、归档章节和已确认设定。
4. 修复后重新运行 detect_project.py。
5. 检测结果为 existing 后，才能继续创作。
```

如果 `phase` 或 `current_phase` 缺失：

```text
1. 优先从现有章节、草稿、归档和 next_action 判断。
2. 无法判断时设为 paused。
3. 在 blocked_reason 中写明需要用户确认当前阶段。
```

如果 `next_action` 缺失：

```text
1. 根据 phase 生成一个具体动作。
2. 动作必须可执行，不得只写“继续创作”。
3. 示例：与用户确认主角目标；生成第 1 卷大纲；设计第 3 章细纲。
```

---

## 12. 输出格式

当需要汇报状态时，使用以下格式：

```text
当前阶段：
判断依据：
当前任务：
下一步动作：
需要确认：
将读取文件：
将更新文件：
```

当只是修复状态文件时，不要输出小说设定草案，不要推进剧情。

---

## 13. 最小验收标准

一个小说项目的状态系统合格，必须满足：

```text
1. scripts/detect_project.py 返回 existing。
2. .agent/status.md 包含必备字段。
3. phase 属于合法阶段枚举。
4. next_action 是具体可执行动作。
5. story.md、settings/、memory/ 存在。
6. novel-agent 能根据 phase 找到下一步模块。
```
