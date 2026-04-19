# OpenClaw Android Native Entry 阶段性开发交接文档

## 1. 项目概述

### 项目名称

OpenClaw Android Native Entry

### 项目目标

本项目不是重写 OpenClaw，也不是把 OpenClaw 宿主环境嵌入 APK，而是为已经在 Termux 中可运行的 OpenClaw 宿主链路提供一个 Android 原生入口 App。  
目标是把“手动进入 Termux / 浏览器 / tmux 维护”的使用方式，逐步收敛为一个更稳定、可操作、可诊断的原生控制入口。

### 当前阶段目标

当前阶段的重点不是做完整聊天客户端，而是先完成以下最小闭环：

- Android App 能在真机安装、启动、运行
- App 能检测本机 OpenClaw Gateway 状态
- App 能真实调用 Termux 执行 `boot-openclaw`
- App 能显示启动诊断和状态诊断
- App 能尝试进入聊天入口，并把失败原因定位到具体层次

### 当前项目定位

当前项目最准确的定位是：

- 安卓原生入口
- 本机 OpenClaw 控制面板
- 聊天入口实验能力

其中“聊天入口”目前仍属于实验能力，不应被视为稳定产品功能。

---

## 2. 当前架构

### Android App 侧组成

当前 App 采用 `Kotlin + Jetpack Compose`，主要由以下部分组成：

- `Home` 页：状态展示、启动按钮、进入聊天按钮
- `Logs` 页：状态检测、启动链路、tmux 检测等诊断信息
- `Settings` 页：当前为轻量占位页
- `Chat` 页：辅助 route，不在底部主导航中，用于承载受控 WebView 与调试信息

关键代码位置：

- `app/src/main/java/com/openclaw/android/nativeentry/ui/OpenClawApp.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/navigation/OpenClawNavHost.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/home/*`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/logs/LogsScreen.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/chat/OpenClawChatScreen.kt`

### Termux / tmux / OpenClaw 宿主组成

宿主侧不在 App 内，而在设备本机 Termux 环境中，当前依赖关系为：

- Termux
- `tmux`
- OpenClaw CLI / Gateway
- 启动脚本：
  - `~/bin/start-openclaw`
  - `~/bin/start-sshd`
  - `~/bin/boot-openclaw`

运行模式是：

- OpenClaw Gateway 运行在 Termux 中
- `tmux` 会话名为 `openclaw`
- Gateway 本机监听 `http://127.0.0.1:18789`

### Android App 与 Termux / OpenClaw 的交互关系

当前 App 与宿主的交互不是复杂 IPC，而是两条最小链路：

1. 状态检测链路  
   App 直接访问本机 `http://127.0.0.1:18789`

2. 宿主命令调用链路  
   App 通过 Termux `RUN_COMMAND` Intent 触发：
   - `boot-openclaw`
   - `tmux has-session -t openclaw`
   - `openclaw dashboard`

关键代码位置：

- `app/src/main/java/com/openclaw/android/nativeentry/termux/TermuxCommandBridge.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/termux/TermuxCommandResultReceiver.kt`

### 三条核心链路

#### Gateway 检测链路

- App 启动时自动检测一次
- App 回到前台时自动重检
- 用户可手动点击重新检测
- 目标地址固定为 `http://127.0.0.1:18789`
- 至少区分：
  - 检测中
  - 已连接 / 运行中
  - 无法连接
  - 检测失败

#### 启动链路

- 首页点击 `启动 OpenClaw`
- App 通过 Termux `RUN_COMMAND` 调用 `boot-openclaw`
- 启动后先检查 `tmux has-session -t openclaw`
- 若 `tmux` 已建立，再继续轮询 `127.0.0.1:18789`
- 轮询成功则进入“已连接 / 运行中”
- 轮询超时或 `tmux` 未建立则在 Logs 页显示明确诊断

#### 聊天入口链路

- 首页点击 `进入聊天`
- 先检查 Gateway 是否在线
- 在线后通过 Termux 执行 `openclaw dashboard`
- 从输出中提取带 token 的 Dashboard URL
- Chat 页用受控 WebView 加载该 URL
- WebView 只允许加载本机 Dashboard 地址
- 当前已能进入 WebView 承载阶段，但聊天前端在目标设备上存在兼容性问题

---

## 3. 本阶段已完成内容

