# 11_promise_tracking.md

## 0. 工作流入口

适用阶段：`outline`、`volume`、`chapter`、`retention`、`archive`。

必读文件：

```text
memory/promise-ledger.md
memory/foreshadowing-memory.md
memory/unresolved-threads.md
memory/reader-feedback.md
```

## 1. 管理对象

统一管理：

```text
伏笔
悬念
章尾钩子
人物承诺
能力或规则承诺
类型体验承诺
```

每项承诺使用唯一 `PRM-四位数字` ID，并记录提出、最近推进、预计回收和实际回收章节。

## 2. 生命周期

```text
active -> resolved
active -> abandoned
```

禁止直接删除承诺。放弃时必须记录原因和用户确认状态。

## 3. 逾期规则

- 当前章节超过 `due_chapter`：重要项。
- 连续五章没有推进：重要项。
- 标记 `resolved` 却没有 `resolved_chapter`：阻断项。
- 回收方式没有满足 `payoff_requirement`：语义复核阻断项。

## 4. 章节工作流

章纲阶段选择本章要新增、推进或回收的承诺。正文不得凭空新增重大伏笔。归档时更新台账，并同步相关伏笔和未解决线索记忆。

## 5. 输出格式

```text
新增承诺：
推进承诺：
回收承诺：
逾期承诺：
长期未推进承诺：
台账更新建议：
```
