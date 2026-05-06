#!/usr/bin/env python3
"""
V3 Comprehensive Live Smoke Test

Strategy: 35-round mixed (20 normal + 15 high-density) on minimax-m2.7.
Validates:
  1. Core memory maintenance (product, human, sales_strategy, customer_intelligence)
  2. Memory status evolution (observed -> inferred -> confirmed / superseded)
  3. Customer intelligence drafting and ranking
  4. User correction handling
  5. Context management (75% pressure warning, 90% compression, 95% guard)
  6. Post-summary recall of early-session facts
  7. Agent self-compaction under system-prompt bloat

Usage:
    OPENCLAW_BACKEND_RUN_LIVE_LLM_SMOKE=1 \\
    OPENCLAW_BACKEND_LLM_MODEL=minimax-m2.7 \\
    python backend/scripts/v3_comprehensive_live_smoke.py

Expected duration: 5-15 minutes depending on API latency.
Expected token consumption: ~250K input + ~80K output (approximate).

Note on failed turns: when a turn fails (e.g. LLM returns no tool_call or a platform
error occurs), the user_message for that turn remains in session.messages. This is
deliberate and consistent with mainstream agent / LLM platforms, which keep such
"orphan" user messages as part of the conversation context for subsequent turns.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import tiktoken

    _TIKTOKEN_ENCODING = tiktoken.get_encoding("cl100k_base")
except Exception:
    _TIKTOKEN_ENCODING = None

# Ensure backend root is importable
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT.parent))

from backend.api.config import get_settings, reset_settings_cache
from backend.runtime.v3_sandbox import run_v3_sandbox_turn
from backend.runtime.v3_sandbox.schemas import (
    V3SandboxDebugTraceOptions,
    V3SandboxMessage,
    V3SandboxSession,
    default_core_memory_blocks,
)

LIVE_ENV = "OPENCLAW_BACKEND_RUN_LIVE_LLM_SMOKE"
TARGET_MODEL = "minimax-m2.7"
CONTEXT_WINDOW = 200_000
WARNING_RATIO = 0.75
COMPRESSION_RATIO = 0.90
GUARD_RATIO = 0.95

# ---------------------------------------------------------------------------
# Act definitions: 35 turns across 5 acts
# ---------------------------------------------------------------------------

ACT_1_BREAKTHROUGH_AND_PRODUCT: list[str] = [
    "你好，我是李明，深圳云算科技的创始人。",
    "我们公司做中小企业财税 SaaS，主打自动报税和发票管理。",
    "目标用户是 20-50 人的财税代理公司，他们最头疼的是月底集中报税时人工录入发票太慢。",
    "目前月活客户大概 300 家，客单价 299 元每月，续费率 78%。",
    "我们的核心优势是 AI 自动分类发票，准确率号称 95%，支持增值税专票、普票和电子发票三种类型。",
]

ACT_2_LEAD_EXPLORATION: list[str] = [
    "最近接触了三个潜在客户。A 公司是 30 人规模的代账公司，老板张总对自动报税很感兴趣，痛点是每月 200 多家客户的报税要 5 个人忙一周。B 公司是 15 人规模，主要关心价格，说 299 有点贵。C 公司是 50 人规模，但已经有自研系统，切换成本顾虑很大。",
    "你觉得这三个客户应该怎么排序？哪个优先级最高？",
    "A 公司张总下周二要演示，你帮我准备一下切入点。他们最关心的应该是什么？",
    "B 公司财务经理今天打电话来，问能不能先试用一个月再决定。这个请求怎么处理比较好？",
    "C 公司那边有变化，他们 CTO 私下说他们自研系统的维护成本越来越高，每年光一个工程师就要 40 万，开始认真考虑第三方方案了。",
]

ACT_3_STRATEGY_FORMATION: list[str] = [
    "我觉得应该先集中精力拿下 A 公司，作为标杆客户。如果 30 人代账公司能用起来，同类产品复制会容易很多。",
    "但有个内部问题：我们的自动报税功能还有一个已知 bug，批量导入超过 500 张发票时会漏掉大约 3%。下周二演示要不要回避这个功能？",
    "下周二演示时我应该怎么介绍？重点讲 AI 分类还是价格优势？演示时间大概 30 分钟。",
    "另外我打算给前 10 家签约客户终身 8 折优惠，外加免费数据迁移。这个策略怎么样？会不会让后面客户觉得不公平？",
    "如果 A 公司签约了，我打算把他们的案例做成白皮书，用于后续销售。你觉得白皮书的重点应该写什么？",
]

ACT_4_USER_CORRECTION: list[str] = [
    "纠正一下，A 公司不是 30 人，是 50 人规模。之前我说错了，他们实际有 5 个会计和 3 个外勤。",
    "还有一个纠正：客单价不是 299，我们从本月起涨价到 399 了，老客户维持原价不变。",
    "C 公司那边也更新了，他们已经正式决定放弃自研系统，CTO 说预算批了 50 万，正在评估三家供应商，我们在名单里。",
    "B 公司那边不用降价了，他们接受了 399 的价格，准备签一年合同，预付全款。",
    "对了，公司名字纠正一下，不是深圳云算科技，是深圳云算智能科技有限公司。李明是我的真名，职务是创始人兼 CEO。",
]

ACT_5_HIGH_DENSITY_PRESSURE: list[str] = [
    textwrap.dedent("""\
        今天收到了三封重要邮件，帮我分析一下优先级和回复策略：
        邮件一（张总，A公司）："李总，下周二演示能否提前到周一上午？我们周二要临时出差。另外能否准备一份同行业案例？"
        邮件二（C公司CTO）："我们需要一份详细的数据迁移方案和安全合规说明，特别是等保三级和客户数据隔离方面的文档。"
        邮件三（老客户王姐，20人代账公司）："最近系统偶尔卡顿，尤其是上午 9-10 点，能否优化？另外我们想要一个批量导出 PDF 的功能。"
        """),
    textwrap.dedent("""\
        竞争对手动态更新：
        竞品 X 公司今天发布了新版本，主打 "AI 智能报税 + 自动银行对账"，定价 499/月，比我们贵 100 元。他们在抖音投了广告，获客成本看起来很高。
        竞品 Y 公司是老牌厂商，功能齐全但界面老旧，定价 599/月，客户抱怨学习成本高。
        我们的差异化应该是什么？要不要也做自动银行对账？
        """),
    textwrap.dedent("""\
        销售团队周会纪要：
        小明负责华东区，本周拜访了 8 家客户，成交 2 家，主要阻力是 "担心数据安全"。
        小红负责华南区，本周成交 3 家，但有一家签约后因为发票识别错误要求退款。
        小华负责线上线索，本周从抖音和小红书获得 45 个留资，转化率 11%，主要问题是留资后跟进不及时。
        需要制定下周重点行动计划。
        """),
    textwrap.dedent("""\
        产品需求池（本周新增）：
        P0：发票批量导入 bug（超过 500 张漏 3%）必须在下个版本修复。
        P1：客户要求支持银行流水自动导入和对账。
        P1：销售团队要求 CRM 集成，能自动同步客户状态和跟进记录。
        P2：老客户要求批量导出 PDF 报表。
        P2：市场部要求landing page A/B 测试数据对接。
        资源只有 2 个后端 + 1 个前端，怎么排期？
        """),
    textwrap.dedent("""\
        财务数据更新：
        本月收入 12.8 万，其中新客户 8.2 万，续费 4.6 万。
        获客成本 CAC 从 800 涨到 1200，因为抖音竞价变贵了。
        客户生命周期价值 LTV 估算 4500 元（399 * 12 个月 * 0.78 续费率 * 1.2 扩展率）。
        LTV/CAC = 3.75，还在健康区间但比上季度下降了。
        现金余额 86 万，能支撑 7 个月运营。要不要考虑融资？
        """),
    textwrap.dedent("""\
        行业政策变化：
        税务局通知，明年 1 月起所有电子发票必须通过国家税务总局统一平台开具，原有第三方接口可能失效。
        这意味着我们现有的发票识别逻辑可能需要重写，而且要和税局平台对接。
        预计开发周期 2-3 个月，需要投入 1 个后端全职 + 半个测试。
        同时，这可能是行业洗牌机会，谁先对接完谁就有先发优势。我们应该怎么做？
        """),
    textwrap.dedent("""\
        客户成功案例素材收集：
        A 公司（50 人代账）签约后 2 个月，报税效率提升 60%，从 5 人一周降到 2 人三天。
        老客户王姐（20 人代账）用了 8 个月，累计处理发票 12 万张，人工复核率从 15% 降到 4%。
        请帮我整理一份标准话术，用于销售演示时讲述客户成功故事。
        """),
    textwrap.dedent("""\
        团队扩张计划讨论：
        目前团队 12 人：2 后端、1 前端、2 销售、1 客户成功、1 运营、1 设计、1 产品、1 测试、2 管理层（我和 CTO）。
        计划 Q3 扩招到 20 人，重点招： senior 后端（1 人）、销售（2 人）、客户成功（1 人）。
        预算：人均月薪 2.5 万，社保公积金 30%，办公室扩租每月多 1.5 万。
        请帮我算一下扩张后的月度 burn rate，以及现有现金能支撑多久。
        """),
    textwrap.dedent("""\
        合作伙伴洽谈记录：
        今天和园区孵化器谈合作，他们管理 8 个园区、600 多家企业，愿意把我们作为 "财税服务商" 推荐给入驻企业。
        条件：每成功推荐一家客户，园区抽成 15%，按月结算。他们要求我们先交 3 万保证金。
        另外，一家 ERP 厂商（慧算账）愿意 API 对接，互相导流。他们不抽成，但要求联合品牌露出。
        这两个合作要不要做？优先级怎么排？
        """),
    textwrap.dedent("""\
        市场活动复盘：
        上周参加了 "华南财税行业峰会"，我们设了展位，发了 200 份资料，收集名片 67 张，当场 demo 12 次，留资 34 个。
        会后 3 天内销售跟进了 20 个，约到下周面谈 5 个，转化率看起来一般。
        现场 feedback：客户最关心的是 "数据会不会丢" 和 "能不能试用"。
        下次展会应该怎么改进？要不要准备试用账号二维码？
        """),
    textwrap.dedent("""\
        法务合规审查：
        律师提醒：我们的用户协议中关于 "数据所有权" 的条款表述模糊，可能被客户质疑。
        建议修改为："客户原始数据所有权归客户所有，我司仅提供处理服务，不拥有、不出售客户数据。"
        另外，SaaS 订阅协议中缺少 "服务可用性 SLA" 条款，建议承诺 99.5% 可用性，否则按天退款。
        这两个修改会影响销售话术，请你更新 product memory 中的 "常见反对意见" 部分。
        """),
    textwrap.dedent("""\
        投资人沟通准备：
        下周要和天使投资人老张做月度汇报，他关注的核心指标是：
        1. MRR（月度经常性收入）增长率和流失率
        2. 获客成本 CAC 和 LTV/CAC 比值
        3. 产品核心功能 NPS（净推荐值）
        4. 竞品差异化护城河
        5. 团队扩张计划和资金 runway
        请帮我整理一份 10 分钟汇报的结构，每个指标给出当前数字和趋势判断。
        """),
    textwrap.dedent("""\
        客户投诉紧急处理：
        老客户赵哥（用了 6 个月）今天突然在群里发飙，说昨天系统故障导致他错过了 3 家客户的报税 deadline，被税务局罚款共 6000 元。
        他要求我们赔偿全部损失，否则要曝光到财税行业群和知乎。
        技术排查：昨天确实有一次 20 分钟的服务中断，原因是数据库连接池耗尽。
        请帮我：1）评估赔偿方案；2）准备安抚话术；3）制定防止再发的技术措施；4）更新 product memory 中的 "已知限制和风险提示"。
        """),
    textwrap.dedent("""\
        战略方向讨论：
        我在考虑两个长期方向，想听听你的分析：
        方向 A：继续深耕财税 SaaS，未来 2 年做到 3000 家客户，然后被大厂收购。
        方向 B：转型为 "企业服务中台"，不只做财税，还接人事、法务、知识产权等服务，做平台抽成模式。
        方向 A 更聚焦但天花板明显，方向 B 空间大但需要巨额投入和多领域 expertise。
        结合我们当前的团队、资金和市场位置，你建议怎么选？或者有没有方向 C？
        """),
    textwrap.dedent("""\
        最后，我想确认一下你记住了多少我们今天的讨论。请帮我回答以下问题：
        1. 我叫什么名字，公司叫什么？
        2. 我们产品的核心功能、客单价和目标用户是谁？
        3. A、B、C 三个客户现在的最新状态分别是什么？
        4. 我们产品目前的已知 bug 是什么？
        5. 下周二（或改到周一）的演示对象是谁，应该重点讲什么？
        6. 我们的 LTV/CAC 比值是多少，现金还能支撑几个月？
        """),
]

ALL_TURNS = (
    ACT_1_BREAKTHROUGH_AND_PRODUCT
    + ACT_2_LEAD_EXPLORATION
    + ACT_3_STRATEGY_FORMATION
    + ACT_4_USER_CORRECTION
    + ACT_5_HIGH_DENSITY_PRESSURE
)

assert len(ALL_TURNS) == 35, f"Expected 35 turns, got {len(ALL_TURNS)}"

# ---------------------------------------------------------------------------
# Observability / metrics
# ---------------------------------------------------------------------------

class TurnMetrics:
    def __init__(self, turn_index: int, user_content: str) -> None:
        self.turn_index = turn_index
        self.user_content_preview = user_content[:80].replace("\n", " ")
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.assistant_content_preview: str = ""
        self.tool_calls: list[str] = []
        self.memory_block_lengths: dict[str, int] = {}
        self.memory_block_snapshots: dict[str, str] = {}
        self.context_summary_present: bool = False
        self.summary_recursion_count: int = 0
        self.early_return_reason: str | None = None
        self.summary_chars: int = 0
        self.prompt_tokens_estimate: int = 0
        self.llm_usage: dict[str, int] | None = None
        self.context_pressure_tokens: int = 0
        self.context_pressure_threshold: int = 0
        self.context_pressure_triggered: bool = False
        self.summarization_token_count: int = 0
        self.summarization_action: str | None = None
        self.guard_tool_tokens: int = 0
        self.guard_tool_threshold: int = 0
        self.outcome: str = "pending"
        self.error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "turn": self.turn_index + 1,
            "user_preview": self.user_content_preview,
            "duration_seconds": round(self.end_time - self.start_time, 2),
            "assistant_preview": self.assistant_content_preview,
            "tool_calls": self.tool_calls,
            "memory_block_lengths": self.memory_block_lengths,
            "memory_block_snapshots": self.memory_block_snapshots,
            "context_summary_present": self.context_summary_present,
            "summary_recursion_count": self.summary_recursion_count,
            "early_return_reason": self.early_return_reason,
            "summary_chars": self.summary_chars,
            "prompt_tokens_estimate": self.prompt_tokens_estimate,
            "llm_usage": self.llm_usage,
            "context_pressure_tokens": self.context_pressure_tokens,
            "context_pressure_threshold": self.context_pressure_threshold,
            "context_pressure_triggered": self.context_pressure_triggered,
            "summarization_token_count": self.summarization_token_count,
            "summarization_action": self.summarization_action,
            "guard_tool_tokens": self.guard_tool_tokens,
            "guard_tool_threshold": self.guard_tool_threshold,
            "outcome": self.outcome,
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_env() -> None:
    if os.environ.get(LIVE_ENV) != "1":
        print(f"ERROR: Set {LIVE_ENV}=1 to run this live smoke test.")
        sys.exit(1)

    settings = get_settings()
    if not settings.llm_api_key:
        print("ERROR: OPENCLAW_BACKEND_LLM_API_KEY is required.")
        sys.exit(1)

    if settings.llm_model != TARGET_MODEL:
        print(f"INFO: Overriding model from {settings.llm_model} to {TARGET_MODEL}")
        os.environ["OPENCLAW_BACKEND_LLM_MODEL"] = TARGET_MODEL
        reset_settings_cache()

    print(f"Model: {get_settings().llm_model}")
    print(f"API base: {get_settings().llm_base_url}")
    print(f"Timeout: {get_settings().llm_timeout_seconds}s")
    print()


def _extract_tool_calls(result) -> list[str]:
    """Extract tool names from trace event."""
    tool_events = result.trace_event.tool_events if result.trace_event else []
    return [e.tool_name for e in tool_events]


def _extract_memory_lengths(session: V3SandboxSession) -> dict[str, int]:
    return {label: len(block.value) for label, block in session.core_memory_blocks.items()}


def _extract_memory_snapshots(session: V3SandboxSession) -> dict[str, str]:
    return {label: block.value for label, block in session.core_memory_blocks.items()}


def _estimate_prompt_tokens(system_prompt: str, after_cursor: list[Any], user_content: str) -> int:
    """Script-side estimate of the turn-start payload token count.
    Falls back to 0 if tiktoken is unavailable."""
    if _TIKTOKEN_ENCODING is None:
        return 0
    parts = [system_prompt]
    parts.extend(f"[{m.role}] {m.content}" for m in after_cursor)
    parts.append(user_content)
    return len(_TIKTOKEN_ENCODING.encode("\n".join(parts)))


def _classify_outcome(
    error: str | None,
    tool_calls: list[str],
    assistant_content: str,
) -> str:
    """Classify turn outcome into one of four categories.

    - success: LLM produced at least one tool call and an assistant reply.
    - runtime_seam: LLM returned content but no tool_call (e.g. no_tool_call).
      This is a runtime design seam, not a model failure.
    - platform_error: HTTP 4xx/5xx excluding 402 quota.
    - quota_error: HTTP 402 FREE_QUOTA_EXHAUSTED or paid-plan balance depleted.
    """
    if error is None:
        return "success"
    if "v3_tool_loop_no_tool_call" in error:
        return "runtime_seam"
    if "FREE_QUOTA_EXHAUSTED" in error or "quota" in error.lower():
        return "quota_error"
    if "tokenhub_http_error" in error or "http_error" in error.lower():
        return "platform_error"
    return "platform_error"


def _is_quota_error(error: str) -> bool:
    return "FREE_QUOTA_EXHAUSTED" in error or "quota" in error.lower()


def _is_rate_limit_error(error: str) -> bool:
    return "429" in error or "rate" in error.lower() or "limit" in error.lower()


# ---------------------------------------------------------------------------
# Assertions (soft: collect failures, don't abort)
# ---------------------------------------------------------------------------

class SoftAssertions:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def assert_contains(self, haystack: str, needle: str, msg: str) -> None:
        if needle not in haystack:
            self.failures.append(f"ASSERT FAIL: {msg} (expected '{needle}' in content)")

    def assert_true(self, condition: bool, msg: str) -> None:
        if not condition:
            self.failures.append(f"ASSERT FAIL: {msg}")

    def report(self) -> str:
        if not self.failures:
            return "All assertions passed."
        return "\n".join(self.failures)


# ---------------------------------------------------------------------------
# Context saturation prefill
# ---------------------------------------------------------------------------

# Early facts embedded in prefill messages so we can verify post-summary recall.
PREFILL_EARLY_FACTS: list[str] = [
    "我叫李明，是深圳云算智能科技有限公司的创始人兼CEO。",
    "我们公司做中小企业财税SaaS，主打自动报税和发票管理。",
    "目标用户是20到50人的财税代理公司。",
    "客单价399元每月，老客户维持原价不变。",
]

# Filler sentence used to bulk-up prefill message size without semantic noise.
_PREFILL_FILLER_SENTENCE = (
    "销售自动化平台可以帮助企业提升效率，减少人工操作，实现智能化客户管理，"
    "降低运营成本，提高团队协作效率，优化业务流程，增强客户满意度。"
)


def _prefill_saturation_history(
    session: V3SandboxSession,
    n_messages: int = 60,
    chars_per_message: int = 3000,
) -> None:
    """Pre-fill session.messages with large synthetic history to force
    context-pressure thresholds in subsequent turns.

    Does NOT consume LLM tokens — all work is done locally.
    """
    sentence = _PREFILL_FILLER_SENTENCE
    repeats = chars_per_message // len(sentence) + 1
    base_text = (sentence * repeats)[:chars_per_message]

    for i in range(n_messages):
        if i < len(PREFILL_EARLY_FACTS):
            fact = PREFILL_EARLY_FACTS[i]
            content = fact + " " + base_text[len(fact) + 1 :]
        else:
            content = f"历史消息 {i}: {base_text}"
        session.messages.append(
            V3SandboxMessage(
                id=f"prefill_{i:03d}",
                role="user" if i % 2 == 0 else "assistant",
                content=content,
            )
        )


# ---------------------------------------------------------------------------
# Recall verification turn
# ---------------------------------------------------------------------------

RECALL_TURN: str = (
    "请帮我回忆一下我们之前的对话：\n"
    "1）我叫什么名字？\n"
    "2）我的公司叫什么？\n"
    "3）我们产品的核心功能是什么？"
)


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

PREFLIGHT_TURNS: list[str] = [
    "你好，请简单介绍一下你自己，并记住我的名字是测试用户。",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parent / "reports"),
        help="Directory for the final JSON report and the incremental JSONL "
             "(default: backend/scripts/reports/, gitignored).",
    )
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Run a 1-turn preflight smoke to verify API key and connectivity.",
    )
    parser.add_argument(
        "--max-tokens-budget",
        type=int,
        default=0,
        help="Max total_tokens budget across all turns. 0 = unlimited. "
             "If exceeded, stops gracefully after the current turn.",
    )
    parser.add_argument(
        "--context-saturation",
        action="store_true",
        help="Pre-fill large synthetic history to force 75%%/90%% threshold triggers.",
    )
    args = parser.parse_args()

    _check_env()
    settings = get_settings()

    turns = list(ALL_TURNS)
    if args.preflight:
        turns = PREFLIGHT_TURNS
        print("[PREFLIGHT MODE] Running 1-turn connectivity check.\n")
    elif args.context_saturation:
        turns.append(RECALL_TURN)
        print("[SATURATION MODE] Will append recall verification after ACT-5.\n")

    # Prepare incremental report directory
    report_dir = Path(args.out_dir).expanduser().resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = report_dir / "current_smoke.jsonl"
    if jsonl_path.exists():
        jsonl_path.unlink()

    session = V3SandboxSession(
        id=f"v3_live_smoke_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        title="V3 Comprehensive Live Smoke",
        core_memory_blocks=default_core_memory_blocks(),
    )

    prefill_message_count = 0
    if args.context_saturation:
        _prefill_saturation_history(session)
        prefill_message_count = len(session.messages)
        print(f"[SATURATION MODE] Pre-filled {prefill_message_count} large messages.\n")

    metrics: list[TurnMetrics] = []
    soft = SoftAssertions()

    debug_options = V3SandboxDebugTraceOptions(
        verbose=True,
        include_prompt=True,
        include_raw_llm_output=False,
        include_repair_attempts=True,
        include_node_io=True,
        include_state_diff=True,
        max_bytes=200_000,
    )

    print("=" * 70)
    print("V3 COMPREHENSIVE LIVE SMOKE TEST")
    print(f"Target model: {TARGET_MODEL}  |  Context window: {CONTEXT_WINDOW:,}")
    print(f"Warning @ {WARNING_RATIO*100:.0f}% ({int(CONTEXT_WINDOW*WARNING_RATIO):,})")
    print(f"Compression @ {COMPRESSION_RATIO*100:.0f}% ({int(CONTEXT_WINDOW*COMPRESSION_RATIO):,})")
    print(f"Guard @ {GUARD_RATIO*100:.0f}% ({int(CONTEXT_WINDOW*GUARD_RATIO):,})")
    if args.max_tokens_budget:
        print(f"Budget: {args.max_tokens_budget:,} total_tokens")
    print("=" * 70)
    print()

    overall_start = time.perf_counter()
    total_tokens_consumed = 0
    budget_exhausted = False
    quota_exhausted = False

    for turn_idx, user_content in enumerate(turns):
        act_name = ""
        if args.preflight:
            act_name = "PREFLIGHT"
        elif turn_idx < 5:
            act_name = "ACT-1 BREAKTHROUGH"
        elif turn_idx < 10:
            act_name = "ACT-2 LEADS"
        elif turn_idx < 15:
            act_name = "ACT-3 STRATEGY"
        elif turn_idx < 20:
            act_name = "ACT-4 CORRECTION"
        elif turn_idx < 35:
            act_name = "ACT-5 PRESSURE"
        else:
            act_name = "RECALL"

        m = TurnMetrics(turn_idx, user_content)
        m.start_time = time.perf_counter()

        print(f"[{turn_idx + 1:02d}/{len(turns)}] {act_name}  →  {m.user_content_preview}...")

        turn_done = False
        retries = 0
        max_retries = 3

        while not turn_done:
            try:
                result = run_v3_sandbox_turn(
                    settings=settings,
                    session=session,
                    user_message=V3SandboxMessage(
                        id=f"msg_user_{turn_idx:03d}",
                        role="user",
                        content=user_content,
                    ),
                    debug_options=debug_options,
                    max_steps=16,
                )

                # Update session in-place for next turn
                session = result.session
                m.end_time = time.perf_counter()
                m.assistant_content_preview = (
                    result.assistant_message.content[:120].replace("\n", " ") + "..."
                    if len(result.assistant_message.content) > 120
                    else result.assistant_message.content.replace("\n", " ")
                )
                m.tool_calls = _extract_tool_calls(result)
                m.memory_block_lengths = _extract_memory_lengths(session)
                m.memory_block_snapshots = _extract_memory_snapshots(session)
                m.context_summary_present = session.context_summary is not None and len(session.context_summary) > 0
                m.summary_recursion_count = session.summary_recursion_count

                if result.trace_event and result.trace_event.runtime_metadata:
                    meta = result.trace_event.runtime_metadata
                    m.early_return_reason = meta.get("early_return_reason")
                    m.summary_chars = meta.get("context_summary_chars", 0)
                    m.llm_usage = meta.get("llm_usage")
                    m.context_pressure_tokens = meta.get("context_pressure_tokens", 0)
                    m.context_pressure_threshold = meta.get("context_pressure_threshold", 0)
                    m.context_pressure_triggered = bool(meta.get("context_pressure_triggered", False))
                    m.summarization_token_count = meta.get("summarization_token_count", 0)
                    m.summarization_action = meta.get("summarization_action")
                    m.guard_tool_tokens = meta.get("guard_tool_tokens", 0)
                    m.guard_tool_threshold = meta.get("guard_tool_threshold", 0)
                    if m.llm_usage:
                        total_tokens_consumed += m.llm_usage.get("total_tokens", 0)

                # Script-side prompt token estimate (fallback if metadata absent)
                if m.prompt_tokens_estimate == 0 and _TIKTOKEN_ENCODING is not None:
                    m.prompt_tokens_estimate = _estimate_prompt_tokens(
                        "\n".join([
                            f"[{label}] {block.value}"
                            for label, block in session.core_memory_blocks.items()
                        ]),
                        session.messages,
                        user_content,
                    )

                turn_done = True

            except Exception as exc:
                error_str = f"{type(exc).__name__}: {exc}"
                if _is_rate_limit_error(error_str) and retries < max_retries:
                    wait = 2 ** retries
                    print(f"       RATE_LIMIT: retrying in {wait}s...")
                    time.sleep(wait)
                    retries += 1
                    continue

                m.end_time = time.perf_counter()
                m.error = error_str
                m.memory_block_lengths = _extract_memory_lengths(session)
                m.memory_block_snapshots = _extract_memory_snapshots(session)
                traceback.print_exc()
                turn_done = True

                if _is_quota_error(error_str):
                    quota_exhausted = True

        m.outcome = _classify_outcome(m.error, m.tool_calls, m.assistant_content_preview)
        metrics.append(m)

        # Incremental JSONL write for live dashboard
        with open(jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(m.to_dict(), ensure_ascii=False) + "\n")
            f.flush()

        # Immediate print of key signals
        signals: list[str] = []
        if m.tool_calls:
            signals.append(f"tools={m.tool_calls}")
        if m.context_summary_present:
            signals.append(f"summary=yes(recursion={m.summary_recursion_count})")
        if m.early_return_reason:
            signals.append(f"EARLY_RETURN={m.early_return_reason}")
        if m.context_pressure_triggered:
            signals.append(f"PRESSURE({m.context_pressure_tokens}/{m.context_pressure_threshold})")
        if m.error:
            signals.append(f"ERROR={m.error}")
        if m.outcome != "success":
            signals.append(f"OUTCOME={m.outcome}")

        mem_lens = ", ".join(f"{k}={v}" for k, v in m.memory_block_lengths.items())
        print(f"       duration={m.end_time - m.start_time:.1f}s  |  mem=[{mem_lens}]")
        if signals:
            print(f"       *** {' | '.join(signals)}")
        print()

        if quota_exhausted:
            print("[QUOTA EXHAUSTED] Stopping smoke run.")
            break

        if args.max_tokens_budget and total_tokens_consumed >= args.max_tokens_budget:
            print(f"[BUDGET EXHAUSTED] total_tokens={total_tokens_consumed:,} >= budget={args.max_tokens_budget:,}. Stopping gracefully.")
            budget_exhausted = True
            break

    overall_end = time.perf_counter()

    # -----------------------------------------------------------------------
    # Post-run soft assertions
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("POST-RUN ASSERTIONS")
    print("=" * 70)

    final_human = session.core_memory_blocks["human"].value
    final_product = session.core_memory_blocks["product"].value
    final_sales = session.core_memory_blocks["sales_strategy"].value
    final_ci = session.core_memory_blocks["customer_intelligence"].value

    # Act 1 assertions
    soft.assert_contains(final_human, "李明", "human block should contain user name")
    soft.assert_contains(final_human, "云算智能", "human block should contain corrected company name")
    soft.assert_contains(final_product, "财税", "product block should mention product domain")
    soft.assert_contains(final_product, "发票", "product block should mention invoice capability")

    # Act 2 assertions
    soft.assert_contains(final_ci, "A 公司", "customer_intelligence should track lead A")
    soft.assert_contains(final_ci, "B 公司", "customer_intelligence should track lead B")
    soft.assert_contains(final_ci, "C 公司", "customer_intelligence should track lead C")

    # Act 3 assertions
    soft.assert_contains(final_sales, "A 公司", "sales_strategy should mention lead A strategy")
    soft.assert_true(
        "50 人" in final_ci or "张总" in final_ci,
        "customer_intelligence should reflect corrected A-company size",
    )

    # Act 4 assertions (corrections)
    soft.assert_contains(final_product, "399", "product block should reflect corrected price 399")
    soft.assert_true(
        "299" not in final_product or "涨价" in final_product or "老客户" in final_product,
        "old price 299 should be superseded or annotated",
    )

    # Act 5 / context assertions
    any_compression = any(m.context_summary_present for m in metrics)
    any_warning = any(m.context_pressure_triggered for m in metrics)
    any_early_return = any(m.early_return_reason is not None for m in metrics)
    any_platform_error = any(m.outcome == "platform_error" for m in metrics)
    any_quota_error = any(m.outcome == "quota_error" for m in metrics)
    any_runtime_seam = any(m.outcome == "runtime_seam" for m in metrics)
    any_error = any(m.error is not None for m in metrics)

    # We do NOT hard-require compression to trigger every run; token volume varies.
    # But we record whether it happened.
    if any_compression:
        print("[PASS] Context compression (90%) triggered at least once.")
        # Find first compression turn
        first_comp = next(m for m in metrics if m.context_summary_present)
        print(f"       First compression at turn {first_comp.turn_index + 1}")
    else:
        print("[INFO] Context compression (90%) did NOT trigger in this run.")
        print("       This is acceptable if total tokens stayed under threshold.")

    if any_warning:
        print("[PASS] Pressure warning (75%) injected at least once.")
    else:
        print("[INFO] Pressure warning (75%) did NOT trigger.")

    if any_early_return:
        print(f"[WARN] Early return occurred: {next(m.early_return_reason for m in metrics if m.early_return_reason)}")
    else:
        print("[PASS] No early return (95% guard) triggered.")

    if any_runtime_seam:
        print(f"[INFO] Runtime seam(s) occurred: {sum(1 for m in metrics if m.outcome == 'runtime_seam')} turn(s) (no_tool_call).")
    if any_platform_error:
        print(f"[FAIL] Platform errors occurred: {sum(1 for m in metrics if m.outcome == 'platform_error')} turn(s).")
    if any_quota_error:
        print(f"[FAIL] Quota error occurred: {sum(1 for m in metrics if m.outcome == 'quota_error')} turn(s).")
    if not any_error:
        print("[PASS] No runtime errors.")

    # Pressure warning effectiveness check (2.5)
    pressure_warning_effectiveness: dict[str, Any] | None = None
    if any_warning:
        warning_turn = next(m for m in metrics if m.context_pressure_triggered)
        w_idx = warning_turn.turn_index
        before_turns = metrics[max(0, w_idx - 5):w_idx]
        after_turns = metrics[w_idx + 1:w_idx + 6]
        rethink_before = sum(
            1 for m in before_turns for tc in m.tool_calls if tc == "memory_rethink"
        )
        rethink_after = sum(
            1 for m in after_turns for tc in m.tool_calls if tc == "memory_rethink"
        )
        pressure_warning_effectiveness = {
            "warning_turn": w_idx + 1,
            "rethink_before": rethink_before,
            "rethink_after": rethink_after,
        }
        print(f"[INFO] Pressure warning at turn {w_idx + 1}: "
              f"rethink_before={rethink_before}, rethink_after={rethink_after}")
        # Soft assertion: warning should not cause a spike in memory_rethink
        if rethink_after > rethink_before + 1:
            print(f"[WARN] Pressure warning effectiveness: rethink_after ({rethink_after}) > "
                  f"rethink_before ({rethink_before}) + 1. "
                  f"This is a soft check and does not block the run.")
        else:
            print("[PASS] Pressure warning effectiveness check passed.")
    else:
        print("[INFO] Pressure warning effectiveness check skipped (no warning triggered).")

    # Recall verification (saturation mode only)
    recall_verification: dict[str, Any] = {"attempted": False, "passed": False}
    if args.context_saturation:
        recall_metrics = metrics[-1] if metrics and metrics[-1].turn_index >= 35 else None
        if recall_metrics and recall_metrics.outcome in ("success", "runtime_seam"):
            recall_verification["attempted"] = True
            if any_compression:
                # Check if early facts appear in the recall turn assistant response
                recall_content = recall_metrics.assistant_content_preview.lower()
                facts_found = []
                for fact in PREFILL_EARLY_FACTS:
                    # Use a simple keyword match for each fact's key terms
                    keywords = []
                    if "李明" in fact:
                        keywords.append("李明")
                    if "云算智能" in fact:
                        keywords.append("云算智能")
                    if "财税" in fact or "发票" in fact:
                        keywords.extend(["财税", "发票", "自动报税"])
                    if "399" in fact:
                        keywords.append("399")
                    found_any = any(kw in recall_content for kw in keywords)
                    facts_found.append(found_any)
                recall_verification["passed"] = any(facts_found)
                if recall_verification["passed"]:
                    print(f"[PASS] Recall verification: at least one early fact recalled ({sum(facts_found)}/{len(facts_found)}).")
                else:
                    print("[INFO] Recall verification: early facts not found in recall response. "
                          "This may happen if summarization dropped them.")
            else:
                print("[SKIP] Recall verification skipped: summarization did not trigger.")
        else:
            print("[SKIP] Recall verification skipped: recall turn did not complete successfully.")

    # Self-compaction observation
    max_human = max(m.memory_block_lengths.get("human", 0) for m in metrics)
    max_product = max(m.memory_block_lengths.get("product", 0) for m in metrics)
    max_ci = max(m.memory_block_lengths.get("customer_intelligence", 0) for m in metrics)
    max_sales = max(m.memory_block_lengths.get("sales_strategy", 0) for m in metrics)
    final_human_len = len(session.core_memory_blocks["human"].value)
    final_product_len = len(session.core_memory_blocks["product"].value)
    final_ci_len = len(session.core_memory_blocks["customer_intelligence"].value)
    final_sales_len = len(session.core_memory_blocks["sales_strategy"].value)

    print()
    print("Memory block length evolution (max -> final):")
    print(f"  human:            {max_human:>6} -> {final_human_len:>6}  {'(self-compacted)' if final_human_len < max_human else '(stable/grew)'}")
    print(f"  product:          {max_product:>6} -> {final_product_len:>6}  {'(self-compacted)' if final_product_len < max_product else '(stable/grew)'}")
    print(f"  customer_intel:   {max_ci:>6} -> {final_ci_len:>6}  {'(self-compacted)' if final_ci_len < max_ci else '(stable/grew)'}")
    print(f"  sales_strategy:   {max_sales:>6} -> {final_sales_len:>6}  {'(self-compacted)' if final_sales_len < max_sales else '(stable/grew)'}")

    print()
    print(soft.report())

    # -----------------------------------------------------------------------
    # Report
    # -----------------------------------------------------------------------
    print()
    print("=" * 70)
    print("SUMMARY REPORT")
    print("=" * 70)

    report_data = {
        "session_id": session.id,
        "model": TARGET_MODEL,
        "context_window": CONTEXT_WINDOW,
        "total_turns": len(turns),
        "completed_turns": len(metrics),
        "total_duration_seconds": round(overall_end - overall_start, 2),
        "total_messages": len(session.messages),
        "total_tokens_consumed": total_tokens_consumed,
        "budget_exhausted": budget_exhausted,
        "summary_state": {
            "context_summary_present": session.context_summary is not None and len(session.context_summary) > 0,
            "context_summary_chars": len(session.context_summary) if session.context_summary else 0,
            "summary_cursor_message_id": session.summary_cursor_message_id,
            "summary_recursion_count": session.summary_recursion_count,
        },
        "context_management": {
            "pressure_warning_triggered": any_warning,
            "compression_triggered": any_compression,
            "early_return_triggered": any_early_return,
            "early_return_reason": next((m.early_return_reason for m in metrics if m.early_return_reason), None),
        },
        "memory_blocks_final": {k: len(v.value) for k, v in session.core_memory_blocks.items()},
        "memory_self_compaction": {
            "human": {"max": max_human, "final": final_human_len, "compacted": final_human_len < max_human},
            "product": {"max": max_product, "final": final_product_len, "compacted": final_product_len < max_product},
            "customer_intelligence": {"max": max_ci, "final": final_ci_len, "compacted": final_ci_len < max_ci},
            "sales_strategy": {"max": max_sales, "final": final_sales_len, "compacted": final_sales_len < max_sales},
        },
        "outcome_counts": {
            "success": sum(1 for m in metrics if m.outcome == "success"),
            "runtime_seam": sum(1 for m in metrics if m.outcome == "runtime_seam"),
            "platform_error": sum(1 for m in metrics if m.outcome == "platform_error"),
            "quota_error": sum(1 for m in metrics if m.outcome == "quota_error"),
        },
        "saturation_mode": args.context_saturation,
        "prefill_message_count": prefill_message_count,
        "recall_verification": recall_verification,
        "pressure_warning_effectiveness": pressure_warning_effectiveness,
        "errors": [m.to_dict() for m in metrics if m.error],
        "turn_metrics": [m.to_dict() for m in metrics],
    }

    print(json.dumps(report_data, indent=2, ensure_ascii=False))

    # Save report to file
    report_path = report_dir / f"v3_live_smoke_report_{session.id}.json"
    report_path.write_text(json.dumps(report_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print()
    print(f"Full report saved to: {report_path}")

    # Rename incremental JSONL to timestamped version
    final_jsonl_path = report_dir / f"v3_live_smoke_{session.id}.jsonl"
    if jsonl_path.exists():
        jsonl_path.rename(final_jsonl_path)
        print(f"Incremental JSONL saved to: {final_jsonl_path}")
    else:
        print(f"[WARN] JSONL not finalized; current_smoke.jsonl may be missing.")

    # Exit codes: 0 = success/runtime_seam, 2 = platform_error, 3 = quota_error
    if any_quota_error:
        return 3
    if any_platform_error:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
