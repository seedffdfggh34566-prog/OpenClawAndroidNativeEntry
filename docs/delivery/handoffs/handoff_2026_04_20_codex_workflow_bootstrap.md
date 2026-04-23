# 阶段性交接：Codex 工作流基础设施启动

> 迁移说明：本文档记录的是 2026-04-20 的阶段状态，正文中保留了当时的旧目录结构表述，仅作历史记录，不作为当前正式路径导航依据。

更新时间：2026-04-20

## 1. 文档定位

本文档用于记录本阶段围绕 **`jianglab` + Codex + Git + 文档体系** 所完成的关键工作，并为后续人工或 AI 接手提供阶段性交接说明。

本阶段的重点不是产品功能开发，而是：

- 明确当前项目主线
- 建立 `jianglab` 作为唯一工作区
- 打通 Codex app 远程连接 `jianglab`
- 打通 `jianglab -> GitHub` 的 SSH 推送
- 搭建最小文档骨架
- 建立后续 agent 开发的基本规则

---

## 2. 本阶段完成内容

## 2.1 项目主线已明确切换

当前项目已不再以早期 **OpenClaw Android Native Entry / HarmonyOS 宿主入口实验** 为主要目标。

当前主线已收口为：

> **AI 销售助手 V1**

当前 V1 核心闭环为：

1. 产品学习
2. 获客分析
3. 结构化输出 / 报告

当前明确不优先推进：

- 联系方式抓取
- 自动触达
- 完整 CRM
- 大而全企业销售平台能力

---

## 2.2 `jianglab` 已确立为唯一工作区

当前正式工作区已经明确为：

```text
jianglab:/home/yulin/projects/OpenClawAndroidNativeEntry
```

当前原则为：

- 正式代码、文档、任务和 Git 操作都以该仓库为准
- 不维护 Windows 本地第二份正式工作副本
- Windows 端主要作为远程控制台使用

---

## 2.3 Git 仓库状态已理清

已确认：

- `~/projects/OpenClawAndroidNativeEntry` 是正常 Git 仓库
- `origin` 已连接 GitHub
- 当前分支为 `main`
- 仓库曾存在 `gradlew` 权限位变化
- 该变化已作为 Linux 可执行权限合理提交
- 本地改动已成功 push 到 GitHub

当前 Git 推送已成功，说明主仓库与远程同步链路正常。

---

## 2.4 `jianglab -> GitHub` 的 SSH 推送已打通

早期 GitHub 远程地址为 HTTPS，推送时出现：

- 要求输入 GitHub 用户名
- 要求输入 Password
- 网页密码方式被拒绝

后续已完成：

- 在 `jianglab` 上配置 GitHub SSH key
- 验证 `ssh -T git@github.com`
- 将 `origin` 从 HTTPS 改为 SSH
- 成功执行 `git push origin main`

当前结论：

> `jianglab -> GitHub` 已稳定采用 SSH 推送方式。

---

## 2.5 Codex app 远程连接 `jianglab` 已打通

已完成：

- Windows 本机配置 SSH config
- 修复 Codex app 手工连接时误用 Windows 本地用户名的问题
- 使用正确的 `User yulin`
- 使用正确的 Windows 私钥
- 通过 host alias 连接 `jianglab`
- 成功在 Codex Windows App 中打开远程项目

当前结论：

> Codex app 已能把 `jianglab` 上的真实仓库作为远程项目打开。

---

## 2.6 当前工具分工已明确

当前推荐的工具分工已收口为：

### Codex app
主控制台，用于：

- 远程线程
- 任务执行
- agent 开发
- 后续 review

### FinalShell
辅助终端，用于：

- SSH 登录
- 文件上传下载
- 系统运维
- Git 基础命令
- 环境排查

### VS Code
当前已明确不再作为主工作流必需组成。

---

## 2.7 文档骨架已建立

`docs/` 目录当前已形成最小骨架：

