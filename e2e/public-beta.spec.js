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

test("public scope exposes only one JD plus one supported resume", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("仅分析 JD")).toHaveCount(0);
  await expect(page.getByText("仅诊断简历")).toHaveCount(0);
  await expect(page.getByText("多 JD 对比")).toHaveCount(0);
  await expect(page.locator('input[type="file"]')).toHaveAttribute("accept", ".pdf,.docx,.txt");
});

test("public complete analysis shows evidence without scores or deferred features", async ({ page }) => {
  await page.goto("/");
  await page.locator("textarea").fill(
    "招聘 AI 产品经理，要求具备 Python、SQL、用户研究、数据分析和产品规划能力。"
  );
  await page.locator('input[type="file"]').setInputFiles({
    name: "resume.txt",
    mimeType: "text/plain",
    buffer: Buffer.from(
      "教育经历\n项目经历\n使用 Python 和 SQL 完成用户研究与数据分析，负责产品规划。",
      "utf8"
    ),
  });
  await page.locator("#privacy-consent").check();
  await page.getByRole("button", { name: "分析这份简历" }).click();

  await expect(page.getByText("事实台账")).toBeVisible();
  await expect(page.getByText("匹配度")).toHaveCount(0);
  await expect(page.getByText("竞争力强")).toHaveCount(0);
  await expect(page.getByText("ATS")).toHaveCount(0);
  await expect(page.getByText("面试准备度")).toHaveCount(0);
  await expect(page.getByText("简历可信度")).toHaveCount(0);
  await expect(page.getByText("学习路线")).toHaveCount(0);
  await expect(page.getByText("面试辅导")).toHaveCount(0);

  await page.getByRole("button", { name: /^查看差距/ }).click();
  await expect(page.getByRole("heading", { name: "查漏补缺", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "生成学习路线 & 面试辅导" })).toHaveCount(0);
  await expect(page.getByText("学习路线")).toHaveCount(0);
  await expect(page.getByText("面试辅导")).toHaveCount(0);
});

test("390px shell has no page overflow and sidebar starts closed", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  const metrics = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    sidebarTransform: getComputedStyle(document.querySelector(".sidebar")).transform
  }));
  expect(metrics.scrollWidth).toBeLessThanOrEqual(metrics.clientWidth);
  expect(metrics.sidebarTransform).not.toBe("none");
});

test("core form is keyboard-addressable", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByLabel("岗位 JD")).toBeVisible();
  await expect(page.getByLabel("上传简历")).toBeAttached();
  await expect(page.getByLabel(/我已阅读并同意/)).toBeAttached();
});
