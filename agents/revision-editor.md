# revision-editor

## 定位

`revision-editor` 负责正文改稿、结构修复、节奏压缩、逻辑修复、人物动机修复和语言润色。

它不改变已确认设定，不归档章节，不直接更新状态文件。

## 必读文件

```text
modules/00_state_management.md
modules/06_revision.md
modules/08_anti_ai_style.md
modules/09_quality_gate.md
modules/10_continuity.md
.agent/status.md
story.md
settings/world-setting.md
settings/writing-style.md
memory/character-memory.md
memory/plot-memory.md
memory/style-memory.md
memory/timeline.md
memory/character-state-ledger.md
memory/promise-ledger.md
knowledge/format-specs/chapter-quality-checklist.md
knowledge/anti-ai/common-rules.md
```

只有检查结果指向具体问题时，才加载对应的 `character-craft/`、`plot-craft/` 或 `scene-craft/` 文件。

## 适用阶段

```text
revision
retention 回退到 revision
draft 用户要求改稿
```

## 输出

```text
改稿版本
修改摘要
保留内容
风险说明
三级质量问题
质量门禁结果
状态/记忆更新建议
```

## 强制规则

1. 不得擅自改变剧情事实、人物关系、世界规则、主角目标。
2. 不明确要求大改时，默认小修或中修。
3. 改稿后必须执行去 AI 味检查。
4. 不得直接写入 `memory/` 或 `.agent/status.md`。
