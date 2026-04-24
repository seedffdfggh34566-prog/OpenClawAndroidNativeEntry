# V1 后端最小 API contract

更新时间：2026-04-21

## 1. 文档定位

本文档用于冻结 **AI 销售助手 V1** 的最小后端 API contract。

它服务于以下后续工作：

- Android 壳层从占位数据切换到真实数据
- 后端最小实现线程
- runtime 输出与正式对象写回边界收口

本文档不是：

- 完整 REST 平台设计
- 数据库 schema 文档
- ORM 设计文档
- 完整鉴权方案

关联文档：

- `docs/product/overview.md`
- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/architecture/system-context.md`
- `docs/reference/schemas/v1-domain-model-baseline.md`
- `docs/architecture/clients/mobile-information-architecture.md`
- `docs/delivery/tasks/task_v1_backend_api_contract.md`

---

## 2. 当前结论

V1 当前只冻结以下 8 个最小接口：

- `POST /product-profiles`
- `POST /product-profiles/{id}/confirm`
- `GET /product-profiles/{id}`
- `POST /analysis-runs`
- `GET /analysis-runs/{id}`
- `GET /lead-analysis-results/{id}`
- `GET /reports/{id}`
- `GET /history`

当前采用以下关键 contract 决策：

1. 后端是正式对象权威真相
2. runtime 只返回草稿形态和执行结果，不直接定义正式对象生命周期
3. `POST /analysis-runs` 采用统一入口，用 `run_type` 区分：
   - `lead_analysis`
   - `report_generation`
4. `/history` 采用首页聚合结构，优先服务 Android 首页与 History 页
5. 正式对象状态与 `AgentRun` 状态严格分离

---

## 3. 总体 contract 原则

### 3.1 权威边界

- `ProductProfile`
- `LeadAnalysisResult`
- `AnalysisReport`
- `AgentRun`

以上对象均以后端为权威来源。

手机端不应依赖：

- 聊天消息
- runtime 私有状态
- 宿主路径
- 手工脚本输出

### 3.2 Runtime 与后端分工

runtime 负责：

- 执行分析
- 返回草稿形态
- 返回证据、缺失字段和错误信息

后端负责：

- 创建正式对象
- 校验 runtime 输出
- 写回正式对象
- 赋予状态和版本
- 暴露正式 API

### 3.3 当前非目标

当前不做：

- 完整 CRUD
- 搜索、分页、筛选
- 鉴权细节
- 多租户权限矩阵
- CRM / 联系人 / 自动触达扩展

---

## 4. 最小通用结构

## 4.1 `ObjectRef`

用于表达 `AgentRun.input_refs` 和 `AgentRun.output_refs`。

最小字段：

- `object_type`
- `object_id`
- `version` 可选

支持的 `object_type`：

- `product_profile`
- `lead_analysis_result`
- `analysis_report`

## 4.2 `AgentRunSummary`

最小字段：

- `id`
- `run_type`
- `status`
- `trigger_source`
- `started_at`
- `ended_at`
- `error_message`

## 4.3 `ProductProfileSummary`

最小字段：

- `id`
- `name`
- `one_line_description`
- `status`
- `version`
- `updated_at`

## 4.4 `ProductProfileDetail`

最小字段：

- `id`
- `name`
- `one_line_description`
- `status`
- `version`
- `target_customers`
- `target_industries`
- `typical_use_cases`
- `pain_points_solved`
- `core_advantages`
- `delivery_model`
- `constraints`
- `missing_fields`
- `created_at`
- `updated_at`

## 4.5 `AnalysisReportDetail`

最小字段：

- `id`
- `product_profile_id`
- `lead_analysis_result_id`
- `status`
- `title`
- `summary`
- `sections`
- `version`
- `updated_at`

## 4.6 `RecentHistoryItem`

最小字段：

- `object_type`
- `id`
- `title`
- `status`
- `updated_at`

## 4.7 `HistoryResponse`

最小字段：

- `current_run`
- `latest_product_profile`
- `latest_analysis_result`
- `latest_report`
- `recent_items`

---

## 5. 状态与对象关系

## 5.1 正式对象状态

### `ProductProfile`

```text
draft → confirmed → superseded
```

说明：

- `draft`：已写回正式对象，但仍待用户确认
- `confirmed`：可作为正式分析输入
- `superseded`：被更新版本替代

### `LeadAnalysisResult`

```text
draft → published → superseded
```

说明：

- `draft`：runtime 草稿已写回正式对象，但尚未作为最终用户结果发布
- `published`：可展示、可复看
- `superseded`：被新结果替代

### `AnalysisReport`

```text
draft → published → superseded
```

说明：

- `draft`：草稿报告已写回
- `published`：可被查看与复用
- `superseded`：被新报告替代

### `AgentRun`

```text
queued → running → succeeded | failed | cancelled
```

说明：

- 失败、重试、取消只体现在 `AgentRun`
- `superseded` 不表示失败，只表示新版本替代

## 5.2 `AgentRun` 与正式对象的关系

- `AgentRun.input_refs` 表示本次运行读取了哪些正式对象
- `AgentRun.output_refs` 表示本次运行产出了哪些正式对象
- `AgentRun` 不反向拥有正式对象生命周期

当前最小关系约定：

- `lead_analysis`：
  - 输入：一个 `confirmed` 的 `ProductProfile`
  - 输出：一个 `LeadAnalysisResult`
- `report_generation`：
  - 输入：一个 `ProductProfile` + 一个 `LeadAnalysisResult`
  - 输出：一个 `AnalysisReport`

---

## 6. 接口定义

## 6.1 `POST /product-profiles`

### 职责

创建一个新的 `ProductProfile` 初始草稿。

该接口只承接产品画像草稿创建，不负责确认。

### 最小请求字段

```json
{
  "name": "AI 销售助手 V1",
  "one_line_description": "帮助用户先讲清产品，再生成获客分析结果。",
  "source_notes": "可选，自由文本或上传材料摘要。"
}
```

### 最小响应字段

```json
{
  "product_profile": {
    "id": "pp_001",
    "name": "AI 销售助手 V1",
    "one_line_description": "帮助用户先讲清产品，再生成获客分析结果。",
    "status": "draft",
    "version": 1,
    "updated_at": "2026-04-21T10:00:00Z"
  },
  "current_run": null,
  "links": {
    "self": "/product-profiles/pp_001"
  }
}
```

### 说明

- 创建成功后默认 `status = draft`
- 需要通过 `POST /product-profiles/{id}/confirm` 将状态升级为 `confirmed`

## 6.2 `POST /product-profiles/{id}/confirm`

### 职责

将 `ProductProfile` 从 `draft` 状态升级为 `confirmed`。

### 最小响应字段

```json
{
  "product_profile": {
    "id": "pp_001",
    "name": "AI 销售助手 V1",
    "one_line_description": "帮助用户先讲清产品，再生成获客分析结果。",
    "status": "confirmed",
    "version": 2,
    "updated_at": "2026-04-21T10:15:00Z"
  }
}
```

### 说明

- 幂等：对已经是 `confirmed` 的状态再次调用仍返回成功
- 确认后版本号 `version` 自动递增
- 只有 `confirmed` 的 `ProductProfile` 才能作为 `lead_analysis` 的输入

## 6.3 `GET /product-profiles/{id}`

### 职责

读取单个 `ProductProfile` 详情。

Android 产品画像确认页应依赖该接口作为主要读取入口。

### 最小响应字段

```json
{
  "product_profile": {
    "id": "pp_001",
    "name": "AI 销售助手 V1",
    "one_line_description": "帮助用户先讲清产品，再生成获客分析结果。",
    "status": "draft",
    "version": 1,
    "target_customers": ["中小企业老板", "销售负责人"],
    "target_industries": ["企业服务", "教育培训"],
    "typical_use_cases": ["产品定位梳理", "获客方向澄清"],
    "pain_points_solved": ["不知道卖给谁", "缺少第一版分析材料"],
    "core_advantages": ["对话式澄清", "结构化沉淀"],
    "delivery_model": "移动端控制入口 + 本地后端处理",
    "constraints": ["当前仍是 V1 最小闭环"],
    "missing_fields": ["价格区间", "销售区域"],
    "created_at": "2026-04-21T10:00:00Z",
    "updated_at": "2026-04-21T10:12:00Z"
  }
}
```

### 说明

- 可返回 `draft` 或 `confirmed` 的正式对象形态
- `missing_fields` 用于帮助 Android 确认页展示“仍待补充”的信息

## 6.4 `POST /analysis-runs`

### 职责

统一创建分析类执行任务。

使用 `run_type` 区分：

- `lead_analysis`
- `report_generation`

### 最小请求字段

```json
{
  "run_type": "lead_analysis",
  "product_profile_id": "pp_001",
  "lead_analysis_result_id": null,
  "trigger_source": "android_home"
}
```

当 `run_type = report_generation` 时：

- `lead_analysis_result_id` 必填

### 最小响应字段

```json
{
  "agent_run": {
    "id": "run_001",
    "run_type": "lead_analysis",
    "status": "queued",
    "triggered_by": "user",
    "trigger_source": "android_home",
    "input_refs": [
      {
        "object_type": "product_profile",
        "object_id": "pp_001"
      }
    ],
    "output_refs": [],
    "started_at": null,
    "ended_at": null,
    "error_message": null
  }
}
```

### 行为约束

- `lead_analysis` 只能接受 `confirmed` 的 `ProductProfile`
- `report_generation` 只能接受已有 `LeadAnalysisResult`
- 创建成功后默认 `AgentRun.status = queued`

## 6.5 `GET /analysis-runs/{id}`

### 职责

查询单个 `AgentRun` 的状态与输出关联。

Android 轮询状态页和 History 页应优先依赖该接口。

### 最小响应字段

```json
{
  "agent_run": {
    "id": "run_001",
    "run_type": "lead_analysis",
    "status": "running",
    "triggered_by": "user",
    "trigger_source": "android_home",
    "input_refs": [
      {
        "object_type": "product_profile",
        "object_id": "pp_001",
        "version": 1
      }
    ],
    "output_refs": [],
    "started_at": "2026-04-21T10:15:00Z",
    "ended_at": null,
    "error_message": null
  },
  "result_summary": null
}
```

当运行成功并已有输出时：

```json
{
  "agent_run": {
    "id": "run_001",
    "run_type": "lead_analysis",
    "status": "succeeded",
    "triggered_by": "user",
    "trigger_source": "android_home",
    "input_refs": [
      {
        "object_type": "product_profile",
        "object_id": "pp_001",
        "version": 1
      }
    ],
    "output_refs": [
      {
        "object_type": "lead_analysis_result",
        "object_id": "lar_001",
        "version": 1
      }
    ],
    "started_at": "2026-04-21T10:15:00Z",
    "ended_at": "2026-04-21T10:18:00Z",
    "error_message": null
  },
  "result_summary": {
    "lead_analysis_result_id": "lar_001",
    "status": "published",
    "updated_at": "2026-04-21T10:18:00Z"
  }
}
```

### 失败、取消、重试表现

- `failed`
  - `error_message` 必填
- `cancelled`
  - 保留已知输入，不保证输出
- `retry`
  - 不在同一 `AgentRun` 内复用状态
  - 建议重新创建新的 `AgentRun`

## 6.6 `GET /lead-analysis-results/{id}`

### 职责

读取单个 `LeadAnalysisResult` 详情。

Android 分析结果页应依赖该接口作为主要读取入口。

### 最小响应字段

```json
{
  "lead_analysis_result": {
    "id": "lar_001",
    "product_profile_id": "pp_001",
    "created_by_agent_run_id": "run_001",
    "title": "第一版获客分析结果",
    "analysis_scope": "v1_stub",
    "summary": "基于 AI 销售助手 V1 的最小占位获客分析结果...",
    "priority_industries": ["企业服务", "教育培训"],
    "priority_customer_types": ["中小企业老板", "销售负责人"],
    "scenario_opportunities": ["产品定位梳理", "获客方向澄清"],
    "ranking_explanations": ["优先选择更容易快速说明产品价值的行业方向。"],
    "recommendations": ["先验证企业服务方向的需求表达是否足够清晰。"],
    "risks": ["当前为 stub 结果，尚未接入真实 OpenClaw runtime。"],
    "limitations": ["分析深度受限于固定模板与本地占位逻辑。"],
    "status": "published",
    "version": 1,
    "created_at": "2026-04-21T10:18:00Z",
    "updated_at": "2026-04-21T10:18:00Z"
  }
}
```

### 说明

- 可返回 `draft` 或 `published` 的正式对象形态
- 字段列表与 `LeadAnalysisResult` 模型一一对应
- Android 端使用该接口展示完整分析结果，不再仅依赖 `/history` 摘要

## 6.7 `GET /reports/{id}`

### 职责

读取单个 `AnalysisReport`。

该接口只定义读取，不定义报告创建接口。

报告创建通过 `POST /analysis-runs` 的 `report_generation` 完成。

### 最小响应字段

```json
{
  "report": {
    "id": "rep_001",
    "product_profile_id": "pp_001",
    "lead_analysis_result_id": "lar_001",
    "status": "published",
    "title": "AI 销售助手 V1 获客分析报告",
    "summary": "该报告总结产品定位、优先行业方向与下一步建议。",
    "sections": [
      {
        "title": "产品理解摘要",
        "body": "当前产品聚焦帮助用户澄清产品和获客方向。"
      },
      {
        "title": "优先方向",
        "body": "建议优先验证企业服务和教育培训方向。"
      }
    ],
    "version": 1,
    "updated_at": "2026-04-21T10:28:00Z"
  }
}
```

## 6.8 `GET /history`

### 职责

为首页和 History 页返回聚合读取结果。

当前采用首页聚合结构，不做通用时间线。

### 最小响应字段

```json
{
  "current_run": {
    "id": "run_002",
    "run_type": "report_generation",
    "status": "running",
    "trigger_source": "android_report",
    "started_at": "2026-04-21T10:30:00Z",
    "ended_at": null,
    "error_message": null
  },
  "latest_product_profile": {
    "id": "pp_001",
    "name": "AI 销售助手 V1",
    "one_line_description": "帮助用户先讲清产品，再生成获客分析结果。",
    "status": "confirmed",
    "version": 1,
    "updated_at": "2026-04-21T10:12:00Z"
  },
  "latest_analysis_result": {
    "id": "lar_001",
    "status": "published",
    "title": "第一版获客分析结果",
    "updated_at": "2026-04-21T10:18:00Z"
  },
  "latest_report": {
    "id": "rep_001",
    "status": "published",
    "title": "AI 销售助手 V1 获客分析报告",
    "updated_at": "2026-04-21T10:28:00Z"
  },
  "recent_items": [
    {
      "object_type": "analysis_report",
      "id": "rep_001",
      "title": "AI 销售助手 V1 获客分析报告",
      "status": "published",
      "updated_at": "2026-04-21T10:28:00Z"
    },
    {
      "object_type": "lead_analysis_result",
      "id": "lar_001",
      "title": "第一版获客分析结果",
      "status": "published",
      "updated_at": "2026-04-21T10:18:00Z"
    },
    {
      "object_type": "product_profile",
      "id": "pp_001",
      "title": "AI 销售助手 V1",
      "status": "confirmed",
      "updated_at": "2026-04-21T10:12:00Z"
    }
  ]
}
```

### 说明

- `current_run` 可为空
- `latest_product_profile`、`latest_analysis_result`、`latest_report` 可为空
- `recent_items` 建议最多返回 3-5 条
- 当前不扩展搜索、筛选、分页

---

## 7. Runtime 与后端边界

### 7.1 Runtime 返回什么

runtime 可以返回：

- `ProductProfileDraft`
- `LeadAnalysisResultDraft`
- `AnalysisReportDraft`
- 缺失字段
- 证据引用
- 错误信息

这些都是中间结果，不直接暴露为正式 API 主对象。

### 7.2 后端暴露什么

后端对外暴露：

- 正式对象
- 正式对象的状态和版本
- `AgentRun` 的状态和引用关系
- 首页和历史页所需聚合数据

### 7.3 当前必须避免的耦合

必须避免：

- 让 Android 直接依赖聊天记录
- 让 runtime 越过产品后端直接写正式对象
- 让失败状态直接写入 `ProductProfile`、`LeadAnalysisResult`、`AnalysisReport`
- 把技术宿主路径或脚本输出作为正式 contract

---

## 8. Android 壳层依赖说明

Android 壳层最小依赖关系如下：

- 首页：依赖 `GET /history`
- History 页：依赖 `GET /history`
- 产品画像页：依赖 `GET /product-profiles/{id}`
- 发起获客分析：依赖 `POST /analysis-runs`
- 轮询执行状态：依赖 `GET /analysis-runs/{id}`
- 分析结果详情页：依赖 `GET /lead-analysis-results/{id}`
- 报告详情页：依赖 `GET /reports/{id}`

当前不要求 Android 直接读取 runtime 草稿对象。

Android 应依赖后端已经校验并正式写回的对象和聚合结果。

---

## 9. 已知限制

本次最小 contract 明确保留以下限制：

- 不包含确认 `ProductProfile` 的接口
- 不包含 `PATCH`、删除、搜索、分页
- 不包含鉴权实现方案
- 不包含完整错误码体系

如后续需要扩展，应在新的 task 或 spec 中单独冻结，而不是在本轮直接扩张。