```text
docs/
├─ 00_project_overview.md
├─ 01_prd/
├─ 02_specs/
├─ 03_tasks/
├─ 04_runbooks/
├─ 05_handoffs/
├─ 06_decisions/
└─ archive_openclaw/
```

此外，仓库根目录已规划放置：

```text
AGENTS.md
```

---

## 2.8 OpenClaw 历史资料已降级归档

与早期 OpenClaw 原生入口、HarmonyOS 宿主部署、Dashboard 兼容性修复相关的文档，已不再作为当前主线文档。

当前处理原则为：

- 保留历史价值
- 放入 `docs/archive/openclaw/`
- 不混入当前 AI 销售助手 V1 主线

---

## 3. 本阶段新增/起草的关键文档

本阶段已起草或规划的关键文档包括：

### 仓库根目录
- `AGENTS.md`

### `docs/`
- `00_project_overview.md`
- `04_runbooks/developer_workflow_playbook.md`
- `04_runbooks/jianglab_codex_ops.md`
- `04_runbooks/git_github_ssh_and_remote_access.md`

### 待继续补充
- `01_prd/v1_reference_notes.md`
- `01_prd/ai_sales_assistant_v1_prd.md`
- 第一批正式 task 文档

---

## 4. 当前工作方式总结

当前项目的标准工作方式已初步明确为：

1. `jianglab` 是唯一工作区
2. Codex app 是主控制台
3. FinalShell 是辅助终端
4. 正式代码与文档以 `jianglab` 仓库为准
5. GitHub 推送通过 SSH
6. 产品变化先改文档，再进入实现
7. 新功能先建 task，再开 Codex 线程
8. 功能完成后的细节修改，按 follow-up task 处理

---

## 5. 当前尚未完成的内容

尽管基础设施已明显成型，但本阶段**尚未进入正式产品功能开发**。

当前尚未完成的重点包括：

### 5.1 参考研究尚未正式收口
虽然已有竞品分析基础，但当前还未形成系统化的：

- `v1_reference_notes.md`

### 5.2 V1 PRD 尚未正式落地
当前主线和范围已明确，但正式 PRD 仍未写完。

### 5.3 第一个正式产品 task 尚未开始
当前尚未开始真正的产品功能开发任务。

### 5.4 `AGENTS.md` 与 overview 等文件仍处于初版阶段
已有初稿，但后续还需要在真实使用中小幅修正。

---

## 6. 当前风险与注意事项

## 6.1 不要让 Codex 直接从“聊天式需求”开始开发
当前阶段应先建立 task，再执行。

## 6.2 不要重新把 OpenClaw 历史文档当作当前主线
这些文档只作历史参考。

## 6.3 不要把 Windows 本地目录当正式工作区
所有正式文件与 Git 操作都应以 `jianglab` 为准。

## 6.4 不要频繁改 `AGENTS.md`
`AGENTS.md` 属于仓库级规则文件，应低频维护。  
更高频变化应优先写到：

- `00_project_overview.md`
- `01_prd/`
- `03_tasks/`
- `05_handoffs/`

## 6.5 当前不要急于并行多功能线程
虽然 Codex app 已支持远程线程，但当前更适合先用小任务验证工作流，而不是同时跑很多功能任务。

---

## 7. 后续最推荐的下一步

当前最合理的下一步顺序为：

### Step 1
完成：

- `AGENTS.md`
- `00_project_overview.md`
- 本轮 runbooks

### Step 2
编写：

- `docs/product/research/v1_reference_notes.md`

完成面向 V1 的定向参考研究收口。

### Step 3
编写：

- `docs/product/prd/ai_sales_assistant_v1_prd.md`

把 V1 做什么、不做什么、核心流程与验收标准正式写清。

### Step 4
再拆第一个正式产品 task，交给 Codex 执行。

---

## 8. 本阶段一句话结论

本阶段已经完成：

> **从“零散远程开发尝试”到“以 `jianglab` 为唯一工作区、以 Codex app 为主控制台、以 Git SSH 推送为基础、并具备最小文档体系的 agent 开发基础设施收口”。**
