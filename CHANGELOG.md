\# CHANGELOG.md



本文件用于记录 `novel\_writing\_engine` 的所有重要更新。



版本格式采用语义化版本：



```text id="zmryx9"

主版本号.次版本号.修订号

```



示例：



```text id="dbn9o2"

0.1.0

0.1.1

0.2.0

1.0.0

```



\---


## [0.4.0] - 2026-07-08

### Added

* `scripts/detect_project.py` 新增 `skill_root` 检测，避免在 Skill 目录内误初始化小说项目。
* `scripts/detect_project.py` 新增 `.agent/status.md` 关键字段检查。
* `scripts/detect_project.py` 支持新版字段与旧版字段兼容检测。
* `scripts/init_project.py` 新增 `--dry-run` 初始化预览。
* `scripts/init_project.py` 初始化前输出将创建的目录和文件清单。
* 初始化项目时新增基础记忆文件：`world-memory.md`、`character-memory.md`、`plot-memory.md`、`style-memory.md`、`foreshadowing-memory.md`、`unresolved-threads.md`、`reader-feedback.md`。
* `templates/status.md.template` 新增 `engine_version`、`phase`、`current_task`、`next_action`、`blocked_reason` 等标准状态字段。

### Changed

* `agents/novel-agent.md` 升级为以 `.agent/status.md` 为唯一状态源的总调度入口。
* `agents/novel-agent.md` 新增 `phase` 阶段调度表和状态更新规则。
* `SKILL.md` 项目系统入口与新版检测、初始化、调度流程对齐。
* `README.md` 更新项目初始化、检测、文件结构和当前版本说明。
* 当前版本提升为 `0.4.0`。

### Fixed

* 初始化脚本默认拒绝覆盖已有 `story.md` 或 `.agent/status.md`，降低误覆盖用户项目的风险。
* 检测脚本能识别状态文件缺少关键字段的损坏项目。

### Reason

* 将第一层项目系统从“最小可用”升级为“可稳定落地”的基础能力。
* 为后续状态系统、多 Agent 拆分、记忆系统和迁移同步能力打基础。

### Impact

* 新初始化项目会带有更完整的目录、状态文件和记忆占位文件。
* 已有旧版状态字段仍可被检测脚本兼容识别。
* 后续继续写作应优先通过 `agents/novel-agent.md` 读取 `.agent/status.md` 的 `phase` 进行调度。


\---



## [0.3.0] - 2026-07-08

### Added

* 新增标准 Codex Skill frontmatter：`name: novel-writing-engine`。
* 新增项目初始化脚本：`scripts/init_project.py`。
* 新增项目状态检测脚本：`scripts/detect_project.py`。
* 新增总调度入口：`agents/novel-agent.md`。
* 新增 UI 元数据：`agents/openai.yaml`。
* 新增项目模板：`templates/story.md.template`、`templates/status.md.template`、设定模板和记忆模板。
* 新增 `.agent/status.md` 项目状态文件模板。

### Changed

* Skill 从单纯规则库升级为具备第一层项目系统能力。
* README 当前版本更新为 `0.3.0`。
* `SKILL.md` 新增项目系统入口规则。

### Reason

* 用户要求执行第一层能力：标准安装结构、项目初始化、状态检测、总调度 agent、任务状态文件。
* 为后续多 Agent、迁移、归档和记忆系统打基础。

### Impact

* 可以初始化新的小说项目骨架。
* 可以检测当前目录是新项目、已有项目、旧版项目、损坏项目或部分项目。
* 后续可以围绕 `.agent/status.md` 继续迭代多 Agent 调度。



\---



## [0.2.1] - 2026-07-08

### Added

* 新增去 AI 味自动执行规则。
* 正文生成、续写、扩写、改写、章节成稿和改稿输出时，默认自动执行去 AI 味后处理。
* 新增正文模块自动去 AI 味规则。
* 新增改稿模块自动去 AI 味规则。
* 新增去 AI 味模块自动调用规则。

### Changed

* 去 AI 味不再只依赖用户显式调用。
* 默认正文输出前会自动检查模板句、机械总结、过度解释、对白不自然、段落过于工整等问题。
* 自动去 AI 味默认强度设为中度。
* 如果用户要求只改错别字、保持原文或不改风格，则自动去 AI 味降级或暂停。

### Reason

