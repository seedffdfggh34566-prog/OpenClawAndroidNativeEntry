# Android 真实后端读路径联调

更新时间：2026-04-23

## 1. 用途

本文档用于联调 Android 控制壳层读取 V1 最小正式后端。

当前只覆盖读路径：

- `GET /history`
- `GET /product-profiles/{id}`
- `GET /reports/{id}`

不覆盖：

- `POST /product-profiles`
- `POST /analysis-runs`
- 真实 OpenClaw runtime 接入
- 鉴权、多环境切换或生产部署

---

## 2. 后端启动

在 `jianglab` 仓库根目录运行：

```bash
backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
```

健康检查：

```bash
curl http://127.0.0.1:8013/health
curl http://127.0.0.1:8013/history
```

---

## 3. Android 设备转发

Android 端默认读取：

```text
http://127.0.0.1:8013
```

真机或模拟器联调前需要执行：

```bash
adb devices
adb reverse tcp:8013 tcp:8013
```

如果没有执行 `adb reverse`，设备上的 `127.0.0.1:8013` 会指向设备自身，而不是 `jianglab` 上的后端。

---

## 4. Android 构建与启动

构建：

```bash
./gradlew :app:assembleDebug
```

安装：

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

启动：

```bash
adb shell am start -n com.openclaw.android.nativeentry/.MainActivity
```

---

## 5. 验证点

至少检查以下状态：

1. 空库状态
   - Home / History 显示真实空态
   - 不展示占位样例数据冒充真实结果

2. 后端不可达
   - Home / History 显示连接失败
   - 页面提示检查后端启动与 `adb reverse`
   - 允许手动进入“占位/调试数据”

3. 有真实对象
   - Home / History 显示 `/history` 返回的最近对象
   - ProductProfile 页读取 `GET /product-profiles/{id}`
   - AnalysisReport 页读取 `GET /reports/{id}`
   - AnalysisResult 页只展示 `/history.latest_analysis_result` 摘要

---

## 6. 当前限制

- 详情页使用 `/history` 中的 latest id，不支持从历史列表按任意 id 打开。
- AnalysisResult 详情接口不在当前最小 contract 中，本轮不新增。
- 当前仍无鉴权与多环境配置，端口和 base URL 固定用于本地联调。
