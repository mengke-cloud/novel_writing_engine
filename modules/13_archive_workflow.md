# 13_archive_workflow.md

## 0. 工作流入口

适用阶段：`archive`。

执行者：`agents/novel-agent.md` 调用 `scripts/archive_chapter.py`，归档后由 `agents/updater.md` 处理用户确认的记忆更新。

## 1. 前置条件

- `.agent/status.md` 的 `phase` 与 `current_phase` 均为 `archive`。
- 当前章纲、正文和用户接受记录存在。
- 归档目标不存在，或用户明确要求 `--force`。

## 2. 执行命令

```text
python scripts/archive_chapter.py <project-path> --chapter-plan <章纲> --draft <正文>
```

预览：

```text
python scripts/archive_chapter.py <project-path> --chapter-plan <章纲> --draft <正文> --dry-run
```

## 3. 事务顺序

1. 验证阶段和输入。
2. 检查目标文件覆盖风险。
3. 重新运行归档质量门禁。
4. 门禁通过后复制定稿到 `archives/`。
5. 生成 `.agent/task/chapter-XXXX-archive-update.md`。
6. 将状态更新为“本章已归档，等待确认记忆更新”。
7. 用户确认且 `updater` 完成记忆写入后，再进入下一章的 `chapter` 阶段。

前 3 步失败时不得写入归档、建议或状态。

## 4. 记忆边界

脚本只生成时间线、人物、剧情、伏笔和承诺更新建议，不自动把语义推断写进正式记忆。用户确认后，`updater` 才能写入对应台账。

## 5. 强制规则

- 默认禁止覆盖已有归档。
- 禁止绕过质量门禁。
- 禁止在非 `archive` 阶段运行正式归档。
- 禁止把系统推断直接标记为用户已确认。
- 归档成功后必须保留质量报告和更新建议。
