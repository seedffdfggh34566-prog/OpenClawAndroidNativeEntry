# Git / GitHub / SSH / Remote Access 运维说明

更新时间：2026-04-20

## 1. 文档定位

本文档用于记录当前项目的以下基础访问链路与鉴权方式：

1. Windows → `jianglab`
2. Codex app → `jianglab`
3. `jianglab` → GitHub

本文档主要解决以下问题：

- 当前 SSH 是怎么配的
- 当前 GitHub 是怎么推送的
- 哪条链路用哪把 key
- 常见错误分别意味着什么
- 以后出问题应先查哪里

本文档不是产品文档，也不是开发任务文档。  
它只负责固定当前可用的基础设施访问方案。

---

## 2. 当前链路总览

当前项目涉及三条不同的访问链路：

### 链路 A：Windows → jianglab
用途：
- PowerShell 手动 SSH
- FinalShell 登录
- Codex app 远程连接的底层 SSH 基础

### 链路 B：Codex app → jianglab
用途：
- 远程项目接入
- agent 线程执行
- 远程仓库开发

### 链路 C：jianglab → GitHub
用途：
- `git pull`
- `git push`
- 仓库远程同步

这三条链路不能混为一谈。  
它们使用的用户、配置位置、认证目标都可能不同。

---

## 3. 当前基本原则

### 原则 1：`jianglab` 是唯一真实工作区
正式代码、文档和 Git 操作都以 `jianglab` 上的仓库为准。

### 原则 2：Windows 主要用于远程控制，不是主副本
Windows 不维护第二份正式开发副本。

### 原则 3：长期优先使用 SSH，而不是 HTTPS + 手工输入密码/token
特别是 GitHub 推送，应优先走 SSH。

---

## 4. Windows → jianglab 链路

## 4.1 当前用途

这条链路用于：

- PowerShell 中 `ssh jianglab`
- FinalShell 登录 `jianglab`
- Codex app 远程连接 `jianglab` 的底层 SSH 基础

---

## 4.2 当前推荐用户

当前远程登录 `jianglab` 的用户名应为：

```text
yulin
```

不要默认使用 Windows 本机用户名。

---

## 4.3 当前 Windows SSH config 位置

当前应使用：

```text
C:\Users\28760\.ssh\config
```

---

## 4.4 当前推荐 host alias

当前推荐配置为：

```sshconfig
Host jianglab
    HostName 100.116.81.62
    User yulin
    Port 22
    IdentityFile C:\Users\28760\.ssh\id_ed25519
```

这段配置的核心作用是：

- 固定远程用户名为 `yulin`
- 固定远程主机地址为 `100.116.81.62`
- 固定 Windows 侧使用的私钥为 `id_ed25519`
- 给 Codex app 和 PowerShell 提供统一入口

---

## 4.5 当前验证命令

在 Windows PowerShell 中执行：

```bash
ssh jianglab
```

如果能直接进入 `jianglab`，说明：

- SSH config 生效
- 用户名正确
- 私钥可用
- 远程主机可达

如果这一步不通，Codex app 的远程连接也不应继续排查更高层逻辑。

---

## 5. Codex app → jianglab 链路

## 5.1 当前用途

这条链路用于：

- Codex Windows App 打开远程项目
- 远程线程执行
- agent 在 `jianglab` 仓库上读写文件与执行命令

---

## 5.2 当前关键原则

Codex app 不应长期通过“手工填 IP + 手工填密钥路径”的方式建立连接项。  
更推荐使用 Windows SSH config 中定义的 host alias。

原因：

- 可以显式指定 `User yulin`
- 可避免默认误用 Windows 本地用户名
- 配置更稳定
- 与 PowerShell 验证方式统一

---

## 5.3 当前已知经验

曾出现过以下问题：

### 1）错误使用不存在的密钥
例如填写：

```text
~/.ssh/id_rsa
```

但该文件在 Windows 上并不存在，最终导致认证失败。

### 2）错误使用 Windows 本机用户名
Codex app 曾尝试使用：

```text
28760@100.116.81.62
```

而非：

```text
yulin@100.116.81.62
```

这说明如果不通过 SSH config 显式指定 `User yulin`，远程连接很容易失败。

---

## 5.4 当前排查顺序

如果 Codex app 无法连接 `jianglab`，优先检查：

1. PowerShell 中 `ssh jianglab` 是否成功
2. `C:\Users\28760\.ssh\config` 是否存在且格式正确
3. `IdentityFile` 指向的私钥是否真实存在
4. `jianglab` 上 `codex` 是否在 PATH 中可用

---

## 6. jianglab → GitHub 链路

## 6.1 当前用途

这条链路用于：

- 从 `jianglab` 仓库推送到 GitHub
- 从 GitHub 拉取到 `jianglab`

这与 Windows → `jianglab` 的 SSH 登录不是同一件事。

---

## 6.2 当前远程仓库方式

