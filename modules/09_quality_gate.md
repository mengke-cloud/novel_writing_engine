# 09_quality_gate.md

## 0. 工作流入口

适用阶段：

```text
revision
retention
archive
```

对应执行者：

```text
revision -> agents/revision-editor.md
retention -> agents/reader-reviewer.md
archive -> agents/novel-agent.md 调用 scripts/quality_gate.py
```

必读文件：

```text
.agent/status.md
knowledge/format-specs/chapter-quality-checklist.md
当前章节细纲
当前章节正文
memory/timeline.md
memory/character-state-ledger.md
memory/promise-ledger.md
```

输出结果：

```text
质量分数
阻断项
重要项
优化项
门禁决定
```

禁止事项：

```text
不得用分数替代作者审美判断
不得自动修改正文
存在阻断项时不得进入 archive
不得因重要项或优化项单独阻止用户确认的归档
```

## 1. 门禁层级

```text
阻断：
  项目结构损坏、状态非法、正文缺失或为空、存在未完成占位、
  章纲仍有待确认内容、归档前关键设定仍未确认。
  时间线倒序、人物状态引用未来章节、承诺状态非法或回收记录缺失。

重要：
  章纲关键部分缺失、正文疑似不完整、存在需要人工确认的一致性风险。

优化：
  标题、局部重复、表达和阅读体验的非强制改进。
```

## 2. 执行命令

项目完整性检查：

```text
python scripts/quality_gate.py <project-path> --target project
```

正文阶段检查：

```text
python scripts/quality_gate.py <project-path> --target draft --chapter-plan <章纲> --draft <正文>
```

归档门禁与报告：

```text
python scripts/quality_gate.py <project-path> --target archive --chapter-plan <章纲> --draft <正文> --report <报告路径>
```

脚本退出码：

```text
0 = 无阻断项，门禁通过
1 = 存在阻断项，门禁未通过
```

## 3. 人工质量复核

脚本负责确定性检查。人物动机、情节效果、类型兑现、语言自然度等语义质量，仍由对应 Agent 按章节质量检查表复核，并将结果加入同一三级问题列表。

## 4. 阶段流转

```text
revision:
  运行正文门禁，修复阻断项和用户选择的重要项。

retention:
  在机器检查基础上补充读者体验复核。

archive:
  必须重新运行归档门禁。
  门禁必须合并 scripts/consistency_check.py 的结果。
  退出码为 0 后才允许归档正文、更新记忆和推进章节。
  退出码为 1 时回退到 revision，并把阻断原因写入 blocked_reason。
```

## 5. 输出格式

报告必须使用 `templates/quality-report.md.template` 定义的结构，至少包含检查目标、时间、结论、分数、三级问题和门禁决定。
