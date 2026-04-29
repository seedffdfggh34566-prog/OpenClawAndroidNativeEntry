# Delivery Package: V2.1 Android OpenClaw-Style Multi-Thread Chat

更新时间：2026-04-28

## 1. Package 定位

- Package 名称：V2.1 Android OpenClaw-Style Multi-Thread Chat
- 当前状态：`done`
- 优先级：P0
- Package 类型：`implementation / product surface / backend contract increment`
- Authorization source：human instruction on 2026-04-28: 用户要求 Android 前端像 OpenClaw 一样，并支持同一个 Sales Workspace 下多个对话线程。
- 是否允许 package 内部 tasks / steps 连续执行：`yes`
- 完成后是否允许自动进入下游 package：`no`

本 package 是对前一 Android chat surface package 的显式 scope 扩展。前一 package 的 stop condition 会阻止新增 API / migration；本次由人工指令开放新的 delivery package 后执行。

## 2. Package 目标

目标是在同一个 Sales Workspace 项目下支持多个 conversation thread，并让 Android Workspace 页面接近 OpenClaw Control UI 的信息架构：

- thread list / switcher
- large transcript as primary surface
- fixed composer
- running / error / assistant result state
- workspace details / ContextPack / projection 作为次级信息

## 3. Scope

允许：

- 新增最小 conversation thread backend model、migration 和 thread API。
- 旧 `/messages` 和 `/agent-runs/sales-agent-turns` 继续映射到 default thread `main`。
- Android backend client/model/parser 增加 thread API 支持。
- Android Workspace UI 增加 thread switcher、“新对话”、更大的 transcript 和固定 composer。
- 针对 thread history isolation、旧 endpoint compatibility 和 Android build/device smoke 做最小验证。

禁止：

- auth / tenant / CRM / V2.2 search/contact。
- formal LangGraph、WebSocket streaming、完整 `chat.abort` / `chat.inject`。
- 产品 milestone completion claim。
- 读取或打印 `backend/.env` secret 内容。

## 4. Task

- `docs/delivery/tasks/task_v2_1_android_openclaw_multithread_chat.md`（done）

## 5. Stop Conditions

本 package 执行期间未触发需要停止的条件。新增 backend API / migration 是本 package 的显式授权范围；未进入 auth / tenant / CRM / V2.2 search/contact / formal LangGraph。
