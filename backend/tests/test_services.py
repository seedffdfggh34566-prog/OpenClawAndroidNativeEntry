from __future__ import annotations

from backend.api import models, schemas, services


def test_create_product_profile_sets_expected_defaults(db_session) -> None:
    profile = services.create_product_profile(
        db_session,
        schemas.ProductProfileCreateRequest(
            name="AI 销售助手 V1",
            one_line_description="帮助用户先讲清产品，再生成获客分析结果。",
            source_notes="用于 service 测试。",
        ),
    )

    assert profile.id.startswith("pp_")
    assert profile.status == "draft"
    assert profile.version == 1
    assert "价格区间" in profile.missing_fields


def test_create_analysis_run_queues_lead_analysis(db_session) -> None:
    profile = services.create_product_profile(
        db_session,
        schemas.ProductProfileCreateRequest(
            name="AI 销售助手 V1",
            one_line_description="帮助用户先讲清产品，再生成获客分析结果。",
            source_notes="用于 run 测试。",
        ),
    )

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
    assert run.runtime_provider == "stub"
    assert run.output_refs == []


def test_build_result_summary_returns_none_for_non_succeeded_run(db_session) -> None:
    agent_run = models.AgentRun(
        id="run_manual",
        run_type="lead_analysis",
        triggered_by="user",
        trigger_source="android_home",
        input_refs=[],
        output_refs=[],
        status="queued",
        runtime_provider="stub",
        runtime_metadata={"adapter": "stub"},
    )
    db_session.add(agent_run)
    db_session.commit()

    assert services.build_result_summary(db_session, agent_run) is None
