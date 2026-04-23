# Skill Spec: `android-logcat-triage`

更新时间：2026-04-23

## Skill name

`android-logcat-triage`

## Purpose

采集、裁剪、归类 Android / 运行时日志，生成可读的排障摘要。

## When to trigger

适用于以下场景：

- 安装失败
- 启动失败
- 运行崩溃
- `Termux / OpenClaw` 异常
- Dashboard / 连接异常
- 需要补充真机运行证据时

通常在 `android-build-verify` 发现运行失败，或 `android-runtime-integration-guard` 要求补更多诊断证据时触发。

## Required repo docs

- 根 `AGENTS.md`
- `app/AGENTS.md`
- 当前 task
- 相关 runbook
- 对应 handoff（如有）

如果需要解释最新 Android 平台行为、权限策略或系统日志含义，可补查官方
Android 文档 / Android Knowledge Base，但这不是默认第一步。

## Allowed tools / commands

- `adb devices`
- `adb logcat -d`
- 必要的只读 `adb shell` 命令

不应依赖破坏性设备命令。

## Expected outputs / evidence

输出应至少包括：

- 复现上下文摘要
- 关键日志片段
- 初步问题归类
- 哪些结论是证据支持的
- 哪些部分仍不确定
- 下一步还需要什么补充证据

推荐归类至少覆盖：

- 安装 / 启动失败
- Manifest / permission / exported
- WebView / Dashboard
- `Termux / command dispatch`
- backend / network / connection

## Stop / escalate conditions

遇到以下情况应停止并升级：

- 无法稳定复现
- 当前日志不足以支持有效结论
- 需要额外设备、网络或外部环境信息
- 日志显示问题已超出 Android 客户端边界，进入 backend / runtime / 设备配置问题
- 需要依赖最新官方 Android guidance 才能解释行为，但尚未查证

## Bundled resources plan

本 Skill 后续允许补充：

- 日志裁剪脚本
- 基于 package/tag/时间窗的过滤模板
- 常见错误分类参考文件

本阶段只固定采集与摘要边界，不要求立刻补脚本。

## Non-goals

- 不在证据不足时宣布 root cause 已确认
- 不替代构建验证
- 不替代人工架构判断
