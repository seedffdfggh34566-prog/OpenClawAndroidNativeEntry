from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from time import perf_counter
from uuid import uuid4

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from backend.api import serializers, services
from backend.api.config import get_settings
from backend.api.database import get_db_session, init_db
from backend.api.logging_utils import (
    configure_logging,
    reset_request_context,
    set_request_context,
)
from backend.api.sales_workspace import (
    create_chat_trace_store,
    create_draft_review_store,
    create_sales_workspace_store,
    router as sales_workspace_router,
)
from backend.api.schemas import (
    AnalysisRunCreateRequest,
    AnalysisRunCreateResponse,
    AnalysisRunDetailResponse,
    HistoryResponse,
    LeadAnalysisResultDetailResponse,
    ProductProfileConfirmResponse,
    ProductProfileCreateRequest,
    ProductProfileCreateResponse,
    ProductProfileDetailResponse,
    ProductProfileEnrichRequest,
    ProductProfileEnrichResponse,
    ReportDetailResponse,
)
from backend.runtime.llm_trace import get_llm_trace, list_llm_trace_summaries

logger = logging.getLogger(__name__)


def _dev_llm_inspector_html() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OpenClaw LLM Run Inspector</title>
  <style>
    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 24px; color: #1f2937; background: #f8fafc; }
    main { display: grid; grid-template-columns: minmax(280px, 420px) minmax(0, 1fr); gap: 16px; }
    button { display: block; width: 100%; padding: 10px 12px; margin: 0 0 8px; text-align: left; border: 1px solid #cbd5e1; background: #fff; border-radius: 6px; cursor: pointer; }
    button:hover { border-color: #2563eb; }
    pre { padding: 16px; overflow: auto; background: #0f172a; color: #e2e8f0; border-radius: 6px; white-space: pre-wrap; word-break: break-word; }
    .meta { color: #64748b; font-size: 13px; margin: 4px 0 0; }
    .toolbar { margin-bottom: 16px; display: flex; gap: 8px; align-items: center; }
    .toolbar button { width: auto; margin: 0; }
    .detail-grid { display: grid; gap: 14px; }
    .panel { background: #fff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 14px; }
    .panel h3 { margin: 0 0 10px; font-size: 18px; }
    .kv { display: grid; grid-template-columns: 150px minmax(0, 1fr); gap: 6px 12px; font-size: 14px; }
    .kv div:nth-child(odd) { color: #64748b; }
    .raw-content { min-height: 360px; max-height: 620px; }
    .json-content { max-height: 360px; }
  </style>
</head>
<body>
  <h1>OpenClaw LLM Run Inspector</h1>
  <div class="toolbar">
    <button type="button" onclick="loadRuns()">Refresh</button>
    <span class="meta">Dev-only local trace viewer</span>
  </div>
  <main>
    <section>
      <h2>Runs</h2>
      <div id="runs">Loading...</div>
    </section>
    <section>
      <h2>Detail</h2>
      <div id="detail" class="detail-grid">
        <pre>Select a run.</pre>
      </div>
    </section>
  </main>
  <script>
    async function loadRuns() {
      const container = document.getElementById("runs");
      container.textContent = "Loading...";
      const response = await fetch("/dev/llm-runs");
      const payload = await response.json();
      const runs = payload.llm_runs || [];
      if (!runs.length) {
        container.textContent = "No traces found.";
        return;
      }
      container.innerHTML = "";
      for (const run of runs) {
        const button = document.createElement("button");
        const tokens = run.total_tokens == null ? "-" : run.total_tokens;
        button.innerHTML = `<strong>${run.run_type}</strong> ${run.run_id}<div class="meta">${run.parse_status} - ${run.model} - ${tokens} tokens - ${run.duration_ms} ms</div>`;
        button.onclick = () => loadDetail(run.run_id);
        container.appendChild(button);
      }
    }

    async function loadDetail(runId) {
      const response = await fetch(`/dev/llm-runs/${encodeURIComponent(runId)}`);
      const payload = await response.json();
      renderDetail(payload);
    }

    function textBlock(value) {
      if (value == null || value === "") {
        return "";
      }
      if (typeof value === "string") {
        return value;
      }
      return JSON.stringify(value, null, 2);
    }

    function appendPanel(container, title, content, className) {
      const panel = document.createElement("section");
      panel.className = "panel";
      const heading = document.createElement("h3");
      heading.textContent = title;
      const pre = document.createElement("pre");
      pre.className = className || "json-content";
      pre.textContent = content || "(empty)";
      panel.appendChild(heading);
      panel.appendChild(pre);
      container.appendChild(panel);
    }

    function renderDetail(payload) {
      const container = document.getElementById("detail");
      container.innerHTML = "";

      const summary = document.createElement("section");
      summary.className = "panel";
      const heading = document.createElement("h3");
      heading.textContent = "Summary";
      const kv = document.createElement("div");
      kv.className = "kv";
      const fields = [
        ["run_id", payload.run_id],
        ["run_type", payload.run_type],
        ["parse_status", payload.parse_status],
        ["error_type", payload.error_type || "-"],
        ["provider", payload.provider],
        ["model", payload.model],
        ["prompt_version", payload.prompt_version],
        ["duration_ms", payload.duration_ms],
        ["started_at", payload.started_at],
        ["ended_at", payload.ended_at],
      ];
      for (const [label, value] of fields) {
        const key = document.createElement("div");
        key.textContent = label;
        const val = document.createElement("div");
        val.textContent = value == null ? "-" : String(value);
        kv.appendChild(key);
        kv.appendChild(val);
      }
      summary.appendChild(heading);
      summary.appendChild(kv);
      container.appendChild(summary);

      appendPanel(container, "Raw content", textBlock(payload.raw_content), "raw-content");
      appendPanel(container, "Parsed draft", textBlock(payload.parsed_draft), "json-content");
      appendPanel(container, "Usage", textBlock(payload.usage), "json-content");
      appendPanel(container, "Full trace JSON", JSON.stringify(payload, null, 2), "json-content");
    }

    loadRuns();
  </script>
</body>
</html>"""


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        init_db()
        yield

    init_db()
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    app.state.sales_workspace_store = create_sales_workspace_store()
    app.state.sales_workspace_draft_review_store = create_draft_review_store()
    app.state.sales_workspace_chat_trace_store = create_chat_trace_store()
    app.include_router(sales_workspace_router)

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
        background_tasks: BackgroundTasks,
        session: Session = Depends(get_db_session),
    ) -> ProductProfileCreateResponse:
        created = services.create_product_profile(session, payload)
        background_tasks.add_task(services.process_agent_run, created.current_run.id)
        return ProductProfileCreateResponse(
            product_profile=serializers.product_profile_summary(created.product_profile),
            current_run=serializers.agent_run_payload(created.current_run),
            links={"self": f"/product-profiles/{created.product_profile.id}"},
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

    @app.post(
        "/product-profiles/{product_profile_id}/enrich",
        response_model=ProductProfileEnrichResponse,
    )
    def enrich_product_profile(
        product_profile_id: str,
        payload: ProductProfileEnrichRequest,
        background_tasks: BackgroundTasks,
        session: Session = Depends(get_db_session),
    ) -> ProductProfileEnrichResponse:
        agent_run = services.enrich_product_profile(session, product_profile_id, payload)
        background_tasks.add_task(services.process_agent_run, agent_run.id)
        return ProductProfileEnrichResponse(agent_run=serializers.agent_run_payload(agent_run))

    @app.post("/product-profiles/{product_profile_id}/confirm", response_model=ProductProfileConfirmResponse)
    def confirm_product_profile(
        product_profile_id: str,
        session: Session = Depends(get_db_session),
    ) -> ProductProfileConfirmResponse:
        product_profile = services.confirm_product_profile(session, product_profile_id)
        return ProductProfileConfirmResponse(
            product_profile=serializers.product_profile_summary(product_profile)
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

    def require_dev_llm_trace_enabled():
        request_settings = get_settings()
        if not request_settings.dev_llm_trace_enabled:
            raise HTTPException(status_code=404, detail="dev_llm_trace_not_enabled")
        return request_settings

    @app.get("/dev/llm-runs")
    def list_dev_llm_runs() -> dict[str, object]:
        request_settings = require_dev_llm_trace_enabled()
        return {"llm_runs": list_llm_trace_summaries(request_settings)}

    @app.get("/dev/llm-runs/{run_id}")
    def get_dev_llm_run(run_id: str) -> dict[str, object]:
        request_settings = require_dev_llm_trace_enabled()
        trace = get_llm_trace(request_settings, run_id)
        if trace is None:
            raise HTTPException(status_code=404, detail="llm_trace_not_found")
        return trace

    @app.get("/dev/llm-inspector", response_class=HTMLResponse)
    def get_dev_llm_inspector() -> HTMLResponse:
        require_dev_llm_trace_enabled()
        return HTMLResponse(_dev_llm_inspector_html())

    return app


app = create_app()
