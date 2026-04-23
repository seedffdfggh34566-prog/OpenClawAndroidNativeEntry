# Skill Spec: `android-ui-change-check`

更新时间：2026-04-23

## Skill name

`android-ui-change-check`

## Purpose

对 Android UI 变更做轻量守门，要求最低合理证据，并提示是否需要进一步验证。

## When to trigger

适用于以下变化：

- Compose 页面改动
- 导航入口改动
- 资源 / 文案 / 主题改动
- 可见交互变化
- 信息组织变化

本阶段固定按 **轻量守门版** 理解，而不是 screenshot testing Skill。

## Required repo docs

- 根 `AGENTS.md`
- `app/AGENTS.md`
- `docs/architecture/clients/android-client-implementation-constraints.md`
- 当前 task

如果 UI 判断依赖最新 Compose、Navigation、screenshot testing 或其他 Android
UI guidance，应优先查官方 Android 文档 / Android Knowledge Base。

## Allowed tools / commands

- `./gradlew :app:assembleDebug`
- 必要时 `adb devices`
- 安装 / 启动命令

本阶段不依赖 screenshot infra。

## Expected outputs / evidence

输出应至少包括：

- 这次 UI 变化属于哪一类
- 最低验证要求是什么
- 当前证据是否足够
- 是否需要运行中证据
- 是否建议未来升级到 screenshot testing

## Stop / escalate conditions

遇到以下情况应停止并升级：

- 用户可见变化但没有运行中证据
- 触及高风险 UI 入口但只提供静态说明
- 需要 screenshot testing 才能继续，但仓库当前没有相应基建
- 需要依赖最新官方 Android UI guidance 才能继续判断，但尚未查证

## Bundled resources plan

本阶段只允许：

- 检查清单
- 输出模板
- 升级到未来截图测试的参考说明

本阶段不规划：

- screenshot plugin
- golden image 流程
- 截图对比脚本

## Non-goals

- 本阶段不做 golden screenshot 对比系统
- 不冒充完整 UI 自动化验证器
- 不替代 `android-build-verify`
