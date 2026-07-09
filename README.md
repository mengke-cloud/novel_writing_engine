\# novel\_writing\_engine 使用说明



\## 1. Skill 定位



`novel\_writing\_engine` 是一个工程化小说写作 Skill，核心用途是辅助长期小说创作。



它主要帮助完成：



\* 世界观创建

\* 世界观整理

\* 设定确认

\* 人物设计

\* 人物关系设计

\* 小说大纲

\* 分卷大纲

\* 章节细纲

\* 正文写作

\* 正文续写

\* 改稿润色

- 去 AI 味与自然化改写

\* 爽点设计

\* 虐点设计

\* 反转设计

\* 章尾追读优化



\---



\## 2. 核心运行逻辑



本 Skill 的核心流程是：



```text

先确认世界观

再确认人物

再确认主线

再确认章节

最后写正文

```



系统自动生成的任何设定，都必须先让用户确认。



未经用户确认的设定，不得进入大纲、人物、章节或正文。



## 去 AI 味自动执行

本 Skill 默认自动执行去 AI 味。

以下任务不需要用户额外提醒：

```text
1. 正文生成
2. 正文续写
3. 正文扩写
4. 正文改写
5. 章节成稿
6. 改稿输出
```

系统会默认检查并优化：

```text
1. 模板化表达
2. 机械总结
3. 过度解释
4. 高频 AI 词句
5. 对话不自然
6. 情绪太直白
7. 段落太工整
8. 爽点反应太泛
```

自动去 AI 味不会改变：

```text
1. 剧情
2. 人物关系
3. 世界观
4. 主角目标
5. 已确认设定
6. 关键反转
```

如果用户明确要求“保持原文”“只改错别字”“不要改风格”，则以用户当前要求为准。



## 项目初始化与检测

本 Skill 从 `0.8.0` 开始具备标准化长期记忆系统，从 `0.9.0` 开始具备按需加载的创作知识库。

检测当前目录是否为小说项目：

```text
python scripts/detect_project.py <project-path>
```

初始化一个新的小说项目：

```text
python scripts/init_project.py <project-path> --name <小说名> --genre <题材>
```

预览初始化清单但不写入：

```text
python scripts/init_project.py <project-path> --dry-run
```

修复状态文件缺失字段：

```text
python scripts/repair_status.py <project-path>
```

预览状态修复但不写入：

```text
python scripts/repair_status.py <project-path> --dry-run
```

检查项目完整性：

```text
python scripts/quality_gate.py <project-path> --target project
```

执行归档质量门禁并生成报告：

```text
python scripts/quality_gate.py <project-path> --target archive --chapter-plan <章纲路径> --draft <正文路径> --report <报告路径>
```

质量门禁将问题分为 `阻断`、`重要`、`优化`。只有阻断项会禁止归档；重要项和优化项保留给作者判断。

检查时间线、人物状态和剧情承诺：

```text
python scripts/consistency_check.py <project-path> --chapter <当前章节>
```

该检查会识别事件倒序、未来人物状态、台账字段缺失、伏笔逾期、长期未推进及错误回收状态。

按当前阶段生成上下文包：

```text
python scripts/context_builder.py <project-path> --max-chars 30000 --output <project-path>/.agent/task/context.md
```

正文、改稿和归档任务应同时传入 `--chapter-plan` 与 `--draft`。生成结果包含文件选择原因、优先级、纳入字符数以及 `included`、`truncated`、`skipped_budget`、`missing` 状态。

统一命令行入口：

```text
python scripts/novel.py init <project-path> --name <小说名> --genre <题材>
python scripts/novel.py status <project-path>
python scripts/novel.py next <project-path> --output <project-path>/.agent/task/context.md
python scripts/novel.py consistency <project-path> --chapter <当前章节>
python scripts/novel.py quality <project-path> --target project
python scripts/novel.py archive <project-path> --chapter-plan <章纲路径> --draft <正文路径>
python scripts/novel.py test
python scripts/novel.py migrate <旧项目路径> --dry-run
python scripts/novel.py analytics <项目路径> --output <报告路径>
python scripts/novel.py example <目标目录>
python scripts/novel.py release
```

归档命令会重新运行门禁、保存定稿、生成质量报告和记忆更新建议。用户确认更新建议并由 `updater` 写入记忆后，状态才进入下一章。

旧项目正式迁移前必须先使用 `--dry-run` 查看计划。迁移会创建 ZIP 备份，保留 `story.yaml` 和旧资料，只补建缺失的新结构，并在结束后生成 `.agent/migration-report.md`。

安装 Skill：

```text
powershell -ExecutionPolicy Bypass -File install.ps1
sh install.sh
```

完整兼容范围见 `COMPATIBILITY.md`。发布检查会验证版本、测试、类型指南和示例项目。

