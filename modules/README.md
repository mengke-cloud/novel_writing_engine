# modules 工作流规范

## 目标

`modules/` 下的文件不是普通说明文，而是可执行工作流。

每个模块必须回答：

```text
什么时候用？
开始前读什么？
需要什么输入？
产出什么结果？
按什么步骤执行？
完成后如何检查？
哪些事情禁止做？
需要更新哪些状态或记忆？
```

## 标准结构

除 `00_state_management.md` 外，每个模块最终都应包含以下章节：

```text
# 模块文件名

## 1. 模块定位

## 2. 适用阶段

## 3. 必读文件

## 4. 输入要求

## 5. 输出结果

## 6. 执行步骤

## 7. 检查清单

## 8. 禁止事项

## 9. 状态与记忆更新建议

## 10. 输出格式
```

## 阶段映射

```text
01_worldbuilding.md -> setup
02_outline.md -> outline, volume
03_character.md -> setup, outline
04_chapter_design.md -> chapter
05_prose_writing.md -> draft
06_revision.md -> revision
07_reader_retention.md -> retention
08_anti_ai_style.md -> draft, revision
09_quality_gate.md -> revision, retention, archive
10_continuity.md -> chapter, draft, revision, archive
11_promise_tracking.md -> outline, volume, chapter, retention, archive
12_context_assembly.md -> 所有阶段
13_archive_workflow.md -> archive
14_cli.md -> 命令行入口
15_testing.md -> 引擎变更与发布
16_migration.md -> legacy, partial
17_analytics.md -> 数据分析
18_release.md -> 稳定版发布
```

## Agent 映射

```text
01_worldbuilding.md -> agents/worldbuilder.md
02_outline.md -> agents/outline-planner.md
03_character.md -> agents/character-designer.md
04_chapter_design.md -> agents/chapter-planner.md
05_prose_writing.md -> agents/writer.md
06_revision.md -> agents/revision-editor.md
07_reader_retention.md -> agents/reader-reviewer.md
08_anti_ai_style.md -> agents/anti-ai-editor.md
09_quality_gate.md -> agents/revision-editor.md, agents/reader-reviewer.md, agents/novel-agent.md
10_continuity.md -> agents/chapter-planner.md, agents/writer.md, agents/revision-editor.md, agents/updater.md
11_promise_tracking.md -> agents/outline-planner.md, agents/chapter-planner.md, agents/reader-reviewer.md, agents/updater.md
12_context_assembly.md -> agents/novel-agent.md
13_archive_workflow.md -> agents/novel-agent.md, agents/updater.md
14_cli.md -> 用户或 agents/novel-agent.md
15_testing.md -> 开发者与发布流程
16_migration.md -> agents/novel-agent.md
17_analytics.md -> agents/novel-agent.md
18_release.md -> 开发者与发布流程
```

## 必读文件规则

所有模块默认必须读取：

```text
modules/00_state_management.md
.agent/status.md
story.md
```

如果 `.agent/task/context.md` 存在，执行 Agent 先读取其中的文件清单和选择原因，再读取清单指向的原始文件。上下文包不替代原始项目文件。

涉及设定时读取：

```text
settings/world-setting.md
settings/genre-setting.md
settings/writing-style.md
memory/world-memory.md
memory/character-memory.md
memory/plot-memory.md
```

涉及正文、改稿、追读时读取：

```text
memory/style-memory.md
memory/foreshadowing-memory.md
memory/unresolved-threads.md
memory/reader-feedback.md
```

## 输出边界

模块可以输出草案、检查结果、建议和更新建议。

模块不得直接写入：

```text
.agent/status.md
settings/
memory/
archives/
```

需要写入状态、设定或记忆时，模块必须输出“更新建议”，由 `novel-agent` 形成更新指令，再交给 `updater` 执行。

## 知识库调用

模块规定工作流，`knowledge/` 提供可复用的方法和格式。执行模块时按 `knowledge/README.md` 的 Agent 路由加载知识：

1. 先读模块、项目设定和记忆。
2. 再读当前产物对应的格式规范。
3. 只在任务需要时加载人物、情节或场景知识。
4. 类型指南先路由后加载，禁止全库加载。
5. 知识与项目事实冲突时，以已确认项目记忆为准。

## 更新建议格式

```text
更新对象：
更新原因：
更新内容：
是否用户已确认：
影响范围：
```

## 最小验收标准

模块改造完成后，必须满足：

```text
1. 明确适用 phase。
2. 明确对应 agent。
3. 明确输入文件和输出结果。
4. 明确执行步骤。
5. 明确检查清单。
6. 明确禁止事项。
7. 不直接写状态、设定、记忆或归档文件。
```
