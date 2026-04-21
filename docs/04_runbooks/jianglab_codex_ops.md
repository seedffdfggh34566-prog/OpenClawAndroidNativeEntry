# jianglab + Codex 运维与工作区说明

更新时间：2026-04-20

## 1. 文档定位

本文档用于记录当前项目在 `jianglab` 主机上的工作区、Codex 远程连接方式、Git/GitHub 使用方式，以及日常运维与排查要点。

本文档的主要读者包括：

- 开发者本人
- 后续 AI 运维 / AI 接手者
- 未来需要在同一仓库上继续推进的人

本文档不是产品文档，也不是 PRD。  
本文档只回答：

- 当前唯一工作区在哪里
- Codex app 如何连接和使用
- FinalShell 在哪里介入
- Git 和 GitHub 当前怎么工作
- 出现问题先查哪里

---

## 2. 当前工作区与工具角色

## 2.1 唯一权威工作区

当前唯一权威工作区为：

```text
jianglab:/home/yulin/projects/OpenClawAndroidNativeEntry
```

所有正式代码、文档、任务和 Git 操作，都以该仓库为准。

不维护 Windows 本地的第二份主工作副本。

---

## 2.2 当前工具角色分工

### Codex app
作为**主控制台**，主要负责：

- 远程连接 `jianglab`
- 开发线程 / 切换线程
- 执行明确 task
- 读取并遵循仓库文档
- 进行 agent 开发与 review

### FinalShell
作为**辅助终端与运维入口**，主要负责：

- SSH 登录 `jianglab`
- 文件上传 / 下载
- Git 基础命令
- 系统命令执行
- 网络、磁盘、SSH、环境排查

### jianglab
作为**唯一真实工作区和执行主机**，负责：

- Git 仓库主工作区
- Android 构建环境
- `adb` 与真机链路
- Codex 远程执行环境
- GitHub 推送主机

---

## 3. 当前基础链路

当前工作链路为：

```text
Codex app (Windows)
    ↓ SSH remote project
jianglab
    ↓ Git / docs / Android build / adb
OpenClawAndroidNativeEntry
    ↓ SSH push
GitHub
```

辅助链路为：

```text
FinalShell (Windows)
    ↓ SSH
jianglab
```

---

## 4. 当前 Codex 远程连接约定

## 4.1 当前使用方式

当前采用：

- **Codex Windows App**
- 通过 **SSH Remote Project** 连接 `jianglab`
- 远程项目目录为：

```text
/home/yulin/projects/OpenClawAndroidNativeEntry
```

---

## 4.2 当前账号约定

当前已采用 **方案 1**：

- Windows 端 Codex app
- `jianglab` 上 Codex CLI

使用的是**同一个 ChatGPT 账号**。

这样做的目的是减少：

- 额度归属混乱
- 认证方式不一致
- 远程线程身份不清楚

---

## 4.3 当前连接原则

Codex app 连接 `jianglab` 时：

- 应通过 Windows 本机 SSH config 中定义的 host alias 连接
- 不推荐长期手工填 IP + 密钥路径的新连接项
- SSH 用户名必须明确指定为 `yulin`
- 不应默认使用 Windows 本机用户名

---

## 5. Windows 侧 SSH 配置原则

## 5.1 SSH config 位置

Windows 本机当前应使用：

```text
C:\Users\28760\.ssh\config
```

## 5.2 当前推荐 host alias

建议使用如下配置：

```sshconfig
Host jianglab
    HostName 100.116.81.62
    User yulin
    Port 22
    IdentityFile C:\Users\28760\.ssh\id_ed25519
```

## 5.3 当前作用

这段配置用于：

- PowerShell 中 `ssh jianglab`
- Codex app 识别并连接远程主机
- 避免远程连接时误用 Windows 本机用户名 `28760`

---

## 6. jianglab 上的 Codex 环境约定

## 6.1 Codex CLI

当前 `jianglab` 上已安装并使用 Codex CLI。

后续若远程连接异常，应优先检查：

```bash
which codex
codex --version
echo $PATH
```

## 6.2 PATH 要求

远程连接要求 `codex` 命令在登录 shell 的 `PATH` 中可用。  
如果 `which codex` 无结果，应优先修复环境变量，而不是先怀疑 app UI。

---

## 7. Git 与 GitHub 当前状态

## 7.1 当前仓库位置

仓库路径：

```text
/home/yulin/projects/OpenClawAndroidNativeEntry
```

## 7.2 当前远程仓库方式

当前 `origin` 已使用 **SSH**，而非 HTTPS。

推荐检查命令：

```bash
git remote -v
```

理想结果应类似：

```text
origin  git@github.com:seedffdfggh34566-prog/OpenClawAndroidNativeEntry.git (fetch)
origin  git@github.com:seedffdfggh34566-prog/OpenClawAndroidNativeEntry.git (push)
```

## 7.3 当前 GitHub 推送方式

