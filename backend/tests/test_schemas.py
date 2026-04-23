from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.api import schemas


def test_product_profile_create_request_accepts_valid_payload() -> None:
    payload = schemas.ProductProfileCreateRequest.model_validate(
        {
            "name": "AI 销售助手 V1",
            "one_line_description": "帮助用户先讲清产品，再生成获客分析结果。",
            "source_notes": "最小测试输入。",
        }
    )

    assert payload.name == "AI 销售助手 V1"
    assert payload.source_notes == "最小测试输入。"


def test_product_profile_create_request_rejects_blank_name() -> None:
    with pytest.raises(ValidationError):
        schemas.ProductProfileCreateRequest.model_validate(
            {
                "name": "",
                "one_line_description": "desc",
            }
        )


def test_report_generation_requires_lead_analysis_result_id() -> None:
    with pytest.raises(ValidationError):
        schemas.AnalysisRunCreateRequest.model_validate(
            {
                "run_type": "report_generation",
                "product_profile_id": "pp_1234",
                "trigger_source": "android_report",
            }
        )
