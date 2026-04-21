# archive_openclaw 说明
更新时间：2026-04-20
## 1. 文档定位
本目录用于存放与 **OpenClaw Android Native Entry / HarmonyOS 宿主部署 
/ 早期数字分身路线** 相关的历史资料。 
这些文件仍然保留，是因为它们对以下场景仍有参考价值： - 
回看早期宿主部署方式 - 回看 HarmonyOS / WebView 兼容性问题 - 
回看原生入口阶段的已验证链路与已知限制 - 回看早期产品化路线设想 
但需要明确：
> **本目录中的文件不再属于当前 AI 销售助手 V1 的主线文档。**
当前主线请优先参考： - `AGENTS.md` - `docs/00_project_overview.md` - 
`docs/01_prd/` - `docs/04_runbooks/` - `docs/05_handoffs/` ---
## 2. 使用原则
### 2.1 当前状态
本目录文件统一视为： - 历史参考 - 专项背景资料 - 技术复盘资料 
不应作为当前项目方向、当前 V1 范围、当前日常工作方式的第一入口。
### 2.2 何时查看本目录
只有在下面情况时，才建议回看这些文件： - 需要恢复或复刻早期 OpenClaw 
宿主部署 - 需要排查 HarmonyOS / Android 设备上的历史兼容性问题 - 
需要理解 Android Native Entry 阶段为什么这样设计 - 
需要复盘早期“数字分身平台”路线的来源
### 2.3 何时不该优先看本目录
如果你当前要处理的是： - AI 销售助手 V1 的产品设计 - 当前 `jianglab + 
Codex` 工作流 - 当前 Git / SSH / GitHub 运维 - 当前任务拆解与 handoff 
那么不应优先进入本目录。 ---
## 3. 文件说明 3.1 `OpenClaw_HarmonyOS_Android_Deployment_Guide.md`
### 类型
宿主部署 / 运行环境工程化文档
### 主要内容
- HarmonyOS 平板上的 Termux 安装与配置 - OpenClaw CLI 安装与初始化 - 
`tmux + sshd + boot-openclaw` 宿主方案 - SSH 隧道访问 Dashboard - 
Android / HarmonyOS 设备迁移时的注意事项
### 当前价值
这份文件仍然是：
> **OpenClaw 宿主层部署与恢复的历史核心参考文档**
### 当前限制
它不是当前 AI 销售助手 V1 的产品文档，也不是当前主开发工作流文档。 
---
## 3.2 `OpenClaw_Android_Native_Entry_Phase_Report.md`
### 类型
阶段性状态总结 / 技术交接文档
### 主要内容
- OpenClaw Android Native Entry 的项目目标 - 当前 Android App 架构 - 
已完成能力 - 已验证链路 - 已知问题与限制 - 运维与排查说明 - 后续建议
### 当前价值
这份文件是：
> **Android Native Entry 阶段历史的主摘要文档**
如果要快速理解“原生入口阶段到底做到了哪一步”，应优先看这份。
### 当前限制
它描述的是历史阶段成果，不是当前 AI 销售助手主线的状态文档。 ---
## 3.3 `OpenClaw_Android_Native_Entry_Development_Worklog.md`
### 类型
开发过程记录 / 工作日志式总结
### 主要内容
- 各阶段开发里程碑 - 问题与解决过程 - 工程搭建与真机调试过程 - 
WebView 兼容性问题的过程性记录
### 当前价值
它保留了：
> **比 Phase Report 更细的开发过程信息**
适合在需要回看“当时是怎么一路排查出来的”时使用。
### 当前限制
它与 `OpenClaw_Android_Native_Entry_Phase_Report.md` 
高度重叠，当前不应作为首要接手入口。 ---
## 3.4 `openclaw_android_roadmap_summary.md`
### 类型
早期路线设想 / 产品化方向总结
### 主要内容
- 数字分身平台长期目标 - 宿主层与产品层分离 - Termux → APK 安装器 / 
Standalone APK → 自有 Runtime App + Product App 的路线设想
### 当前价值
这份文件中仍然值得保留的一条核心原则是：
> **宿主与产品分离**
### 当前限制
其余大部分内容属于更早期的路线设想，已经不再是当前主线，不应继续作为当前项目来源中的主文档。 
---
## 4. 当前建议保留方式
当前建议将本目录中的文件全部视为： - archive-only - 
默认不加入当前主来源集合 - 需要时再临时打开参考 如果是在 ChatGPT 
项目“来源”中做精简，建议：
### 默认只保留
- 本 README
### 需要时再临时加入
- `OpenClaw_HarmonyOS_Android_Deployment_Guide.md` - 
`OpenClaw_Android_Native_Entry_Phase_Report.md`
### 不建议长期保留为主来源
- `OpenClaw_Android_Native_Entry_Development_Worklog.md` - 
`openclaw_android_roadmap_summary.md` ---
## 5. 与当前主线的关系
当前项目主线已经转为：
> **AI 销售助手 V1 的定义、收敛与标准化 agent 开发**
因此，本目录中的文档与当前主线的关系应理解为： - **不是当前主线** - 
**不是当前第一入口** - **只是历史基础设施与历史阶段资料** ---
## 6. 一句话总结
`archive_openclaw/` 保存的是：
> **OpenClaw 宿主部署、Android Native Entry 阶段、以及早期数字分身路线的历史参考资料；这些文件保留，但不再主导当前 AI 销售助手 V1 的工作流与文档体系。**

