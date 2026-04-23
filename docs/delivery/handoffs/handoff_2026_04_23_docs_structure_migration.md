# 阶段性交接：docs 结构迁移

更新时间：2026-04-23

## 1. 本次改了什么

本次把仓库文档结构从旧的编号目录迁移到了新的 docs 架构：

- `product/`
- `architecture/`
- `reference/`
- `how-to/`
- `adr/`
- `delivery/`
- `archive/`

同时更新了主要入口文件和核心内部引用。

---

## 2. 为什么这么定

当前仓库已经进入“后端优先、多端入口、agent 驱动开发”阶段，继续沿用编号目录会让语义越来越模糊。

本次先完成文档结构迁移，而不同时动代码目录，可以在低 blast radius 下提升后续协作效率。

---

## 3. 本次验证了什么

1. 检查 `docs/` 文件树已经切换到新结构
2. 检查 `AGENTS.md`、`docs/README.md`、`docs/delivery/tasks/_active.md` 已能作为统一入口
3. 检查主要旧路径引用已更新到新路径

---

## 4. 已知限制

- 部分历史 handoff / archive 文案仍保留少量旧结构描述
- 本次没有重构代码目录
- 本次没有新增 Android 联调 task，只保留为下一步建议

---

## 5. 推荐下一步

1. 创建“Android 壳层最小真实数据对接” follow-up task
2. 后续所有新任务与 handoff 只使用新 docs 路径
