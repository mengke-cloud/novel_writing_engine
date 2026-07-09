# novel_writing_engine 迭代规范

本文档用于指导协作者为 `novel_writing_engine` 增加或修改知识库、Agent 规则、模块流程、脚本和测试。目标是让不同用户更新时保持同一套结构、质量标准和兼容性。

## 1. 迭代原则

1. 不破坏现有项目。
   - 不覆盖用户已有 `story.md`、`.agent/status.md`、`settings/`、`memory/`、`archives/`。
   - 迁移和修复类操作必须先支持 `--dry-run`。

2. 项目事实优先。
   - 用户当前明确要求 > 用户已确认设定 > 项目记忆 > 类型知识 > 通用知识。
   - 新知识只能作为建议，不能覆盖已确认设定。

3. 按需加载知识。
   - 禁止一次性读取整个 `knowledge/`。
   - 通过 `knowledge/README.md` 和 `knowledge/genre-guides/routing.md` 路由到具体文件。

4. 规则必须可测试。
   - 新增路由、脚本、质量门禁、上下文选择逻辑时，必须同步增加或修改测试。

5. 文档、Agent、脚本保持一致。
   - `SKILL.md`、`modules/`、`agents/`、`scripts/`、`tests/` 之间不能互相矛盾。

## 2. 目录职责

```text
novel_writing_engine/
  SKILL.md                       # Skill 总入口和触发说明
  README.md                      # 用户说明
  CHANGELOG.md                   # 版本变更记录
  UPDATE_PROTOCOL.md             # 更新协议
  agents/                        # 多 Agent 职责
  modules/                       # 工作流模块
  scripts/                       # 自动化脚本
  templates/                     # 初始化项目模板
  knowledge/                     # 可复用写作知识库
  project_rules/                 # 用户长期偏好
  tests/                         # 自动化测试
```

## 3. 知识库新增规范

### 3.1 知识分类

新增知识优先放入以下目录：

```text
knowledge/genre-guides/       # 题材指南
knowledge/anti-ai/            # 反 AI 味规则
knowledge/scene-craft/        # 场景写法
knowledge/plot-craft/         # 剧情技巧
knowledge/character-craft/    # 角色设计
knowledge/title-craft/        # 标题设计
knowledge/format-specs/       # 输出格式规范
```

不要把多个领域混在一个文件里。例如“玄幻题材规则”和“玄幻反 AI 句式”应分别放入：

```text
knowledge/genre-guides/xuanhuan.md
knowledge/anti-ai/xuanhuan.md
```

### 3.2 文件命名

使用小写英文、数字和连字符：

```text
urban-cultivation.md
suspense-crime.md
opening-hooks.md
villain-types.md
web-title-patterns.md
```

避免：

```text
玄幻规则.md
new file.md
scene_技巧.md
```

### 3.3 知识文件结构

每个知识文件建议使用以下结构：

```markdown
# 文件标题

> 适用范围：说明适用题材、任务或阶段。

## 使用时机

- 什么时候读这个文件
- 什么时候不要读这个文件

## 核心规则

1. 规则一
2. 规则二
3. 规则三

## 可执行方法

- 给出可直接用于生成、改稿或检查的步骤。

## 正反例

错误写法：

正确写法：

## 与项目设定冲突时

以用户已确认设定和项目记忆为准。
```

## 4. 题材指南更新规范

新增题材时，至少修改：

```text
knowledge/genre-guides/README.md
knowledge/genre-guides/routing.md
knowledge/genre-guides/<genre>.md
tests/test_genre_guides.py
tests/test_context_builder.py
```

`routing.md` 必须包含：

```text
题材名称
关键词
对应文件
适用任务
冲突判断规则
```

示例：

```text
urban-cultivation:
  keywords: 都市修仙, 灵气复苏, 高武都市, 异能觉醒
  guide: knowledge/genre-guides/urban-cultivation.md
  anti_ai: knowledge/anti-ai/urban-cultivation.md
  use_for: worldbuilding, outline, chapter, prose, revision
```

## 5. 反 AI 知识更新规范

新增反 AI 规则时，至少修改：

```text
knowledge/anti-ai/README.md
knowledge/anti-ai/<topic-or-genre>.md
modules/08_anti_ai_style.md
agents/anti-ai-editor.md
tests/test_context_builder.py
```

反 AI 规则必须满足：

1. 不改变剧情。
2. 不改变人物关系。
3. 不改变世界观规则。
4. 不改变主角目标。
5. 给出具体病句和替代写法。

推荐格式：

```markdown
## 高频问题

### 问题：机械总结

错误写法：
他意识到，这一切都说明命运已经发生了改变。

替代写法：
他看着掌心那道还没愈合的伤口，半天没说话。
```

## 6. 场景、剧情、角色、标题知识更新规范

### 6.1 场景写法

目录：

```text
knowledge/scene-craft/
```

需要同步检查：

```text
modules/04_chapter_design.md
modules/05_prose_writing.md
agents/chapter-planner.md
agents/writer.md
```

### 6.2 剧情技巧

目录：

```text
knowledge/plot-craft/
```

需要同步检查：

```text
modules/02_outline.md
modules/04_chapter_design.md
modules/07_reader_retention.md
agents/outline-planner.md
agents/chapter-planner.md
agents/reader-reviewer.md
```

### 6.3 角色设计

目录：

```text
knowledge/character-craft/
```

需要同步检查：

```text
modules/03_character.md
agents/character-designer.md
tests/test_context_builder.py
```

### 6.4 标题设计

目录：

```text
knowledge/title-craft/
```

需要同步检查：

```text
agents/novel-agent.md
agents/outline-planner.md
README.md
```

## 7. 模块更新规范

修改 `modules/` 时必须做到：

