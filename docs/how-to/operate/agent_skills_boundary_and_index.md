# Agent Skills 边界与索引说明

更新时间：2026-04-23

## 1. 文档定位

本文档用于给当前仓库补一层**最小 Skills 接口说明**。

它的目标不是把 Skills 提升为新的主工作流，而是明确：

- 哪些内容必须继续留在 `AGENTS.md` 与 `docs/`
- 哪些内容适合后续抽成可复用 Skills
- 后续若真的开始沉淀 Skills，仓库里至少要保留什么索引信息

本文档是对当前文档驱动工作流的补充，不是替代。

---

## 2. 当前结论

当前仓库仍应坚持：

> **`AGENTS.md` + `docs/` 是正式控制平面，Skills 只是可复用执行插件。**

也就是说：

1. `AGENTS.md` 负责仓库级持久规则
2. `docs/` 负责项目事实源
3. Skills 负责复用型流程封装
4. Skills 不能替代 task / handoff / runbook / spec

---

## 3. 哪些内容应继续留在 `AGENTS.md`

以下内容应继续由规则文件承担：

- 工作区与环境假设
- Git 规则
- 高风险文件类别
- 验证分级与完成定义
- 停止 / 升级处理条件
- 对 docs 更新责任的要求
- 子树局部规则入口

这些内容的特点是：

- 作用范围覆盖整个仓库
- 跨 thread 稳定存在
- 不应依赖某个具体 Skill 才被看见

在当前分层下：

- 根 `AGENTS.md` 负责仓库级稳定规则
- `app/AGENTS.md` 负责 Android 局部规则

---

## 4. 哪些内容应继续留在 `docs/`

以下内容必须继续留在仓库文档中，而不是外包给 Skills：

### 4.1 方向层

- `docs/product/*`
- `docs/adr/*`

### 4.2 方案层

- `docs/architecture/*`
- `docs/reference/*`
- `docs/how-to/*`

### 4.3 执行层

- `docs/delivery/tasks/*`
- `docs/delivery/handoffs/*`

这些内容的共同点是：

- 是项目事实源
- 需要被人工 review
- 需要被后续 agent 和开发者稳定引用
- 不应跟随某个工具实现一起漂移

---

## 5. 哪些内容适合抽成 Skills

适合抽成 Skills 的，应当是**可复用、可重复触发、边界稳定的流程包**。

当前仓库后续最可能适合的方向包括：

### 5.1 Android 构建与验证类 Skill

例如：

- Debug 包构建与快速 smoke check
- `adb` 设备识别与安装验证
- 真机证据收集
- Compose 视觉回归检查

### 5.2 文档执行类 Skill

例如：

- task / handoff 同步检查
- `_active.md` 与 task 状态一致性巡检
- docs 导航漂移检查

### 5.3 运行与排障类 Skill

例如：

- `jianglab` 环境检查
- Android / Termux / OpenClaw 连接链路排障
- 常见日志采集与摘要

这些流程适合做 Skill，是因为它们：

- 跨多个线程会重复出现
- 可以捆绑固定命令或脚本
- 输出形式比较标准
- 不需要自己重新定义产品含义

---

## 6. 当前不适合抽成 Skills 的内容

以下内容当前不应被 Skill 化为“事实源”：

- V1 做什么、不做什么
- 当前正式活跃任务是什么
- 当前 API contract 的正式含义
- Android 与 backend 的产品边界
- 关键 ADR 决策
- 当前 thread 的验收口径

这些内容可以被 Skill **引用**，但不应由 Skill **拥有**。

---

## 7. 后续 Skills 的最小仓库接口

即使未来 Skill 本体不放在本仓库中，仓库内也应至少保留以下索引信息：

1. Skill 名称
2. Skill 用途
3. 触发场景
4. 必须先读的仓库文档
5. 允许使用的命令 / 工具边界
6. 预期输出与证据类型
7. 遇到什么情况必须停止并升级给人工

建议每个后续 Skill 至少能回答下面几个问题：

- 它解决什么重复问题？
- 它依赖哪些仓库事实源？
- 它能自动做到哪一步？
- 哪一步必须回到 task / docs / 人工确认？

---

## 8. 推荐的最小 Skill 条目模板

后续若要正式引入仓库相关 Skill，建议至少维护如下条目：

```text
Skill name:
Purpose:
When to trigger:
Required repo docs:
Allowed tools / commands:
Expected outputs / evidence:
Stop / escalate conditions:
Notes:
```

这层模板的作用是：

- 让 Skill 与仓库事实源对齐
- 防止 Skill 自己长成新的隐式规则中心
- 让后续 agent 能快速判断“该不该用这个 Skill”

---

## 9. 当前建议的最小候选索引

当前如需优先沉淀 Skills，建议优先考虑以下低风险候选：

1. `android-debug-build-smoke`
   - 负责 `assembleDebug`、安装、启动与基础验证摘要
2. `android-adb-evidence-capture`
   - 负责 `adb devices`、基础 `logcat`、设备信息与真机证据摘要
3. `compose-visual-check`
   - 负责视觉变更的截图验证或截图基线检查建议
4. `task-handoff-sync-check`
   - 负责 task、handoff、README 导航的一致性巡检

这些候选都应被理解为：

- **执行辅助层**
- **不是方向层**
- **不是当前主工作流的替代物**

当前仓库已经进一步把这些候选收口为 repo 内 Skill 规格层，见：

- `docs/how-to/operate/skills/README.md`
- `docs/how-to/operate/skills/rollout-order.md`

---

## 10. 与当前仓库的关系

当前仓库已经具备比较稳定的文档驱动入口：

`AGENTS.md -> docs/README.md -> docs/delivery/tasks/_active.md -> 当前 task`

如果任务涉及 Android 代码，还应继续读取：

`app/AGENTS.md`

后续如果增加 Skills，推荐采用的关系应为：

```text
AGENTS.md / docs 负责定义边界
        ↓
Skill 读取并复用这些边界
        ↓
agent 执行具体流程
        ↓
结果仍回写 task / handoff / runbook
```

换句话说：

> **Skill 可以加速执行，但不能替代仓库文档成为新的主真相层。**
