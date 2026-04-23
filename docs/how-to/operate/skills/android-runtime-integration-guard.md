# Skill Spec: `android-runtime-integration-guard`

更新时间：2026-04-23

## Skill name

`android-runtime-integration-guard`

## Purpose

对 Android 高风险运行时集成改动做守门与验证升级，避免在证据不足时误报完成。

## When to trigger

适用于触及以下高风险区域的改动：

- `termux/*`
- `MainActivity`
- `OpenClawApp`
- `navigation/*`
- `AndroidManifest.xml`
- OpenClaw 启动链路
- Dashboard URL
- 权限 / exported / intent / deep link 相关逻辑

它应作为高风险 Android 任务的前置判断器，通常先于 `android-build-verify` 触发。

## Required repo docs

- 根 `AGENTS.md`
- `app/AGENTS.md`
- `docs/architecture/clients/android-client-implementation-constraints.md`
- 当前 task
- 相关 runbook / handoff

如果判断涉及最新 Manifest、权限、导出组件、deep link 或平台运行时 guidance，
应优先查官方 Android 文档 / Android Knowledge Base，再决定验证升级要求。

## Allowed tools / commands

- 构建命令
- `adb devices`
- 安装 / 启动命令
- `adb logcat -d`
- 必要的只读 `adb shell` 命令

## Expected outputs / evidence

输出应至少包括：

- 风险判定
- 需要提升到哪一级验证
- 是否需要真机证据
- 当前证据是否足够
- 若不够，还缺什么

## Stop / escalate conditions

遇到以下情况应停止并升级：

- 高风险集成改动缺少真机验证
- 需要修改设备假设
- 需要改动 Manifest 边界或产品 / backend 合同含义
- 当前变更已经超出 Android 控制入口职责
- 需要依赖最新官方 Android guidance 才能做出守门结论，但尚未查证

## Bundled resources plan

本 Skill 后续允许补充：

- 高风险路径清单
- 自动风险识别脚本
- 与验证等级联动的规则模板

本阶段优先固定守门规则，不要求立刻补自动判定脚本。

## Non-goals

- 不直接实现运行时集成功能
- 不替代人工架构审批
- 不直接代替 `android-build-verify` 或 `android-logcat-triage`