### Android Studio 工程初始化

已完成可被 Android Studio 正常识别的 Android 工程初始化，并修复过一轮主题与依赖配置问题，使项目能够作为纯 Jetpack Compose 工程构建运行。  
这一步的结果是：项目已经具备稳定的 IDE 打开、编译、安装基础，不再停留在概念仓库状态。

### 真机部署与调试

已在真实 HarmonyOS 平板设备上完成：

- Android Studio / ADB 连接
- APK 安装
- App 启动
- UI 层级抓取
- 真机交互验证

这意味着后续工作不是“理论可行”，而是已经建立在真实设备闭环之上。

### Gateway 状态检测

已完成首页与共享状态层的本机 Gateway 检测能力：

- 地址固定为 `127.0.0.1:18789`
- App 启动自动检测
- App `onResume` 自动重检
- 手动刷新可重复发起新请求
- 首页与 Logs 页共享同一份检测结果

这一步的意义是：App 已经从静态壳子变成了一个可观测的本地控制入口。

### 启动 OpenClaw 按钮真实接入

`启动 OpenClaw` 按钮已经不再是占位，而是完成真实接入：

- 使用 Termux `RUN_COMMAND`
- 通过 `bash -lc` 调用
- 显式设置 `HOME` 和 `PATH`
- 启动日志落地到固定日志文件
- 启动后先检查 `tmux` 会话，再检查 Gateway

这一步的价值在于：App 已经具备真实控制宿主的能力，而不只是“展示状态”。

### Logs 页诊断能力

Logs 页已经能展示最小但实用的诊断信息，包括：

- 最近一次检测时间
- 检测地址
- 当前检测状态
- 最近一次启动尝试时间
- RUN_COMMAND 是否发起成功
- 外部启动日志路径
- 脚本退出码
- `tmux` 会话检测结果
- 最终连接结果

这使得后续维护者在不打开 Android Studio 的情况下，也能通过 App 直接看到大量有效状态。

### 聊天入口 / WebView 实验

聊天入口已从占位状态推进到可执行实验阶段：

- 点击进入聊天后先做 Gateway 在线检查
- 在线后再请求 Dashboard URL
- 能获取带 token 的本机 Dashboard 地址
- 能进入独立 Chat 页
- 能进入 WebView 承载阶段

这一步已经证明：聊天入口链路在“地址获取”和“页面承载”层面是成立的，问题不在启动链路和 token 获取链路。

### 兼容性诊断能力

聊天页已加入最小但有效的诊断能力：

- 打码显示 Dashboard URL
- WebView 页面加载进度
- 页面标题
- 最近 `onPageStarted` / `onPageFinished` / `onPageCommitVisible`
- 最近资源错误 / HTTP 错误
- 最近 console 信息
- DOM 探针结果
- render process 信息
- WebView / Chromium 版本

阶段性结论已收口为：

> 当前目标设备上的 HarmonyOS / WebView 环境与 OpenClaw Dashboard 前端 bundle 存在兼容性问题，导致主文档加载成功但前端 JS 在该环境中发生致命语法错误，最终页面无法正常渲染。

---

## 4. 已验证通过的链路

以下内容已经在真机实测通过：

- App 可正常安装并启动
- 真机可通过 ADB 与 Android Studio 识别
- 首页可正确检测 Gateway 在线 / 离线
- App 回到前台会自动重检 Gateway
- 手动“重新检测”可正常工作
- 点击 `启动 OpenClaw` 能真实调用 Termux
- 启动后能检测到 `openclaw` tmux 会话
- 启动后能轮询到 Gateway 在线
- Logs 页能显示状态检测、启动尝试、tmux 检测与最终结果
- 点击 `进入聊天` 后能获取 Dashboard URL
- Chat 页能进入 WebView 承载阶段
- 自测 HTML 页能在 WebView 中正常渲染
- Dashboard 主文档可成功加载，标题为 `OpenClaw Control`

需要特别说明：

- “聊天页可进入 WebView 承载阶段”已验证通过
- “聊天页内容可稳定正常渲染”未通过，已定位为兼容性问题

---

## 5. 当前已知问题与限制

### 1. HarmonyOS 设备 WebView 与 OpenClaw Dashboard 前端 bundle 的兼容性问题

这是当前最重要的已知限制，且已基本定位，不应继续写成“未知问题”。

