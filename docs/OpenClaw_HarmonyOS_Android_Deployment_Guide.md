# OpenClaw 在鸿蒙平板上的安装配置总结与 Android 迁移流程

## 文档目的

本文基于一次真实的 **HarmonyOS 平板（HUAWEI MatePad 10.4，HarmonyOS 2.0）** 部署过程，系统总结了：

1. 如何在鸿蒙平板上完成 OpenClaw 的安装与基础配置
2. 如何将该流程抽象为可迁移到其他 Android 设备的标准安装流程
3. 如何把 OpenClaw 运行环境工程化，便于长期维护与恢复

本文不以“网页前端可直接在平板本机显示”为唯一目标，而以 **“Android 设备作为长期在线宿主机，稳定承载 OpenClaw Gateway”** 为核心思路。

---

## 一、项目结论

本次部署验证了以下结论：

- OpenClaw **可以** 在鸿蒙平板的 Termux 环境中运行。
- 平板本机浏览器存在前端兼容问题，**不适合作为主要操作界面**。
- 通过 **SSH 隧道 + 电脑浏览器 Dashboard** 可以稳定访问 OpenClaw。
- 通过 **tmux + sshd + 启动脚本**，可以将该平板转化为一个可长期维护的 OpenClaw 宿主机。
- 默认模型已切换并稳定到 **Step 3.5 Flash（阶跃星辰）**。

适合的最终使用形态是：

- **Android / HarmonyOS 设备**：作为 OpenClaw Gateway 宿主机
- **电脑**：作为 Dashboard 管理端
- **未来消息入口 / 原生入口**：再逐步接入 Telegram、QQ、飞书或自研 Android 客户端

---

## 二、本次实测设备信息

| 项目 | 值 |
|---|---|
| 设备 | HUAWEI MatePad 10.4 |
| 型号 | BAH3-W59 |
| 系统 | HarmonyOS 2.0 |
| 处理器 | Kirin 820 |
| 运行内存 | 4 GB |
| 存储 | 128 GB |
| 可用存储 | 约 107.9 GB |
| 网络方式 | WLAN |
| 局域网 IP（实测时） | 192.168.43.54 |
| Termux 用户名 | u0_a174 |

### 兼容性判断

- **硬件配置层面：可用**。该设备足够承载 Termux、Node.js、OpenClaw Gateway 与基础运维组件。
- **系统兼容层面：部分受限**。HarmonyOS 与标准 Android 并不完全等价，尤其在浏览器前端渲染、后台保活和某些 Android 行为上存在差异。

因此，本方案适合作为 **“HarmonyOS / Android 宿主化部署方案”**，但不建议把该设备的原生浏览器视为唯一主界面。

---

## 三、总体架构设计

### 推荐架构

```text
Android / HarmonyOS 设备（Termux + OpenClaw Gateway）
        ↓ 通过 SSH / 局域网维护
电脑浏览器 Dashboard（主管理界面）
        ↓ 后续再扩展
消息入口 / 原生客户端 / 节点能力
```

### 设计原则

1. **宿主稳定优先**：先确保 Gateway 长期在线
2. **前端解耦**：不把宿主机浏览器兼容性作为唯一依赖
3. **最少恢复步骤**：重启后快速恢复服务
4. **便于迁移**：流程尽量抽象为标准 Android 设备通用方案

---

## 四、在鸿蒙平板上的完整安装过程总结

### 步骤 1：确认设备基础条件

部署前确认以下条件：

- 可安装外部 APK
- 至少 4 GB RAM
- 至少 4–8 GB 可用存储
- 网络可用
- 能关闭或放宽部分电池优化限制

本次设备满足要求。

---

### 步骤 2：安装正确的 Termux

#### 实际过程中的坑

最初误装了“终端器 / SSH 客户端”一类应用，导致：

- 看到的是 SSH 连接界面
- 出现 `localhost`、用户名、端口等表单
- `pkg` 命令无法使用

这类应用 **不是** 真正的 Termux。

#### 正确做法

由于华为应用市场中搜不到标准 Termux，需要：

1. 允许安装外部 APK
2. 从可靠来源获取 Termux 安装包
3. 选择适合 Android 7+ 的版本

本次选择的是：

- `termux-app_v0.119.0-beta.3+apt-android-7-github-debug_universal.apk`

#### 安装完成的正确标志

打开后应直接进入黑色命令行界面，而不是 SSH 表单页。

---

### 步骤 3：更新软件包并安装基础运行环境

在 Termux 中执行：

```bash
pkg update
pkg upgrade -y
pkg install nodejs-lts -y
pkg install git -y
pkg install curl -y
pkg install openssh -y
pkg install tmux -y
```

#### 实测安装结果

- Node.js：`v24.14.1`
- npm：`11.12.1`
- git：可用
- curl：可用
- openssh：可用
- tmux：可用

