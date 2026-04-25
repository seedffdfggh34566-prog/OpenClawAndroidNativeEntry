from __future__ import annotations

from typing import Protocol


DEFAULT_DELIVERY_MODEL = "mobile_control_entry + local_backend"


class ProductLearningProfileLike(Protocol):
    name: str
    one_line_description: str
    target_customers: list[str]
    target_industries: list[str]
    typical_use_cases: list[str]
    pain_points_solved: list[str]
    core_advantages: list[str]
    delivery_model: str
    constraints: list[str]
    status: str


def canonical_missing_fields(profile: ProductLearningProfileLike) -> list[str]:
    missing_fields: list[str] = []

    if not profile.name.strip():
        missing_fields.append("产品名称")
    if not profile.one_line_description.strip():
        missing_fields.append("一句话描述")
    if not profile.target_customers:
        missing_fields.append("目标客户")
    if not profile.typical_use_cases:
        missing_fields.append("典型场景")
    if not profile.pain_points_solved:
        missing_fields.append("解决痛点")
    if not profile.core_advantages:
        missing_fields.append("核心优势")
    if not profile.target_industries:
        missing_fields.append("目标行业")
    if not profile.constraints:
        missing_fields.append("限制条件")
    if not profile.delivery_model.strip():
        missing_fields.append("交付方式")

    return missing_fields


def derive_learning_stage(profile: ProductLearningProfileLike) -> str:
    if profile.status == "confirmed":
        return "confirmed"
    if profile.status != "draft":
        return "collecting"
    return (
        "ready_for_confirmation"
        if not any(
            label in canonical_missing_fields(profile)
            for label in ("目标客户", "典型场景", "解决痛点", "核心优势")
        )
        else "collecting"
    )