已经观察到：

- Dashboard URL 获取成功
- WebView 自测页通过
- 主文档成功加载
- `readyState=complete`
- 标题为 `OpenClaw Control`
- 但 console 出现致命 JS 错误：
  - `Uncaught SyntaxError: Unexpected token '{'`
- 最终前端未正常渲染

因此可以明确判断：

> 当前问题不是 Gateway 未启动，不是 token 未获取，不是网络错误，也不是 WebView 完全不可用，而是目标设备 WebView / HarmonyOS 对 Dashboard 前端 bundle 的 JS 语法或打包产物兼容性不足。

### 2. 当前聊天页不能作为稳定功能

原因不是入口没打通，而是“最后一公里渲染”不稳定。  
因此当前聊天页仍应被视为：

- 实验能力
- 诊断入口
- 兼容性验证入口

不应视为稳定聊天功能。

### 3. 已经排除的问题

以下方向已经被当前阶段排除：

- Gateway 地址获取失败
- token 未生成
- WebView 自身完全不可用
- 页面主文档未加载
- 页面标题未拿到
- App 无法进入聊天页
- `启动 OpenClaw` 按钮无效
- Termux `RUN_COMMAND` 权限问题

### 4. 仍未解决的问题

- 当前设备上 Dashboard 前端 bundle 的 JS 兼容性问题
- 当前设备上聊天页内容区稳定渲染问题
- 是否存在前端构建目标、语法降级或 polyfill 级别的解决方式

---

## 6. 关键配置与依赖条件

### Android 侧权限

Manifest 中当前关键权限与配置：

- `android.permission.INTERNET`
- `com.termux.permission.RUN_COMMAND`
- `queries` 中包含 `com.termux`
- `usesCleartextTraffic=true`

### Termux 侧配置

必须具备以下条件：

- 已安装标准 Termux
- 已安装 `tmux`
- 已安装 OpenClaw CLI
- `HOME` 应为 `/data/data/com.termux/files/home`
- `PATH` 需包含 `~/bin`

### `allow-external-apps`

Termux 需开启：

```properties
allow-external-apps=true
```

修改后需要重启 Termux。

### RUN_COMMAND 权限

系统侧必须给本 App 授予 Termux 运行命令权限，否则启动链路无法工作。

### `~/bin` 中的关键脚本

当前依赖以下脚本存在且可执行：

- `~/bin/start-openclaw`
- `~/bin/start-sshd`
- `~/bin/boot-openclaw`

### OpenClaw / tmux / boot-openclaw 的依赖关系

当前推荐关系为：

- `boot-openclaw`
  - 启动 `sshd`
  - 调 `start-openclaw`
- `start-openclaw`
  - 确保 `tmux` 会话 `openclaw` 存在
  - 在该会话中拉起 OpenClaw Gateway

App 本身不直接控制 OpenClaw 进程，而是通过这些脚本触发宿主侧动作。

---

## 7. 运维与排查指南

### 如何手动启动 OpenClaw

在 Termux 中执行：

```bash
boot-openclaw
```

### 如何手动停止 OpenClaw

当前 App 未提供停止按钮。  
建议在 Termux 中手动处理：

```bash
tmux kill-session -t openclaw
```

说明：这属于宿主侧运维操作，不是当前 App 功能的一部分。

### 如何查看 tmux 会话

```bash
tmux ls
tmux has-session -t openclaw
tmux attach -t openclaw
```

### 如何验证 Gateway 是否在线

可在 Termux 中执行：

```bash
curl -I http://127.0.0.1:18789
```

或直接在 App 首页查看状态。

### 如何从 App 内查看状态

- 首页：当前 Gateway 状态、最近更新时间、启动与进入聊天入口
- Logs 页：检测与启动链路诊断

### 如何查看 Logs 页

在底部导航进入 `Logs`，可查看：

- 最近检测时间
- 检测地址
- 成功/失败状态
- 启动动作是否成功发起
- 脚本退出码
- tmux 检测结果
- 最终连接结果

### 如何查看 Termux 启动日志

最重要的日志文件：

```bash
~/openclaw-runcommand.log
```

常用查看方式：

```bash
tail -n 100 ~/openclaw-runcommand.log
cat ~/openclaw-runcommand.log
```

### 常用命令清单