当 `detect_project.py` 返回 `needs_repair`，且 `story.md` 与 `.agent/status.md` 都存在时，可以先用 `repair_status.py` 补齐状态字段。修复后必须重新运行 `detect_project.py`，结果为 `existing` 后再继续写作。

初始化会创建：

```text
story.md
settings/
volumes/
chapters/
drafts/
archives/
memory/
memory/README.md
memory/world-memory.md
memory/character-memory.md
memory/plot-memory.md
memory/style-memory.md
memory/foreshadowing-memory.md
memory/unresolved-threads.md
memory/reader-feedback.md
memory/timeline.md
memory/character-state-ledger.md
memory/promise-ledger.md
.agent/status.md
.agent/task/
.agent/reports/
```

初始化只创建项目骨架和空白状态文件，不会自动生成未经确认的世界观、人物关系、主线剧情或关键设定。

如果目标目录已经存在 `story.md` 或 `.agent/status.md`，初始化脚本默认拒绝覆盖。只有明确传入 `--force` 时，才会覆盖模板管理的文件。

初始化完成后，后续任务由 `agents/novel-agent.md` 作为总调度入口。

知识库位于 `knowledge/`，包含格式规范、类型指南、人物、情节、场景、去 AI 化和标题设计知识。代理依据 `knowledge/README.md` 按任务加载，禁止整库读取；项目已确认事实始终优先于通用知识。

当前 Agent 职责：

```text
agents/novel-agent.md
  第一层总调度入口，负责检测项目、读取状态、判断 phase、选择模块、生成更新指令。

agents/worldbuilder.md
  世界观与规则 agent。

agents/character-designer.md
  人物与关系 agent。

agents/outline-planner.md
  主线大纲与分卷规划 agent。

agents/chapter-planner.md
  章节细纲与章尾钩子 agent。

agents/writer.md
  正文生成、续写、扩写 agent。

agents/revision-editor.md
  改稿与结构修复 agent。

agents/anti-ai-editor.md
  去 AI 味与自然化 agent。

agents/reader-reviewer.md
  追读、爽点、疲劳点检查 agent。

agents/updater.md
  项目文件更新 agent，负责写入 .agent/status.md、settings/、memory/。
```

`novel-agent` 不直接写状态、设定或记忆文件；需要写入时，必须生成更新指令并交给 `updater` 执行。



\---



\## 3. 设定状态



所有设定分为三类：



```text

【用户已确认】

可以正式使用的设定。



【系统待确认】

系统自动生成或补全，但用户尚未确认的设定。



【不可使用】

用户否定、废弃或推翻的设定。

```



只有 `【用户已确认】` 可以进入正式创作。



\---



\## 4. 用户确认方式



当系统生成设定草案后，会要求用户确认：



```text

A. 全部确认，继续生成

B. 部分修改，我会按你的修改调整

C. 推翻重建，重新生成设定

```



选择规则：



```text

A = 接受当前设定，可以继续

B = 修改部分设定，修改后再次确认

C = 当前设定废弃，重新生成

```



\---



\## 5. 推荐使用流程



\### 5.1 从零开始写小说



可以这样输入：



```text

我想写一部男频玄幻小说，请先帮我创建世界观。

```



或：



```text

我想写一部都市异能小说，但还没有完整设定，请先帮我做世界观草案。

```



\---



\### 5.2 已有设定时



可以这样输入：



```text

这是我的小说世界观，请先帮我整理，并判断是否足够支撑长篇连载。

```



然后粘贴已有设定。



\---



\### 5.3 写大纲



必须在世界观确认后使用：



```text

基于已确认世界观，帮我写主线大纲。

```



或：



```text

基于已确认世界观，帮我设计前三卷分卷大纲。

```



\---



\### 5.4 写人物



可以这样输入：



```text

基于已确认世界观，帮我设计主角和主要反派。

```



或：



```text

帮我检查这个主角的人物动机是否成立。

```



\---



\### 5.5 写章节



可以这样输入：



```text

基于已确认大纲，帮我设计第一章章节细纲。

```



或：



```text

帮我优化这一章的章尾追读点。

```



\---



\### 5.6 写正文



必须在世界观、人物和章节方向确认后使用：



```text

基于已确认设定和第一章细纲，开始写第一章正文。

```



\---



\### 5.7 改稿



可以这样输入：



```text

帮我中修改稿，重点增强冲突、节奏和章尾追读。

```



或：



```text

只做小修，不改变剧情和设定。

```



### 5.8 去 AI 味

可以这样输入：

```text
帮我把下面这段小说去 AI 味，只改文风，不改变剧情。
```

或：

```text
这段太像 AI 了，帮我改得更像真人写的，保留原剧情和人物关系。
```

或：

```text
帮我中度去 AI 味，重点优化对白、情绪和段落节奏。
```

去 AI 味默认不改变：

```text
1. 剧情
2. 人物关系
3. 世界观
4. 主角目标
5. 关键设定
```



\---



