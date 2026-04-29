# Milestone Acceptance Review Template

更新时间：YYYY-MM-DD

## 1. Review Target

- Milestone：
- Review owner：
- Review type：docs-only evidence review
- Authorization source：

本 review 用于判断 milestone 状态是否可以调整。它不开放 backend / Android / runtime implementation，不替代 PRD、roadmap、ADR 或 architecture baseline。

---

## 2. Acceptance Sources

列出本次验收使用的产品和架构标准。

| Source | Scope | Notes |
|---|---|---|
| `docs/product/prd/...` |  |  |
| `docs/product/roadmap.md` |  |  |
| `docs/adr/...` |  |  |
| `docs/architecture/...` |  |  |

---

## 3. Implementation Evidence Inspected

列出实际检查过的代码区域。没有检查的区域必须明示，不能用 task / handoff 的 `done` 代替。

| Area | Files / directories inspected | Notes |
|---|---|---|
| Backend |  |  |
| Android |  |  |
| Runtime |  |  |
| Persistence / migration |  |  |
| API / contract |  |  |

---

## 4. Validation Evidence

列出实际运行或已记录的验证证据。

| Validation | Command or evidence source | Result | Notes |
|---|---|---|---|
|  |  |  |  |

---

## 5. PRD Acceptance Traceability

Status must use exactly: `done`, `partial`, `missing`, `out of scope`.

| PRD criterion | Status | Acceptance source | Code evidence | Validation evidence | Delivery evidence | Gap | Confidence |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

Rules:

- `done` requires acceptance source, code evidence, and validation evidence.
- `partial` must describe the remaining gap against the acceptance source.
- `missing` must identify the missing implementation object or behavior.
- `out of scope` must cite the PRD, roadmap, ADR, or explicit scope rule.
- If code or validation evidence was not inspected, confidence must be `low`.

---

## 6. Capability Matrix Update Recommendation

| Capability | Current status | Recommended status | Evidence summary | Reason |
|---|---|---|---|---|
|  |  |  |  |  |

---

## 7. Milestone Status Recommendation

Recommended milestone status：

Rationale：

Required follow-up before status upgrade：

Human decision needed：

---

## 8. Explicit Non-Goals

- Do not implement backend / Android / runtime code in this review.
- Do not open V2.2 implementation unless separately authorized.
- Do not treat task / handoff completion as primary proof.
- Do not change PRD / ADR product meaning unless explicitly authorized.

---

## 9. Known Limits

- TBD

---

## 10. Recommended Next Package

- Package name：
- Package type：docs / planning / implementation
- Authorization source needed：
- Stop conditions：