```bash
boot-openclaw
start-openclaw
start-sshd
tmux ls
tmux has-session -t openclaw
tmux attach -t openclaw
tmux kill-session -t openclaw
curl -I http://127.0.0.1:18789
openclaw dashboard
tail -n 100 ~/openclaw-runcommand.log
```

---

## 8. 关键日志与诊断入口

### App 中哪里看状态

- 首页：看 Gateway 在线状态与最近更新时间
- Logs 页：看检测链路与启动链路的诊断信息
- Chat 页：看 WebView / Dashboard 兼容性诊断信息

### Logs 页能看到什么

- 最近一次检测时间
- 检测地址
- 检测结果
- 最近一次启动尝试
- 启动是否成功发起
- 启动发起说明
- 外部启动日志路径
- 脚本退出码
- tmux 会话检测
- 轮询状态
- 最终连接结果
- 启动诊断说明

### Termux 哪个日志文件最重要

最重要的是：

```text
/data/data/com.termux/files/home/openclaw-runcommand.log
```

即：

```bash
~/openclaw-runcommand.log
```

### 启动失败时先看哪里

优先顺序建议：

1. App 首页是否仍显示离线
2. App `Logs` 页中的：
   - 启动动作发起
   - tmux 会话检测
   - 脚本退出码
3. Termux 中的 `~/openclaw-runcommand.log`
4. `tmux ls`
5. `curl -I http://127.0.0.1:18789`

### 聊天页兼容性问题时看哪些调试字段

Chat 页当前关键调试字段包括：

- 当前状态
- WebView 版本
- Dashboard 地址（打码）
- 页面进度
- 页面标题
- 自测页结果
- 最近 `onPageStarted`
- 最近 `onPageFinished`
- 最近可视提交
- 最近资源错误
- 最近 HTTP 错误
- 最近 render process
- DOM 探针
- 最近 console

当前对兼容性问题最关键的字段通常是：

- `当前状态`
- `页面标题`
- `自测页结果`
- `DOM 探针`
- `最近 console`
- `WebView 版本`

---

## 9. 本阶段经验总结

### 哪些方案有效

#### 1. 先做控制入口，而不是先做聊天前端

这是正确路径。  
先把 Gateway 状态检测、Termux 启动、Logs 诊断打通，能快速建立可运维基础；否则一开始就做聊天页，问题会混在“宿主未启动”“入口不可用”“前端黑屏”里，无法定位。

#### 2. 使用 Termux RUN_COMMAND 是当前最合适的最小方案

相比复杂 IPC、前台服务、宿主重构，`RUN_COMMAND` 足够小、足够直接，也已经在真机上证明可行。

#### 3. 启动后先查 tmux，再查 Gateway，非常重要

如果只轮询 `127.0.0.1:18789`，会出现“盲等但不知道失败在哪”的情况。  
加上 `tmux has-session -t openclaw` 后，启动链路可以被切成：

- 命令是否发起
- 脚本是否执行
- tmux 是否建立
- Gateway 是否上线

这是本阶段最有效的诊断增强之一。

#### 4. 启动日志落地到固定文件非常有价值

`~/openclaw-runcommand.log` 是把 App 侧动作与宿主侧行为连接起来的关键诊断点。  
没有它，很多问题只能猜。

### 哪些方向被证明不可行或暂不适合

#### 1. 把当前聊天页当稳定功能推进

这条路现在不适合继续投入大量时间，因为当前设备上的问题已经定位到 WebView / HarmonyOS 与 Dashboard 前端 bundle 的兼容性层，不是 App 侧几个小配置就能解决的。

#### 2. 继续盲目试探 WebView 小配置

当前已经证明：

- URL 成功
- token 成功
- 主文档成功
- WebView 自测页成功
- 但 bundle JS 语法报错

所以再继续试探式改 `WebView` 小开关，收益很低。

### 为什么状态检测要先于聊天入口

因为状态检测是整个项目的基础能力：

- 它决定了 App 是否能知道宿主在线状态
- 它是启动成功与否的判定依据
- 它给 Logs 页和 Chat 页提供了前置条件
- 它让问题能先在“宿主层”收口，再进入“前端层”

没有状态检测，聊天入口的所有问题都会失去上下文。

### 为什么当前更适合把 App 定位为“原生控制入口”

因为在当前 HarmonyOS / WebView 现实条件下，最稳定、最有价值的能力是：