当前已打通：

```text
jianglab -> GitHub
```

通过 SSH key 推送，不再依赖：

- GitHub 用户名 + 网页密码
- HTTPS 下手动输入 PAT

---

## 8. 当前 Git 工作原则

## 8.1 正式 Git 操作位置
正式 Git 操作优先在 `jianglab` 上执行，包括：

- `git status`
- `git add`
- `git commit`
- `git push`
- `git pull`
- 分支切换

## 8.2 当前分支原则
- `main` 作为稳定主分支
- 不把 `main` 当长期试验区
- 后续正式功能开发应逐步转向：
  - `feat/...`
  - `fix/...`
  - `docs/...`
  - `chore/...`

## 8.3 推送原则
除非明确需要，否则不要自动 push。  
先确认改动范围与文档同步，再 push。

---

## 9. 当前文档目录原则

当前文档结构位于：

```text
docs/
```

主要层级包括：

- `00_project_overview.md`
- `01_prd/`
- `02_specs/`
- `03_tasks/`
- `04_runbooks/`
- `05_handoffs/`
- `06_decisions/`
- `archive_openclaw/`

### 当前原则
- 当前主线文档保留在主层级
- 旧 OpenClaw 资料放入 `archive_openclaw/`
- 不让历史文档混淆当前 AI 销售助手 V1 主线

---

## 10. 当前日常操作建议

## 10.1 开始工作前
建议先做：

```bash
cd ~/projects/OpenClawAndroidNativeEntry
git status
```

确认：
- 当前是否在正确目录
- 工作区是否干净
- 当前分支是否正确

---

## 10.2 需要远程控制 Codex 时
优先确认：

- Codex app 是否能连上 `jianglab`
- SSH config 是否正确
- `ssh jianglab` 在 PowerShell 中是否可用

---

## 10.3 需要 Git 推送时
优先确认：

```bash
git remote -v
ssh -T git@github.com
```

---

## 10.4 需要 Android 构建时
在 `jianglab` 仓库目录中执行：

```bash
./gradlew tasks
./gradlew assembleDebug
adb devices
```

---

## 11. 常用检查命令

## 11.1 仓库与 Git

```bash
cd ~/projects/OpenClawAndroidNativeEntry
git status
git branch
git remote -v
git log --oneline -n 5
```

## 11.2 Codex 环境

```bash
which codex
codex --version
echo $PATH
```

## 11.3 GitHub SSH

```bash
ssh -T git@github.com
```

## 11.4 Android 构建与设备

```bash
./gradlew tasks
./gradlew assembleDebug
adb devices
```

---

## 12. 常见问题与排查顺序

## 12.1 Codex app 远程连接失败

### 先查
1. Windows PowerShell 中是否能执行：
   ```bash
   ssh jianglab
   ```
2. SSH config 是否写了正确的：
   - `HostName`
   - `User yulin`
   - `IdentityFile`
3. `jianglab` 上 `codex` 是否在 PATH 中：
   ```bash
   which codex
   ```

### 典型问题
- 默认用了 Windows 本地用户名
- 密钥路径错误
- 连接项手工填 IP，未经过 SSH config
- 远程机上找不到 `codex`

---

## 12.2 GitHub push 鉴权失败

### 先查
1. 当前 `origin` 是否还是 HTTPS
2. `git remote -v` 输出是否是 SSH 形式
3. `ssh -T git@github.com` 是否成功

### 典型问题
- 仍使用 HTTPS 地址
- 错把 GitHub 网页密码当 Git push 密码
- `jianglab` 上 GitHub SSH key 未配置或 agent 未加载

---

## 12.3 工作区混乱

### 先查
1. 当前是否确实在 `jianglab` 仓库目录中
2. 是否误在 Windows 本地维护了另一份副本
3. 当前文档是否写到了错误位置

### 原则
- `jianglab` 是唯一真实工作区
- Windows 端不维护第二份正式工作副本

---

## 13. 当前已明确的运维结论

1. `jianglab` 是唯一工作区  
2. Codex app 已可远程连接 `jianglab`  
3. FinalShell 继续保留为辅助终端  
4. VS Code 不再作为当前主工作流的必要组成  
5. GitHub 推送已切换为 SSH 并验证成功  
6. 当前项目已转入 AI 销售助手 V1 主线  
7. OpenClaw 相关旧文档只作为历史参考

---

## 14. 下一步建议

当前最合理的下一步是：

1. 继续完善仓库级文档
2. 完成参考研究笔记
3. 编写 V1 PRD
4. 再拆第一个正式产品 task
5. 用 Codex app 在 `jianglab` 上执行小步开发任务

---

## 15. 一句话总结

当前项目的运行与开发基础设施已经形成如下稳定模式：

> **Codex app 作为主控制台，FinalShell 作为辅助终端，`jianglab` 作为唯一真实工作区和 Git/构建/推送主机。**
