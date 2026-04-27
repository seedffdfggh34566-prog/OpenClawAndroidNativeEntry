# Handoff：V2 Android workspace read-only demo

- 日期：2026-04-27
- 状态：done
- 对应任务：`docs/delivery/tasks/task_v2_android_workspace_readonly_view.md`

---

## 1. 本次变更

打通 Android 只读查看 Sales Workspace 的最小 demo 闭环：

- 新增 `scripts/seed_sales_workspace_demo.py`，通过现有 API examples seed `ws_demo`。
- 新增 Android Sales Workspace read-only client / parser / model。
- 新增 top-level `Workspace` 页面。
- Android 展示 workspace、ranking、ranking delta、ContextPack 和 projection 文件名。
- 更新 `_active.md`、`docs/README.md`、`docs/delivery/README.md`。

---

## 2. 仍未开放范围

- Android 不提交 `WorkspacePatch`。
- Android 不写 workspace 主存。
- 不新增 backend endpoint。
- 不做 DB persistence / migration。
- 不接 Runtime / LangGraph。
- 不接 LLM / search / CRM / ContactPoint。

---

## 3. 验证

已执行：

```bash
backend/.venv/bin/python -m pytest backend/tests/sales_workspace backend/tests/test_sales_workspace_api.py -q
OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_sales_workspace_android_demo.db backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
python3 scripts/seed_sales_workspace_demo.py --base-url http://127.0.0.1:8013 --workspace-id ws_demo
curl http://127.0.0.1:8013/sales-workspaces/ws_demo/ranking-board/current
./gradlew :app:assembleDebug
./gradlew :app:lintDebug
adb devices
git diff --check
git status --short
```

结果：

- targeted backend/API tests：`14 passed`。
- seed script：成功创建 `ws_demo` 并应用三组 patch，`cand_d` 排名第一，score=`230`。
- backend ranking curl：返回 `cand_d` / `D Company` / `230`。
- Android assemble：通过；clean 后重跑 `:app:clean :app:assembleDebug` 也通过。
- Android lint：通过。
- `adb devices`：检测到设备 `f3b59f04`。
- 真机 smoke：已安装并启动 app；执行 `adb reverse tcp:8013 tcp:8013` 后，Workspace tab 可打开，并显示 `Demo sales workspace`、`FactoryOps AI`、`#1 D Company · 230 · active`。

---

## 4. 建议下一步

不要自动继续扩展 Android 或 backend。

建议规划层决定下一步优先级：

- 继续增强 Android workspace read-only 体验。
- 决策 persistence-backed API / DB schema。
- 开始 Runtime / LangGraph WorkspacePatchDraft integration。
