# Task：V2 Android workspace read-only view

更新时间：2026-04-27

## 1. 任务定位

- 任务名称：V2 Android workspace read-only view
- 当前状态：`done`
- 优先级：P1

本任务在 no-DB Sales Workspace Backend API prototype 完成后，打通 Android 只读查看工作区的最小 demo 闭环。

---

## 2. 任务目标

让 Android 以 read-only 方式查看固定 prototype workspace：`ws_demo`。

展示内容：

- workspace version。
- 当前产品理解摘要。
- 当前获客方向摘要。
- top ranked candidates。
- ranking delta。
- ContextPack top candidates。
- Markdown projection 文件名。

---

## 3. 实际实现

- 新增 seed 工具：`scripts/seed_sales_workspace_demo.py`。
- 新增 Android V2 workspace client / model / parser，复用 `HttpURLConnection + org.json`。
- 新增 top-level `Workspace` 页面。
- Android 只读调用：
  - `GET /sales-workspaces/ws_demo`
  - `GET /sales-workspaces/ws_demo/ranking-board/current`
  - `GET /sales-workspaces/ws_demo/projection`
  - `POST /sales-workspaces/ws_demo/context-packs`

---

## 4. Out of Scope

- Android 提交 `WorkspacePatch`。
- Android 直接写 workspace 主存。
- Android 本地替代 backend truth。
- 新增或扩展 backend endpoint。
- DB persistence / migration。
- Runtime / LangGraph integration。
- LLM / search / CRM / ContactPoint。

---

## 5. 已做验证

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

验证结果以 handoff 为准。

结果：

- targeted backend/API tests：`14 passed`。
- seed script：成功创建 `ws_demo` 并应用三组 patch，`cand_d` 排名第一，score=`230`。
- backend ranking curl：返回 `cand_d` / `D Company` / `230`。
- Android assemble：通过；clean 后重跑 `:app:clean :app:assembleDebug` 也通过。
- Android lint：通过。
- `adb devices`：检测到设备 `f3b59f04`。
- 真机 smoke：已安装并启动 app；执行 `adb reverse tcp:8013 tcp:8013` 后，Workspace tab 可打开，并显示 `Demo sales workspace`、`FactoryOps AI`、`#1 D Company · 230 · active`。

---

## 6. 后续状态

本任务完成后仍无自动排定下一项任务。

后续如果继续推进，应由规划层单独选择：

- Android workspace 交互体验增强。
- persistence-backed API / DB schema。
- Runtime / LangGraph WorkspacePatchDraft integration。
