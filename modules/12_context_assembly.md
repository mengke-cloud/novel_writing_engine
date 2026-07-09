# 12_context_assembly.md

## 0. 工作流入口

适用于所有阶段，由 `agents/novel-agent.md` 在分派任务前执行。

## 1. 系统目标

根据项目状态和当前任务组装最小充分上下文，减少无关文件占用，避免整库加载，并保留完整文件选择清单。

## 2. 执行命令

```text
python scripts/context_builder.py <project-path>
```

正文、改稿或归档时显式指定当前文件：

```text
python scripts/context_builder.py <project-path> --chapter-plan <章纲> --draft <正文> --max-chars 30000 --output .agent/task/context.md
```

## 3. 优先级

```text
优先级 0：
  .agent/status.md、story.md、状态模块、显式指定的当前章纲和正文。

优先级 1：
  当前阶段对应的设定、记忆、台账、模块和知识规范。

优先级 2：
  最近两章归档等辅助上下文。
```

高优先级文件先进入预算。预算耗尽后，低优先级文件标记为 `skipped_budget`；文件只纳入一部分时标记为 `truncated`。

## 4. 阶段路由

- `setup`：基础设定、世界观、人物。
- `outline / volume`：世界观、人物、主线、剧情承诺。
- `chapter`：人物状态、时间线、剧情进展、承诺和追读反馈。
- `draft`：章纲、世界规则、文风、人物状态、时间线和承诺。
- `revision`：当前正文、事实约束、一致性、语言和质量规范。
- `retention`：当前正文、类型承诺、钩子、承诺和历史反馈。
- `archive`：当前章纲正文、全部待更新台账和归档门禁。

## 5. 强制规则

1. 禁止整库加载 `knowledge/`。
2. 禁止只凭聊天记忆选择阶段。
3. 当前章纲和正文路径可确定时必须显式传入。
4. `missing` 文件必须向总调度报告，不得假装已读取。
5. 上下文包是任务输入快照，不是项目事实源，不得反向覆盖原文件。

## 6. 输出格式

上下文包必须包含阶段、任务、字符预算、文件清单、选择原因、纳入状态和实际内容。
