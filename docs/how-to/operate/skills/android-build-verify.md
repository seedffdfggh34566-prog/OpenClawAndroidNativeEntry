# Skill Spec: `android-build-verify`

更新时间：2026-04-23

## Skill name

`android-build-verify`

## Purpose

根据当前 Android 改动风险，选择最轻但足够的验证动作，并输出结构化验证摘要。

## When to trigger

适用于任何触及 `app/` 的实现任务，尤其是：

- Compose/UI 改动
- 导航改动
- 资源改动
- `AndroidManifest.xml` 改动
- 与 backend / runtime 集成相关的 Android 改动

如果存在明显高风险运行时集成改动，应先由 `android-runtime-integration-guard` 判定风险，再决定调用本 Skill。

## Required repo docs

- 根 `AGENTS.md`
- `app/AGENTS.md`
- `docs/README.md`
- 当前 task
- 对应 handoff

如果验证策略依赖最新 Android 测试、验证或工具 guidance，应先查官方
Android 文档 / Android Knowledge Base，再决定是否提升验证等级或变更验证建议。

## Allowed tools / commands

- `./gradlew :app:assembleDebug`
- `./gradlew :app:lintDebug`
- `./gradlew :app:testDebugUnitTest`
- `./gradlew :app:connectedDebugAndroidTest`
- `adb devices`

可按风险等级选择命令，不要求每次全跑。

## Expected outputs / evidence

输出应至少包括：

- 本次验证等级判断
- 实际执行的命令
- 哪些通过
- 哪些失败
- 哪些跳过
- 跳过原因
- 是否还需要更高一级验证

## Stop / escalate conditions

遇到以下情况应停止并升级：

- 需要更高风险验证但当前环境不满足
- 触及高风险运行时集成但没有真机证据
- 需要修改验证等级定义本身
- 当前 task 对验证要求与 `app/AGENTS.md` 冲突
- 需要依赖最新官方 Android guidance 才能做出验证建议，但尚未查证

## Bundled resources plan

本 Skill 后续允许补充：

- 一个低自由度执行脚本
- 一份“验证等级 -> 命令映射”参考文件

本阶段不要求实现脚本，只需把接口和输出格式固定。

## Non-goals

- 不判断业务逻辑是否正确
- 不替代代码 review
- 不代替 `android-runtime-integration-guard`
- 不自动扩展成完整 CI 流水线
