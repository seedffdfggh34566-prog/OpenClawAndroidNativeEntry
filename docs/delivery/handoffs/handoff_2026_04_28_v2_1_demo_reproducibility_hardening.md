# Handoff: V2.1 Demo Reproducibility Hardening

更新时间：2026-04-28

## 1. 本次改了什么

- 创建 V2.1 implementation continuation package。
- 创建并关闭 P1 demo reproducibility hardening task。
- 更新 V2.1 product experience demo runbook，补充 reset/seed、health、chat-first smoke、Android adb reverse 和排障说明。
- 更新 `_active.md`，将当前 continuation package 衔接到 P2 Android workspace onboarding。

---

## 2. 为什么这么定

- 当前 V2.1 prototype path 已验证，但 product milestone 仍开放于规划控制下。
- P1 只强化复现路径，不改变产品能力或 backend contract。

---

## 3. 本次验证了什么

1. `git diff --check`

---

## 4. 已知限制

- 本任务未运行 backend / Android tests，因为只改 runbook 和 delivery docs。
- Postgres verification 留给 P5。
- Android workspace creation 和 message history 分别留给 P2 / P3。

---

## 5. 推荐下一步

继续 P2：实现 Android workspace creation / onboarding，复用已有 `POST /sales-workspaces`。

