from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.api.config import reset_settings_cache
from backend.api.database import reset_database_state
from backend.runtime.llm_client import TokenHubCompletion


class BackendApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.llm_patcher = patch(
            "backend.runtime.graphs.product_learning.TokenHubClient.complete",
            return_value=TokenHubCompletion(
                content=json.dumps(
                    {
                        "target_customers": ["销售负责人", "创始人"],
                        "target_industries": ["企业服务"],
                        "typical_use_cases": ["梳理产品表达", "生成获客分析输入"],
                        "pain_points_solved": ["产品价值表达不清"],
                        "core_advantages": ["先讲清产品再做销售分析"],
                        "delivery_model": "mobile_control_entry + local_backend",
                        "constraints": ["当前仍需人工确认"],
                        "missing_fields": [],
                        "confidence_score": 82,
                    },
                    ensure_ascii=False,
                ),
                usage={"total_tokens": 128},
            ),
        )
        self.llm_patcher.start()
        self.temp_dir = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_dir.name) / "test.db"
        os.environ["OPENCLAW_BACKEND_DATABASE_PATH"] = str(database_path)
        reset_settings_cache()
        reset_database_state()

        from backend.api.main import create_app

        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        reset_database_state()
        reset_settings_cache()
        os.environ.pop("OPENCLAW_BACKEND_DATABASE_PATH", None)
        self.temp_dir.cleanup()
        self.llm_patcher.stop()

    def test_product_profile_create_and_get(self) -> None:
        create_response = self.client.post(
            "/product-profiles",
            json={
                "name": "AI 销售助手 V1",
                "one_line_description": "帮助用户先讲清产品，再生成获客分析结果。",
                "source_notes": "最小测试输入。",
            },
        )
        self.assertEqual(create_response.status_code, 200)
        created_payload = create_response.json()
        product_profile_id = created_payload["product_profile"]["id"]
        current_run = created_payload["current_run"]
        self.assertIsNotNone(current_run)
        self.assertEqual(current_run["run_type"], "product_learning")

        get_response = self.client.get(f"/product-profiles/{product_profile_id}")
        self.assertEqual(get_response.status_code, 200)
        payload = get_response.json()["product_profile"]
        self.assertEqual(payload["id"], product_profile_id)
        self.assertEqual(payload["status"], "draft")
        self.assertIn(payload["learning_stage"], ["collecting", "ready_for_confirmation"])
        self.assertIn("missing_fields", payload)

        run_detail = self.client.get(f"/analysis-runs/{current_run['id']}")
        self.assertEqual(run_detail.status_code, 200)
        run_payload = run_detail.json()
        self.assertEqual(run_payload["agent_run"]["status"], "succeeded")
        runtime_metadata = run_payload["agent_run"]["runtime_metadata"]
        self.assertEqual(runtime_metadata["llm_provider"], "tencent_tokenhub")
        self.assertEqual(runtime_metadata["llm_model"], "minimax-m2.5")
        self.assertEqual(runtime_metadata["llm_usage"]["total_tokens"], 128)
        self.assertEqual(
            run_payload["result_summary"]["product_profile_id"],
            product_profile_id,
        )

        not_found_response = self.client.get("/product-profiles/pp_missing")
        self.assertEqual(not_found_response.status_code, 404)

    def test_product_profile_enrich_queues_learning_run(self) -> None:
        product_profile_id = self._create_product_profile()

        enrich_response = self.client.post(
            f"/product-profiles/{product_profile_id}/enrich",
            json={
                "supplemental_notes": "补充目标客户是销售负责人，典型场景是首轮获客分析。",
                "trigger_source": "android_product_learning_iteration",
            },
        )
        self.assertEqual(enrich_response.status_code, 200)
        enrich_payload = enrich_response.json()["agent_run"]
        self.assertEqual(enrich_payload["run_type"], "product_learning")
        self.assertEqual(enrich_payload["trigger_source"], "android_product_learning_iteration")

        run_detail = self.client.get(f"/analysis-runs/{enrich_payload['id']}")
        self.assertEqual(run_detail.status_code, 200)
        run_payload = run_detail.json()
        self.assertEqual(run_payload["agent_run"]["status"], "succeeded")
        self.assertEqual(
            run_payload["result_summary"]["product_profile_id"],
            product_profile_id,
        )

        from backend.api import services
        from backend.api.database import get_session_factory

        session = get_session_factory()()
        try:
            profile = services.get_product_profile_or_404(session, product_profile_id)
            self.assertIn("用于集成测试。", profile.source_notes or "")
            self.assertIn("补充目标客户是销售负责人", profile.source_notes or "")
        finally:
            session.close()

    def test_product_profile_enrich_rejects_invalid_requests(self) -> None:
        product_profile_id = self._create_product_profile()

        blank_response = self.client.post(
            f"/product-profiles/{product_profile_id}/enrich",
            json={
                "supplemental_notes": "   ",
                "trigger_source": "android_product_learning_iteration",
            },
        )
        self.assertEqual(blank_response.status_code, 422)

        not_found_response = self.client.post(
            "/product-profiles/pp_missing/enrich",
            json={
                "supplemental_notes": "补充信息。",
                "trigger_source": "android_product_learning_iteration",
            },
        )
        self.assertEqual(not_found_response.status_code, 404)

    def test_lead_analysis_result_detail(self) -> None:
        product_profile_id = self._create_product_profile()
        self._confirm_product_profile(product_profile_id)
        lead_analysis_result_id = self._run_lead_analysis(product_profile_id)

        detail_response = self.client.get(f"/lead-analysis-results/{lead_analysis_result_id}")
        self.assertEqual(detail_response.status_code, 200)
        payload = detail_response.json()["lead_analysis_result"]
        self.assertEqual(payload["id"], lead_analysis_result_id)
        self.assertEqual(payload["product_profile_id"], product_profile_id)
        self.assertIn("summary", payload)
        self.assertEqual(payload["analysis_scope"], "基于已确认产品画像的获客方向分析")
        self.assertIn("priority_industries", payload)
        self.assertIsInstance(payload["priority_industries"], list)
        self.assertIn("priority_customer_types", payload)
        self.assertIn("scenario_opportunities", payload)
        self.assertIn("ranking_explanations", payload)
        self.assertIn("recommendations", payload)
        self.assertIn("risks", payload)
        self.assertIn("limitations", payload)

        not_found_response = self.client.get("/lead-analysis-results/lar_missing")
        self.assertEqual(not_found_response.status_code, 404)

    def test_product_profile_confirm(self) -> None:
        product_profile_id = self._create_product_profile()

        confirm_response = self.client.post(f"/product-profiles/{product_profile_id}/confirm")
        self.assertEqual(confirm_response.status_code, 200)
        payload = confirm_response.json()["product_profile"]
        self.assertEqual(payload["id"], product_profile_id)
        self.assertEqual(payload["status"], "confirmed")
        self.assertEqual(payload["version"], 3)

        # Idempotent: confirming again should succeed
        second_confirm = self.client.post(f"/product-profiles/{product_profile_id}/confirm")
        self.assertEqual(second_confirm.status_code, 200)
        self.assertEqual(second_confirm.json()["product_profile"]["status"], "confirmed")

        not_found = self.client.post("/product-profiles/pp_missing/confirm")
        self.assertEqual(not_found.status_code, 404)

    def test_product_profile_confirm_rejects_collecting_draft(self) -> None:
        create_response = self.client.post(
            "/product-profiles",
            json={
                "name": "仅有名称的画像",
                "one_line_description": "先建一个画像。",
                "source_notes": "",
            },
        )
        self.assertEqual(create_response.status_code, 200)
        product_profile_id = create_response.json()["product_profile"]["id"]

        # Force a collecting draft through the service boundary assumptions.
        from backend.api.database import get_session_factory
        from backend.api import services

        session = get_session_factory()()
        try:
            profile = services.get_product_profile_or_404(session, product_profile_id)
            profile.target_customers = []
            profile.typical_use_cases = []
            profile.pain_points_solved = []
            profile.core_advantages = []
            profile.missing_fields = ["目标客户", "典型场景", "解决痛点", "核心优势"]
            session.commit()
        finally:
            session.close()

        confirm_response = self.client.post(f"/product-profiles/{product_profile_id}/confirm")
        self.assertEqual(confirm_response.status_code, 409)

    def test_lead_analysis_rejects_draft_profile(self) -> None:
        product_profile_id = self._create_product_profile()

        run_response = self.client.post(
            "/analysis-runs",
            json={
                "run_type": "lead_analysis",
                "product_profile_id": product_profile_id,
                "lead_analysis_result_id": None,
                "trigger_source": "android_home",
            },
        )
        self.assertEqual(run_response.status_code, 409)

    def test_lead_analysis_run_succeeds_and_returns_output_refs(self) -> None:
        product_profile_id = self._create_product_profile()
        self._confirm_product_profile(product_profile_id)

        run_response = self.client.post(
            "/analysis-runs",
            json={
                "run_type": "lead_analysis",
                "product_profile_id": product_profile_id,
                "lead_analysis_result_id": None,
                "trigger_source": "android_home",
            },
        )
        self.assertEqual(run_response.status_code, 200)
        run_id = run_response.json()["agent_run"]["id"]

        get_run_response = self.client.get(f"/analysis-runs/{run_id}")
        self.assertEqual(get_run_response.status_code, 200)
        payload = get_run_response.json()
        self.assertEqual(payload["agent_run"]["status"], "succeeded")
        self.assertEqual(
            payload["agent_run"]["output_refs"][0]["object_type"],
            "lead_analysis_result",
        )
        self.assertIsNotNone(payload["result_summary"])

    def test_report_generation_run_and_report_read(self) -> None:
        product_profile_id = self._create_product_profile()
        self._confirm_product_profile(product_profile_id)
        lead_analysis_result_id = self._run_lead_analysis(product_profile_id)

        report_run_response = self.client.post(
            "/analysis-runs",
            json={
                "run_type": "report_generation",
                "product_profile_id": product_profile_id,
                "lead_analysis_result_id": lead_analysis_result_id,
                "trigger_source": "android_report",
            },
        )
        self.assertEqual(report_run_response.status_code, 200)
        report_run_id = report_run_response.json()["agent_run"]["id"]

        run_detail_response = self.client.get(f"/analysis-runs/{report_run_id}")
        self.assertEqual(run_detail_response.status_code, 200)
        run_payload = run_detail_response.json()
        self.assertEqual(run_payload["agent_run"]["status"], "succeeded")
        report_id = run_payload["agent_run"]["output_refs"][0]["object_id"]

        report_response = self.client.get(f"/reports/{report_id}")
        self.assertEqual(report_response.status_code, 200)
        report_payload = report_response.json()["report"]
        self.assertEqual(report_payload["id"], report_id)
        self.assertEqual(report_payload["status"], "published")
        self.assertGreaterEqual(len(report_payload["sections"]), 1)
        self.assertIn("下一步建议", [section["title"] for section in report_payload["sections"]])

    def test_history_empty_and_populated(self) -> None:
        empty_history_response = self.client.get("/history")
        self.assertEqual(empty_history_response.status_code, 200)
        empty_payload = empty_history_response.json()
        self.assertIsNone(empty_payload["current_run"])
        self.assertIsNone(empty_payload["latest_product_profile"])
        self.assertEqual(empty_payload["recent_items"], [])

        product_profile_id = self._create_product_profile()
        self._confirm_product_profile(product_profile_id)
        lead_analysis_result_id = self._run_lead_analysis(product_profile_id)
        self._run_report_generation(product_profile_id, lead_analysis_result_id)

        history_response = self.client.get("/history")
        self.assertEqual(history_response.status_code, 200)
        payload = history_response.json()
        self.assertIsNotNone(payload["latest_product_profile"])
        self.assertIn(
            payload["latest_product_profile"]["learning_stage"],
            ["ready_for_confirmation", "confirmed"],
        )
        self.assertIsNotNone(payload["latest_analysis_result"])
        self.assertIsNotNone(payload["latest_report"])
        self.assertGreaterEqual(len(payload["recent_items"]), 3)

    def test_invalid_requests_return_4xx(self) -> None:
        product_profile_id = self._create_product_profile()

        invalid_run_type_response = self.client.post(
            "/analysis-runs",
            json={
                "run_type": "invalid_type",
                "product_profile_id": product_profile_id,
                "lead_analysis_result_id": None,
                "trigger_source": "android_home",
            },
        )
        self.assertEqual(invalid_run_type_response.status_code, 422)

        missing_input_response = self.client.post(
            "/analysis-runs",
            json={
                "run_type": "report_generation",
                "product_profile_id": product_profile_id,
                "lead_analysis_result_id": None,
                "trigger_source": "android_report",
            },
        )
        self.assertEqual(missing_input_response.status_code, 422)

        missing_object_response = self.client.post(
            "/analysis-runs",
            json={
                "run_type": "report_generation",
                "product_profile_id": product_profile_id,
                "lead_analysis_result_id": "lar_missing",
                "trigger_source": "android_report",
            },
        )
        self.assertEqual(missing_object_response.status_code, 404)

    def _create_product_profile(self) -> str:
        response = self.client.post(
            "/product-profiles",
            json={
                "name": "AI 销售助手 V1",
                "one_line_description": "帮助用户先讲清产品，再生成获客分析结果。",
                "source_notes": "用于集成测试。",
            },
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["product_profile"]["id"]

    def _confirm_product_profile(self, product_profile_id: str) -> None:
        response = self.client.post(f"/product-profiles/{product_profile_id}/confirm")
        self.assertEqual(response.status_code, 200)

    def _run_lead_analysis(self, product_profile_id: str) -> str:
        response = self.client.post(
            "/analysis-runs",
            json={
                "run_type": "lead_analysis",
                "product_profile_id": product_profile_id,
                "lead_analysis_result_id": None,
                "trigger_source": "android_home",
            },
        )
        self.assertEqual(response.status_code, 200)
        run_id = response.json()["agent_run"]["id"]
        detail_response = self.client.get(f"/analysis-runs/{run_id}")
        self.assertEqual(detail_response.status_code, 200)
        return detail_response.json()["agent_run"]["output_refs"][0]["object_id"]

    def _run_report_generation(
        self,
        product_profile_id: str,
        lead_analysis_result_id: str,
    ) -> str:
        response = self.client.post(
            "/analysis-runs",
            json={
                "run_type": "report_generation",
                "product_profile_id": product_profile_id,
                "lead_analysis_result_id": lead_analysis_result_id,
                "trigger_source": "android_report",
            },
        )
        self.assertEqual(response.status_code, 200)
        run_id = response.json()["agent_run"]["id"]
        detail_response = self.client.get(f"/analysis-runs/{run_id}")
        self.assertEqual(detail_response.status_code, 200)
        return detail_response.json()["agent_run"]["output_refs"][0]["object_id"]


if __name__ == "__main__":
    unittest.main()
