# 阶段性交接：AGENTS.md compression and minimal skill migration

更新时间：2026-04-29

## 1. 本次改了什么

- 将根 `AGENTS.md` 压缩为 V3-first 的稳定仓库执行契约。
- 删除根规则中的默认多 agent 工作流和硬性 milestone 表格规则。
- 将两个 multi-agent how-to 文件降级为 historical reference only。
- 新增 `repo-task-bootstrap` 真实 skill source/spec。
- 更新 `task-handoff-sync`，加入 task/handoff completion wording guard。
- 更新 skill 同步脚本和 skill spec 索引。

---

## 2. 为什么这么定

- 用户明确要求暂时不要多 agent 工作流。
- 用户明确要求移除过硬的 milestone 规则，只保留普通 task/handoff 不应越界声明版本或阶段完成的边界。
- 根 `AGENTS.md` 应承载稳定仓库规则，可复用流程迁入 skill，避免再次膨胀。

---

## 3. 本次验证了什么

1. `git diff --check`
2. 旧 V2 / 多 agent /硬 milestone 关键短语检查
3. V3 / task-handoff 关键词检查
4. 本机 Codex skills 文件存在性检查

---

## 4. 已知限制

- `app/AGENTS.md` 和 `backend/AGENTS.md` 本轮未调整。
- 历史 task / handoff / research 文件未批量重写。
- V3 runtime / memory / backend / Android implementation 未启动。

---

## 5. 推荐下一步

1. 单独 review `backend/AGENTS.md` 是否也需要 V3-first 压缩。
2. 后续如恢复多线程协作，应先重新讨论并创建新的当前流程文档。
