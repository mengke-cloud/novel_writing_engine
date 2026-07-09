# 兼容性

## Python

- 支持 Python 3.11、3.12、3.13。
- 核心脚本只使用 Python 标准库。
- Windows 是主要测试环境，GitHub Actions 使用 `windows-latest` 和 Python 3.11。

## 项目版本

- `0.18.0` 与 `1.0.0` 项目结构可直接使用。
- `0.4.0` 至 `0.16.0` 项目可先运行检测和状态修复，再补齐缺失台账。
- 包含 `story.yaml` 的旧项目使用 `novel.py migrate`。
- 迁移不会删除或覆盖旧文件，并在 `.migration-backups/` 创建 ZIP 备份。

## 状态字段

当前标准字段以 `modules/00_state_management.md` 为准。`current_phase` 和 `last_task` 继续作为兼容字段保留；新流程优先读取 `phase`、`current_task` 和 `next_action`。

## 不兼容情况

- 自定义阶段值不会自动映射，迁移后进入 `paused` 等待确认。
- 无法确定含义的旧人物、剧情和伏笔内容只保留为 legacy 文件，不自动写入正式记忆。
- 第三方修改过的非标准目录需要先运行 `migrate --dry-run` 检查计划。