#### 验证命令

```bash
node -v
npm -v
node -e "console.log('Node OK')"
git --version
curl --version
```

---

### 步骤 4：安装 OpenClaw CLI

执行：

```bash
npm install -g openclaw
openclaw --version
```

#### 实测结果

成功安装，版本为：

```text
OpenClaw 2026.3.24 (cff6dc9)
```

这表明 OpenClaw CLI 已经可正常调用。

---

### 步骤 5：处理 Termux 下的 HOME 路径问题

在 Android / Termux 环境中，不能像普通 Linux 那样在根目录创建 `/home`，否则会遇到：

```text
mkdir: cannot create directory '/home': Read-only file system
```

#### 正确思路

不要在根目录创建 `/home`，而应明确把当前 shell 的 `HOME` 指向 Termux 自己的家目录：

```bash
export HOME=/data/data/com.termux/files/home
```

并建议写入 `~/.bashrc`：

```bash
echo 'export HOME=/data/data/com.termux/files/home' >> ~/.bashrc
source ~/.bashrc
```

---

### 步骤 6：初始化 OpenClaw

执行：

```bash
openclaw doctor
```

#### 初始化过程中发生的关键动作

1. 生成并配置 gateway token
2. 创建 `~/.openclaw`
3. 创建 session store 目录
4. 检查配置完整性

#### 重要现象

出现了如下提示：

```text
Error: Gateway service install not supported on android
```

这不是安装失败，而是因为 Android 上 **不支持把 Gateway 安装成系统服务**。在 Android / Termux 路线里，正确做法是：

- 手动运行 Gateway
- 再通过 `tmux` 做稳定托管

---

### 步骤 7：设置 Gateway 为本地模式并启动

执行：

```bash
openclaw config set gateway.mode local
openclaw gateway --verbose
```

#### 实测关键日志

可观察到类似以下信息：

- `canvas host mounted at http://127.0.0.1:18789/...`
- `listening on ws://127.0.0.1:18789`
- `Browser control listening on http://127.0.0.1:18791`

这表明 OpenClaw Gateway 已经成功运行。

---

### 步骤 8：解决本机浏览器黑屏问题

#### 实测现象

在平板浏览器直接访问以下地址时：

- `http://127.0.0.1:18789`
- `http://127.0.0.1:18789/__openclaw__/canvas`
- `http://127.0.0.1:18791`

最初会出现：

```json
{"error":{"message":"Unauthorized","type":"unauthorized"}}
```

这是因为缺少 token。

随后通过：

```bash
openclaw dashboard
```

拿到了带 token 的 Dashboard URL，例如：

```text
http://127.0.0.1:18789/#token=...
```

但在平板浏览器中仍表现为 **黑屏**。

#### 结论

- 后端正常
- token 认证正常
- **平板浏览器前端渲染存在兼容性问题**

因此，最终采用：

- **平板：只负责运行 Gateway**
- **电脑：通过 SSH 隧道访问 Dashboard**

---

### 步骤 9：在电脑上通过 SSH 隧道访问 Dashboard

#### 1）在平板上启动 SSH 服务

```bash
sshd
whoami
```

本次实测用户名为：

```text
u0_a174
```

#### 2）获取平板局域网 IP

安装网络工具：

```bash
pkg install iproute2 -y
ip addr show wlan0
```

实测 IP 为：

```text
192.168.43.54
```

#### 3）设置密码

```bash
passwd
```

#### 4）在电脑上建立 SSH 隧道

```bash
ssh -p 8022 -N -L 18789:127.0.0.1:18789 u0_a174@192.168.43.54
```

#### 5）在电脑浏览器访问 Dashboard

使用 `openclaw dashboard` 输出的完整链接：

```text
http://127.0.0.1:18789/#token=...
```

#### 最终结果

电脑浏览器成功打开 OpenClaw 对话界面。

这一步证明：

- OpenClaw 后端完全可用
- 平板宿主方案成立
- 平板浏览器仅是前端兼容问题，不影响宿主方案

---

### 步骤 10：切换模型到 Step 3.5 Flash

原始默认模型曾指向 Anthropic，测试对话时提示缺少 API key。

后续改为接入 **阶跃星辰 Step 3.5 Flash**。

#### 配置方式

通过 OpenClaw onboarding / 自定义 provider，设置为：

- Endpoint compatibility：`OpenAI-compatible`
- Model ID：`step-3.5-flash`
- Base URL：`https://api.stepfun.com/step_plan/v1`

后续确认：

- `Step 3.5 Flash` 已成为稳定默认模型
- 电脑 Dashboard 可正常对话

#### 关键策略

在 onboarding 过程中，凡是与当前核心目标无关的额外 skill / 第三方 API key 问题，均优先：

- **Skip for now**
- 或选 **No**

