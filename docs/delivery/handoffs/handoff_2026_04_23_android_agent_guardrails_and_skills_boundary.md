# 阶段性交接：第一阶段规则分层落地与 Android 约束下沉

更新时间：2026-04-23

## 1. 本次改了什么

- 重写根 `AGENTS.md`，把 Android 详细实现约束从根规则中移出
- 新建 `app/AGENTS.md`，承接 Android 默认实现风格、验证分级、真机证据、高风险文件、停止条件与完成定义
- 新增 `docs/architecture/clients/android-client-implementation-constraints.md`
- 收缩 `docs/how-to/operate/agent_skills_boundary_and_index.md`
- 同步更新 `docs/README.md`、`docs/architecture/README.md` 与 `docs/how-to/README.md`
- 重写本次 task 记录

---

## 2. 为什么这么定

- 当前仓库已经是产品主仓库，而不是 Android 专仓
- Android 默认实现风格属于平台局部规则，不适合长期堆在根 `AGENTS.md`
- `app/AGENTS.md` 更适合承接 Android 侧的执行性规则
- `docs/architecture/clients/` 更适合解释这些 Android 约束为什么成立
- Skills 继续保留为增强层，但不应抢占 docs 主入口

---

## 3. 本次验证了什么

1. 对照当前 `app/` 单模块 Compose 工程与已有导航 / Termux / shell 代码，确认新增规则贴合当前仓库现实
2. 对照官方 Android 文档，确认本次约束与 UDF、可选 domain layer、测试分层、按需模块化方向一致
3. 对照官方 OpenAI / Codex 资料，确认 `AGENTS.md` 应继续承接持久上下文，而 Skills 适合作为执行增强层
4. 运行 `git diff --check`，确认本次文档改动无格式问题

---

## 4. 已知限制

- 本次只完成第一阶段规则分层，没有创建真实 Skill
- 本次没有新增 `backend/AGENTS.md` 或未来 iOS 规则文件
- 本次没有引入新的 Android 自动化测试或截图测试基础设施

---

## 5. 推荐下一步

1. 若 Android 线程开始频繁涉及 `adb` / Termux / 真机验证，可单独拆一个低风险 Skill 索引落地任务
2. 若 `backend/` 或 iOS 目录后续形成稳定子系统，再按同样模式做局部规则分层
