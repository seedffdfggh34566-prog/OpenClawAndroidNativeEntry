# Skills 落地顺序说明

更新时间：2026-04-23

## 1. 文档定位

本文档用于固定当前仓库这 5 个 Android / workflow Skills 的推荐落地顺序。

这里的顺序服务于：

- 降低前期投入成本
- 优先覆盖当前最频繁、最容易出错的流程
- 避免过早建设仓库当前还不需要的自动化基础设施

---

## 2. 固定顺序

当前推荐按以下顺序落地：

1. `android-build-verify`
2. `task-handoff-sync`
3. `android-runtime-integration-guard`
4. `android-logcat-triage`
5. `android-ui-change-check`

---

## 3. 顺序理由

### 3.1 `android-build-verify`

最先落地，因为它：

- 依赖的命令当前都存在
- 与 `app/AGENTS.md` 的验证分级直接对齐
- 最容易立刻提升 Android 线程的稳定性

### 3.2 `task-handoff-sync`

第二个落地，因为它：

- 最贴合当前仓库的 task / handoff 驱动工作流
- 不依赖额外运行环境
- 能提升每个 thread 的收口质量

### 3.3 `android-runtime-integration-guard`

第三个落地，因为它：

- 和当前项目的 `Termux / OpenClaw / Manifest / navigation` 高风险区高度相关
- 能为高风险 Android 任务自动提升验证要求

### 3.4 `android-logcat-triage`

第四个落地，因为它：

- 当前环境已经支持
- 但更适合在几轮真实排障后优化摘要方式和过滤模板

### 3.5 `android-ui-change-check`

最后落地，因为它当前只能做轻量版：

- 现在没有 screenshot testing 基建
- 没有 `androidTest` / 截图测试目录
- 因此先做证据守门即可，不宜过早做重型视觉自动化

---

## 4. 当前明确不做

本轮不要求：

- 创建真实 Skill 目录
- 编写复杂执行脚本
- 接入 screenshot testing
- 新建 Android 自动化测试基建

只有在后续 task 明确授权时，才继续推进更重的 Skill 实现。
