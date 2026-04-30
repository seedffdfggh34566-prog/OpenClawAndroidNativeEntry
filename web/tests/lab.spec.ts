import { expect, test } from "@playwright/test";

test("lab creates a session and renders v3 sandbox state", async ({ page }) => {
  await page.goto("/lab");

  await expect(page.getByRole("heading", { name: "Sales Agent Lab" })).toBeVisible();
  await expect(page.getByText("Backend online")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Memory", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Working State" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Customer Intelligence" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Trace / Actions" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Memory Transitions" })).toBeVisible();
  await expect(page.getByTestId("store-backend")).not.toHaveText("unknown");

  await page.getByRole("button", { name: "Settings" }).click();
  await expect(page.getByRole("dialog", { name: "Settings" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Settings" })).toBeVisible();
  await expect(page.getByText("Backend Status")).toBeVisible();
  await expect(page.getByText("Runtime Config")).toBeVisible();
  await expect(page.getByText("Danger / Read-only")).toBeVisible();
  await expect(page.getByText("LLM key")).toBeVisible();
  await page.getByLabel("Timeout").selectOption("120");
  await page.getByLabel("Trace max bytes").selectOption("200000");
  await page.getByLabel("Default verbose trace").check();
  await page.getByLabel("Default include prompt").check();
  await page.getByLabel("Default include raw LLM output").check();
  await page.getByLabel("Default include state diff").check();
  await page.getByRole("button", { name: "Apply changes" }).click();
  await expect(page.getByLabel("Default verbose trace")).toBeChecked();
  await page.getByRole("button", { name: "Close settings" }).click();

  await page.getByRole("button", { name: "New session" }).click();
  await expect(page.getByTestId("session-id")).not.toHaveText("None");

  await expect(page.getByText("Trace controls")).toBeVisible();
  await page.getByLabel("Verbose trace").check();
  await page.getByLabel("Include prompt").check();
  await page.getByLabel("Include raw LLM output").check();
  await page.getByLabel("Include state diff").check();
  await page.getByPlaceholder("Enter a sales-agent turn...").fill("我们做面向苏州小企业老板的销售管理培训，主要是线下课。");
  await page.getByRole("button", { name: "Send turn" }).click();

  await expect
    .poll(async () => {
      const alert = await page.getByRole("alert").count();
      const assistant = await page.locator(".message-assistant").count();
      return alert + assistant;
    }, { timeout: 40_000 })
    .toBeGreaterThan(0);

  await expect(page.locator(".message-user").filter({ hasText: "我们做面向苏州小企业老板的销售管理培训" })).toBeVisible();

  const hasError = (await page.getByRole("alert").count()) > 0;
  if (hasError) {
    await expect(page.getByRole("alert")).toContainText(/llm_runtime_unavailable|llm_structured_output_invalid/);
    await expect(page.getByText(/llm_runtime_unavailable|llm_structured_output_invalid/).first()).toBeVisible();
    await page.getByRole("button", { name: "Open inspector" }).click();
    await expect(page.getByRole("dialog", { name: "Trace inspector" })).toBeVisible();
    await expect(page.getByTestId("inspector-node-call_llm")).toBeVisible();
  } else {
    await expect(page.locator(".message-assistant")).toBeVisible();
    await page.getByRole("button", { name: "Open inspector" }).click();
    await expect(page.getByRole("dialog", { name: "Trace inspector" })).toBeVisible();
    await expect(page.getByTestId("inspector-node-load_state")).toBeVisible();
    await expect(page.getByTestId("inspector-node-call_llm")).toBeVisible();
    await expect(page.getByTestId("inspector-node-parse_actions")).toBeVisible();
    await expect(page.getByTestId("inspector-node-apply_actions")).toBeVisible();
    await expect(page.getByTestId("inspector-node-return_turn")).toBeVisible();
    await page.getByTestId("inspector-node-call_llm").click();
    await expect(page.getByText("LLM prompt / messages").first()).toBeVisible();
    await expect(page.getByText("Raw LLM output").first()).toBeVisible();
    await page.getByRole("button", { name: "Close trace inspector" }).click();
  }
});

test("lab supports deterministic seed, safe reset, and replay report", async ({ page }) => {
  test.setTimeout(120_000);
  await page.goto("/lab");
  await expect(page.getByText("Backend online")).toBeVisible();

  await page.getByRole("button", { name: "Seed demo" }).click();
  await expect(page.getByTestId("session-id")).not.toHaveText("None");
  const seededSessionId = await page.getByTestId("session-id").textContent();

  await expect(page.getByText("observed").first()).toBeVisible();
  await expect(page.getByText("superseded").first()).toBeVisible();
  await expect(page.getByText("confirmed").first()).toBeVisible();
  await expect(page.getByText("苏州小企业老板").first()).toBeVisible();
  await expect(page.getByText("cand_seed_owner")).toBeVisible();
  await expect(page.getByText("v3_sandbox_demo_seed").first()).toBeVisible();

  const storeBackend = await page.getByTestId("store-backend").textContent();
  if (storeBackend === "database") {
    await expect(page.getByText("write_memory").first()).toBeVisible();
    await expect(page.getByText("update_memory_status").first()).toBeVisible();
  } else {
    await expect(page.getByText("DB inspection unavailable in current store mode.")).toBeVisible();
  }

  await page.getByRole("button", { name: "Reset session" }).click();
  await expect(page.getByTestId("session-id")).not.toHaveText(seededSessionId ?? "");
  await expect(page.getByText("No memory items yet.")).toBeVisible();
  await expect(page.getByText("No trace events yet.")).toBeVisible();

  await page.getByRole("button", { name: "Seed demo" }).click();
  await page.getByRole("button", { name: "Replay user turns" }).click();
  await expect(page.getByRole("status")).toContainText(/Replay (completed|failed)/, { timeout: 100_000 });
  await expect(page.getByRole("status")).toContainText(/turns/);
  await expect(page.getByRole("status")).toContainText(/v3s_replay_/);
});

test("lab shows database-backed memory transition inspection when backend is in database mode", async ({ page }) => {
  test.setTimeout(120_000);
  await page.goto("/lab");
  await expect(page.getByText("Backend online")).toBeVisible();

  await page.getByRole("button", { name: "Seed demo" }).click();
  const storeBackend = await page.getByTestId("store-backend").textContent();
  test.skip(storeBackend !== "database", "requires OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND=database backend");

  await expect(page.getByRole("heading", { name: "Memory Transitions" })).toBeVisible();
  await expect(page.getByText("write_memory").first()).toBeVisible();
  await expect(page.getByText("update_memory_status").first()).toBeVisible();
  await expect(page.getByText("mem_seed_product").first()).toBeVisible();

  await page.getByRole("button", { name: "Replay user turns" }).click();
  await expect(page.getByRole("status")).toContainText(/v3s_replay_/, { timeout: 100_000 });
  await page.getByRole("button", { name: "Refresh" }).click();
  await expect(page.getByRole("heading", { name: "Memory Transitions" })).toBeVisible();
  await expect(page.getByTestId("store-backend")).toHaveText("database");
});
