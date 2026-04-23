# docs/archive/openclaw 说明

更新时间：2026-04-23

## 1. 文档定位

本目录用于存放与以下历史阶段相关的资料：

- OpenClaw Android Native Entry
- HarmonyOS / Android 宿主部署
- 更早期的数字分身路线设想

这些文档仍然保留，是因为它们对以下场景还有参考价值：

- 回看早期宿主部署方式
- 回看 HarmonyOS / WebView 兼容性问题
- 回看原生入口阶段的已验证链路与已知限制
- 回看更早期路线设想的来源

但需要明确：

> **本目录只用于历史参考，不属于当前 AI 销售助手 V1 的正式导航入口。**

当前主线请优先参考：

- `AGENTS.md`
- `docs/README.md`
- `docs/product/overview.md`
- `docs/product/`
- `docs/how-to/operate/`
- `docs/delivery/`

---

## 2. 使用原则

### 2.1 当前状态

本目录文件统一视为：

- 历史参考
- 专项背景资料
- 技术复盘资料

它们不应作为当前项目方向、当前 V1 范围、当前日常工作方式的第一入口。

### 2.2 何时查看本目录

只有在下面情况时，才建议回看这些文件：

- 需要恢复或复刻早期 OpenClaw 宿主部署
- 需要排查 HarmonyOS / Android 设备上的历史兼容性问题
- 需要理解 Android Native Entry 阶段为什么这样设计
- 需要复盘早期“数字分身平台”路线的来源

### 2.3 何时不该优先看本目录

如果你当前要处理的是：

- AI 销售助手 V1 的产品设计
- 当前 `jianglab + Codex` 工作流
- 当前 Git / SSH / GitHub 运维
- 当前任务拆解与 handoff

那么不应优先进入本目录。

---

## 3. 当前建议

当前建议把本目录理解为：

- archive-only
- 默认不加入当前主来源集合
- 需要时再临时打开参考

如果要理解当前正式主线，应返回：

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/delivery/tasks/_active.md`

---

## 4. 一句话总结

`docs/archive/openclaw/` 保存的是：

> **OpenClaw 宿主部署、Android Native Entry 阶段，以及更早期路线设想的历史参考资料；这些文件保留，但不再主导当前 AI 销售助手 V1 的工作流与文档体系。**
