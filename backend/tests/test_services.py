from __future__ import annotations

import pytest
from fastapi import HTTPException

from backend.api import models, schemas, services


def test_create_product_profile_sets_expected_defaults(db_session) -> None:
    created = services.create_product_profile(
        db_session,
        schemas.ProductProfileCreateRequest(
            name="AI 销售助手 V1",
            one_line_description="帮助用户先讲清产品，再生成获客分析结果。",
            source_notes="用于 service 测试。",
        ),
    )
    profile = created.product_profile
    current_run = created.current_run

    assert profile.id.startswith("pp_")
    assert profile.status == "draft"
    assert profile.version == 1
    assert current_run.run_type == "product_learning"
    assert current_run.status == "queued"
    assert current_run.runtime_metadata["graph_name"] == "product_learning_graph"
    assert current_run.runtime_metadata["prompt_version"] == "heuristic_v1"
    assert current_run.runtime_metadata["round_index"] == 0
    assert profile.missing_fields
    assert services.derive_learning_stage(profile) == "collecting"


def test_create_analysis_run_queues_lead_analysis(db_session) -> None:
    profile = services.create_product_profile(
        db_session,
        schemas.ProductProfileCreateRequest(
            name="AI 销售助手 V1",
            one_line_description="帮助用户先讲清产品，再生成获客分析结果。",
            source_notes="用于 run 测试。",
        ),
    ).product_profile

    profile.target_customers = ["销售负责人"]
    profile.typical_use_cases = ["梳理销售表达"]
    profile.pain_points_solved = ["产品价值表达不清"]
    profile.core_advantages = ["先帮助用户讲清产品"]
    profile.missing_fields = services.canonical_missing_fields(profile)
    db_session.commit()

    services.confirm_product_profile(db_session, profile.id)

    run = services.create_analysis_run(
        db_session,
        schemas.AnalysisRunCreateRequest(
            run_type="lead_analysis",
            product_profile_id=profile.id,
            trigger_source="android_home",
        ),
    )

    assert run.id.startswith("run_")
    assert run.status == "queued"
    assert run.runtime_provider == "langgraph"
    assert run.output_refs == []
    assert run.runtime_metadata["provider"] == "langgraph"
    assert run.runtime_metadata["graph_name"] == "lead_analysis_graph"
    assert run.runtime_metadata["prompt_version"] == "heuristic_v1"
    assert run.runtime_metadata["round_index"] == 0


def test_process_agent_run_marks_failed_for_unsupported_run_type(db_session) -> None:
    agent_run = models.AgentRun(
        id="run_invalid",
        run_type="invalid_runtime_path",
        triggered_by="user",
        trigger_source="test",
        input_refs=[],
        output_refs=[],
        status="queued",
        runtime_provider="langgraph",
        runtime_metadata={"provider": "langgraph"},
    )
    db_session.add(agent_run)
    db_session.commit()

    services.process_agent_run(agent_run.id)
    db_session.expire_all()

    refreshed = services.get_agent_run_or_404(db_session, agent_run.id)
    assert refreshed.status == "failed"
    assert "unsupported_run_type" in str(refreshed.error_message)
    assert refreshed.runtime_metadata["error_type"] == "ValueError"


def test_build_result_summary_returns_none_for_non_succeeded_run(db_session) -> None:
    agent_run = models.AgentRun(
        id="run_manual",
        run_type="lead_analysis",
        triggered_by="user",
        trigger_source="android_home",
        input_refs=[],
        output_refs=[],
        status="queued",
        runtime_provider="langgraph",
        runtime_metadata={"provider": "langgraph"},
    )
    db_session.add(agent_run)
    db_session.commit()

    assert services.build_result_summary(db_session, agent_run) is None


def test_process_product_learning_run_updates_same_profile(db_session) -> None:
    created = services.create_product_profile(
        db_session,
        schemas.ProductProfileCreateRequest(
            name="AI 销售助手 V1",
            one_line_description="帮助用户先讲清产品，再生成获客分析结果。",
            source_notes="适合企业服务团队做产品学习。",
        ),
    )

    services.process_agent_run(created.current_run.id)
    db_session.expire_all()

    refreshed_profile = services.get_product_profile_or_404(db_session, created.product_profile.id)
    refreshed_run = services.get_agent_run_or_404(db_session, created.current_run.id)
    assert refreshed_run.status == "succeeded"
    assert refreshed_run.runtime_metadata["prompt_version"] == "heuristic_v1"
    assert refreshed_run.runtime_metadata["round_index"] == 0
    assert refreshed_profile.version == 2
    assert refreshed_profile.target_customers
    assert refreshed_profile.typical_use_cases
    assert refreshed_profile.pain_points_solved
    assert refreshed_profile.core_advantages
    assert services.derive_learning_stage(refreshed_profile) == "ready_for_confirmation"
    assert refreshed_run.output_refs[0]["object_type"] == "product_profile"
    assert refreshed_run.output_refs[0]["object_id"] == refreshed_profile.id


