import { expect, test } from "@playwright/test";

test("lab creates a session and renders v3 sandbox state", async ({ page }) => {
  await page.goto("/lab");

  await expect(page.getByRole("heading", { name: "Sales Agent Lab" })).toBeVisible();
  await expect(page.getByText("Backend online")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Memory" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Working State" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Customer Intelligence" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Trace / Actions" })).toBeVisible();

  await page.getByRole("button", { name: "New session" }).click();
  await expect(page.getByTestId("session-id")).not.toHaveText("None");

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
  } else {
    await expect(page.locator(".message-assistant")).toBeVisible();
  }
});