\## 6. 更新 Skill



后续可以用这个格式更新：



```text

【更新小说 Skill】

模块：

动作：

规则内容：

原因：

优先级：

```



示例：



```text

【更新小说 Skill】

模块：正文

动作：新增

规则内容：正文默认保持手机阅读友好的短段落，关键反转必须单独成段。

原因：增强阅读节奏。

优先级：建议

```



\---



\## 7. 当前文件结构



```text
novel_writing_engine/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── UPDATE_PROTOCOL.md
├── agents/
│   ├── anti-ai-editor.md
│   ├── character-designer.md
│   ├── chapter-planner.md
│   ├── novel-agent.md
│   ├── openai.yaml
│   ├── outline-planner.md
│   ├── reader-reviewer.md
│   ├── revision-editor.md
│   ├── updater.md
│   ├── worldbuilder.md
│   └── writer.md
├── modules/
│   ├── README.md
│   ├── 00_state_management.md
│   ├── 01_worldbuilding.md
│   ├── 02_outline.md
│   ├── 03_character.md
│   ├── 04_chapter_design.md
│   ├── 05_prose_writing.md
│   ├── 06_revision.md
│   ├── 07_reader_retention.md
│   └── 08_anti_ai_style.md
├── scripts/
│   ├── detect_project.py
│   ├── init_project.py
│   └── repair_status.py
├── templates/
│   ├── story.md.template
│   ├── status.md.template
│   ├── world-setting.md.template
│   ├── genre-setting.md.template
│   ├── writing-style.md.template
│   ├── user-preferences.md.template
│   ├── memory-readme.md.template
│   ├── world-memory.md.template
│   ├── character-memory.md.template
│   ├── plot-memory.md.template
│   ├── style-memory.md.template
│   ├── foreshadowing-memory.md.template
│   ├── unresolved-threads.md.template
│   ├── reader-feedback.md.template
│   ├── character-state.md.template
│   └── plot-hooks.md.template
├── 初始化项目后生成：
│   ├── story.md
│   ├── settings/
│   ├── volumes/
│   ├── chapters/
│   ├── drafts/
│   ├── archives/
│   ├── memory/
│   │   ├── README.md
│   │   ├── world-memory.md
│   │   ├── character-memory.md
│   │   ├── plot-memory.md
│   │   ├── style-memory.md
│   │   ├── foreshadowing-memory.md
│   │   ├── unresolved-threads.md
│   │   └── reader-feedback.md
│   └── .agent/status.md
└── project_rules/
    └── user_preferences.md
```



\---



\## 8. 当前版本



```text

version: 1.0.0

```



当前版本已经具备最小可用能力：



\* 世界观前置确认

\* 自动设定确认

\* 项目状态检测

\* 安全初始化项目骨架

\* `.agent/status.md` 状态源

\* `phase` 阶段调度

\* 状态系统规范模块

\* 状态文件缺字段修复

\* 第一批多 Agent 分工

\* 模块工作流入口规范

\* 标准化长期记忆系统

\* 按需加载的创作知识库

\* 世界观、人物、主线、卷纲、章纲和正文格式规范

\* 章节质量检查与类型知识路由

\* 人物、情节、场景、标题和分类型去 AI 化方法

\* 自动化项目与章节质量门禁

\* 阻断、重要、优化三级验收报告

\* 归档前强制检查与失败回退

\* 长篇事件时间线与因果追踪

\* 人物位置、伤势、物品、能力和知情范围台账

\* 伏笔、悬念、钩子和剧情承诺生命周期

\* 承诺逾期及长期未推进提醒

\* 按阶段自动选择设定、记忆、知识和最近章节

\* 可配置字符预算与上下文截断

\* 上下文文件清单、选择原因和缺失报告

\* 归档门禁、定稿保存和状态自动更新

\* 时间线、人物、剧情、伏笔及承诺更新建议

\* 初始化、检测、修复、检查和归档统一 CLI

\* 项目生命周期、损坏项目、兼容性和端到端测试

\* 统一测试入口与 Markdown 测试报告

\* Windows GitHub Actions 自动测试

\* 旧项目非破坏迁移、ZIP 备份和迁移报告

\* 言情、历史、科幻、末世、无限流和同人指南

\* 九类题材自动路由与按需加载

\* 章节、人物、冲突信号、承诺和质量趋势分析

\* Windows、macOS 和 Linux 安装脚本

\* 可运行示例项目生成器

\* 版本、测试、示例和必需文件发布门禁

\* 大纲设计

\* 人物设计

\* 章节设计

\* 正文写作

\* 改稿

\* 追读与爽点优化

\* 后续持续更新机制



\---



\## 9. 使用原则总结



这个 Skill 的核心原则是：



```text

不确认，不继续。

不乱改，不漂移。

先设定，再创作。

先结构，再正文。

每章都要有目标、阻碍、变化和追读。

```



