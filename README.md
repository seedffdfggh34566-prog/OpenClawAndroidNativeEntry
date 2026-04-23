# OpenClawAndroidNativeEntry

> 当前仓库名保留历史来源，但当前正式主线已切换为 **AI 销售助手 V1**。  
> 当前建议先阅读 [docs/README.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/README.md) 与 [AGENTS.md](/home/yulin/projects/OpenClawAndroidNativeEntry/AGENTS.md)。

## 当前定位

这个仓库现在应理解为：

- **AI 销售助手 V1 的主仓库**
- **后端优先的单仓库工作区**
- **Android 为当前入口之一，而不是整个项目本体**

当前系统主线为：

> **正式后端承载业务主真相，OpenClaw 作为 runtime，Android / 后续 iOS / PC 作为控制入口。**

---

## V1 当前目标

V1 只验证三件事：

1. 产品学习
2. 线索 / 获客分析
3. 结构化分析结果与报告输出

当前明确不做：

- 完整 CRM
- 自动触达 / 自动外呼
- 大型企业工作流平台
- 一开始就做完整多端产品矩阵
- 没有明确授权的大规模架构重写

---

## 当前系统形态

当前阶段的推荐理解如下：

- `backend/`
  - 正式业务后端
  - 权威对象主存
  - 任务状态与结果沉淀
- OpenClaw runtime
  - agent runtime / execution layer
  - 模型调用与工具调用
- `app/`
  - 当前 Android 控制入口
  - 后续可与 iOS / PC 一起成为多个客户端入口之一
- `docs/`
  - 当前项目的正式文档控制平面

---

## 当前文档入口

无论是人工还是 agent，建议按以下顺序进入仓库：

1. [AGENTS.md](/home/yulin/projects/OpenClawAndroidNativeEntry/AGENTS.md)
2. [docs/README.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/README.md)
3. [docs/product/overview.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/product/overview.md)
4. [docs/product/prd/ai_sales_assistant_v1_prd.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/product/prd/ai_sales_assistant_v1_prd.md)
5. [docs/adr/ADR-001-backend-deployment-baseline.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/adr/ADR-001-backend-deployment-baseline.md)
6. [docs/delivery/tasks/_active.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/delivery/tasks/_active.md)

当前正式 docs 结构为：

```text
docs/
├─ README.md
├─ product/
├─ architecture/
├─ reference/
├─ how-to/
├─ adr/
├─ delivery/
└─ archive/
```

旧编号目录已经迁出，不再作为正式入口。

---

## 当前仓库结构

```text
OpenClawAndroidNativeEntry/
├─ app/          # Android 控制入口
├─ backend/      # V1 最小正式后端
├─ docs/         # 正式文档与 agent 控制平面
└─ ...
```

当前最重要的是：

- 保持后端优先
- 用 task / handoff 驱动 agent 工作流
- 让 Android 逐步从占位数据切到真实后端

---

## 历史背景

这个仓库起源于早期的 OpenClaw Android Native Entry / HarmonyOS 宿主入口实验，因此仓库名和部分历史资料保留了旧痕迹。

这些内容现在只作为背景参考，统一放在：

- [docs/archive/openclaw/README.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/archive/openclaw/README.md)

历史资料不再主导当前 AI 销售助手 V1 的方向、任务入口或日常工作流。
