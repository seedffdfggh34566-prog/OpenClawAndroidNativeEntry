# Task：Android CLI Knowledge Base 试点接入

更新时间：2026-04-23

## 1. 任务定位

- 任务名称：Android CLI Knowledge Base 试点接入
- 建议路径：`docs/delivery/tasks/task_android_cli_knowledge_base_trial.md`
- 当前状态：`done`
- 优先级：P1

---

## 2. 任务目标

在 `jianglab` 上试点安装并验证 Android CLI，使当前仓库从“规则层已接入 Android Knowledge Base”推进到“命令行可实际访问 Android Knowledge Base”。

本任务完成后，Android CLI 在当前仓库中的定位为：

- **推荐增强工具**
- 不是仓库前置依赖
- 不替代 `adb + gradle + docs + task/handoff` 主链路

---

## 3. 当前背景

当前仓库已经完成：

- Android Knowledge Base 在 Android 规则层、workflow 文档和相关 Skill specs 中的接入
- Android CLI 在文档中的“可选增强”定位

本任务开始前的现实情况是：

- `command -v android` 无结果
- `adb` 已在 `jianglab` 上可用
- 官方安装脚本默认写入 `/usr/local/bin`
- 当前用户对 `/usr/local/bin` 无写权限，且 `sudo` 需要密码

因此本任务需要验证：

1. Android CLI 是否能在当前主机上以低风险方式安装
2. `android docs search` / `android docs fetch` 是否能稳定服务于当前仓库
3. 是否值得把 Android CLI 从“后续试点项”提升为“推荐增强工具”

---

## 4. 范围

本任务 In Scope：

- 验证当前 `jianglab` 环境中的 Android CLI 可安装性
- 安装 Android CLI
- 验证 `android --version` / `android -h`
- 验证 `android docs search` / `android docs fetch`
- 用当前仓库直接相关的 Android 问题做样例查询
- 记录安装方式、环境要求、收益与限制
- 在试点成功后最小更新 `docs/how-to/operate/jianglab_codex_ops.md`
- 新增本 task 与对应 handoff

本任务 Out of Scope：

- 修改 Android 产品代码
- 修改测试基建
- 替换 `adb + gradle` 主链路
- 把 Android CLI 升格为强制依赖
- 一次性试点 `android run`、`android layout`、`android screen capture`

---

## 5. 涉及文件

高概率涉及：

- `docs/delivery/tasks/task_android_cli_knowledge_base_trial.md`
- `docs/delivery/handoffs/handoff_2026_04_23_android_cli_knowledge_base_trial.md`
- `docs/how-to/operate/jianglab_codex_ops.md`

参考文件：

- `docs/delivery/tasks/task_android_knowledge_base_workflow_integration.md`
- `docs/delivery/handoffs/handoff_2026_04_23_android_knowledge_base_workflow_integration.md`
- `docs/how-to/operate/developer_workflow_playbook.md`

---

## 6. 产出要求

至少应产出：

1. 一个正式 task 文件
2. 一个对应 handoff 文件
3. Android CLI 安装与验证结论
4. 如试点成功，对 `jianglab` 运维/workflow 文档的最小同步

---

## 7. 验收标准

满足以下条件可认为完成：

1. `android` 命令在 `jianglab` 可用
2. `android --version` 和 `android -h` 正常
3. `android docs search` 能返回有效结果
4. `android docs fetch <kb://...>` 能输出文档内容
5. 至少完成 2 个与当前仓库直接相关的问题样例
6. handoff 中明确给出结论：
   - Android CLI 是否值得纳入仓库“推荐增强工具”
   - 它仍然是可选增强，不替代主链路
   - 当前限制和后续建议是什么

---

## 8. 推荐执行顺序

建议执行顺序：

1. 环境摸底：确认 `android`、`adb`、SDK 路径、`PATH`
2. 确认官方 Linux 下载入口与安装方式
3. 解决当前环境与官方脚本的路径权限冲突
4. 安装 Android CLI，并验证版本与帮助命令
5. 用 `docs search` / `docs fetch` 做仓库相关样例验证
6. 评估收益与限制
7. 更新 handoff 与 `jianglab_codex_ops.md`

---

## 9. 风险与注意事项

- 官方安装脚本默认安装到 `/usr/local/bin`，当前环境没有无密码 sudo，因此不能照搬脚本
- 本任务只能使用官方来源，不能引入非官方镜像
- 首次并发运行 `android docs search` 可能与 Knowledge Base 索引初始化发生竞争
- 本任务成功后也不能把 Android CLI 写成强制依赖

---

## 10. 下一步衔接

本任务完成后，推荐继续：

1. 在 Android 相关研究与实现 thread 中，把 Android CLI 作为推荐增强入口使用
2. 观察一段时间，再决定是否需要把 `android docs` 的使用说明回写到 Android 相关 Skill specs

---

## 11. 实际产出

本次已完成以下产出：

1. 在 `jianglab` 上安装 Android CLI
2. 验证 `android --version`、`android -h`
3. 验证 `android docs search`、`android docs fetch`
4. 用 3 组与当前仓库直接相关的问题完成样例验证
5. 新增本 task 与对应 handoff
6. 最小更新 `docs/how-to/operate/jianglab_codex_ops.md`

---

## 12. 本次定稿边界

本次明确采用以下边界：

- 只试点 Android CLI 的 Knowledge Base 能力
- 不扩展到 `android run`、`android layout`、`android screen capture`
- Android CLI 当前定位为推荐增强，不是前置依赖
- 保留 `adb + gradle + docs + task/handoff` 作为主链路

---

## 13. 已做验证

本次已完成以下验证：

1. `command -v android` 从“无结果”变为 `/home/yulin/bin/android`
2. `android --version` 返回 `0.7.15232955`
3. `android -h` 正常输出命令列表
4. `android info` 返回：
   - `sdk: /usr/lib/android-sdk`
   - `version: 0.7.15232955`
5. `android docs search` 成功返回以下类别的 `kb://...` 结果：
   - Compose screenshot testing
   - `AndroidManifest.xml` / exported / deep link / permission
   - Navigation Compose / architecture guidance
6. `android docs fetch` 成功拉取以下文档内容：
   - `kb://android/privacy-and-security/risks/access-control-to-exported-components`
   - `kb://android/training/testing/ui-tests/screenshot`
   - `kb://android/develop/ui/compose/navigation`
7. `git diff --check`

---

## 14. 实际结果说明

本次试点结论为：

1. Android CLI 已可在 `jianglab` 上使用
2. Android Knowledge Base 已可通过命令行实际访问
3. Android CLI 值得纳入当前仓库的**推荐增强工具**集合
4. 由于官方安装脚本需要写入 `/usr/local/bin` 且当前环境没有无密码 sudo，本次采用了官方 Linux 二进制直链安装到 `/home/yulin/bin/android`
5. 当前仍不建议把 Android CLI 设为仓库前置依赖或主链路替代品
