# Tencent TokenHub Native FC Model Probe：2026-04-30

## 1. Scope

This note records a point-in-time Tencent TokenHub model probe for OpenClaw V3 memory-native sales-agent work.

Date: 2026-04-30  
Endpoint tested: `https://tokenhub.tencentmaas.com/v1/chat/completions`  
Repo config source: current backend settings loaded from `backend/.env` without reading or printing secret values.

Important limits:

- Results are point-in-time evidence only. Tencent Cloud model availability, default parameters, Token Plan coverage, pricing, quota policy, and routing can change.
- This probe used the normal TokenHub `/v1` endpoint. It did not test the Token Plan `/plan/v3` endpoint.
- Tencent Token Plan Enterprise docs currently describe a narrower model set than the `/v1` endpoint exposed in this probe; `/v1` success does not prove a model is included in a specific enterprise Token Plan package.
- The probe used a minimal `upsert_memory` function schema and a short memory fact. It is not a full agent benchmark.

Official references checked:

- Tencent TokenHub model list: `https://cloud.tencent.com/document/product/1823/130051`
- Tencent TokenHub model prices: `https://cloud.tencent.com/document/product/1823/130055`
- Tencent TokenHub thinking controls: `https://cloud.tencent.com/document/product/1823/131208`
- Tencent Token Plan Enterprise overview: `https://cloud.tencent.com/document/product/1823/131172`
- Kimi K2.6 quickstart / agent docs: `https://platform.kimi.com/docs/guide/kimi-k2-6-quickstart`
- MiniMax M2.7 tool-use docs: `https://platform.minimax.io/docs/api-reference/text-m2-function-call-refer`

## 2. Current OpenClaw Fit

V3 needs a model that can support:

- Native OpenAI-style `tool_calls`.
- Stable memory-tool loops.
- Forced or named tool calls for deterministic memory write probes.
- Chinese sales/customer-intelligence context.
- Reasonable latency and cost for `/lab` iterative testing.
- Per-model policy controls for `thinking`, `temperature`, and `tool_choice`.

The current `TokenHubClient` only supports plain `complete(messages)` and expects non-empty `message.content`. Native FC responses can return empty content plus `message.tool_calls`; therefore a `complete_with_tools(...)` adapter is still required before V3 memory tools can use native FC as the main path.

## 3. Live Probe Summary

| Model | Plain call | FC auto | FC required | FC named tool | Full tool loop | Notes |
|---|---:|---:|---:|---:|---:|---|
| `minimax-m2.7` | pass | pass | pass | pass | pass | Best current engineering fit: stable FC, low special handling, lower latency than Kimi K2.6 in this probe. |
| `kimi-k2.6` | pass | pass | pass with `thinking=disabled`, `temperature=0.6` | pass with `thinking=disabled`, `temperature=0.6` | pass with auto | Strong agent candidate, but TokenHub parameter policy is special and latency was high in this probe. |
| `kimi-k2.5` | pass | pass | pass with `thinking=disabled`, `temperature=0.6` | pass with `thinking=disabled`, `temperature=0.6` | not fully tested | Faster than K2.6 in this probe; older model. |
| `deepseek-v4-flash` | pass | pass | pass | pass with `thinking=disabled` | pass | Good speed/cost candidate; named tool needs thinking disabled. |
| `deepseek-v4-pro` | pass | pass | pass | pass with `thinking=disabled` | not fully tested | More expensive and slower; keep as premium eval lane, not default. |
| `deepseek-v3.2` | pass | pass | pass | pass | not fully tested | Strong compatibility baseline for smoke tests. |
| `glm-5.1` | pass | pass | pass | pass | not fully tested | Strong agent/coding candidate; needs cost/latency eval before default use. |
| `hy3-preview` | pass | auto timed out once | fail | fail | not tested | TokenHub reported `tool_choice only supports "auto" currently`; not a good forced memory-tool validation model. |
| `deepseek-v3.1-terminus` | pass | pass | pass | pass | not fully tested | Legacy stable fallback; not preferred as new default. |
| `minimax-m2.5` | fail | fail | fail | fail | not tested | Current endpoint returned `FREE_QUOTA_EXHAUSTED`; this is quota/endpoint state, not an FC capability conclusion. |

## 4. Parameter Findings

### Kimi K2.6 / K2.5 on TokenHub

Observed TokenHub behavior:

- With thinking enabled/default:
  - `temperature` must be `1`.
  - `tool_choice="auto"` works.
  - `tool_choice="required"` fails.
  - Named tool-choice object fails.
- With `thinking={"type":"disabled"}`:
  - `temperature` must be `0.6`.
  - `tool_choice="required"` works.
  - Named tool-choice object works.

Implication:

