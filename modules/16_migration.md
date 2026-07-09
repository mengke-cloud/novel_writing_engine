# 16_migration.md

## 0. 工作流入口

适用于检测结果为 `legacy`、`partial`，或旧项目缺少当前标准文件时。

## 1. 执行

预览：

```text
python scripts/novel.py migrate <project-path> --dry-run
```

正式迁移：

```text
python scripts/novel.py migrate <project-path>
```

## 2. 安全顺序

1. 检测旧项目和可识别字段。
2. 输出将创建的目录、文件及保留资料。
3. 正式迁移前创建 `.migration-backups/` ZIP 备份。
4. 只创建缺失的新文件，不覆盖原文件。
5. 保留 `story.yaml`，并复制旧人物状态和剧情钩子到 legacy 文件。
6. 修复旧状态缺失字段，再运行项目检测、项目门禁和一致性检查。
7. 生成 `.agent/migration-report.md`。

## 3. 字段转换

```text
title / name / project_name -> project_name
type / genre -> genre
status / current_phase / phase -> phase
current_volume -> current_volume
current_chapter -> current_chapter
```

无法识别的阶段设置为 `paused`。未迁移的语义内容保留在备份或 legacy 文件中，等待用户确认。

## 4. 禁止事项

- 禁止迁移 Skill 根目录。
- 禁止删除或覆盖旧文件。
- 禁止将旧资料中的推断自动标记为用户已确认。
- 禁止验证失败后删除备份或迁移报告。
