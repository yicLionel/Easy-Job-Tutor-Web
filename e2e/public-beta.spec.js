const { test, expect } = require("@playwright/test");

test("health endpoint returns ok", async ({ request }) => {
  const response = await request.get("/api/health");
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body).toEqual({ status: "ok" });
});

test("public beta states its limits and requires privacy consent", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("公开 Beta")).toBeVisible();
  await expect(page.getByText("不预测录用结果")).toBeVisible();
  const consent = page.locator("#privacy-consent");
  await expect(consent).not.toBeChecked();
  await expect(page.getByRole("button", { name: "分析这份简历" })).toBeDisabled();
  await expect(page.getByRole("link", { name: "隐私说明" })).toHaveAttribute("href", "/privacy.html");
});

test("public navigation hides deferred features", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("多 JD 对比")).toHaveCount(0);
  await expect(page.getByText("学习路线")).toHaveCount(0);
  await expect(page.getByText("模拟面试")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "EN" })).toHaveCount(0);
});