当前仓库的 `origin` 已经从 HTTPS 切换为 SSH。

推荐检查：

```bash
git remote -v
```

当前理想结果应为：

```text
origin  git@github.com:seedffdfggh34566-prog/OpenClawAndroidNativeEntry.git (fetch)
origin  git@github.com:seedffdfggh34566-prog/OpenClawAndroidNativeEntry.git (push)
```

---

## 6.3 为什么不再使用 HTTPS

早期 `git push origin main` 时，仓库远程地址还是 HTTPS，结果出现：

- 提示输入 GitHub 用户名
- 提示输入 Password
- 输入网页密码后失败

根本原因是：

> GitHub 已不支持使用网页密码进行 Git 操作鉴权。

在 HTTPS 模式下，正确做法是使用 Personal Access Token（PAT），而不是网页密码。

但当前项目已切换到 SSH，因此不再推荐继续依赖 HTTPS + PAT。

---

## 6.4 当前 GitHub SSH 认证方式

当前已经在 `jianglab` 上为 GitHub 配置了 SSH key，且推送已验证成功。

推荐验证命令：

```bash
ssh -T git@github.com
```

若配置正常，通常会看到 GitHub 的认证成功提示。

---

## 6.5 当前推送状态

当前 `git push origin main` 已成功执行，说明：

- `origin` SSH 远程地址正常
- `jianglab` 上 GitHub key 正常
- 当前主仓库与 GitHub 已能正常同步

---

## 7. 当前三条链路分别用什么

| 链路 | 发起端 | 目标端 | 主要用途 | 当前方式 |
|---|---|---|---|---|
| A | Windows | jianglab | SSH 登录 / PowerShell / FinalShell | SSH config + `id_ed25519` |
| B | Codex app | jianglab | 远程项目 / agent 执行 | 基于 Windows SSH config |
| C | jianglab | GitHub | Git push / pull | SSH remote + GitHub key |

---

## 8. 常用验证命令

## 8.1 Windows → jianglab

在 PowerShell 中：

```bash
ssh jianglab
```

---

## 8.2 jianglab → GitHub

在 `jianglab` 上：

```bash
ssh -T git@github.com
```

---

## 8.3 检查当前仓库远程地址

在 `jianglab` 仓库目录中：

```bash
git remote -v
```

---

## 8.4 检查当前工作区状态

```bash
cd ~/projects/OpenClawAndroidNativeEntry
git status
git branch
```

---

## 9. 常见错误与解释

## 9.1 `Permission denied (publickey,password)`

### 可能原因
- 密钥路径写错
- 远程用户写错
- 公钥未配置到目标主机
- SSH config 未生效

### 典型案例
Codex app 曾因默认使用 Windows 本地用户名而失败。

---

## 9.2 `Invalid username or token. Password authentication is not supported for Git operations.`

### 含义
- 当前是 HTTPS 仓库地址
- GitHub 不接受网页密码
- 应改用 PAT 或切换到 SSH

### 当前结论
本项目已切换为 SSH，因此后续不应再回到网页密码方式。

---

## 9.3 `Identity file ... not accessible`

### 含义
指定的私钥文件不存在。

### 当前经验
Windows 上曾指定 `id_rsa`，但该文件不存在，最终 SSH 退回到密码登录。

---

## 9.4 PowerShell 能连，Codex app 不能连

### 优先检查
- Codex app 是否绕开了 SSH config
- 是否未显式使用 `User yulin`
- 是否仍引用了错误密钥路径

### 原则
先保证：

```bash
ssh jianglab
```

成功，再排查 Codex app。

---

## 10. 当前操作建议

## 10.1 新增或修改 SSH 连接时
优先改：

```text
C:\Users\28760\.ssh\config
```

而不是在多个客户端里各自填不同参数。

---

## 10.2 需要验证远程连接时
先在 PowerShell 验证，再看 Codex app。

---

## 10.3 需要验证 GitHub 推送时
优先检查：

```bash
ssh -T git@github.com
git remote -v
```

不要先去猜 token 或网页密码。

---

## 10.4 需要给 AI 接手时
优先让其阅读本文档，先理解三条链路的区别，再进行排障。

---

## 11. 当前固定约定

1. `jianglab` 是唯一真实工作区  
2. Windows 只作为远程控制台  
3. Windows → `jianglab` 依赖 SSH config  
4. Codex app 应通过 host alias 连接 `jianglab`  
5. `jianglab -> GitHub` 使用 SSH 推送  
6. 不再使用 GitHub 网页密码进行 Git 推送  
7. 不长期回退到 HTTPS + PAT 作为主方式

---

## 12. 一句话总结

当前项目的 SSH 与 Git 访问模式已固定为：

> **Windows 通过 SSH config 连接 `jianglab`，Codex app 基于同一 SSH 配置使用远程项目，而 `jianglab` 通过 SSH 与 GitHub 同步仓库。**
