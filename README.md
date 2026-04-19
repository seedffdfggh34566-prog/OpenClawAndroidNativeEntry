# OpenClaw Android Native Entry

一个面向 **HarmonyOS / Android 平板** 的 **OpenClaw 安卓原生入口项目**。

当前目标不是重写 OpenClaw 本体，而是基于已经跑通的 **Termux + OpenClaw Gateway** 宿主环境，做一个可在设备桌面直接启动的 **Android 原生 App 入口**，逐步替代“手动进 Termux / 浏览器打开 Dashboard”的使用方式。

---

## 1. 项目目标

本项目要实现一个 Android 原生 App，用于：

- 显示本机 OpenClaw Gateway 状态
- 一键调用既有脚本启动 OpenClaw
- 进入聊天界面
- 查看日志与诊断信息
- 为后续的原生聊天、通知、语音、快捷方式、前台服务打基础

项目的产品定位是：

> **原生入口层**，而不是 OpenClaw 宿主层重构。

也就是说：

- **宿主层**：继续复用平板中已验证可运行的 Termux + tmux + OpenClaw Gateway
- **入口层**：新增 Android 原生 App
- **能力层**：后续再逐步加入原生聊天、状态同步、前台服务、设备能力接入

---

## 2. 当前已知事实

以下事实已经在真实设备部署中得到验证：

- OpenClaw **可以在 HarmonyOS 平板的 Termux 环境中运行**
- `tmux`、`sshd`、启动脚本等运维能力已经建立
- 已有脚本：`boot-openclaw`、`start-openclaw`、`start-sshd`
- 默认模型已稳定配置为 **Step 3.5 Flash**
- 本机浏览器直接访问 Dashboard 存在兼容问题
- 电脑浏览器通过 SSH 隧道访问 Dashboard 是可行的

因此，本项目的核心任务不是“证明 OpenClaw 能在平板上跑”，而是：

> **把已经跑通的宿主环境，包装成一个更像产品的安卓原生入口。**

详细背景见：

- `docs/OpenClaw_HarmonyOS_Android_Deployment_Guide.md`

---

## 3. V1 范围

第一阶段只做一个 **最小可运行版本（V1）**。

### V1 必做

- 首页显示 Gateway 状态
- “启动 OpenClaw”按钮
- “进入聊天”按钮
- 日志页
- 设置页

### V1 技术路线

- Android Studio
- Kotlin
- Jetpack Compose
- WebView 作为聊天页承载方式
- 后续通过 Termux 的命令调用能力接入 `boot-openclaw`

### V1 暂不做

- 不重写完整 OpenClaw 聊天协议客户端
- 不在 APK 内嵌 OpenClaw 宿主环境
- 不做多设备同步
- 不做复杂插件系统
- 不做完整语音能力
- 不做 iOS 适配

---

## 4. 推荐架构

```text
HarmonyOS / Android Device
├─ Termux
│  ├─ OpenClaw Gateway
│  ├─ tmux
│  ├─ sshd
│  └─ boot-openclaw / start-openclaw / start-sshd
│
└─ Android Native App
   ├─ Home / Status
   ├─ WebView Chat Entry
   ├─ Logs / Diagnostics
   ├─ Settings
   └─ Later: native chat / foreground service / notifications
```

设计原则：

1. **先复用现有宿主层**
2. **先做入口，再做聊天原生化**
3. **先跑通最小闭环，再增强自动化与保活**
4. **所有设计优先适配当前 HarmonyOS 平板的现实约束**

---

## 5. 开发里程碑

### Milestone 1：项目骨架

- 建立 Android Studio Kotlin + Compose 工程
- 完成首页、日志页、设置页占位
- 建立基础导航结构

### Milestone 2：入口可用

- 首页显示 Gateway 状态占位
- 接入“启动 OpenClaw”按钮
- 接入“进入聊天”按钮
- 用 WebView 打开本机 Dashboard

### Milestone 3：可控制

- 连接 Termux 启动脚本
- 查看启动结果和错误信息
- 增加诊断与日志展示

### Milestone 4：可常驻

- 增加前台服务
- 增加持续通知
- 增加自动重连与状态检测

### Milestone 5：逐步原生化

- 原生会话列表
- 原生消息输入
- 原生状态同步
- WebView 仅保留复杂页面或 Canvas

---

## 6. 当前建议的项目结构

```text
OpenClaw-android-native-entry/
├─ app/
├─ docs/
│  └─ OpenClaw_HarmonyOS_Android_Deployment_Guide.md
├─ README.md
└─ future/
```

后续 Android 工程内建议分层：

```text
app/src/main/java/.../
├─ ui/
│  ├─ home/
│  ├─ chat/
│  ├─ logs/
│  └─ settings/
├─ domain/
│  ├─ gateway/
│  ├─ termux/
│  └─ auth/
├─ data/
│  ├─ local/
│  ├─ webview/
│  └─ termuxipc/
└─ service/
   └─ status/
```

---

## 7. 对 Codex 的要求

Codex 在本项目中的角色是：

> **协助构建 Android 原生入口工程，而不是擅自改变项目方向。**

Codex 在执行任务时应遵守以下约束：

1. 先阅读本 README 与部署文档
2. 优先保持项目目标聚焦在“原生入口 App”
3. 不擅自改成“重写 OpenClaw 全部功能”
4. 不擅自引入无关云服务、网页部署、iOS 代码或后端系统
5. 每次先完成一个小里程碑，再进入下一步
6. 对每一次改动给出清晰说明
7. 优先生成可运行、可审查、可迭代的代码

---

## 8. 首轮开发任务

Codex 第一轮建议只做以下内容：

1. 创建 Android Studio Kotlin + Compose 项目骨架
2. 建立首页 `HomeScreen`
3. 建立日志页 `LogsScreen`
4. 建立设置页 `SettingsScreen`
5. 首页放置两个按钮：
   - `启动 OpenClaw`
   - `进入聊天`
6. 先用占位逻辑，不接真实 Termux，不接真实 WebView
7. 保证工程可以编译运行

---

## 9. 后续会接入的真实能力

后面将逐步接入：

- 调用 `boot-openclaw`
- 检测 `127.0.0.1:18789` 的 Gateway 状态
- 打开带 token 的 Dashboard
- 展示 OpenClaw 启动日志
- 添加桌面快捷方式
- 添加前台服务和通知
- 逐步减少对 WebView 的依赖

---

## 10. 非目标说明

以下内容不属于当前阶段目标：

- 在 Android 内重新实现完整 OpenClaw 宿主
- 一步到位做成完整数字分身系统
- 一开始就接入全部系统权限与设备能力
- 一开始就做复杂的消息入口整合
- 为所有 Android 设备一次性适配完毕

当前阶段只关注：

> **把这台已完成部署的 HarmonyOS 平板，做出一个稳定、可点击进入的 Android 原生 OpenClaw 入口。**

---

## 11. 开发备注

如无特别说明，请始终基于以下判断工作：

- 宿主层已存在，先不要推倒重来
- 浏览器兼容性是已知问题，因此优先考虑原生入口和受控 WebView
- 第一阶段先追求“能跑通”，第二阶段再追求“更优雅”
- 所有实现都应便于未来逐步演进为更完整的原生客户端

