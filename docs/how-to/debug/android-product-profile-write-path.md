# Android ProductProfile 写路径联调

更新时间：2026-04-23

## 1. 用途

本文档用于联调 Android 控制壳层创建第一版 `ProductProfile` 草稿。

当前只覆盖：

- `POST /product-profiles`
- 创建成功后刷新 `/history`
- 创建成功后打开 `GET /product-profiles/{id}` 详情

不覆盖：

- ProductProfile 编辑或确认
- `POST /analysis-runs`
- `GET /analysis-runs/{id}` 轮询
- 真实 OpenClaw runtime 接入

---

## 2. 后端启动与设备转发

在仓库根目录启动后端：

```bash
backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
```

真机联调前执行：

```bash
adb devices
adb reverse tcp:8013 tcp:8013
```

---

## 3. Android 操作

1. 构建并安装：

```bash
./gradlew :app:assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.openclaw.android.nativeentry/.MainActivity
```

2. 在 Home 点击“开始分析”
3. 在 ProductLearning 页填写：
   - 产品名称
   - 一句话描述
   - 补充材料（可选）
4. 点击“创建 ProductProfile 草稿”
5. 确认跳转到 ProductProfile 页，并显示新建对象详情

---

## 4. 验证点

- 后端返回 `draft` 状态 ProductProfile
- `/history.latest_product_profile` 更新为新建对象
- ProductProfile 页显示真实详情，而不是占位调试数据
- 后端不可达时 ProductLearning 页展示明确失败提示

---

## 5. 当前限制

- 当前 base URL 固定为 `http://127.0.0.1:8013`
- 当前不支持编辑或确认 ProductProfile
- 当前不触发获客分析或报告生成