1. 明确模块输入。
2. 明确模块输出。
3. 明确何时读取哪些知识文件。
4. 明确不能读取哪些文件。
5. 明确是否需要用户确认。
6. 明确是否需要调用脚本。

模块文件里不要堆大量知识正文，只写调用规则。知识正文放入 `knowledge/`。

## 8. Agent 更新规范

修改 `agents/` 时必须保持职责边界。

```text
novel-agent.md          # 调度，不直接写设定、记忆、正文
worldbuilder.md         # 世界观
character-designer.md   # 人物
outline-planner.md      # 大纲和分卷
chapter-planner.md      # 章节细纲
writer.md               # 正文
revision-editor.md      # 改稿
anti-ai-editor.md       # 去 AI 味
reader-reviewer.md      # 追读和读者反馈
updater.md              # 写入状态、设定、记忆
```

禁止：

1. `novel-agent` 直接写入 `settings/`、`memory/`、`.agent/status.md`。
2. `updater` 自行设计剧情或生成正文。
3. `writer` 私自改变已确认设定。
4. `anti-ai-editor` 借去 AI 味改变剧情。

## 9. 脚本更新规范

修改 `scripts/` 时，必须同步考虑测试。

常见脚本职责：

```text
context_builder.py      # 按阶段和题材选择上下文
quality_gate.py         # 质量门禁
consistency_check.py    # 时间线、人物状态、承诺一致性
archive_chapter.py      # 归档章节
migrate_project.py      # 旧项目迁移
release_check.py        # 发布前检查
novel.py                # 统一 CLI
```

如果新增知识文件需要自动加载，优先修改：

```text
scripts/context_builder.py
```

如果新增知识文件是发布必需项，修改：

```text
scripts/release_check.py
```

如果新增规则会阻止归档，修改：

```text
scripts/quality_gate.py
```

## 10. 测试规范

每次更新后按影响范围选择测试：

```text
tests/test_genre_guides.py        # 题材指南和路由
tests/test_context_builder.py     # 上下文选择
tests/test_quality_gate.py        # 质量门禁
tests/test_consistency_check.py   # 一致性检查
tests/test_migration.py           # 迁移
tests/test_release_and_example.py # 发布和示例项目
```

新增知识库至少测试：

1. 路由能匹配新题材。
2. 上下文不会读取整个知识库。
3. 只加载当前任务需要的知识文件。
4. 缺失必需文件时 release check 会失败。

## 11. 版本和变更记录

每次可见更新都要修改：

```text
CHANGELOG.md
```

如果变更影响使用方式，修改：

```text
README.md
SKILL.md
UPDATE_PROTOCOL.md
```

版本建议：

```text
patch: 修正文档、错别字、轻微规则补充
minor: 新增题材、知识库、Agent 能力、测试
major: 项目结构、状态机、迁移规则、兼容性发生破坏性变化
```

## 12. 提交流程

一次标准迭代按以下顺序执行：

```text
1. 明确变更目标
2. 判断影响范围
3. 新增或修改 knowledge/
4. 更新 knowledge/README.md 或 routing.md
5. 更新相关 modules/
6. 更新相关 agents/
7. 必要时更新 scripts/
8. 更新测试
9. 运行测试
10. 更新 CHANGELOG.md
11. 自查兼容性
```

## 13. 自查清单

提交前检查：

```text
[ ] 新知识放在正确目录
[ ] 文件名使用小写英文和连字符
[ ] knowledge/README.md 已更新
[ ] routing.md 已更新
[ ] 相关 modules/ 已说明何时读取新知识
[ ] 相关 agents/ 已同步职责说明
[ ] context_builder.py 需要时已更新
[ ] release_check.py 需要时已更新
[ ] 测试已新增或修改
[ ] CHANGELOG.md 已记录
[ ] 没有提交 __pycache__、.pyc、临时文件
[ ] 没有覆盖用户项目文件
```

## 14. 推荐提交说明格式

```text
类型: 简短说明

变更内容:
- 

影响范围:
- knowledge:
- modules:
- agents:
- scripts:
- tests:

验证:
- 

兼容性:
- 是否影响旧项目:
- 是否需要迁移:
```

类型建议：

```text
feat: 新能力或新知识
fix: 修复错误
docs: 文档更新
test: 测试更新
refactor: 不改变行为的重构
chore: 工程维护
```

## 15. 示例：新增“都市修仙”题材

应修改：

```text
knowledge/genre-guides/urban-cultivation.md
knowledge/anti-ai/urban-cultivation.md
knowledge/genre-guides/routing.md
knowledge/genre-guides/README.md
modules/01_worldbuilding.md
modules/02_outline.md
modules/12_context_assembly.md
agents/worldbuilder.md
agents/outline-planner.md
tests/test_genre_guides.py
tests/test_context_builder.py
CHANGELOG.md
```

验证重点：

```text
1. 输入“都市修仙、灵气复苏、高武都市”能匹配 urban-cultivation。
2. context_builder 只加载 urban-cultivation 相关题材指南和必要格式规范。
3. 不会误加载玄幻、仙侠、都市日常等无关文件。
4. 反 AI 规则只作用于文风，不改变剧情和设定。
```

## 16. 禁止事项

1. 禁止把大段知识直接写进 `SKILL.md`。
2. 禁止让 `context_builder.py` 无条件读取整个 `knowledge/`。
3. 禁止新增知识后不写路由。
4. 禁止修改 Agent 职责但不更新模块说明。
5. 禁止修改脚本但不加测试。
6. 禁止提交 `__pycache__/`、`.pyc`、临时测试项目。
7. 禁止让通用规则覆盖用户已确认设定。
8. 禁止以“去 AI 味”为理由改剧情、人物关系或世界观。

