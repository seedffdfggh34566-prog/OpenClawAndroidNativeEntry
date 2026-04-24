from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from time import perf_counter
from uuid import uuid4

from fastapi import BackgroundTasks, Depends, FastAPI
from sqlalchemy.orm import Session

from backend.api import serializers, services
from backend.api.config import get_settings
from backend.api.database import get_db_session, init_db
from backend.api.logging_utils import (
    configure_logging,
    reset_request_context,
    set_request_context,
)
from backend.api.schemas import (
    AnalysisRunCreateRequest,
    AnalysisRunCreateResponse,
    AnalysisRunDetailResponse,
    HistoryResponse,
    LeadAnalysisResultDetailResponse,
    ProductProfileCreateRequest,
    ProductProfileCreateResponse,
    ProductProfileDetailResponse,
    ReportDetailResponse,
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        init_db()
        yield

    init_db()
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

    @app.middleware("http")
    async def request_logging_middleware(request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid4().hex
        token = set_request_context(request_id)
        started_at = perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:  # noqa: BLE001
            duration_ms = round((perf_counter() - started_at) * 1000, 3)
            logger.exception(
                "request.failed",
                extra={
                    "event": "request.failed",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status": "failed",
                    "duration_ms": duration_ms,
                    "error": str(exc),
                },
            )
            reset_request_context(token)
            raise

        duration_ms = round((perf_counter() - started_at) * 1000, 3)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request.completed",
            extra={
                "event": "request.completed",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": "succeeded",
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        reset_request_context(token)
        return response

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/product-profiles", response_model=ProductProfileCreateResponse)
    def create_product_profile(
        payload: ProductProfileCreateRequest,
        session: Session = Depends(get_db_session),
    ) -> ProductProfileCreateResponse:
        product_profile = services.create_product_profile(session, payload)
        return ProductProfileCreateResponse(
            product_profile=serializers.product_profile_summary(product_profile),
            current_run=None,
            links={"self": f"/product-profiles/{product_profile.id}"},
        )

    @app.get("/product-profiles/{product_profile_id}", response_model=ProductProfileDetailResponse)
    def get_product_profile(
        product_profile_id: str,
        session: Session = Depends(get_db_session),
    ) -> ProductProfileDetailResponse:
        product_profile = services.get_product_profile_or_404(session, product_profile_id)
        return ProductProfileDetailResponse(
            product_profile=serializers.product_profile_detail(product_profile)
        )

    @app.post("/analysis-runs", response_model=AnalysisRunCreateResponse)
    def create_analysis_run(
        payload: AnalysisRunCreateRequest,
        background_tasks: BackgroundTasks,
        session: Session = Depends(get_db_session),
    ) -> AnalysisRunCreateResponse:
        agent_run = services.create_analysis_run(session, payload)
        background_tasks.add_task(services.process_agent_run, agent_run.id)
        return AnalysisRunCreateResponse(agent_run=serializers.agent_run_payload(agent_run))

    @app.get("/analysis-runs/{run_id}", response_model=AnalysisRunDetailResponse)
    def get_analysis_run(
        run_id: str,
        session: Session = Depends(get_db_session),
    ) -> AnalysisRunDetailResponse:
        agent_run = services.get_agent_run_or_404(session, run_id)
        return AnalysisRunDetailResponse(
            agent_run=serializers.agent_run_payload(agent_run),
            result_summary=services.build_result_summary(session, agent_run),
        )

    @app.get("/reports/{report_id}", response_model=ReportDetailResponse)
    def get_report(
        report_id: str,
        session: Session = Depends(get_db_session),
    ) -> ReportDetailResponse:
        report = services.get_report_or_404(session, report_id)
        return ReportDetailResponse(report=serializers.report_payload(report))

    @app.get(
        "/lead-analysis-results/{lead_analysis_result_id}",
        response_model=LeadAnalysisResultDetailResponse,
    )
    def get_lead_analysis_result(
        lead_analysis_result_id: str,
        session: Session = Depends(get_db_session),
    ) -> LeadAnalysisResultDetailResponse:
        lead_analysis_result = services.get_lead_analysis_result_or_404(
            session, lead_analysis_result_id
        )
        return LeadAnalysisResultDetailResponse(
            lead_analysis_result=serializers.lead_analysis_result_detail(lead_analysis_result)
        )

    @app.get("/history", response_model=HistoryResponse)
    def get_history(
        session: Session = Depends(get_db_session),
    ) -> HistoryResponse:
        return services.build_history(session)

    return app


app = create_app()