从而优先跑通最小闭环。

---

## 五、工程化改造：把平板变成可维护宿主机

为了让该系统具备长期可用性，需要把运行环境工程化。

### 1. 使用 tmux 托管 Gateway

启动 tmux：

```bash
tmux
```

在 tmux 中启动 OpenClaw：

```bash
openclaw gateway --verbose
```

#### 常用 tmux 操作

| 功能 | 操作 |
|---|---|
| 新建窗口 | `Ctrl+b` 后按 `c` |
| 下一个窗口 | `Ctrl+b` 后按 `n` |
| 上一个窗口 | `Ctrl+b` 后按 `p` |
| 安全脱离 | `Ctrl+b` 后按 `d` |
| 重新进入 | `tmux attach` |

> 注意：跑着 Gateway 的 tmux 窗口不要直接 `exit`，否则会结束进程。应使用 `Ctrl+b` 然后按 `d` 脱离。

---

### 2. 创建脚本目录

```bash
mkdir -p ~/bin
```

---

### 3. 启动 OpenClaw 的脚本：`start-openclaw`

文件路径：

```text
~/bin/start-openclaw
```

内容：

```bash
#!/data/data/com.termux/files/usr/bin/bash

export HOME=/data/data/com.termux/files/home

SESSION="openclaw"

if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  tmux new-session -d -s "$SESSION" "openclaw gateway --verbose"
fi

echo "OpenClaw tmux session: $SESSION"
echo "Attach with: tmux attach -t $SESSION"
```

赋予权限：

```bash
chmod +x ~/bin/start-openclaw
```

---

### 4. 进入 Gateway 会话的脚本：`openclaw-attach`

文件路径：

```text
~/bin/openclaw-attach
```

内容：

```bash
#!/data/data/com.termux/files/usr/bin/bash
tmux attach -t openclaw
```

赋予权限：

```bash
chmod +x ~/bin/openclaw-attach
```

---

### 5. 启动 sshd 的脚本：`start-sshd`

文件路径：

```text
~/bin/start-sshd
```

内容：

```bash
#!/data/data/com.termux/files/usr/bin/bash
sshd
echo "sshd started on port 8022"
```

赋予权限：

```bash
chmod +x ~/bin/start-sshd
```

---

### 6. 总启动脚本：`boot-openclaw`

文件路径：

```text
~/bin/boot-openclaw
```

内容：

```bash
#!/data/data/com.termux/files/usr/bin/bash

export HOME=/data/data/com.termux/files/home

sshd >/dev/null 2>&1
start-openclaw

echo "Boot done."
echo "Use 'openclaw-attach' to view gateway."
```

赋予权限：

```bash
chmod +x ~/bin/boot-openclaw
```

---

### 7. 配置 PATH

为了直接调用上述脚本，把 `~/bin` 加入 PATH：

```bash
echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc
echo 'export HOME=/data/data/com.termux/files/home' >> ~/.bashrc
source ~/.bashrc
```

之后可以直接使用：

```bash
start-openclaw
openclaw-attach
start-sshd
boot-openclaw
```

---

## 六、日常使用与恢复流程

### 平板重启后的最简恢复流程

在平板上打开 Termux，执行：

```bash
boot-openclaw
```

然后在电脑上执行：

```bash
ssh -p 8022 -N -L 18789:127.0.0.1:18789 用户名@平板IP
```

浏览器再打开 Dashboard 地址即可。

### 推荐恢复 SOP

#### 平板端

```bash
boot-openclaw
```

#### 电脑端

```bash
ssh -p 8022 -N -L 18789:127.0.0.1:18789 u0_a174@192.168.43.54
```

然后访问：

```text
http://127.0.0.1:18789/#token=...
```

### 每次启动后的快速检查

1. `openclaw-attach` 能否看到 Gateway 正常运行
2. 电脑 Dashboard 能否打开
3. 发送一条 `hello` 测试能否正常回复

---

## 七、可迁移到其他 Android 设备的标准安装流程

以下流程适用于大多数 Android / HarmonyOS 设备。

### A. 前提条件

- Android 7+ 或兼容层
- 至少 4 GB RAM（建议 6 GB+）
- 至少 4 GB 可用存储（建议 8 GB+）
- 可安装外部 APK
- 可联网
- 最好可关闭部分电池优化

---

### B. 标准安装步骤

#### 第 1 步：安装标准 Termux

- 不要安装 SSH 客户端、Terminal Emulator、终端器之类替代品
- 需要安装真正的 Termux
- 优先选 Android 7+ 的 universal 版本

#### 第 2 步：基础环境安装

```bash
pkg update
pkg upgrade -y
pkg install nodejs-lts -y
pkg install git -y
pkg install curl -y
pkg install openssh -y
pkg install tmux -y
pkg install iproute2 -y
```