def test_confirm_requires_ready_for_confirmation(db_session) -> None:
    created = services.create_product_profile(
        db_session,
        schemas.ProductProfileCreateRequest(
            name="Collecting Draft",
            one_line_description="只创建一个草稿。",
            source_notes=None,
        ),
    )

    with pytest.raises(HTTPException) as exc_info:
        services.confirm_product_profile(db_session, created.product_profile.id)

    assert exc_info.value.status_code == 409


def test_build_result_summary_supports_product_learning(db_session) -> None:
    created = services.create_product_profile(
        db_session,
        schemas.ProductProfileCreateRequest(
            name="AI 销售助手 V1",
            one_line_description="帮助用户先讲清产品，再生成获客分析结果。",
            source_notes="适合企业服务团队做产品学习。",
        ),
    )

    services.process_agent_run(created.current_run.id)
    db_session.expire_all()
    refreshed_run = services.get_agent_run_or_404(db_session, created.current_run.id)

    summary = services.build_result_summary(db_session, refreshed_run)
    assert summary is not None
    assert summary["product_profile_id"] == created.product_profile.id
    assert summary["learning_stage"] == "ready_for_confirmation"


def test_enrich_product_profile_appends_notes_and_increments_round_index(db_session) -> None:
    created = services.create_product_profile(
        db_session,
        schemas.ProductProfileCreateRequest(
            name="AI 销售助手 V1",
            one_line_description="帮助用户先讲清产品，再生成获客分析结果。",
            source_notes="第一轮说明。",
        ),
    )
    services.process_agent_run(created.current_run.id)
    db_session.expire_all()

    first_enrich = services.enrich_product_profile(
        db_session,
        created.product_profile.id,
        schemas.ProductProfileEnrichRequest(
            supplemental_notes="补充目标客户和典型场景。",
            trigger_source="android_product_learning_iteration",
        ),
    )
    second_enrich = services.enrich_product_profile(
        db_session,
        created.product_profile.id,
        schemas.ProductProfileEnrichRequest(
            supplemental_notes="继续补充限制条件。",
            trigger_source="android_product_learning_iteration",
        ),
    )
    db_session.expire_all()

    refreshed_profile = services.get_product_profile_or_404(db_session, created.product_profile.id)
    assert refreshed_profile.source_notes == (
        "第一轮说明。\n补充目标客户和典型场景。\n继续补充限制条件。"
    )
    assert first_enrich.run_type == "product_learning"
    assert first_enrich.runtime_metadata["round_index"] == 1
    assert second_enrich.runtime_metadata["round_index"] == 2
    assert second_enrich.runtime_metadata["prompt_version"] == "heuristic_v1"


def test_enrich_product_profile_rejects_missing_profile(db_session) -> None:
    with pytest.raises(HTTPException) as exc_info:
        services.enrich_product_profile(
            db_session,
            "pp_missing",
            schemas.ProductProfileEnrichRequest(
                supplemental_notes="补充信息。",
                trigger_source="android_product_learning_iteration",
            ),
        )

    assert exc_info.value.status_code == 404


def test_enrich_product_profile_requires_draft(db_session) -> None:
    created = services.create_product_profile(
        db_session,
        schemas.ProductProfileCreateRequest(
            name="AI 销售助手 V1",
            one_line_description="帮助用户先讲清产品，再生成获客分析结果。",
            source_notes="适合企业服务团队做产品学习。",
        ),
    )
    services.process_agent_run(created.current_run.id)
    db_session.expire_all()
    services.confirm_product_profile(db_session, created.product_profile.id)

    with pytest.raises(HTTPException) as exc_info:
        services.enrich_product_profile(
            db_session,
            created.product_profile.id,
            schemas.ProductProfileEnrichRequest(
                supplemental_notes="确认后不再通过 enrich 修改。",
                trigger_source="android_product_learning_iteration",
            ),
        )

    assert exc_info.value.status_code == 409