- 看状态
- 启动宿主
- 看日志
- 做本机控制

而不是强行把所有聊天前端能力都塞进当前 WebView。

### HarmonyOS / WebView / Termux 集成上的具体经验

- HarmonyOS 设备上，Termux 宿主链路是可行的
- `tmux + boot-openclaw + Gateway` 这条链路已在真机验证可用
- Android 原生入口与 Termux `RUN_COMMAND` 的集成是可行的
- 设备浏览器与嵌入式 WebView 对同一个 Dashboard 前端都可能出现兼容性问题
- 因此“宿主可行”与“前端可用”必须分开判断，不能混为一谈

---

## 10. 下一阶段建议

### P0

- 保持 App 的核心定位为“原生控制入口”
- 继续稳定状态检测、启动、日志、诊断链路
- 如果要继续处理聊天入口，优先从前端 bundle 兼容性角度排查，而不是继续试探 WebView 开关
- 对聊天页兼容性失败给出更明确的产品提示，避免用户误以为是启动失败

### P1

- 增加宿主控制能力，但保持最小增量
  - 停止 OpenClaw
  - 查看 tmux 状态
  - 一键打开关键日志
- 对 Logs 页做结构化整理，提升运维可读性
- 评估是否需要在 App 中加入“复制诊断摘要”到更多页面

### P2

- 评估聊天能力的替代方案
  - 原生最小消息入口
  - 轻量协议桥接
  - 替代前端壳层
- 评估是否引入前台服务、通知、常驻保活等更重能力

### 明确不建议继续浪费时间的方向

- 不建议继续在当前阶段大幅重构启动架构
- 不建议继续为 WebView 黑屏做大量无方向的小配置试错
- 不建议把当前聊天页包装成稳定功能对外承诺
- 不建议现在就进入完整原生聊天协议重写

---

## 11. 建议的文档附录

### 常用命令

```bash
boot-openclaw
start-openclaw
start-sshd
tmux ls
tmux has-session -t openclaw
tmux attach -t openclaw
tmux kill-session -t openclaw
curl -I http://127.0.0.1:18789
openclaw dashboard
tail -n 100 ~/openclaw-runcommand.log
```

### 关键路径

```text
Gateway: http://127.0.0.1:18789
Browser control: http://127.0.0.1:18791
Termux HOME: /data/data/com.termux/files/home
启动日志: /data/data/com.termux/files/home/openclaw-runcommand.log
脚本目录: /data/data/com.termux/files/home/bin
```

### 关键文件

```text
app/src/main/java/com/openclaw/android/nativeentry/ui/OpenClawApp.kt
app/src/main/java/com/openclaw/android/nativeentry/navigation/OpenClawNavHost.kt
app/src/main/java/com/openclaw/android/nativeentry/ui/home/GatewayStatus.kt
app/src/main/java/com/openclaw/android/nativeentry/ui/logs/LogsScreen.kt
app/src/main/java/com/openclaw/android/nativeentry/ui/chat/OpenClawChatScreen.kt
app/src/main/java/com/openclaw/android/nativeentry/termux/TermuxCommandBridge.kt
app/src/main/java/com/openclaw/android/nativeentry/termux/TermuxCommandResultReceiver.kt
app/src/main/AndroidManifest.xml
docs/OpenClaw_HarmonyOS_Android_Deployment_Guide.md
README.md
```

### 重要注意事项

- 当前聊天页黑屏不是“未知问题”，而是已定位到设备 WebView / HarmonyOS 与 Dashboard 前端 bundle 的兼容性问题
- 当前聊天页仍是实验入口，不是稳定产品能力
- 当前最稳定、最有价值的成果是“原生控制入口”能力，而不是“原生聊天能力”
- 后续接手时，应优先维护宿主可用性与诊断能力，不应一开始就冲动重构整个架构

---

## 建议的文件命名与存放位置

建议文件名：

```text
OpenClaw_Android_Native_Entry_Phase_Report.md
```

建议放置位置：

```text
docs/OpenClaw_Android_Native_Entry_Phase_Report.md
```

原因：

- 与部署文档、阶段性技术资料归档在同一目录，便于后续维护者查找
- 不污染仓库根目录
- 符合“开发文档 / 运维文档 / 阶段交接文档”集中管理的方式
