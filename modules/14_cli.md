# 14_cli.md

## 0. 定位

`scripts/novel.py` 是统一命令行入口，负责将命令和参数转发给单一职责脚本，并原样返回退出码。

## 1. 命令

```text
init -> scripts/init_project.py
detect -> scripts/detect_project.py
repair -> scripts/repair_status.py
context -> scripts/context_builder.py
consistency -> scripts/consistency_check.py
quality -> scripts/quality_gate.py
archive -> scripts/archive_chapter.py
status -> scripts/detect_project.py
next -> scripts/context_builder.py
test -> scripts/test_engine.py
migrate -> scripts/migrate_project.py
analytics -> scripts/analyze_project.py
example -> scripts/create_example_project.py
release -> scripts/release_check.py
```

## 2. 示例

```text
python scripts/novel.py init <project-path> --name <小说名> --genre <题材>
python scripts/novel.py status <project-path>
python scripts/novel.py next <project-path> --output <project-path>/.agent/task/context.md
python scripts/novel.py consistency <project-path> --chapter 12
python scripts/novel.py quality <project-path> --target project
python scripts/novel.py archive <project-path> --chapter-plan <章纲> --draft <正文>
python scripts/novel.py test
python scripts/novel.py migrate <旧项目路径> --dry-run
python scripts/novel.py analytics <项目路径> --output <报告路径>
python scripts/novel.py example <目标目录>
python scripts/novel.py release
```

## 3. 边界

- 统一入口只负责调度，不复制业务逻辑。
- 子命令参数与底层脚本保持一致。
- 底层脚本返回非零退出码时，统一入口必须原样返回。
- 写入命令仍遵守各模块的确认、覆盖和门禁规则。
- CLI 不直接调用语言模型；`next` 只准备下一任务上下文。
