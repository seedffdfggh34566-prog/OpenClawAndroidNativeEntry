# V2 Sales Workspace Markdown Projection

- 文档状态：Draft v0.1
- 更新日期：2026-04-26
- 阶段定位：Sales Workspace Kernel v0 的 Markdown projection 规范
- 建议路径：`docs/architecture/workspace/markdown-projection.md`

---

## 1. 目的

Markdown projection 的目标是让 agent 和开发者可以像阅读软件工程仓库一样阅读销售工作区。

但是 v0 必须坚持：

> **Markdown 是 projection，不是 truth。**

正式业务状态来自结构化 `SalesWorkspace` state。Markdown 由 renderer 生成，不允许被 parse 回主存。

---

## 2. v0 最小目录结构

v0 只渲染 5 类文件：

```text
workspace_projection/
  product/
    current.md
  directions/
    current.md
  research/
    rounds/
      rr_001.md
      rr_002.md
  candidates/
    index.md
  rankings/
    current.md
```

不渲染：

- `memory/`
- `reports/`
- `evidence/sources/`
- `candidates/{candidate_id}.md`
- `commits/`
- `feedback/`

这些留给后续阶段。

---

## 3. Frontmatter

每个文件必须包含 YAML frontmatter：

```yaml
---
generated: true
workspace_id: ws_demo
workspace_version: 4
object_type: candidate_ranking_board
object_id: board_002
generated_at: 2026-04-26T10:00:00Z
---
```

v0 不做：

- checksum。
- sync status。
- parse-back marker。
- editable regions。

---

## 4. 生成规则

### 4.1 `product/current.md`

内容包括：

- 产品名称。
- 一句话描述。
- 目标客户。
- 目标行业。
- 解决痛点。
- 价值主张。
- 约束。

### 4.2 `directions/current.md`

内容包括：

- 优先行业。
- 目标客户类型。
- 地区。
- 公司规模。
- 优先约束。
- 排除行业。
- 排除客户类型。
- 变更原因。

### 4.3 `research/rounds/{round_id}.md`

内容包括：

- round index。
- objective。
- summary。
- limitations。
- 本轮来源摘要。
- 本轮新增或更新候选。

### 4.4 `candidates/index.md`

内容包括当前 ranking board 的候选表：

```markdown
| Rank | Candidate | Score | Status | Reason |
|---:|---|---:|---|---|
| 1 | D 公司 | 63 | high_priority | pain + timing + region evidence |
```

### 4.5 `rankings/current.md`

内容包括：

- 当前排名榜。
- 每个 top candidate 的 score、status、reason。
- supporting observation ids。
- RankingDelta。

---

## 5. v0 禁止事项

v0 禁止：

```text
Product Sales Agent / Runtime 直接编辑 generated markdown
从 markdown parse 回 structured state
让 Markdown 与 JSON state 双向同步
把 Markdown 作为唯一主存
把 ranking 只写在 Markdown 而不写结构化对象
```

---

## 6. 后续可能扩展

v0 之后可以考虑：

1. 生成 `candidates/{candidate_id}.md`。
2. 生成 `evidence/sources/{source_id}.md`。
3. 生成 `reports/latest.md`。
4. 支持 Product Sales Agent / Runtime scratch markdown。
5. 支持 scratch markdown -> patch draft，但仍必须通过 kernel 校验。
6. 支持 checksum 和 generated_from_commit_id。
7. 支持真实 Git commit。

这些均不进入 v0。
