from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from uuid import uuid4

from backend.api import models
from backend.runtime.graphs.lead_analysis import invoke_lead_analysis_graph
from backend.runtime.graphs.product_learning import invoke_product_learning_graph
from backend.runtime.graphs.report_generation import invoke_report_generation_graph
from backend.runtime.types import (
    AnalysisReportDraft,
    LeadAnalysisDraft,
    LeadAnalysisResultRuntimePayload,
    ProductLearningDraft,
    ProductProfileRuntimePayload,
)


class RuntimeProvider(ABC):
    provider_name: str

    @abstractmethod
    def runtime_metadata(
        self,
        run_type: str,
        *,
        round_index: int = 0,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def generate_lead_analysis_draft(
        self,
        profile: models.ProductProfile,
        *,
        run_id: str,
    ) -> LeadAnalysisDraft:
        raise NotImplementedError

    @abstractmethod
    def generate_report_draft(
        self,
        profile: models.ProductProfile,
        analysis_result: models.LeadAnalysisResult,
        *,
        run_id: str,
    ) -> AnalysisReportDraft:
        raise NotImplementedError

    @abstractmethod
    def generate_product_learning_draft(
        self,
        profile: models.ProductProfile,
        *,
        run_id: str,
    ) -> ProductLearningDraft:
        raise NotImplementedError


class LangGraphRuntimeProvider(RuntimeProvider):
    provider_name = "langgraph"

    def runtime_metadata(
        self,
        run_type: str,
        *,
        round_index: int = 0,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        graph_name = {
            "product_learning": "product_learning_graph",
            "lead_analysis": "lead_analysis_graph",
            "report_generation": "report_generation_graph",
        }.get(run_type, "unknown_graph")
        return {
            "provider": self.provider_name,
            "mode": "backend_direct_langgraph",
            "phase": "product_learning_followup"
            if run_type == "product_learning"
            else "phase1",
            "graph_name": graph_name,
            "run_type": run_type,
            "trace_id": trace_id or uuid4().hex,
            "prompt_version": "heuristic_v1",
            "round_index": round_index,
        }

    def generate_lead_analysis_draft(
        self,
        profile: models.ProductProfile,
        *,
        run_id: str,
    ) -> LeadAnalysisDraft:
        return invoke_lead_analysis_graph(
            run_id=run_id,
            product_profile_payload=ProductProfileRuntimePayload.from_model(profile),
        )

    def generate_report_draft(
        self,
        profile: models.ProductProfile,
        analysis_result: models.LeadAnalysisResult,
        *,
        run_id: str,
    ) -> AnalysisReportDraft:
        return invoke_report_generation_graph(
            run_id=run_id,
            product_profile_payload=ProductProfileRuntimePayload.from_model(profile),
            lead_analysis_result_payload=LeadAnalysisResultRuntimePayload.from_model(
                analysis_result
            ),
        )

    def generate_product_learning_draft(
        self,
        profile: models.ProductProfile,
        *,
        run_id: str,
    ) -> ProductLearningDraft:
        return invoke_product_learning_graph(
            run_id=run_id,
            product_profile_payload=ProductProfileRuntimePayload.from_model(profile),
        )


def get_runtime_provider() -> RuntimeProvider:
    return LangGraphRuntimeProvider()
