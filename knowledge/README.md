# 小说知识库

`knowledge/` 保存可复用的小说创作知识，供代理按任务需要读取。它与其他目录的职责不同：

- `modules/`：规定工作流程、输入输出与执行边界。
- `project_rules/`：规定整个引擎必须遵守的硬性规则。
- `memory/`：保存某一部小说持续变化的事实与状态。
- `knowledge/`：提供跨项目复用的创作方法、格式规范和类型经验。

## 分类索引

| 分类 | 用途 | 当前状态 |
|---|---|---|
| `format-specs/` | 统一设定、规划、正文和记忆文件格式 | 待建设 |
| `anti-ai/` | 通用及分类型的去 AI 化规则 | 待建设 |
| `genre-guides/` | 各小说类型的创作约束和读者预期 | 待建设 |
| `genre-examples/` | 类型化案例、正反例和拆解 | 待建设 |
| `character-craft/` | 人物塑造、关系、弧光与反派设计 | 待建设 |
| `plot-craft/` | 冲突、钩子、转折、情绪和结构方法 | 待建设 |
| `scene-craft/` | 对话、战斗、环境、转场等场景技法 | 待建设 |
| `title-craft/` | 书名、卷名和章节名方法 | 待建设 |

## 读取原则

1. 代理先读取对应模块和项目记忆，再按任务选择知识文件。
2. 不允许默认加载整个知识库，防止上下文膨胀和规则互相干扰。
3. 通用规则先于类型规则读取；类型规则只在项目类型匹配时加载。
4. 示例用于理解方法，不得直接复制其中的人物、情节或表达。
5. 知识文件与项目已确认事实冲突时，以项目记忆为准。
6. 知识文件与硬性规则冲突时，以 `project_rules/` 为准。

## 建设约定

每个正式知识文件至少包含：

- 适用范围
- 核心原则
- 可执行方法
- 常见错误
- 检查清单

尚未完成审核的内容必须明确标记为“草案”，不得作为强制规则使用。

## Agent 路由

| Agent | 必读知识 | 按需知识 |
|---|---|---|
| `worldbuilder` | `format-specs/world-setting.md` | 匹配的类型指南 |
| `character-designer` | `format-specs/character-setting.md`、`character-craft/decision-engine.md` | `relationship-arcs.md` |
| `outline-planner` | `format-specs/story-arc.md` 或 `volume-outline.md` | 类型指南、`plot-craft/` |
| `chapter-planner` | `format-specs/chapter-outline.md`、`scene-craft/scene-engine.md` | `plot-craft/`、具体场景知识 |
| `writer` | `format-specs/prose-output.md`、`anti-ai/common-rules.md` | 类型调整、具体场景知识 |
| `revision-editor` | `format-specs/chapter-quality-checklist.md` | 人物、情节、场景及去 AI 化知识 |
| `anti-ai-editor` | `anti-ai/common-rules.md` | `anti-ai/genre-adjustments.md` |
| `reader-reviewer` | `format-specs/chapter-quality-checklist.md`、`plot-craft/hooks-and-payoffs.md` | 匹配的类型指南 |

类型文件必须先通过 `genre-guides/routing.md` 选择。未匹配的类型文件禁止加载。