#### 第 3 步：修正 HOME

```bash
echo 'export HOME=/data/data/com.termux/files/home' >> ~/.bashrc
source ~/.bashrc
```

#### 第 4 步：安装 OpenClaw

```bash
npm install -g openclaw
openclaw --version
```

#### 第 5 步：初始化

```bash
openclaw doctor
openclaw config set gateway.mode local
```

- Android 上看到 “Gateway service install not supported on android” 属正常
- 不需要强行把它当系统服务安装

#### 第 6 步：启动 Gateway

```bash
openclaw gateway --verbose
```

#### 第 7 步：配置模型

推荐采用 **OpenAI-compatible** provider，便于接入更多服务。

例如接入 Step 3.5 Flash：

- Base URL：`https://api.stepfun.com/step_plan/v1`
- Model：`step-3.5-flash`

#### 第 8 步：建立运维能力

- 启用 `sshd`
- 设置密码：`passwd`
- 使用 `tmux` 托管 Gateway
- 建立 `start-openclaw`、`start-sshd`、`boot-openclaw`

---

### C. Android 设备迁移时要特别注意的变量

| 项目 | 是否变化 | 说明 |
|---|---|---|
| Termux 用户名 | 会变化 | 每台设备的 `whoami` 结果可能不同 |
| 局域网 IP | 会变化 | 每次网络环境变化可能变化 |
| 浏览器兼容性 | 可能变化 | 有些 Android 浏览器能正常显示，有些会黑屏 |
| ssh 端口 | 通常不变 | Termux 默认 8022 |
| HOME 路径 | 通常不变 | 一般仍为 `/data/data/com.termux/files/home` |
| 启动脚本 | 基本可复用 | 只需确保路径一致 |

---

## 八、常见问题与解决思路

### 1. 打开后是 SSH 登录页，不是命令行
**原因**：装错了应用，装成了 SSH 客户端或终端器。  
**解决**：重新安装真正的 Termux。

### 2. `pkg` 命令不可用
**原因**：不是真正的 Termux，或者环境损坏。  
**解决**：重新安装标准 Termux。

### 3. 不能创建 `/home`
**原因**：Android 根目录只读。  
**解决**：不要创建 `/home`，改为设置 `HOME=/data/data/com.termux/files/home`。

### 4. `Gateway service install not supported on android`
**原因**：Android 不支持将 Gateway 安装成系统服务。  
**解决**：使用 `tmux` 手动托管 Gateway。

### 5. 浏览器显示 `Unauthorized`
**原因**：访问地址没有带 token。  
**解决**：使用 `openclaw dashboard` 生成带 token 的完整地址。

### 6. 浏览器带 token 后黑屏
**原因**：浏览器前端兼容问题。  
**解决**：改用电脑浏览器通过 SSH 隧道访问；不要把宿主机浏览器作为唯一依赖。

### 7. 聊天时报缺少 Anthropic / 其他 provider 的 API key
**原因**：默认模型指向了对应 provider，但未配置密钥。  
**解决**：切换到正确的 provider，或补齐 API key。

### 8. `chmod` 提示 No such file or directory
**原因**：脚本还没创建，或文件名写错。  
**解决**：先确认文件已通过 `nano` 保存，再执行 `chmod +x`。

### 9. 不知道怎么从 tmux 里退出
**正确方式**：

- 安全脱离：`Ctrl+b` 后按 `d`
- 重新进入：`tmux attach`

---

## 九、当前建议的产品化方向

在当前阶段，更合适的定位不是“平板本机网页聊天器”，而是：

**一台长期在线的 Android / HarmonyOS 宿主机 + 外部操作入口。**

### 短期建议

- 保持平板作为 Gateway 宿主
- 电脑作为主运维和调试端
- Step 3.5 Flash 作为默认模型
- 用 `boot-openclaw` 固化恢复流程

### 中期建议

- 接入 Telegram、QQ、飞书等消息入口
- 把高频交互入口从网页迁移到消息或原生客户端

### 长期建议

- 逐步接入设备上下文、通知、位置、联系人、日程等能力
- 建立用户画像与长期记忆系统
- 最终形成“最了解手机主人的数字分身”

---

## 十、结论

本次部署的最大价值，不在于“网页是否能在平板本机显示”，而在于完成了以下验证：

1. **OpenClaw 可以在 HarmonyOS 平板的 Termux 环境中作为宿主运行**
2. **通过 SSH 隧道，电脑端可以稳定访问 Dashboard**
3. **通过 tmux、sshd 与启动脚本，可以把设备工程化为一个可维护宿主机**
4. **Step 3.5 Flash 已可作为稳定默认模型工作**

因此，这套方案已经具备迁移到其他 Android 设备的可行性，并可作为后续构建“随身数字分身系统”的基础设施模板。