* 用户要求“去除 AI 味自动执行”。
* 小说正文生成时应默认减少 AI 痕迹，而不是等用户额外提醒。
* 提高正文自然度、人物真实感和作者感。

### Impact

* 影响正文写作、正文续写、正文扩写、正文改写、章节成稿和改稿输出。
* 不改变剧情、人物关系、世界观规则、主角目标和已确认设定。
* 不得新增未经确认的关键设定。



\---



## [0.2.0] - 2026-07-08

### Added

* 新增去 AI 味模块：`modules/08_anti_ai_style.md`。
* 新增 AI 味诊断能力。
* 新增去模板化规则。
* 新增对话自然化规则。
* 新增情绪克制改写规则。
* 新增段落节奏去机械化规则。
* 新增高频 AI 词句规避清单。
* 新增轻度 / 中度 / 重度去 AI 味分级。
* 新增“保留作者感”规则。

### Changed

* `SKILL.md` 新增去 AI 味任务调用逻辑。
* 改稿能力扩展为支持专门的去 AI 味处理。
* README 使用说明增加去 AI 味相关用法。

### Reason

* 当前 Skill 具备基础自然化能力，但缺少专门针对 AI 味的诊断和改写模块。
* 用户要求增加一个去 AI 味模块。
* 小说正文需要更像人物正在经历，而不是系统正在说明。

### Impact

* 影响正文改写、润色、改稿、对话优化和文风自然化任务。
* 用户可以直接要求“去 AI 味”“降低 AI 痕迹”“保留剧情，只改自然”。
* 默认不改变剧情、人物关系、世界观规则和主角目标。



\---



\## \[0.1.0] - 2026-07-08



\### Added



\* 建立 `novel\_writing\_engine` 小说写作 Skill。

\* 建立主控文件 `SKILL.md`。

\* 建立模块化目录结构。

\* 新增世界观模块：`modules/01\_worldbuilding.md`。

\* 新增大纲模块：`modules/02\_outline.md`。

\* 新增人物模块：`modules/03\_character.md`。

\* 新增章节设计模块：`modules/04\_chapter\_design.md`。

\* 新增正文写作模块：`modules/05\_prose\_writing.md`。

\* 新增改稿模块：`modules/06\_revision.md`。

\* 新增追读与爽点模块：`modules/07\_reader\_retention.md`。

\* 新增更新协议：`UPDATE\_PROTOCOL.md`。

\* 新增长期偏好文件规划：`project\_rules/user\_preferences.md`。



\### Core Rules



\* 小说任务必须先确认世界观，再进入大纲、人物、章节或正文。

\* 系统自动生成、自动补全、推断或扩展的设定，必须先交给用户确认。

\* 未经用户确认的设定只能标记为 `【系统待确认】`，不得进入正式创作。

\* 用户确认后的设定标记为 `【用户已确认】`。

\* 用户否定、废弃或要求重做的设定标记为 `【不可使用】`。

\* 用户未确认前，不得继续生成大纲、人物、章节或正文。

\* 正文写作默认采用商业网文逻辑、手机阅读友好段落、冲突驱动和章尾追读。

\* 改稿默认保护用户原文，不明确要求大改时，只做小修或中修。

\* 每章必须有目标、阻碍、变化和追读点。



\### Reason



\* 用户需要一个以小说写作为核心的工程化 Skill。

\* 用户希望 Skill 可以后续持续更新。

\* 用户要求 Skill 在运行前先处理小说世界观。

\* 用户要求系统自动生成的设定必须经用户确认后，才能继续生成后续内容。



\### Impact



\* 所有小说创作任务都会受到世界观确认协议影响。

\* 所有自动生成设定都会受到确认机制约束。

\* 大纲、人物、章节、正文、改稿和追读模块都必须遵守设定状态标记。

\* 后续更新必须按照 `UPDATE\_PROTOCOL.md` 执行。



\---



\## \[0.1.1] - 待更新



\### Added



\* 待补充。



\### Changed



\* 待补充。



\### Removed



\* 待补充。



\### Deprecated



\* 待补充。



\### Reason



\* 待补充。



\### Impact



\* 待补充。



\---



\## 更新记录模板



```text id="6tpu57"

\## \[版本号] - YYYY-MM-DD



\### Added

\- 新增内容。



\### Changed

\- 修改内容。



\### Removed

\- 删除内容。



\### Deprecated

\- 废弃内容。



\### Reason

\- 更新原因。



\### Impact

\- 影响范围。

```



