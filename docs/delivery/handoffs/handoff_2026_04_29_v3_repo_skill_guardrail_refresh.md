# 阶段性交接：V3 repo-managed skill guardrail refresh

更新时间：2026-04-29

## 1. 本次改了什么

- 将 backend runtime/API/task/DB/contract sync skills 更新为 V3 Memory-native 口径。
- 为 Android build/runtime/logcat skills 增加 V3 scope note。
- 增强 `repo-task-bootstrap`：当前用户消息可作为授权来源，历史 V1/V2 文档不自动成为当前真相。
- 增强 `task-handoff-sync`：检查 V3 implementation、production-ready、历史 V1/V2 docs 越界表述。
- 同步本机 Codex skills。

---

## 2. 为什么这么定

- 当前主线已切到 V3，旧 V1/V2 backend/API/runtime guardrail 会限制 memory-native 方向。
- V3 需要放开 runtime cognitive memory，但正式业务对象写回仍由 backend governance 裁决。
- Android 旧控制入口风险仍存在，但 V3 不自动开放 Android 重写。

---

## 3. 本次验证了什么

1. `git diff --check`
2. 旧 V1/V2 guardrail 残留搜索
3. V3 runtime/memory/formal writeback 关键词检查
4. 本机 Codex skills 同步结果

---

## 4. 已知限制

- `backend/AGENTS.md` 仍有 V1 口径，后续应单独压缩/V3 化。
- `app/AGENTS.md` 仍保留 OpenClaw/Termux 旧控制入口风险，这符合当前历史资产状态。
- 本次未修改任何代码或启动 V3 implementation。

---

## 5. 推荐下一步

1. 单独 review `backend/AGENTS.md` 的 V3-first 改造。
2. 在 V3 runtime POC task 开放前，优先使用更新后的 `backend-runtime-boundary-guard` 和 `backend-db-risk-check`。