- Kimi K2.6 should not be added as a simple model-name-only config.
- It needs a per-model request policy in the future native FC adapter.
- Kimi K2.6 remains valuable for high-capability agent evaluation, but it is not the lowest-risk default for the first memory-tool loop.

### MiniMax M2.7 on TokenHub

Observed TokenHub behavior:

- `temperature=0` worked in this probe.
- Plain call passed.
- FC `auto`, `required`, and named tool-choice all passed.
- Full tool loop passed.

Implication:

- MiniMax M2.7 is the cleanest first default candidate for V3 `/lab` native FC POC.

### DeepSeek V4 Flash on TokenHub

Observed TokenHub behavior:

- Plain call passed.
- FC `auto` and `required` passed.
- Named tool-choice requires `thinking={"type":"disabled"}`.
- `enable_thinking=false` did not disable thinking for this endpoint; Tencent's documented `thinking` object must be used.
- Full tool loop passed.

Implication:

- DeepSeek V4 Flash is a strong speed/cost candidate and good secondary default candidate.
- It also needs model policy support for named tool-choice.

## 5. Cost Snapshot

Tencent Cloud public online-inference prices queried on 2026-04-30. Unit: RMB per 1M tokens.

| Model | Input | Output | Cache hit input | Notes |
|---|---:|---:|---:|---|
| `deepseek-v4-flash` | 1 | 2 | 0.2 | Strong cost candidate. |
| `deepseek-v4-pro` | 12 | 24 | 1 | Premium lane. |
| `deepseek-v3.2` | 2 | 3 | - | Compatibility baseline. |
| `deepseek-v3.1-terminus` | 4 | 12 | - | Listed as Deepseek-v3.1. |
| `deepseek-r1-0528` | 4 | 16 | - | Not live-probed in this pass. |
| `deepseek-v3-0324` | 2 | 8 | - | Not live-probed in this pass. |
| `glm-5.1` | 6 / 8 | 24 / 28 | 1.3 / 2 | Tiered by input length: `(0,32k]` / `32k+`. |
| `kimi-k2.6` | 6.5 | 27 | 1.1 | Strong agent candidate but higher latency and policy complexity in this probe. |
| `kimi-k2.5` | 4 | 21 | 0.7 | Older Kimi fallback. |
| `minimax-m2.7` | 2.1 | 8.4 | 0.42 | Best first OpenClaw V3 native FC default candidate from this probe. |
| `minimax-m2.5` | 2.1 | 8.4 | 0.21 | Current endpoint quota exhausted in live probe. |
| `hy3-preview` | 1.2 / 1.6 / 2 | 4 / 6.4 / 8 | 0.4 / 0.6 / 0.8 | Tiered by input length: `(0,16k)`, `[16k,32k)`, `[32k+)`. |

Cost caveats:

- These are public online-inference prices, not a guarantee of enterprise Token Plan effective price.
- Token Plan Enterprise docs say model support and routing can change. On 2026-04-29, Enterprise Professional listed Auto, GLM-5, Kimi-K2.5, and MiniMax-M2.5; Enterprise Light listed Auto only.
- Effective cost depends heavily on output length, hidden/reasoning token behavior, cache hit rate, retries, and provider-side routing.

## 6. Recommendation

Current recommendation for the next native FC adapter POC:

1. Use `minimax-m2.7` as the first default `/lab` memory-tool-loop model.
2. Add `deepseek-v4-flash` as a low-cost/low-latency comparison model with `thinking={"type":"disabled"}` for named tool-choice probes.
3. Add `deepseek-v3.2` as the compatibility smoke baseline.
4. Add `kimi-k2.6` as a high-capability agent evaluation lane, with explicit per-model policies:
   - Auto tool use: `temperature=1`.
   - Forced/named tool use: `thinking={"type":"disabled"}`, `temperature=0.6`.
5. Keep `glm-5.1` as a strong agent/coding comparison model, but do not make it the first default until cost and latency are measured on realistic V3 turns.
6. Keep `deepseek-v3.1-terminus` only as a legacy fallback.
7. Do not use `hy3-preview` as the forced-memory-tool validation model because forced/named tool choice was not supported in this probe.

## 7. Recommended Adapter Requirements

Future `TokenHubClient.complete_with_tools(...)` should support:

- `tools`.
- `tool_choice`: `auto`, `required`, `none`, or named tool-choice object.
- Parsed `message.tool_calls`.
- Assistant-message round-trip for tool-result loops.
- Per-model request policy:
  - `temperature`.
  - `thinking`.
  - optional `reasoning_effort`.
  - fallback behavior when forced/named tool choice is unsupported in a mode.
- Safe tracing that never records API keys or authorization headers.

This adapter should preserve `json_simulated_tool_calls` as a fallback, but native FC should become the preferred path after tests cover the selected model policies.
