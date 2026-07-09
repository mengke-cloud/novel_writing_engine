# 18_release.md

## 0. 定位

定义稳定版发布检查、安装、兼容性和示例项目要求。

## 1. 发布检查

```text
python scripts/release_check.py
```

检查版本一致性、必需文件、Skill frontmatter、类型指南、完整测试及示例项目。

## 2. 安装

Windows：

```text
powershell -ExecutionPolicy Bypass -File install.ps1
```

macOS / Linux：

```text
sh install.sh
```

目标已存在时默认拒绝；明确更新时使用 Windows `-Update` 或 shell `--update`。

## 3. 稳定版标准

- `VERSION`、Skill、README 和脚本版本一致。
- 完整测试全部通过。
- 示例项目能够生成并通过项目门禁。
- 迁移、归档和安装默认不删除用户文件。
- 兼容范围记录在 `COMPATIBILITY.md`。

## 4. 禁止事项

发布检查失败时不得发布。不得手工跳过版本不一致、缺失文件或示例项目失败。
